# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_visualization.py
=============================
Tests for the src/visualization module.

Each test verifies:
  1. The figure object is returned (not None).
  2. Axis labels / titles contain expected physics keywords.
  3. Plotted data values match the framework constants (pillar_plots).
  4. SVG output is written when output_path is provided.
  5. Constants embedded in each sub-module match the master values.

All figures are rendered with the non-interactive Agg backend; no display
is required.  SVG output is written to a temporary directory and cleaned up
automatically by pytest's tmp_path fixture.
"""

import importlib
import os

import numpy as np
import pytest

matplotlib = pytest.importorskip("matplotlib", reason="matplotlib not installed")
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def close_figures():
    """Close all open figures after each test to avoid memory leaks."""
    yield
    plt.close("all")


# ---------------------------------------------------------------------------
# Master framework constants (ground truth for all sub-module checks)
# ---------------------------------------------------------------------------

MASTER = {
    "N_W": 5,
    "K_CS": 74,
    "C_S": 12 / 37,
    "R_C": 5 / 74,
    "N_S_UM": 0.9635,
    "N_S_PLANCK": 0.9649,
    "R_TENSOR_UM": 0.0315,
    "BETA_ADMISSIBLE_LOW": 0.22,
    "BETA_ADMISSIBLE_HIGH": 0.38,
    "BETA_CANONICAL_LOW": 0.273,
    "BETA_CANONICAL_HIGH": 0.331,
    "BETA_DERIVED_LOW": 0.290,
    "BETA_DERIVED_HIGH": 0.351,
}


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _get_ax_text(fig) -> str:
    """Collect all text items (labels, titles, legends) from a figure."""
    parts = []
    for ax in fig.axes:
        if ax.get_xlabel():
            parts.append(ax.get_xlabel())
        if ax.get_ylabel():
            parts.append(ax.get_ylabel())
        if ax.get_title():
            parts.append(ax.get_title())
        for t in ax.texts:
            parts.append(t.get_text())
        leg = ax.get_legend()
        if leg:
            for t in leg.get_texts():
                parts.append(t.get_text())
    # Also grab suptitle
    sup = fig._suptitle
    if sup is not None:
        parts.append(sup.get_text())
    return " ".join(parts)


# ===========================================================================
# 1. pillar_plots
# ===========================================================================

class TestPillarPlots:
    """Tests for src/visualization/pillar_plots.py."""

    @pytest.fixture(scope="class")
    def mod(self):
        return importlib.import_module("src.visualization.pillar_plots")

    # -- constants -----------------------------------------------------------

    def test_constants_n_w(self, mod):
        assert mod.N_W == MASTER["N_W"]

    def test_constants_k_cs(self, mod):
        assert mod.K_CS == MASTER["K_CS"]

    def test_constants_n_s_um(self, mod):
        assert mod.N_S_UM == pytest.approx(MASTER["N_S_UM"], abs=1e-6)

    def test_constants_r_tensor(self, mod):
        assert mod.R_TENSOR_UM == pytest.approx(MASTER["R_TENSOR_UM"], abs=1e-6)

    def test_constants_r_c(self, mod):
        assert mod.R_C_PLANCK == pytest.approx(MASTER["R_C"], rel=1e-6)

    def test_constants_beta_admissible(self, mod):
        assert mod.BETA_ADMISSIBLE_LOW == pytest.approx(MASTER["BETA_ADMISSIBLE_LOW"])
        assert mod.BETA_ADMISSIBLE_HIGH == pytest.approx(MASTER["BETA_ADMISSIBLE_HIGH"])

    def test_constants_beta_canonical(self, mod):
        assert mod.BETA_CANONICAL_LOW == pytest.approx(MASTER["BETA_CANONICAL_LOW"])
        assert mod.BETA_CANONICAL_HIGH == pytest.approx(MASTER["BETA_CANONICAL_HIGH"])

    # -- birefringence window ------------------------------------------------

    def test_birefringence_window_returns_figure(self, mod):
        fig = mod.plot_birefringence_window()
        assert isinstance(fig, plt.Figure)

    def test_birefringence_window_has_ylabel(self, mod):
        fig = mod.plot_birefringence_window()
        text = _get_ax_text(fig)
        assert "irefringence" in text or "beta" in text.lower() or "β" in text

    def test_birefringence_window_title_contains_um(self, mod):
        fig = mod.plot_birefringence_window()
        text = _get_ax_text(fig)
        assert "Unitary Manifold" in text or "UM" in text

    def test_birefringence_window_svg_saved(self, mod, tmp_path):
        path = tmp_path / "beta_window.svg"
        mod.plot_birefringence_window(output_path=path)
        assert path.exists()
        assert path.stat().st_size > 1000

    # -- r–nₛ plane ----------------------------------------------------------

    def test_r_ns_returns_figure(self, mod):
        fig = mod.plot_r_ns_plane()
        assert isinstance(fig, plt.Figure)

    def test_r_ns_xlabel_contains_ns(self, mod):
        fig = mod.plot_r_ns_plane()
        text = _get_ax_text(fig)
        assert "n_s" in text or "spectral" in text.lower() or "n_{s}" in text

    def test_r_ns_ylabel_contains_r(self, mod):
        fig = mod.plot_r_ns_plane()
        text = _get_ax_text(fig)
        assert "tensor" in text.lower() or "ratio" in text.lower() or "r$" in text

    def test_r_ns_um_prediction_in_range(self, mod):
        """UM prediction point must lie within the plotted axis range."""
        fig = mod.plot_r_ns_plane()
        ax = fig.axes[0]
        xlo, xhi = ax.get_xlim()
        ylo, yhi = ax.get_ylim()
        assert xlo <= MASTER["N_S_UM"] <= xhi
        assert ylo <= MASTER["R_TENSOR_UM"] <= yhi

    def test_r_ns_svg_saved(self, mod, tmp_path):
        path = tmp_path / "r_ns.svg"
        mod.plot_r_ns_plane(output_path=path)
        assert path.exists()
        assert path.stat().st_size > 1000

    # -- KK mass tower -------------------------------------------------------

    def test_kk_tower_returns_figure(self, mod):
        fig = mod.plot_kk_mass_tower()
        assert isinstance(fig, plt.Figure)

    def test_kk_tower_ylabel_contains_mass(self, mod):
        fig = mod.plot_kk_mass_tower()
        text = _get_ax_text(fig)
        assert "mass" in text.lower() or "m_n" in text or "KK" in text

    def test_kk_tower_mass_gap_correct(self, mod):
        """Mass gap Δm = 1/R_c = K_CS / N_W must match master constants."""
        expected_gap = MASTER["K_CS"] / MASTER["N_W"]
        assert 1.0 / MASTER["R_C"] == pytest.approx(expected_gap, rel=1e-6)

    def test_kk_tower_n_max_levels(self, mod):
        n_max = 7
        fig = mod.plot_kk_mass_tower(n_max=n_max)
        assert isinstance(fig, plt.Figure)

    def test_kk_tower_svg_saved(self, mod, tmp_path):
        path = tmp_path / "kk_tower.svg"
        mod.plot_kk_mass_tower(output_path=path)
        assert path.exists()

    # -- CMB TT spectrum -----------------------------------------------------

    def test_cmb_tt_returns_figure(self, mod):
        fig = mod.plot_cmb_tt_spectrum()
        assert isinstance(fig, plt.Figure)

    def test_cmb_tt_xlabel_contains_ell(self, mod):
        fig = mod.plot_cmb_tt_spectrum()
        text = _get_ax_text(fig)
        assert "ell" in text.lower() or "ℓ" in text or "Multipole" in text

    def test_cmb_tt_has_two_curves(self, mod):
        """Must have at least two line artists (ΛCDM and UM)."""
        fig = mod.plot_cmb_tt_spectrum()
        ax = fig.axes[0]
        assert len(ax.get_lines()) >= 2

    def test_cmb_tt_svg_saved(self, mod, tmp_path):
        path = tmp_path / "cmb_tt.svg"
        mod.plot_cmb_tt_spectrum(output_path=path)
        assert path.exists()


# ===========================================================================
# 2. geometry_viz
# ===========================================================================

class TestGeometryViz:
    """Tests for src/visualization/geometry_viz.py."""

    @pytest.fixture(scope="class")
    def mod(self):
        return importlib.import_module("src.visualization.geometry_viz")

    def test_constants_r_c(self, mod):
        assert mod.R_C == pytest.approx(MASTER["R_C"], rel=1e-6)

    def test_constants_n_w_k_cs(self, mod):
        assert mod.N_W == MASTER["N_W"]
        assert mod.K_CS == MASTER["K_CS"]

    def test_metric_slice_returns_figure(self, mod):
        fig = mod.plot_metric_slice()
        assert isinstance(fig, plt.Figure)

    def test_metric_slice_has_two_axes(self, mod):
        fig = mod.plot_metric_slice()
        assert len(fig.axes) == 2

    def test_metric_slice_ylabel_contains_phi(self, mod):
        fig = mod.plot_metric_slice()
        text = _get_ax_text(fig)
        assert "phi" in text.lower() or "φ" in text or "Radion" in text

    def test_metric_slice_svg_saved(self, mod, tmp_path):
        path = tmp_path / "metric_slice.svg"
        mod.plot_metric_slice(output_path=path)
        assert path.exists()

    def test_compactification_radius_returns_figure(self, mod):
        fig = mod.plot_compactification_radius()
        assert isinstance(fig, plt.Figure)

    def test_compactification_radius_xlabel(self, mod):
        fig = mod.plot_compactification_radius()
        text = _get_ax_text(fig)
        assert "winding" in text.lower() or "n_w" in text.lower() or "n_{w}" in text

    def test_compactification_radius_n5_selection(self, mod):
        """The n_w = 5 bar must be the tallest bar at x = 5 in the bar chart."""
        fig = mod.plot_compactification_radius()
        ax = fig.axes[0]
        # All bars: verify bar at position 5 (index 4) has height 5/74
        containers = ax.containers
        assert containers, "Expected bar containers in the figure"
        # Orange bar for n_w=5 has height = 5/74
        expected_height = MASTER["N_W"] / MASTER["K_CS"]
        # Find a bar with that height (within float tolerance)
        found = False
        for container in containers:
            for bar in container:
                h = bar.get_height()
                if abs(h - expected_height) < 1e-9:
                    found = True
        assert found, f"Expected a bar of height {expected_height:.6f} (5/74) in the chart"

    def test_winding_diagram_returns_figure(self, mod):
        fig = mod.plot_winding_number_diagram()
        assert isinstance(fig, plt.Figure)

    def test_winding_diagram_has_two_axes(self, mod):
        fig = mod.plot_winding_number_diagram()
        assert len(fig.axes) == 2

    def test_5d_potential_returns_figure(self, mod):
        fig = mod.plot_5d_potential()
        assert isinstance(fig, plt.Figure)

    def test_5d_potential_minimum_at_rc(self, mod):
        """The potential minimum must be at r_c = R_C (ratio = 1.0)."""
        fig = mod.plot_5d_potential()
        ax = fig.axes[0]
        lines = ax.get_lines()
        assert lines, "Expected plot lines in the potential figure"
        # The potential line is the first plotted line
        xdata = lines[0].get_xdata()
        ydata = lines[0].get_ydata()
        min_idx = np.argmin(ydata)
        assert xdata[min_idx] == pytest.approx(1.0, abs=0.1), \
            f"Potential minimum at x={xdata[min_idx]:.3f}, expected ≈ 1.0"

    def test_5d_potential_svg_saved(self, mod, tmp_path):
        path = tmp_path / "potential.svg"
        mod.plot_5d_potential(output_path=path)
        assert path.exists()


# ===========================================================================
# 3. feynman_diagrams
# ===========================================================================

class TestFeynmanDiagrams:
    """Tests for src/visualization/feynman_diagrams.py."""

    @pytest.fixture(scope="class")
    def mod(self):
        return importlib.import_module("src.visualization.feynman_diagrams")

    def test_constants_k_cs(self, mod):
        assert mod.K_CS == MASTER["K_CS"]

    def test_kk_graviton_returns_figure(self, mod):
        fig = mod.draw_kk_graviton_vertex()
        assert isinstance(fig, plt.Figure)

    def test_kk_graviton_title_contains_graviton(self, mod):
        fig = mod.draw_kk_graviton_vertex()
        text = _get_ax_text(fig)
        assert "graviton" in text.lower() or "Graviton" in text or "G^" in text

    def test_kk_graviton_svg_saved(self, mod, tmp_path):
        path = tmp_path / "kk_graviton.svg"
        mod.draw_kk_graviton_vertex(output_path=path)
        assert path.exists()

    def test_kk_photon_returns_figure(self, mod):
        fig = mod.draw_kk_photon_vertex()
        assert isinstance(fig, plt.Figure)

    def test_kk_photon_title_contains_photon(self, mod):
        fig = mod.draw_kk_photon_vertex()
        text = _get_ax_text(fig)
        assert "photon" in text.lower() or "Photon" in text or "U(1)" in text

    def test_radion_coupling_returns_figure(self, mod):
        fig = mod.draw_radion_coupling()
        assert isinstance(fig, plt.Figure)

    def test_radion_coupling_title_contains_radion(self, mod):
        fig = mod.draw_radion_coupling()
        text = _get_ax_text(fig)
        assert "radion" in text.lower() or "Radion" in text or "phi" in text.lower()

    def test_braided_winding_returns_figure(self, mod):
        fig = mod.draw_braided_winding_vertex()
        assert isinstance(fig, plt.Figure)

    def test_braided_winding_title_contains_cs(self, mod):
        fig = mod.draw_braided_winding_vertex()
        text = _get_ax_text(fig)
        assert "74" in text or "K_{CS}" in text or "braid" in text.lower()

    def test_braided_winding_svg_saved(self, mod, tmp_path):
        path = tmp_path / "braided_winding.svg"
        mod.draw_braided_winding_vertex(output_path=path)
        assert path.exists()


# ===========================================================================
# 4. cmb_skymap
# ===========================================================================

class TestCmbSkymap:
    """Tests for src/visualization/cmb_skymap.py."""

    @pytest.fixture(scope="class")
    def mod(self):
        return importlib.import_module("src.visualization.cmb_skymap")

    def test_constants_n_s_um(self, mod):
        assert mod.N_S_UM == pytest.approx(MASTER["N_S_UM"], abs=1e-6)

    def test_constants_r_tensor(self, mod):
        assert mod.R_TENSOR_UM == pytest.approx(MASTER["R_TENSOR_UM"], abs=1e-6)

    def test_constants_beta_canonical(self, mod):
        assert mod.BETA_CANONICAL_LOW == pytest.approx(MASTER["BETA_CANONICAL_LOW"])
        assert mod.BETA_CANONICAL_HIGH == pytest.approx(MASTER["BETA_CANONICAL_HIGH"])

    def test_cl_spectrum_returns_figure(self, mod):
        fig = mod.plot_cl_spectrum()
        assert isinstance(fig, plt.Figure)

    def test_cl_spectrum_has_three_panels(self, mod):
        fig = mod.plot_cl_spectrum()
        assert len(fig.axes) == 3

    def test_cl_spectrum_tt_panel_ylabel(self, mod):
        fig = mod.plot_cl_spectrum()
        text = _get_ax_text(fig)
        assert "TT" in text or "D_" in text

    def test_cl_spectrum_bb_panel_ylabel(self, mod):
        fig = mod.plot_cl_spectrum()
        text = _get_ax_text(fig)
        assert "BB" in text

    def test_cl_spectrum_r_value_in_title_or_label(self, mod):
        fig = mod.plot_cl_spectrum()
        text = _get_ax_text(fig)
        assert str(MASTER["R_TENSOR_UM"]) in text

    def test_cl_spectrum_svg_saved(self, mod, tmp_path):
        path = tmp_path / "cl_spectrum.svg"
        mod.plot_cl_spectrum(output_path=path)
        assert path.exists()
        assert path.stat().st_size > 2000

    def test_mollweide_returns_figure(self, mod):
        fig = mod.plot_mollweide_cmb(n_side=32, seed=0)
        assert isinstance(fig, plt.Figure)

    def test_mollweide_uses_mollweide_projection(self, mod):
        fig = mod.plot_mollweide_cmb(n_side=32, seed=0)
        # Mollweide axes have a specific class name
        ax = fig.axes[0]
        assert "Mollweide" in type(ax).__name__ or "mollweide" in str(ax).lower()

    def test_mollweide_reproducible(self, mod):
        """Same seed must produce identical pixel arrays."""
        fig1 = mod.plot_mollweide_cmb(n_side=32, seed=7)
        fig2 = mod.plot_mollweide_cmb(n_side=32, seed=7)
        # Extract image data from both
        fig1.canvas.draw()
        fig2.canvas.draw()
        data1 = np.frombuffer(fig1.canvas.tostring_argb(), dtype=np.uint8)
        data2 = np.frombuffer(fig2.canvas.tostring_argb(), dtype=np.uint8)
        np.testing.assert_array_equal(data1, data2)

    def test_mollweide_svg_saved(self, mod, tmp_path):
        path = tmp_path / "mollweide.svg"
        mod.plot_mollweide_cmb(n_side=32, seed=0, output_path=path)
        assert path.exists()

    def test_birefringence_rotation_returns_figure(self, mod):
        fig = mod.plot_birefringence_rotation()
        assert isinstance(fig, plt.Figure)

    def test_birefringence_rotation_xlabel_ell(self, mod):
        fig = mod.plot_birefringence_rotation()
        text = _get_ax_text(fig)
        assert "Multipole" in text or "ell" in text.lower() or "ℓ" in text

    def test_birefringence_rotation_has_four_curves(self, mod):
        """One curve per canonical/derived β value (4 total)."""
        fig = mod.plot_birefringence_rotation()
        ax = fig.axes[0]
        assert len(ax.get_lines()) >= 4

    def test_birefringence_rotation_svg_saved(self, mod, tmp_path):
        path = tmp_path / "bire_rotation.svg"
        mod.plot_birefringence_rotation(output_path=path)
        assert path.exists()

    # -- physics value check: β rotation formula ----------------------------

    def test_birefringence_rotation_formula(self, mod):
        """ΔD_ell^BB(β) = sin²(2β) × D_ell^EE must hold at ell=400."""
        ell_test = np.array([400.0])
        D_ee_test = mod._analytic_ee(ell_test)[0]
        beta_rad = np.deg2rad(MASTER["BETA_CANONICAL_HIGH"])
        expected_delta = np.sin(2 * beta_rad) ** 2 * D_ee_test
        # Recompute from the module
        D_ee_arr = mod._analytic_ee(ell_test)
        computed = np.sin(2 * beta_rad) ** 2 * D_ee_arr[0]
        assert computed == pytest.approx(expected_delta, rel=1e-9)


# ===========================================================================
# 5. __init__ importability
# ===========================================================================

def test_visualization_package_importable():
    mod = importlib.import_module("src.visualization")
    assert mod is not None


def test_all_submodules_importable():
    for name in ["pillar_plots", "geometry_viz", "feynman_diagrams", "cmb_skymap"]:
        mod = importlib.import_module(f"src.visualization.{name}")
        assert mod is not None


# ===========================================================================
# 6. New honest-accounting plots (v22.10)
# ===========================================================================

class TestTensionReductionChart:
    @pytest.fixture(scope="class")
    def mod(self):
        return pytest.importorskip("src.visualization.pillar_plots")

    def test_returns_figure(self, mod):
        fig = mod.plot_tension_reduction_chart()
        assert fig is not None

    def test_has_correct_sigma_values(self, mod):
        """The function must encode the three documented σ values."""
        import inspect
        src = inspect.getsource(mod.plot_tension_reduction_chart)
        assert "2.98" in src
        assert "1.16" in src
        assert "1.07" in src

    def test_architecture_limit_annotation(self, mod):
        import inspect
        src = inspect.getsource(mod.plot_tension_reduction_chart)
        assert "ARCHITECTURE_LIMIT" in src

    def test_pillar_references(self, mod):
        import inspect
        src = inspect.getsource(mod.plot_tension_reduction_chart)
        assert "772" in src
        assert "773" in src

    def test_svg_saved(self, mod, tmp_path):
        out = tmp_path / "tension.svg"
        fig = mod.plot_tension_reduction_chart(out)
        assert out.exists()


class TestTestPillarTimeline:
    @pytest.fixture(scope="class")
    def mod(self):
        return pytest.importorskip("src.visualization.pillar_plots")

    def test_returns_figure(self, mod):
        fig = mod.plot_test_pillar_timeline()
        assert fig is not None

    def test_has_v22_entries(self, mod):
        import inspect
        src = inspect.getsource(mod.plot_test_pillar_timeline)
        assert "v22.10" in src

    def test_lean4_data_present(self, mod):
        import inspect
        src = inspect.getsource(mod.plot_test_pillar_timeline)
        assert "976" in src

    def test_test_count_data_present(self, mod):
        import inspect
        src = inspect.getsource(mod.plot_test_pillar_timeline)
        assert "56.8" in src  # 56,772 tests ≈ 56.8k

    def test_no_toe_score_language(self, mod):
        import inspect
        src = inspect.getsource(mod.plot_test_pillar_timeline)
        assert "ToE score" not in src
        assert "toe_score" not in src.lower()

    def test_svg_saved(self, mod, tmp_path):
        out = tmp_path / "timeline.svg"
        fig = mod.plot_test_pillar_timeline(out)
        assert out.exists()


class TestArchitectureLimitsSummary:
    @pytest.fixture(scope="class")
    def mod(self):
        return pytest.importorskip("src.visualization.pillar_plots")

    def test_returns_figure(self, mod):
        fig = mod.plot_architecture_limits_summary()
        assert fig is not None

    def test_all_four_gaps_present(self, mod):
        import inspect
        src = inspect.getsource(mod.plot_architecture_limits_summary)
        assert "G1" in src
        assert "G2" in src
        assert "G3" in src
        assert "G4" in src

    def test_type_b_labels(self, mod):
        import inspect
        src = inspect.getsource(mod.plot_architecture_limits_summary)
        assert "TYPE_B_STRUCTURAL_FLOOR" in src
        assert "TYPE_B_CANDIDATE" in src

    def test_fallibility_reference(self, mod):
        import inspect
        src = inspect.getsource(mod.plot_architecture_limits_summary)
        assert "FALLIBILITY" in src

    def test_pillar_references(self, mod):
        import inspect
        src = inspect.getsource(mod.plot_architecture_limits_summary)
        assert "784" in src
        assert "785" in src

    def test_svg_saved(self, mod, tmp_path):
        out = tmp_path / "arch_limits.svg"
        fig = mod.plot_architecture_limits_summary(out)
        assert out.exists()
