"""CLI — eine dünne Hülle um die API.

Subcommands: scan · report · audit · market · forensics · code · factory · continuity
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import market as market_mod
from . import report as report_mod
from .scanner import scan_workspace

DEFAULT_ROOT = Path.home() / "workspace"
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2

SEVERITY_ORDER = {"critical": 0, "warn": 1, "info": 2}


def _common_args(parser: argparse.ArgumentParser, suppress: bool) -> None:
    """Die gemeinsamen Optionen — vor *und* nach dem Unterbefehl nutzbar.

    ``suppress=True`` verhindert, dass der Subparser den Wert der Hauptzeile
    überschreibt: ohne SUPPRESS setzt argparse den Default und damit den
    Wert vor dem Unterbefehl weg.
    """

    def default(value):
        return argparse.SUPPRESS if suppress else value

    parser.add_argument(
        "--root", default=default(str(DEFAULT_ROOT)),
        help="Workspace-Wurzel (Default: ~/workspace)",
    )
    parser.add_argument(
        "--jobs", type=int, default=default(8),
        help="Parallelfaktor für den Scan",
    )
    parser.add_argument(
        "--timeout", type=int, default=default(30),
        help="Timeout je Git-Aufruf in Sekunden",
    )
    parser.add_argument(
        "--manifest", default=default(None), help="Pfad zu projects.yaml",
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aethel-projects",
        description="Portfolio-Analyse des AETHEL-Workspace — ausschließlich lesend.",
    )
    _common_args(parser, suppress=False)

    sub = parser.add_subparsers(dest="command", required=True)

    def add(name: str, help_text: str) -> argparse.ArgumentParser:
        child = sub.add_parser(name, help=help_text)
        _common_args(child, suppress=True)
        return child

    scan_cmd = add("scan", "JSON-Snapshot des gesamten Workspace")
    scan_cmd.add_argument("--json", default="-", help="Zieldatei für JSON ('-' = stdout)")

    report_cmd = add("report", "Portfolio-Report als Markdown oder HTML")
    report_cmd.add_argument("--format", choices=["md", "html"], default="md")
    report_cmd.add_argument("--out", default=None, help="Ausgabeverzeichnis (Default: ./reports)")
    report_cmd.add_argument("--no-detail", action="store_true", help="Detailtabelle weglassen")

    audit_cmd = add("audit", "Findings und Aufräum-Vorschläge")
    audit_cmd.add_argument("--format", choices=["md", "json"], default="md")
    audit_cmd.add_argument("--severity", choices=["critical", "warn", "info"], default="info")
    audit_cmd.add_argument("--out", default=None, help="Zieldatei (Default: stdout)")

    market_cmd = add("market", "Marktview, USP und Marketing-Claims")
    market_cmd.add_argument("--format", choices=["md", "json"], default="md")
    market_cmd.add_argument("--out", default=None, help="Zieldatei (Default: stdout)")

    forensics_cmd = add(
        "forensics", "Forensik: das Hässliche, das Schöne, das Interessante"
    )
    forensics_cmd.add_argument("--format", choices=["md", "json"], default="md")
    forensics_cmd.add_argument("--kind", choices=["hässlich", "schön", "interessant", "alle"], default="alle")
    forensics_cmd.add_argument("--repo", default=None, help="Nur ein Repository betrachten")
    forensics_cmd.add_argument("--out", default=None, help="Zieldatei (Default: stdout)")

    code_cmd = add("code", "Statische Code-Analyse via aethelCodeAnalyzer")
    code_cmd.add_argument("--format", choices=["md", "json"], default="md")
    code_cmd.add_argument("--repo", default=None, help="Nur ein Repository analysieren")
    code_cmd.add_argument("--limit", type=int, default=0, help="Maximal N Repos (0 = alle)")
    code_cmd.add_argument("--severity", choices=["critical", "warn", "info"], default="warn")
    code_cmd.add_argument("--out", default=None, help="Zieldatei (Default: stdout)")

    factory_cmd = add("factory", "Fabrik- und Firmensicht: Wertschöpfungskette und Lücken")
    factory_cmd.add_argument("--format", choices=["md", "json"], default="md")
    factory_cmd.add_argument("--out", default=None, help="Zieldatei (Default: stdout)")

    continuity_cmd = add("continuity", "Kontinuität: wo war ich, was ist offen, was kommt als Nächstes")
    continuity_cmd.add_argument("--format", choices=["md", "json"], default="md")
    continuity_cmd.add_argument("--repo", default=None, help="Nur ein Repository betrachten")
    continuity_cmd.add_argument("--out", default=None, help="Zieldatei (Default: stdout)")

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


def _cmd_code(args: argparse.Namespace) -> int:
    """Statische Code-Analyse via aethelCodeAnalyzer."""
    from . import codeanalysis as code_mod

    result = scan_workspace(args.root, jobs=args.jobs, timeout=args.timeout, manifest_path=args.manifest)
    binary = code_mod.find_analyzer()
    if binary is None:
        sys.stderr.write(
            "aethelCodeAnalyzer nicht gefunden — setze AETHEL_CODE_ANALYZER_BIN "
            "oder baue das Binary.\n"
        )
        return EXIT_ERROR

    targets = [r for r in result.repos if code_mod.is_analysable(r)]
    if args.repo:
        targets = [r for r in targets if r.name == args.repo]
    if args.limit > 0:
        targets = targets[: args.limit]

    def run(repo):
        return repo.name, code_mod.analyse_repo(repo, binary=binary, timeout=max(args.timeout, 120))

    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        analysen = dict(pool.map(run, targets))

    threshold = SEVERITY_ORDER[args.severity]
    selected = [
        (name, analysis)
        for name, analysis in sorted(analysen.items())
        for finding in analysis.findings
        if SEVERITY_ORDER.get(finding.severity, 3) <= threshold
    ]

    if args.format == "json":
        _write(
            json.dumps(
                {
                    "analyzer": str(binary),
                    "schema": code_mod.AIX_SCHEMA,
                    "repos_analysiert": sum(1 for a in analysen.values() if a.analyzed),
                    "findings": [
                        {
                            "repo": name,
                            "code": f.code,
                            "severity": f.severity,
                            "message": f.message,
                            "action": f.action,
                        }
                        for name, f in selected
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            args.out,
        )
        return EXIT_OK

    stats = code_mod.summarise(analysen)
    lines = ["# Code-Analyse (aethelCodeAnalyzer)", ""]
    lines.append(f"Analyzer: `{binary}`  ")
    lines.append(f"Schema: `{code_mod.AIX_SCHEMA}`  ")
    lines.append(
        f"Analysiert: {stats['repos_analysiert']} von {stats['repos_gefunden']} Repos · "
        f"Findings: {stats['findings']} (davon {stats['high']} mit Schweregrad high)"
    )
    lines.append("")
    lines.append("> Der Analyzer liest nur. Er schreibt ausser nach stdout nichts.")
    lines.append("")

    by_repo: dict[str, list] = {}
    for name, finding in selected:
        by_repo.setdefault(name, []).append(finding)
    if not by_repo:
        lines.append("_Keine Findings oberhalb des Schweregrads._")
    for name in sorted(by_repo):
        lines.append(f"## {name}")
        lines.append("")
        lines.append("| Schwere | Regel | Befund | Repro |")
        lines.append("|---|---|---|---|")
        for finding in by_repo[name]:
            lines.append(
                f"| {finding.severity} | `{finding.code.removeprefix('code:')}` | "
                f"{finding.message} | `{finding.action}` |"
            )
        lines.append("")

    notes = [(name, a.note) for name, a in sorted(analysen.items()) if a.note]
    if notes:
        lines.append("## Hinweise")
        lines.append("")
        for name, note in notes:
            lines.append(f"- **{name}**: {note}")
        lines.append("")

    _write("\n".join(lines), args.out)
    return EXIT_OK


def _cmd_factory(args: argparse.Namespace) -> int:
    """Fabrik- und Firmensicht."""
    from . import factory as factory_mod

    result = scan_workspace(args.root, jobs=args.jobs, timeout=args.timeout, manifest_path=args.manifest)
    view = factory_mod.build(result.repos)

    if args.format == "json":
        _write(json.dumps(view.as_dict(), ensure_ascii=False, indent=2), args.out)
        return EXIT_OK

    lines = ["# Fabrik- und Firmensicht", ""]
    lines.append(f"Workspace: `{result.workspace_root}`  ")
    lines.append(f"Erzeugt: {result.generated_at}  ")
    lines.append(f"**Fabrik-Reifegrad: {view.readiness}/100**  ")
    lines.append(f"**Kettenintegrität: {view.kettenintegritaet}/100**")
    lines.append("")
    lines.append(
        "> Geprüft wird gegen **Belege** (Dateien, Workflows, Verträge), nicht gegen "
        "Absichtserklärungen. Ein **Träger** erfüllt *alle* Anforderungen einer Stufe — "
        "erst er zählt als vorhanden."
    )
    lines.append("")

    lines.append("## Wertschöpfungskette")
    lines.append("")
    lines.append("| Stufe | Zustand | Träger | Mitwirkende | Bedeutung |")
    lines.append("|---|---|---|---|---|")
    for stage in view.stages:
        mark = {"voll": "🟢", "teilweise": "🟡", "leer": "🔴"}[stage.level]
        lines.append(
            f"| **{stage.label}** | {mark} {stage.level} | {len(stage.carriers)} | "
            f"{len(stage.covered_by)} | {stage.description} |"
        )
    lines.append("")

    for stage in view.stages:
        if not stage.carriers:
            continue
        lines.append(f"### {stage.label} — Träger")
        lines.append("")
        for name in stage.carriers[:12]:
            lines.append(f"- **{name}** — {stage.evidence.get(name, '')}")
        if len(stage.carriers) > 12:
            lines.append(f"- … und {len(stage.carriers) - 12} weitere")
        lines.append("")

    if view.end_to_end:
        lines.append("## End-to-End-Ketten")
        lines.append("")
        lines.append(
            "Diese Repos tragen die Kette von der Marktanforderung bis zur Rückkopplung "
            "fast vollständig — sie sind das Nächstliegende zu einer digitalen Firma:"
        )
        lines.append("")
        for name in view.end_to_end[:20]:
            lines.append(f"- **{name}**")
        lines.append("")

    lines.append("## Rollen im Portfolio")
    lines.append("")
    lines.append("| Rolle | Repos | Beispiele |")
    lines.append("|---|---|---|")
    role_labels = {
        "kern": "Kern / Plattform",
        "produkt": "Produkt",
        "werkzeug": "Werkzeug der Fabrik",
        "wissen": "Wissen / DNA",
        "infrastruktur": "Infrastruktur",
        "experiment": "Experiment",
    }
    for role, names in view.roles.items():
        examples = ", ".join(names[:5]) + (f" … (+{len(names) - 5})" if len(names) > 5 else "")
        lines.append(f"| {role_labels.get(role, role)} | {len(names)} | {examples} |")
    lines.append("")

    lines.append("## Fabrik-Motor und Fabrik-Output")
    lines.append("")
    lines.append(f"**Motor** ({len(view.engine)}): {', '.join(view.engine) or '—'}")
    lines.append("")
    lines.append(f"**Output** ({len(view.output)}): {', '.join(view.output) or '—'}")
    lines.append("")

    lines.append("## Lücken")
    lines.append("")
    if view.gaps:
        for gap in view.gaps:
            lines.append(f"- {gap}")
    else:
        lines.append("_Keine Lücke erkennbar._")
    lines.append("")

    if view.notes:
        lines.append("## Anmerkungen")
        lines.append("")
        for note in view.notes:
            lines.append(f"- {note}")
        lines.append("")

    _write("\n".join(lines), args.out)
    return EXIT_OK


def _cmd_continuity(args: argparse.Namespace) -> int:
    """Kontinuität über den Workspace."""
    from . import continuity as continuity_mod

    result = scan_workspace(args.root, jobs=args.jobs, timeout=args.timeout, manifest_path=args.manifest)
    repos = result.repos
    if args.repo:
        repos = tuple(r for r in repos if r.name == args.repo)
        if not repos:
            sys.stderr.write(f"Repository nicht gefunden: {args.repo}\n")
            return EXIT_ERROR

    view = continuity_mod.build(repos)

    if args.format == "json":
        _write(json.dumps(view.as_dict(), ensure_ascii=False, indent=2), args.out)
        return EXIT_OK

    lines = ["# Kontinuität — wo war ich, was ist offen, was kommt", ""]
    lines.append(f"Workspace: `{result.workspace_root}`  ")
    lines.append(f"Erzeugt: {result.generated_at}  ")
    lines.append(f"Offene Arbeit: **{view.offene_arbeit:,} Commits** ausserhalb von main  ")
    lines.append(f"Repos mit uncommitteten Änderungen: **{view.uncommittet}**")
    lines.append("")
    if view.hinweis:
        lines.append(f"> {view.hinweis}")
        lines.append("")
    if view.naechster_schritt:
        lines.append(f"**Nächster Schritt:** {view.naechster_schritt}")
        lines.append("")

    lines.append("## Zuletzt angefasst")
    lines.append("")
    lines.append("| Repository | Standort | Offen | Nächster Schritt | Dringlichkeit |")
    lines.append("|---|---|---|---|---|")
    for state in view.zuletzt:
        offen = "; ".join(state.offen[:2]) or "—"
        step = state.naechster_schritt or "—"
        lines.append(
            f"| **{state.repo}** | {state.standort} | {offen} | {step} | {state.dringlichkeit} |"
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
    "code": _cmd_code,
    "factory": _cmd_factory,
    "continuity": _cmd_continuity,
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
