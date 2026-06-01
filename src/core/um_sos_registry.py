from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from src.core.pillar394_postulate_minimality_audit import ADMISSIONS
from src.core.pillar435_hllhc_kk_graviton import (
    M_KK_BOUND_TEV,
    PILLAR_NUMBER as P435,
    PILLAR_STATUS as S435,
    PILLAR_TITLE as T435,
    PREREGISTRATION_HASH as H435,
)
from src.core.pillar437_spherex_fnl_preregistration import (
    PILLAR_NUMBER as P437,
    PILLAR_STATUS as S437,
    PILLAR_TITLE as T437,
    PREREGISTRATION_HASH as H437,
)
from src.core.pillar442_so_dr1_routing import PILLAR_STATUS as S442, PREREGISTRATION_HASH as H442
from src.core.pillar467_desi_dr3_falsification_gate import (
    PILLAR_STATUS as S467,
    sha256_preregistration as H467,
)
from src.core.pillar468_litebird_discrimination_protocol import PILLAR_STATUS as S468
from src.core.pillar469_so_dr1_joint_routing import PILLAR_STATUS as S469
from src.core.pillar475_juno_nlo_full_closure import (
    PILLAR_NUMBER as P475,
    PILLAR_STATUS as S475,
    PILLAR_TITLE as T475,
)
from src.core.pillar486_desi_dr3_final_prep import (
    PILLAR_NUMBER as P486,
    PILLAR_STATUS as S486,
    PILLAR_TITLE as T486,
    sha256_preregistration_486 as H486,
)
from src.core.prediction_registry import PREDICTION_REGISTRY


PREREG_PILLARS: List[Dict[str, Any]] = [
    {
        "pillar": P435,
        "title": T435,
        "status": S435,
        "experiment": "HL-LHC Run 4",
        "decision_window": "2029-2033",
        "hash": H435,
        "tripwire": "m_G_KK < 5.0 TeV",
        "prediction_summary": f"Bessel-exact lower bound m_G_KK >= {M_KK_BOUND_TEV:.1f} TeV",
        "source_module": "src/core/pillar435_hllhc_kk_graviton.py",
    },
    {
        "pillar": P437,
        "title": T437,
        "status": S437,
        "experiment": "SPHEREx",
        "decision_window": "2027-2028",
        "hash": H437,
        "tripwire": "f_NL inconsistent with preregistered range",
        "prediction_summary": "Primordial non-Gaussianity f_NL preregistered",
        "source_module": "src/core/pillar437_spherex_fnl_preregistration.py",
    },
    {
        "pillar": 442,
        "title": "SO DR1 routing protocol",
        "status": S442,
        "experiment": "Simons Observatory DR1",
        "decision_window": "2027",
        "hash": H442,
        "tripwire": "r excludes preregistered routing",
        "prediction_summary": "SO DR1 decision routing for tensor-to-scalar ratio",
        "source_module": "src/core/pillar442_so_dr1_routing.py",
    },
    {
        "pillar": 467,
        "title": "DESI DR3 falsification gate",
        "status": S467,
        "experiment": "DESI DR3",
        "decision_window": "2026",
        "hash": H467(),
        "tripwire": "w_a tension exceeds predefined sigma gates",
        "prediction_summary": "DESI DR3 falsification protocol preregistered",
        "source_module": "src/core/pillar467_desi_dr3_falsification_gate.py",
    },
    {
        "pillar": 468,
        "title": "LiteBIRD discrimination protocol",
        "status": S468,
        "experiment": "LiteBIRD",
        "decision_window": "~2032",
        "hash": hashlib.sha256(f"468:{S468}".encode()).hexdigest(),
        "tripwire": "beta in forbidden interval or outside admissible range",
        "prediction_summary": "Birefringence discrimination protocol formalized",
        "source_module": "src/core/pillar468_litebird_discrimination_protocol.py",
    },
    {
        "pillar": 469,
        "title": "SO DR1 joint routing",
        "status": S469,
        "experiment": "Simons Observatory DR1",
        "decision_window": "2027",
        "hash": hashlib.sha256(f"469:{S469}".encode()).hexdigest(),
        "tripwire": "joint r constraints violate SO routing protocol",
        "prediction_summary": "SO DR1 joint-routing formalized",
        "source_module": "src/core/pillar469_so_dr1_joint_routing.py",
    },
    {
        "pillar": P475,
        "title": T475,
        "status": S475,
        "experiment": "JUNO",
        "decision_window": "2027",
        "hash": hashlib.sha256(f"{P475}:{S475}:{T475}".encode()).hexdigest(),
        "tripwire": "Delta m^2_31 outside preregistered NLO band",
        "prediction_summary": "JUNO NLO full-chain safety package",
        "source_module": "src/core/pillar475_juno_nlo_full_closure.py",
    },
    {
        "pillar": P486,
        "title": T486,
        "status": S486,
        "experiment": "DESI DR3",
        "decision_window": "2026",
        "hash": H486(),
        "tripwire": "DR3 one/two-dimensional tension exceeds falsification gates",
        "prediction_summary": "Final DESI DR3 preregistration synchronization package",
        "source_module": "src/core/pillar486_desi_dr3_final_prep.py",
    },
]


def _admissions_payload() -> List[Dict[str, Any]]:
    return [
        {
            "name": rec.name,
            "status": rec.status.value,
            "breaks_if_fails": rec.breaks_if_fails,
            "citation": rec.citation,
            "closed_by": rec.closed_by,
            "used_by": rec.used_by,
        }
        for rec in ADMISSIONS
    ]


def export_registry() -> Dict[str, Any]:
    entries = sorted(PREREG_PILLARS, key=lambda x: x["pillar"])
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "schema_version": "1.0.0",
        "registry_kind": "um_sos_preregistration_registry",
        "entry_count": len(entries),
        "entries": entries,
        "admissions": _admissions_payload(),
        "prediction_registry_size": len(PREDICTION_REGISTRY),
    }


def write_registry_json(output_path: str | Path) -> Path:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = export_registry()
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out
