"""Workspace-Discovery mit Worktree-Deduplizierung (REQ-001).

Der Dedup-Schlüssel ist ``git rev-parse --path-format=absolute --git-common-dir``:
Bei einem Worktree zeigt ``--git-dir`` auf ``…/.git/worktrees/<name>`` — jeder
Worktree sähe wie ein eigenes Repository aus. ``common_dir`` zeigt auf das
**gemeinsame** ``.git`` und identifiziert die Historie korrekt.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import gitio
from .inventory import census


@dataclass(frozen=True)
class RepoIdentity:
    """Die Identität einer Historie — ein Repository, wie viele Verzeichnisse es auch gebe."""

    name: str
    path: str
    git_common_dir: str
    is_worktree: bool
    worktree_paths: tuple[str, ...]


def _candidate_dirs(root: Path) -> list[Path]:
    """Alle Verzeichnisse unterhalb root, die ein .git enthalten (Datei oder Ordner)."""
    return [Path(p) for p in census(root)["git_candidates"]]


def _common_dir(repo: Path) -> str | None:
    """Absoluter Pfad des gemeinsamen .git-Verzeichnisses."""
    output = gitio.run_git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if not output:
        return None
    common = Path(output)
    if not common.is_absolute():
        common = (repo / common).resolve()
    return str(common)


def discover(root: Path | str) -> list[RepoIdentity]:
    """Findet alle Repositories unterhalb root — jedes genau einmal."""
    root_path = Path(root).expanduser().resolve()
    if not root_path.is_dir():
        return []

    grouped: dict[str, list[Path]] = {}
    for candidate in _candidate_dirs(root_path):
        common = _common_dir(candidate)
        if not common:
            continue
        grouped.setdefault(common, []).append(candidate)

    identities: list[RepoIdentity] = []
    for common, members in sorted(grouped.items()):
        # Das Hauptverzeichnis ist derjenige, in dem .git selbst liegt.
        owner = None
        for member in members:
            if (member / ".git").is_dir():
                owner = member
                break
        if owner is None:
            # Ohne Hauptcheckout einen vorhandenen Worktree oder Bare-Pfad nutzen.
            owner = members[0]
        worktrees = tuple(
            sorted(str(m) for m in members if m != owner)
        )
        identities.append(
            RepoIdentity(
                name=owner.name,
                path=str(owner),
                git_common_dir=common,
                is_worktree=(owner / ".git").is_file(),
                worktree_paths=worktrees,
            )
        )

    identities.sort(key=lambda i: i.name.lower())
    return identities
