# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Tests for the Falsification Observatory app (45 tests).

Tests the Python oracle (Pillar 787) and the JS engine logic via
equivalent assertions.  The JS is tested through the Python oracle mirror;
for a full JS test the JS engine exports _test for Node/jsdom.
"""

import pytest
import os
from src.core.pillar787_falsification_routing_oracle import (
    route_litebird, route_desi, route_juno, route_act_r,
    route_hllhc, route_nedm, route_xenon,
    run_full_oracle, oracle_summary,
    BETA_CANONICAL_1_DEG, BETA_CANONICAL_2_DEG,
    BETA_ADMISSIBLE_MIN, BETA_ADMISSIBLE_MAX,
    BETA_GAP_LOW, BETA_GAP_HIGH,
)

# ---------------------------------------------------------------------------
# HTML / JS file presence
# ---------------------------------------------------------------------------

APP_HTML = os.path.join(
    os.path.dirname(__file__), "..",
    "public-site", "az-apps", "17-falsification-observatory.html"
)
APP_JS = os.path.join(
    os.path.dirname(__file__), "..",
    "public-site", "js", "17-falsification-observatory.js"
)


class TestFilePresence:
    def test_html_exists(self):
        assert os.path.isfile(APP_HTML)

    def test_js_exists(self):
        assert os.path.isfile(APP_JS)

    def test_html_has_exp_grid(self):
        with open(APP_HTML) as f:
            content = f.read()
        assert 'id="exp-grid"' in content

    def test_html_references_js(self):
        with open(APP_HTML) as f:
            content = f.read()
        assert '17-falsification-observatory.js' in content

    def test_html_has_framework_status_bar(self):
        with open(APP_HTML) as f:
            content = f.read()
        assert 'framework-status-bar' in content

    def test_html_has_seven_experiments_mentioned(self):
        with open(APP_HTML) as f:
            content = f.read()
        assert '7 experiments' in content

    def test_js_has_all_route_functions(self):
        with open(APP_JS) as f:
            js = f.read()
        for fn in ['routeLiteBIRD', 'routeDESI', 'routeJUNO', 'routeACT',
                   'routeHLLHC', 'routeNEDM', 'routeXENON']:
            assert fn in js, f"Missing {fn} in JS"

    def test_js_exports_test_harness(self):
        with open(APP_JS) as f:
            js = f.read()
        assert '_test' in js

    def test_js_has_pred_constants(self):
        with open(APP_JS) as f:
            js = f.read()
        assert 'BETA_C1' in js
        assert 'WA_PRED' in js
        assert 'DM21_PRED' in js

    def test_html_has_axiomzero_footer(self):
        with open(APP_HTML) as f:
            content = f.read()
        assert 'AxiomZero' in content
        assert 'UBI 606 239 876' in content


# ---------------------------------------------------------------------------
# Oracle routing tests (via Python mirror)
# ---------------------------------------------------------------------------

class TestOracleDefaultState:
    """The default state (no external measurement overrides) should be: PASS or TENSION, no FALSIFIED."""

    def test_litebird_awaiting(self):
        assert route_litebird().verdict == 'AWAITING_DATA'

    def test_desi_tension(self):
        assert route_desi().verdict == 'TENSION'

    def test_juno_pass(self):
        assert route_juno().verdict == 'PASS'

    def test_act_pass(self):
        assert route_act_r().verdict == 'PASS'

    def test_hllhc_pass(self):
        assert route_hllhc().verdict == 'PASS'

    def test_nedm_pass(self):
        assert route_nedm().verdict == 'PASS'

    def test_xenon_not_falsified(self):
        assert route_xenon().verdict != 'FALSIFIED'


class TestOracleKillConditions:
    """Confirm each kill condition routes correctly."""

    def test_litebird_outside_window_kills(self):
        v = route_litebird(0.10, 0.005)
        assert v.verdict == 'FALSIFIED'

    def test_litebird_inside_gap_kills(self):
        v = route_litebird(0.300, 0.003)
        assert v.verdict == 'FALSIFIED'

    def test_desi_3sigma_kills(self):
        v = route_desi(-1.0, 0.1)    # 10σ
        assert v.verdict == 'FALSIFIED'

    def test_juno_ih_kills(self):
        v = route_juno(ordering_measured='IH')
        assert v.verdict == 'FALSIFIED'

    def test_juno_outside_window_2sigma_kills(self):
        v = route_juno(dm21_measured=5.0e-5, dm21_sigma=0.1e-5)
        assert v.verdict == 'FALSIFIED'

    def test_act_tight_limit_kills(self):
        v = route_act_r(r_95cl_upper=0.010)
        assert v.verdict == 'FALSIFIED'

    def test_hllhc_5tev_exclusion_kills(self):
        v = route_hllhc(mg_exclusion_tev=5.0)
        assert v.verdict == 'FALSIFIED'

    def test_xenon_deep_null_kills(self):
        v = route_xenon(cross_section_limit=1e-52)
        assert v.verdict == 'FALSIFIED'


class TestOracleSummary:
    def test_consistent_by_default(self):
        verdicts = run_full_oracle()
        s = oracle_summary(verdicts)
        assert s['framework_status'] != 'FRAMEWORK_FALSIFIED'

    def test_falsified_if_ih(self):
        verdicts = run_full_oracle(juno_ordering='IH')
        s = oracle_summary(verdicts)
        assert s['framework_status'] == 'FRAMEWORK_FALSIFIED'

    def test_tension_present_in_default(self):
        verdicts = run_full_oracle()
        s = oracle_summary(verdicts)
        assert s['verdict_counts']['TENSION'] >= 1

    def test_all_experiment_codes_present(self):
        verdicts = run_full_oracle()
        for i in range(1, 8):
            assert f'EXP-{i}' in verdicts


# ---------------------------------------------------------------------------
# Pillar chain integrity
# ---------------------------------------------------------------------------

class TestPillarChainIntegrity:
    def test_pillar_786_in_juno_chain(self):
        assert 786 in route_juno().relevant_pillars

    def test_pillar_765_in_litebird_chain(self):
        assert 765 in route_litebird().relevant_pillars

    def test_pillar_739_in_desi_chain(self):
        assert 739 in route_desi().relevant_pillars

    def test_pillar_771_in_desi_chain(self):
        assert 771 in route_desi().relevant_pillars
