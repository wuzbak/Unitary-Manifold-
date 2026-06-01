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


def test_next_substack_slot_uses_max_plus_one(tmp_path):
    posts_dir = tmp_path / "7-OUTREACH" / "substack" / "posts"
    posts_dir.mkdir(parents=True)
    (posts_dir / "post-005-a.md").write_text("", encoding="utf-8")
    (posts_dir / "post-010-b.md").write_text("", encoding="utf-8")
    (posts_dir / "notes.md").write_text("", encoding="utf-8")

    assert next_substack_slot(tmp_path) == 11


def test_latest_monograph_major_version_detected_from_filenames(tmp_path):
    mono_dir = tmp_path / "6-MONOGRAPH"
    mono_dir.mkdir(parents=True)
    (mono_dir / "THEBOOKV9a.pdf").write_text("", encoding="utf-8")
    (mono_dir / "UM_v15_release_notes.md").write_text("", encoding="utf-8")

    assert latest_monograph_major_version(tmp_path) == 15


def test_completion_master_audit_shape_and_flags(tmp_path):
    (tmp_path / "src" / "core").mkdir(parents=True)
    (tmp_path / "src" / "core" / "pillar285_dark_energy_extension_specification.py").write_text("", encoding="utf-8")
    (tmp_path / "src" / "core" / "pillar486_desi_dr3_final_prep.py").write_text("", encoding="utf-8")
    (tmp_path / "src" / "core" / "boltzmann_bridge.py").write_text("", encoding="utf-8")
    (tmp_path / "7-OUTREACH" / "substack" / "posts").mkdir(parents=True)
    (tmp_path / "7-OUTREACH" / "substack" / "posts" / "post-100-x.md").write_text("", encoding="utf-8")
    (tmp_path / "6-MONOGRAPH").mkdir(parents=True)
    (tmp_path / "6-MONOGRAPH" / "THEBOOKV9a.pdf").write_text("", encoding="utf-8")

    report = completion_master_audit(tmp_path)

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

    status_by_key = {task["key"]: task["status"] for task in report["tasks"]}
    category_by_key = {task["key"]: task["category"] for task in report["tasks"]}
    blocker_keys = {key for key, _ in report["blockers_executable"]}
    for key, status in status_by_key.items():
        if category_by_key[key] != "EXECUTABLE":
            continue
        if status != "DONE":
            assert key in blocker_keys

    external_unknown_keys = {key for key, _ in report["external_unknowns"]}
    assert "arxiv_submitted" in external_unknown_keys
    assert "zenodo_doi_minted" in external_unknown_keys

    actions = report["immediate_actions"]
    assert any("Lean4 Tier-2" in action for action in actions)
    assert any("arXiv" in action for action in actions)


def test_completion_master_audit_marks_lean4_done_when_valid_certificate(tmp_path):
    cert = tmp_path / "lean4" / "TIER2_COMPILATION_CERTIFICATE.json"
    cert.parent.mkdir(parents=True)
    cert.write_text('{"status":"COMPILED","tier2_compile_passed":true}', encoding="utf-8")

    report = completion_master_audit(tmp_path)
    task_map = {task["key"]: task for task in report["tasks"]}
    assert task_map["lean4_tier2_compile"]["status"] == "DONE"


def test_completion_master_audit_marks_lean4_done_when_status_contains_compiled(tmp_path):
    cert = tmp_path / "lean4" / "tier2_compilation_certificate.json"
    cert.parent.mkdir(parents=True)
    cert.write_text('{"status":"compiled in ci"}', encoding="utf-8")

    report = completion_master_audit(tmp_path)
    task_map = {task["key"]: task for task in report["tasks"]}
    assert task_map["lean4_tier2_compile"]["status"] == "DONE"


def test_completion_master_audit_accepts_status_normalization_variants(tmp_path):
    cert = tmp_path / "lean4" / "tier2_compilation_certificate.json"
    cert.parent.mkdir(parents=True)
    cert.write_text('{"status":"Compiled-In-CI"}', encoding="utf-8")

    report = completion_master_audit(tmp_path)
    task_map = {task["key"]: task for task in report["tasks"]}
    assert task_map["lean4_tier2_compile"]["status"] == "DONE"


def test_completion_master_audit_marks_lean4_done_from_markdown_certificate(tmp_path):
    cert = tmp_path / "docs" / "LEAN4_TIER2_COMPILATION_CERTIFICATE.md"
    cert.parent.mkdir(parents=True)
    cert.write_text("# Tier2\nCompilation PASSED", encoding="utf-8")

    report = completion_master_audit(tmp_path)
    task_map = {task["key"]: task for task in report["tasks"]}
    assert task_map["lean4_tier2_compile"]["status"] == "DONE"


def test_completion_master_audit_rejects_negative_markdown_certificate(tmp_path):
    cert = tmp_path / "docs" / "LEAN4_TIER2_COMPILATION_CERTIFICATE.md"
    cert.parent.mkdir(parents=True)
    cert.write_text("# Tier2\nCompilation NOT PASSED", encoding="utf-8")

    report = completion_master_audit(tmp_path)
    task_map = {task["key"]: task for task in report["tasks"]}
    assert task_map["lean4_tier2_compile"]["status"] == "PENDING"
