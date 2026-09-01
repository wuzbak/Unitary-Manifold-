# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_ROOT))

from omega.open_science_export import (
    collect_derived_sm_parameters,
    export_sm_parameters,
    flatten_export_payload,
)
from omega.yukawa_explorer import (
    DEFAULT_BC_PARAMS,
    compute_yukawa_svd,
    parse_bc_parameters,
)


def _generated_paths() -> tuple[Path, Path]:
    output_dir = APP_ROOT / "tests" / "_generated"
    output_dir.mkdir(exist_ok=True)
    stem = f"sm_export_{os.getpid()}"
    return output_dir / f"{stem}.json", output_dir / f"{stem}.csv"


def _cleanup_generated_files() -> None:
    json_path, csv_path = _generated_paths()
    for path in (json_path, csv_path):
        if path.exists():
            path.unlink()


def test_parse_bc_parameters_defaults():
    assert parse_bc_parameters(None) == DEFAULT_BC_PARAMS


def test_parse_bc_parameters_from_string():
    params = parse_bc_parameters("alpha=0.1,beta=0.2")
    assert params["alpha"] == 0.1
    assert params["beta"] == 0.2
    assert params["gamma"] == 0.0


def test_parse_bc_parameters_rejects_invalid_chunk():
    try:
        parse_bc_parameters("alpha")
    except ValueError as exc:
        assert "Invalid boundary-condition item" in str(exc)
    else:
        raise AssertionError("ValueError not raised")


def test_compute_yukawa_svd_returns_expected_top_level_keys():
    payload = compute_yukawa_svd()
    assert {"source", "bc_params", "constants", "texture_matrices", "singular_values", "ckm", "pmns"} <= set(payload)


def test_compute_yukawa_svd_defaults_bc_params():
    payload = compute_yukawa_svd()
    assert payload["bc_params"] == DEFAULT_BC_PARAMS


def test_compute_yukawa_svd_reports_core_constants():
    payload = compute_yukawa_svd()
    assert payload["constants"]["n_w"] == 5
    assert payload["constants"]["k_cs"] == 74
    assert payload["constants"]["phi0"] == 1.0


def test_texture_matrices_have_three_by_three_shape():
    payload = compute_yukawa_svd()
    for matrix in payload["texture_matrices"].values():
        assert len(matrix) == 3
        assert all(len(row) == 3 for row in matrix)


def test_singular_values_are_sorted_descending():
    payload = compute_yukawa_svd()
    for values in payload["singular_values"].values():
        assert values[0] >= values[1] >= values[2] > 0.0


def test_ckm_report_shape_and_unitarity():
    payload = compute_yukawa_svd()
    ckm = payload["ckm"]
    assert len(ckm["matrix"]) == 3
    assert all(len(row) == 3 for row in ckm["matrix"])
    assert ckm["unitarity_residual"] < 1e-8


def test_pmns_report_shape_and_unitarity():
    payload = compute_yukawa_svd()
    pmns = payload["pmns"]
    assert len(pmns["matrix"]) == 3
    assert all(len(row) == 3 for row in pmns["matrix"])
    assert pmns["unitarity_residual"] < 1e-8


def test_ckm_angles_are_physical():
    payload = compute_yukawa_svd()
    for key in ("theta_12_deg", "theta_13_deg", "theta_23_deg"):
        assert 0.0 <= payload["ckm"][key] <= 90.0


def test_pmns_angles_are_physical():
    payload = compute_yukawa_svd()
    for key in ("theta_12_deg", "theta_13_deg", "theta_23_deg"):
        assert 0.0 <= payload["pmns"][key] <= 90.0


def test_compute_yukawa_svd_is_deterministic():
    first = compute_yukawa_svd({"alpha": 0.1, "beta": 0.2})
    second = compute_yukawa_svd({"alpha": 0.1, "beta": 0.2})
    assert first == second


def test_alpha_bc_perturbs_up_texture():
    base = compute_yukawa_svd()
    shifted = compute_yukawa_svd({"alpha": 0.2})
    assert base["texture_matrices"]["up"] != shifted["texture_matrices"]["up"]


def test_beta_bc_perturbs_down_texture():
    base = compute_yukawa_svd()
    shifted = compute_yukawa_svd({"beta": 0.2})
    assert base["texture_matrices"]["down"] != shifted["texture_matrices"]["down"]


def test_gamma_bc_perturbs_ckm_matrix():
    base = compute_yukawa_svd()
    shifted = compute_yukawa_svd({"gamma": 0.5})
    assert base["ckm"]["matrix"] != shifted["ckm"]["matrix"]


def test_payload_is_json_serialisable():
    payload = compute_yukawa_svd({"alpha": 0.1})
    text = json.dumps(payload)
    assert "ckm" in text
    assert "pmns" in text


def test_cli_runs_with_bc_arguments():
    script = APP_ROOT / "omega" / "yukawa_explorer.py"
    result = subprocess.run([sys.executable, str(script), "--bc", "alpha=0.1,beta=0.2"], capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert "CKM:" in result.stdout
    assert "PMNS:" in result.stdout
    assert "alpha" in result.stdout


def test_collect_derived_sm_parameters_contains_sections():
    payload = collect_derived_sm_parameters({"alpha": 0.1})
    assert payload["metadata"]["repository_version"] == "v25.5"
    assert "particle_physics" in payload
    assert "yukawa" in payload


def test_collect_derived_sm_parameters_carries_bc_params():
    payload = collect_derived_sm_parameters({"alpha": 0.1, "beta": 0.2})
    assert payload["yukawa"]["bc_params"]["alpha"] == 0.1
    assert payload["yukawa"]["bc_params"]["beta"] == 0.2


def test_flatten_export_payload_exposes_particle_paths():
    payload = collect_derived_sm_parameters()
    rows = dict(flatten_export_payload(payload))
    assert "particle_physics.y5_universal" in rows
    assert "yukawa.ckm.matrix.0.0" in rows


def test_export_sm_parameters_writes_json_and_csv():
    _cleanup_generated_files()
    json_path, csv_path = _generated_paths()
    payload = export_sm_parameters(json_path, csv_path, {"alpha": 0.1})
    assert json_path.exists()
    assert csv_path.exists()
    json_payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert json_payload["metadata"]["sprint"] == "BA"
    assert payload["yukawa"]["bc_params"]["alpha"] == 0.1
    csv_text = csv_path.read_text(encoding="utf-8")
    assert "path,value" in csv_text
    assert "particle_physics.y5_universal" in csv_text
    _cleanup_generated_files()


def test_export_cli_writes_requested_files():
    _cleanup_generated_files()
    json_path, csv_path = _generated_paths()
    script = APP_ROOT / "omega" / "open_science_export.py"
    result = subprocess.run(
        [sys.executable, str(script), "--json-path", str(json_path), "--csv-path", str(csv_path), "--bc", "alpha=0.1"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert json_path.exists()
    assert csv_path.exists()
    assert "Wrote" in result.stdout
    _cleanup_generated_files()


def test_source_reports_core_or_fallback_mode():
    payload = compute_yukawa_svd()
    assert payload["source"] in {"src.core.yukawa_orbifold_bc_texture", "standalone_numpy"}
