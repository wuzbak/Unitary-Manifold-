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
    while state.running:
        try:
            with state.lock:
                state.system     = step_pentad(state.system, dt=STEP_DT)
                state.step      += 1
                state.defect     = pentad_defect(state.system)
                gaps             = pentad_pairwise_gaps(state.system)
                phases           = pentad_pairwise_phases(state.system)
                state.max_gap    = max(gaps.values())
                state.max_phase  = max(phases.values())
                state.trust_val  = trust_modulation(state.system)
                state.human_val  = state.system.bodies[PentadLabel.HUMAN].phi

                csig                  = detect_collapse_mode(state.system)
                state.collapse_mode   = csig.mode
                state.collapse_severity = csig.severity

                metrics          = harmonic_state_metrics(state.system)
                state.is_harmonic = metrics.is_harmonic

                # Send brightness to Arduino if connected
                if arduino is not None:
                    _send_led_brightness(state, arduino)

        except Exception as exc:
            with state.lock:
                state.last_error = str(exc)[:80]

        time.sleep(TICK_SLEEP)


def _send_led_brightness(state: PilotState, arduino: object) -> None:
    """Map each body's φ to LED brightness and send to Arduino."""
    try:
        for lbl in PENTAD_LABELS:
            phi        = state.system.bodies[lbl].phi
            brightness = int(np.clip(phi / PHI_MAX * 255, 0, 255))
            idx        = BODY_LED_IDX[lbl]
            arduino.write(f"B {idx} {brightness}\n".encode())
    except Exception as exc:
        state.last_error = f"Arduino write: {exc}"[:80]


# ── Arduino thread ───────────────────────────────────────────────────────────

def _arduino_thread(state: PilotState, arduino: object) -> None:
    """Read pot values from Arduino and inject directly into the simulation."""
    buf = ""
    while state.running:
        try:
            if arduino.in_waiting:
                buf += arduino.read(arduino.in_waiting).decode(errors="replace")
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    line = line.strip()
                    if line.startswith("P "):
                        parts = line.split()
                        if len(parts) >= 3:
                            try:
                                trust_pot = float(parts[1])   # 0.0 – 1.0
                                human_pot = float(parts[2])   # 0.0 – 1.0
                            except ValueError:
                                state.last_error = (
                                    f"Bad pot data from Arduino: {line!r:.60s}"
                                )
                                continue
                            trust_phi = PHI_MIN + trust_pot * (PHI_MAX - PHI_MIN)
                            human_phi = PHI_MIN + human_pot * (PHI_MAX - PHI_MIN)
                            with state.lock:
                                _set_body_phi(state, PentadLabel.TRUST, trust_phi)
                                _set_body_phi(state, PentadLabel.HUMAN, human_phi)
                                state.trust_val = trust_phi
                                state.human_val = human_phi
        except Exception as exc:
            state.last_error = f"Arduino read: {exc}"[:80]
        time.sleep(0.05)


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
    os.system("cls" if os.name == "nt" else "clear")
    W = 72

    # Header
    harmonic_str = f"{_GRN}✓ HARMONIC STATE{_RST}" if state.is_harmonic \
                   else f"{_YLW}converging...{_RST}"
    print(f"{_BOLD}{'═' * W}{_RST}")
    print(f"{_BOLD}  PENTAD PILOT NODE (PPN-1)   Step {state.step:6d}   "
          f"{harmonic_str}{_RST}")
    print(f"{'═' * W}")

    # Collapse warning
    if state.collapse_mode != CollapseMode.NONE:
        sev     = state.collapse_severity
        sev_bar = _bar(sev, 1.0, 20, "▓", "░")
        print(f"\n  {_RED}{_BOLD}⚠  COLLAPSE: {state.collapse_mode}"
              f"   [{sev_bar}] {sev:.2f}{_RST}")

    # Body table
    print(f"\n  {'BODY':<22}  {'φ':>6}  {'BAR':20}  STATUS")
    print(f"  {'─' * 22}  {'─' * 6}  {'─' * 20}  {'─' * 10}")
    for lbl in PENTAD_LABELS:
        phi    = state.system.bodies[lbl].phi
        col    = _phi_color(phi)
        sym    = BODY_SYMBOLS[lbl]
        name   = BODY_NAMES[lbl]
        bar    = _bar(phi, PHI_MAX, 20)
        if lbl == PentadLabel.HUMAN:
            status = f"{_CYN}← YOU{_RST}"
        elif lbl == PentadLabel.TRUST:
            status = f"{_RED}ERODED{_RST}" if phi < TRUST_PHI_MIN \
                     else (f"{_YLW}LOW{_RST}" if phi < 0.3 else f"{_GRN}OK{_RST}")
        else:
            status = f"{_GRN}STABLE{_RST}" if phi >= 0.5 else f"{_YLW}DRIFTING{_RST}"
        print(f"  {sym} {name}  {col}{phi:6.3f}{_RST}  {col}{bar}{_RST}  {status}")

    # Metrics
    print(f"\n  DEFECT:    {state.defect:12.6f}   (< 1e-6 = fixed point)")
    print(f"  MAX GAP:   {state.max_gap:12.6f}   (→ 0 at Harmonic State)")
    print(f"  MAX PHASE: {state.max_phase:8.4f} rad   "
          f"(π/2 = {PHASE_REVERSAL_THRESHOLD:.4f} = reversal threshold)")
    print(f"  TRUST φ:   {trust_modulation(state.system):10.4f}   "
          f"(floor = {TRUST_PHI_MIN})")

    # Control bars
    print(f"\n  Trust  : [{_GRN}{_bar(state.trust_val, PHI_MAX, 28)}{_RST}]"
          f"  {state.trust_val:.3f}")
    print(f"  Human φ: [{_CYN}{_bar(state.human_val, PHI_MAX, 28)}{_RST}]"
          f"  {state.human_val:.3f}")

    if state.hardware_connected:
        print(f"\n  {_GRN}● Hardware connected (LED panel active){_RST}")
    if state.last_error:
        print(f"  {_RED}Error: {state.last_error}{_RST}")

    print(f"\n  {'─' * 68}")
    print(f"  [↑/+] Trust UP   [↓/-] Trust DOWN   "
          f"[→/]] Human UP   [←/[] Human DOWN")
    print(f"  [SPACE] Reset    [R] Adversarial intent    [Q/ESC] Quit")
    print(f"{'═' * W}")


