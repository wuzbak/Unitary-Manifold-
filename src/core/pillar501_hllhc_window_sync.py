from __future__ import annotations

from typing import Dict

PILLAR_NUMBER = 501
PILLAR_STATUS = "HLLHC_DECISION_WINDOW_ACTIVE"
PILLAR_TITLE = "HL-LHC KK graviton decision window synchronization"


def decision_window() -> Dict[str, object]:
    return {
        "experiment": "HL-LHC",
        "window": "2029-2033",
        "tripwire": "m_G_KK observed below 5 TeV",
        "state": "ACTIVE",
    }


def pillar_report() -> Dict[str, object]:
    return {"pillar": PILLAR_NUMBER, "status": PILLAR_STATUS, "title": PILLAR_TITLE, "result": decision_window()}
