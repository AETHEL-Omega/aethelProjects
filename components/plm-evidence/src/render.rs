//! Human-readable projection; source text cannot inject terminal control sequences.
use crate::{Assessment, Snapshot};
use std::fmt::Write;

fn safe(text: &str) -> String {
    text.chars()
        .flat_map(|c| {
            if c.is_control() || matches!(c, '\u{202a}'..='\u{202e}' | '\u{2066}'..='\u{2069}') {
                c.escape_default().collect::<Vec<_>>()
            } else {
                vec![c]
            }
        })
        .collect()
}

pub fn render_text(a: &Assessment) -> String {
    let mut out = String::new();
    writeln!(
        out,
        "Referenzauswertung — keine Freigabe; Quellen nicht unabhängig verifiziert."
    )
    .unwrap();
    match &a.snapshot {
        Snapshot::Historical { captured_on } => writeln!(
            out,
            "Historische Momentaufnahme: {}; kein Live-Stand.",
            safe(captured_on)
        ),
        Snapshot::Unspecified => writeln!(out, "Quellenzeit unbekannt; Aktualität nicht geprüft."),
    }
    .unwrap();
    writeln!(
        out,
        "{} — {}\nZiel: {}\nBetrachteter Stand: {}",
        safe(&a.change.id),
        safe(&a.change.context),
        safe(&a.change.goal),
        safe(a.change.candidate.as_deref().unwrap_or("unbekannt"))
    )
    .unwrap();
    for claim in &a.claims {
        writeln!(
            out,
            "\n{}: {}\n  Benötigte Belegart: {}",
            safe(&claim.id),
            safe(&claim.statement),
            safe(&claim.required_kind)
        )
        .unwrap();
        for r in &claim.references {
            let e = &r.evidence;
            writeln!(out, "  {}: berichtet {:?}; Artvergleich: {}; Standbindung: {}; {}\n    Quelle: {} ({}); Stand: {}\n    Art: {}; Revision/Digest: {}\n    Berichtete Herkunft: {}", safe(&e.id), e.reported_result, r.kind_match, r.candidate_binding, r.assurance, safe(&e.source), safe(&e.source_id), safe(e.candidate.as_deref().unwrap_or("unbekannt")), safe(&e.kind), safe(e.revision_or_digest.as_deref().unwrap_or("unbekannt")), safe(&e.provenance)).unwrap();
            if let Some(explanation) = &e.explanation {
                writeln!(out, "    Berichtete Erklärung: {}", safe(explanation)).unwrap();
            }
        }
        for g in &claim.gaps {
            writeln!(out, "  [{}] {}", g.code, safe(&g.explanation)).unwrap();
        }
    }
    for e in &a.unreferenced_evidence {
        writeln!(
            out,
            "\nNicht zugeordnet: {} — Quelle: {} ({}); keiner Aussage zugerechnet.",
            safe(&e.id),
            safe(&e.source),
            safe(&e.source_id)
        )
        .unwrap();
    }
    out
}
