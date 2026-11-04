use plm_evidence::{
    projects::{project_export, ProjectExport},
    ReportedResult,
};
use serde_json::json;
fn export() -> serde_json::Value {
    json!({"schema":"aethel.projects.pm-input/v1","generated_at":"reported-export","scan_generated_at":"reported-scan","projects":[{"repository_id":"synthetic-repo","observed_head":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","name":"not a product id","documents":[{"path":"/absent/$(touch no)"}]}]})
}
fn parse(v: serde_json::Value) -> ProjectExport {
    serde_json::from_value(v).unwrap()
}
#[test]
fn source_data_is_never_promoted_to_verified_product_evidence() {
    let p = project_export(parse(export()), "synthetic-repo", "export-1", "evidence-1").unwrap();
    assert_eq!(p.product_reference, None);
    assert_eq!(p.freshness, "not_checked");
    assert!(!p.evidence.verified);
    assert_eq!(p.evidence.reported_result, ReportedResult::Unknown);
    assert_eq!(
        p.evidence.candidate.as_deref(),
        Some("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    );
    assert_eq!(p.export_generated_at_reported, "reported-export");
    assert_eq!(p.scan_generated_at_reported, "reported-scan");
}
#[test]
fn explicit_selector_version_and_nonambiguous_repository_are_mandatory() {
    let mut v = export();
    v["schema"] = "future".into();
    assert!(project_export(parse(v), "synthetic-repo", "s", "e").is_err());
    assert!(project_export(parse(export()), "other", "s", "e").is_err());
    let mut v = export();
    let row = v["projects"][0].clone();
    v["projects"].as_array_mut().unwrap().push(row);
    assert!(project_export(parse(v), "synthetic-repo", "s", "e").is_err());
    assert!(project_export(parse(export()), "synthetic-repo", "", "e").is_err());
}
#[test]
fn malformed_head_is_rejected_and_missing_head_is_unknown() {
    let mut v = export();
    v["projects"][0]["observed_head"] = "not-a-sha".into();
    assert!(project_export(parse(v), "synthetic-repo", "s", "e").is_err());
    let mut v = export();
    v["projects"][0]["observed_head"] = serde_json::Value::Null;
    assert!(project_export(parse(v), "synthetic-repo", "s", "e")
        .unwrap()
        .evidence
        .candidate
        .is_none());
}
#[test]
fn evidence_can_feed_existing_assessment_without_becoming_success() {
    let p = project_export(parse(export()), "synthetic-repo", "s", "e").unwrap();
    let mut c: plm_evidence::Case =
        serde_json::from_str(include_str!("../fixtures/y1-historical.json")).unwrap();
    c.change.candidate = p.evidence.candidate.clone();
    c.claims[0].required_kind = "project_dossier".into();
    c.claims[0].evidence_ids = vec![p.evidence.id.clone()];
    c.evidence.push(p.evidence);
    let a = plm_evidence::assess(c).unwrap();
    let login = a.claims.iter().find(|x| x.id == "login").unwrap();
    assert_eq!(login.references[0].assurance, "source_assertion_only");
    assert!(login
        .gaps
        .iter()
        .any(|g| g.code == "independent_verification_missing"));
}
#[test]
fn cli_requires_explicit_selection() {
    let path =
        std::env::temp_dir().join(format!("projects-export-test-{}.json", std::process::id()));
    std::fs::write(&path, serde_json::to_vec(&export()).unwrap()).unwrap();
    let bin = env!("CARGO_BIN_EXE_plm-evidence");
    let file = path.to_str().unwrap();
    let bad = std::process::Command::new(bin)
        .args(["project-observation", "--input", file, "--format", "json"])
        .output()
        .unwrap();
    assert_eq!(bad.status.code(), Some(2));
    let ok = std::process::Command::new(bin)
        .args([
            "project-observation",
            "--input",
            file,
            "--format",
            "json",
            "--repository-id",
            "synthetic-repo",
            "--source-id",
            "source-1",
            "--evidence-id",
            "ev-1",
        ])
        .output()
        .unwrap();
    assert_eq!(ok.status.code(), Some(0));
    let v: serde_json::Value = serde_json::from_slice(&ok.stdout).unwrap();
    assert_eq!(v["product_reference"], serde_json::Value::Null);
    assert_eq!(v["freshness"], "not_checked");
    assert_eq!(v["evidence"]["reported_result"], "unknown");
    std::fs::remove_file(path).unwrap();
}

#[test]
fn missing_head_is_a_structure_error_while_explicit_null_is_unknown() {
    let mut v = export();
    v["projects"][0]
        .as_object_mut()
        .unwrap()
        .remove("observed_head");
    assert!(serde_json::from_value::<ProjectExport>(v).is_err());
}
