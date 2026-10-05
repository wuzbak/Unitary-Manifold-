from __future__ import annotations

from typing import Dict

PILLAR_NUMBER = 500
PILLAR_STATUS = "SPHEREX_DECISION_WINDOW_ACTIVE"
PILLAR_TITLE = "SPHEREx primordial non-Gaussianity decision window synchronization"


def decision_window() -> Dict[str, object]:
    return {
        "experiment": "SPHEREx",
        "window": "2027-2028",
        "tripwire": "f_NL fails preregistered range",
        "state": "ACTIVE",
    }


def pillar_report() -> Dict[str, object]:
    return {"pillar": PILLAR_NUMBER, "status": PILLAR_STATUS, "title": PILLAR_TITLE, "result": decision_window()}
