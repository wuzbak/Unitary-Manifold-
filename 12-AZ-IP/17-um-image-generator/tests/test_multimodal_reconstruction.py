# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from image_generator.engine.multimodal_reconstruction import (
    build_extruded_mesh,
    build_multimodal_scene_bundle,
    evaluate_multimodal_quality,
    export_mesh_stl,
    export_point_cloud_ply,
    generate_calibrated_point_cloud,
    generate_gaussian_splats,
)
from image_generator.engine import multimodal_reconstruction as mm


def test_generate_calibrated_point_cloud_shape_and_bounds() -> None:
    cloud = generate_calibrated_point_cloud(grid_size=9, scale_meters=2.0)
    points = cloud["points"]
    assert isinstance(points, np.ndarray)
    assert points.shape == (81, 3)
    assert cloud["bounds_meters"]["min"][0] == 0.0
    assert cloud["bounds_meters"]["max"][1] == 2.0


def test_generate_gaussian_splats_shape_matches_cloud() -> None:
    cloud = generate_calibrated_point_cloud(grid_size=7, scale_meters=1.0)
    splats = generate_gaussian_splats(cloud["points"], spacing_meters=float(cloud["spacing_meters"]))
    assert splats["centers"].shape == (49, 3)
    assert splats["sigmas_xyz"].shape == (49, 3)
    assert splats["opacities"].shape == (49,)
    assert splats["colors_rgb"].shape == (49, 3)


def test_generate_gaussian_splats_rejects_invalid_shape() -> None:
    with pytest.raises(ValueError):
        generate_gaussian_splats(np.array([1.0, 2.0, 3.0]), spacing_meters=0.01)


def test_build_extruded_mesh_is_watertight() -> None:
    cloud = generate_calibrated_point_cloud(grid_size=11, scale_meters=1.0)
    mesh = build_extruded_mesh(cloud["points"], grid_size=11)
    quality = evaluate_multimodal_quality(
        cloud["points"],
        mesh["vertices"],
        mesh["faces"],
        calibration_scale_meters=1.0,
    )
    assert quality["is_watertight"] is True
    assert quality["boundary_edge_count"] == 0
    assert quality["non_manifold_edge_count"] == 0


def test_build_extruded_mesh_rejects_mismatched_grid() -> None:
    cloud = generate_calibrated_point_cloud(grid_size=5, scale_meters=1.0)
    with pytest.raises(ValueError):
        build_extruded_mesh(cloud["points"], grid_size=4)


def test_export_point_cloud_ply_writes_ascii_ply(tmp_path: Path) -> None:
    cloud = generate_calibrated_point_cloud(grid_size=5, scale_meters=1.0)
    ply_path = export_point_cloud_ply(cloud["points"], tmp_path / "scene.ply")
    text = ply_path.read_text(encoding="utf-8")
    assert text.startswith("ply\nformat ascii 1.0\n")
    assert "element vertex 25" in text


def test_export_point_cloud_ply_accepts_255_color_space(tmp_path: Path) -> None:
    cloud = generate_calibrated_point_cloud(grid_size=3, scale_meters=1.0)
    colors = np.full((9, 3), [10.0, 20.0, 30.0], dtype=float)
    ply_path = export_point_cloud_ply(cloud["points"], tmp_path / "scene-255.ply", colors_rgb=colors)
    lines = ply_path.read_text(encoding="utf-8").splitlines()
    assert lines[-1].endswith("10 20 30")


def test_export_point_cloud_ply_rejects_invalid_color_range(tmp_path: Path) -> None:
    cloud = generate_calibrated_point_cloud(grid_size=3, scale_meters=1.0)
    colors = np.full((9, 3), [300.0, 20.0, 30.0], dtype=float)
    with pytest.raises(ValueError):
        export_point_cloud_ply(cloud["points"], tmp_path / "bad-colors.ply", colors_rgb=colors)


