//! A deterministic, reference-only assessment. Inputs confer no verifier authority.
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Case {
    pub schema: String,
    pub change: Change,
    #[serde(default)]
    pub snapshot: Snapshot,
    pub claims: Vec<Claim>,
    pub evidence: Vec<EvidenceReference>,
}
/// Describes supplied source context, never freshness established by this evaluator.
#[derive(Clone, Debug, Default, Deserialize, Serialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum Snapshot {
    #[default]
    Unspecified,
    Historical {
        captured_on: String,
    },
}

fn valid_date(date: &str) -> bool {
    let b = date.as_bytes();
    if b.len() != 10
        || b[4] != b'-'
        || b[7] != b'-'
        || !b
            .iter()
            .enumerate()
            .all(|(i, c)| i == 4 || i == 7 || c.is_ascii_digit())
    {
        return false;
    }
    let year: u32 = date[..4].parse().unwrap();
    let month: usize = date[5..7].parse().unwrap();
    let day: u32 = date[8..].parse().unwrap();
    let leap = year.is_multiple_of(4) && (!year.is_multiple_of(100) || year.is_multiple_of(400));
    let days = [
        31,
        if leap { 29 } else { 28 },
        31,
        30,
        31,
        30,
        31,
        31,
        30,
        31,
        30,
        31,
    ];
    year > 0 && (1..=12).contains(&month) && day > 0 && day <= days[month - 1]
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
    pub snapshot: Snapshot,
    pub unreferenced_evidence: Vec<EvidenceReference>,
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
    pub evidence_ids: Vec<String>,
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
        evidence_ids: Vec::new(),
    }
}
fn reference_gap(code: &'static str, id: &str, explanation: &str) -> Gap {
    Gap {
        code,
        explanation: explanation.into(),
        evidence_ids: vec![id.into()],
    }
}
/// Validate all structure before evaluating; never open references or execute their contents.
pub fn assess(case: Case) -> Result<Assessment, String> {
    if case.schema != "aethel.plm.case/v1" {
        return Err("unsupported case schema".into());
    }
    if let Snapshot::Historical { captured_on } = &case.snapshot {
        if !valid_date(captured_on) {
            return Err("invalid historical captured_on date (expected YYYY-MM-DD)".into());
        }
    }
    if case.claims.is_empty() {
        return Err("case must contain at least one claim".into());
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
    let mut used = BTreeSet::new();
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
        let mut decisive_ids = Vec::new();
        let has_references = !refs.is_empty();
        for id in refs {
            used.insert(id.clone());
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
                gaps.insert(reference_gap(
                    "wrong_kind",
                    &id,
                    &format!("{id}: evidence kind does not match the required kind."),
                ));
            }
            match candidate_binding {
                "unknown" => {
                    gaps.insert(reference_gap(
                        "unknown_binding",
                        &id,
                        &format!("{id}: candidate binding is unknown."),
                    ));
                }
                "different" => {
                    gaps.insert(reference_gap(
                        "different_candidate",
                        &id,
                        &format!("{id}: evidence refers to another candidate."),
                    ));
                }
                _ => {}
            }
            if e.reported_result == ReportedResult::NotApplicable {
                gaps.insert(reference_gap("not_applicable", &id, &format!("{id}: this reference is reported not applicable; its explanation is a source assertion, not a claim-level exemption or approval.")));
            } else if kind_match == "match" && candidate_binding == "match" {
                matching = true;
                results.insert(e.reported_result);
                if matches!(
                    e.reported_result,
                    ReportedResult::Pass | ReportedResult::Fail
                ) {
                    decisive_ids.push(id.clone());
                }
                match e.reported_result {
                    ReportedResult::Fail => {
                        gaps.insert(reference_gap(
                            "reported_failure",
                            &id,
                            &format!("{id}: an applicable reference reports failure."),
                        ));
                    }
                    ReportedResult::Unknown => {
                        gaps.insert(reference_gap(
                            "reported_unknown",
                            &id,
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
            gaps.insert(Gap {
                code: "contradictory_results",
                explanation: "Applicable references report both pass and fail.".into(),
                evidence_ids: decisive_ids,
            });
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
        snapshot: case.snapshot,
        unreferenced_evidence: evidence
            .into_iter()
            .filter(|(id, _)| !used.contains(id))
            .map(|(_, e)| e)
            .collect(),
        claims: result,
    })
}

mod render;
pub use render::render_text;
