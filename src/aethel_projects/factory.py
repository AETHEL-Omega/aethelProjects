"""Fabrik- und Firmensicht: wo steht die digitale Fabrik, was fehlt für die digitale Firma.

aethelProjects beantwortet die Frage, die kein Einzel-Repo beantworten kann:
**Sind die Bausteine einer digitalen Firma vollständig vorhanden — und wo ist die Lücke?**

Zwei Ebenen:

* **Wertschöpfungskette** — die acht Stufen von der Marktanforderung bis zur
  Rückkopplung. Jede Stufe wird gegen **Belege** geprüft (Dateien, Workflows,
  Verträge), nicht gegen Absichtserklärungen. Eine Stufe ohne Beleg ist *leer*.
* **Rollen** — was jedes Repository in der Fabrik ist: Kern, Produkt, Werkzeug,
  Wissen, Infrastruktur, Experiment. Daraus folgt die Trennung von *Fabrik-Motor*
  (baut die Fabrik) und *Fabrik-Output* (ist das Ergebnis der Fabrik).

Es wird nichts erfunden: jede Zuordnung nennt den Beleg, aus der sie folgt.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from .models import RepoReport

#: Die acht Stufen der digitalen Wertschöpfungskette.
STAGE_ORDER = (
    "markt",
    "entwurf",
    "bau",
    "sicherung",
    "freigabe",
    "auslieferung",
    "betrieb",
    "rueckkopplung",
)

STAGE_LABELS = {
    "markt": "Marktanforderung",
    "entwurf": "Entwurf",
    "bau": "Implementierung",
    "sicherung": "Qualitätssicherung",
    "freigabe": "Freigabe",
    "auslieferung": "Auslieferung",
    "betrieb": "Betrieb",
    "rueckkopplung": "Rückkopplung",
}

STAGE_DESCRIPTIONS = {
    "markt": "Die Frage, warum es das Produkt gibt — Intention, Zielgruppe, Abgrenzung.",
    "entwurf": "SPEC, DESIGN, ARCHITECTURE — die Entscheidungen vor dem Bau.",
    "bau": "Tatsächlicher Quellcode, der etwas tut.",
    "sicherung": "Tests, CI, Validierungsvertrag, Scorecard — die Qualitätsschleuse.",
    "freigabe": "Versionierung, Changelog, Release-Artefakt.",
    "auslieferung": "Deployment, Distribution, Publish an Dritte.",
    "betrieb": "Betrieb, Überwachung, Support, Incident.",
    "rueckkopplung": "Rückmeldung aus dem Betrieb und vom Markt — der Motor der Schleife.",
}

#: Gewichtung der Stufen für den Reifegrad der Fabrik.
STAGE_WEIGHTS = {
    "markt": 10,
    "entwurf": 15,
    "bau": 20,
    "sicherung": 20,
    "freigabe": 10,
    "auslieferung": 10,
    "betrieb": 8,
    "rueckkopplung": 7,
}

#: Rollen-Muster — erstes Treffer gewinnt.
ROLE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("kern", re.compile(r"(^|_)(core|omega|foundation|kernel|platform|shared|base)($|_)",
                       re.IGNORECASE)),
    ("wissen", re.compile(r"(memory|knowledge|wiki|bible|lexikon|harmonia|gedaechtnis|"
                          r"notiz|lernen|study|akademie)", re.IGNORECASE)),
    ("infrastruktur", re.compile(r"(infra|infrastruktur|deploy|server|proxy|router|ledger|"
                                 r"runtime|ops|stack|gateway|hosting|storage)", re.IGNORECASE)),
    ("werkzeug", re.compile(r"(scripts|forge|factory|analyzer|analyse|lint|cli|bot|agent|"
                            r"runner|orchestrat|launcher|manager|guard|doctor|forge)", re.IGNORECASE)),
)

#: Belege je Stufe: **Anforderungsgruppen**. Eine Gruppe gilt als erfüllt, wenn
#: **irgendeines** ihrer Muster passt — Alternativen zählen als ein Beleg, nicht
#: als zwei. Jede Gruppe entspricht einer Anforderung, die die Stufe tragen muss.
STAGE_EVIDENCE: dict[str, tuple[tuple[str, tuple[str, ...]], ...]] = {
    "markt": (
        ("Zweckangabe", (r"(?i)(readme|docs/.*\.(md|rst))$", r"(?i)docs/SPEC\.md$")),
        ("Landing oder Marktmaterial", (r"(?i)(landing|marketing|site|www|homepage|positioning)",)),
    ),
    "entwurf": (
        ("Spezifikation", (r"(?i)docs/SPEC\.md$",)),
        ("Design", (r"(?i)docs/DESIGN\.md$",)),
        ("Architektur", (r"(?i)docs/ARCHITECTURE\.md$", r"(?i)\.aix/architecture\.md$")),
    ),
    "bau": (
        ("Quellcode", (r"(?i)(src|lib|packages|crates|apps)/",)),
    ),
    "sicherung": (
        ("Testsuite", (r"(?i)(^|/)tests?/", r"(?i)(^|/)test_[^/]+\.py$")),
        ("CI-Workflow", (r"(?i)\.github/workflows/.*\.(yml|yaml)$",)),
        ("Qualitätsnachweis", (r"(?i)\.aix/validation-contract\.json$", r"(?i)scorecard\.sh$")),
    ),
    "freigabe": (
        ("Versionierbare Definition", (r"(?i)^(Cargo\.toml|pubspec\.yaml|package\.json|pyproject\.toml)$",
                                       r"(?i)(^|/)VERSION$")),
        ("Release-Nachweis", (r"(?i)(^|/)CHANGELOG(\..*)?$", r"(?i)(^|/)VERSION$",
                              r"(?i)\.github/workflows/.*(release|publish).*\.(yml|yaml)$")),
    ),
    "auslieferung": (
        ("Container", (r"(?i)(^|/)Dockerfile$",)),
        ("Deployment-Verzeichnis", (r"(?i)(^|/)deploy/",)),
        ("Installation", (r"(?i)(^|/)scripts/.*install", r"(?i)(^|/)bin/[^/]+$")),
    ),
    "betrieb": (
        ("Startskript", (r"(?i)(^|/)run.*\.(sh|py)$",)),
        ("Betriebswerkzeug", (r"(?i)(health|monitor|logging|metrics|alert|incident|logs/)",)),
        ("Service-Definition", (r"(?i)(^|/)(systemd|launchd)/",)),
    ),
    "rueckkopplung": (
        ("Rückmeldungsquelle", (r"(?i)(feedback|analytics|telemetry|survey|auswertung|retrospekt)",)),
        ("Auswertungsdokument", (r"(?i)(^|/)docs/.*(review|retro|postmortem|auswertung)",)),
        ("Projekt-Graph", (r"(?i)\.aix/pcg\.json$",)),
    ),
}

#: Eine Stufe gilt als „voll“, wenn mindestens dieser Anteil ihrer
#: Anforderungsgruppen belegt ist.
FULL_COVERAGE_RATIO = 0.6

SOURCE_SUFFIXES = (".py", ".rs", ".dart", ".ts", ".tsx", ".js", ".go", ".swift", ".kt", ".sh")


@dataclass(frozen=True)
class Stage:
    """Eine Stufe der Wertschöpfungskette und ihre Belege.

    * **Träger** — Repos, die *alle* Anforderungen der Stufe belegen. Nur sie
      tragen die Stufe wirklich; alle anderen sind Mitwirkende.
    * **Mitwirkende** — Repos, die einen Teil der Anforderungen belegen.
    """

    key: str
    label: str
    description: str
    level: str  # "voll" | "teilweise" | "leer"
    covered_by: tuple[str, ...] = ()
    carriers: tuple[str, ...] = ()
    evidence: dict[str, str] = field(default_factory=dict)

    @property
    def score(self) -> int:
        return {"leer": 0, "teilweise": 1, "voll": 2}[self.level]


@dataclass(frozen=True)
class FactoryView:
    """Das Fabrikbild: Kette, Träger, Rollen, Lücken, Reifegrad."""

    stages: tuple[Stage, ...]
    roles: dict[str, tuple[str, ...]]
    engine: tuple[str, ...]
    output: tuple[str, ...]
    gaps: tuple[str, ...]
    readiness: int
    kettenintegritaet: int = 0
    end_to_end: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict:
        return {
            "readiness": self.readiness,
            "kettenintegritaet": self.kettenintegritaet,
            "end_to_end": list(self.end_to_end),
            "stages": [
                {
                    "key": s.key,
                    "label": s.label,
                    "level": s.level,
                    "covered_by": list(s.covered_by),
                    "carriers": list(s.carriers),
                    "evidence": dict(s.evidence),
                }
                for s in self.stages
            ],
            "roles": {role: list(repos) for role, repos in self.roles.items()},
            "engine": list(self.engine),
            "output": list(self.output),
            "gaps": list(self.gaps),
            "notes": list(self.notes),
        }


def _relative_paths(root: Path, limit: int = 4000) -> list[str]:
    """Die relativen Pfade eines Repositories — ohne Build-Verzeichnisse."""
    from .fsutil import relative_paths

    return relative_paths(root, limit=limit)


def _has_source(root: Path) -> bool:
    from .fsutil import walk_files

    return bool(walk_files(root, suffix=SOURCE_SUFFIXES, limit=1))


def _classify_role(repo: RepoReport) -> str:
    """Die Rolle eines Repositories in der Fabrik."""
    name = repo.name
    for role, pattern in ROLE_PATTERNS:
        if pattern.search(name):
            return role
    root = Path(repo.path)
    if (root / "dna" / "genome.yaml").is_file():
        return "wissen"
    if (root / "pubspec.yaml").is_file() or (root / "Cargo.toml").is_file():
        return "produkt"
    if repo.maturity and repo.maturity.score >= 60:
        return "produkt"
    return "experiment"


def _stage_evidence(repo: RepoReport, stage: str) -> dict[str, str]:
    """Welche Anforderungen der Stufe belegt dieses Repository?

    Rückgabe: Anforderungsname → der konkrete Pfad, der sie belegt.
    """
    root = Path(repo.path)
    if not root.is_dir():
        return {}
    found: dict[str, str] = {}
    paths = _relative_paths(root)
    for requirement, patterns in STAGE_EVIDENCE.get(stage, ()):
        for pattern in patterns:
            regex = re.compile(pattern)
            for relative in paths:
                if regex.search(relative):
                    found[requirement] = relative
                    break
            if requirement in found:
                break
    if stage == "bau" and not found and _has_source(root):
        found["Quellcode"] = "Quellcode"
    if stage == "markt" and not found:
        intent_text = (repo.intent.text if repo.intent else "") or ""
        if len(intent_text) > 30:
            found["Zweckangabe"] = f"Intent: „{intent_text[:60]}…“"
    return found


def build(repos: tuple[RepoReport, ...]) -> FactoryView:
    """Baut das Fabrikbild aus dem Scan-Ergebnis.

    Die zentrale Unterscheidung: **Mitwirkende** sind Repos, die *irgendetwas*
    zur Stufe beitragen — bei 260 Repos ist das fast überall der Fall und damit
    informationslos. **Träger** sind Repos, die *alle* Anforderungen der Stufe
    belegen. Erst die Träger sagen, ob eine Stufe wirklich existiert.
    """
    evidence_by_stage: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    roles: dict[str, list[str]] = defaultdict(list)

    for repo in repos:
        role = _classify_role(repo)
        roles[role].append(repo.name)
        for stage in STAGE_ORDER:
            evidence = _stage_evidence(repo, stage)
            if evidence:
                evidence_by_stage[stage][repo.name] = evidence

    stages: list[Stage] = []
    ketten_pro_repo: dict[str, set[str]] = defaultdict(set)

    for key in STAGE_ORDER:
        per_repo = evidence_by_stage.get(key, {})
        alle_anforderungen = {name for name, _ in STAGE_EVIDENCE.get(key, ())}

        traeger = tuple(
            sorted(
                name
                for name, evidence in per_repo.items()
                if alle_anforderungen.issubset(evidence)
            )
        )
        # Ein Träger belegt die Stufe vollständig — er zählt für die Kettenintegrität.
        for name in traeger:
            ketten_pro_repo[name].add(key)

        if not per_repo:
            level = "leer"
        elif traeger:
            level = "voll"
        else:
            level = "teilweise"

        evidence_text = {
            name: "; ".join(f"{anforderung} ({pfad})" for anforderung, pfad in sorted(evidence.items()))
            for name, evidence in sorted(per_repo.items())
        }
        stages.append(
            Stage(
                key=key,
                label=STAGE_LABELS[key],
                description=STAGE_DESCRIPTIONS[key],
                level=level,
                covered_by=tuple(sorted(per_repo)),
                carriers=traeger,
                evidence=evidence_text,
            )
        )

    # Rollenverteilung
    role_map: dict[str, tuple[str, ...]] = {
        role: tuple(sorted(names)) for role, names in sorted(roles.items())
    }

    # Fabrik-Motor: die Werkzeuge, die die Fabrik bauen.
    engine = tuple(sorted(set(role_map.get("werkzeug", ())) | set(role_map.get("wissen", ()))))
    # Fabrik-Output: die Produkte, die die Fabrik verlässt.
    output = tuple(sorted(role_map.get("produkt", ())))

    gaps: list[str] = []
    for stage in stages:
        if stage.level == "leer":
            gaps.append(
                f"Stufe „{stage.label}“ ist unbelegt — kein Repository liefert dafür einen Beleg."
            )
        elif stage.level == "teilweise":
            gaps.append(
                f"Stufe „{stage.label}“ hat keinen Träger — {len(stage.covered_by)} Repos "
                f"beitragen, aber keines erfüllt alle Anforderungen."
            )
    if not engine:
        gaps.append("Kein Fabrik-Motor erkennbar — kein Werkzeug, das die Fabrik selbst baut.")
    if not output:
        gaps.append("Kein Fabrik-Output erkennbar — die Fabrik erzeugt kein Produkt.")

    # Reifegrad: gewichtete Stufenabdeckung, gemessen an den **Trägern**.
    earned = 0
    maximum = 0
    for stage in stages:
        weight = STAGE_WEIGHTS[stage.key]
        maximum += weight * 2
        earned += weight * stage.score
    readiness = int(round(100 * earned / maximum)) if maximum else 0

    # Kettenintegrität: trägt ein Repository die Kette von Ende zu Ende?
    ketten_laengen = {name: len(stufen) for name, stufen in ketten_pro_repo.items()}
    beste_kette = max(ketten_laengen.values(), default=0)
    kettenintegritaet = int(round(100 * beste_kette / len(STAGE_ORDER)))
    end_to_end = tuple(
        sorted(name for name, laenge in ketten_laengen.items() if laenge >= len(STAGE_ORDER) - 2)
    )

    notes: list[str] = []
    if engine:
        notes.append(f"Fabrik-Motor: {len(engine)} Repos (Werkzeug und Wissen).")
    if output:
        notes.append(f"Fabrik-Output: {len(output)} Repos (Produkte).")
    if beste_kette:
        notes.append(
            f"Beste Einzelkette: {beste_kette}/{len(STAGE_ORDER)} Stufen in einem Repository — "
            f"die digitale Firma existiert damit als Föderation, nicht an einem Ort."
        )
    else:
        notes.append(
            "Kein Repository trägt mehr als eine Stufe vollständig — "
            "die Fabrik ist vollständig fragmentiert."
        )
    stub = [
        r.name
        for r in repos
        if r.maturity and r.maturity.score < 30 and r.commits_total > 0
    ]
    if stub:
        notes.append(
            f"{len(stub)} Repos haben Reifegrad unter 30 — sie zählen in der Kette als Zeuge, "
            f"nicht als Träger (Beispiele: {', '.join(sorted(stub)[:5])})."
        )

    return FactoryView(
        stages=tuple(stages),
        roles=role_map,
        engine=engine,
        output=output,
        gaps=tuple(gaps),
        readiness=readiness,
        kettenintegritaet=kettenintegritaet,
        end_to_end=end_to_end,
        notes=tuple(notes),
    )
