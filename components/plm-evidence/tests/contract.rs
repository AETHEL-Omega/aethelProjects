use plm_evidence::{assess, Case, ReportedResult};
use std::{fs, process::Command};
fn fixture() -> Case {
    serde_json::from_str(include_str!("../fixtures/y1-historical.json")).unwrap()
}
fn json(c: Case) -> String {
    serde_json::to_string(&assess(c).unwrap()).unwrap()
}
#[test]
fn y1_login_and_gate_are_unproven() {
    let a = assess(fixture()).unwrap();
    for id in ["login", "gate"] {
        let claim = a.claims.iter().find(|c| c.id == id).unwrap();
        assert!(claim
            .gaps
            .iter()
            .any(|g| g.code == "missing_applicable_evidence"));
        assert!(claim
            .references
            .iter()
            .all(|r| r.assurance == "source_assertion_only"));
    }
}
#[test]
fn binding_and_verified_flag_do_not_grant_authority() {
    let mut c = fixture();
    c.claims[0].required_kind = "unit_test".into();
    c.evidence[0].candidate = Some("other".into());
    c.evidence[0].verified = true;
    let a = assess(c.clone()).unwrap();
    let claim = a.claims.iter().find(|x| x.id == "login").unwrap();
    assert_eq!(claim.references[0].candidate_binding, "different");
    assert_eq!(claim.references[0].assurance, "source_assertion_only");
    c.evidence[0].candidate = None;
    let a = assess(c).unwrap();
    assert_eq!(
        a.claims
            .iter()
            .find(|x| x.id == "login")
            .unwrap()
            .references[0]
            .candidate_binding,
        "unknown"
    );
}
#[test]
fn conflict_and_non_applicability() {
    let mut c = fixture();
    c.claims[0].required_kind = "unit_test".into();
    let mut e = c.evidence[0].clone();
    e.id = "second".into();
    e.reported_result = ReportedResult::Fail;
    c.claims[0].evidence_ids.push(e.id.clone());
    c.evidence.push(e);
    let a = assess(c.clone()).unwrap();
    assert!(a
        .claims
        .iter()
        .find(|x| x.id == "login")
        .unwrap()
        .gaps
        .iter()
        .any(|g| g.code == "contradictory_results"));
    c.evidence[0].reported_result = ReportedResult::NotApplicable;
    assert!(assess(c.clone()).is_err());
    c.evidence[0].explanation = Some("not relevant for this scenario".into());
    assert!(assess(c)
        .unwrap()
        .claims
        .iter()
        .find(|x| x.id == "login")
        .unwrap()
        .gaps
        .iter()
        .any(|g| g.code == "not_applicable"));
}
#[test]
fn invalid_structure_is_rejected() {
    let mut c = fixture();
    c.schema = "aethel.plm.case/v2".into();
    assert!(assess(c).is_err());
    let mut c = fixture();
    c.claims.push(c.claims[0].clone());
    assert!(assess(c).is_err());
    let mut c = fixture();
    c.evidence.push(c.evidence[0].clone());
    assert!(assess(c).is_err());
    let mut c = fixture();
    c.claims[0].evidence_ids.push("missing".into());
    assert!(assess(c).is_err());
}
#[test]
fn deterministic_under_reordering() {
    let c = fixture();
    let expected = json(c.clone());
    assert_eq!(expected, json(c.clone()));
    let mut c = c;
    c.claims.reverse();
    c.evidence.reverse();
    for claim in &mut c.claims {
        claim.evidence_ids.reverse();
    }
    assert_eq!(expected, json(c));
}
#[test]
fn cli_does_not_execute_or_open_references() {
    let dir = std::env::temp_dir().join(format!("plm-evidence-test-{}", std::process::id()));
    fs::create_dir_all(&dir).unwrap();
    let marker = dir.join("marker");
    let mut c = fixture();
    c.evidence[0].source = format!("$(touch {})", marker.display());
    c.evidence[0].source_id = dir.join("nonexistent").display().to_string();
    let path = dir.join("case.json");
    fs::write(&path, serde_json::to_vec(&c).unwrap()).unwrap();
    let out = Command::new(env!("CARGO_BIN_EXE_plm-evidence"))
        .args([
            "assess",
            "--input",
            path.to_str().unwrap(),
            "--format",
            "json",
        ])
        .output()
        .unwrap();
    assert!(out.status.success());
    assert!(!marker.exists());
    let bad = Command::new(env!("CARGO_BIN_EXE_plm-evidence"))
        .args([
            "assess",
            "--input",
            dir.join("absent").to_str().unwrap(),
            "--format",
            "json",
        ])
        .output()
        .unwrap();
    assert_eq!(bad.status.code(), Some(3));
    fs::write(&path, "{}").unwrap();
    let bad = Command::new(env!("CARGO_BIN_EXE_plm-evidence"))
        .args([
            "assess",
            "--input",
            path.to_str().unwrap(),
            "--format",
            "json",
        ])
        .output()
        .unwrap();
    assert_eq!(bad.status.code(), Some(2));
    fs::remove_dir_all(dir).unwrap();
}

#[test]
fn independent_dimensions_and_empty_references() {
    let mut c = fixture();
    c.evidence[0].candidate = Some("other".into());
    let a = assess(c).unwrap();
    let login = a.claims.iter().find(|x| x.id == "login").unwrap();
    assert_eq!(login.references[0].kind_match, "different");
    assert_eq!(login.references[0].candidate_binding, "different");
    for code in [
        "wrong_kind",
        "different_candidate",
        "missing_applicable_evidence",
    ] {
        assert!(login.gaps.iter().any(|g| g.code == code));
    }
    let review = a.claims.iter().find(|x| x.id == "review").unwrap();
    assert!(review.gaps.iter().any(|g| g.code == "missing_evidence"));
    assert!(!review
        .gaps
        .iter()
        .any(|g| g.code == "missing_applicable_evidence"));
}

#[test]
fn results_and_non_applicability_are_distinct() {
    for (result, expected) in [
        (ReportedResult::Fail, "reported_failure"),
        (ReportedResult::Unknown, "reported_unknown"),
        (ReportedResult::NotApplicable, "not_applicable"),
    ] {
        let mut c = fixture();
        c.claims[0].required_kind = "unit_test".into();
        c.evidence[0].reported_result = result;
        if result == ReportedResult::NotApplicable {
            c.evidence[0].explanation = Some("Scenario does not apply to this reference".into());
        }
        let a = assess(c).unwrap();
        let login = a.claims.iter().find(|x| x.id == "login").unwrap();
        assert!(login.gaps.iter().any(|g| g.code == expected));
        assert_eq!(
            login
                .gaps
                .iter()
                .any(|g| g.code == "missing_applicable_evidence"),
            result == ReportedResult::NotApplicable
        );
    }
}

#[test]
fn omitted_optional_fields_stay_unknown() {
    let mut value: serde_json::Value =
        serde_json::from_str(include_str!("../fixtures/y1-historical.json")).unwrap();
    value["change"].as_object_mut().unwrap().remove("candidate");
    value["change"]
        .as_object_mut()
        .unwrap()
        .remove("product_reference");
    let e = value["evidence"][0].as_object_mut().unwrap();
    for field in ["candidate", "revision_or_digest", "explanation", "verified"] {
        e.remove(field);
    }
    let a = assess(serde_json::from_value(value).unwrap()).unwrap();
    assert!(a.change.product_reference.is_none());
    assert_eq!(
        a.claims
            .iter()
            .find(|c| c.id == "login")
            .unwrap()
            .references[0]
            .candidate_binding,
        "unknown"
    );
}
