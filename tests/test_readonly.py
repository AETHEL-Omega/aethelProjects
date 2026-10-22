"""TC-013, TC-014, TC-030 — Read-only-Garantie und Offline-Fähigkeit (REQ-007, REQ-016).

Die Prüfung erfolgt über den **AST**, nicht über Textsuche: so werden
Empfehlungstexte (die ein Kommando *nennen*) nicht mit echten Aufrufen verwechselt.
"""

from __future__ import annotations

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "aethel_projects"

#: Git-Subkommandos, die den Workspace verändern — verboten.
FORBIDDEN_SUBCOMMANDS = {
    "checkout",
    "commit",
    "push",
    "reset",
    "clean",
    "rebase",
    "merge",
    "cherry-pick",
    "stash",
    "am",
    "rm",
    "mv",
    "update-ref",
    "gc",
    "prune",
}

#: Erlaubte lesende Subkommandos.
ALLOWED_SUBCOMMANDS = {
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
    "ls-files",
}

GIT_HELPERS = {"run_git", "run_git_lines", "count", "ref_exists"}


def _source_files() -> list[Path]:
    return sorted(SRC.rglob("*.py"))


def _git_call_arguments(path: Path) -> list[tuple[int, str]]:
    """Das Git-Subkommando jedes Git-Aufrufs.

    Bei ``run_git(repo, "rev-list", ...)`` ist das Subkommando das **erste**
    String-Argument nach dem Repository. ``ref_exists`` kapselt ``show-ref``.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
        if name not in GIT_HELPERS:
            continue
        if name == "ref_exists":
            found.append((node.lineno, "show-ref"))
            continue
        for arg in node.args[1:]:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                found.append((arg.lineno, arg.value))
                break
    return found


def test_tc013_no_destructive_git_commands_in_source() -> None:
    """TC-013: kein Git-Aufruf übergibt ein schreibendes Subkommando."""
    offenders: list[str] = []
    for path in _source_files():
        for lineno, argument in _git_call_arguments(path):
            head = argument.split()[0] if argument.split() else ""
            if head in FORBIDDEN_SUBCOMMANDS:
                offenders.append(f"{path.name}:{lineno} → {argument!r}")
    assert not offenders, "Schreibende Git-Kommandos gefunden:\n" + "\n".join(offenders)


def test_tc014_all_git_calls_use_read_only_subcommands() -> None:
    """TC-014: jeder Git-Subcommand gehört zur Whitelist (Flags zählen nicht)."""
    used: set[str] = set()
    for path in _source_files():
        for _lineno, argument in _git_call_arguments(path):
            parts = argument.split()
            if not parts:
                continue
            head = parts[0]
            # Nur echte Subkommandos prüfen — Flags und Rev-Specs sind keine.
            if head.startswith("-"):
                continue
            used.add(head)
    assert used, "keine Git-Aufrufe gefunden — Test wäre wirkungslos"
    assert used <= ALLOWED_SUBCOMMANDS, f"Nicht erlaubte Git-Subkommandos: {sorted(used - ALLOWED_SUBCOMMANDS)}"


def test_gitio_is_the_only_subprocess_entrypoint() -> None:
    """Nur gitio.py darf subprocess aufrufen — so bleibt der Ausgangspunkt prüfbar."""
    offenders: list[str] = []
    for path in _source_files():
        if path.name == "gitio.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
                if name in {"run", "Popen", "call", "check_output", "system"}:
                    offenders.append(f"{path.name}:{node.lineno} → {name}()")
    assert not offenders, "subprocess außerhalb von gitio.py:\n" + "\n".join(offenders)


def test_no_filesystem_deletion_helpers() -> None:
    """Das Werkzeug enthält keine Lösch-/Verschieb-Aufrufe."""
    for path in _source_files():
        text = path.read_text(encoding="utf-8")
        for forbidden in ("os.remove(", "shutil.rmtree", "os.rename(", "os.unlink("):
            assert forbidden not in text, f"{path.name} enthält {forbidden}"


def test_tc030_suite_does_not_touch_the_real_workspace() -> None:
    """TC-030: kein Test greift auf den echten ~/workspace zu."""
    real_workspace = str(Path.home() / "workspace")
    for path in Path(__file__).resolve().parent.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert real_workspace not in text, f"{path.name} verweist auf den echten Workspace"
