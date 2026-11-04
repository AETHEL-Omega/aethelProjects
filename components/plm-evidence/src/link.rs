//! Proposed read-only linkage between a change assessment and a quality snapshot.
use crate::{
    assess,
    quality::{assess_quality, QualityAssessment, QualityCase},
    Assessment, Case,
};
use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct LinkedCase {
    pub schema: String,
    pub change_case: Case,
    pub quality_case: QualityCase,
    pub links: Vec<Link>,
}
/// A source assertion that an action addressing an issue relates to a claim.
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Link {
    pub id: String,
    pub issue_id: String,
    pub action_id: String,
    pub claim_id: String,
    pub provenance: String,
}
#[derive(Debug, Serialize, PartialEq, Eq, PartialOrd, Ord)]
pub struct LinkFinding {
    pub code: &'static str,
    pub object_type: &'static str,
    pub object_id: String,
    pub link_id: Option<String>,
    pub related_issue_id: Option<String>,
}
#[derive(Debug, Serialize)]
pub struct LinkAssessment {
    pub schema: &'static str,
    pub authority: &'static str,
    pub change: Assessment,
    pub quality: QualityAssessment,
    pub links: Vec<Link>,
    pub findings: Vec<LinkFinding>,
}
fn finding(
    findings: &mut Vec<LinkFinding>,
    code: &'static str,
    object_type: &'static str,
    object_id: &str,
    link_id: Option<&str>,
) {
    findings.push(LinkFinding {
        code,
        object_type,
        object_id: object_id.to_owned(),
        link_id: link_id.map(str::to_owned),
        related_issue_id: None,
    });
}
/// Evaluate both packages as-is; linking assertions do not prove coverage or authorise work.
pub fn assess_linked(mut input: LinkedCase) -> Result<LinkAssessment, String> {
    if input.schema != "aethel.plm.linked-case/v1" {
        return Err("unsupported linked case schema".into());
    }
    let change = assess(input.change_case)?;
    let quality = assess_quality(input.quality_case)?;
    input.links.sort_by(|a, b| a.id.cmp(&b.id));
    let mut ids = BTreeSet::new();
    let mut tuples = BTreeSet::new();
    let mut findings = Vec::new();
    for link in &input.links {
        if [
            &link.id,
            &link.issue_id,
            &link.action_id,
            &link.claim_id,
            &link.provenance,
        ]
        .iter()
        .any(|v| v.trim().is_empty())
        {
            return Err("empty link field".into());
        }
        if !ids.insert(&link.id) {
            return Err(format!("duplicate link id: {}", link.id));
        }
        if !tuples.insert((&link.issue_id, &link.action_id, &link.claim_id)) {
            return Err("duplicate issue/action/claim link".into());
        }
        if !quality.source.issues.iter().any(|i| i.id == link.issue_id) {
            return Err(format!("unknown linked issue: {}", link.issue_id));
        }
        let action = quality
            .source
            .actions
            .iter()
            .find(|a| a.id == link.action_id)
            .ok_or_else(|| format!("unknown linked action: {}", link.action_id))?;
        if !change.claims.iter().any(|c| c.id == link.claim_id) {
            return Err(format!("unknown linked claim: {}", link.claim_id));
        }
        let scopes: Vec<_> = action
            .scopes
            .iter()
            .filter(|s| s.issue_id == link.issue_id)
            .collect();
        if scopes.is_empty() {
            return Err(format!(
                "action {} does not address issue {}",
                link.action_id, link.issue_id
            ));
        }
        match &change.change.candidate {
            None => finding(
                &mut findings,
                "candidate_binding_unknown",
                "link",
                &link.id,
                Some(&link.id),
            ),
            Some(candidate) if !scopes.iter().any(|s| s.candidate == *candidate) => finding(
                &mut findings,
                "different_candidate",
                "link",
                &link.id,
                Some(&link.id),
            ),
            _ => {}
        }
        // A matching identifier is only a declared association, never a claim of effectiveness.
        finding(
            &mut findings,
            "link_not_independently_verified",
            "link",
            &link.id,
            Some(&link.id),
        );
    }
    for claim in &change.claims {
        if !input.links.iter().any(|l| l.claim_id == claim.id) {
            finding(&mut findings, "claim_unlinked", "claim", &claim.id, None);
        }
    }
    for issue in &quality.source.issues {
        if !input.links.iter().any(|l| l.issue_id == issue.id) {
            finding(&mut findings, "issue_unlinked", "issue", &issue.id, None);
        }
    }
    for action in &quality.source.actions {
        if !input.links.iter().any(|l| l.action_id == action.id) {
            finding(&mut findings, "action_unlinked", "action", &action.id, None);
        }
    }
    for action in &quality.source.actions {
        let issue_ids: BTreeSet<_> = action
            .scopes
            .iter()
            .map(|scope| scope.issue_id.as_str())
            .collect();
        for issue_id in issue_ids {
            if !input
                .links
                .iter()
                .any(|link| link.action_id == action.id && link.issue_id == issue_id)
            {
                findings.push(LinkFinding {
                    code: "action_issue_unlinked",
                    object_type: "action",
                    object_id: action.id.clone(),
                    link_id: None,
                    related_issue_id: Some(issue_id.to_owned()),
                });
            }
        }
    }
    findings.sort();
    findings.dedup();
    Ok(LinkAssessment {
        schema: "aethel.plm.linked-assessment/v1",
        authority: "associations_are_assertions; no_verification_or_authorisation",
        change,
        quality,
        links: input.links,
        findings,
    })
}
pub fn render_linked_text(a: &LinkAssessment) -> String {
    use std::fmt::Write;
    let mut out =
        String::from("Verknüpfte Fallauswertung — Referenzen sind Behauptungen, keine Freigabe.\n");
    writeln!(
        out,
        "Änderung: {} · Qualitätsfall: {}",
        a.change.change.id.escape_debug(),
        a.quality.source.id.escape_debug()
    )
    .unwrap();
    out.push_str(&crate::render_text(&a.change));
    out.push_str(&crate::quality::render_quality_text(&a.quality));
    for link in &a.links {
        writeln!(
            out,
            "Verknüpfung {}: Issue {} → Maßnahme {} → Aussage {} (berichtet)",
            link.id.escape_debug(),
            link.issue_id.escape_debug(),
            link.action_id.escape_debug(),
            link.claim_id.escape_debug()
        )
        .unwrap();
    }
    for f in &a.findings {
        writeln!(
            out,
            "  [{}] {} {}",
            f.code,
            f.object_type,
            f.object_id.escape_debug()
        )
        .unwrap();
    }
    out
}
