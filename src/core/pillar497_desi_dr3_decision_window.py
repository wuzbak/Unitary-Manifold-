from __future__ import annotations

from typing import Dict

PILLAR_NUMBER = 497
PILLAR_STATUS = "DESI_DR3_DECISION_WINDOW_ACTIVE"
PILLAR_TITLE = "DESI DR3 decision window synchronization"


def decision_window() -> Dict[str, object]:
    return {
        "experiment": "DESI DR3",
        "window": "2026",
        "tripwire": "w_a significance >= 3 sigma => architecture stress",
        "state": "ACTIVE",
    }


def pillar_report() -> Dict[str, object]:
    return {"pillar": PILLAR_NUMBER, "status": PILLAR_STATUS, "title": PILLAR_TITLE, "result": decision_window()}