def _simple_loop_unix(state: PilotState) -> None:
    """Keyboard loop using termios (Linux / macOS)."""
    import select
    import termios
    import tty

    fd  = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while state.running:
            with state.lock:
                _simple_display_frame(state)

            rlist, _, _ = select.select([sys.stdin], [], [], 0.12)
            if not rlist:
                continue
            ch = sys.stdin.read(1)
            if ch in ("q", "Q", "\x1b"):
                # ESC or Q — may be start of arrow key sequence
                rlist2, _, _ = select.select([sys.stdin], [], [], 0.02)
                if rlist2:
                    seq = sys.stdin.read(2)
                    if   seq == "[A":  inject_trust(state,  TRUST_STEP)   # UP
                    elif seq == "[B":  inject_trust(state, -TRUST_STEP)   # DOWN
                    elif seq == "[C":  inject_human(state,  HUMAN_STEP)   # RIGHT
                    elif seq == "[D":  inject_human(state, -HUMAN_STEP)   # LEFT
                    # other escape sequences ignored
                else:
                    # plain ESC or Q
                    state.running = False
            elif ch in ("+", "="):  inject_trust(state,  TRUST_STEP)
            elif ch in ("-", "_"):  inject_trust(state, -TRUST_STEP)
            elif ch in ("]", "."):  inject_human(state,  HUMAN_STEP)
            elif ch in ("[", ","):  inject_human(state, -HUMAN_STEP)
            elif ch == " ":         reset_system(state)
            elif ch in ("r", "R"):  inject_human(state, 0.7)  # adversarial
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _simple_loop_windows(state: PilotState) -> None:
    """Keyboard loop using msvcrt (Windows without curses)."""
    import msvcrt

    KEY_MAP = {
        b"+": (inject_trust,  TRUST_STEP),
        b"=": (inject_trust,  TRUST_STEP),
        b"-": (inject_trust, -TRUST_STEP),
        b"_": (inject_trust, -TRUST_STEP),
        b"]": (inject_human,  HUMAN_STEP),
        b".": (inject_human,  HUMAN_STEP),
        b"[": (inject_human, -HUMAN_STEP),
        b",": (inject_human, -HUMAN_STEP),
    }

    while state.running:
        with state.lock:
            _simple_display_frame(state)

        time.sleep(0.12)
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch in (b"q", b"Q", b"\x1b"):
                state.running = False
            elif ch in KEY_MAP:
                fn, delta = KEY_MAP[ch]
                fn(state, delta)
            elif ch == b" ":
                reset_system(state)
            elif ch in (b"r", b"R"):
                inject_human(state, 0.7)
            elif ch == b"\xe0":           # Windows arrow-key prefix
                ch2 = msvcrt.getch()
                if   ch2 == b"H": inject_trust(state,  TRUST_STEP)  # UP
                elif ch2 == b"P": inject_trust(state, -TRUST_STEP)  # DOWN
                elif ch2 == b"M": inject_human(state,  HUMAN_STEP)  # RIGHT
                elif ch2 == b"K": inject_human(state, -HUMAN_STEP)  # LEFT


