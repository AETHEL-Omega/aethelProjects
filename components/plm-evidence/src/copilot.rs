//! Minimal projection of an explicitly supplied Copilot goal; no execution or authority.
use crate::{EvidenceReference, ReportedResult};
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize)]
pub struct CopilotGoal {
    pub schema: String,
    pub goal_id: String,
    pub state: String,
    pub actor: String,
    pub agent_id: String,
    pub baseline_sha: String,
    pub compute_mode: String,
    pub updated_at: String,
}
#[derive(Debug, Serialize)]
pub struct CopilotObservation {
    pub schema: &'static str,
    pub source_schema: &'static str,
    pub goal_id: String,
    pub reported_state: String,
    pub reported_actor: String,
    pub reported_agent_id: String,
    pub reported_compute_mode: String,
    pub updated_at_reported: String,
    pub actual_inference_location: Option<String>,
    pub freshness: &'static str,
    pub assessment: &'static str,
    pub evidence: EvidenceReference,
}
pub fn goal_observation(
    goal: CopilotGoal,
    expected_goal: &str,
    source_id: &str,
    evidence_id: &str,
) -> Result<CopilotObservation, String> {
    if goal.schema != "aix.copilot_goal.v1" {
        return Err("unsupported Copilot goal schema".into());
    }
    if [
        expected_goal,
        source_id,
        evidence_id,
        &goal.goal_id,
        &goal.state,
        &goal.actor,
        &goal.agent_id,
        &goal.baseline_sha,
        &goal.compute_mode,
        &goal.updated_at,
    ]
    .iter()
    .any(|v| v.trim().is_empty())
    {
        return Err("empty Copilot goal field".into());
    }
    let id = goal.goal_id.as_bytes();
    if id.len() != 17
        || !goal.goal_id.starts_with("goal-")
        || !id[5..].iter().all(u8::is_ascii_hexdigit)
    {
        return Err("invalid goal ID".into());
    }
    if goal.goal_id != expected_goal {
        return Err("goal ID does not match selector".into());
    }
    if !matches!(goal.baseline_sha.len(), 40 | 64)
        || !goal.baseline_sha.bytes().all(|b| b.is_ascii_hexdigit())
    {
        return Err("invalid reported baseline SHA".into());
    }
    Ok(CopilotObservation { schema:"aethel.plm.copilot-observation/v1",source_schema:"aix.copilot_goal.v1",goal_id:goal.goal_id,reported_state:goal.state,reported_actor:goal.actor,reported_agent_id:goal.agent_id,reported_compute_mode:goal.compute_mode,updated_at_reported:goal.updated_at,actual_inference_location:None,freshness:"not_checked",assessment:"source_assertion_only; source_and_authority_not_verified",evidence:EvidenceReference{id:evidence_id.into(),source:"aix.copilot_goal.v1 (supplied goal)".into(),source_id:source_id.into(),revision_or_digest:None,kind:"copilot_goal".into(),candidate:Some(goal.baseline_sha),provenance:"Reported goal baseline only; not a result, review, candidate, gate, lease, or inference location.".into(),reported_result:ReportedResult::Unknown,explanation:None,verified:false} })
}
