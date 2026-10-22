"""Die einzige Git-Schnittstelle des Werkzeugs.

**Harte Regel:** Hier werden ausschließlich lesende Git-Kommandos ausgeführt.
Kein `checkout`, `commit`, `push`, `branch -d`, `worktree remove`, `reset`, `clean`.
Das ist durch TC-013/TC-014 maschinell belegt.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

DEFAULT_TIMEOUT = 30

#: Erlaubte Git-Subkommandos — alles andere wird nicht ausgeführt.
READ_ONLY_SUBCOMMANDS = frozenset(
    {
        "rev-list",
        "rev-parse",
        "for-each-ref",
        "symbolic-ref",
        "log",
        "status",
        "show-ref",
        "remote",
        "worktree",
        "config",
    }
)

#: Subkommandos von `git worktree`, die entfernen — verboten.
_FORBIDDEN_WORKTREE_ACTIONS = frozenset({"remove", "prune", "repair", "add"})


def run_git(
    repo: Path,
    *args: str,
    timeout: int = DEFAULT_TIMEOUT,
) -> str | None:
    """Führt `git -C <repo> <args>` aus.

    Gibt stdout (ohne trailing newline) zurück, oder ``None`` bei Fehler/Timeout.
    """
    if not args:
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def run_git_lines(repo: Path, *args: str, timeout: int = DEFAULT_TIMEOUT) -> list[str]:
    """Wie :func:`run_git`, aber als Liste nicht-leerer Zeilen."""
    output = run_git(repo, *args, timeout=timeout)
    if not output:
        return []
    return [line for line in output.splitlines() if line.strip()]


def ref_exists(repo: Path, ref: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
    """Existiert der Ref? Nutzt den Exit-Code — ``show-ref --quiet`` liefert keine Ausgabe."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "show-ref", "--verify", "--quiet", ref],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError):
        return False
    return result.returncode == 0


def count(repo: Path, *args: str, timeout: int = DEFAULT_TIMEOUT) -> int | None:
    """Zählt Zeilen einer Git-Ausgabe. ``None`` bei Fehler — nie 0 als Ersatz."""
    lines = run_git_lines(repo, *args, timeout=timeout)
    if not lines:
        return None
    try:
        return int(lines[0].strip())
    except ValueError:
        return None


def git_available() -> bool:
    """Ist ``git`` im PATH verfügbar?"""
    try:
        result = subprocess.run(
            ["git", "--version"], capture_output=True, text=True, timeout=10, check=False
        )
    except (subprocess.TimeoutExpired, OSError):
        return False
    return result.returncode == 0
