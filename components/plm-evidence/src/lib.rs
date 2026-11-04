//! A deterministic, reference-only assessment. Inputs confer no verifier authority.
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Case {
    pub schema: String,
    pub change: Change,
    pub claims: Vec<Claim>,
    pub evidence: Vec<EvidenceReference>,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Change {
    pub id: String,
    pub product_reference: Option<String>,
    pub problem: String,
    pub goal: String,
    pub candidate: Option<String>,
    pub context: String,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Claim {
    pub id: String,
    pub statement: String,
    pub required_kind: String,
    pub evidence_ids: Vec<String>,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct EvidenceReference {
    pub id: String,
    pub source: String,
    pub source_id: String,
    pub revision_or_digest: Option<String>,
    pub kind: String,
    pub candidate: Option<String>,
    pub provenance: String,
    pub reported_result: ReportedResult,
    pub explanation: Option<String>,
    #[serde(default)]
    pub verified: bool,
}
#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq, PartialOrd, Ord)]
#[serde(rename_all = "snake_case")]
pub enum ReportedResult {
    Pass,
    Fail,
    Unknown,
    NotApplicable,
}
#[derive(Debug, Serialize)]
pub struct Assessment {
    pub schema: &'static str,
    pub change: Change,
    pub claims: Vec<ClaimAssessment>,
}
#[derive(Debug, Serialize)]
pub struct ClaimAssessment {
    pub id: String,
    pub statement: String,
    pub required_kind: String,
    pub references: Vec<ReferenceAssessment>,
    pub gaps: Vec<Gap>,
}
#[derive(Debug, Serialize)]
pub struct ReferenceAssessment {
    pub evidence: EvidenceReference,
    pub kind_match: &'static str,
    pub candidate_binding: &'static str,
    pub assurance: &'static str,
}
#[derive(Debug, Serialize, PartialEq, Eq, PartialOrd, Ord)]
pub struct Gap {
    pub code: &'static str,
    pub explanation: String,
}

fn nonempty(s: &str) -> bool {
    !s.trim().is_empty()
}
fn optional_valid(s: &Option<String>) -> bool {
    s.as_ref().is_none_or(|v| nonempty(v))
}
fn gap(code: &'static str, explanation: &str) -> Gap {
    Gap {
        code,
        explanation: explanation.into(),
    }
}
/// Validate all structure before evaluating; never open references or execute their contents.
pub fn assess(case: Case) -> Result<Assessment, String> {
    if case.schema != "aethel.plm.case/v1" {
        return Err("unsupported case schema".into());
    }
    let c = &case.change;
    if ![&c.id, &c.problem, &c.goal, &c.context]
        .iter()
        .all(|x| nonempty(x))
        || !optional_valid(&c.candidate)
        || !optional_valid(&c.product_reference)
    {
        return Err("invalid change fields".into());
    }
    let mut evidence = BTreeMap::new();
    for e in case.evidence {
        if ![&e.id, &e.source, &e.source_id, &e.kind, &e.provenance]
            .iter()
            .all(|x| nonempty(x))
            || !optional_valid(&e.candidate)
            || !optional_valid(&e.revision_or_digest)
            || !optional_valid(&e.explanation)
        {
            return Err("invalid evidence fields".into());
        }
        if e.reported_result == ReportedResult::NotApplicable
            && e.explanation.as_ref().is_none_or(|s| !nonempty(s))
        {
            return Err(format!(
                "not_applicable evidence {} requires an explanation",
                e.id
            ));
        }
        let id = e.id.clone();
        if evidence.insert(id.clone(), e).is_some() {
            return Err(format!("duplicate evidence id: {id}"));
        }
    }
    let mut seen = BTreeSet::new();
    let mut claims = case.claims;
    claims.sort_by(|a, b| a.id.cmp(&b.id));
    let mut result = Vec::new();
    for claim in claims {
        if ![&claim.id, &claim.statement, &claim.required_kind]
            .iter()
            .all(|x| nonempty(x))
        {
            return Err("invalid claim fields".into());
        }
        if !seen.insert(claim.id.clone()) {
            return Err(format!("duplicate claim id: {}", claim.id));
        }
        let mut refs = claim.evidence_ids.clone();
        refs.sort();
        if refs.windows(2).any(|w| w[0] == w[1]) {
            return Err(format!("duplicate reference in claim {}", claim.id));
        }
        let mut references = Vec::new();
        let mut gaps = BTreeSet::new();
        let mut matching = false;
        let mut results = BTreeSet::new();
        let has_references = !refs.is_empty();
        for id in refs {
            let e = evidence
                .get(&id)
                .ok_or_else(|| format!("unknown evidence reference: {id}"))?;
            let kind_match = if e.kind == claim.required_kind {
                "match"
            } else {
                "different"
            };
            let candidate_binding = if c.candidate.is_none() || e.candidate.is_none() {
                "unknown"
            } else if e.candidate != c.candidate {
                "different"
            } else {
                "match"
            };
            if kind_match == "different" {
                gaps.insert(gap(
                    "wrong_kind",
                    &format!("{id}: evidence kind does not match the required kind."),
                ));
            }
            match candidate_binding {
                "unknown" => {
                    gaps.insert(gap(
                        "unknown_binding",
                        &format!("{id}: candidate binding is unknown."),
                    ));
                }
                "different" => {
                    gaps.insert(gap(
                        "different_candidate",
                        &format!("{id}: evidence refers to another candidate."),
                    ));
                }
                _ => {}
            }
            if e.reported_result == ReportedResult::NotApplicable {
                gaps.insert(gap("not_applicable", &format!("{id}: this reference is reported not applicable; its explanation is a source assertion, not a claim-level exemption or approval.")));
            } else if kind_match == "match" && candidate_binding == "match" {
                matching = true;
                results.insert(e.reported_result);
                match e.reported_result {
                    ReportedResult::Fail => {
                        gaps.insert(gap(
                            "reported_failure",
                            &format!("{id}: an applicable reference reports failure."),
                        ));
                    }
                    ReportedResult::Unknown => {
                        gaps.insert(gap(
                            "reported_unknown",
                            &format!("{id}: an applicable reference reports an unknown result."),
                        ));
                    }
                    _ => {}
                }
            }
            references.push(ReferenceAssessment {
                evidence: e.clone(),
                kind_match,
                candidate_binding,
                assurance: "source_assertion_only",
            });
        }
        if !has_references {
            gaps.insert(gap(
                "missing_evidence",
                "No evidence references were provided for this claim.",
            ));
        } else if !matching {
            gaps.insert(gap("missing_applicable_evidence", "No reference of the required kind is bound to the candidate and reported applicable."));
        }
        if results.contains(&ReportedResult::Pass) && results.contains(&ReportedResult::Fail) {
            gaps.insert(gap(
                "contradictory_results",
                "Applicable references report both pass and fail.",
            ));
        }
        gaps.insert(gap(
            "independent_verification_missing",
            "References and caller assertions are not independent verification.",
        ));
        result.push(ClaimAssessment {
            id: claim.id,
            statement: claim.statement,
            required_kind: claim.required_kind,
            references,
            gaps: gaps.into_iter().collect(),
        });
    }
    Ok(Assessment {
        schema: "aethel.plm.assessment/v1",
        change: case.change,
        claims: result,
    })
}
