# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import numpy as np


def generate_calibrated_point_cloud(
    grid_size: int = 41,
    scale_meters: float = 1.0,
    height_scale_meters: float = 0.12,
) -> dict[str, np.ndarray | float | dict[str, list[float]]]:
    size = max(3, int(grid_size))
    x = np.linspace(0.0, scale_meters, size, dtype=float)
    y = np.linspace(0.0, scale_meters, size, dtype=float)
    xx, yy = np.meshgrid(x, y, indexing="xy")
    xr = (xx - (scale_meters / 2.0)) / max(scale_meters, 1e-12)
    yr = (yy - (scale_meters / 2.0)) / max(scale_meters, 1e-12)
    bump = np.exp(-12.0 * (xr**2 + yr**2))
    corrugation = 0.08 * np.sin(8.0 * np.pi * xr) * np.cos(8.0 * np.pi * yr)
    zz = height_scale_meters * (bump + corrugation)
    points = np.column_stack((xx.ravel(), yy.ravel(), zz.ravel()))
    spacing = float(scale_meters / (size - 1))
    return {
        "points": points,
        "grid_size": float(size),
        "scale_meters": float(scale_meters),
        "spacing_meters": spacing,
        "bounds_meters": {
            "min": points.min(axis=0).tolist(),
            "max": points.max(axis=0).tolist(),
        },
    }


def generate_gaussian_splats(points: np.ndarray, spacing_meters: float) -> dict[str, np.ndarray]:
    cloud = np.asarray(points, dtype=float)
    if cloud.ndim != 2 or cloud.shape[1] != 3:
        raise ValueError("points must be shaped (N, 3)")
    sigma = max(spacing_meters * 0.45, 1e-6)
    z = cloud[:, 2]
    z_span = max(float(z.max() - z.min()), 1e-12)
    z_norm = (z - z.min()) / z_span
    colors = np.column_stack((0.2 + 0.8 * z_norm, 0.4 + 0.5 * (1.0 - z_norm), np.full_like(z_norm, 0.92)))
    return {
        "centers": cloud.copy(),
        "sigmas_xyz": np.full((cloud.shape[0], 3), sigma, dtype=float),
        "opacities": np.full(cloud.shape[0], 0.88, dtype=float),
        "colors_rgb": colors,
    }


def build_extruded_mesh(points: np.ndarray, grid_size: int, base_offset_meters: float = 0.02) -> dict[str, np.ndarray]:
    cloud = np.asarray(points, dtype=float)
    size = int(grid_size)
    if cloud.shape != (size * size, 3):
        raise ValueError("points must match a flattened square grid")

    top = cloud.copy()
    base_z = float(cloud[:, 2].min() - abs(base_offset_meters))
    bottom = cloud.copy()
    bottom[:, 2] = base_z
    vertices = np.vstack((top, bottom))

    def idx_top(r: int, c: int) -> int:
        return r * size + c

    def idx_bottom(r: int, c: int) -> int:
        return size * size + r * size + c

    faces: list[tuple[int, int, int]] = []

    for r in range(size - 1):
        for c in range(size - 1):
            a = idx_top(r, c)
            b = idx_top(r, c + 1)
            d = idx_top(r + 1, c)
            e = idx_top(r + 1, c + 1)
            faces.append((a, b, d))
            faces.append((b, e, d))

            ab = idx_bottom(r, c)
            bb = idx_bottom(r, c + 1)
            db = idx_bottom(r + 1, c)
            eb = idx_bottom(r + 1, c + 1)
            faces.append((ab, db, bb))
            faces.append((bb, db, eb))

    perimeter: list[tuple[int, int]] = []
    for c in range(size - 1):
        perimeter.append((idx_top(0, c), idx_top(0, c + 1)))
    for r in range(size - 1):
        perimeter.append((idx_top(r, size - 1), idx_top(r + 1, size - 1)))
    for c in range(size - 1, 0, -1):
        perimeter.append((idx_top(size - 1, c), idx_top(size - 1, c - 1)))
    for r in range(size - 1, 0, -1):
        perimeter.append((idx_top(r, 0), idx_top(r - 1, 0)))

    for t0, t1 in perimeter:
        b0 = t0 + size * size
        b1 = t1 + size * size
        faces.append((t0, t1, b0))
        faces.append((t1, b1, b0))

    return {"vertices": vertices, "faces": np.asarray(faces, dtype=int)}


def _edge_manifold_stats(faces: np.ndarray) -> dict[str, int | bool]:
    counts: dict[tuple[int, int], int] = {}
    for tri in faces:
        a, b, c = [int(v) for v in tri]
        for u, v in ((a, b), (b, c), (c, a)):
            edge = (u, v) if u < v else (v, u)
            counts[edge] = counts.get(edge, 0) + 1
    non_manifold = sum(1 for c in counts.values() if c > 2)
    boundary = sum(1 for c in counts.values() if c == 1)
    return {
        "non_manifold_edge_count": non_manifold,
        "boundary_edge_count": boundary,
        "is_watertight": non_manifold == 0 and boundary == 0,
    }


