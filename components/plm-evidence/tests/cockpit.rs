use plm_evidence::cockpit::{project, Input};
use serde_json::json;

#[test]
fn preserves_source_and_missing_without_claiming_freshness() {
    let input: Input = serde_json::from_value(json!({"schema":"aethel.projects.cockpit/v1", "kacheln":[{"titel":"Register", "wert":"3", "quelle":"scan.json"}], "fehlt":["Owner unklar"], "quellen":{"registers":"scan.json"}})).unwrap();
    let view = project(input, "explicit export").unwrap();
    assert_eq!(view.tiles[0].quelle, "scan.json");
    assert_eq!(view.missing, vec!["Owner unklar"]);
    assert_eq!(view.source_time, None);
    assert_eq!(view.freshness, "not_checked");
    assert!(view.authority.contains("not_verified"));
}

#[test]
fn rejects_unknown_schema_and_unattributed_tiles() {
    for (schema, source) in [("future", "scan"), ("aethel.projects.cockpit/v1", "")] {
        let input: Input = serde_json::from_value(json!({"schema":schema, "kacheln":[{"titel":"x","wert":"0","quelle":source}], "fehlt":[], "quellen":{}})).unwrap();
        assert!(project(input, "export").is_err());
    }
}