def test_export_mesh_stl_writes_ascii_stl(tmp_path: Path) -> None:
    cloud = generate_calibrated_point_cloud(grid_size=5, scale_meters=1.0)
    mesh = build_extruded_mesh(cloud["points"], grid_size=5)
    stl_path = export_mesh_stl(mesh["vertices"], mesh["faces"], tmp_path / "scene.stl", solid_name="scene")
    text = stl_path.read_text(encoding="utf-8")
    assert text.startswith("solid scene\n")
    assert "facet normal" in text
    assert text.rstrip().endswith("endsolid scene")


def test_build_multimodal_scene_bundle_outputs_all_artifacts(tmp_path: Path) -> None:
    bundle = build_multimodal_scene_bundle(tmp_path, scene_id="demo", grid_size=9, scale_meters=1.5)
    for key in ("gaussian_path", "point_cloud_path", "stl_path", "metadata_path", "manifest_path"):
        assert Path(bundle[key]).exists()

    metadata = json.loads(Path(bundle["metadata_path"]).read_text(encoding="utf-8"))
    assert metadata["source_of_truth"] == "point_cloud"
    assert metadata["quality"]["is_watertight"] is True
    assert metadata["quality"]["registration_rmse_mm"] >= 0.0
    assert metadata["quality"]["registration_rmse_mm"] < 1e-6

    gaussian = json.loads(Path(bundle["gaussian_path"]).read_text(encoding="utf-8"))
    assert gaussian["scene_id"] == "demo"
    assert gaussian["point_count"] == 81
    assert len(gaussian["splats"]["centers"]) == 81
    assert len(gaussian["splats"]["sigmas_xyz"]) == 81
    assert len(gaussian["splats"]["opacities"]) == 81
    assert len(gaussian["splats"]["colors_rgb"]) == 81


def test_bundle_write_failure_does_not_leave_partial_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_stl(*args, **kwargs):
        raise RuntimeError("forced stl failure")

    monkeypatch.setattr(mm, "export_mesh_stl", fail_stl)
    with pytest.raises(RuntimeError):
        build_multimodal_scene_bundle(tmp_path, scene_id="broken", grid_size=7, scale_meters=1.0)

    assert not (tmp_path / "broken.bundle.json").exists()
    assert not list(tmp_path.glob("broken.*"))


def test_bundle_failure_preserves_previous_manifest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    first = build_multimodal_scene_bundle(tmp_path, scene_id="stable", grid_size=7, scale_meters=1.0)
    original_manifest = Path(first["manifest_path"]).read_text(encoding="utf-8")

    def fail_stl(*args, **kwargs):
        raise RuntimeError("forced stl failure")

    monkeypatch.setattr(mm, "export_mesh_stl", fail_stl)
    with pytest.raises(RuntimeError):
        build_multimodal_scene_bundle(tmp_path, scene_id="stable", grid_size=9, scale_meters=1.5)

    assert Path(first["manifest_path"]).read_text(encoding="utf-8") == original_manifest


def test_bundle_rejects_parallel_same_scene_export(tmp_path: Path) -> None:
    lock = tmp_path / ".locked.lock"
    lock.write_text("1", encoding="utf-8")
    with pytest.raises(RuntimeError):
        build_multimodal_scene_bundle(tmp_path, scene_id="locked", grid_size=5, scale_meters=1.0)


def test_scene_id_is_sanitized_for_safe_paths(tmp_path: Path) -> None:
    bundle = build_multimodal_scene_bundle(tmp_path, scene_id="../unsafe/\nname", grid_size=5, scale_meters=1.0)
    assert ".." not in Path(bundle["manifest_path"]).name
    assert "/unsafe/" not in bundle["manifest_path"]


def test_manifest_uses_relative_artifact_paths(tmp_path: Path) -> None:
    bundle = build_multimodal_scene_bundle(tmp_path, scene_id="portable", grid_size=5, scale_meters=1.0)
    manifest_path = Path(bundle["manifest_path"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for rel_path in manifest["artifacts"].values():
        resolved = manifest_path.parent / rel_path
        assert resolved.exists()
