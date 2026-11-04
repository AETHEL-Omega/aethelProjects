"""Leitstand: eine Seite, die alle Register und Läufe zusammenzieht.

Für einen Menschen sind neun Berichte und sechs JSON-Register nicht führbar. Der Leitstand
liest ausschließlich die Analysen-Ablage (``analysen/``): den Index, Vorschläge, Kreisläufe
und die jeweils jüngste JSON-Ausgabe von ``registers``, ``stack``, ``incubator`` und
``applefirst`` (abgelegt als ``analysen/<Datum>/*.json``). Er rechnet nichts neu und
schreibt nichts; er verdichtet.

Schema der JSON-Ausgabe: ``aethel.projects.cockpit/v1``.
"""

from __future__ import annotations

import html
import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import analyses as analyses_mod

SCHEMA = "aethel.projects.cockpit/v1"

# Welche Lauf-Ausgabe unter welchem Schema erwartet wird; der jüngste Treffer gewinnt.
RUN_SCHEMAS = {
    "registers": "aethel.projects.register-drift/v1",
    "stack": "aethel.projects.stack/v1",
    "incubator": "aethel.projects.incubator/v1",
    "applefirst": "aethel.projects.applefirst/v1",
}


@dataclass(frozen=True)
class Kachel:
    """Eine Kennzahl mit Herkunft."""

    titel: str
    wert: str
    quelle: str
    hinweis: str = ""

    def as_dict(self) -> dict[str, str]:
        return {"titel": self.titel, "wert": self.wert, "quelle": self.quelle, "hinweis": self.hinweis}


@dataclass(frozen=True)
class Leitstand:
    """Verdichtete Sicht über Ablage, Register und Läufe."""

    kacheln: tuple[Kachel, ...]
    kreise: dict[str, int]
    kreise_offen: tuple[str, ...]
    vorschlaege: dict[str, int]
    dominosteine: tuple[str, ...]
    inkubator: dict[str, int]
    applefirst: dict[str, int]
    applefirst_schlechteste: tuple[str, ...]
    register_drift: dict[str, int]
    leere_schichten: tuple[str, ...]
    analysen: tuple[str, ...]
    fehlt: tuple[str, ...]
    quellen: dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "kacheln": [k.as_dict() for k in self.kacheln],
            "kreise": dict(self.kreise),
            "kreise_offen": list(self.kreise_offen),
            "vorschlaege": dict(self.vorschlaege),
            "dominosteine": list(self.dominosteine),
            "inkubator": dict(self.inkubator),
            "applefirst": dict(self.applefirst),
            "applefirst_schlechteste": list(self.applefirst_schlechteste),
            "register_drift": dict(self.register_drift),
            "leere_schichten": list(self.leere_schichten),
            "analysen": list(self.analysen),
            "fehlt": list(self.fehlt),
            "quellen": dict(self.quellen),
        }


def _latest_run(base: Path, schema: str) -> tuple[dict | None, str]:
    """Jüngste JSON-Datei unter ``base`` mit passendem Schema (Pfad sortiert, letzter gewinnt)."""
    import re

    best: tuple[str, dict] | None = None
    best_key: tuple[str, float, str] | None = None
    date_dir = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    # Nur Läufe in <YYYY-MM-DD>/ zählen; jüngstes Datum gewinnt, am selben Tag die jüngste Datei.
    for path in base.glob("*/*.json"):
        if not date_dir.match(path.parent.name):
            continue
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(payload, dict) and payload.get("schema") == schema:
            key = (path.parent.name, mtime, path.name)
            if best_key is None or key > best_key:
                best_key, best = key, (str(path.relative_to(base)), payload)
    if best is None:
        return None, ""
    return best[1], best[0]


def _items(payload: dict | None) -> list[dict]:
    """Liste der Einträge einer Lauf-Ausgabe, unabhängig vom Schlüsselnamen."""
    if not payload:
        return []
    for key in ("items", "assignments", "readiness", "audits", "repos"):
        value = payload.get(key)
        if isinstance(value, list):
            return [v for v in value if isinstance(v, dict)]
    for value in payload.values():
        if isinstance(value, list) and value and isinstance(value[0], dict):
            return value
    return []


