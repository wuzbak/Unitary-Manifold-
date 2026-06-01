from src.core.um_sos_registry import export_registry


def test_registry_contains_expected_pillars():
    payload = export_registry()
    pillars = {entry["pillar"] for entry in payload["entries"]}
    assert {435, 437, 442, 467, 468, 469, 475, 486}.issubset(pillars)
    assert payload["entry_count"] == len(payload["entries"])


def test_registry_has_admissions():
    payload = export_registry()
    assert payload["admissions"]
    assert any("Admission 1" in record["name"] for record in payload["admissions"])
