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

MAX_DEPTH = 2


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
    found: list[Path] = []
    for depth in range(1, MAX_DEPTH + 1):
        pattern = "/".join(["*"] * depth) + "/.git"
        for git_marker in root.glob(pattern):
            found.append(git_marker.parent)
    return sorted(set(found))


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
        common_path = Path(common)
        # Das Hauptverzeichnis ist derjenige, in dem .git selbst liegt.
        owner = None
        for member in members:
            if (member / ".git").is_dir():
                owner = member
                break
        if owner is None:
            # Alle sind Worktrees: der Besitzer liegt eine Ebene über common_dir.
            owner = common_path.parent
        worktrees = tuple(
            sorted(str(m) for m in members if m != owner)
        )
        identities.append(
            RepoIdentity(
                name=owner.name,
                path=str(owner),
                git_common_dir=common,
                is_worktree=owner not in members,
                worktree_paths=worktrees,
            )
        )

    identities.sort(key=lambda i: i.name.lower())
    return identities