def _nearest_vertex_distances_chunked(points: np.ndarray, vertices: np.ndarray, chunk_size: int = 2048) -> np.ndarray:
    result = np.empty(points.shape[0], dtype=float)
    for start in range(0, points.shape[0], chunk_size):
        stop = min(points.shape[0], start + chunk_size)
        block = points[start:stop]
        sq = np.sum((block[:, None, :] - vertices[None, :, :]) ** 2, axis=2)
        result[start:stop] = np.sqrt(np.min(sq, axis=1))
    return result


def evaluate_multimodal_quality(
    point_cloud: np.ndarray,
    mesh_vertices: np.ndarray,
    mesh_faces: np.ndarray,
    calibration_scale_meters: float,
) -> dict[str, float | bool | int]:
    cloud = np.asarray(point_cloud, dtype=float)
    vertices = np.asarray(mesh_vertices, dtype=float)
    faces = np.asarray(mesh_faces, dtype=int)
    z_floor = float(vertices[:, 2].min())
    top_surface = vertices[vertices[:, 2] > (z_floor + 1e-12)]
    nearest: np.ndarray | None = None

    try:
        from scipy.interpolate import LinearNDInterpolator  # type: ignore

        interpolator = LinearNDInterpolator(top_surface[:, :2], top_surface[:, 2], fill_value=np.nan)
        z_surface = interpolator(cloud[:, 0], cloud[:, 1])
        if not np.isnan(z_surface).any():
            projected = np.column_stack((cloud[:, 0], cloud[:, 1], z_surface))
            nearest = np.linalg.norm(cloud - projected, axis=1)
    except Exception:
        nearest = None

    if nearest is None:
        try:
            from scipy.spatial import cKDTree  # type: ignore

            tree = cKDTree(top_surface if top_surface.size else vertices)
            nearest = tree.query(cloud, workers=-1)[0]
        except Exception:
            nearest = _nearest_vertex_distances_chunked(cloud, top_surface if top_surface.size else vertices)

    nearest_sq = np.square(nearest)
    x_span = float(vertices[:, 0].max() - vertices[:, 0].min())
    y_span = float(vertices[:, 1].max() - vertices[:, 1].min())
    reference_span = max(x_span, y_span, 1e-12)
    meters_per_unit = float(calibration_scale_meters) / reference_span
    scale_mm = 1000.0 * meters_per_unit
    manifold = _edge_manifold_stats(faces)
    return {
        "calibration_scale_meters": float(calibration_scale_meters),
        "registration_rmse_mm": float(np.sqrt(np.mean(nearest_sq)) * scale_mm),
        "cloud_to_mesh_max_mm": float(nearest.max() * scale_mm),
        "cloud_to_mesh_p95_mm": float(np.quantile(nearest, 0.95) * scale_mm),
        "vertex_count": int(vertices.shape[0]),
        "triangle_count": int(faces.shape[0]),
        "is_watertight": bool(manifold["is_watertight"]),
        "boundary_edge_count": int(manifold["boundary_edge_count"]),
        "non_manifold_edge_count": int(manifold["non_manifold_edge_count"]),
    }


def export_point_cloud_ply(points: np.ndarray, destination: str | Path, colors_rgb: np.ndarray | None = None) -> Path:
    pts = np.asarray(points, dtype=float)
    if pts.ndim != 2 or pts.shape[1] != 3:
        raise ValueError("points must be shaped (N, 3)")
    if colors_rgb is None:
        colors = np.full((pts.shape[0], 3), 220, dtype=np.uint8)
    else:
        color_input = np.asarray(colors_rgb, dtype=float)
        if color_input.shape != (pts.shape[0], 3):
            raise ValueError("colors_rgb must be shaped (N, 3)")
        max_value = float(np.max(color_input))
        min_value = float(np.min(color_input))
        if 0.0 <= min_value and max_value <= 1.0:
            colors = np.clip(np.rint(color_input * 255.0), 0, 255).astype(np.uint8)
        elif 0.0 <= min_value and max_value <= 255.0:
            colors = np.clip(np.rint(color_input), 0, 255).astype(np.uint8)
        else:
            raise ValueError("colors_rgb must be in 0..1 or 0..255 range")

    out = Path(destination)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        fh.write("ply\nformat ascii 1.0\n")
        fh.write(f"element vertex {pts.shape[0]}\n")
        fh.write("property float x\nproperty float y\nproperty float z\n")
        fh.write("property uchar red\nproperty uchar green\nproperty uchar blue\n")
        fh.write("end_header\n")
        for xyz, rgb in zip(pts, colors, strict=True):
            fh.write(f"{xyz[0]:.8f} {xyz[1]:.8f} {xyz[2]:.8f} {int(rgb[0])} {int(rgb[1])} {int(rgb[2])}\n")
    return out


