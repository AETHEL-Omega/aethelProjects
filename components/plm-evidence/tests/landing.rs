use plm_evidence::landing::{observe, Report};
use serde_json::json;

fn report() -> Report {
    serde_json::from_value(json!({
        "ok": false, "reason": "no_structured_verdict_for_head", "verdicts": [],
        "other_heads": [], "rejected_lines": [], "covered_by_seal": [],
        "unstructured": 0, "notes": {}
    }))
    .unwrap()
}

#[test]
fn landing_report_is_only_a_source_assertion_and_head_is_supplied() {
    let p = observe(
        report(),
        "repo-id",
        &"a".repeat(40),
        "report-source",
        "2026-11-04",
    )
    .unwrap();
    assert!(!p.reported_ok);
    assert_eq!(p.reported_reason, "no_structured_verdict_for_head");
    assert_eq!(p.head_supplied, "a".repeat(40));
    assert_eq!(p.freshness, "not_checked");
    assert!(p.authority.contains("not_verified"));
}

#[test]
fn explicit_full_head_repository_source_and_time_are_required() {
    assert!(observe(report(), "repo", "abc", "source", "date").is_err());
    assert!(observe(report(), "", &"a".repeat(40), "source", "date").is_err());
    assert!(observe(report(), "repo", &"a".repeat(40), "", "date").is_err());
    assert!(observe(report(), "repo", &"a".repeat(40), "source", "").is_err());
}
