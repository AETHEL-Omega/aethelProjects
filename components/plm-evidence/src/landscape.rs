//! A reading view of a supplied, dated workspace observation, never a registry.
use crate::{Case, Snapshot};
use serde::{Deserialize, Serialize};
use std::collections::HashSet;

#[derive(Debug, Deserialize)]
pub struct Observation {
    pub schema: String,
    pub generated_at: String,
    pub nodes: Vec<Node>,
    pub edges: Vec<Edge>,
    #[serde(default)]
    pub scope: serde_json::Value,
    #[serde(default)]
    pub summary: serde_json::Value,
    #[serde(default)]
    pub problems: serde_json::Value,
    #[serde(default)]
    pub excluded_paths: serde_json::Value,
    #[serde(default)]
    pub symlinks: serde_json::Value,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct Node {
    pub id: String,
    pub name: String,
    pub kind: String,
    #[serde(default)]
    pub category: Option<String>,
    #[serde(default)]
    pub recorded_status: Option<String>,
    #[serde(default)]
    pub purpose: Option<String>,
    #[serde(default)]
    pub proposal_status: Option<String>,
    #[serde(default)]
    pub loop_status: Option<String>,
    #[serde(default)]
    pub git_common_dir: Option<String>,
    #[serde(default)]
    pub source: Option<String>,
    #[serde(default)]
    pub source_revision: Option<String>,
    #[serde(default)]
    pub path: Option<String>,
    #[serde(default)]
    pub paths: Vec<String>,
    #[serde(default)]
    pub areas: Vec<String>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct Edge {
    pub from: String,
    pub to: String,
    #[serde(rename = "type")]
    pub kind: String,
    pub status: String,
    pub evidence: String,
    pub detail: String,
    #[serde(default)]
    pub source_revision: Option<String>,
    #[serde(default)]
    pub origin: Option<String>,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Supplement {
    pub schema: String,
    pub source_id: String,
    pub generated_at: String,
    pub nodes: Vec<Node>,
    pub edges: Vec<Edge>,
}

#[derive(Debug, Serialize)]
pub struct SupplementInfo {
    pub source_id: String,
    pub generated_at: String,
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct FollowUp {
    pub claim_id: String,
    pub responsible_source: String,
    pub next_step: String,
    pub as_of: String,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CaseBinding {
    pub schema: String,
    pub node_id: String,
    pub repository_id: String,
    pub case_source: String,
    pub case_id: String,
    pub candidate: String,
    #[serde(default)]
    pub followups: Vec<FollowUp>,
}

#[derive(Debug, Serialize)]
pub struct Attachment {
    pub node_id: String,
    pub repository_id: String,
    pub case_source: String,
    pub case_id: String,
    pub candidate: String,
    pub snapshot: Snapshot,
    pub claims: Vec<crate::ClaimAssessment>,
    pub followups: Vec<FollowUp>,
    pub authority: &'static str,
}

#[derive(Debug, Serialize)]
pub struct Projection {
    pub schema: &'static str,
    pub source_schema: &'static str,
    pub source_id: String,
    pub source_revision: Option<String>,
    pub source_time_reported: String,
    pub freshness: &'static str,
    pub authority: &'static str,
    pub nodes: Vec<Node>,
    pub edges: Vec<Edge>,
    pub unresolved_endpoints: Vec<String>,
    pub attachments: Vec<Attachment>,
    pub scope: serde_json::Value,
    pub summary: serde_json::Value,
    pub problems: serde_json::Value,
    pub excluded_paths: serde_json::Value,
    pub symlinks: serde_json::Value,
    pub supplements: Vec<SupplementInfo>,
}

fn present(s: &str) -> bool {
    !s.trim().is_empty()
}

/// Keeps source identities and edges distinct. It does not dereference any source.
pub fn project(
    observation: Observation,
    source_id: &str,
    attachment: Option<(CaseBinding, Case)>,
) -> Result<Projection, String> {
    if observation.schema != "aethel.workspace.relationship-observation/v1" {
        return Err("unsupported landscape source schema".into());
    }
    if !present(source_id) || !present(&observation.generated_at) {
        return Err("landscape source and time are required".into());
    }
    let mut ids = HashSet::new();
    for n in &observation.nodes {
        if ![&n.id, &n.name, &n.kind].iter().all(|v| present(v)) {
            return Err("empty landscape node identity".into());
        }
        if !ids.insert(n.id.as_str()) {
            return Err(format!("duplicate landscape node id: {}", n.id));
        }
    }
    let mut missing = Vec::new();
    for e in &observation.edges {
        if ![&e.from, &e.to, &e.kind, &e.status, &e.evidence, &e.detail]
            .iter()
            .all(|v| present(v))
        {
            return Err("empty landscape relationship field".into());
        }
        for id in [&e.from, &e.to] {
            if !ids.contains(id.as_str()) && !missing.contains(id) {
                missing.push(id.clone());
            }
        }
    }
    missing.sort();
    let mut attachments = Vec::new();
    if let Some((b, case)) = attachment {
        if b.schema != "aethel.plm.landscape-case-binding/v1"
            || ![&b.node_id, &b.repository_id, &b.case_source, &b.case_id]
                .iter()
                .all(|v| present(v))
            || !matches!(b.candidate.len(), 40 | 64)
            || !b.candidate.bytes().all(|x| x.is_ascii_hexdigit())
        {
            return Err("invalid case binding".into());
        }
        let node = observation
            .nodes
            .iter()
            .find(|n| n.id == b.node_id)
            .ok_or("case binding node not found")?;
        if node.kind != "repository" || node.git_common_dir.as_deref() != Some(&b.repository_id) {
            return Err("case binding repository identity mismatch".into());
        }
        if case.schema != "aethel.plm.case/v1"
            || case.change.id != b.case_id
            || case.change.candidate.as_deref() != Some(&b.candidate)
        {
            return Err("case binding case or candidate mismatch".into());
        }
        // The existing evaluator validates the complete case, including its date and IDs.
        let assessed =
            crate::assess(case.clone()).map_err(|e| format!("invalid bound case: {e}"))?;
        for f in &b.followups {
            if ![&f.claim_id, &f.responsible_source, &f.next_step, &f.as_of]
                .iter()
                .all(|v| present(v))
                || !assessed.claims.iter().any(|c| c.id == f.claim_id)
            {
                return Err("invalid or foreign case follow-up".into());
            }
        }
        attachments.push(Attachment {
            node_id: b.node_id,
            repository_id: b.repository_id,
            case_source: b.case_source,
            case_id: b.case_id,
            candidate: b.candidate,
            snapshot: case.snapshot,
            claims: assessed.claims,
            followups: b.followups,
            authority: "explicit_source_assertion_only; identity_and_source_not_verified",
        });
    }
    Ok(Projection {
        schema: "aethel.plm.landscape-projection/v1",
        source_schema: "aethel.workspace.relationship-observation/v1",
        source_id: source_id.into(),
        source_revision: None,
        source_time_reported: observation.generated_at,
        freshness: "not_checked",
        authority: "source_assertions_only; source_and_authority_not_verified",
        nodes: observation
            .nodes
            .into_iter()
            .map(|mut n| {
                if n.areas.is_empty() {
                    let derived: &[&str] = match n.category.as_deref() {
                        Some("company" | "firma") => &["Firma"],
                        Some("factory" | "kernel") => &["Fabrik"],
                        Some("coding-agent") => &["Fabrik", "Plattform"],
                        Some("omega" | "aethel-app") => &["Produkte"],
                        Some("core" | "quality") => &["Plattform"],
                        _ => &[],
                    };
                    n.areas = derived.iter().map(|s| (*s).to_owned()).collect();
                }
                n
            })
            .collect(),
        edges: observation.edges,
        unresolved_endpoints: missing,
        attachments,
        scope: observation.scope,
        summary: observation.summary,
        problems: observation.problems,
        excluded_paths: observation.excluded_paths,
        symlinks: observation.symlinks,
        supplements: Vec::new(),
    })
}

/// Explicit, source-named additions are not folded into the original scan summary.
pub fn supplement(p: &mut Projection, mut extra: Supplement) -> Result<(), String> {
    if extra.schema != "aethel.plm.landscape-supplement/v1"
        || !present(&extra.source_id)
        || !present(&extra.generated_at)
    {
        return Err("invalid landscape supplement metadata".into());
    }
    let mut ids: HashSet<String> = p.nodes.iter().map(|n| n.id.clone()).collect();
    for n in &extra.nodes {
        if ![&n.id, &n.name, &n.kind].iter().all(|v| present(v)) || !ids.insert(n.id.clone()) {
            return Err("invalid or duplicate supplement node".into());
        }
    }
    for e in &mut extra.edges {
        if ![&e.from, &e.to, &e.kind, &e.status, &e.evidence, &e.detail]
            .iter()
            .all(|v| present(v))
            || !ids.contains(&e.from)
            || !ids.contains(&e.to)
        {
            return Err("invalid supplement relationship".into());
        }
        e.origin = Some(format!("supplement: {}", extra.source_id));
    }
    p.nodes.extend(extra.nodes);
    p.edges.extend(extra.edges);
    p.supplements.push(SupplementInfo {
        source_id: extra.source_id,
        generated_at: extra.generated_at,
    });
    Ok(())
}
