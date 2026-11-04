use plm_evidence::{
    copilot::{goal_observation, CopilotGoal},
    ReportedResult,
};
use serde_json::{json, Value};
fn raw() -> Value {
    json!({"schema":"aix.copilot_goal.v1","goal_id":"goal-123456abcdef","state":"COMPLETED","actor":"claude","agent_id":"test-agent","baseline_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","compute_mode":"LOCAL","updated_at":"reported-time","prompt":"private text must not be projected","artifacts":{"events":"/tmp/DO_NOT_OPEN"}})
}
fn parse(v: Value) -> CopilotGoal {
    serde_json::from_value(v).unwrap()
}
#[test]
fn state_and_local_mode_do_not_create_authority_or_inference_claim() {
    let o = goal_observation(parse(raw()), "goal-123456abcdef", "source", "evidence").unwrap();
    assert_eq!(o.reported_state, "COMPLETED");
    assert_eq!(o.actual_inference_location, None);
    assert_eq!(o.freshness, "not_checked");
    assert_eq!(o.evidence.reported_result, ReportedResult::Unknown);
    assert!(!o.evidence.verified);
    let text = serde_json::to_string(&o).unwrap();
    assert!(!text.contains("private text"));
    assert!(!text.contains("DO_NOT_OPEN"));
    assert!(text.contains("not a result, review, candidate, gate"));
}
#[test]
fn schema_selector_and_baseline_are_checked() {
    let mut v = raw();
    v["schema"] = "aix.copilot_goal.v2".into();
    assert!(goal_observation(parse(v), "goal-123456abcdef", "s", "e").is_err());
    assert!(goal_observation(parse(raw()), "goal-abcdef123456", "s", "e").is_err());
    let mut v = raw();
    v["baseline_sha"] = "unbound".into();
    assert!(goal_observation(parse(v), "goal-123456abcdef", "s", "e").is_err());
    let mut v = raw();
    v["goal_id"] = "invalid".into();
    assert!(goal_observation(parse(v), "invalid", "s", "e").is_err());
}
#[test]
fn cli_requires_selector_and_does_not_copy_private_text() {
    let path = std::env::temp_dir().join(format!("copilot-synthetic-{}.json", std::process::id()));
    std::fs::write(&path, serde_json::to_vec(&raw()).unwrap()).unwrap();
    let bin = env!("CARGO_BIN_EXE_plm-evidence");
    let file = path.to_str().unwrap();
    let bad = std::process::Command::new(bin)
        .args(["copilot-observation", "--input", file, "--format", "json"])
        .output()
        .unwrap();
    assert_eq!(bad.status.code(), Some(2));
    let out = std::process::Command::new(bin)
        .args([
            "copilot-observation",
            "--input",
            file,
            "--format",
            "json",
            "--goal-id",
            "goal-123456abcdef",
            "--source-id",
            "s",
            "--evidence-id",
            "e",
        ])
        .output()
        .unwrap();
    assert_eq!(out.status.code(), Some(0));
    assert!(!String::from_utf8(out.stdout)
        .unwrap()
        .contains("private text"));
    std::fs::remove_file(path).unwrap();
}
