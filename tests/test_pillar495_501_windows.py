from src.core import (
    pillar495_cmb_amplitude_ir_window as p495,
    pillar496_ckm_phase_closure_lane as p496,
    pillar497_desi_dr3_decision_window as p497,
    pillar498_so_dr1_decision_window as p498,
    pillar499_juno_window_sync as p499,
    pillar500_spherex_window_sync as p500,
    pillar501_hllhc_window_sync as p501,
)


def test_pillar_495_structure():
    out = p495.pillar_report()
    assert out["pillar"] == 495
    assert out["result"]["suppression_lo"] < out["result"]["suppression_hi"]


def test_pillar_496_structure():
    out = p496.pillar_report()
    assert out["pillar"] == 496
    assert out["result"]["residual_pct"] < 1.0


def test_decision_windows_active():
    for module, expected in [
        (p497, "DESI DR3"),
        (p498, "SO DR1"),
        (p499, "JUNO"),
        (p500, "SPHEREx"),
        (p501, "HL-LHC"),
    ]:
        out = module.pillar_report()
        assert out["result"]["state"] == "ACTIVE"
        assert out["result"]["experiment"] == expected