# ── Curses display ───────────────────────────────────────────────────────────

def _curses_loop(stdscr: object, state: PilotState) -> None:
    """Full-featured curses display and keyboard loop."""
    import curses

    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(60)

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN,  -1)   # healthy / harmonic
    curses.init_pair(2, curses.COLOR_YELLOW, -1)   # warning
    curses.init_pair(3, curses.COLOR_RED,    -1)   # danger / collapse
    curses.init_pair(4, curses.COLOR_CYAN,   -1)   # human body
    curses.init_pair(5, curses.COLOR_WHITE,  -1)   # neutral
    curses.init_pair(6, curses.COLOR_BLUE,   -1)   # universe body

    GRN  = curses.color_pair(1)
    YLW  = curses.color_pair(2)
    RED  = curses.color_pair(3)
    CYN  = curses.color_pair(4)
    WHT  = curses.color_pair(5)
    BLU  = curses.color_pair(6)
    BOLD = curses.A_BOLD
    DIM  = curses.A_DIM

    BODY_CPAIRS = {
        PentadLabel.UNIV:  BLU | BOLD,
        PentadLabel.BRAIN: GRN,
        PentadLabel.HUMAN: CYN | BOLD,
        PentadLabel.AI:    WHT,
        PentadLabel.TRUST: RED,
    }

    def _phi_cpair(phi: float) -> int:
        if phi >= 0.7: return GRN
        if phi >= 0.3: return YLW
        return RED

    while state.running:
        key = stdscr.getch()

        if   key in (ord("q"), ord("Q"), 27):   state.running = False; break
        elif key in (curses.KEY_UP,   ord("+"), ord("=")):  inject_trust(state,  TRUST_STEP)
        elif key in (curses.KEY_DOWN, ord("-"), ord("_")):  inject_trust(state, -TRUST_STEP)
        elif key in (curses.KEY_RIGHT,ord("]"), ord(".")): inject_human(state,  HUMAN_STEP)
        elif key in (curses.KEY_LEFT, ord("["), ord(",")):  inject_human(state, -HUMAN_STEP)
        elif key == ord(" "):                               reset_system(state)
        elif key in (ord("r"), ord("R")):                  inject_human(state, 0.7)

        # Take a snapshot under the lock
        with state.lock:
            snap = {
                "step":     state.step,
                "defect":   state.defect,
                "max_gap":  state.max_gap,
                "max_phase":state.max_phase,
                "harmonic": state.is_harmonic,
                "collapse": state.collapse_mode,
                "severity": state.collapse_severity,
                "trust":    state.trust_val,
                "human":    state.human_val,
                "trust_eff":trust_modulation(state.system),
                "phis":     {lbl: state.system.bodies[lbl].phi
                             for lbl in PENTAD_LABELS},
                "hw":       state.hardware_connected,
                "err":      state.last_error,
            }

        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()

        def _safe(row: int, col: int, text: str, attr: int = 0) -> None:
            if row < max_y and col < max_x:
                try:
                    stdscr.addstr(row, col, text[:max_x - col - 1], attr)
                except curses.error:
                    pass

        row = 0
        _safe(row, 0, "═" * min(72, max_x - 1), WHT | BOLD); row += 1
        _safe(row, 0,
              f"  PENTAD PILOT NODE (PPN-1)   Step {snap['step']:6d}   ",
              WHT | BOLD)
        if snap["harmonic"]:
            _safe(row, 50, "✓ HARMONIC STATE", GRN | BOLD)
        else:
            _safe(row, 50, "converging...", YLW)
        row += 1
        _safe(row, 0, "═" * min(72, max_x - 1), WHT | BOLD); row += 1

        if snap["collapse"] != CollapseMode.NONE:
            sev_bar = _bar(snap["severity"], 1.0, 18, "▓", "░")
            _safe(row, 0,
                  f"  ⚠  COLLAPSE: {snap['collapse']}   [{sev_bar}] {snap['severity']:.2f}",
                  RED | BOLD)
            row += 1
        row += 1

        _safe(row, 0, f"  {'BODY':<22}  {'φ':>6}  {'BAR':20}  STATUS", DIM); row += 1
        _safe(row, 0, f"  {'─'*22}  {'─'*6}  {'─'*20}  {'─'*10}", DIM);     row += 1

        for lbl in PENTAD_LABELS:
            phi  = snap["phis"][lbl]
            col  = BODY_CPAIRS[lbl]
            hcol = _phi_cpair(phi)
            sym  = BODY_SYMBOLS[lbl]
            name = BODY_NAMES[lbl]
            bar  = _bar(phi, PHI_MAX, 20)

            if lbl == PentadLabel.HUMAN:
                status = "← YOU   "; hcol = CYN
            elif lbl == PentadLabel.TRUST and phi < TRUST_PHI_MIN:
                status = "ERODED! "; hcol = RED | BOLD
            elif phi >= 0.5:
                status = "STABLE  "
            else:
                status = "DRIFTING"

            _safe(row, 0, f"  {sym} {name}  ", col)
            _safe(row, 26, f"{phi:6.3f}  ", hcol | BOLD)
            _safe(row, 34, bar + "  ", hcol)
            _safe(row, 56, status, hcol)
            row += 1

        row += 1
        mc = GRN if snap["harmonic"] else YLW
        _safe(row, 0,
              f"  DEFECT: {snap['defect']:12.6f}   MAX GAP: {snap['max_gap']:.6f}", mc)
        row += 1
        _safe(row, 0,
              f"  MAX PHASE: {snap['max_phase']:8.4f} rad   "
              f"TRUST φ: {snap['trust_eff']:.4f}  (floor={TRUST_PHI_MIN})", mc)
        row += 2

        _safe(row, 0, "  Trust  : [", WHT)
        _safe(row, 12, _bar(snap["trust"], PHI_MAX, 28), GRN)
        _safe(row, 40, f"] {snap['trust']:.3f}", WHT)
        row += 1
        _safe(row, 0, "  Human φ: [", WHT)
        _safe(row, 12, _bar(snap["human"], PHI_MAX, 28), CYN)
        _safe(row, 40, f"] {snap['human']:.3f}", WHT)
        row += 2

        if snap["hw"]:
            _safe(row, 0, "  ● Hardware connected (LED panel active)", GRN); row += 1
        if snap["err"]:
            _safe(row, 0, f"  Error: {snap['err']}", RED); row += 1

        row += 1
        _safe(row, 0, "─" * min(70, max_x - 1), DIM); row += 1
        _safe(row, 0,
              "  [↑+] Trust UP  [↓-] Trust DOWN  [→]] Human UP  [←[] Human DOWN", DIM)
        row += 1
        _safe(row, 0, "  [SPACE] Reset  [R] Adversarial intent  [Q/ESC] Quit", DIM)
        stdscr.refresh()


