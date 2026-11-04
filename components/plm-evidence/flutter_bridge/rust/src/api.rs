//! In-memory adapter to the existing evidence core; no source I/O or authority.
use serde::{de::DeserializeOwned, Serialize};

const MAX_INPUT_BYTES: usize = 8 * 1024 * 1024;

fn evaluate<I: DeserializeOwned, O: Serialize>(
    input: &str,
    evaluator: impl FnOnce(I) -> Result<O, String>,
) -> Result<String, String> {
    if input.len() > MAX_INPUT_BYTES {
        return Err("input exceeds 8 MiB limit".into());
    }
    let input = serde_json::from_str(input).map_err(|e| format!("invalid JSON: {e}"))?;
    let assessment = evaluator(input)?;
    serde_json::to_string(&assessment).map_err(|e| format!("output JSON: {e}"))
}

pub fn assess_case_json(input: String) -> Result<String, String> {
    evaluate(&input, plm_evidence::assess)
}

pub fn assess_quality_json(input: String) -> Result<String, String> {
    evaluate(&input, plm_evidence::quality::assess_quality)
}

pub fn assess_linked_json(input: String) -> Result<String, String> {
    evaluate(&input, plm_evidence::link::assess_linked)
}
