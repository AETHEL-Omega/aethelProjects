use plm_evidence::{
    landscape::{project, CaseBinding, Observation},
    Case,
};
use serde_json::{json, Value};

fn observation() -> Value {
    serde_json::from_str(include_str!("../fixtures/landscape-historical.json")).unwrap()
}
fn binding() -> Value {
    serde_json::from_str(include_str!("../fixtures/y1-landscape-binding.json")).unwrap()
}
fn case() -> Value {
    serde_json::from_str(include_str!("../fixtures/y1-historical.json")).unwrap()
}
fn run(obs: Value, binding: Option<(Value, Value)>) -> Result<Value, String> {
    let input: Observation = serde_json::from_value(obs).unwrap();
    let pair: Option<(CaseBinding, Case)> = binding.map(|(b, c)| {
        (
            serde_json::from_value(b).unwrap(),
            serde_json::from_value(c).unwrap(),
        )
    });
    Ok(serde_json::to_value(project(input, "selected source", pair)?).unwrap())
}

#[test]
fn projection_preserves_separate_identities_multiple_edges_and_reported_status() {
    let result = run(observation(), Some((binding(), case()))).unwrap();
    let nodes = result["nodes"].as_array().unwrap();
    assert!(nodes
        .iter()
        .any(|n| n["id"] == "repo:ed4da66dacb79098" && n["name"] == "aethelBrowser"));
    assert!(nodes
        .iter()
        .any(|n| n["id"] == "registry:2c1f33a64ac8e676" && n["name"] == "aethelBrowser"));
    let edges = result["edges"].as_array().unwrap();
    assert!(edges
        .iter()
        .any(|e| e["from"] == "registry:2c1f33a64ac8e676" && e["status"] == "ungeprüft"));
    assert!(
        edges
            .iter()
            .filter(|e| e["from"] == "repo:ed4da66dacb79098" && e["to"] == "repo:1eeab475f9154add")
            .count()
            > 1
    );
    assert_eq!(result["freshness"], "not_checked");
    assert_eq!(result["source_revision"], Value::Null);
    assert!(result["attachments"][0]["authority"]
        .as_str()
        .unwrap()
        .contains("not_verified"));
}

#[test]
fn ambiguous_id_rejected_but_missing_relationship_endpoint_is_not_hidden() {
    let mut obs = observation();
    let duplicate = obs["nodes"][0].clone();
    obs["nodes"].as_array_mut().unwrap().push(duplicate);
    assert!(run(obs, None).unwrap_err().contains("duplicate"));
    let mut obs = observation();
    obs["edges"].as_array_mut().unwrap().push(json!({"from":"missing:id","to":"repo:ed4da66dacb79098","type":"reported","status":"ungeprüft","evidence":"source","detail":"unknown target"}));
    let result = run(obs, None).unwrap();
    assert!(result["unresolved_endpoints"]
        .as_array()
        .unwrap()
        .contains(&json!("missing:id")));
    assert!(result["edges"]
        .as_array()
        .unwrap()
        .iter()
        .any(|e| e["from"] == "missing:id"));
}

#[test]
fn explicit_case_binding_requires_exact_repository_identity_and_candidate() {
    let mut b = binding();
    b["repository_id"] = "another repo".into();
    assert!(run(observation(), Some((b, case())))
        .unwrap_err()
        .contains("repository identity mismatch"));
    let mut b = binding();
    b["node_id"] = "registry:2c1f33a64ac8e676".into();
    assert!(run(observation(), Some((b, case())))
        .unwrap_err()
        .contains("repository identity mismatch"));
    let mut changed = case();
    changed["change"]["candidate"] = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa".into();
    assert!(run(observation(), Some((binding(), changed)))
        .unwrap_err()
        .contains("candidate mismatch"));
    let result = run(observation(), None).unwrap();
    assert!(result["attachments"].as_array().unwrap().is_empty());
    let mut b = binding();
    b["followups"][0]["claim_id"] = "foreign-claim".into();
    assert!(run(observation(), Some((b, case())))
        .unwrap_err()
        .contains("foreign case follow-up"));
}

#[test]
fn explicit_supplement_keeps_original_summary_and_provenance() {
    let obs: Observation = serde_json::from_value(observation()).unwrap();
    let mut projection = project(obs, "snapshot", None).unwrap();
    let before = projection.nodes.len();
    let v = json!({"schema":"aethel.plm.landscape-supplement/v1", "source_id":"manifest", "generated_at":"date", "nodes":[{"id":"component:lambda","name":"Lambda","kind":"komponente"}], "edges":[{"from":"repo:ed4da66dacb79098","to":"component:lambda","type":"declared","status":"geplant","evidence":"manifest","detail":"source assertion"}]});
    plm_evidence::landscape::supplement(
        &mut projection,
        serde_json::from_value(v.clone()).unwrap(),
    )
    .unwrap();
    assert_eq!(projection.nodes.len(), before + 1);
    assert_eq!(
        projection.edges.last().unwrap().origin.as_deref(),
        Some("supplement: manifest")
    );
    assert_eq!(projection.supplements.len(), 1);
    assert!(plm_evidence::landscape::supplement(
        &mut projection,
        serde_json::from_value(v).unwrap()
    )
    .is_err());
}

#[test]
fn changed_candidate_does_not_turn_old_login_or_test_report_into_matching_evidence() {
    let mut changed: Case = serde_json::from_value(case()).unwrap();
    changed.change.candidate = Some("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa".into());
    let assessed = plm_evidence::assess(changed).unwrap();
    let gate = assessed.claims.iter().find(|c| c.id == "gate").unwrap();
    let login = assessed.claims.iter().find(|c| c.id == "login").unwrap();
    assert_eq!(gate.references[0].candidate_binding, "different");
    assert_eq!(login.references[0].candidate_binding, "different");
    assert!(!gate.gaps.is_empty() && !login.gaps.is_empty());
}

#[test]
fn cli_requires_both_case_and_binding_and_does_not_follow_paths() {
    let bin = env!("CARGO_BIN_EXE_plm-evidence");
    let root = env!("CARGO_MANIFEST_DIR");
    let input = format!("{root}/fixtures/landscape-historical.json");
    let bind = format!("{root}/fixtures/y1-landscape-binding.json");
    let bad = std::process::Command::new(bin)
        .args([
            "landscape-project",
            "--input",
            &input,
            "--format",
            "json",
            "--source-id",
            "source",
            "--binding",
            &bind,
        ])
        .output()
        .unwrap();
    assert_eq!(bad.status.code(), Some(2));
    let ok = std::process::Command::new(bin)
        .args([
            "landscape-project",
            "--input",
            &input,
            "--format",
            "json",
            "--source-id",
            "/nonexistent/source",
        ])
        .output()
        .unwrap();
    assert_eq!(ok.status.code(), Some(0));
    let result: Value = serde_json::from_slice(&ok.stdout).unwrap();
    assert_eq!(result["source_id"], "/nonexistent/source");
    assert!(result["attachments"].as_array().unwrap().is_empty());
}
