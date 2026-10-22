"""Marktview, Alleinstellungsmerkmale und Marketing-Claims (REQ-014, REQ-015).

**Der Marktview ist intern** (ADR-005): Er beschreibt die Positionierung im
AETHEL-Portfolio, nicht den Weltmarkt. Externe Wettbewerberdaten wären offline
nicht belastbar verfügbar — geraten wird nicht.

Jeder USP nennt die **messbare Beobachtung**, aus der er folgt.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass

from .models import RepoReport

SCOPE = "internal"

OVERSUPPLIED = 5
THIN = 2
LEADER_COMMITS = 500
ALONE_COMMITS = 100


@dataclass(frozen=True)
class CategoryView:
    """Die Sicht auf eine Kategorie des Portfolios."""

    name: str
    repos: int
    commits_total: int
    commits_not_on_main: int
    median_maturity: int
    crowded: bool
    thin: bool
    gap: bool


@dataclass(frozen=True)
class UniqueSellingPoint:
    """Ein Alleinstellungsmerkmal mit messbarer Begründung."""

    repo: str
    kind: str  # "Führungsrepo" | "Alleinsteller" | "Lücke" | "Reifeführer"
    claim: str
    evidence: str


@dataclass(frozen=True)
class MarketView:
    """Das Ergebnis der Markt-Analyse."""

    scope: str
    categories: tuple[CategoryView, ...]
    usps: tuple[UniqueSellingPoint, ...]
    positioning: dict[str, str]


def _maturity_of(repo: RepoReport) -> int:
    return repo.maturity.score if repo.maturity else 0


def build_categories(repos: tuple[RepoReport, ...]) -> tuple[CategoryView, ...]:
    """Verteilt die Repos auf Kategorien und bewertet deren Abdeckung."""
    buckets: dict[str, list[RepoReport]] = {}
    for repo in repos:
        buckets.setdefault(repo.category, []).append(repo)

    views: list[CategoryView] = []
    for name, group in sorted(buckets.items()):
        scores = [_maturity_of(r) for r in group]
        mature = sum(1 for r in group if _maturity_of(r) >= 50)
        views.append(
            CategoryView(
                name=name,
                repos=len(group),
                commits_total=sum(r.commits_on_main + r.commits_not_on_main for r in group),
                commits_not_on_main=sum(r.commits_not_on_main for r in group),
                median_maturity=int(statistics.median(scores)) if scores else 0,
                crowded=len(group) > OVERSUPPLIED,
                thin=0 < len(group) <= THIN,
                gap=len(group) == 1 and mature == 0 and sum(
                    r.commits_on_main + r.commits_not_on_main for r in group
                ) < ALONE_COMMITS,
            )
        )
    return tuple(views)


def build_usps(
    repos: tuple[RepoReport, ...], categories: tuple[CategoryView, ...]
) -> tuple[UniqueSellingPoint, ...]:
    """Leitet Alleinstellungsmerkmale aus messbaren Beobachtungen ab."""
    usps: list[UniqueSellingPoint] = []
    by_category: dict[str, list[RepoReport]] = {}
    for repo in repos:
        by_category.setdefault(repo.category, []).append(repo)

    for view in categories:
        group = by_category.get(view.name, [])
        if not group:
            continue
        total = [r.commits_on_main + r.commits_not_on_main for r in group]

        if view.gap:
            usps.append(
                UniqueSellingPoint(
                    repo=group[0].name,
                    kind="Lücke",
                    claim=f"Einzige Kategorie '{view.name}' ohne tragende Implementierung.",
                    evidence=f"1 Repo, {total[0]} Commits, medianer Reifegrad {view.median_maturity}",
                )
            )

        if len(group) == 1 and total[0] >= ALONE_COMMITS:
            usps.append(
                UniqueSellingPoint(
                    repo=group[0].name,
                    kind="Alleinsteller",
                    claim=f"Einziges Repository der Kategorie '{view.name}' mit {total[0]} Commits.",
                    evidence=f"{total[0]} Commits, Reifegrad {_maturity_of(group[0])}",
                )
            )

        leader = max(group, key=lambda r: (r.commits_on_main + r.commits_not_on_main))
        leader_total = leader.commits_on_main + leader.commits_not_on_main
        if leader_total >= LEADER_COMMITS and len(group) > 1:
            usps.append(
                UniqueSellingPoint(
                    repo=leader.name,
                    kind="Führungsrepo",
                    claim=(
                        f"Führungsrepo der Kategorie '{view.name}' mit {leader_total} Commits "
                        f"({len(group)} Repos in der Kategorie)."
                    ),
                    evidence=f"{leader_total} Commits, Reifegrad {_maturity_of(leader)}",
                )
            )

        mature = [r for r in group if _maturity_of(r) >= 50]
        if mature:
            best = max(mature, key=_maturity_of)
            usps.append(
                UniqueSellingPoint(
                    repo=best.name,
                    kind="Reifeführer",
                    claim=(
                        f"Höchster Reifegrad in '{view.name}' "
                        f"({_maturity_of(best)} von 100, Standard erfüllt)."
                    ),
                    evidence=f"Scorecard-Score {_maturity_of(best)}",
                )
            )

    usps.sort(key=lambda u: (u.repo.lower(), u.kind))
    return tuple(usps)


def build_positioning(
    repos: tuple[RepoReport, ...], categories: tuple[CategoryView, ...]
) -> dict[str, str]:
    """Ordnet jedes Repository innerhalb seiner Kategorie ein."""
    by_category: dict[str, list[RepoReport]] = {}
    for repo in repos:
        by_category.setdefault(repo.category, []).append(repo)

    positioning: dict[str, str] = {}
    for name, group in by_category.items():
        ranked = sorted(
            group,
            key=lambda r: (
                -_maturity_of(r),
                -(r.commits_on_main + r.commits_not_on_main),
            ),
        )
        for index, repo in enumerate(ranked, start=1):
            positioning[repo.name] = f"{index}/{len(ranked)} in '{name}'"
    return positioning


def build(repos: tuple[RepoReport, ...]) -> MarketView:
    """Baut den vollständigen Marktview."""
    categories = build_categories(repos)
    return MarketView(
        scope=SCOPE,
        categories=categories,
        usps=build_usps(repos, categories),
        positioning=build_positioning(repos, categories),
    )


def claims(repo: RepoReport) -> tuple[str, ...]:
    """Marketing-Claims je Repository — jeder Claim nennt messbare Fakten (REQ-015)."""
    found: list[str] = []

    if repo.commits_on_main >= 500:
        found.append(f"{repo.commits_on_main} Commits auf main — substanzieller Stand.")
    if repo.maturity and repo.maturity.score >= 80:
        found.append("Entspricht dem AETHEL Engineering Standard (Professional).")
    elif repo.maturity and repo.maturity.score >= 50:
        found.append(f"Reifegrad {repo.maturity.score}/100 — Kernartefakte vorhanden.")
    if repo.commits_not_on_main == 0 and repo.branches_total <= 2 and repo.commits_on_main > 0:
        found.append("Vollständig auf main integriert, keine offenen Branches.")
    if repo.maturity and repo.maturity.parts.get("tests", 0) >= 20:
        found.append("Testabdeckung mit echten Assertions vorhanden.")
    if repo.dirty_files == 0:
        found.append("Sauberer Working Tree.")
    if repo.maturity and repo.maturity.parts.get("CI", 0) > 0:
        found.append("CI-Gate vorhanden.")
    if repo.maturity and repo.maturity.parts.get("DNA", 0) > 0:
        found.append("Software-DNA hinterlegt — regenerierbar.")
    if repo.ahead_of_origin == 0 and repo.remote_url:
        found.append("Arbeitsstand vollständig auf origin.")

    return tuple(found)
