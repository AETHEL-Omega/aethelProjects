//! Presents one explicitly supplied Landing CLI report without becoming a landing authority.
use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Debug, Deserialize)]
pub struct Report {
    pub ok: bool,
    pub reason: String,
    pub verdicts: Vec<Value>,
    pub other_heads: Vec<String>,
    pub rejected_lines: Vec<Value>,
    pub covered_by_seal: Vec<String>,
    pub unstructured: u64,
    pub notes: Value,
    #[serde(default)]
    pub unfulfilled: Option<Value>,
    #[serde(default)]
    pub inherited_from: Option<String>,
}

#[derive(Debug, Serialize)]
pub struct Observation {
    pub schema: &'static str,
    pub repository_id: String,
    pub head_supplied: String,
    pub source_id: String,
    pub observed_at_supplied: String,
    pub reported_ok: bool,
    pub reported_reason: String,
    pub reported_verdicts: Vec<Value>,
    pub reported_other_heads: Vec<String>,
    pub reported_rejected_lines: Vec<Value>,
    pub reported_covered_by_seal: Vec<String>,
    pub reported_unstructured: u64,
    pub reported_notes: Value,
    pub reported_unfulfilled: Option<Value>,
    pub reported_inherited_from: Option<String>,
    pub freshness: &'static str,
    pub authority: &'static str,
}

/// The CLI's `--head` and repository are supplied separately: a report alone does not authenticate either.
pub fn observe(
    report: Report,
    repository_id: &str,
    head: &str,
    source: &str,
    time: &str,
) -> Result<Observation, String> {
    if [repository_id, source, time, &report.reason]
        .iter()
        .any(|s| s.trim().is_empty())
        || !matches!(head.len(), 40 | 64)
        || !head.bytes().all(|b| b.is_ascii_hexdigit())
    {
        return Err("invalid Landing report selector or metadata".into());
    }
    Ok(Observation {
        schema: "aethel.plm.landing-observation/v1",
        repository_id: repository_id.into(),
        head_supplied: head.into(),
        source_id: source.into(),
        observed_at_supplied: time.into(),
        reported_ok: report.ok,
        reported_reason: report.reason,
        reported_verdicts: report.verdicts,
        reported_other_heads: report.other_heads,
        reported_rejected_lines: report.rejected_lines,
        reported_covered_by_seal: report.covered_by_seal,
        reported_unstructured: report.unstructured,
        reported_notes: report.notes,
        reported_unfulfilled: report.unfulfilled,
        reported_inherited_from: report.inherited_from,
        freshness: "not_checked",
        authority: "reported_only; head_source_and_authority_not_verified",
    })
}