def export_mesh_stl(vertices: np.ndarray, faces: np.ndarray, destination: str | Path, solid_name: str = "um_multimodal") -> Path:
    verts = np.asarray(vertices, dtype=float)
    tris = np.asarray(faces, dtype=int)
    out = Path(destination)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        fh.write(f"solid {solid_name}\n")
        for tri in tris:
            p0, p1, p2 = verts[tri[0]], verts[tri[1]], verts[tri[2]]
            normal = np.cross(p1 - p0, p2 - p0)
            norm = float(np.linalg.norm(normal))
            if norm > 0.0:
                normal = normal / norm
            fh.write(f"  facet normal {normal[0]:.8e} {normal[1]:.8e} {normal[2]:.8e}\n")
            fh.write("    outer loop\n")
            fh.write(f"      vertex {p0[0]:.8f} {p0[1]:.8f} {p0[2]:.8f}\n")
            fh.write(f"      vertex {p1[0]:.8f} {p1[1]:.8f} {p1[2]:.8f}\n")
            fh.write(f"      vertex {p2[0]:.8f} {p2[1]:.8f} {p2[2]:.8f}\n")
            fh.write("    endloop\n")
            fh.write("  endfacet\n")
        fh.write(f"endsolid {solid_name}\n")
    return out


def build_multimodal_scene_bundle(
    output_dir: str | Path,
    scene_id: str = "um_scene",
    grid_size: int = 41,
    scale_meters: float = 1.0,
) -> dict[str, str | dict[str, float | bool | int]]:
    cloud = generate_calibrated_point_cloud(grid_size=grid_size, scale_meters=scale_meters)
    points = np.asarray(cloud["points"], dtype=float)
    spacing = float(cloud["spacing_meters"])
    splats = generate_gaussian_splats(points, spacing_meters=spacing)
    mesh = build_extruded_mesh(points, grid_size=int(cloud["grid_size"]))
    quality = evaluate_multimodal_quality(points, mesh["vertices"], mesh["faces"], calibration_scale_meters=scale_meters)

    base = Path(output_dir)
    base.mkdir(parents=True, exist_ok=True)
    gaussian_path = base / f"{scene_id}.gaussian.json"
    cloud_path = base / f"{scene_id}.pointcloud.ply"
    stl_path = base / f"{scene_id}.mesh.stl"
    metadata_path = base / f"{scene_id}.metadata.json"
    temp_tag = uuid4().hex
    gaussian_tmp = base / f".{scene_id}.{temp_tag}.gaussian.json.tmp"
    cloud_tmp = base / f".{scene_id}.{temp_tag}.pointcloud.ply.tmp"
    stl_tmp = base / f".{scene_id}.{temp_tag}.mesh.stl.tmp"
    metadata_tmp = base / f".{scene_id}.{temp_tag}.metadata.json.tmp"

    gaussian_payload = {
        "scene_id": scene_id,
        "calibration_scale_meters": scale_meters,
        "point_count": int(points.shape[0]),
        "splats": {
            "centers": splats["centers"].tolist(),
            "sigmas_xyz": splats["sigmas_xyz"].tolist(),
            "opacities": splats["opacities"].tolist(),
            "colors_rgb": splats["colors_rgb"].tolist(),
        },
    }
    cleanup_targets = [gaussian_tmp, cloud_tmp, stl_tmp, metadata_tmp]
    backups: list[tuple[Path, Path]] = []
    promoted: list[Path] = []
    try:
        gaussian_tmp.write_text(json.dumps(gaussian_payload, indent=2), encoding="utf-8")
        export_point_cloud_ply(points, cloud_tmp, colors_rgb=np.asarray(splats["colors_rgb"], dtype=float))
        export_mesh_stl(mesh["vertices"], mesh["faces"], stl_tmp, solid_name=scene_id)

        metadata = {
            "scene_id": scene_id,
            "calibration_scale_meters": scale_meters,
            "units": "meters",
            "source_of_truth": "point_cloud",
            "artifacts": {
                "gaussian_render": gaussian_path.name,
                "point_cloud_measurement": cloud_path.name,
                "stl_mesh": stl_path.name,
            },
            "quality": quality,
        }
        metadata_tmp.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        replacements = [
            (gaussian_tmp, gaussian_path),
            (cloud_tmp, cloud_path),
            (stl_tmp, stl_path),
            (metadata_tmp, metadata_path),
        ]
        for _, final_path in replacements:
            if final_path.exists():
                backup = base / f".{final_path.name}.{temp_tag}.bak"
                final_path.replace(backup)
                backups.append((final_path, backup))

        for temp_path, final_path in replacements:
            temp_path.replace(final_path)
            promoted.append(final_path)
    except Exception:
        for final_path in promoted:
            if final_path.exists():
                final_path.unlink()
        for final_path, backup in backups:
            if backup.exists():
                backup.replace(final_path)
        for target in cleanup_targets:
            if target.exists():
                target.unlink()
        raise
    finally:
        for _, backup in backups:
            if backup.exists():
                backup.unlink()

    return {
        "gaussian_path": str(gaussian_path),
        "point_cloud_path": str(cloud_path),
        "stl_path": str(stl_path),
        "metadata_path": str(metadata_path),
        "quality": quality,
    }


__all__ = [
    "generate_calibrated_point_cloud",
    "generate_gaussian_splats",
    "build_extruded_mesh",
    "evaluate_multimodal_quality",
    "export_point_cloud_ply",
    "export_mesh_stl",
    "build_multimodal_scene_bundle",
]
