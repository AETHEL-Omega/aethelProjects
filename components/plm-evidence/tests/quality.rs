use plm_evidence::{quality::*, ReportedResult};
fn case() -> QualityCase {
    serde_json::from_str(include_str!("../fixtures/quality-synthetic.json")).unwrap()
}
fn complete() -> QualityCase {
    let mut c = case();
    let mut e = c.evidence[0].clone();
    e.id = "effect-1".into();
    e.kind = "effectiveness".into();
    c.evidence.push(e);
    let s = &c.actions[0].scopes[0];
    c.checks.push(EffectivenessCheck {
        id: "check-1".into(),
        action_id: "action-1".into(),
        plan_revision: 1,
        issue_id: s.issue_id.clone(),
        candidate: s.candidate.clone(),
        environment: s.environment.clone(),
        criterion: s.criterion.clone(),
        observation_window: s.observation_window.clone(),
        reviewer_reference: "independent-reviewer".into(),
        evidence_ids: vec!["effect-1".into()],
    });
    c
}
fn has(c: QualityCase, code: &str) -> bool {
    assess_quality(c).unwrap().transitions[0]
        .findings
        .iter()
        .any(|f| f.code == code)
}
#[test]
fn implementation_does_not_prove_effectiveness() {
    assert!(has(case(), "effectiveness_missing"));
}
#[test]
fn complete_declarations_never_grant_authority_or_apply_state() {
    let a = assess_quality(complete()).unwrap();
    assert!(a.transitions[0].findings.is_empty());
    assert!(a.authority.contains("external_authority_not_verified"));
    assert_eq!(
        a.source.actions[0].state,
        ActionState::AwaitingEffectiveness
    );
    assert!(render_quality_text(&a).contains("keine Freigabe"));
}
#[test]
fn adjacency_matrix_is_explicit_and_terminal_dispositions_are_not_success() {
    use ActionState::*;
    let states = [
        Proposed,
        Assigned,
        InProgress,
        Implemented,
        AwaitingEffectiveness,
        Closed,
        Cancelled,
        Superseded,
        NotRequired,
    ];
    let allowed = [
        (Proposed, Assigned),
        (Proposed, Cancelled),
        (Proposed, NotRequired),
        (Assigned, InProgress),
        (Assigned, Cancelled),
        (Assigned, Superseded),
        (Assigned, NotRequired),
        (InProgress, Implemented),
        (InProgress, Cancelled),
        (InProgress, Superseded),
        (Implemented, AwaitingEffectiveness),
        (Implemented, InProgress),
        (Implemented, Superseded),
        (AwaitingEffectiveness, Closed),
        (AwaitingEffectiveness, InProgress),
        (AwaitingEffectiveness, Superseded),
        (Closed, InProgress),
    ];
    for from in states {
        for to in states {
            assert_eq!(
                action_edge(from, to),
                allowed.contains(&(from, to)),
                "{from:?} -> {to:?}"
            );
        }
    }
    use IssueState as I;
    let states = [
        I::Registered,
        I::Triaged,
        I::Investigating,
        I::Monitoring,
        I::Closed,
    ];
    let allowed = [
        (I::Registered, I::Triaged),
        (I::Triaged, I::Investigating),
        (I::Investigating, I::Monitoring),
        (I::Monitoring, I::Closed),
        (I::Monitoring, I::Investigating),
        (I::Closed, I::Investigating),
    ];
    for from in states {
        for to in states {
            assert_eq!(issue_edge(from, to), allowed.contains(&(from, to)));
        }
    }
    let mut c = complete();
    c.actions[0].state = Proposed;
    assert!(has(c, "illegal_transition"));
}
#[test]
fn closure_requires_current_complete_scope_and_separate_reviewer() {
    for dimension in 0..6 {
        let mut c = complete();
        match dimension {
            0 => c.checks[0].candidate = "other".into(),
            1 => c.checks[0].environment = "other".into(),
            2 => c.checks[0].criterion = "other".into(),
            3 => c.checks[0].observation_window = "other".into(),
            4 => c.actions[0].plan_revision = 2,
            _ => {
                let scope = Scope {
                    environment: "second-environment".into(),
                    ..c.actions[0].scopes[0].clone()
                };
                c.actions[0].scopes.push(scope);
            }
        }
        assert!(has(c, "effectiveness_missing"), "dimension {dimension}");
    }
    let mut c = complete();
    c.checks[0].reviewer_reference = "implementer".into();
    assert!(has(c, "self_review"));
    let mut c = complete();
    c.checks[0].evidence_ids = vec!["implementation-1".into()];
    assert!(has(c, "implementation_reused_as_effectiveness"));
}
#[test]
fn failed_unknown_or_inapplicable_reports_cannot_close() {
    for outcome in [
        ReportedResult::Fail,
        ReportedResult::Unknown,
        ReportedResult::NotApplicable,
    ] {
        let mut c = complete();
        c.evidence[1].reported_result = outcome;
        c.evidence[1].explanation = Some("synthetic explanation".into());
        c.evidence[1].verified = true;
        assert!(has(c, "report_not_pass"));
    }
    let mut c = complete();
    let mut e = c.evidence[1].clone();
    e.id = "failure".into();
    e.reported_result = ReportedResult::Fail;
    c.evidence.push(e);
    c.checks[0].evidence_ids.push("failure".into());
    assert!(has(c, "conflicting_reports"));
    let mut c = complete();
    let mut check = c.checks[0].clone();
    check.id = "second".into();
    let mut e = c.evidence[1].clone();
    e.id = "failure".into();
    e.reported_result = ReportedResult::Fail;
    c.evidence.push(e);
    check.evidence_ids = vec!["failure".into()];
    c.checks.push(check);
    assert!(has(c, "report_not_pass"));
}
#[test]
fn wrong_evidence_kind_candidate_and_missing_implementation_block() {
    let mut c = complete();
    c.evidence[1].kind = "unit_test".into();
    assert!(has(c, "report_kind_mismatch"));
    let mut c = complete();
    c.evidence[1].candidate = None;
    assert!(has(c, "report_candidate_mismatch"));
    let mut c = complete();
    c.actions[0].implementation_evidence_ids.clear();
    assert!(has(c, "report_missing"));
    let mut c = complete();
    c.evidence[0].candidate = Some("other".into());
    assert!(has(c, "implementation_outside_scope"));
}
#[test]
fn ownership_cause_deadline_and_revision_are_required() {
    let mut c = complete();
    c.actions[0].owner_reference = None;
    assert!(has(c, "owner_missing"));
    let mut c = complete();
    c.actions[0].cause_reference = None;
    assert!(has(c, "cause_reference_missing"));
    let mut c = complete();
    c.actions[0].due_on = None;
    assert!(has(c, "due_date_missing"));
    let mut c = complete();
    c.actions[0].revision += 1;
    assert!(has(c, "stale_transition"));
    let mut c = complete();
    if let Transition::Action {
        decision_reference, ..
    } = &mut c.transitions[0]
    {
        *decision_reference = None;
    }
    assert!(has(c, "transition_decision_missing"));
}
fn issue_closure(mut c: QualityCase) -> QualityCase {
    c.issues[0].state = IssueState::Monitoring;
    c.issues[0].closure_decision_reference = Some("source:closure".into());
    c.transitions = vec![Transition::Issue {
        id: "close-issue".into(),
        object_id: "issue-1".into(),
        expected_revision: 1,
        to: IssueState::Closed,
        reason: "synthetic resolution".into(),
        decision_reference: Some("source:decision".into()),
    }];
    c
}
#[test]
fn issue_closure_rechecks_action_evidence_not_just_reported_state() {
    assert!(has(issue_closure(complete()), "issue_action_unresolved"));
    let mut c = case();
    c.actions[0].state = ActionState::Closed;
    assert!(has(issue_closure(c), "effectiveness_missing"));
    let mut c = complete();
    c.actions[0].state = ActionState::Closed;
    assert!(assess_quality(issue_closure(c)).unwrap().transitions[0]
        .findings
        .is_empty());
    let mut c = complete();
    c.actions[0].state = ActionState::Cancelled;
    c.actions[0].disposition = Some(Disposition {
        reason: "cancelled".into(),
        decision_reference: "source:decision".into(),
        replacement_action_id: None,
    });
    assert!(has(issue_closure(c), "issue_action_unresolved"));
    let mut c = case();
    c.actions.clear();
    c.evidence.clear();
    assert!(has(issue_closure(c), "issue_actions_missing"));
}
#[test]
fn reopening_is_possible_even_when_prior_closure_is_inconsistent() {
    let mut c = case();
    c.actions[0].state = ActionState::Closed;
    if let Transition::Action { to, .. } = &mut c.transitions[0] {
        *to = ActionState::InProgress;
    }
    let a = assess_quality(c).unwrap();
    assert!(a
        .snapshot_findings
        .iter()
        .any(|f| f.code == "effectiveness_missing"));
    assert!(a.transitions[0].findings.is_empty());
    let mut c = issue_closure(case());
    c.issues[0].state = IssueState::Closed;
    if let Transition::Issue { to, .. } = &mut c.transitions[0] {
        *to = IssueState::Investigating;
    }
    assert!(assess_quality(c).unwrap().transitions[0]
        .findings
        .is_empty());
}
#[test]
fn workflow_revision_change_does_not_invalidate_plan_bound_check() {
    let mut c = complete();
    c.actions[0].state = ActionState::Closed;
    c.actions[0].revision = 5;
    c.transitions.clear();
    assert!(assess_quality(c).unwrap().snapshot_findings.is_empty());
}
#[test]
fn dispositions_require_decisions_and_replacements_cannot_cycle() {
    let mut c = case();
    c.actions[0].state = ActionState::InProgress;
    if let Transition::Action { to, .. } = &mut c.transitions[0] {
        *to = ActionState::Cancelled;
    }
    assert!(has(c.clone(), "disposition_missing"));
    c.actions[0].disposition = Some(Disposition {
        reason: "superseded".into(),
        decision_reference: "source:decision".into(),
        replacement_action_id: None,
    });
    if let Transition::Action { to, .. } = &mut c.transitions[0] {
        *to = ActionState::Superseded;
    }
    assert!(has(c.clone(), "replacement_missing"));
    let mut other = c.actions[0].clone();
    other.id = "replacement".into();
    other.disposition.as_mut().unwrap().replacement_action_id = Some("action-1".into());
    c.actions.push(other);
    c.actions[0]
        .disposition
        .as_mut()
        .unwrap()
        .replacement_action_id = Some("replacement".into());
    assert!(assess_quality(c).is_err());
}
#[test]
fn malformed_contracts_fail_as_structure_errors() {
    let mut c = case();
    c.schema = "aethel.plm.quality-case/v2".into();
    assert!(assess_quality(c).is_err());
    let mut c = case();
    c.actions.push(c.actions[0].clone());
    assert!(assess_quality(c).is_err());
    let mut c = case();
    c.actions[0].scopes[0].issue_id = "absent".into();
    assert!(assess_quality(c).is_err());
    let mut c = case();
    c.actions[0].due_on = Some("2026-02-29".into());
    assert!(assess_quality(c).is_err());
    let mut c = complete();
    c.checks[0].evidence_ids.push("missing".into());
    assert!(assess_quality(c).is_err());
    let mut v = serde_json::to_value(case()).unwrap();
    v["transitions"][0]["approved"] = true.into();
    assert!(serde_json::from_value::<QualityCase>(v).is_err());
}
#[test]
fn evaluation_is_deterministic_and_requests_do_not_apply_to_each_other() {
    let mut c = complete();
    c.transitions.push(Transition::Issue {
        id: "issue-close".into(),
        object_id: "issue-1".into(),
        expected_revision: 1,
        to: IssueState::Closed,
        reason: "synthetic".into(),
        decision_reference: Some("source:decision".into()),
    });
    let a = assess_quality(c.clone()).unwrap();
    assert!(a
        .transitions
        .iter()
        .find(|t| matches!(&t.request, Transition::Issue { .. }))
        .unwrap()
        .findings
        .iter()
        .any(|f| f.code == "issue_action_unresolved"));
    let expected = serde_json::to_string(&a).unwrap();
    c.transitions.reverse();
    c.evidence.reverse();
    c.actions.reverse();
    c.issues.reverse();
    c.checks.reverse();
    assert_eq!(
        expected,
        serde_json::to_string(&assess_quality(c).unwrap()).unwrap()
    );
}
#[test]
fn quality_cli_reports_gaps_without_error_or_execution() {
    let out = std::process::Command::new(env!("CARGO_BIN_EXE_plm-evidence"))
        .args([
            "assess-quality",
            "--input",
            concat!(
                env!("CARGO_MANIFEST_DIR"),
                "/fixtures/quality-synthetic.json"
            ),
            "--format",
            "json",
        ])
        .output()
        .unwrap();
    assert_eq!(out.status.code(), Some(0));
    assert!(out.stderr.is_empty());
    let v: serde_json::Value = serde_json::from_slice(&out.stdout).unwrap();
    assert_eq!(v["schema"], "aethel.plm.quality-assessment/v1");
    assert_eq!(
        v["transitions"][0]["findings"][0]["code"],
        "effectiveness_missing"
    );
}

#[test]
fn replacement_needs_scope_coverage_and_its_own_effectiveness() {
    let mut c = complete();
    let mut old = c.actions[0].clone();
    old.id = "old-action".into();
    old.state = ActionState::Superseded;
    old.disposition = Some(Disposition {
        reason: "replaced".into(),
        decision_reference: "source:replacement-decision".into(),
        replacement_action_id: Some("action-1".into()),
    });
    c.actions[0].state = ActionState::Closed;
    c.actions.push(old);
    let c = issue_closure(c);
    assert!(assess_quality(c.clone()).unwrap().transitions[0]
        .findings
        .is_empty());
    let mut missing = c.clone();
    missing.checks.clear();
    assert!(has(missing, "effectiveness_missing"));
    let mut mismatch = c;
    mismatch.actions[1].scopes[0].environment = "other-environment".into();
    assert!(has(mismatch, "replacement_scope_missing"));
}
