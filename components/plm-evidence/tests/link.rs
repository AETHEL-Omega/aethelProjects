use plm_evidence::link::{assess_linked, LinkedCase};
fn input() -> LinkedCase {
    serde_json::from_str(include_str!("../fixtures/linked-synthetic.json")).unwrap()
}
fn has(a: &plm_evidence::link::LinkAssessment, code: &str) -> bool {
    a.findings.iter().any(|f| f.code == code)
}
#[test]
fn links_preserve_claim_gaps_and_do_not_grant_authority() {
    let result = assess_linked(input()).unwrap();
    assert!(result
        .authority
        .contains("no_verification_or_authorisation"));
    assert!(has(&result, "link_not_independently_verified"));
    assert!(result.change.claims[0]
        .gaps
        .iter()
        .any(|g| g.code == "missing_evidence"));
    assert!(result.quality.transitions[0]
        .findings
        .iter()
        .any(|g| g.code == "effectiveness_missing"));
    assert!(!has(&result, "claim_unlinked"));
}
#[test]
fn candidate_mismatch_and_unknown_are_distinct() {
    let mut c = input();
    c.change_case.change.candidate = Some("different".into());
    assert!(has(&assess_linked(c).unwrap(), "different_candidate"));
    let mut c = input();
    c.change_case.change.candidate = None;
    assert!(has(&assess_linked(c).unwrap(), "candidate_binding_unknown"));
}
#[test]
fn missing_associations_are_explicit() {
    let mut c = input();
    c.links.clear();
    let r = assess_linked(c).unwrap();
    for code in ["claim_unlinked", "issue_unlinked", "action_unlinked"] {
        assert!(has(&r, code));
    }
}
#[test]
fn malformed_and_cross_scope_links_are_rejected() {
    let mut c = input();
    c.schema = "aethel.plm.linked-case/v2".into();
    assert!(assess_linked(c).is_err());
    let mut c = input();
    c.links.push(c.links[0].clone());
    assert!(assess_linked(c).is_err());
    let mut c = input();
    let mut other = c.links[0].clone();
    other.id = "second".into();
    c.links.push(other);
    assert!(assess_linked(c).is_err());
    for n in 0..3 {
        let mut c = input();
        match n {
            0 => c.links[0].claim_id = "absent".into(),
            1 => c.links[0].action_id = "absent".into(),
            _ => c.links[0].issue_id = "absent".into(),
        };
        assert!(assess_linked(c).is_err());
    }
    let mut c = input();
    let mut issue = c.quality_case.issues[0].clone();
    issue.id = "other".into();
    c.quality_case.issues.push(issue);
    c.links[0].issue_id = "other".into();
    assert!(assess_linked(c).is_err());
    let mut c = input();
    c.quality_case.schema = "unsupported".into();
    assert!(assess_linked(c).is_err());
}
#[test]
fn deterministic_across_input_permutations() {
    let mut c = input();
    let mut claim = c.change_case.claims[0].clone();
    claim.id = "claim-2".into();
    c.change_case.claims.push(claim);
    let mut link = c.links[0].clone();
    link.id = "link-2".into();
    link.claim_id = "claim-2".into();
    c.links.push(link);
    let first = serde_json::to_vec(&assess_linked(c.clone()).unwrap()).unwrap();
    c.links.reverse();
    c.change_case.claims.reverse();
    c.quality_case.evidence.reverse();
    assert_eq!(
        first,
        serde_json::to_vec(&assess_linked(c).unwrap()).unwrap()
    );
}
#[test]
fn cli_json_and_text_expose_the_same_link_and_gap() {
    let exe = env!("CARGO_BIN_EXE_plm-evidence");
    let file = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/fixtures/linked-synthetic.json"
    );
    for format in ["json", "text"] {
        let o = std::process::Command::new(exe)
            .args(["assess-linked", "--input", file, "--format", format])
            .output()
            .unwrap();
        assert!(o.status.success());
        let s = String::from_utf8(o.stdout).unwrap();
        assert!(s.contains("link-1"));
        assert!(s.contains("effectiveness_missing"));
        assert!(s.contains("missing_evidence"));
    }
}

#[test]
fn each_issue_scope_needs_its_own_association() {
    let mut c = input();
    let mut issue = c.quality_case.issues[0].clone();
    issue.id = "issue-2".into();
    c.quality_case.issues.push(issue);
    let mut scope = c.quality_case.actions[0].scopes[0].clone();
    scope.issue_id = "issue-2".into();
    c.quality_case.actions[0].scopes.push(scope);
    let a = assess_linked(c).unwrap();
    assert!(a.findings.iter().any(|f| f.code == "action_issue_unlinked"
        && f.object_id == "action-1"
        && f.related_issue_id.as_deref() == Some("issue-2")));
}
