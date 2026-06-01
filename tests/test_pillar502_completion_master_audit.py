from src.core.pillar502_completion_master_audit import (
    completion_master_audit,
    extract_post_number,
    latest_monograph_major_version,
    next_substack_slot,
)


def test_extract_post_number_parses_valid_name():
    assert extract_post_number("post-250-s03e028.md") == 250


def test_extract_post_number_returns_none_for_invalid():
    assert extract_post_number("notes.md") is None


def test_next_substack_slot_matches_repository_state():
    slot = next_substack_slot(".")
    assert isinstance(slot, int)
    assert slot >= 1


def test_latest_monograph_major_version_detected():
    version = latest_monograph_major_version(".")
    assert version is None or version >= 1


def test_completion_master_audit_shape_and_flags():
    report = completion_master_audit(".")

    assert report["pillar"] == 502
    assert report["title"] == "COMPLETION_MASTER_AUDIT"
    assert 0.0 <= report["completion_fraction_executable"] <= 1.0
    assert isinstance(report["tasks"], list)
    assert len(report["tasks"]) >= 6
    assert "blockers_executable" in report
    assert "external_unknowns" in report

    task_keys = {task["key"] for task in report["tasks"]}
    assert "arxiv_submitted" in task_keys
    assert "zenodo_doi_minted" in task_keys

    external = {task["key"]: task["status"] for task in report["tasks"] if task["category"] == "EXTERNAL"}
    assert external["arxiv_submitted"] == "EXTERNAL_UNVERIFIED"
    assert external["zenodo_doi_minted"] == "EXTERNAL_UNVERIFIED"

