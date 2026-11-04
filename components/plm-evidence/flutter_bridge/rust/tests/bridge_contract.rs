use aethel_evidence_bridge::api::{assess_case_json, assess_linked_json, assess_quality_json};

#[test]
fn native_bridge_matches_the_existing_case_evaluator() {
    let raw = include_str!("../../../fixtures/y1-historical.json");
    let input = serde_json::from_str(raw).unwrap();
    let direct = serde_json::to_value(plm_evidence::assess(input).unwrap()).unwrap();
    let via_bridge: serde_json::Value =
        serde_json::from_str(&assess_case_json(raw.into()).unwrap()).unwrap();
    assert_eq!(direct, via_bridge);
}

#[test]
fn native_bridge_keeps_the_existing_quality_and_linked_contracts() {
    let quality = include_str!("../../../fixtures/quality-synthetic.json");
    let linked = include_str!("../../../fixtures/linked-synthetic.json");
    let q: serde_json::Value =
        serde_json::from_str(&assess_quality_json(quality.into()).unwrap()).unwrap();
    let l: serde_json::Value =
        serde_json::from_str(&assess_linked_json(linked.into()).unwrap()).unwrap();
    assert_eq!(q["schema"], "aethel.plm.quality-assessment/v1");
    assert_eq!(l["schema"], "aethel.plm.linked-assessment/v1");
    assert!(assess_case_json("{".into()).is_err());
    assert!(assess_case_json("x".repeat(8 * 1024 * 1024 + 1)).is_err());
}
