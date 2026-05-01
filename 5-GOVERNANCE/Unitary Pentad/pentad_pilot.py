#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/pentad_pilot.py
================================
Pentad Pilot Node (PPN-1) — real-time Human-in-the-Loop Pentad interface.

You are Body 3 — the Human Intent Layer (Ψ_human).
You steer the simulation via keyboard or physical hardware knobs.

Usage
-----
Phase 0 — software only (any computer, free):

    python pentad_pilot.py

Phase 1–3 — with Arduino hardware panel:

    python pentad_pilot.py --port /dev/ttyUSB0    (Linux / Mac)
    python pentad_pilot.py --port COM3             (Windows)
    python pentad_pilot.py --port auto             (auto-detect)

Use --no-curses if the display looks garbled (e.g. some Windows terminals):

    python pentad_pilot.py --no-curses

Keyboard controls (Phase 0 / fallback)
---------------------------------------
    UP   / +   Increase Trust Field φ_trust
    DOWN / -   Decrease Trust Field φ_trust
    RIGHT/ ]   Increase Human Intent φ_human  (you push harder)
    LEFT / [   Decrease Human Intent φ_human  (you pull back)
    SPACE      Reset to canonical initial conditions
    R          Inject adversarial intent (Malicious Precision test)
    Q / ESC    Quit

What to look for
----------------
1. At start-up the five bodies converge — watch DEFECT drop toward 0.
2. Turn the Trust knob (or press DOWN) below 0.1 — all bodies decouple
   instantly: TRUST EROSION collapse.
3. Push Human Intent (RIGHT) far past 1.0 — MALICIOUS PRECISION fires:
   trust is intact but intent is adversarial.
4. HARMONIC STATE ✓ appears when all 10 pairwise gaps and phases are near 0.
"""


from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}

import argparse
import math
import os
import sys
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

# ── Path setup ──────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_ROOT, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── Pentad imports ──────────────────────────────────────────────────────────
from unitary_pentad import (
    PentadSystem,
    PentadLabel,
    PENTAD_LABELS,
    BRAIDED_SOUND_SPEED,
    TRUST_PHI_MIN,
    trust_modulation,
    pentad_pairwise_gaps,
    pentad_pairwise_phases,
    pentad_defect,
    step_pentad,
)
from pentad_scenarios import (
    harmonic_state_metrics,
    detect_collapse_mode,
    CollapseMode,
    PHASE_REVERSAL_THRESHOLD,
)
from src.consciousness.coupled_attractor import ManifoldState

# ── Optional serial ──────────────────────────────────────────────────────────
try:
    import serial
    import serial.tools.list_ports
    HAS_SERIAL: bool = True
except ImportError:
    HAS_SERIAL = False

# ── Optional curses ──────────────────────────────────────────────────────────
try:
    import curses as _curses_mod
    HAS_CURSES: bool = True
except ImportError:
    HAS_CURSES = False

# ── Simulation parameters ────────────────────────────────────────────────────
STEP_DT:    float = 0.05   # physics pseudo-timestep per tick
TICK_SLEEP: float = 0.05   # wall-clock seconds between simulation ticks
TRUST_STEP: float = 0.05   # trust knob step per keypress
HUMAN_STEP: float = 0.05   # human intent step per keypress
PHI_MIN:    float = 0.01   # minimum φ clamp
PHI_MAX:    float = 1.50   # maximum φ clamp

# ── Body display metadata ────────────────────────────────────────────────────
BODY_NAMES: Dict[str, str] = {
    PentadLabel.UNIV:  "UNIV  (Universe) ",
    PentadLabel.BRAIN: "BRAIN (Biology)  ",
    PentadLabel.HUMAN: "HUMAN (You)      ",
    PentadLabel.AI:    "AI    (Precision)",
    PentadLabel.TRUST: "TRUST (Coupling) ",
}
BODY_SYMBOLS: Dict[str, str] = {
    PentadLabel.UNIV:  "◉",
    PentadLabel.BRAIN: "◎",
    PentadLabel.HUMAN: "★",
    PentadLabel.AI:    "◆",
    PentadLabel.TRUST: "♥",
}
# LED index for Arduino (0–4 in PENTAD_LABELS order)
BODY_LED_IDX: Dict[str, int] = {lbl: i for i, lbl in enumerate(PENTAD_LABELS)}


# ── Shared state ─────────────────────────────────────────────────────────────

@dataclass
class PilotState:
    """Mutable pilot state shared between the simulation thread and display."""
    system:           PentadSystem
    step:             int   = 0
    defect:           float = 1.0
    max_gap:          float = 1.0
    max_phase:        float = math.pi
    trust_val:        float = 0.9
    human_val:        float = 0.6
    collapse_mode:    str   = CollapseMode.NONE
    collapse_severity: float = 0.0
    is_harmonic:      bool  = False
    hardware_connected: bool = False
    last_error:       str   = ""
    running:          bool  = True
    lock: threading.Lock    = field(default_factory=threading.Lock)


# ── φ injection helpers ──────────────────────────────────────────────────────

def _clamp(val: float) -> float:
    return float(np.clip(val, PHI_MIN, PHI_MAX))


def _set_body_phi(state: PilotState, label: str, new_phi: float) -> None:
    """Replace a body's φ value in the simulation (caller holds the lock)."""
    old = state.system.bodies[label]
    state.system.bodies[label] = ManifoldState(
        node=old.node,
        phi=new_phi,
        n1=old.n1,
        n2=old.n2,
        k_cs=old.k_cs,
        label=old.label,
    )


def inject_trust(state: PilotState, delta: float) -> None:
    with state.lock:
        new_phi = _clamp(state.trust_val + delta)
        state.trust_val = new_phi
        _set_body_phi(state, PentadLabel.TRUST, new_phi)


def inject_human(state: PilotState, delta: float) -> None:
    with state.lock:
        new_phi = _clamp(state.human_val + delta)
        state.human_val = new_phi
        _set_body_phi(state, PentadLabel.HUMAN, new_phi)


def reset_system(state: PilotState) -> None:
    with state.lock:
        state.system = PentadSystem.default()
        state.step = 0
        state.trust_val = state.system.bodies[PentadLabel.TRUST].phi
        state.human_val = state.system.bodies[PentadLabel.HUMAN].phi


# ── Simulation thread ────────────────────────────────────────────────────────

def _sim_thread(state: PilotState, arduino: Optional[object]) -> None:
    """Step the Pentad simulation continuously and update diagnostics."""
    # -----------------------------------------------------------------------
    # PENTAD PRODUCT POLICY v1.0 — AxiomZero Technologies
    # The HILS Pentad is a protected AxiomZero product currently in active
    # development.  This function's implementation is held in a private
    # AxiomZero repository.  See PENTAD_PRODUCT_NOTICE.md for details and
    # instructions on how to obtain access.
    # -----------------------------------------------------------------------
    raise NotImplementedError(
        "_sim_thread() is part of the AxiomZero Pentad product layer, "
        "currently in active development.  "
        "See PENTAD_PRODUCT_NOTICE.md."
    )


def _send_led_brightness(state: PilotState, arduino: object) -> None:
    """Map each body's φ to LED brightness and send to Arduino."""
    # -----------------------------------------------------------------------
    # PENTAD PRODUCT POLICY v1.0 — AxiomZero Technologies
    # The HILS Pentad is a protected AxiomZero product currently in active
    # development.  This function's implementation is held in a private
    # AxiomZero repository.  See PENTAD_PRODUCT_NOTICE.md for details and
    # instructions on how to obtain access.
    # -----------------------------------------------------------------------
    raise NotImplementedError(
        "_send_led_brightness() is part of the AxiomZero Pentad product layer, "
        "currently in active development.  "
        "See PENTAD_PRODUCT_NOTICE.md."
    )


# ── Arduino thread ───────────────────────────────────────────────────────────

def _arduino_thread(state: PilotState, arduino: object) -> None:
    """Read pot values from Arduino and inject directly into the simulation."""
    # -----------------------------------------------------------------------
    # PENTAD PRODUCT POLICY v1.0 — AxiomZero Technologies
    # The HILS Pentad is a protected AxiomZero product currently in active
    # development.  This function's implementation is held in a private
    # AxiomZero repository.  See PENTAD_PRODUCT_NOTICE.md for details and
    # instructions on how to obtain access.
    # -----------------------------------------------------------------------
    raise NotImplementedError(
        "_arduino_thread() is part of the AxiomZero Pentad product layer, "
        "currently in active development.  "
        "See PENTAD_PRODUCT_NOTICE.md."
    )


# ── Display helpers ──────────────────────────────────────────────────────────

def _bar(val: float, maxval: float, width: int = 20,
         fill: str = "█", empty: str = "░") -> str:
    frac = max(0.0, min(1.0, val / max(maxval, 1e-9)))
    n    = int(frac * width)
    return fill * n + empty * (width - n)


_RST  = "\033[0m"
_BOLD = "\033[1m"
_DIM  = "\033[2m"
_RED  = "\033[91m"
_GRN  = "\033[92m"
_YLW  = "\033[93m"
_CYN  = "\033[96m"
_WHT  = "\033[97m"


def _phi_color(phi: float) -> str:
    if phi >= 0.7:
        return _GRN
    if phi >= 0.3:
        return _YLW
    return _RED


# ── Simple print-based display (no curses) ───────────────────────────────────

def _simple_display_frame(state: PilotState) -> None:
    """Print a single snapshot of the Pentad state to stdout."""
    # -----------------------------------------------------------------------
    # PENTAD PRODUCT POLICY v1.0 — AxiomZero Technologies
    # The HILS Pentad is a protected AxiomZero product currently in active
    # development.  This function's implementation is held in a private
    # AxiomZero repository.  See PENTAD_PRODUCT_NOTICE.md for details and
    # instructions on how to obtain access.
    # -----------------------------------------------------------------------
    raise NotImplementedError(
        "_simple_display_frame() is part of the AxiomZero Pentad product layer, "
        "currently in active development.  "
        "See PENTAD_PRODUCT_NOTICE.md."
    )


def _simple_loop_unix(state: PilotState) -> None:
    """Keyboard loop using termios (Linux / macOS)."""
    # -----------------------------------------------------------------------
    # PENTAD PRODUCT POLICY v1.0 — AxiomZero Technologies
    # The HILS Pentad is a protected AxiomZero product currently in active
    # development.  This function's implementation is held in a private
    # AxiomZero repository.  See PENTAD_PRODUCT_NOTICE.md for details and
    # instructions on how to obtain access.
    # -----------------------------------------------------------------------
    raise NotImplementedError(
        "_simple_loop_unix() is part of the AxiomZero Pentad product layer, "
        "currently in active development.  "
        "See PENTAD_PRODUCT_NOTICE.md."
    )


def _simple_loop_windows(state: PilotState) -> None:
    """Keyboard loop using msvcrt (Windows without curses)."""
    # -----------------------------------------------------------------------
    # PENTAD PRODUCT POLICY v1.0 — AxiomZero Technologies
    # The HILS Pentad is a protected AxiomZero product currently in active
    # development.  This function's implementation is held in a private
    # AxiomZero repository.  See PENTAD_PRODUCT_NOTICE.md for details and
    # instructions on how to obtain access.
    # -----------------------------------------------------------------------
    raise NotImplementedError(
        "_simple_loop_windows() is part of the AxiomZero Pentad product layer, "
        "currently in active development.  "
        "See PENTAD_PRODUCT_NOTICE.md."
    )


# ── Curses display ───────────────────────────────────────────────────────────

def _curses_loop(stdscr: object, state: PilotState) -> None:
    """Full-featured curses display and keyboard loop."""
    # -----------------------------------------------------------------------
    # PENTAD PRODUCT POLICY v1.0 — AxiomZero Technologies
    # The HILS Pentad is a protected AxiomZero product currently in active
    # development.  This function's implementation is held in a private
    # AxiomZero repository.  See PENTAD_PRODUCT_NOTICE.md for details and
    # instructions on how to obtain access.
    # -----------------------------------------------------------------------
    raise NotImplementedError(
        "_curses_loop() is part of the AxiomZero Pentad product layer, "
        "currently in active development.  "
        "See PENTAD_PRODUCT_NOTICE.md."
    )


# ── Arduino connection ───────────────────────────────────────────────────────

def _connect_arduino(port: str) -> Optional[object]:
    """Return a serial.Serial connection or None."""
    # -----------------------------------------------------------------------
    # PENTAD PRODUCT POLICY v1.0 — AxiomZero Technologies
    # The HILS Pentad is a protected AxiomZero product currently in active
    # development.  This function's implementation is held in a private
    # AxiomZero repository.  See PENTAD_PRODUCT_NOTICE.md for details and
    # instructions on how to obtain access.
    # -----------------------------------------------------------------------
    raise NotImplementedError(
        "_connect_arduino() is part of the AxiomZero Pentad product layer, "
        "currently in active development.  "
        "See PENTAD_PRODUCT_NOTICE.md."
    )


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    # -----------------------------------------------------------------------
    # PENTAD PRODUCT POLICY v1.0 — AxiomZero Technologies
    # The HILS Pentad is a protected AxiomZero product currently in active
    # development.  This function's implementation is held in a private
    # AxiomZero repository.  See PENTAD_PRODUCT_NOTICE.md for details and
    # instructions on how to obtain access.
    # -----------------------------------------------------------------------
    raise NotImplementedError(
        "main() is part of the AxiomZero Pentad product layer, "
        "currently in active development.  "
        "See PENTAD_PRODUCT_NOTICE.md."
    )


if __name__ == "__main__":
    main()
