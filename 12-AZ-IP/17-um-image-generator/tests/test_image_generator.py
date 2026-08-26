# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import image_generator
from image_generator.app.server import ImageGeneratorRequestHandler, UI_ROOT, create_server
from image_generator.engine import export as export_mod
from image_generator.engine.constants import (
    AREA_TO_ENTROPY_RATIO,
    BETA_CEILING,
    BETA_FLOOR,
    BETA_FORBIDDEN_HIGH,
    BETA_FORBIDDEN_LOW,
    BETA_HIGH,
    BETA_LOW,
    BRAIDED_SOUND_SPEED,
    CMB_BICEP_KECK_BOUND,
    CMB_X_RANGE,
    CMB_Y_RANGE,
    DM21_TENSIONS,
    HOLOGRAPHIC_RADIUS,
    K_CS,
    KK_MODE_COUNT,
    LEAN4_THEOREMS,
    N_S,
    PENROSE_ENTROPY_RATIO,
    PHI_0,
    PLANCK_CENTER,
    R_BRAIDED,
    TEST_COUNT,
    UM_IMAGE_CONSTANTS,
    WINDING_NUMBER,
    XI_C,
)
from image_generator.engine.visualizations import (
    VISUALIZATION_FUNCTIONS,
    generate_birefringence_window_data,
    generate_braided_sound_speed_data,
    generate_cmb_plane_data,
    generate_holographic_boundary_data,
    generate_kk_tower_data,
    generate_penrose_entropy_data,
    generate_phi_landscape_data,
    generate_winding_mode_data,
)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("N_S", 0.9635),
        ("R_BRAIDED", 0.0315),
        ("BETA_LOW", 0.273),
        ("BETA_HIGH", 0.331),
        ("BETA_FLOOR", 0.22),
        ("BETA_CEILING", 0.38),
        ("BETA_FORBIDDEN_LOW", 0.29),
        ("BETA_FORBIDDEN_HIGH", 0.31),
        ("WINDING_NUMBER", 5),
        ("K_CS", 74),
        ("BRAIDED_SOUND_SPEED", 12 / 37),
        ("XI_C", 35 / 74),
        ("PHI_0", 1.0),
        ("LEAN4_THEOREMS", 1411),
        ("TEST_COUNT", 58563),
        ("PENROSE_ENTROPY_RATIO", 0.25),
        ("AREA_TO_ENTROPY_RATIO", 4.0),
        ("HOLOGRAPHIC_RADIUS", 1.0),
    ],
)
def test_scalar_constants(name: str, expected: float) -> None:
    from image_generator.engine import constants as const

    assert getattr(const, name) == pytest.approx(expected)


@pytest.mark.parametrize("index, expected", list(enumerate([2.98, 1.16, 1.07])))
def test_dm21_tensions(index: int, expected: float) -> None:
    assert DM21_TENSIONS[index] == pytest.approx(expected)


def test_um_image_constants_contains_expected_keys() -> None:
    for key in ["N_S", "R_BRAIDED", "BETA_LOW", "K_CS", "DM21_TENSIONS", "TEST_COUNT"]:
        assert key in UM_IMAGE_CONSTANTS


def test_um_image_constants_array_copies_are_numpy() -> None:
    assert isinstance(UM_IMAGE_CONSTANTS["PLANCK_CENTER"], np.ndarray)
    assert isinstance(UM_IMAGE_CONSTANTS["DM21_TENSIONS"], np.ndarray)


def test_package_exports_server_symbols() -> None:
    assert hasattr(image_generator, "create_server")
    assert hasattr(image_generator, "UI_ROOT")


def test_visualization_registry_has_eight_entries() -> None:
    assert len(VISUALIZATION_FUNCTIONS) == 8


@pytest.mark.parametrize(
    "name",
    [
        "cmb",
        "birefringence",
        "kk_tower",
        "winding_mode",
        "phi_landscape",
        "penrose_entropy",
        "holographic_boundary",
        "braided_sound_speed",
    ],
)
def test_visualization_registry_entries_are_callable(name: str) -> None:
    assert callable(VISUALIZATION_FUNCTIONS[name])


def test_cmb_plane_return_type() -> None:
    assert isinstance(generate_cmb_plane_data(), dict)


def test_cmb_plane_prediction_point_present() -> None:
    data = generate_cmb_plane_data()
    assert data["prediction"][0] == pytest.approx(N_S)
    assert data["prediction"][1] == pytest.approx(R_BRAIDED)


def test_cmb_plane_planck_center_matches_constant() -> None:
    data = generate_cmb_plane_data()
    assert np.allclose(data["planck_center"], PLANCK_CENTER)


