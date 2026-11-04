use std::{
    env,
    fs::File,
    io::{self, Read, Write},
    process::ExitCode,
};
const MAX_INPUT_BYTES: u64 = 8 * 1024 * 1024;
fn run() -> Result<(), (u8, String)> {
    let args: Result<Vec<_>, _> = env::args_os()
        .skip(1)
        .map(|arg| arg.into_string())
        .collect();
    let mut args = args
        .map_err(|_| (2, "arguments must be valid UTF-8".into()))?
        .into_iter();
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
    if !std::fs::metadata(&input)
        .map_err(|e| (3, format!("input I/O: {e}")))?
        .is_file()
    {
        return Err((2, "input must be a regular JSON file".into()));
    }
    let file = File::open(input).map_err(|e| (3, format!("input I/O: {e}")))?;
    if !file.metadata().map_err(|e| (3, e.to_string()))?.is_file() {
        return Err((2, "input must be a regular JSON file".into()));
    }
    let mut bytes = Vec::new();
    file.take(MAX_INPUT_BYTES + 1)
        .read_to_end(&mut bytes)
        .map_err(|e| (3, format!("input I/O: {e}")))?;
    if bytes.len() as u64 > MAX_INPUT_BYTES {
        return Err((2, "input exceeds 8 MiB limit".into()));
    }
    let case = serde_json::from_slice(&bytes)
        .map_err(|e| (2, format!("invalid JSON or case structure: {e}")))?;
    let assessment = plm_evidence::assess(case).map_err(|e| (2, e))?;
    let output = if format == "json" {
        serde_json::to_string_pretty(&assessment).map_err(|e| (2, e.to_string()))? + "\n"
    } else {
        plm_evidence::render_text(&assessment)
    };
    io::stdout()
        .lock()
        .write_all(output.as_bytes())
        .map_err(|e| (3, format!("output I/O: {e}")))?;
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
