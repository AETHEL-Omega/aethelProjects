//! Narrow projection of an explicitly supplied aethelProjects cockpit snapshot.
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

#[derive(Debug, Deserialize, Serialize)]
pub struct Tile {
    pub titel: String,
    pub wert: String,
    pub quelle: String,
    #[serde(default)]
    pub hinweis: String,
}

#[derive(Debug, Deserialize)]
pub struct Input {
    pub schema: String,
    pub kacheln: Vec<Tile>,
    pub fehlt: Vec<String>,
    pub quellen: BTreeMap<String, String>,
}

#[derive(Debug, Serialize)]
pub struct Observation {
    pub schema: &'static str,
    pub source_schema: &'static str,
    pub source_id: String,
    pub source_time: Option<String>,
    pub freshness: &'static str,
    pub authority: &'static str,
    pub tiles: Vec<Tile>,
    pub missing: Vec<String>,
    pub sources: BTreeMap<String, String>,
}

pub fn project(input: Input, source_id: &str) -> Result<Observation, String> {
    if input.schema != "aethel.projects.cockpit/v1" || source_id.trim().is_empty() {
        return Err("unsupported cockpit schema or empty source".into());
    }
    if input
        .kacheln
        .iter()
        .any(|t| t.titel.trim().is_empty() || t.quelle.trim().is_empty())
    {
        return Err("cockpit tile needs title and source".into());
    }
    Ok(Observation {
        schema: "aethel.plm.cockpit-observation/v1",
        source_schema: "aethel.projects.cockpit/v1",
        source_id: source_id.into(),
        source_time: None,
        freshness: "not_checked",
        authority: "source_assertions_only; source_and_authority_not_verified",
        tiles: input.kacheln,
        missing: input.fehlt,
        sources: input.quellen,
    })
}