def test_cmb_plane_ranges_match_constants() -> None:
    data = generate_cmb_plane_data()
    assert np.allclose(data["x_range"], CMB_X_RANGE)
    assert np.allclose(data["y_range"], CMB_Y_RANGE)


def test_cmb_plane_scatter_shape() -> None:
    data = generate_cmb_plane_data()
    assert data["scatter"].shape == (6, 2)


def test_cmb_plane_bicep_bound() -> None:
    data = generate_cmb_plane_data()
    assert data["bicep_keck_bound"] == pytest.approx(CMB_BICEP_KECK_BOUND)


def test_birefringence_return_type() -> None:
    assert isinstance(generate_birefringence_window_data(), dict)


def test_birefringence_predictions_in_bounds() -> None:
    data = generate_birefringence_window_data()
    assert data["predictions_in_bounds"].all()


def test_birefringence_predictions_outside_gap() -> None:
    data = generate_birefringence_window_data()
    assert data["predictions_outside_gap"].all()


def test_birefringence_canonical_values_present() -> None:
    data = generate_birefringence_window_data()
    assert np.allclose(data["predictions"], np.array([BETA_LOW, BETA_HIGH]))


def test_birefringence_admissible_window_matches_constants() -> None:
    data = generate_birefringence_window_data()
    assert np.allclose(data["admissible_window"], np.array([BETA_FLOOR, BETA_CEILING]))


def test_birefringence_forbidden_gap_matches_constants() -> None:
    data = generate_birefringence_window_data()
    assert np.allclose(data["forbidden_gap"], np.array([BETA_FORBIDDEN_LOW, BETA_FORBIDDEN_HIGH]))


def test_kk_tower_return_type() -> None:
    assert isinstance(generate_kk_tower_data(), dict)


def test_kk_tower_mode_count() -> None:
    assert len(generate_kk_tower_data()["modes"]) == KK_MODE_COUNT


def test_kk_tower_first_mode_amplitude() -> None:
    assert generate_kk_tower_data()["amplitudes"][0] == pytest.approx(1.0)


def test_kk_tower_last_mode_amplitude() -> None:
    assert generate_kk_tower_data()["amplitudes"][-1] == pytest.approx(1 / 100)


def test_kk_tower_normalized_equals_amplitudes() -> None:
    data = generate_kk_tower_data()
    assert np.allclose(data["normalized_amplitudes"], data["amplitudes"])


def test_winding_mode_return_type() -> None:
    assert isinstance(generate_winding_mode_data(), dict)


def test_winding_mode_active_mode_is_five() -> None:
    assert generate_winding_mode_data()["active_mode"] == WINDING_NUMBER


def test_winding_mode_mode_numbers_end_at_five() -> None:
    assert generate_winding_mode_data()["mode_numbers"][-1] == WINDING_NUMBER


def test_winding_mode_primary_and_companion_shapes_match() -> None:
    data = generate_winding_mode_data()
    assert data["primary_mode"].shape == data["companion_mode"].shape


def test_winding_mode_starts_at_zero() -> None:
    assert generate_winding_mode_data()["primary_mode"][0] == pytest.approx(0.0)


def test_phi_landscape_return_type() -> None:
    assert isinstance(generate_phi_landscape_data(), dict)


def test_phi_landscape_minimum_at_phi_zero_point() -> None:
    assert generate_phi_landscape_data()["minimum_phi"] == pytest.approx(PHI_0)


def test_phi_landscape_minimum_value_is_zero() -> None:
    assert generate_phi_landscape_data()["minimum_value"] == pytest.approx(0.0)


def test_phi_landscape_gradient_vanishes_at_minimum() -> None:
    data = generate_phi_landscape_data()
    assert data["gradient"][data["minimum_index"]] == pytest.approx(0.0)


def test_phi_landscape_phi_grid_contains_phi0() -> None:
    assert PHI_0 in generate_phi_landscape_data()["phi"]


def test_penrose_entropy_return_type() -> None:
    assert isinstance(generate_penrose_entropy_data(), dict)


def test_penrose_entropy_nonnegative() -> None:
    assert np.all(generate_penrose_entropy_data()["entropy"] >= 0.0)


def test_penrose_entropy_ratio_constant() -> None:
    assert np.allclose(generate_penrose_entropy_data()["entropy_to_area_ratio"], PENROSE_ENTROPY_RATIO)


def test_penrose_area_to_entropy_ratio_constant() -> None:
    assert np.allclose(generate_penrose_entropy_data()["area_to_entropy_ratio"], AREA_TO_ENTROPY_RATIO)


def test_penrose_entropy_scales_with_mass_squared() -> None:
    data = generate_penrose_entropy_data(np.array([1.0, 2.0]))
    assert data["entropy"][1] / data["entropy"][0] == pytest.approx(4.0)


def test_holographic_boundary_return_type() -> None:
    assert isinstance(generate_holographic_boundary_data(), dict)


