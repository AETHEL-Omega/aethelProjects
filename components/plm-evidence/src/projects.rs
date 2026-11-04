//! Narrow reader for an explicit aethelProjects pm-input export. No source is opened.
use crate::{EvidenceReference, ReportedResult};
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize)]
pub struct ProjectExport {
    pub schema: String,
    pub generated_at: String,
    pub scan_generated_at: String,
    pub projects: Vec<Project>,
}
#[derive(Debug, Deserialize)]
pub struct Project {
    pub repository_id: String,
    #[serde(deserialize_with = "required_optional_head")]
    pub observed_head: Option<String>,
}
fn required_optional_head<'de, D: serde::Deserializer<'de>>(
    d: D,
) -> Result<Option<String>, D::Error> {
    Option::<String>::deserialize(d)
}
#[derive(Debug, Serialize)]
pub struct ProjectProjection {
    pub schema: &'static str,
    pub source_schema: &'static str,
    pub product_reference: Option<String>,
    pub repository_id: String,
    pub export_generated_at_reported: String,
    pub scan_generated_at_reported: String,
    pub freshness: &'static str,
    pub assessment: &'static str,
    pub evidence: EvidenceReference,
}
fn not_empty(value: &str) -> bool {
    !value.trim().is_empty()
}
/// Only reads the supplied value, selects an exact local repository identity, and never verifies it.
pub fn project_export(
    export: ProjectExport,
    repository_id: &str,
    source_id: &str,
    evidence_id: &str,
) -> Result<ProjectProjection, String> {
    if export.schema != "aethel.projects.pm-input/v1" {
        return Err("unsupported project export schema".into());
    }
    if ![
        repository_id,
        source_id,
        evidence_id,
        &export.generated_at,
        &export.scan_generated_at,
    ]
    .iter()
    .all(|x| not_empty(x))
    {
        return Err("empty project export/selector field".into());
    }
    let mut matches = export
        .projects
        .into_iter()
        .filter(|p| p.repository_id == repository_id);
    let project = matches.next().ok_or("repository identity not found")?;
    if matches.next().is_some() {
        return Err("ambiguous repository identity".into());
    }
    if let Some(head) = &project.observed_head {
        if !matches!(head.len(), 40 | 64) || !head.bytes().all(|x| x.is_ascii_hexdigit()) {
            return Err("invalid reported Git head".into());
        }
    }
    Ok(ProjectProjection {
        schema:"aethel.plm.project-observation/v1", source_schema:"aethel.projects.pm-input/v1",
        product_reference:None, repository_id:repository_id.into(),
        export_generated_at_reported:export.generated_at, scan_generated_at_reported:export.scan_generated_at,
        freshness:"not_checked", assessment:"source_assertion_only; source_and_authority_not_verified",
        evidence: EvidenceReference { id:evidence_id.into(),source:"aethel.projects.pm-input/v1 (supplied export)".into(),source_id:source_id.into(),revision_or_digest:None,kind:"project_dossier".into(),candidate:project.observed_head,provenance:"Reported by supplied Projects export; no repository, document, freshness or producer verification performed.".into(),reported_result:ReportedResult::Unknown,explanation:None,verified:false },
    })
}
