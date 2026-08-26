# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
from __future__ import annotations

from pathlib import Path

from .visualizations import (
    generate_birefringence_window_data,
    generate_braided_sound_speed_data,
    generate_cmb_plane_data,
    generate_holographic_boundary_data,
    generate_kk_tower_data,
    generate_penrose_entropy_data,
    generate_phi_landscape_data,
    generate_winding_mode_data,
)


def _get_pyplot():
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "matplotlib>=3.7 is required for PNG export. Install it before calling export helpers."
        ) from exc
    return plt


def _save_figure(fig, output_path: str | Path) -> Path:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=200, bbox_inches="tight")
    return destination


def export_cmb_plane_png(output_path: str | Path) -> Path:
    plt = _get_pyplot()
    data = generate_cmb_plane_data()
    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = data["scatter"]
    ax.scatter(scatter[:, 0], scatter[:, 1], alpha=0.9, label="comparison points")
    prediction = data["prediction"]
    ax.scatter([prediction[0]], [prediction[1]], marker="x", s=150, linewidths=3, label="UM prediction")
    ax.axhline(data["bicep_keck_bound"], linestyle="--", label="BICEP/Keck bound")
    ax.set_xlim(*data["x_range"])
    ax.set_ylim(*data["y_range"])
    ax.set_xlabel("scalar tilt n_s")
    ax.set_ylabel("tensor ratio r")
    ax.legend(loc="upper left")
    return _save_figure(fig, output_path)


def export_birefringence_window_png(output_path: str | Path) -> Path:
    plt = _get_pyplot()
    data = generate_birefringence_window_data()
    fig, ax = plt.subplots(figsize=(10, 2.5))
    ax.axvspan(*data["admissible_window"], alpha=0.25, label="admissible")
    ax.axvspan(*data["forbidden_gap"], alpha=0.35, color="red", label="forbidden gap")
    for beta in data["predictions"]:
        ax.axvline(beta, linewidth=2)
    ax.set_xlim(*data["axis_range"])
    ax.set_yticks([])
    ax.set_xlabel("beta (degrees)")
    ax.legend(loc="upper center", ncol=2)
    return _save_figure(fig, output_path)


def export_kk_tower_png(output_path: str | Path) -> Path:
    plt = _get_pyplot()
    data = generate_kk_tower_data()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(data["modes"], data["amplitudes"], width=0.7)
    ax.set_xlabel("mode number")
    ax.set_ylabel("normalized amplitude")
    return _save_figure(fig, output_path)


def export_winding_mode_png(output_path: str | Path) -> Path:
    plt = _get_pyplot()
    data = generate_winding_mode_data()
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(data["phase"], data["primary_mode"], label="primary")
    ax.plot(data["phase"], data["companion_mode"], label="companion")
    ax.set_xlabel("phase")
    ax.set_ylabel("amplitude")
    ax.legend(loc="upper right")
    return _save_figure(fig, output_path)


def export_phi_landscape_png(output_path: str | Path) -> Path:
    plt = _get_pyplot()
    data = generate_phi_landscape_data()
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(data["phi"], data["potential"], label="V(phi)")
    ax.axvline(data["minimum_phi"], linestyle="--", label="minimum")
    ax.set_xlabel("phi")
    ax.set_ylabel("potential")
    ax.legend(loc="upper center")
    return _save_figure(fig, output_path)


def export_penrose_entropy_png(output_path: str | Path) -> Path:
    plt = _get_pyplot()
    data = generate_penrose_entropy_data()
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(data["masses"], data["entropy"], label="entropy")
    ax.set_xlabel("mass")
    ax.set_ylabel("entropy")
    ax.legend(loc="upper left")
    return _save_figure(fig, output_path)


def export_holographic_boundary_png(output_path: str | Path) -> Path:
    plt = _get_pyplot()
    data = generate_holographic_boundary_data()
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(data["boundary_x"], data["boundary_y"])
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    return _save_figure(fig, output_path)


def export_braided_sound_speed_png(output_path: str | Path) -> Path:
    plt = _get_pyplot()
    data = generate_braided_sound_speed_data()
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(data["wave_number"], data["angular_frequency"], label="omega = c_s k")
    ax.set_xlabel("wave number")
    ax.set_ylabel("angular frequency")
    ax.legend(loc="upper left")
    return _save_figure(fig, output_path)


EXPORTERS = {
    "cmb": export_cmb_plane_png,
    "birefringence": export_birefringence_window_png,
    "kk_tower": export_kk_tower_png,
    "winding_mode": export_winding_mode_png,
    "phi_landscape": export_phi_landscape_png,
    "penrose_entropy": export_penrose_entropy_png,
    "holographic_boundary": export_holographic_boundary_png,
    "braided_sound_speed": export_braided_sound_speed_png,
}


def export_visualization(name: str, output_path: str | Path, **kwargs) -> Path:
    exporter = EXPORTERS.get(name)
    if exporter is None:
        raise ValueError(f"Unknown visualization name: {name}")
    if kwargs:
        raise ValueError("Per-visualization keyword overrides are not implemented in this standalone exporter.")
    return exporter(output_path)


__all__ = [
    "EXPORTERS",
    "export_visualization",
    "export_cmb_plane_png",
    "export_birefringence_window_png",
    "export_kk_tower_png",
    "export_winding_mode_png",
    "export_phi_landscape_png",
    "export_penrose_entropy_png",
    "export_holographic_boundary_png",
    "export_braided_sound_speed_png",
]
