"""Projektmanagement-View (REQ-013): Status, Risiko, nächste Schritte.

Die View leitet sich **ausschließlich** aus dem Scan ab — sie erfindet keinen Plan.
"""

from __future__ import annotations

from datetime import date, datetime

from .models import ProjectManagementView, RepoReport

ACTIVE_DAYS = 30
STALE_DAYS = 90


def _days_since(timestamp: str | None) -> int | None:
    if not timestamp:
        return None
    try:
        parsed = datetime.strptime(timestamp, "%Y-%m-%d").date()
    except ValueError:
        return None
    return (date.today() - parsed).days


def build(repo: RepoReport) -> ProjectManagementView:
    """Erzeugt die Projektmanagement-Sicht für ein Repository."""
    age = _days_since(repo.last_commit_date)
    activity = "active" if (age is not None and age <= ACTIVE_DAYS) else "inactive"

    actions: list[str] = []

    if repo.commits_not_on_main > 0:
        actions.append(
            f"{repo.commits_not_on_main} Commits nicht auf main: "
            f"{', '.join(b.name for b in repo.unmerged_branches[:3]) or 'Branches prüfen'}"
        )
    if repo.ahead_of_origin:
        actions.append(f"{repo.ahead_of_origin} Commits pushen (nicht auf origin).")
    if repo.default_branch is None:
        actions.append("Default-Branch (main/master) fehlt — Repository-Status klären.")
    if repo.maturity is not None and repo.maturity.score < 50:
        missing = [
            name
            for name, points in repo.maturity.parts.items()
            if points == 0 and name in {"SPEC", "DESIGN", "ARCHITECTURE", "TEST-CASES", "CI", "DNA"}
        ]
        if missing:
            actions.append(f"Engineering-Standard: {', '.join(missing)} fehlen.")
    if not repo.intent or repo.intent.text is None:
        actions.append("Kein Zweck erkennbar — README oder docs/SPEC.md ergänzen.")
    if repo.dirty_files > 50:
        actions.append(f"{repo.dirty_files} ungespeicherte Änderungen — aufräumen.")
    if age is not None and age > STALE_DAYS:
        actions.append(f"Seit {age} Tagen ohne Commit — Weiterbau oder Archivierung entscheiden.")

    if not actions:
        actions.append("Kein Handlungsbedarf erkannt.")

    risk = "low"
    if repo.commits_not_on_main > 50 or repo.default_branch is None:
        risk = "high"
    elif repo.commits_not_on_main > 0 or (age is not None and age > STALE_DAYS) or repo.dirty_files > 20:
        risk = "medium"

    return ProjectManagementView(activity=activity, risk=risk, next_actions=tuple(actions))
