"""CLI — eine dünne Hülle um die API.

Subcommands: scan · report · audit · market · forensics · code · factory · continuity · analyses · registers · stack · incubator · applefirst · cockpit
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import market as market_mod
from . import report as report_mod
from .scanner import load_snapshot, scan_workspace

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

    aix_cmd = add("aix-input", "Projektdossier an bestehenden AIX-Eingang binden (nur Kontext)")
    aix_cmd.add_argument("--input", required=True, help="Unfreigegebener aix.engineering_input.v1")
    aix_cmd.add_argument("--dossiers", required=True, help="Export aus dossier")
    aix_cmd.add_argument("--max-age-seconds", type=int, default=3600)
    aix_cmd.add_argument("--out", required=True)

    dossier_cmd = add("dossier", "Belegte Projektdossiers als PM-Input aus einem Scan-Snapshot")
    dossier_cmd.add_argument("--snapshot", required=True, help="JSON aus scan --json")
    dossier_cmd.add_argument("--out", default=None)

    inventory_cmd = add("inventory", "Rekursiver lokaler Vollständigkeitsabgleich, inkl. Nicht-Git-Projekte")
    inventory_cmd.add_argument("--format", choices=["md", "json"], default="json")
    inventory_cmd.add_argument("--out", default=None)

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

    analyses_cmd = add("analyses", "Analysen-Ablage: Berichte, Vorschläge und Kreisläufe lesen oder registrieren")
    analyses_mode = analyses_cmd.add_mutually_exclusive_group(required=True)
    analyses_mode.add_argument("--list", action="store_true", help="Alle registrierten Analysen")
    analyses_mode.add_argument("--show", metavar="ID", default=None, help="Eine Analyse ausgeben (Prüfsumme wird geprüft)")
    analyses_mode.add_argument("--proposals", action="store_true", help="Vorgeschlagene Projekte (vorschlaege.json)")
    analyses_mode.add_argument("--rat", action="store_true", help="Rat-Register")
    analyses_mode.add_argument("--geschaeftsfaelle", action="store_true", help="Geschäftsfälle")
    analyses_mode.add_argument("--loops", action="store_true", help="Definierte Kreisläufe (kreislaeufe.json)")
    analyses_mode.add_argument("--stats", action="store_true", help="Zähler der Ablage")
    analyses_mode.add_argument("--register", metavar="PATH", default=None, help="Markdown-Datei unter analysen/ registrieren")
    analyses_cmd.add_argument("--base", default=None, help="Ablage-Ordner (Default: <repo>/analysen)")
    analyses_cmd.add_argument("--scope", choices=["workspace", "aethelProjects", "fabrik", "firma", "stack"], default=None)
    analyses_cmd.add_argument("--summary", default=None, help="Ein Satz Zusammenfassung (für --register)")
    analyses_cmd.add_argument("--tags", default="", help="Kommagetrennte Schlagwörter (für --register)")
    analyses_cmd.add_argument("--id", default=None, help="Explizite ID (für --register)")
    analyses_cmd.add_argument("--date", default=None, help="Datum YYYY-MM-DD (für --register)")
    analyses_cmd.add_argument("--format", choices=["md", "json"], default="md")
    analyses_cmd.add_argument("--out", default=None, help="Zieldatei (Default: stdout)")

    registers_cmd = add("registers", "Register-Abgleich: Manifest, Scan, Projektprofile, Aufträge")
    registers_cmd.add_argument("--snapshot", required=True, help="JSON aus scan --json")
    registers_cmd.add_argument("--auftraege", default=None, help="auftraege.jsonl (Default: ~/.aix/auftraege/auftraege.jsonl, wenn vorhanden)")
    registers_cmd.add_argument("--profiles-root", default=None, help="Wurzel für .aix/project-profile.json (Default: --root)")
    registers_cmd.add_argument("--fail-on-drift", action="store_true", help="Exit-Code 1, wenn Drift vorliegt")
    registers_cmd.add_argument("--format", choices=["md", "json"], default="md")
    registers_cmd.add_argument("--out", default=None, help="Zieldatei (Default: stdout)")

    stack_cmd = add("stack", "Schichtenkarte: jedes Repo einer Stack-Schicht zugeordnet, leere Schichten sichtbar")
    stack_cmd.add_argument("--format", choices=["md", "json"], default="md")
    stack_cmd.add_argument("--repo", default=None, help="Nur ein Repository betrachten")
    stack_cmd.add_argument("--out", default=None, help="Zieldatei (Default: stdout)")

    applefirst_cmd = add("applefirst", "Apple-first-Audit: Sprachanteile, Apple-Frameworks, Unified Memory, Anti-Muster je Repo")
    applefirst_cmd.add_argument("--format", choices=["md", "json"], default="md")
    applefirst_cmd.add_argument("--repo", action="append", default=None, help="Nur diese Repositories (mehrfach möglich)")
    applefirst_cmd.add_argument("--min-score", type=int, default=None, help="Nur Repos mit Score unter N zeigen; Exit 1, wenn eines darunter liegt")
    applefirst_cmd.add_argument("--out", default=None, help="Zieldatei (Default: stdout)")

    cockpit_cmd = add("cockpit", "Leitstand: eine Seite aus Ablage, Vorschlägen, Kreisläufen und den jüngsten Läufen")
    cockpit_cmd.add_argument("--base", default=None, help="Ablage-Ordner (Default: <repo>/analysen)")
    cockpit_cmd.add_argument("--format", choices=["md", "json", "html"], default="md")
    cockpit_cmd.add_argument("--out", default=None, help="Zieldatei (Default: stdout)")

    incubator_cmd = add("incubator", "Inkubator-Reifeleiter: R0 Idee bis R11 Betrieb je Repo, mit Belegen und nächster Lücke")
    incubator_cmd.add_argument("--format", choices=["md", "json"], default="md")
    incubator_cmd.add_argument("--repo", action="append", default=None, help="Nur diese Repositories (mehrfach möglich)")
    incubator_cmd.add_argument("--klasse", choices=["produkt", "forschung", "infrastruktur", "inhalt"], default=None,
                               help="Nur Repos dieser Portfolio-Klasse")
    incubator_cmd.add_argument("--out", default=None, help="Zieldatei (Default: stdout)")

    for name in ("scan", "report", "audit", "market", "forensics", "code", "factory",
                 "continuity", "stack", "applefirst", "incubator"):
        sub.choices[name].add_argument("--snapshot", default=None, help="JSON aus scan --json")

    return parser


class _SnapshotMissing(FileNotFoundError):
    """Der angegebene Scan-Snapshot fehlt."""


def _scan(args: argparse.Namespace):
    """Lädt einen Snapshot oder scannt den Workspace."""
    if args.snapshot:
        try:
            return load_snapshot(args.snapshot)
        except FileNotFoundError as error:
            raise _SnapshotMissing(str(error)) from error
    return scan_workspace(args.root, jobs=args.jobs, timeout=args.timeout, manifest_path=args.manifest)


def _write(text: str, destination: str | None) -> None:
    if destination in (None, "-"):
        sys.stdout.write(text + "\n")
        return
    path = Path(destination)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n", encoding="utf-8")
    except OSError as exc:
        print(f"Ausgabe nicht schreibbar: {path}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


def _cmd_aix_input(args: argparse.Namespace) -> int:
    from . import aix_input
    source = json.loads(Path(args.input).read_text())
    dossiers = json.loads(Path(args.dossiers).read_text())
    result = aix_input.attach(source, dossiers, max_age_s=args.max_age_seconds)
    _write(json.dumps(result, ensure_ascii=False, indent=2), args.out)
    return EXIT_OK


def _cmd_dossier(args: argparse.Namespace) -> int:
    from . import dossier
    snapshot = json.loads(Path(args.snapshot).read_text())
    _write(json.dumps(dossier.build(snapshot), ensure_ascii=False, indent=2), args.out)
    return EXIT_OK


def _cmd_inventory(args: argparse.Namespace) -> int:
    from . import inventory
    result = inventory.build(args.root, jobs=args.jobs)
    output = (json.dumps(result, ensure_ascii=False, indent=2)
              if args.format == "json" else inventory.render_markdown(result))
    _write(output, args.out)
    return EXIT_OK


def _cmd_scan(args: argparse.Namespace) -> int:
    result = _scan(args)
    _write(report_mod.to_json(result), args.json)
    return EXIT_OK


def _cmd_report(args: argparse.Namespace) -> int:
    result = _scan(args)
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
    result = _scan(args)
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
    result = _scan(args)
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
    result = _scan(args)
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

    result = _scan(args)
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
        # Schlüssel ist der Pfad (Namen können doppelt vorkommen); ein Fehler in
        # einem Repo bricht den Lauf nicht ab, sondern wird je Repo festgehalten.
        try:
            analysis = code_mod.analyse_repo(
                repo, binary=binary, timeout=max(args.timeout, 120)
            )
        except Exception as exc:  # noqa: BLE001 - Fehler je Repo festhalten
            analysis = code_mod.CodeAnalysis(
                available=True,
                analyzed=False,
                schema=code_mod.AIX_SCHEMA,
                findings=(),
                rule_counts={},
                note=f"Analyse fehlgeschlagen: {type(exc).__name__}: {exc}",
            )
        return repo.path, repo.name, analysis

    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        ergebnisse = list(pool.map(run, targets))
    analysen = {path: analysis for path, _, analysis in ergebnisse}
    namen = {path: name for path, name, _ in ergebnisse}
    for _, name, analysis in ergebnisse:
        if analysis.note.startswith("Analyse fehlgeschlagen"):
            print(f"{name}: {analysis.note}", file=sys.stderr)

    threshold = SEVERITY_ORDER[args.severity]
    selected = [
        (namen[path], finding)
        for path, analysis in sorted(analysen.items(), key=lambda item: (namen[item[0]], item[0]))
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

    result = _scan(args)
    view = factory_mod.build(result.repos)

    if args.format == "json":
        _write(json.dumps(view.as_dict(), ensure_ascii=False, indent=2), args.out)
        return EXIT_OK

    lines = ["# Fabrik- und Firmensicht", ""]
    lines.append(f"Workspace: `{result.workspace_root}`  ")
    lines.append(f"Erzeugt: {result.generated_at}  ")
    lines.append(f"**Fabrik-Reifegrad aus Inhaltsbelegen: {view.reife}/100**  ")
    lines.append(f"Pfadabdeckung (bisher readiness): {view.readiness}/100; kein Reifenachweis.  ")
    lines.append(f"Vorhanden: {len(view.vorhanden)}; belegt: {len(view.belegt)}; Stubs: {len(view.stubs)}.  ")
    lines.append(f"**Kettenintegrität: {view.kettenintegritaet}/100**")
    lines.append("")
    lines.append(
        "> Pfade zeigen Vorhandensein; Inhaltsbelege belegen keine Funktion oder Ausführung. "
        "Die bisherige Trägerdarstellung beschreibt Pfadabdeckung."
    )
    lines.append("")

    lines.append("## Inhaltsbelege")
    lines.append("")
    for proof in view.belegt:
        lines.append(f"- {proof['repo']}: `{proof['path']}` — {proof['quelle']}; SHA-256 `{proof['sha256']}`")
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

    result = _scan(args)
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


def _cmd_analyses(args: argparse.Namespace) -> int:
    """Analysen-Ablage lesen oder eine Analyse registrieren (schreibt nur INDEX.json)."""
    from . import analyses as analyses_mod

    base = Path(args.base).expanduser() if args.base else analyses_mod.default_base()
    if not base.is_dir():
        sys.stderr.write(f"Ablage nicht gefunden: {base}\n")
        return EXIT_USAGE
    if args.out and _is_within(Path(args.out).expanduser(), base):
        sys.stderr.write("--out darf nicht in die Ablage zeigen (nur --register schreibt dort, und nur INDEX.json)\n")
        return EXIT_USAGE
    try:
        if args.list:
            entries = analyses_mod.list_entries(base)
            text = (json.dumps(analyses_mod.render_index_json(entries), ensure_ascii=False, indent=2, sort_keys=True)
                    if args.format == "json" else analyses_mod.render_index_markdown(entries))
        elif args.rat or args.geschaeftsfaelle:
            is_rat = args.rat
            records = analyses_mod.load_rat(base) if is_rat else analyses_mod.load_geschaeftsfaelle(base)
            key = "raete" if is_rat else "geschaeftsfaelle"
            schema = analyses_mod.SCHEMA_RAT if is_rat else analyses_mod.SCHEMA_GESCHAEFTSFAELLE
            rows = [record.as_dict() for record in records]
            if args.format == "json":
                text = json.dumps({"schema": schema, key: rows}, ensure_ascii=False, indent=2, sort_keys=True)
            else:
                headers = tuple(rows[0]) if rows else (("id",) if is_rat else ("produkt",))
                text = analyses_mod._table(headers, [tuple(row[k] if row[k] is not None else "" for k in headers) for row in rows])
        elif args.proposals:
            proposals = analyses_mod.load_proposals(base)
            text = (json.dumps(analyses_mod.render_proposals_json(proposals), ensure_ascii=False, indent=2, sort_keys=True)
                    if args.format == "json" else analyses_mod.render_proposals_markdown(proposals))
        elif args.loops:
            loops = analyses_mod.load_loops(base)
            text = (json.dumps(analyses_mod.render_loops_json(loops), ensure_ascii=False, indent=2, sort_keys=True)
                    if args.format == "json" else analyses_mod.render_loops_markdown(loops))
        elif args.stats:
            stats = analyses_mod.summary(base)
            text = (json.dumps({"schema": "aethel.projects.analysen-stats/v1", **stats}, ensure_ascii=False, indent=2, sort_keys=True) if args.format == "json"
                    else "\n".join(f"{key}: {value}" for key, value in sorted(stats.items())))
        elif args.show:
            markdown = analyses_mod.show(base, args.show)
            if args.format == "json":
                text = json.dumps({"schema": "aethel.projects.analyse/v1", "id": args.show, "markdown": markdown,
                                   "verified": not markdown.startswith(analyses_mod.CHANGED_WARNING)},
                                  ensure_ascii=False, indent=2)
            else:
                text = markdown
        else:
            if not args.scope or not args.summary:
                sys.stderr.write("--register braucht --scope und --summary\n")
                return EXIT_USAGE
            tags = tuple(tag.strip() for tag in args.tags.split(",") if tag.strip())
            entry = analyses_mod.register(base, Path(args.register).expanduser(), scope=args.scope,
                                          summary=args.summary, tags=tags, entry_id=args.id, date=args.date)
            text = (json.dumps(entry.as_dict(), ensure_ascii=False, indent=2, sort_keys=True) if args.format == "json"
                    else f"registriert: {entry.id} ({entry.date}) → {entry.path}")
    except KeyError as error:
        sys.stderr.write(f"Unbekannte Analyse: {error.args[0] if error.args else error}\n")
        return EXIT_ERROR
    except (FileNotFoundError, ValueError) as error:
        # Datenfehler (kaputtes Register, fehlende registrierte Datei): Exit 1, kein Bedienfehler
        sys.stderr.write(f"{error}\n")
        return EXIT_ERROR
    _write(text, args.out)
    return EXIT_OK


def _is_within(candidate: Path, base: Path) -> bool:
    """Liegt ``candidate`` in ``base``? Robust gegen Groß-/Kleinschreibung (APFS) und Symlinks."""
    import os

    try:
        target = candidate.resolve()
    except OSError:
        target = candidate.absolute()
    root = base.resolve()
    if target == root or root in target.parents:
        return True
    return os.path.normcase(str(target)).casefold().startswith(os.path.normcase(str(root)).casefold() + os.sep)


def _cmd_registers(args: argparse.Namespace) -> int:
    """Vier lokale Register gegeneinander: Manifest, Scan, Projektprofile, Aufträge (GitHub wird nicht abgefragt)."""
    from . import manifest as manifest_mod
    from . import registers as registers_mod

    snapshot = Path(args.snapshot).expanduser()
    if not snapshot.is_file():
        sys.stderr.write(f"Snapshot nicht gefunden: {snapshot} (erzeugen mit: aethel-projects scan --json <pfad>)\n")
        return EXIT_USAGE
    try:
        scan = registers_mod.load_scan(snapshot)
    except ValueError as error:
        sys.stderr.write(f"{error}\n")
        return EXIT_ERROR
    # Explizit genannte Pfade müssen existieren; nur Defaults dürfen fehlen.
    for label, value in (("--manifest", args.manifest), ("--auftraege", args.auftraege), ("--profiles-root", args.profiles_root)):
        if value and not Path(value).expanduser().exists():
            sys.stderr.write(f"{label} nicht gefunden: {value}\n")
            return EXIT_USAGE
    manifest_path = Path(args.manifest).expanduser() if args.manifest else manifest_mod.DEFAULT_MANIFEST
    if not manifest_path.is_file():
        sys.stderr.write(f"Hinweis: Manifest fehlt ({manifest_path}); alle Repos erscheinen als ohne Manifest-Eintrag\n")
    manifest = manifest_mod.load_manifest(manifest_path)
    profiles = registers_mod.find_profiles(Path(args.profiles_root or args.root).expanduser())
    auftraege_path = Path(args.auftraege).expanduser() if args.auftraege else registers_mod.DEFAULT_AUFTRAEGE
    auftraege, lines = registers_mod.load_auftraege(auftraege_path if auftraege_path.is_file() else None)
    drift = registers_mod.reconcile(scan, manifest, profiles, auftraege,
                                    manifest_path=manifest_path if manifest_path.is_file() else None,
                                    auftraege_lines=lines)
    _write(registers_mod.render_json(drift) if args.format == "json" else registers_mod.render_markdown(drift), args.out)
    if args.fail_on_drift and drift.has_drift:
        return EXIT_ERROR
    return EXIT_OK


def _cmd_stack(args: argparse.Namespace) -> int:
    """Schichtenkarte des Gesamtstacks."""
    from . import stack as stack_mod

    result = _scan(args)
    repos = result.repos
    if args.repo:
        repos = tuple(r for r in repos if r.name == args.repo)
        if not repos:
            sys.stderr.write(f"Repository nicht gefunden: {args.repo}\n")
            return EXIT_ERROR
    stack_map = stack_mod.build(repos, Path(args.root).expanduser())
    _write(stack_mod.render_json(stack_map) if args.format == "json" else stack_mod.render_markdown(stack_map), args.out)
    return EXIT_OK


def _cmd_applefirst(args: argparse.Namespace) -> int:
    """Apple-first-Audit über den Workspace."""
    from . import applefirst as applefirst_mod

    result = _scan(args)
    repos = result.repos
    if args.repo:
        wanted = set(args.repo)
        repos = tuple(r for r in repos if r.name in wanted)
        if not repos:
            sys.stderr.write(f"Repository nicht gefunden: {', '.join(sorted(wanted))}\n")
            return EXIT_ERROR
    items = applefirst_mod.build(repos, Path(args.root).expanduser())
    below = False
    if args.min_score is not None:
        items = tuple(i for i in items if i.score is not None and i.score < args.min_score)
        below = bool(items)
    _write(applefirst_mod.render_json(items) if args.format == "json" else applefirst_mod.render_markdown(items), args.out)
    return EXIT_ERROR if below else EXIT_OK


def _cmd_cockpit(args: argparse.Namespace) -> int:
    """Leitstand aus der Analysen-Ablage; rechnet nichts neu, schreibt nur --out."""
    from . import analyses as analyses_mod
    from . import cockpit as cockpit_mod

    base = Path(args.base).expanduser() if args.base else analyses_mod.default_base()
    if not base.is_dir():
        sys.stderr.write(f"Ablage nicht gefunden: {base}\n")
        return EXIT_USAGE
    if args.out:
        out = Path(args.out).expanduser()
        try:
            target = out.resolve()
        except OSError:
            target = out.absolute()
        # Name und Endung am aufgelösten Ziel prüfen, damit kein Symlink auf INDEX.json führt.
        allowed = target.name.lower().startswith("leitstand") and target.suffix.lower() in {".md", ".html", ".json"}
        if _is_within(target, base) and not allowed:
            sys.stderr.write("--out in der Ablage nur als LEITSTAND-*.md/.html/.json\n")
            return EXIT_USAGE
    try:
        view = cockpit_mod.build(base)
    except ValueError as error:
        sys.stderr.write(f"{error}\n")
        return EXIT_ERROR
    if args.format == "json":
        text = cockpit_mod.render_json(view)
    elif args.format == "html":
        text = cockpit_mod.render_html(view)
    else:
        text = cockpit_mod.render_markdown(view)
    _write(text, args.out)
    return EXIT_OK


def _cmd_incubator(args: argparse.Namespace) -> int:
    """Inkubator-Reifeleiter über den Workspace."""
    from . import incubator as incubator_mod

    result = _scan(args)
    repos = result.repos
    if args.repo:
        wanted = set(args.repo)
        repos = tuple(r for r in repos if r.name in wanted)
        if not repos:
            sys.stderr.write(f"Repository nicht gefunden: {', '.join(sorted(wanted))}\n")
            return EXIT_ERROR
    items = incubator_mod.build(repos, Path(args.root).expanduser())
    if args.klasse:
        items = tuple(i for i in items if i.klasse == args.klasse)
    _write(incubator_mod.render_json(items) if args.format == "json" else incubator_mod.render_markdown(items), args.out)
    return EXIT_OK


COMMANDS = {
    "aix-input": _cmd_aix_input,
    "inventory": _cmd_inventory,
    "dossier": _cmd_dossier,
    "scan": _cmd_scan,
    "report": _cmd_report,
    "audit": _cmd_audit,
    "market": _cmd_market,
    "forensics": _cmd_forensics,
    "code": _cmd_code,
    "factory": _cmd_factory,
    "continuity": _cmd_continuity,
    "analyses": _cmd_analyses,
    "registers": _cmd_registers,
    "stack": _cmd_stack,
    "applefirst": _cmd_applefirst,
    "cockpit": _cmd_cockpit,
    "incubator": _cmd_incubator,
}


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not Path(args.root).expanduser().is_dir():
        sys.stderr.write(f"Workspace-Wurzel nicht lesbar: {args.root}\n")
        return EXIT_ERROR
    try:
        return COMMANDS[args.command](args)
    except _SnapshotMissing as error:
        sys.stderr.write(f"Fehler: {error}\n")
        return EXIT_USAGE
    except (OSError, ValueError) as error:
        sys.stderr.write(f"Fehler: {error}\n")
        return EXIT_ERROR


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
