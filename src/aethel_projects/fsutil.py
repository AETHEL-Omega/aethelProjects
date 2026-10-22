"""Dateibaum-Walk mit Pruning — die Grundlage der Code-Sicht.

``Path.rglob`` steigt in ``node_modules``, ``target`` und ``.dart_tool`` ab und
liest dabei Millionen Dateien, ohne sie zu brauchen. Diese Module laufen über
208 Repos; das ist der Unterschied zwischen Sekunden und einer Viertelstunde.

Die Funktionen hier sind **begrenzt** (Budget) und **prunend** — sie betreten
Build-Verzeichnisse gar nicht erst.
"""

from __future__ import annotations

import os
from pathlib import Path

#: Verzeichnisse, die nie betreten werden.
DEFAULT_SKIP_DIRS = frozenset(
    {
        ".git",
        ".build",
        ".dart_tool",
        ".gradle",
        ".idea",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        ".vscode",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
        "site-packages",
        "target",
        "venv",
    }
)

#: Verzeichnisse, deren **Name** mit einem dieser Präfixe beginnt.
SKIP_PREFIXES = (".venv", ".tox", ".mypy", ".pytest", ".ruff", ".dart_tool")

#: Verzeichnisse, deren **Name** mit einem dieser Suffixe endet.
SKIP_SUFFIXES = ("-worktrees", "_worktrees", "-worktree", ".worktrees")


def is_skipped(name: str, skip_dirs: frozenset[str] = DEFAULT_SKIP_DIRS) -> bool:
    """Soll dieses Verzeichnis betreten werden?

    Neben den exakten Namen zählen Präfixe (``.venv-ml``) und Suffixe
    (``aethelScripts-worktrees``) — beide tragen Fremdcode oder Kopien.
    """
    if name in skip_dirs:
        return True
    if name.startswith(SKIP_PREFIXES):
        return True
    if name.endswith(SKIP_SUFFIXES):
        return True
    return False


#: Wie viele Dateien ein Walk höchstens liefert.
DEFAULT_LIMIT = 20_000


def walk_files(
    root: Path,
    *,
    suffix: tuple[str, ...] | None = None,
    skip_dirs: frozenset[str] = DEFAULT_SKIP_DIRS,
    limit: int = DEFAULT_LIMIT,
) -> list[Path]:
    """Alle Dateien unterhalb von ``root`` — ohne Build-Verzeichnisse.

    :param suffix: nur Dateien mit dieser Endung (ohne Punkt)
    :param limit: harte Obergrenze der zurückgegebenen Dateien
    """
    found: list[Path] = []
    root = Path(root)
    if not root.is_dir():
        return found

    for dirpath, dirnames, filenames in os.walk(root, topdown=True, onerror=lambda _e: None):
        # Pruning: die Verzeichnisse gar nicht erst betreten.
        dirnames[:] = sorted(d for d in dirnames if not is_skipped(d, skip_dirs))
        base = Path(dirpath)
        for filename in sorted(filenames):
            if suffix is not None and not filename.endswith(suffix):
                continue
            found.append(base / filename)
            if len(found) >= limit:
                return found
    return found


def relative_paths(
    root: Path,
    *,
    skip_dirs: frozenset[str] = DEFAULT_SKIP_DIRS,
    limit: int = DEFAULT_LIMIT,
) -> list[str]:
    """Die relativen POSIX-Pfade unterhalb von ``root``."""
    root = Path(root)
    result: list[str] = []
    for path in walk_files(root, skip_dirs=skip_dirs, limit=limit):
        try:
            result.append(path.relative_to(root).as_posix())
        except ValueError:
            continue
    return result
