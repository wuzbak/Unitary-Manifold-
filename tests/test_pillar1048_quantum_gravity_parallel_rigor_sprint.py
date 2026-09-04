# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1048_quantum_gravity_parallel_rigor_sprint import (
    IMPACT_CLASSES,
    LEAN4_DELTA,
    LEAN4_END,
    LEAN4_START,
    NEXT_PILLAR_SLOT,
    OBSTRUCTION_CODES,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    ROUTE_CLASSES,
    SPRINT_NAME,
    VERSION,
    intake_evidence_table,
    map_result_to_obstructions,
    pillar1048_summary,
    quantum_gravity_parallel_rigor_sprint,
    reproduce_metric_packet,
    route_qg_metric,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1048
    assert PILLAR_STATUS == "QG_PARALLEL_RIGOR_SPRINT_COMPLETE"
    assert PILLAR_VALID is True


def test_metadata() -> None:
    assert VERSION == "v35.6"
    assert SPRINT_NAME == "BZ"
    assert NEXT_PILLAR_SLOT == 1049
    assert LEAN4_END - LEAN4_START == LEAN4_DELTA == 0


def test_intake_evidence_table() -> None:
    report = intake_evidence_table(
        [
            {
                "source": "arXiv:2601.00001",
                "metric": "qg_metric",
                "metric_value": 1.0,
                "uncertainty": 0.1,
            }
        ]
    )
    assert report["n_rows"] == 1
    assert report["traceable"] is True
    assert report["explicit_uncertainty"] is True
    assert report["valid"] is True


def test_obstruction_mapping_classes() -> None:
    mapped = map_result_to_obstructions(
        source="arXiv:2601.00002",
        touched_obstructions=["O1_PERTURBATIVE_EFT_ONLY", "NOT_A_CODE"],
        significance_sigma=2.5,
    )
    assert mapped["touched_obstructions"] == ["O1_PERTURBATIVE_EFT_ONLY"]
    assert mapped["impact"] in IMPACT_CLASSES
    assert mapped["valid"] is True
    assert mapped["impact"] == "TIGHTENS_BOUND"
    assert set(OBSTRUCTION_CODES) == {
        "O1_PERTURBATIVE_EFT_ONLY",
        "O2_NO_UV_MEASURE",
        "O3_NO_BACKGROUND_INDEPENDENCE",
        "O4_NO_TRANSPLANCKIAN_STATES",
    }


def test_reproduction_packet_verdicts() -> None:
    pass_pkt = reproduce_metric_packet("m1", 1.0, 1.05, 0.1, ["a"])
    tension_pkt = reproduce_metric_packet("m2", 1.0, 1.35, 0.1, ["b"])
    falsified_pkt = reproduce_metric_packet("m3", 1.0, 1.7, 0.1, ["c"])
    assert pass_pkt["verdict"] == "PASS"
    assert tension_pkt["verdict"] == "TENSION"
    assert falsified_pkt["verdict"] == "FALSIFIED"


def test_routing_verdicts() -> None:
    pass_pkt = route_qg_metric("QG-1", sigma_from_um=1.5, in_admissible_window=True)
    tension_pkt = route_qg_metric("QG-2", sigma_from_um=2.1, in_admissible_window=True)
    falsified_pkt = route_qg_metric("QG-3", sigma_from_um=3.3, in_admissible_window=False)
    calibrated_pkt = route_qg_metric(
        "QG-4",
        sigma_from_um=0.1,
        in_admissible_window=True,
        hidden_calibration_detected=True,
    )
    assert pass_pkt["verdict"] == "PASS"
    assert tension_pkt["verdict"] == "TENSION"
    assert falsified_pkt["verdict"] == "FALSIFIED"
    assert calibrated_pkt["verdict"] == "FALSIFIED"
    assert all(pkt["verdict"] in ROUTE_CLASSES for pkt in [pass_pkt, tension_pkt, falsified_pkt, calibrated_pkt])


def test_full_sprint_report_definition_of_done() -> None:
    report = quantum_gravity_parallel_rigor_sprint()
    assert report["status"] == PILLAR_STATUS
    assert report["valid"] is True
    assert all(report["definition_of_done"].values())
    assert report["freeze_registry_snapshot"]["freeze_active"] is True


def test_summary() -> None:
    summary = pillar1048_summary()
    assert summary["pillar"] == 1048
    assert summary["status"] == PILLAR_STATUS
    assert summary["version"] == VERSION
    assert summary["next_pillar_slot"] == 1049