def build(base: Path | None = None) -> Leitstand:
    """Liest die Ablage und verdichtet sie zu einer Sicht."""
    root = base if base is not None else analyses_mod.default_base()
    entries = analyses_mod.list_entries(root)
    proposals = analyses_mod.load_proposals(root)
    loops = analyses_mod.load_loops(root)
    quellen: dict[str, str] = {}

    kreise = Counter(loop.status for loop in loops)
    kreise_offen = tuple(f"{loop.id} ({loop.ebene}): fehlt {'; '.join(loop.fehlt) or '–'}" for loop in loops if loop.status == "offen")
    vorschlaege = Counter(proposal.status for proposal in proposals)
    hebel = sorted(proposals, key=lambda p: (-len(p.hebt), p.id))
    dominosteine = tuple(f"{p.id} {p.name}: hebt {len(p.hebt)}" for p in hebel[:5])

    drift_payload, drift_src = _latest_run(root, RUN_SCHEMAS["registers"])
    register_drift: dict[str, int] = {}
    if drift_payload:
        quellen["registers"] = drift_src
        for key in ("missing_in_manifest", "dead_manifest_entries", "unregistered_worktrees",
                    "profiles_without_manifest", "profiles_without_repo", "auftraege_unknown_repos"):
            value = drift_payload.get(key)
            if isinstance(value, list):
                register_drift[key] = len(value)
        age = drift_payload.get("manifest_age_days")
        if isinstance(age, int):
            register_drift["manifest_age_days"] = age

    stack_payload, stack_src = _latest_run(root, RUN_SCHEMAS["stack"])
    leere: tuple[str, ...] = ()
    if stack_payload:
        quellen["stack"] = stack_src
        names = stack_payload.get("layer_names") or {}
        leere = tuple(f"{code} {names.get(code, '')}".strip() for code in stack_payload.get("empty_layers") or [])

    inc_payload, inc_src = _latest_run(root, RUN_SCHEMAS["incubator"])
    inkubator: dict[str, int] = {}
    if inc_payload:
        quellen["incubator"] = inc_src
        inkubator = dict(sorted(Counter(str(item.get("stufe", "?")) for item in _items(inc_payload)).items()))

    af_payload, af_src = _latest_run(root, RUN_SCHEMAS["applefirst"])
    applefirst: dict[str, int] = {}
    schlechteste: tuple[str, ...] = ()
    if af_payload:
        quellen["applefirst"] = af_src
        items = _items(af_payload)
        applefirst = dict(sorted(Counter(str(item.get("grade", "?")) for item in items).items()))
        scored = [i for i in items if isinstance(i.get("score"), int)]
        scored.sort(key=lambda i: (i["score"], str(i.get("repo"))))
        schlechteste = tuple(
            f"{i.get('repo')}: {i['score']} ({i.get('grade')}, Python {round(100 * float(i.get('python_anteil') or 0))} %)"
            for i in scored[:10]
        )

    fehlt: list[str] = []
    if not drift_payload:
        fehlt.append("Kein Register-Abgleich abgelegt: `registers --snapshot … --format json --out analysen/<Datum>/register-abgleich.json`")
    if not stack_payload:
        fehlt.append("Keine Schichtenkarte abgelegt: `stack --format json --out analysen/<Datum>/schichtenkarte.json`")
    if not inc_payload:
        fehlt.append("Kein Inkubator-Lauf abgelegt: `incubator --format json --out analysen/<Datum>/inkubator.json`")
    if not af_payload:
        fehlt.append("Kein Apple-first-Audit abgelegt: `applefirst --format json --out analysen/<Datum>/applefirst.json`")
    if kreise.get("geschlossen", 0) == 0 and loops:
        fehlt.append("Kein Kreislauf ist geschlossen: Loop-Registry im Kern (aixd) fehlt")
    if register_drift.get("manifest_age_days", 0) > 30:
        fehlt.append(f"Manifest ist {register_drift['manifest_age_days']} Tage alt: Registry mit Produkt-ID fehlt")
    if leere:
        fehlt.append(f"{len(leere)} Stack-Schichten ohne eigenes Repo")
    if not any(p.status == "existiert" for p in proposals) and proposals:
        fehlt.append("Keiner der Vorschläge ist als existierende Komponente markiert")

    kacheln = (
        Kachel("Analysen", str(len(entries)), "analysen/INDEX.json"),
        Kachel("Vorschläge", str(len(proposals)), "analysen/vorschlaege.json",
               ", ".join(f"{k} {v}" for k, v in sorted(vorschlaege.items()))),
        Kachel("Kreisläufe", str(len(loops)), "analysen/kreislaeufe.json",
               ", ".join(f"{k} {v}" for k, v in sorted(kreise.items()))),
        Kachel("Register-Drift", str(sum(v for k, v in register_drift.items() if k != "manifest_age_days")) if register_drift else "–",
               quellen.get("registers", "kein Lauf"), "Summe der Abweichungen"),
        Kachel("Leere Schichten", str(len(leere)) if stack_payload else "–", quellen.get("stack", "kein Lauf")),
        Kachel("Inkubator", f"{sum(inkubator.values())} Repos" if inkubator else "–", quellen.get("incubator", "kein Lauf"),
               ", ".join(f"{k}: {v}" for k, v in inkubator.items())),
        Kachel("Apple-first", f"{sum(applefirst.values())} Repos" if applefirst else "–", quellen.get("applefirst", "kein Lauf"),
               ", ".join(f"{k}: {v}" for k, v in applefirst.items())),
    )
    return Leitstand(
        kacheln=kacheln,
        kreise=dict(kreise),
        kreise_offen=kreise_offen,
        vorschlaege=dict(vorschlaege),
        dominosteine=dominosteine,
        inkubator=inkubator,
        applefirst=applefirst,
        applefirst_schlechteste=schlechteste,
        register_drift=register_drift,
        leere_schichten=leere,
        analysen=tuple(f"{e.date} {e.id}: {e.title}" for e in entries),
        fehlt=tuple(fehlt),
        quellen=quellen,
    )


