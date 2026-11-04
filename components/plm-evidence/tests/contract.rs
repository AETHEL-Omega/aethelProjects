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

#[test]
fn outcome_matrix_preserves_scope_and_source_only_assurance() {
    for kind_matches in [false, true] {
        for binding in [None, Some("other"), Some("candidate")] {
            for outcome in [
                ReportedResult::Pass,
                ReportedResult::Fail,
                ReportedResult::Unknown,
                ReportedResult::NotApplicable,
            ] {
                let mut c = fixture();
                c.claims.truncate(1);
                c.evidence.truncate(1);
                c.change.candidate = Some("candidate".into());
                c.claims[0].required_kind = if kind_matches {
                    "unit_test"
                } else {
                    "real_login"
                }
                .into();
                c.evidence[0].candidate = binding.map(str::to_owned);
                c.evidence[0].reported_result = outcome;
                c.evidence[0].verified = true;
                c.evidence[0].explanation =
                    Some("Only this reference is declared inapplicable".into());
                let a = assess(c).unwrap();
                let claim = &a.claims[0];
                let applicable = kind_matches
                    && binding == Some("candidate")
                    && outcome != ReportedResult::NotApplicable;
                let has = |code| claim.gaps.iter().any(|g| g.code == code);
                assert_eq!(has("missing_applicable_evidence"), !applicable);
                assert_eq!(
                    has("reported_failure"),
                    applicable && outcome == ReportedResult::Fail
                );
                assert_eq!(
                    has("reported_unknown"),
                    applicable && outcome == ReportedResult::Unknown
                );
                assert!(has("independent_verification_missing"));
                assert_eq!(claim.references[0].assurance, "source_assertion_only");
                for gap in &claim.gaps {
                    for id in &gap.evidence_ids {
                        assert_eq!(id, "ua-chain");
                    }
                }
            }
        }
    }
}

#[test]
fn conflicts_link_only_comparable_evidence_and_ignore_input_order() {
    let mut c = fixture();
    c.claims[0].required_kind = "unit_test".into();
    let mut failure = c.evidence[0].clone();
    failure.id = "failure".into();
    failure.reported_result = ReportedResult::Fail;
    let mut foreign = failure.clone();
    foreign.id = "foreign".into();
    foreign.candidate = Some("other".into());
    c.claims[0]
        .evidence_ids
        .extend([failure.id.clone(), foreign.id.clone()]);
    c.evidence.extend([failure, foreign]);
    let a = assess(c.clone()).unwrap();
    let login = a.claims.iter().find(|c| c.id == "login").unwrap();
    assert_eq!(
        login
            .gaps
            .iter()
            .find(|g| g.code == "contradictory_results")
            .unwrap()
            .evidence_ids,
        ["failure", "ua-chain"]
    );
    let expected = json(c.clone());
    c.claims.reverse();
    c.evidence.reverse();
    for claim in &mut c.claims {
        claim.evidence_ids.reverse();
    }
    assert_eq!(expected, json(c));
}

#[test]
fn orphan_references_and_historical_context_are_not_silently_lost() {
    let mut c = fixture();
    c.claims.retain(|c| c.id == "login");
    let a = assess(c).unwrap();
    assert_eq!(
        a.unreferenced_evidence
            .iter()
            .map(|e| e.id.as_str())
            .collect::<Vec<_>>(),
        ["agent-report", "reported-tests"]
    );
    let text = plm_evidence::render_text(&a);
    assert!(text.contains("Historische Momentaufnahme: 2026-11-04; kein Live-Stand."));
    assert!(text.contains("Nicht zugeordnet: reported-tests"));
    for date in [
        "2026-02-29",
        "0000-01-01",
        "2026-13-01",
        "2026-01-00",
        "2026-11-31",
        "today",
    ] {
        let mut c = fixture();
        c.snapshot = plm_evidence::Snapshot::Historical {
            captured_on: date.into(),
        };
        assert!(assess(c).is_err(), "{date}");
    }
    let mut c = fixture();
    c.snapshot = plm_evidence::Snapshot::Historical {
        captured_on: "2024-02-29".into(),
    };
    assert!(assess(c).is_ok());
}

#[test]
fn text_escapes_controls_and_preserves_explanations() {
    let mut c = fixture();
    c.evidence[0].source = "evil\x1b[2J\nforged\u{202e}".into();
    c.evidence[0].reported_result = ReportedResult::NotApplicable;
    c.evidence[0].explanation = Some("scenario excluded".into());
    let text = plm_evidence::render_text(&assess(c).unwrap());
    assert!(!text.contains('\x1b'));
    assert!(!text.contains('\u{202e}'));
    assert!(!text.contains("\nforged"));
    assert!(text.contains("Berichtete Erklärung: scenario excluded"));
}

#[test]
fn empty_case_and_unknown_fields_are_structure_errors() {
    let mut c = fixture();
    c.claims.clear();
    assert!(assess(c).is_err());
    let mut value = serde_json::to_value(fixture()).unwrap();
    value["claims"][0]["approved"] = true.into();
    assert!(serde_json::from_value::<Case>(value).is_err());
    let mut c = fixture();
    c.claims[0].evidence_ids.push("ua-chain".into());
    assert!(assess(c).is_err());
}

#[cfg(unix)]
#[test]
fn stdout_failure_returns_io_exit_code_without_panic() {
    use std::os::{fd::OwnedFd, unix::net::UnixStream};
    use std::process::Stdio;
    let (writer, reader) = UnixStream::pair().unwrap();
    drop(reader);
    let fd: OwnedFd = writer.into();
    let out = Command::new(env!("CARGO_BIN_EXE_plm-evidence"))
        .args([
            "assess",
            "--input",
            concat!(env!("CARGO_MANIFEST_DIR"), "/fixtures/y1-historical.json"),
            "--format",
            "json",
        ])
        .stdout(Stdio::from(fd))
        .output()
        .unwrap();
    assert_eq!(out.status.code(), Some(3));
    let err = String::from_utf8(out.stderr).unwrap();
    assert!(err.contains("output I/O"));
    assert!(!err.contains("panicked"));
}

#[test]
fn cli_rejects_oversized_packages_and_usage_errors() {
    let path = std::env::temp_dir().join(format!("plm-limit-{}.json", std::process::id()));
    let file = fs::File::create(&path).unwrap();
    file.set_len(8 * 1024 * 1024 + 1).unwrap();
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
    fs::remove_file(path).unwrap();
    assert_eq!(out.status.code(), Some(2));
    assert!(out.stdout.is_empty());
    assert!(String::from_utf8(out.stderr).unwrap().contains("8 MiB"));
    for args in [
        vec!["assess"],
        vec!["assess", "--format", "xml", "--input", "absent"],
        vec![
            "assess", "--input", "absent", "--input", "again", "--format", "json",
        ],
    ] {
        let out = Command::new(env!("CARGO_BIN_EXE_plm-evidence"))
            .args(args)
            .output()
            .unwrap();
        assert_eq!(out.status.code(), Some(2));
        assert!(out.stdout.is_empty());
    }
}
