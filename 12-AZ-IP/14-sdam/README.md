# SDAM — Software-Defined Acoustic Modem
## Native Android App — Project Blueprint

---

## What It Is

SDAM turns every Android device into a **hardware-independent, RF-invisible
acoustic modem**. The speaker and microphone are the antenna. Sound is the
carrier. No radio layer. No FCC license. No infrastructure.

At the physical layer it is a **frequency-shift keyed (FSK) digital radio**,
running in the 17–22 kHz near-ultrasonic band:

- **Inaudible** — below human comfort threshold, above most noise floor.
- **Room-contained** — does not penetrate thick concrete or shielded walls.
- **Zero hardware cost** — runs on any device with a speaker + mic.
- **Regulatory-free** — sound transmission requires no spectrum license.

---

## The Core Stack

```
┌─────────────────────────────────────────────────────────┐
│                    SDAM Android App                      │
│                                                          │
│  ┌──────────┐   ┌──────────────┐   ┌─────────────────┐  │
│  │  UI/UX   │   │  ViewModel   │   │  Foreground     │  │
│  │  Layer   │◄──│  + State     │◄──│  Service        │  │
│  └──────────┘   └──────────────┘   └────────┬────────┘  │
│                                             │            │
│  ┌──────────────────────────────────────────▼──────────┐ │
│  │              Acoustic Engine (JNI)                  │ │
│  │   ggwave C++ core (arm64-v8a)                       │ │
│  │   AudioRecord (RX) · AudioTrack (TX)                │ │
│  └──────────────────────────────────────────┬──────────┘ │
│                                             │            │
│  ┌──────────────────────────────────────────▼──────────┐ │
│  │              Crypto Layer                           │ │
│  │   AES-256-GCM payload encryption                    │ │
│  │   HMAC-SHA256 session authentication                │ │
│  │   Android Keystore (hardware-backed key storage)    │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Use-Case Hierarchy

### Tier 1 — Encrypted Acoustic Data Diode *(highest value)*

**Target:** SCIFs, nuclear facilities, power plants, air-gapped industrial
control systems.

**Problem it solves:** USB ports glued shut. Wi-Fi physically disabled.
Getting any data out of a secured machine is a manual, slow process.

**How it works:**
1. A secured Windows/Linux machine runs the SDAM transmitter (software only).
2. It "plays" a highly compressed, AES-256-GCM encrypted payload via
   near-ultrasonic audio (17–22 kHz).
3. A Sentinel Android device "hears" it, decrypts it using a key stored in
   the Android Keystore (hardware-bound, non-exportable).
4. The decrypted payload is logged, forwarded, or acted upon.

**Why it wins:**
- No RF emissions — invisible to spectrum analyzers and RF scanners.
- Physically contained — sound doesn't leave the room through thick walls.
- No added hardware — runs on stock endpoints.
- Regulatory gap — acoustic transmission requires no FCC or government license.

### Tier 2 — Secure Industrial Telemetry

Sensor nodes broadcast readings acoustically. Sentinel devices listen and
aggregate. No wiring. No Wi-Fi provisioning. Instant deployment.

### Tier 3 — Cross-Device Mesh / Relay

Phones act as acoustic relay nodes in RF-denied or RF-congested environments.
Message hops through rooms via speaker→mic chains.

### Tier 4 — Consumer / Field Tools

Metal detecting assist, environmental sensing, field comms. These are the
demo-friendly face of the same underlying stack.

---

## Design Principles

1. **Encryption first.** Every payload is encrypted before ggwave encoding.
   Plaintext acoustic payloads exist only in explicit debug mode.
2. **Hardware-bound keys.** Android Keystore. The key never leaves the device.
3. **Frequency agility.** The modem adapts its operating band to the noise floor.
4. **Physically contained.** Near-ultrasonic band by default. Sound stays in
   the room.
5. **Zero infrastructure.** No server. No cloud. No pairing protocol. No Wi-Fi.
6. **Auditable.** Every transmission is logged with timestamp, HMAC tag,
   payload type, and decode success flag.

---

## Repository Layout

```
SDAM/
├── AGENTS.md          ← agent orientation (read first)
├── README.md          ← this file
├── ROADMAP.md         ← phased build plan
├── sessions/          ← per-session handoff notes
└── docs/              ← architecture, security, wire format, calibration
```

The Android Studio project will live in `SDAM/app/` once scaffolded (Phase S1).

---

## Key Dependencies

| Dependency | Source | Purpose |
|---|---|---|
| ggwave | C++ / Android NDK | FSK acoustic encode/decode core |
| Android Keystore | Platform API | Hardware-backed AES-256-GCM key management |
| AudioRecord / AudioTrack | Platform API | Raw PCM audio I/O |
| Hilt | Gradle | Dependency injection |
| Kotlin Coroutines | Gradle | Async audio pipeline |
| Material 3 | Gradle | UI components |

---

## Connections to the Wider Stack

- **`Gibberlink/scripts/`** — Python reference implementation; calibration data
  and protocol constants are authoritative here until the native app supersedes them.
- **`Unitary-Manifold/`** — The acoustic channel is an instance of
  `∇_μ J^μ_inf = 0`: information is never lost, only transformed. ECC in ggwave
  maps directly to the manifold's irreversibility constraint.
- **`BV9900Pro-HomeTest/`** — Primary field test device. Waterproof membrane
  may cause FSK roll-off below ~2 kHz; near-ultrasonic band avoids this.

---

*README.md — SDAM/ — v1.0 — 2026-04-19*