def test_holographic_boundary_radius_matches_constant() -> None:
    assert generate_holographic_boundary_data()["radius"] == pytest.approx(HOLOGRAPHIC_RADIUS)


def test_holographic_boundary_entropy_area_ratio_matches_pillar_four() -> None:
    assert generate_holographic_boundary_data()["entropy_to_area_ratio"] == pytest.approx(PENROSE_ENTROPY_RATIO)


def test_holographic_boundary_area_to_entropy_ratio_is_four() -> None:
    assert generate_holographic_boundary_data()["area_to_entropy_ratio"] == pytest.approx(AREA_TO_ENTROPY_RATIO)


def test_holographic_boundary_points_match_circle() -> None:
    data = generate_holographic_boundary_data()
    radii = np.sqrt(np.square(data["boundary_x"]) + np.square(data["boundary_y"]))
    assert np.allclose(radii, HOLOGRAPHIC_RADIUS)


def test_braided_sound_speed_return_type() -> None:
    assert isinstance(generate_braided_sound_speed_data(), dict)


def test_braided_sound_speed_constant_value() -> None:
    assert generate_braided_sound_speed_data()["c_s"] == pytest.approx(BRAIDED_SOUND_SPEED)


def test_braided_sound_speed_phase_velocity_constant() -> None:
    assert np.allclose(generate_braided_sound_speed_data()["phase_velocity"], BRAIDED_SOUND_SPEED)


def test_braided_sound_speed_group_velocity_constant() -> None:
    assert np.allclose(generate_braided_sound_speed_data()["group_velocity"], BRAIDED_SOUND_SPEED)


def test_braided_sound_speed_linear_dispersion() -> None:
    data = generate_braided_sound_speed_data()
    ratio = data["angular_frequency"][10] / data["wave_number"][10]
    assert ratio == pytest.approx(BRAIDED_SOUND_SPEED)


def test_ui_root_exists() -> None:
    assert UI_ROOT.exists()


def test_ui_index_exists() -> None:
    assert (UI_ROOT / "index.html").exists()


def test_ui_js_exists() -> None:
    assert (UI_ROOT / "um-image-generator.js").exists()


def test_ui_html_mentions_title() -> None:
    assert "UM Physics Image Generator" in (UI_ROOT / "index.html").read_text(encoding="utf-8")


def test_ui_html_imports_local_js() -> None:
    assert './um-image-generator.js' in (UI_ROOT / "index.html").read_text(encoding="utf-8")


def test_js_copy_contains_constants() -> None:
    assert 'export const N_S = 0.9635;' in (UI_ROOT / "um-image-generator.js").read_text(encoding="utf-8")


def test_run_py_exists() -> None:
    assert (PRODUCT_ROOT / "run.py").exists()


def test_run_py_is_executable() -> None:
    assert os.access(PRODUCT_ROOT / "run.py", os.X_OK)


def test_run_py_defines_default_port() -> None:
    text = (PRODUCT_ROOT / 'run.py').read_text(encoding='utf-8')
    assert '--port' in text
    assert '8017' in text


def test_server_handler_class_present() -> None:
    assert ImageGeneratorRequestHandler.__name__ == 'ImageGeneratorRequestHandler'


def test_create_server_binds_requested_port() -> None:
    server = create_server(port=0)
    try:
        assert server.server_address[1] > 0
    finally:
        server.server_close()


def test_server_serves_ui_directory() -> None:
    server = create_server(port=0)
    try:
        assert server.RequestHandlerClass.keywords['directory'] == UI_ROOT
    finally:
        server.server_close()


def test_export_visualization_rejects_unknown_name() -> None:
    with pytest.raises(ValueError):
        export_mod.export_visualization('unknown', PRODUCT_ROOT / 'out.png')


def test_export_visualization_rejects_kwargs() -> None:
    with pytest.raises(ValueError):
        export_mod.export_visualization('cmb', PRODUCT_ROOT / 'out.png', extra=True)


def test_export_requires_matplotlib_when_missing() -> None:
    with patch.dict(sys.modules, {'matplotlib': None, 'matplotlib.pyplot': None}):
        with pytest.raises(RuntimeError):
            export_mod.export_cmb_plane_png(PRODUCT_ROOT / 'tests' / 'cmb.png')


def test_exporters_registry_has_eight_entries() -> None:
    assert len(export_mod.EXPORTERS) == 8


@pytest.mark.parametrize(
    'name',
    [
        'cmb',
        'birefringence',
        'kk_tower',
        'winding_mode',
        'phi_landscape',
        'penrose_entropy',
        'holographic_boundary',
        'braided_sound_speed',
    ],
)
def test_exporters_registry_entries_callable(name: str) -> None:
    assert callable(export_mod.EXPORTERS[name])


