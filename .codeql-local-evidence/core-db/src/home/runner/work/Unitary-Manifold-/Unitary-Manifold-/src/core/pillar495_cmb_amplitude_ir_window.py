from __future__ import annotations

from typing import Dict

PILLAR_NUMBER = 495
PILLAR_STATUS = "CMB_AMPLITUDE_IR_WINDOW_FORMALIZED"
PILLAR_TITLE = "CMB Acoustic Peak Amplitude IR residual window and closure plan"


def cmb_amplitude_window() -> Dict[str, float | str]:
    return {
        "suppression_lo": 4.0,
        "suppression_hi": 7.0,
        "target": 1.0,
        "status": "OPEN_GAP_BOUNDED",
        "next_step": "Integrate 5D EFT transfer-function correction lane",
    }


def pillar_report() -> Dict[str, object]:
    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "title": PILLAR_TITLE,
        "result": cmb_amplitude_window(),
    }
