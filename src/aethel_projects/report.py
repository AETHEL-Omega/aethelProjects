"""Renderer: JSON, Markdown, HTML (REQ-005, REQ-006)."""

from __future__ import annotations

import html
import json

from . import market as market_mod
from .models import Finding, RepoReport, ScanResult

SEVERITY_MARK = {"critical": "🔴", "warn": "🟡", "info": "🔵"}


def to_json(result: ScanResult) -> str:
    """Serialisiert das Ergebnis als JSON (REQ-005)."""
    return json.dumps(result.as_dict(), ensure_ascii=False, indent=2, sort_keys=False)


def _table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("|" + "|".join("---" for _ in headers) + "|")
    for row in rows:
        lines.append("| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |")
    return lines


def render_markdown(result: ScanResult, include_detail: bool = True) -> str:
    """Erzeugt den Markdown-Portfolio-Report (REQ-006)."""
    s = result.summary
    lines: list[str] = []
    lines.append("# AETHEL Portfolio-Übersicht")
    lines.append("")
    lines.append(f"**Workspace:** `{result.workspace_root}`  ")
    lines.append(f"**Erzeugt:** {result.generated_at}")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.extend(
        _table(
            ["Kennzahl", "Wert"],
            [
                ["Echte Repositories", f"{s.repos}"],
                ["Worktree-Verzeichnisse", f"{s.worktree_dirs}"],
                ["Commits gesamt", f"{s.commits_total:,}"],
                ["Commits auf main", f"{s.commits_on_main:,}"],
                ["**Commits NICHT auf main**", f"**{s.commits_not_on_main:,}**"],
                ["Branches gesamt", f"{s.branches:,}"],
                ["Dirty Repositories", f"{s.dirty_repos}"],
                ["Inaktiv (> 90 Tage)", f"{s.stale_repos}"],
                ["Repos ohne main/master", f"{s.repos_without_main}"],
                ["Repos ohne origin", f"{s.repos_without_remote}"],
            ],
        )
    )
    lines.append("")

    lines.append("## Kategorien")
    lines.append("")
    lines.extend(
        _table(
            ["Kategorie", "Repos", "Commits", "nicht auf main", "Branches", "Reife (Median)"],
            [
                [
                    c.name,
                    str(c.repos),
                    f"{c.commits_total:,}",
                    f"{c.commits_not_on_main:,}",
                    str(c.branches),
                    str(c.median_maturity),
                ]
                for c in result.categories
            ],
        )
    )
    lines.append("")

    lines.append("## Top 20 — nicht auf main")
    lines.append("")
    top = sorted(result.repos, key=lambda r: -r.commits_not_on_main)[:20]
    lines.extend(
        _table(
            ["Repository", "nicht auf main", "auf main", "Branches", "ungemergt", "letzter Commit"],
            [
                [
                    r.name,
                    f"{r.commits_not_on_main:,}",
                    f"{r.commits_on_main:,}",
                    str(r.branches_total),
                    str(r.branches_unmerged),
                    r.last_commit_date or "-",
                ]
                for r in top
            ],
        )
    )
    lines.append("")

    lines.append("## Alleinstellungsmerkmale (interner Marktview)")
    lines.append("")
    view = market_mod.build(result.repos)
    if view.usps:
        lines.extend(
            _table(
                ["Repository", "Art", "Aussage", "Beleg"],
                [[u.repo, u.kind, u.claim, u.evidence] for u in view.usps],
            )
        )
    else:
        lines.append("_Keine USP-Kandidaten ableitbar._")
    lines.append("")

    lines.append("## Findings")
    lines.append("")
    if result.findings:
        lines.extend(
            _table(
                ["", "Code", "Repository", "Befund", "Empfehlung"],
                [
                    [
                        SEVERITY_MARK.get(f.severity, ""),
                        f.code,
                        f.repo,
                        f.message,
                        f.action,
                    ]
                    for f in result.findings[:80]
                ],
            )
        )
        if len(result.findings) > 80:
            lines.append("")
            lines.append(f"_… und {len(result.findings) - 80} weitere._")
    else:
        lines.append("_Keine Findings._")
    lines.append("")

    if include_detail:
        lines.append("## Detail je Repository")
        lines.append("")
        for repo in result.repos:
            lines.append(f"### {repo.name}")
            lines.append("")
            intent = repo.intent.text if repo.intent else None
            lines.append(f"- **Zweck:** {intent or '_nicht ermittelbar_'}")
            if repo.intent:
                lines.append(f"  - Quelle: `{repo.intent.source}` (Konfidenz {repo.intent.confidence})")
            lines.append(
                f"- **Commits:** {repo.commits_on_main:,} auf main · "
                f"{repo.commits_not_on_main:,} nicht auf main · {repo.branches_total} Branches"
            )
            lines.append(
                f"- **Letzter Commit:** {repo.last_commit_date or '-'} — {repo.last_commit_subject or '-'}"
            )
            if repo.maturity:
                lines.append(f"- **Reife:** {repo.maturity.score}/100 ({repo.maturity.grade})")
            if repo.manifest_entry:
                lines.append(
                    f"- **Manifest:** Kategorie `{repo.manifest_entry.category}`, "
                    f"Status `{repo.manifest_entry.status}`"
                )
            claims = market_mod.claims(repo)
            if claims:
                lines.append("- **Claims:**")
                for claim in claims:
                    lines.append(f"  - {claim}")
            if repo.findings:
                lines.append("- **Findings:**")
                for finding in repo.findings:
                    lines.append(
                        f"  - {SEVERITY_MARK.get(finding.severity, '')} `{finding.code}` {finding.message}"
                    )
            lines.append("")

    return "\n".join(lines)