def render_markdown(view: Leitstand) -> str:
    lines = ["# Leitstand", "", "Eine Seite für alles: Ablage, Vorschläge, Kreisläufe, Register, Schichten, Inkubator, Apple-first.", ""]
    lines += ["| Kennzahl | Wert | Quelle | Hinweis |", "|---|---:|---|---|"]
    for k in view.kacheln:
        lines.append(f"| {k.titel} | {k.wert} | `{k.quelle}` | {k.hinweis or '-'} |")
    lines += ["", "## Was fehlt (aus den Daten abgeleitet)", ""]
    lines += [f"- {f}" for f in view.fehlt] or ["- nichts Offenes aus den vorliegenden Läufen"]
    lines += ["", "## Dominosteine (Vorschläge mit größtem Hebel)", ""]
    lines += [f"- {d}" for d in view.dominosteine] or ["- keine Vorschläge"]
    lines += ["", f"## Offene Kreisläufe ({len(view.kreise_offen)})", ""]
    lines += [f"- {k}" for k in view.kreise_offen] or ["- keine"]
    if view.register_drift:
        lines += ["", "## Register-Drift", "", "| Kategorie | Anzahl |", "|---|---:|"]
        lines += [f"| {k} | {v} |" for k, v in view.register_drift.items()]
    if view.leere_schichten:
        lines += ["", "## Leere Stack-Schichten", ""] + [f"- {s}" for s in view.leere_schichten]
    if view.inkubator:
        lines += ["", "## Inkubator-Verteilung", "", "| Stufe | Repos |", "|---|---:|"]
        lines += [f"| {k} | {v} |" for k, v in view.inkubator.items()]
    if view.applefirst:
        lines += ["", "## Apple-first", "", "| Grade | Repos |", "|---|---:|"]
        lines += [f"| {k} | {v} |" for k, v in view.applefirst.items()]
        lines += ["", "Schlechteste zehn:", ""] + [f"- {s}" for s in view.applefirst_schlechteste]
    lines += ["", "## Analysen in der Ablage", ""] + [f"- {a}" for a in view.analysen]
    return "\n".join(lines) + "\n"


def render_json(view: Leitstand) -> str:
    return json.dumps(view.as_dict(), ensure_ascii=False, indent=2, sort_keys=True)