def test_generic_export_uses_registered_exporter() -> None:
    sentinel = PRODUCT_ROOT / 'tests' / 'dummy.png'
    with patch.dict(export_mod.EXPORTERS, {'cmb': lambda output_path: sentinel}):
        assert export_mod.export_visualization('cmb', sentinel) == sentinel


def test_export_cmb_plane_png_with_fake_matplotlib(tmp_path: Path) -> None:
    class FakeFigure:
        def savefig(self, path, dpi=None, bbox_inches=None):
            Path(path).write_text('png', encoding='utf-8')

    class FakeAxes:
        def scatter(self, *args, **kwargs):
            return None
        def axhline(self, *args, **kwargs):
            return None
        def set_xlim(self, *args, **kwargs):
            return None
        def set_ylim(self, *args, **kwargs):
            return None
        def set_xlabel(self, *args, **kwargs):
            return None
        def set_ylabel(self, *args, **kwargs):
            return None
        def legend(self, *args, **kwargs):
            return None

    fake_plt = SimpleNamespace(subplots=lambda **kwargs: (FakeFigure(), FakeAxes()))
    with patch.object(export_mod, '_get_pyplot', return_value=fake_plt):
        output = tmp_path / 'cmb.png'
        assert export_mod.export_cmb_plane_png(output) == output
        assert output.exists()


def test_export_kk_tower_png_with_fake_matplotlib(tmp_path: Path) -> None:
    class FakeFigure:
        def savefig(self, path, dpi=None, bbox_inches=None):
            Path(path).write_text('png', encoding='utf-8')

    class FakeAxes:
        def bar(self, *args, **kwargs):
            return None
        def set_xlabel(self, *args, **kwargs):
            return None
        def set_ylabel(self, *args, **kwargs):
            return None

    fake_plt = SimpleNamespace(subplots=lambda **kwargs: (FakeFigure(), FakeAxes()))
    with patch.object(export_mod, '_get_pyplot', return_value=fake_plt):
        output = tmp_path / 'kk.png'
        assert export_mod.export_kk_tower_png(output) == output
        assert output.exists()


def test_export_holographic_boundary_png_with_fake_matplotlib(tmp_path: Path) -> None:
    class FakeFigure:
        def savefig(self, path, dpi=None, bbox_inches=None):
            Path(path).write_text('png', encoding='utf-8')

    class FakeAxes:
        def plot(self, *args, **kwargs):
            return None
        def set_aspect(self, *args, **kwargs):
            return None
        def set_xlabel(self, *args, **kwargs):
            return None
        def set_ylabel(self, *args, **kwargs):
            return None

    fake_plt = SimpleNamespace(subplots=lambda **kwargs: (FakeFigure(), FakeAxes()))
    with patch.object(export_mod, '_get_pyplot', return_value=fake_plt):
        output = tmp_path / 'boundary.png'
        assert export_mod.export_holographic_boundary_png(output) == output
        assert output.exists()


def test_requirements_file_contents() -> None:
    text = (PRODUCT_ROOT / 'requirements.txt').read_text(encoding='utf-8')
    assert 'numpy>=1.24' in text
    assert 'scipy>=1.11' in text


def test_readme_exists() -> None:
    assert (PRODUCT_ROOT / 'README.md').exists()


def test_readme_mentions_adjacent_track() -> None:
    assert 'ADJACENT TRACK' in (PRODUCT_ROOT / 'README.md').read_text(encoding='utf-8')


def test_readme_has_authorship_footer() -> None:
    text = (PRODUCT_ROOT / 'README.md').read_text(encoding='utf-8')
    assert 'ThomasCory Walker-Pearson' in text
    assert 'GitHub Copilot' in text


def test_run_module_loads() -> None:
    spec = importlib.util.spec_from_file_location('umig_run', PRODUCT_ROOT / 'run.py')
    assert spec is not None and spec.loader is not None


def test_constants_relationship_kcs_sum_of_squares() -> None:
    assert K_CS == 5 ** 2 + 7 ** 2


def test_constants_relationship_ns_in_planck_window() -> None:
    assert CMB_X_RANGE[0] < N_S < CMB_X_RANGE[1]


def test_constants_relationship_r_in_plot_window() -> None:
    assert CMB_Y_RANGE[0] <= R_BRAIDED <= CMB_Y_RANGE[1]


def test_constants_relationship_beta_ordering() -> None:
    assert BETA_FLOOR < BETA_LOW < BETA_FORBIDDEN_LOW < BETA_FORBIDDEN_HIGH < BETA_HIGH < BETA_CEILING


def test_constants_relationship_dm21_monotone_decreasing() -> None:
    assert np.all(np.diff(DM21_TENSIONS) < 0)
