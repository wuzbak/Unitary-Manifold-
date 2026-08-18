# AGENTS.md — SDAM Project Orientation
## `wuzbak/diary/SDAM/`

Read this before every session that touches SDAM work.

---

## 1 · What This Project Is

**SDAM** = Software-Defined Acoustic Modem.

The core idea: treat every speaker and microphone on Earth as a wireless data
port. No radio layer. No Wi-Fi. No Bluetooth. No cellular. No FCC license.
Sound is the carrier. The app is the modem.

This folder is the **primary build workspace** for the native Android
(and eventually cross-platform) SDAM application. It is the successor to the
Python Gibberlink exploration stack and the Android PHASE A9 scaffold.

---

## 2 · Relationship to Other Projects

| Project | Role |
|---|---|
| `Gibberlink/` | Research workspace — Python scripts, acoustic protocol experiments |
| `Android/` | Deployment guide + integration bridge for all Android work |
| `BV9900Pro-HomeTest/` | Physical test hardware (field device) |
| `S24Ultra/` | Daily-driver test device |
| `Unitary-Manifold/` | Theoretical framework — `∇_μ J^μ_inf = 0` |
| **`SDAM/`** | **Production build workspace for the native SDAM app** |

SDAM does not replace Gibberlink — it consumes it. The Python scripts in
`Gibberlink/scripts/` remain the reference implementation and testing ground.
The SDAM app is the productized, hardened, native version of that stack.

---

## 3 · Orientation Order

1. Read this file.
2. Read `README.md` — full architecture, use-case hierarchy, design decisions.
3. Read `ROADMAP.md` — phased build plan (S0–S6+).
4. Read the latest session note in `sessions/SESSION_NNN.md`.
5. For acoustic protocol details → `Gibberlink/AGENTS.md`.
6. For hardware test context → `BV9900Pro-HomeTest/COLLABORATION.md`.

---

## 4 · Key Technical Decisions (Locked)

| Decision | Rationale |
|---|---|
| **ggwave C++ core via Android NDK** | Proven FSK library; arm64-v8a target; JNI wrapper |
| **AudioRecord / AudioTrack** | Native Android audio APIs; replaces PyAudio |
| **Android Keystore** | Hardware-backed key storage; replaces `.env` secrets |
| **Foreground Service** | Required for uninterrupted background mic capture |
| **AES-256-GCM payload encryption** | AEAD — integrity + confidentiality in one pass |
| **Near-ultrasonic frequency band** | 17–22 kHz default; inaudible, physically room-contained |
| **HMAC-SHA256 session auth** | Rolling counter; prevents replay of recorded chirps |

---

## 5 · Use-Case Hierarchy (Highest Value First)

1. **Encrypted Acoustic Data Diode** — air-gap bridge for SCIFs / critical
   infrastructure. Hardware-bound decrypt key. Near-ultrasonic. No RF.
2. **Secure Industrial Telemetry** — sensor → acoustic → Sentinel. No wiring.
3. **Cross-Device Mesh Node** — phones as acoustic relays in RF-denied zones.
4. **Consumer Sensing / Field Tool** — metal detecting, environmental sensing.

Always build toward use case 1. Consumer features are a side effect.

---

## 6 · What Must Never Break

- Never commit a key, token, or secret. Android Keystore only.
- Never alter ggwave encoding parameters without a calibration note in the
  session log. Parameter drift silently breaks cross-device decoding.
- Encryption (AES-256-GCM) must wrap every payload before ggwave encoding.
  Plaintext acoustic payloads are only permitted in explicit `--debug` mode.
- Tests must pass before any push. Never remove existing tests.
- The BV9900Pro is a production field device. ADB commands must be
  read-only or `--dry-run` unless explicitly confirmed in the session note.

---

## 7 · Session Handoff Protocol

Every session closes with a session note at:
`SDAM/sessions/SESSION_NNN.md`

The note must contain:
- What was built / changed
- What was tested and the results
- Any open blockers
- Exact next step (one sentence)

---

*AGENTS.md — SDAM/ — v1.0 — 2026-04-19*
