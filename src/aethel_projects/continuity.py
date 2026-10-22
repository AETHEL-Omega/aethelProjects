"""F0 — Kontinuuität: Funktionen *auf* Git, nicht daneben.

Git weiss, **wo** man war: welcher Branch, welcher Commit, was liegt auf origin.
Git weiss aber nicht, **was offen** ist und schon gar nicht, **was als Nächstes**
zu tun ist — das steht in der SPEC, im README oder in einem ungemergten Branch.

Dieses Modul legt genau diese Schicht ueber Git:

* **Standort** — Branch, letzter Commit, Abstand zu origin, Schmutz.
* **Offen** — ungemergte Branches mit Vorsprung, Commits ausserhalb von main.
* **Nächster Schritt** — abgeleitet aus Belegen: ungemergter Branch, „Nächste
  Schritte"-Abschnitt im Projektdokument, uncommittete Änderungen, Push-Rückstand.
  Ohne Beleg wird **nichts** behauptet.

Es ist wie bei CursorAI: nach einer Unterbrechung weiss das Werkzeug, wo man
war und was als Nächstes kommt — nur eben aus Git und den eigenen Dokumenten
des Projekts statt aus einem Chatverlauf.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .models import RepoReport

#: Überschriften, unter denen der nächste Schritt steht.
NEXT_STEP_HEADINGS = (
    "nächste schritte",
    "naechste schritte",
    "next steps",
    "next step",
    "todo",
    "roadmap",
    "backlog",
    "offen",
    "open issues",
    "to do",
)

#: Aufgaben-Marker in Dokumenten.
TASK_MARKER = re.compile(r"^\s*[-*]\s+\[( |x|X)\]\s+(?P<text>.+)$")

#: Wie viele der zuletzt angefassten Repos die Workspace-Kontinuität zeigt.
RECENT_LIMIT = 10


@dataclass(frozen=True)
class Continuity:
    """Der Kontinuitaets-Zustand eines Repositories."""

    repo: str
    path: str
    standort: str
    offen: tuple[str, ...]
    naechster_schritt: str | None
    beweis: str
    dringlichkeit: int  # 0-100

    def as_dict(self) -> dict:
        return {
            "repo": self.repo,
            "path": self.path,
            "standort": self.standort,
            "offen": list(self.offen),
            "naechster_schritt": self.naechster_schritt,
            "beweis": self.beweis,
            "dringlichkeit": self.dringlichkeit,
        }


@dataclass(frozen=True)
class WorkspaceContinuity:
    """Die Fortsetzung ueber den ganzen Workspace."""

    zuletzt: tuple[Continuity, ...]
    offene_arbeit: int
    uncommittet: int
    naechster_schritt: str | None
    hinweis: str = ""

    def as_dict(self) -> dict:
        return {
            "zuletzt": [c.as_dict() for c in self.zuletzt],
            "offene_arbeit": self.offene_arbeit,
            "uncommittet": self.uncommittet,
            "naechster_schritt": self.naechster_schritt,
            "hinweis": self.hinweis,
        }


def _read_doc(root: Path, names: tuple[str, ...]) -> tuple[str, str]:
    """Liest das erste vorhandene Dokument — gibt (Pfad, Text) zurueck."""
    for name in names:
        path = root / name
        if not path.is_file():
            continue
        try:
            return name, path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
    return "", ""


def _next_step_from_docs(root: Path) -> tuple[str | None, str]:
    """Sucht den naechsten Schritt in den Projektdokumenten."""
    for name in ("docs/SPEC.md", "README.md", "docs/README.md", "SPEC.md", "TODO.md"):
        source, text = _read_doc(root, (name,))
        if not text:
            continue
        lines = text.splitlines()
        in_section = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                heading = re.sub(r"^#+\s*", "", stripped).strip().lower()
                in_section = heading in NEXT_STEP_HEADINGS
                continue
            if not in_section:
                continue
            task = TASK_MARKER.match(line)
            if task:
                # Nur **offene** Aufgaben sind der nächste Schritt.
                if task.group(1) == " " and task.group("text").strip():
                    return task.group("text").strip()[:160], f"{source}: Aufgabenliste"
                continue
            if stripped.startswith(("-", "*")) and len(stripped) > 3:
                return stripped.lstrip("-* ").strip()[:160], f"{source}: Abschnitt „{heading}“"
    return None, ""


def _standort(repo: RepoReport) -> str:
    """Wo steht der Kopf? — in einem Satz."""
    parts = [f"Branch `{repo.current_branch or '?'}`"]
    if repo.last_commit_subject:
        subject = repo.last_commit_subject
        parts.append(f"zuletzt „{subject[:60]}“")
    if repo.last_commit_date:
        parts.append(repo.last_commit_date)
    if repo.ahead_of_origin:
        parts.append(f"{repo.ahead_of_origin} Commits vor origin")
    if repo.behind_origin:
        parts.append(f"{repo.behind_origin} Commits hinter origin")
    if repo.dirty_files:
        parts.append(f"{repo.dirty_files} Datei(en) uncommittet")
    return ", ".join(parts)


def _offen(repo: RepoReport) -> list[str]:
    """Was liegt noch offen?"""
    offen: list[str] = []
    for branch in repo.unmerged_branches[:5]:
        offen.append(f"Branch `{branch.name}` (+{branch.commits_ahead}, {branch.kind})")
    if repo.commits_not_on_main:
        offen.append(f"{repo.commits_not_on_main} Commits ausserhalb von "
                     f"{repo.default_branch or 'main'}")
    if repo.dirty_files:
        offen.append(f"{repo.dirty_files} uncommittete Datei(en)")
    if repo.ahead_of_origin:
        offen.append(f"{repo.ahead_of_origin} Commits nicht gepusht")
    if repo.behind_origin:
        offen.append(f"{repo.behind_origin} Commits von origin nicht geholt")
    return offen


def _next_step(repo: RepoReport) -> tuple[str | None, str, int]:
    """Der naechste Schritt — mit Beleg und Dringlichkeit."""
    root = Path(repo.path)

    # 1. Der ungemergte Branch mit dem groessten Vorsprung traegt die Arbeit.
    if repo.unmerged_branches:
        best = max(repo.unmerged_branches, key=lambda b: b.commits_ahead)
        return (
            f"Branch `{best.name}` zusammenfuehren (+{best.commits_ahead} Commits)",
            f"ungemergter Branch mit dem groessten Vorsprung",
            70 + min(20, best.commits_ahead),
        )

    # 2. Das Projektdokument weiss es besser als Git.
    step, beweis = _next_step_from_docs(root)
    if step:
        return step, beweis, 60

    # 3. Uncommittete Arbeit.
    if repo.dirty_files:
        return (
            f"{repo.dirty_files} uncommittete Datei(en) sichern",
            "Working Tree ist nicht sauber",
            65,
        )

    # 4. Push-Rueckstand.
    if repo.ahead_of_origin:
        return (
            f"{repo.ahead_of_origin} Commits nach origin pushen",
            "lokaler Stand liegt vor origin",
            55,
        )

    # 5. Nichts offen.
    if repo.commits_on_main and repo.commits_on_main == repo.commits_total:
        return None, "alles auf main, Baum sauber", 0

    return None, "kein offener Schritt erkennbar", 0


def continuity_for(repo: RepoReport) -> Continuity:
    """Der Kontinuitaets-Zustand eines einzelnen Repositories."""
    standort = _standort(repo)
    offen = _offen(repo)
    step, beweis, dringlichkeit = _next_step(repo)
    return Continuity(
        repo=repo.name,
        path=repo.path,
        standort=standort,
        offen=tuple(offen),
        naechster_schritt=step,
        beweis=beweis,
        dringlichkeit=dringlichkeit,
    )


def _recency(repo: RepoReport) -> str:
    return repo.last_commit_date or "0000-00-00"


def build(repos: tuple[RepoReport, ...]) -> WorkspaceContinuity:
    """Die Fortsetzung ueber den ganzen Workspace."""
    datums = {repo.name: (repo.last_commit_date or "0000-00-00") for repo in repos}
    zustände = [continuity_for(repo) for repo in repos]
    # Zwei stabile Sortierungen: erst Name, dann Aktualitaet absteigend.
    # Python sortiert stabil — bei gleichem Datum bleibt die Namensordnung.
    zustände.sort(key=lambda c: c.repo.lower())
    zustände.sort(key=lambda c: datums.get(c.repo, "0000-00-00"), reverse=True)

    zuletzt = tuple(zustände[:RECENT_LIMIT])
    offene_arbeit = sum(repo.commits_not_on_main for repo in repos)
    uncommittet = sum(1 for repo in repos if repo.dirty_files)

    dringend = sorted(
        (c for c in zustände if c.naechster_schritt),
        key=lambda c: c.dringlichkeit,
        reverse=True,
    )
    naechster = dringend[0] if dringend else None

    hinweis = ""
    if uncommittet:
        hinweis = (
            f"{uncommittet} Repos haben uncommittete Aenderungen — "
            f"das ist der wahrscheinlichste Wiedereinstiegspunkt."
        )
    elif naechster:
        hinweis = f"Dringendster offener Schritt: {naechster.repo}."

    return WorkspaceContinuity(
        zuletzt=zuletzt,
        offene_arbeit=offene_arbeit,
        uncommittet=uncommittet,
        naechster_schritt=(
            f"{naechster.repo}: {naechster.naechster_schritt}" if naechster else None
        ),
        hinweis=hinweis,
    )