# ── Arduino connection ───────────────────────────────────────────────────────

def _connect_arduino(port: str) -> Optional[object]:
    """Return a serial.Serial connection or None."""
    if not HAS_SERIAL:
        print("Note: pyserial not installed.  Run:  pip install pyserial")
        return None

    if port == "auto":
        ports = list(serial.tools.list_ports.comports())
        candidates = [
            p.device for p in ports
            if any(kw in (p.description or "").lower()
                   for kw in ("arduino", "ch340", "ch341", "usb serial"))
        ]
        if not candidates:
            candidates = [p.device for p in ports]
        if not candidates:
            print("No serial ports detected.")
            return None
        port = candidates[0]
        print(f"Auto-detected port: {port}")

    try:
        conn = serial.Serial(port, 9600, timeout=1)
        time.sleep(2.0)   # allow Arduino reset
        return conn
    except Exception as exc:
        print(f"Cannot connect to {port}: {exc}")
        return None


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pentad Pilot Node (PPN-1) — Human-in-the-Loop Pentad interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--port", default=None,
        help="Serial port for Arduino hardware (e.g. COM3, /dev/ttyUSB0, 'auto')",
    )
    parser.add_argument(
        "--no-curses", action="store_true",
        help="Use simple print-based display instead of curses",
    )
    args = parser.parse_args()

    # ── Hardware connection ──────────────────────────────────────────────────
    arduino: Optional[object] = None
    if args.port:
        arduino = _connect_arduino(args.port)

    # ── Initial state ────────────────────────────────────────────────────────
    state = PilotState(system=PentadSystem.default())
    if arduino is not None:
        state.hardware_connected = True

    # ── Simulation thread ────────────────────────────────────────────────────
    sim_t = threading.Thread(target=_sim_thread, args=(state, arduino), daemon=True)
    sim_t.start()

    # ── Arduino read thread ──────────────────────────────────────────────────
    if arduino is not None:
        ard_t = threading.Thread(
            target=_arduino_thread, args=(state, arduino), daemon=True
        )
        ard_t.start()

    # ── Display loop ─────────────────────────────────────────────────────────
    use_curses = HAS_CURSES and not args.no_curses
    try:
        if use_curses:
            import curses as _c
            _c.wrapper(lambda s: _curses_loop(s, state))
        elif os.name == "nt":
            _simple_loop_windows(state)
        else:
            _simple_loop_unix(state)
    except KeyboardInterrupt:
        pass
    finally:
        state.running = False
        if arduino is not None:
            try:
                arduino.close()
            except Exception:
                pass
        print("\nPentad Pilot Node stopped.  Goodbye.")


if __name__ == "__main__":
    main()
