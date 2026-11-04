use std::{env, fs, process::ExitCode};
fn run() -> Result<(), (u8, String)> {
    let mut args = env::args().skip(1);
    if args.next().as_deref() != Some("assess") {
        return Err((
            2,
            "usage: plm-evidence assess --input FILE --format json|text".into(),
        ));
    }
    let (mut input, mut format) = (None, None);
    while let Some(arg) = args.next() {
        let value = args.next().ok_or((2, format!("missing value for {arg}")))?;
        match arg.as_str() {
            "--input" if input.is_none() => input = Some(value),
            "--format" if format.is_none() => format = Some(value),
            _ => return Err((2, format!("unknown or duplicate option: {arg}"))),
        }
    }
    let input = input.ok_or((2, "missing --input".into()))?;
    let format = format.ok_or((2, "missing --format".into()))?;
    if format != "json" && format != "text" {
        return Err((2, "invalid format".into()));
    }
    let bytes = fs::read(input).map_err(|e| (3, format!("input I/O: {e}")))?;
    let case = serde_json::from_slice(&bytes)
        .map_err(|e| (2, format!("invalid JSON or case structure: {e}")))?;
    let assessment = plm_evidence::assess(case).map_err(|e| (2, e))?;
    if format == "json" {
        println!(
            "{}",
            serde_json::to_string_pretty(&assessment).map_err(|e| (2, e.to_string()))?
        );
    } else {
        println!(
            "{} — {}\n{}",
            assessment.change.id, assessment.change.context, assessment.change.goal
        );
        for claim in assessment.claims {
            println!("\n{}: {}", claim.id, claim.statement);
            for r in claim.references {
                println!(
                    "  {}: {:?}; Art: {}; Standbindung: {}; {}\n    Quelle: {} ({}); Stand: {}; Herkunft: {}",
                    r.evidence.id, r.evidence.reported_result, r.kind_match, r.candidate_binding, r.assurance,
                    r.evidence.source, r.evidence.source_id, r.evidence.candidate.as_deref().unwrap_or("unbekannt"), r.evidence.provenance
                );
                if let Some(explanation) = &r.evidence.explanation {
                    println!("    Berichtete Erklärung: {explanation}");
                }
            }
            for g in claim.gaps {
                println!("  [{}] {}", g.code, g.explanation);
            }
        }
    }
    Ok(())
}
fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err((code, message)) => {
            eprintln!("{message}");
            ExitCode::from(code)
        }
    }
}