def render_html(view: Leitstand, *, standalone: bool = True) -> str:
    """HTML-Seite ohne externe Abhängigkeiten (Ausgabe, keine Hauptoberfläche).

    ``standalone=False`` liefert nur ``<title>``, ``<style>`` und Inhalt, für Umgebungen,
    die das Dokumentgerüst selbst stellen.
    """

    def esc(text: object) -> str:
        return html.escape(str(text))

    def ul(items: tuple[str, ...], leer: str) -> str:
        return "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>" if items else f"<p>{esc(leer)}</p>"

    def table(rows: dict[str, int], kopf: tuple[str, str]) -> str:
        body = "".join(f"<tr><td>{esc(k)}</td><td class='n'>{v}</td></tr>" for k, v in rows.items())
        return f"<div class='tbl'><table><thead><tr><th>{kopf[0]}</th><th>{kopf[1]}</th></tr></thead><tbody>{body}</tbody></table></div>"

    kacheln = "".join(
        f"<div class='k'><div class='t'>{esc(k.titel)}</div><div class='w'>{esc(k.wert)}</div>"
        f"<div class='q'>{esc(k.quelle)}</div><div class='h'>{esc(k.hinweis)}</div></div>"
        for k in view.kacheln
    )
    head = (
        "<!doctype html><html lang='de'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1, viewport-fit=cover'>"
        if standalone else ""
    )
    parts = [
        head,
        "<title>AETHEL Leitstand</title>",
        "<meta name='claude:viewport-fit-sides' content='cover'>" if not standalone else "",
        "<style>",
        # Farbtoken: hell auf :root, dunkel über System-Einstellung und über explizite Wahl.
        ":root{--bg:#f7f7f4;--fg:#1c1c1e;--mute:#6b6b70;--line:#dcdcd6;--acc:#1f5fbf;--warn:#a93226;--tile:#ffffff}",
        "@media (prefers-color-scheme: dark){:root:not([data-theme='light']){--bg:#15161a;--fg:#ececf0;--mute:#9b9ba3;--line:#2d2e34;--acc:#7fb0ff;--warn:#ff7b6e;--tile:#1d1e24;color-scheme:dark}}",
        ":root[data-theme='dark']{--bg:#15161a;--fg:#ececf0;--mute:#9b9ba3;--line:#2d2e34;--acc:#7fb0ff;--warn:#ff7b6e;--tile:#1d1e24;color-scheme:dark}",
        "body{margin:0;padding-block:20px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));"
        "background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,system-ui,'Helvetica Neue',sans-serif}",
        ".wrap{max-width:1100px;margin-inline:auto;min-width:0}",
        "h1{font-size:24px;margin:0 0 4px;text-wrap:balance}h2{font-size:17px;margin:28px 0 8px;border-bottom:1px solid var(--line);padding-bottom:4px}",
        ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-top:14px}",
        ".k{border:1px solid var(--line);background:var(--tile);border-radius:10px;padding:10px;min-width:0}.t{color:var(--mute);font-size:12px;letter-spacing:.02em;text-transform:uppercase}.w{font-size:24px;font-weight:600;font-variant-numeric:tabular-nums}",
        ".q{font-size:11px;color:var(--mute);word-break:break-all}.h{font-size:12px;margin-top:4px}",
        ".tbl{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border-bottom:1px solid var(--line);padding:4px 6px;text-align:left}td.n{text-align:right;font-variant-numeric:tabular-nums}",
        ".fehlt li{color:var(--warn)}ul{padding-left:18px}p.lead{color:var(--mute);margin:0}",
        "</style>",
        "</head><body>" if standalone else "",
        "<div class='wrap'>",
        "<h1>AETHEL Leitstand</h1><p class='lead'>Eine Seite für alles: Ablage, Vorschläge, Kreisläufe, Register, Schichten, Inkubator, Apple-first. Erzeugt aus <code>aethelProjects/analysen/</code>.</p>",
        f"<div class='grid'>{kacheln}</div>",
        "<h2>Was fehlt (aus den Daten abgeleitet)</h2><div class='fehlt'>", ul(view.fehlt, "nichts Offenes aus den vorliegenden Läufen"), "</div>",
        "<h2>Dominosteine: Vorschläge mit größtem Hebel</h2>", ul(view.dominosteine, "keine Vorschläge"),
        f"<h2>Offene Kreisläufe ({len(view.kreise_offen)})</h2>", ul(view.kreise_offen, "keine"),
    ]
    if view.register_drift:
        parts += ["<h2>Register-Drift</h2>", table(view.register_drift, ("Kategorie", "Anzahl"))]
    if view.leere_schichten:
        parts += ["<h2>Leere Stack-Schichten</h2>", ul(view.leere_schichten, "keine")]
    if view.inkubator:
        parts += ["<h2>Inkubator-Verteilung</h2>", table(view.inkubator, ("Stufe", "Repos"))]
    if view.applefirst:
        parts += ["<h2>Apple-first</h2>", table(view.applefirst, ("Grade", "Repos")), "<p>Schlechteste zehn:</p>", ul(view.applefirst_schlechteste, "keine")]
    parts += ["<h2>Analysen in der Ablage</h2>", ul(view.analysen, "keine"), "</div>"]
    parts.append("</body></html>" if standalone else "")
    return "".join(parts)
