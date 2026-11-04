use std::{
    env,
    fs::File,
    io::{self, Read, Write},
    process::ExitCode,
};
const MAX_INPUT_BYTES: u64 = 8 * 1024 * 1024;
fn read_input(input: &str) -> Result<Vec<u8>, (u8, String)> {
    if !std::fs::metadata(input)
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
    Ok(bytes)
}
fn run() -> Result<(), (u8, String)> {
    let args: Result<Vec<_>, _> = env::args_os()
        .skip(1)
        .map(|arg| arg.into_string())
        .collect();
    let mut args = args
        .map_err(|_| (2, "arguments must be valid UTF-8".into()))?
        .into_iter();
    let command = args.next().unwrap_or_default();
    if command != "assess"
        && command != "assess-quality"
        && command != "assess-linked"
        && command != "project-observation"
        && command != "copilot-observation"
        && command != "landscape-project"
        && command != "landing-observation"
        && command != "cockpit-observation"
    {
        return Err((
            2,
            "usage: plm-evidence assess|assess-quality|assess-linked|project-observation|copilot-observation|landscape-project|landing-observation|cockpit-observation --input FILE --format json|text".into(),
        ));
    }
    let (mut input, mut format, mut repository, mut source, mut evidence, mut goal) =
        (None, None, None, None, None, None);
    let (mut binding, mut case) = (None, None);
    let (mut head, mut observed_at, mut supplement) = (None, None, None);
    while let Some(arg) = args.next() {
        let value = args.next().ok_or((2, format!("missing value for {arg}")))?;
        match arg.as_str() {
            "--input" if input.is_none() => input = Some(value),
            "--format" if format.is_none() => format = Some(value),
            "--repository-id"
                if matches!(
                    command.as_str(),
                    "project-observation" | "landing-observation"
                ) && repository.is_none() =>
            {
                repository = Some(value)
            }
            "--source-id"
                if matches!(
                    command.as_str(),
                    "project-observation"
                        | "copilot-observation"
                        | "landscape-project"
                        | "cockpit-observation"
                        | "landing-observation"
                ) && source.is_none() =>
            {
                source = Some(value)
            }
            "--evidence-id"
                if matches!(
                    command.as_str(),
                    "project-observation" | "copilot-observation"
                ) && evidence.is_none() =>
            {
                evidence = Some(value)
            }
            "--goal-id" if command == "copilot-observation" && goal.is_none() => goal = Some(value),
            "--binding" if command == "landscape-project" && binding.is_none() => {
                binding = Some(value)
            }
            "--case" if command == "landscape-project" && case.is_none() => case = Some(value),
            "--head" if command == "landing-observation" && head.is_none() => head = Some(value),
            "--observed-at" if command == "landing-observation" && observed_at.is_none() => {
                observed_at = Some(value)
            }
            "--supplement" if command == "landscape-project" && supplement.is_none() => {
                supplement = Some(value)
            }
            _ => return Err((2, format!("unknown or duplicate option: {arg}"))),
        }
    }
    let input = input.ok_or((2, "missing --input".into()))?;
    let format = format.ok_or((2, "missing --format".into()))?;
    if format != "json" && format != "text" {
        return Err((2, "invalid format".into()));
    }
    let bytes = read_input(&input)?;
    let output = if command == "cockpit-observation" {
        if format != "json" {
            return Err((2, "cockpit-observation requires --format json".into()));
        }
        let source = source.ok_or((2, "missing --source-id".into()))?;
        let input =
            serde_json::from_slice(&bytes).map_err(|e| (2, format!("invalid cockpit: {e}")))?;
        let result = plm_evidence::cockpit::project(input, &source).map_err(|e| (2, e))?;
        serde_json::to_string_pretty(&result).map_err(|e| (2, e.to_string()))? + "\n"
    } else if command == "landing-observation" {
        if format != "json" {
            return Err((2, "landing-observation requires --format json".into()));
        }
        let repo = repository.ok_or((2, "missing --repository-id".into()))?;
        let head = head.ok_or((2, "missing --head".into()))?;
        let source = source.ok_or((2, "missing --source-id".into()))?;
        let time = observed_at.ok_or((2, "missing --observed-at".into()))?;
        let report = serde_json::from_slice(&bytes)
            .map_err(|e| (2, format!("invalid Landing report: {e}")))?;
        let result = plm_evidence::landing::observe(report, &repo, &head, &source, &time)
            .map_err(|e| (2, e))?;
        serde_json::to_string_pretty(&result).map_err(|e| (2, e.to_string()))? + "\n"
    } else if command == "landscape-project" {
        if format != "json" {
            return Err((2, "landscape-project requires --format json".into()));
        }
        let source = source.ok_or((2, "missing --source-id".into()))?;
        let observation = serde_json::from_slice(&bytes)
            .map_err(|e| (2, format!("invalid landscape observation: {e}")))?;
        let attachment = match (binding, case) {
            (None, None) => None,
            (Some(b), Some(c)) => {
                let binding = serde_json::from_slice(&read_input(&b)?)
                    .map_err(|e| (2, format!("invalid case binding: {e}")))?;
                let case = serde_json::from_slice(&read_input(&c)?)
                    .map_err(|e| (2, format!("invalid case: {e}")))?;
                Some((binding, case))
            }
            _ => return Err((2, "--binding and --case must be supplied together".into())),
        };
        let mut result = plm_evidence::landscape::project(observation, &source, attachment)
            .map_err(|e| (2, e))?;
        if let Some(path) = supplement {
            let extra = serde_json::from_slice(&read_input(&path)?)
                .map_err(|e| (2, format!("invalid landscape supplement: {e}")))?;
            plm_evidence::landscape::supplement(&mut result, extra).map_err(|e| (2, e))?;
        }
        serde_json::to_string_pretty(&result).map_err(|e| (2, e.to_string()))? + "\n"
    } else if command == "copilot-observation" {
        if format != "json" {
            return Err((2, "copilot-observation requires --format json".into()));
        }
        let goal = goal.ok_or((2, "missing --goal-id".into()))?;
        let source = source.ok_or((2, "missing --source-id".into()))?;
        let evidence = evidence.ok_or((2, "missing --evidence-id".into()))?;
        let input = serde_json::from_slice(&bytes)
            .map_err(|e| (2, format!("invalid Copilot goal: {e}")))?;
        let result = plm_evidence::copilot::goal_observation(input, &goal, &source, &evidence)
            .map_err(|e| (2, e))?;
        serde_json::to_string_pretty(&result).map_err(|e| (2, e.to_string()))? + "\n"
    } else if command == "project-observation" {
        if format != "json" {
            return Err((2, "project-observation requires --format json".into()));
        }
        let repo = repository.ok_or((2, "missing --repository-id".into()))?;
        let source = source.ok_or((2, "missing --source-id".into()))?;
        let evidence = evidence.ok_or((2, "missing --evidence-id".into()))?;
        let input = serde_json::from_slice(&bytes)
            .map_err(|e| (2, format!("invalid project export: {e}")))?;
        let result = plm_evidence::projects::project_export(input, &repo, &source, &evidence)
            .map_err(|e| (2, e))?;
        serde_json::to_string_pretty(&result).map_err(|e| (2, e.to_string()))? + "\n"
    } else if command == "assess-linked" {
        let input =
            serde_json::from_slice(&bytes).map_err(|e| (2, format!("invalid linked JSON: {e}")))?;
        let assessment = plm_evidence::link::assess_linked(input).map_err(|e| (2, e))?;
        if format == "json" {
            serde_json::to_string_pretty(&assessment).map_err(|e| (2, e.to_string()))? + "\n"
        } else {
            plm_evidence::link::render_linked_text(&assessment)
        }
    } else if command == "assess-quality" {
        let case = serde_json::from_slice(&bytes)
            .map_err(|e| (2, format!("invalid quality JSON: {e}")))?;
        let assessment = plm_evidence::quality::assess_quality(case).map_err(|e| (2, e))?;
        if format == "json" {
            serde_json::to_string_pretty(&assessment).map_err(|e| (2, e.to_string()))? + "\n"
        } else {
            plm_evidence::quality::render_quality_text(&assessment)
        }
    } else {
        let case = serde_json::from_slice(&bytes)
            .map_err(|e| (2, format!("invalid JSON or case structure: {e}")))?;
        let assessment = plm_evidence::assess(case).map_err(|e| (2, e))?;
        if format == "json" {
            serde_json::to_string_pretty(&assessment).map_err(|e| (2, e.to_string()))? + "\n"
        } else {
            plm_evidence::render_text(&assessment)
        }
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
