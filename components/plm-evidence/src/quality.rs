//! Proposed quality contract: read-only transition requirements, never workflow authority.
use crate::{EvidenceReference, ReportedResult};
use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct QualityCase {
    pub schema: String,
    pub id: String,
    pub issues: Vec<Issue>,
    pub actions: Vec<Action>,
    pub checks: Vec<EffectivenessCheck>,
    pub evidence: Vec<EvidenceReference>,
    pub transitions: Vec<Transition>,
}
#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum IssueState {
    Registered,
    Triaged,
    Investigating,
    Monitoring,
    Closed,
}
#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum ActionState {
    Proposed,
    Assigned,
    InProgress,
    Implemented,
    AwaitingEffectiveness,
    Closed,
    Cancelled,
    Superseded,
    NotRequired,
}
#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum ActionKind {
    Containment,
    Corrective,
    Preventive,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Issue {
    pub id: String,
    pub revision: u64,
    pub state: IssueState,
    pub problem: String,
    pub affected_configuration: Option<String>,
    pub severity: Option<String>,
    pub triage_reason: Option<String>,
    pub closure_decision_reference: Option<String>,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Action {
    pub id: String,
    pub revision: u64,
    pub plan_revision: u64,
    pub state: ActionState,
    pub kind: ActionKind,
    pub objective: String,
    pub owner_reference: Option<String>,
    pub due_on: Option<String>,
    pub cause_reference: Option<String>,
    pub scopes: Vec<Scope>,
    pub implementation_evidence_ids: Vec<String>,
    pub disposition: Option<Disposition>,
}
/// Target configuration is distinct from the configuration where an issue was observed.
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Scope {
    pub issue_id: String,
    pub candidate: String,
    pub environment: String,
    pub criterion: String,
    /// Opaque, pre-agreed observation window/protocol, not a duration evaluated against now.
    pub observation_window: String,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Disposition {
    pub reason: String,
    pub decision_reference: String,
    pub replacement_action_id: Option<String>,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct EffectivenessCheck {
    pub id: String,
    pub action_id: String,
    pub plan_revision: u64,
    pub issue_id: String,
    pub candidate: String,
    pub environment: String,
    pub criterion: String,
    pub observation_window: String,
    pub reviewer_reference: String,
    pub evidence_ids: Vec<String>,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(tag = "object_type", rename_all = "snake_case", deny_unknown_fields)]
pub enum Transition {
    Action {
        id: String,
        object_id: String,
        expected_revision: u64,
        to: ActionState,
        reason: String,
        decision_reference: Option<String>,
    },
    Issue {
        id: String,
        object_id: String,
        expected_revision: u64,
        to: IssueState,
        reason: String,
        decision_reference: Option<String>,
    },
}
impl Transition {
    fn fields(&self) -> (&str, &str, u64, &str, &Option<String>) {
        match self {
            Self::Action {
                id,
                object_id,
                expected_revision,
                reason,
                decision_reference,
                ..
            }
            | Self::Issue {
                id,
                object_id,
                expected_revision,
                reason,
                decision_reference,
                ..
            } => (
                id,
                object_id,
                *expected_revision,
                reason,
                decision_reference,
            ),
        }
    }
}
#[derive(Debug, Serialize, PartialEq, Eq, PartialOrd, Ord)]
pub struct Finding {
    pub code: &'static str,
    pub object_id: String,
    pub reference_ids: Vec<String>,
}
#[derive(Debug, Serialize)]
pub struct TransitionAssessment {
    pub request: Transition,
    pub findings: Vec<Finding>,
}
#[derive(Debug, Serialize)]
pub struct QualityAssessment {
    pub schema: &'static str,
    /// Retained and canonically sorted; all identities and results remain source assertions.
    pub source: QualityCase,
    pub authority: &'static str,
    pub snapshot_findings: Vec<Finding>,
    pub transitions: Vec<TransitionAssessment>,
}
fn add(out: &mut Vec<Finding>, code: &'static str, id: &str, refs: &[&str]) {
    let mut reference_ids: Vec<_> = refs.iter().map(|s| s.to_string()).collect();
    reference_ids.sort();
    reference_ids.dedup();
    out.push(Finding {
        code,
        object_id: id.into(),
        reference_ids,
    });
}
fn required(values: &[&str]) -> Result<(), String> {
    if values.iter().any(|s| s.trim().is_empty()) {
        Err("empty required quality field".into())
    } else {
        Ok(())
    }
}
fn optional(values: &[&Option<String>]) -> Result<(), String> {
    for s in values.iter().filter_map(|s| s.as_deref()) {
        required(&[s])?;
    }
    Ok(())
}
fn unique<'a>(ids: impl Iterator<Item = &'a str>) -> Result<BTreeSet<&'a str>, String> {
    let mut set = BTreeSet::new();
    for id in ids {
        required(&[id])?;
        if !set.insert(id) {
            return Err(format!("duplicate id/reference: {id}"));
        }
    }
    Ok(set)
}
fn references(ids: &[String], known: &BTreeSet<&str>) -> Result<(), String> {
    for id in unique(ids.iter().map(String::as_str))? {
        if !known.contains(id) {
            return Err(format!("broken reference: {id}"));
        }
    }
    Ok(())
}
fn revision(value: u64) -> Result<(), String> {
    if value == 0 {
        Err("revision must be positive".into())
    } else {
        Ok(())
    }
}
fn validate(c: &QualityCase) -> Result<(), String> {
    if c.schema != "aethel.plm.quality-case/v1" {
        return Err("unsupported quality schema".into());
    }
    required(&[&c.id])?;
    if c.issues.is_empty() {
        return Err("quality case requires an issue".into());
    }
    let issues = unique(c.issues.iter().map(|x| x.id.as_str()))?;
    let actions = unique(c.actions.iter().map(|x| x.id.as_str()))?;
    unique(c.checks.iter().map(|x| x.id.as_str()))?;
    let evidence = unique(c.evidence.iter().map(|x| x.id.as_str()))?;
    unique(c.transitions.iter().map(|x| x.fields().0))?;
    for e in &c.evidence {
        required(&[&e.source, &e.source_id, &e.kind, &e.provenance])?;
        optional(&[&e.revision_or_digest, &e.candidate, &e.explanation])?;
        if e.reported_result == ReportedResult::NotApplicable && e.explanation.is_none() {
            return Err("not_applicable requires explanation".into());
        }
    }
    for i in &c.issues {
        required(&[&i.problem])?;
        revision(i.revision)?;
        optional(&[
            &i.affected_configuration,
            &i.severity,
            &i.triage_reason,
            &i.closure_decision_reference,
        ])?;
    }
    for a in &c.actions {
        required(&[&a.objective])?;
        revision(a.revision)?;
        revision(a.plan_revision)?;
        optional(&[&a.owner_reference, &a.due_on, &a.cause_reference])?;
        if a.due_on.as_deref().is_some_and(|s| !super::valid_date(s)) {
            return Err("invalid due_on date".into());
        }
        if a.scopes.is_empty() {
            return Err("action requires a scope".into());
        }
        let mut scope_keys = BTreeSet::new();
        for s in &a.scopes {
            required(&[
                &s.issue_id,
                &s.candidate,
                &s.environment,
                &s.criterion,
                &s.observation_window,
            ])?;
            if !issues.contains(s.issue_id.as_str()) {
                return Err(format!("broken issue reference: {}", s.issue_id));
            }
            if !scope_keys.insert((
                &s.issue_id,
                &s.candidate,
                &s.environment,
                &s.criterion,
                &s.observation_window,
            )) {
                return Err("duplicate action scope".into());
            }
        }
        references(&a.implementation_evidence_ids, &evidence)?;
        if let Some(d) = &a.disposition {
            required(&[&d.reason, &d.decision_reference])?;
            optional(&[&d.replacement_action_id])?;
            if let Some(id) = &d.replacement_action_id {
                if id == &a.id || !actions.contains(id.as_str()) {
                    return Err("invalid replacement reference".into());
                }
            }
        }
    }
    // A replacement chain must be finite; it is not an implicit resolution chain.
    for a in &c.actions {
        let mut seen = BTreeSet::new();
        let mut current = Some(a.id.as_str());
        while let Some(id) = current {
            if !seen.insert(id) {
                return Err("cyclic replacement references".into());
            }
            current = c
                .actions
                .iter()
                .find(|a| a.id == id)
                .and_then(|a| a.disposition.as_ref())
                .and_then(|d| d.replacement_action_id.as_deref());
        }
    }
    for check in &c.checks {
        required(&[
            &check.action_id,
            &check.issue_id,
            &check.candidate,
            &check.environment,
            &check.criterion,
            &check.observation_window,
            &check.reviewer_reference,
        ])?;
        revision(check.plan_revision)?;
        if !actions.contains(check.action_id.as_str()) || !issues.contains(check.issue_id.as_str())
        {
            return Err("broken check reference".into());
        }
        if !c
            .actions
            .iter()
            .find(|a| a.id == check.action_id)
            .unwrap()
            .scopes
            .iter()
            .any(|s| s.issue_id == check.issue_id)
        {
            return Err("check issue outside action scope".into());
        }
        references(&check.evidence_ids, &evidence)?;
    }
    for t in &c.transitions {
        let (_, id, rev, reason, decision) = t.fields();
        required(&[id, reason])?;
        revision(rev)?;
        optional(&[decision])?;
        let known = match t {
            Transition::Action { .. } => &actions,
            Transition::Issue { .. } => &issues,
        };
        if !known.contains(id) {
            return Err(format!("unknown transition target: {id}"));
        }
    }
    Ok(())
}
/// Legal adjacency only: no authority or evidence implied.
pub fn action_edge(from: ActionState, to: ActionState) -> bool {
    use ActionState::*;
    matches!(
        (from, to),
        (Proposed, Assigned | Cancelled | NotRequired)
            | (Assigned, InProgress | Cancelled | Superseded | NotRequired)
            | (InProgress, Implemented | Cancelled | Superseded)
            | (Implemented, AwaitingEffectiveness | InProgress | Superseded)
            | (AwaitingEffectiveness, Closed | InProgress | Superseded)
            | (Closed, InProgress)
    )
}
pub fn issue_edge(from: IssueState, to: IssueState) -> bool {
    use IssueState::*;
    matches!(
        (from, to),
        (Registered, Triaged)
            | (Triaged, Investigating)
            | (Investigating, Monitoring)
            | (Monitoring, Closed | Investigating)
            | (Closed, Investigating)
    )
}
fn reports(
    c: &QualityCase,
    ids: &[String],
    candidate: &str,
    kind: &str,
    subject: &str,
    out: &mut Vec<Finding>,
) {
    if ids.is_empty() {
        add(out, "report_missing", subject, &[]);
        return;
    }
    let mut outcomes = BTreeSet::new();
    for id in ids {
        let e = c.evidence.iter().find(|e| &e.id == id).unwrap();
        if e.candidate.as_deref() != Some(candidate) {
            add(out, "report_candidate_mismatch", subject, &[id]);
        }
        if e.kind != kind {
            add(out, "report_kind_mismatch", subject, &[id]);
        }
        if e.reported_result != ReportedResult::Pass {
            add(out, "report_not_pass", subject, &[id]);
        }
        outcomes.insert(e.reported_result);
    }
    if outcomes.contains(&ReportedResult::Pass) && outcomes.contains(&ReportedResult::Fail) {
        add(
            out,
            "conflicting_reports",
            subject,
            &ids.iter().map(String::as_str).collect::<Vec<_>>(),
        );
    }
}
fn action_requirements(c: &QualityCase, a: &Action, state: ActionState, out: &mut Vec<Finding>) {
    use ActionState::*;
    if matches!(state, Cancelled | Superseded | NotRequired) {
        match &a.disposition {
            None => add(out, "disposition_missing", &a.id, &[]),
            Some(d) => {
                if state == Superseded {
                    if let Some(id) = &d.replacement_action_id {
                        let replacement = c.actions.iter().find(|x| &x.id == id).unwrap();
                        for scope in &a.scopes {
                            if !replacement.scopes.iter().any(|s| {
                                s.issue_id == scope.issue_id
                                    && s.environment == scope.environment
                                    && s.criterion == scope.criterion
                                    && s.observation_window == scope.observation_window
                            }) {
                                add(
                                    out,
                                    "replacement_scope_missing",
                                    &a.id,
                                    &[id, &scope.issue_id],
                                );
                            }
                        }
                    } else {
                        add(out, "replacement_missing", &a.id, &[]);
                    }
                } else if d.replacement_action_id.is_some() {
                    add(out, "unexpected_replacement", &a.id, &[]);
                }
            }
        }
        return;
    }
    if state == Proposed {
        return;
    }
    if a.owner_reference.is_none() {
        add(out, "owner_missing", &a.id, &[]);
    }
    if a.due_on.is_none() {
        add(out, "due_date_missing", &a.id, &[]);
    }
    if a.kind == ActionKind::Corrective && a.cause_reference.is_none() {
        add(out, "cause_reference_missing", &a.id, &[]);
    }
    if matches!(state, Implemented | AwaitingEffectiveness | Closed) {
        for s in &a.scopes {
            // One action may affect several candidates. Select implementation reports by candidate.
            let ids: Vec<_> = a
                .implementation_evidence_ids
                .iter()
                .filter(|id| {
                    c.evidence
                        .iter()
                        .any(|e| &e.id == *id && e.candidate.as_deref() == Some(&s.candidate))
                })
                .cloned()
                .collect();
            reports(c, &ids, &s.candidate, "implementation", &a.id, out);
        }
        for id in &a.implementation_evidence_ids {
            let e = c.evidence.iter().find(|e| &e.id == id).unwrap();
            if !a
                .scopes
                .iter()
                .any(|s| e.candidate.as_deref() == Some(&s.candidate))
            {
                add(out, "implementation_outside_scope", &a.id, &[id]);
            }
        }
    }
    if state != Closed {
        return;
    }
    for s in &a.scopes {
        let relevant: Vec<_> = c
            .checks
            .iter()
            .filter(|check| {
                check.action_id == a.id
                    && check.issue_id == s.issue_id
                    && check.candidate == s.candidate
                    && check.environment == s.environment
                    && check.criterion == s.criterion
                    && check.observation_window == s.observation_window
                    && check.plan_revision == a.plan_revision
            })
            .collect();
        if relevant.is_empty() {
            add(out, "effectiveness_missing", &a.id, &[&s.issue_id]);
        }
        for check in relevant {
            if a.owner_reference.as_ref() == Some(&check.reviewer_reference) {
                add(out, "self_review", &a.id, &[&check.id]);
            }
            if check
                .evidence_ids
                .iter()
                .any(|id| a.implementation_evidence_ids.contains(id))
            {
                add(
                    out,
                    "implementation_reused_as_effectiveness",
                    &a.id,
                    &[&check.id],
                );
            }
            reports(
                c,
                &check.evidence_ids,
                &s.candidate,
                "effectiveness",
                &check.id,
                out,
            );
        }
    }
}
fn issue_requirements(c: &QualityCase, i: &Issue, state: IssueState, out: &mut Vec<Finding>) {
    if state == IssueState::Registered {
        return;
    }
    if i.affected_configuration.is_none() {
        add(out, "affected_configuration_missing", &i.id, &[]);
    }
    if i.severity.is_none() || i.triage_reason.is_none() {
        add(out, "triage_missing", &i.id, &[]);
    }
    if !matches!(state, IssueState::Monitoring | IssueState::Closed) {
        return;
    }
    let actions: Vec<_> = c
        .actions
        .iter()
        .filter(|a| a.scopes.iter().any(|s| s.issue_id == i.id))
        .collect();
    if actions.is_empty() {
        add(out, "issue_actions_missing", &i.id, &[]);
    }
    for original in actions {
        let mut a = original;
        while a.state == ActionState::Superseded {
            action_requirements(c, a, a.state, out);
            let Some(id) = a
                .disposition
                .as_ref()
                .and_then(|d| d.replacement_action_id.as_ref())
            else {
                break;
            };
            // Validation above rejects broken/cyclic replacement links.
            a = c.actions.iter().find(|a| &a.id == id).unwrap();
        }
        let ready = if state == IssueState::Closed {
            a.state == ActionState::Closed
        } else {
            matches!(
                a.state,
                ActionState::Implemented | ActionState::AwaitingEffectiveness | ActionState::Closed
            )
        };
        if !ready {
            add(
                out,
                "issue_action_unresolved",
                &i.id,
                &[&original.id, &a.id],
            );
        }
        action_requirements(c, a, a.state, out);
    }
    if state == IssueState::Closed && i.closure_decision_reference.is_none() {
        add(out, "closure_decision_missing", &i.id, &[]);
    }
}
fn canonical(findings: &mut Vec<Finding>) {
    findings.sort();
    findings.dedup();
}
/// Evaluate each request against the same reported snapshot. No transition is applied.
pub fn assess_quality(mut c: QualityCase) -> Result<QualityAssessment, String> {
    validate(&c)?;
    c.issues.sort_by(|a, b| a.id.cmp(&b.id));
    c.actions.sort_by(|a, b| a.id.cmp(&b.id));
    c.checks.sort_by(|a, b| a.id.cmp(&b.id));
    c.evidence.sort_by(|a, b| a.id.cmp(&b.id));
    c.transitions.sort_by(|a, b| a.fields().0.cmp(b.fields().0));
    for a in &mut c.actions {
        a.scopes.sort_by(|a, b| {
            (
                &a.issue_id,
                &a.candidate,
                &a.environment,
                &a.criterion,
                &a.observation_window,
            )
                .cmp(&(
                    &b.issue_id,
                    &b.candidate,
                    &b.environment,
                    &b.criterion,
                    &b.observation_window,
                ))
        });
        a.implementation_evidence_ids.sort();
    }
    for check in &mut c.checks {
        check.evidence_ids.sort();
    }
    let mut snapshot_findings = Vec::new();
    for a in &c.actions {
        action_requirements(&c, a, a.state, &mut snapshot_findings);
    }
    for i in &c.issues {
        issue_requirements(&c, i, i.state, &mut snapshot_findings);
    }
    // Old/out-of-scope checks are retained but never silently reused.
    for check in &c.checks {
        let a = c.actions.iter().find(|a| a.id == check.action_id).unwrap();
        if check.plan_revision != a.plan_revision {
            add(&mut snapshot_findings, "stale_check", &check.id, &[&a.id]);
        }
        if !a.scopes.iter().any(|s| {
            s.issue_id == check.issue_id
                && s.candidate == check.candidate
                && s.environment == check.environment
                && s.criterion == check.criterion
                && s.observation_window == check.observation_window
        }) {
            add(
                &mut snapshot_findings,
                "check_scope_mismatch",
                &check.id,
                &[&a.id],
            );
        }
    }
    canonical(&mut snapshot_findings);
    let mut transitions = Vec::new();
    for t in &c.transitions {
        let (_, id, rev, _, decision) = t.fields();
        let mut findings = Vec::new();
        match t {
            Transition::Action { to, .. } => {
                let a = c.actions.iter().find(|a| a.id == id).unwrap();
                if rev != a.revision {
                    add(&mut findings, "stale_transition", id, &[]);
                }
                if !action_edge(a.state, *to) {
                    add(&mut findings, "illegal_transition", id, &[]);
                }
                if *to != ActionState::InProgress {
                    action_requirements(&c, a, a.state, &mut findings);
                }
                action_requirements(&c, a, *to, &mut findings);
                if (a.state == ActionState::Closed
                    || *to == ActionState::InProgress
                        && a.state == ActionState::AwaitingEffectiveness
                    || *to == ActionState::Closed)
                    && decision.is_none()
                {
                    add(&mut findings, "transition_decision_missing", id, &[]);
                }
            }
            Transition::Issue { to, .. } => {
                let i = c.issues.iter().find(|i| i.id == id).unwrap();
                if rev != i.revision {
                    add(&mut findings, "stale_transition", id, &[]);
                }
                if !issue_edge(i.state, *to) {
                    add(&mut findings, "illegal_transition", id, &[]);
                }
                if *to != IssueState::Investigating {
                    issue_requirements(&c, i, i.state, &mut findings);
                }
                issue_requirements(&c, i, *to, &mut findings);
                if (i.state == IssueState::Closed || *to == IssueState::Closed)
                    && decision.is_none()
                {
                    add(&mut findings, "transition_decision_missing", id, &[]);
                }
            }
        }
        canonical(&mut findings);
        transitions.push(TransitionAssessment {
            request: t.clone(),
            findings,
        });
    }
    Ok(QualityAssessment {
        schema: "aethel.plm.quality-assessment/v1",
        source: c,
        authority: "external_authority_not_verified; requirements_only; no_transition_applied",
        snapshot_findings,
        transitions,
    })
}

pub fn render_quality_text(a: &QualityAssessment) -> String {
    use std::fmt::Write;
    let mut out = String::from("Qualitätsvertrag — lesende Prüfung; keine Übergänge ausgeführt.\nExterne Autorität nicht verifiziert. Auch ohne Befunde entsteht keine Freigabe.\n");
    for f in &a.snapshot_findings {
        writeln!(
            out,
            "Snapshot [{}] {} {:?}",
            f.code,
            f.object_id.escape_debug(),
            f.reference_ids
        )
        .unwrap();
    }
    for t in &a.transitions {
        writeln!(
            out,
            "\nAntrag {} → Objekt {}",
            t.request.fields().0.escape_debug(),
            t.request.fields().1.escape_debug()
        )
        .unwrap();
        if t.findings.is_empty() {
            out.push_str("Deklarierte Voraussetzungen vollständig; externe Entscheidung bleibt erforderlich.\n");
        }
        for f in &t.findings {
            writeln!(
                out,
                "  [{}] {} {:?}",
                f.code,
                f.object_id.escape_debug(),
                f.reference_ids
            )
            .unwrap();
        }
    }
    out
}