def _html_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in row) + "</tr>" for row in rows
    )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def render_html(result: ScanResult) -> str:
    """Erzeugt den HTML-Portfolio-Report (REQ-006)."""
    s = result.summary
    view = market_mod.build(result.repos)
    parts: list[str] = []
    parts.append("<!doctype html>")
    parts.append('<html lang="de"><head><meta charset="utf-8">')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    parts.append("<title>AETHEL Portfolio-Übersicht</title>")
    parts.append(
        "<style>"
        ":root{--bg:#0f1115;--card:#171a21;--fg:#e8eaed;--muted:#9aa3b2;--accent:#6ea8fe;"
        "--crit:#ff6b6b;--warn:#ffd166;--ok:#4ade80;--line:#262b36}"
        "@media (prefers-color-scheme: light){:root{--bg:#f7f8fa;--card:#fff;--fg:#16181d;"
        "--muted:#5b6472;--line:#e3e6ec}}"
        "*{box-sizing:border-box}"
        "body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,"
        "BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;padding:24px}"
        "h1{font-size:1.6rem;margin:0 0 4px}h2{font-size:1.15rem;margin:32px 0 12px}"
        "h3{font-size:1rem;margin:24px 0 8px}"
        ".sub{color:var(--muted);margin-bottom:20px}"
        ".tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}"
        ".tile{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}"
        ".tile .n{font-size:1.5rem;font-weight:650;letter-spacing:-.02em}"
        ".tile .l{color:var(--muted);font-size:.8rem;text-transform:uppercase;letter-spacing:.04em}"
        "table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);"
        "border-radius:10px;overflow:hidden;margin-bottom:8px;font-size:.9rem}"
        "th{text-align:left;padding:8px 10px;background:rgba(110,168,254,.09);font-weight:600;"
        "border-bottom:1px solid var(--line);white-space:nowrap}"
        "td{padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top}"
        "tr:last-child td{border-bottom:none}"
        ".scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}"
        ".crit{color:var(--crit)}.warn{color:var(--warn)}.ok{color:var(--ok)}"
        "code{background:rgba(110,168,254,.12);padding:1px 5px;border-radius:4px;font-size:.85em}"
        ".repo{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;"
        "margin-bottom:10px}"
        ".repo h3{margin:0 0 6px}.meta{color:var(--muted);font-size:.85rem}"
        "ul{margin:6px 0 0;padding-left:20px}"
        "</style></head><body>"
    )
    parts.append("<h1>AETHEL Portfolio-Übersicht</h1>")
    parts.append(
        f'<p class="sub">{html.escape(result.workspace_root)} · {html.escape(result.generated_at)}</p>'
    )

    tiles = [
        ("Repositories", s.repos),
        ("Worktrees", s.worktree_dirs),
        ("Commits auf main", f"{s.commits_on_main:,}"),
        ("nicht auf main", f"{s.commits_not_on_main:,}"),
        ("Branches", f"{s.branches:,}"),
        ("Inaktiv > 90 T", s.stale_repos),
    ]
    parts.append('<div class="tiles">')
    for label, value in tiles:
        parts.append(f'<div class="tile"><div class="n">{html.escape(str(value))}</div>'
                     f'<div class="l">{html.escape(label)}</div></div>')
    parts.append("</div>")

    parts.append("<h2>Kategorien</h2><div class='scroll'>")
    parts.append(
        _html_table(
            ["Kategorie", "Repos", "Commits", "nicht auf main", "Branches", "Reife"],
            [
                [
                    c.name,
                    c.repos,
                    f"{c.commits_total:,}",
                    f"{c.commits_not_on_main:,}",
                    c.branches,
                    c.median_maturity,
                ]
                for c in result.categories
            ],
        )
    )
    parts.append("</div>")

    parts.append("<h2>Nicht auf main</h2><div class='scroll'>")
    parts.append(
        _html_table(
            ["Repository", "nicht auf main", "auf main", "Branches", "ungemergt", "letzter Commit"],
            [
                [
                    r.name,
                    f"{r.commits_not_on_main:,}",
                    f"{r.commits_on_main:,}",
                    r.branches_total,
                    r.branches_unmerged,
                    r.last_commit_date or "-",
                ]
                for r in sorted(result.repos, key=lambda x: -x.commits_not_on_main)[:25]
            ],
        )
    )
    parts.append("</div>")

    parts.append("<h2>Alleinstellungsmerkmale</h2>")
    if view.usps:
        parts.append('<div class="scroll">')
        parts.append(
            _html_table(
                ["Repository", "Art", "Aussage", "Beleg"],
                [[u.repo, u.kind, u.claim, u.evidence] for u in view.usps],
            )
        )
        parts.append("</div>")
    else:
        parts.append("<p class='sub'>Keine USP-Kandidaten ableitbar.</p>")

    parts.append("<h2>Findings</h2><div class='scroll'>")
    parts.append(
        _html_table(
            ["", "Code", "Repository", "Befund", "Empfehlung"],
            [
                [
                    SEVERITY_MARK.get(f.severity, ""),
                    f.code,
                    f.repo,
                    f.message,
                    f.action,
                ]
                for f in result.findings[:100]
            ],
        )
    )
    parts.append("</div>")

    parts.append("<h2>Detail</h2>")
    for repo in result.repos:
        intent = repo.intent.text if repo.intent else None
        parts.append('<div class="repo">')
        parts.append(f"<h3>{html.escape(repo.name)}</h3>")
        parts.append(f'<p class="meta">{html.escape(intent or "Zweck nicht ermittelbar")}</p>')
        meta = (
            f"{repo.commits_on_main:,} auf main · {repo.commits_not_on_main:,} nicht auf main · "
            f"{repo.branches_total} Branches · "
            f"Reife {repo.maturity.score if repo.maturity else 0}/100 · "
            f"{repo.last_commit_date or '-'}"
        )
        parts.append(f'<p class="meta">{html.escape(meta)}</p>')
        claims = market_mod.claims(repo)
        if claims:
            parts.append("<ul>")
            for claim in claims:
                parts.append(f"<li>{html.escape(claim)}</li>")
            parts.append("</ul>")
        parts.append("</div>")

    parts.append("</body></html>")
    return "\n".join(parts)
