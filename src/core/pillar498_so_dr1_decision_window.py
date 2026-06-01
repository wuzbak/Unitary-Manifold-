from __future__ import annotations

from typing import Dict

PILLAR_NUMBER = 498
PILLAR_STATUS = "SO_DR1_DECISION_WINDOW_ACTIVE"
PILLAR_TITLE = "Simons Observatory DR1 decision window synchronization"


def decision_window() -> Dict[str, object]:
    return {
        "experiment": "SO DR1",
        "window": "2027",
        "tripwire": "r routing thresholds from pillars 442/469",
        "state": "ACTIVE",
    }


def pillar_report() -> Dict[str, object]:
    return {"pillar": PILLAR_NUMBER, "status": PILLAR_STATUS, "title": PILLAR_TITLE, "result": decision_window()}
