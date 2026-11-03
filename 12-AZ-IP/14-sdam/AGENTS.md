# AGENTS.md — SDAM Project Orientation
## `wuzbak/diary/SDAM/`

Read this before every session that touches SDAM work.

---

## 1 · What This Project Is

**SDAM** = Software-Defined Acoustic Modem.

The core idea: use a device's speaker and microphone as an acoustic data
channel. The app does not use RF as its message carrier, but it does not
disable phone radios, guarantee RF silence, or establish a regulatory
exemption.

This folder is the **primary build workspace** for the native Android
(and eventually cross-platform) SDAM application. It is the successor to the
Python Gibberlink exploration stack and the Android PHASE A9 scaffold.
The Android implementation is in development and is not release-ready.

---

## 2 · Relationship to Other Projects

| Project | Role |
|---|---|
| `Gibberlink/` | Research workspace — Python scripts, acoustic protocol experiments |
| `Android/` | Deployment guide + integration bridge for all Android work |
| `BV9900Pro-HomeTest/` | Intended physical validation device; results are not verified |
| `S24Ultra/` | Intended validation device; results are not verified |
| `Unitary-Manifold/` | Theoretical context; the connection to this acoustic protocol is conceptual |
| **`SDAM/`** | **Development workspace for the native SDAM app** |

SDAM does not replace Gibberlink — it consumes it. The Python scripts in
`Gibberlink/scripts/` remain the reference implementation and testing ground.
The SDAM Android app is the intended native application; build, device, and
cross-device key-provisioning validation remain incomplete.

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
| **Android Keystore** | Key storage API; hardware backing depends on device and is not verified |
| **Foreground Service** | Required for uninterrupted background mic capture |
| **AES-256-GCM payload encryption** | AEAD — integrity + confidentiality in one pass |
| **Acoustic protocol selection** | User-selectable ggwave protocols; stored default is `ULTRASOUND_FAST`, with spectrum, audibility, range, and containment unverified |
| **HMAC-SHA256 authentication** | SDAM1 frames use 96-bit tags and an in-memory replay high-water mark (not restart-resistant); legacy AcousticAuth retains its 32-bit wire tag |

---

## 5 · Use-Case Hierarchy (Highest Value First)

1. **Encrypted Acoustic Data Diode** — design target for isolated systems.
   Cross-device key provisioning, hardware-backed keys, and acoustic
   containment are not verified; the phone may still emit RF.
2. **Secure Industrial Telemetry** — sensor → acoustic → Sentinel. No wiring.
3. **Cross-Device Mesh Node** — phones as acoustic relays in RF-denied zones.
4. **Consumer Sensing / Field Tool** — metal detecting, environmental sensing.

Always build toward use case 1. Consumer features are a side effect.

---

## 6 · What Must Never Break

- Never commit a key, token, or secret. Android Keystore only.
- Never alter ggwave encoding parameters without a calibration note in the
  session log. Parameter drift silently breaks cross-device decoding.
- Encryption (AES-256-GCM) must wrap every production payload before ggwave
  encoding. Plaintext is only permitted in the explicit in-app debug mode.
- Tests must pass before any push. Never remove existing tests.
- The BV9900Pro is an intended validation device, not a validated production
  field device. ADB commands must be read-only or `--dry-run` unless explicitly
  confirmed in the session note.

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
