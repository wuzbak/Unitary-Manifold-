from __future__ import annotations

from typing import Dict

PILLAR_NUMBER = 499
PILLAR_STATUS = "JUNO_DECISION_WINDOW_ACTIVE"
PILLAR_TITLE = "JUNO atmospheric splitting decision window synchronization"


def decision_window() -> Dict[str, object]:
    return {
        "experiment": "JUNO",
        "window": "2027",
        "tripwire": "Delta m^2_31 outside NLO envelope",
        "state": "ACTIVE",
    }


def pillar_report() -> Dict[str, object]:
    return {"pillar": PILLAR_NUMBER, "status": PILLAR_STATUS, "title": PILLAR_TITLE, "result": decision_window()}
