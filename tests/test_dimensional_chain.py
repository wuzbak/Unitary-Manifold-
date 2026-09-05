# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""tests/test_dimensional_chain.py
==================================
Tests for src/core/dimensional_reduction_chain.py.

Covers:
  - All 7 individual chain link functions (structural + numerical)
  - dimensional_chain_audit() overall verdict
  - Parameter propagation consistency
  - Formal theorem strings present and non-empty
"""

import math
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.dimensional_reduction_chain import (
    K_CS,
    N_W,
    N_C,
    PI_KR,
    N_FLUX,
    N_GEN,
    CHAIN_CLOSED_TOL,
    chain_link_11d_to_10d,
    chain_link_10d_to_9d,
    chain_link_9d_to_8d,
    chain_link_8d_to_7d,
    chain_link_7d_to_6d,
    chain_link_6d_to_5d,
    chain_link_5d_block_structure,
    dimensional_chain_audit,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_k_cs_value(self):
        assert K_CS == 74

    def test_k_cs_topological(self):
        assert K_CS == 5 ** 2 + 7 ** 2

    def test_n_w(self):
        assert N_W == 5

    def test_n_c(self):
        assert N_C == 3

    def test_pi_kr(self):
        assert abs(PI_KR - 37.0) < 1e-10

    def test_n_flux(self):
        assert N_FLUX == 37

    def test_n_flux_eq_k_cs_over_2(self):
        assert N_FLUX == K_CS // 2

    def test_n_gen(self):
        assert N_GEN == 3


# ---------------------------------------------------------------------------
# Link 1: 11D → 10D
# ---------------------------------------------------------------------------

class TestLink11Dto10D:
    def setup_method(self):
        self.result = chain_link_11d_to_10d()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_link_name(self):
        assert "11D" in self.result["link"]

    def test_predicted_n_flux(self):
        assert self.result["predicted_N_FLUX"] == N_FLUX

    def test_residual_zero(self):
        assert self.result["residual"] == 0.0

    def test_label_closed(self):
        assert self.result["label"] == "CHAIN_CLOSED"

    def test_quantity_to_next_has_n_flux(self):
        assert self.result["quantity_to_next"]["N_FLUX"] == N_FLUX

    def test_s1_z2_confirmed(self):
        assert self.result["quantity_to_next"]["S1_Z2_confirmed"] is True


# ---------------------------------------------------------------------------
# Link 2: 10D → 9D
# ---------------------------------------------------------------------------

class TestLink10Dto9D:
    def setup_method(self):
        self.result = chain_link_10d_to_9d()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_gauge_dimension(self):
        assert self.result["gauge_dimension"] == 496

    def test_residual_zero(self):
        assert self.result["residual"] == 0.0

    def test_label_closed(self):
        assert self.result["label"] == "CHAIN_CLOSED"

    def test_gs_counterterm_present(self):
        assert self.result["gs_counterterm_present"] is True


# ---------------------------------------------------------------------------
# Link 3: 9D → 8D
# ---------------------------------------------------------------------------

class TestLink9Dto8D:
    def setup_method(self):
        self.result = chain_link_9d_to_8d()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_predicted_n_c(self):
        assert self.result["predicted_N_c"] == N_C

    def test_alpha_gut_perturbative(self):
        alpha = self.result["alpha_gut"]
        assert 0 < alpha < 1

    def test_alpha_gut_value(self):
        assert abs(self.result["alpha_gut"] - N_C / K_CS) < 1e-12

    def test_residual_zero(self):
        assert self.result["residual"] == 0.0

    def test_label_closed(self):
        assert self.result["label"] == "CHAIN_CLOSED"

    def test_su3_selected(self):
        assert self.result["quantity_to_next"]["SU3_selected"] is True


# ---------------------------------------------------------------------------
# Link 4: 8D → 7D
# ---------------------------------------------------------------------------

class TestLink8Dto7D:
    def setup_method(self):
        self.result = chain_link_8d_to_7d()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_delta_cp_range(self):
        # PDG: 69.2° ± 3.3°; UM: ~68.7°
        assert 60.0 <= self.result["delta_cp_predicted_deg"] <= 80.0

    def test_residual_small(self):
        # < 1% residual for CHAIN_CLOSED
        assert self.result["residual"] < CHAIN_CLOSED_TOL

    def test_label_closed(self):
        assert self.result["label"] == "CHAIN_CLOSED"

    def test_physical_content_non_empty(self):
        assert len(self.result["physical_content"]) > 20


# ---------------------------------------------------------------------------
# Link 5: 7D → 6D
# ---------------------------------------------------------------------------

class TestLink7Dto6D:
    def setup_method(self):
        self.result = chain_link_7d_to_6d()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_predicted_n_gen(self):
        assert self.result["predicted_N_gen"] == N_GEN

    def test_residual_zero(self):
        assert self.result["residual"] == 0.0

    def test_label_closed(self):
        assert self.result["label"] == "CHAIN_CLOSED"

    def test_quantity_to_next(self):
        assert self.result["quantity_to_next"]["N_gen"] == 3


# ---------------------------------------------------------------------------
# Link 6: 6D → 5D
# ---------------------------------------------------------------------------

class TestLink6Dto5D:
    def setup_method(self):
        self.result = chain_link_6d_to_5d()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_block_structure_correct(self):
        assert self.result["block_structure_correct"] is True

    def test_g55_eq_phi_sq(self):
        assert self.result["G55_eq_phi_sq"] is True

    def test_gmu5_eq_lam_phi_squared_bmu(self):
        assert self.result["Gmu5_eq_lam_phi_sq_Bmu"] is True
        assert self.result["Gmu5_eq_lam_phi_Bmu"] is False

    def test_assembly_is_not_parameter_selection(self):
        assert self.result["no_new_free_parameters"] is False
        assert self.result["physical_derivation_established"] is False
        assert self.result["quantity_to_next"]["assembly_inputs"] == ["g", "B", "phi", "lambda"]

    def test_assembly_exception_fails_closed(self, monkeypatch):
        def fail(*args, **kwargs):
            raise RuntimeError("assembly unavailable")
        monkeypatch.setattr("src.core.metric.assemble_5d_metric", fail)
        result = chain_link_6d_to_5d()
        assert result["block_structure_correct"] is False
        assert result["label"] == "CHAIN_OPEN"
        assert result["error"] == "assembly unavailable"

    def test_old_phi_linear_assembly_is_rejected(self, monkeypatch):
        from src.core.metric import assemble_5d_metric
        def incorrect(g, B, phi, lam):
            result = assemble_5d_metric(g, B, phi, lam)
            result[:, :4, 4] = lam*phi[:, None]*B
            result[:, 4, :4] = lam*phi[:, None]*B
            return result
        monkeypatch.setattr("src.core.metric.assemble_5d_metric", incorrect)
        result = chain_link_6d_to_5d()
        assert result["block_structure_correct"] is False
        assert result["label"] == "CHAIN_OPEN"

    def test_label_closed(self):
        assert self.result["label"] == "CHAIN_CLOSED"

    def test_parameter_list(self):
        params = self.result["quantity_to_next"]["parameters"]
        assert "K_CS" in params
        assert "n_w" in params
        assert "N_c" in params


# ---------------------------------------------------------------------------
# Link 7: 5D terminal
# ---------------------------------------------------------------------------

class TestLink5DTerminal:
    def setup_method(self):
        self.result = chain_link_5d_block_structure()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_k_cs_topological(self):
        assert self.result["K_CS_topological"] is True

    def test_n_w_aps(self):
        assert self.result["n_w_aps_selected"] is True

    def test_pi_kr_consistent(self):
        assert self.result["pi_kr_consistent"] is True

    def test_n_gen_geometric(self):
        assert self.result["N_gen_geometric"] is True

    def test_n_c_holonomy(self):
        assert self.result["N_c_holonomy"] is True

    def test_all_pass(self):
        assert self.result["all_pass"] is True

    def test_label_closed(self):
        assert self.result["label"] == "CHAIN_CLOSED"


# ---------------------------------------------------------------------------
# Master audit
# ---------------------------------------------------------------------------

class TestDimensionalChainAudit:
    def setup_method(self):
        self.result = dimensional_chain_audit()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_has_links(self):
        assert "links" in self.result
        assert len(self.result["links"]) == 7

    def test_all_closed(self):
        assert self.result["n_open"] == 0
        assert self.result["n_tension"] == 0

    def test_chain_status_fully_closed(self):
        assert self.result["chain_status"] == "CHAIN_FULLY_CLOSED"

    def test_theorem_non_empty(self):
        assert len(self.result["theorem"]) > 50

    def test_parameters_propagated(self):
        params = self.result["parameters_propagated"]
        assert params["K_CS"] == K_CS
        assert params["n_w"] == N_W
        assert params["N_c"] == N_C
        assert params["N_gen"] == N_GEN
        assert abs(params["pi_kr"] - PI_KR) < 1e-10
        assert params["N_FLUX"] == N_FLUX

    def test_n_closed_equals_7(self):
        assert self.result["n_closed"] == 7
