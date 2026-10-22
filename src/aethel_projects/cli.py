"""CLI — eine dünne Hülle um die API.

Subcommands: scan · report · audit · market
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import market as market_mod
from . import report as report_mod
from .scanner import scan_workspace

DEFAULT_ROOT = Path.home() / "workspace"
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2

SEVERITY_ORDER = {"critical": 0, "warn": 1, "info": 2}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aethel-projects",
        description="Portfolio-Analyse des AETHEL-Workspace — ausschließlich lesend.",
    )
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="Workspace-Wurzel (Default: ~/workspace)")
    parser.add_argument("--jobs", type=int, default=8, help="Parallelfaktor für den Scan")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout je Git-Aufruf in Sekunden")
    parser.add_argument("--manifest", default=None, help="Pfad zu projects.yaml")

    sub = parser.add_subparsers(dest="command", required=True)

    scan_cmd = sub.add_parser("scan", help="JSON-Snapshot des gesamten Workspace")
    scan_cmd.add_argument("--json", default="-", help="Zieldatei für JSON ('-' = stdout)")

    report_cmd = sub.add_parser("report", help="Portfolio-Report als Markdown oder HTML")
    report_cmd.add_argument("--format", choices=["md", "html"], default="md")
    report_cmd.add_argument("--out", default=None, help="Ausgabeverzeichnis (Default: ./reports)")
    report_cmd.add_argument("--no-detail", action="store_true", help="Detailtabelle weglassen")

    audit_cmd = sub.add_parser("audit", help="Findings und Aufräum-Vorschläge")
    audit_cmd.add_argument("--format", choices=["md", "json"], default="md")
    audit_cmd.add_argument("--severity", choices=["critical", "warn", "info"], default="info")
    audit_cmd.add_argument("--out", default=None, help="Zieldatei (Default: stdout)")

    market_cmd = sub.add_parser("market", help="Marktview, USP und Marketing-Claims")
    market_cmd.add_argument("--format", choices=["md", "json"], default="md")
    market_cmd.add_argument("--out", default=None, help="Zieldatei (Default: stdout)")

    forensics_cmd = sub.add_parser(
        "forensics", help="Forensik: das Hässliche, das Schöne, das Interessante"
    )
    forensics_cmd.add_argument("--format", choices=["md", "json"], default="md")
    forensics_cmd.add_argument("--kind", choices=["hässlich", "schön", "interessant", "alle"], default="alle")
    forensics_cmd.add_argument("--repo", default=None, help="Nur ein Repository betrachten")
    forensics_cmd.add_argument("--out", default=None, help="Zieldatei (Default: stdout)")

    return parser


def _write(text: str, destination: str | None) -> None:
    if destination in (None, "-"):
        sys.stdout.write(text + "\n")
        return
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + "\n", encoding="utf-8")


def _cmd_scan(args: argparse.Namespace) -> int:
    result = scan_workspace(args.root, jobs=args.jobs, timeout=args.timeout, manifest_path=args.manifest)
    _write(report_mod.to_json(result), args.json)
    return EXIT_OK


def _cmd_report(args: argparse.Namespace) -> int:
    result = scan_workspace(args.root, jobs=args.jobs, timeout=args.timeout, manifest_path=args.manifest)
    if args.format == "html":
        text = report_mod.render_html(result)
        suffix = "html"
    else:
        text = report_mod.render_markdown(result, include_detail=not args.no_detail)
        suffix = "md"
    out_dir = Path(args.out or "reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"aethel-projects.{suffix}"
    target.write_text(text + "\n", encoding="utf-8")
    sys.stdout.write(f"Report geschrieben: {target}\n")
    return EXIT_OK


def _cmd_audit(args: argparse.Namespace) -> int:
    result = scan_workspace(args.root, jobs=args.jobs, timeout=args.timeout, manifest_path=args.manifest)
    threshold = SEVERITY_ORDER[args.severity]
    selected = [f for f in result.findings if SEVERITY_ORDER.get(f.severity, 3) <= threshold]

    if args.format == "json":
        _write(
            json.dumps(
                [
                    {
                        "code": f.code,
                        "severity": f.severity,
                        "repo": f.repo,
                        "message": f.message,
                        "action": f.action,
                    }
                    for f in selected
                ],
                ensure_ascii=False,
                indent=2,
            ),
            args.out,
        )
        return EXIT_OK

    lines = ["# Audit — Aufräum- und Risikohinweise", ""]
    lines.append(f"Workspace: `{result.workspace_root}`  ")
    lines.append(f"Erzeugt: {result.generated_at}  ")
    lines.append(f"Findings: {len(selected)} (Schweregrad ≥ {args.severity})")
    lines.append("")
    lines.append("> **Nichts wird automatisch ausgeführt.** Alle Vorschläge sind Empfehlungen.")
    lines.append("")
    lines.append("| | Code | Repository | Befund | Empfehlung |")
    lines.append("|---|---|---|---|---|")
    for finding in selected:
        mark = {"critical": "🔴", "warn": "🟡", "info": "🔵"}.get(finding.severity, "")
        lines.append(
            f"| {mark} | `{finding.code}` | {finding.repo} | {finding.message} | {finding.action} |"
        )
    _write("\n".join(lines), args.out)
    return EXIT_OK


def _cmd_market(args: argparse.Namespace) -> int:
    result = scan_workspace(args.root, jobs=args.jobs, timeout=args.timeout, manifest_path=args.manifest)
    view = market_mod.build(result.repos)

    if args.format == "json":
        _write(
            json.dumps(
                {
                    "scope": view.scope,
                    "categories": [
                        {
                            "name": c.name,
                            "repos": c.repos,
                            "commits_total": c.commits_total,
                            "commits_not_on_main": c.commits_not_on_main,
                            "median_maturity": c.median_maturity,
                            "crowded": c.crowded,
                            "thin": c.thin,
                            "gap": c.gap,
                        }
                        for c in view.categories
                    ],
                    "usps": [
                        {"repo": u.repo, "kind": u.kind, "claim": u.claim, "evidence": u.evidence}
                        for u in view.usps
                    ],
                    "positioning": view.positioning,
                },
                ensure_ascii=False,
                indent=2,
            ),
            args.out,
        )
        return EXIT_OK

    lines = ["# Marktview (internes AETHEL-Portfolio)", ""]
    lines.append(f"**Scope:** `{view.scope}` — beschreibt die Positionierung im AETHEL-Portfolio,")
    lines.append("nicht den Weltmarkt. Externe Wettbewerberdaten wären offline nicht belastbar.")
    lines.append("")
    lines.append("## Kategorie-Abdeckung")
    lines.append("")
    lines.append("| Kategorie | Repos | Commits | nicht auf main | Reife (Median) | Bewertung |")
    lines.append("|---|---|---|---|---|---|")
    for category in view.categories:
        notes = []
        if category.crowded:
            notes.append("überbesetzt")
        if category.thin:
            notes.append("dünn besetzt")
        if category.gap:
            notes.append("Lücke")
        lines.append(
            f"| {category.name} | {category.repos} | {category.commits_total:,} | "
            f"{category.commits_not_on_main:,} | {category.median_maturity} | "
            f"{', '.join(notes) or '—'} |"
        )
    lines.append("")
    lines.append("## Alleinstellungsmerkmale")
    lines.append("")
    if view.usps:
        lines.append("| Repository | Art | Aussage | Beleg |")
        lines.append("|---|---|---|---|")
        for usp in view.usps:
            lines.append(f"| {usp.repo} | {usp.kind} | {usp.claim} | {usp.evidence} |")
    else:
        lines.append("_Keine ableitbar._")
    lines.append("")
    lines.append("## Marketing-Claims je Repository")
    lines.append("")
    for repo in result.repos:
        claims = market_mod.claims(repo)
        if not claims:
            continue
        position = view.positioning.get(repo.name, "")
        lines.append(f"**{repo.name}** {f'({position})' if position else ''}")
        lines.append("")
        for claim in claims:
            lines.append(f"- {claim}")
        lines.append("")
    _write("\n".join(lines), args.out)
    return EXIT_OK


def _cmd_forensics(args: argparse.Namespace) -> int:
    result = scan_workspace(args.root, jobs=args.jobs, timeout=args.timeout, manifest_path=args.manifest)
    from . import forensics as forensics_mod

    selected = tuple(result.repos)
    if args.repo:
        selected = tuple(r for r in selected if r.name == args.repo)
        if not selected:
            sys.stderr.write(f"Repository nicht gefunden: {args.repo}\n")
            return EXIT_ERROR

    observations = list(forensics_mod.inspect_workspace(selected))
    for repo in selected:
        observations.extend(forensics_mod.inspect(repo))
    if args.kind != "alle":
        observations = [o for o in observations if o.kind == args.kind]
    observations.sort(key=lambda o: (-o.weight, o.repo.lower(), o.code))

    if args.format == "json":
        _write(
            json.dumps(
                [
                    {
                        "repo": o.repo,
                        "kind": o.kind,
                        "code": o.code,
                        "title": o.title,
                        "observation": o.observation,
                        "suggestion": o.suggestion,
                        "weight": o.weight,
                    }
                    for o in observations
                ],
                ensure_ascii=False,
                indent=2,
            ),
            args.out,
        )
        return EXIT_OK

    counts = forensics_mod.summarise(observations)
    lines = ["# Forensik — das Hässliche, das Schöne, das Interessante", ""]
    lines.append(f"Workspace: `{result.workspace_root}`  ")
    lines.append(f"Erzeugt: {result.generated_at}  ")
    lines.append(
        f"Beobachtungen: {counts.get('hässlich', 0)} hässlich · "
        f"{counts.get('schön', 0)} schön · {counts.get('interessant', 0)} interessant"
    )
    lines.append("")
    lines.append("> Jede Beobachtung nennt die messbare Grundlage. Es wird nichts ausgeführt.")
    lines.append("")

    for kind in ("hässlich", "schön", "interessant"):
        group = [o for o in observations if o.kind == kind]
        if not group:
            continue
        lines.append(f"## {kind.capitalize()}")
        lines.append("")
        lines.append("| Gewicht | Repository | Befund | Beobachtung | Vorschlag |")
        lines.append("|---|---|---|---|---|")
        for observation in group:
            lines.append(
                f"| {observation.weight} | {observation.repo} | **{observation.title}** | "
                f"{observation.observation} | {observation.suggestion} |"
            )
        lines.append("")

    _write("\n".join(lines), args.out)
    return EXIT_OK


COMMANDS = {
    "scan": _cmd_scan,
    "report": _cmd_report,
    "audit": _cmd_audit,
    "market": _cmd_market,
    "forensics": _cmd_forensics,
}


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not Path(args.root).expanduser().is_dir():
        sys.stderr.write(f"Workspace-Wurzel nicht lesbar: {args.root}\n")
        return EXIT_ERROR
    try:
        return COMMANDS[args.command](args)
    except (OSError, ValueError) as error:
        sys.stderr.write(f"Fehler: {error}\n")
        return EXIT_ERROR


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
