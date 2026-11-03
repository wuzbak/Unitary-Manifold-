# SDAM — Software-Defined Acoustic Modem
## Native Android App — Project Blueprint

---

## What It Is

SDAM is an Android application designed to send encrypted data through a
device's built-in speaker and microphone. Its audio link is acoustic rather
than an application-level radio link; it does not make the phone RF-invisible,
silence other radios, or provide a regulatory exemption.

### Current Android implementation status

The Android project now contains a native ggwave v0.4.2/JNI codec, Android
AudioRecord/AudioTrack I/O, and a secure text path: AES-GCM encryption,
countered HMAC-SHA256 frame encoding (96-bit / 24 lowercase hex chars),
acoustic transmit, decoded-frame authentication,
and decrypt/error reporting. If the native library is not packaged, the app
reports audio as unavailable and does not record a successful transmission.
Standard/Secure messages use the distinct `MSG:<id>:<seq>:<total>:` fragment
header and compact base64url-encoded AES-GCM data, independently encrypted per
fragment before the authenticated SDAM1 frame is sent. They support up to
4,995 UTF-8 bytes (999 fragments of at most
5 UTF-8 bytes; multibyte-heavy text may hit the fragment-count limit earlier).
Each generic message has a random 32-bit grouping ID; a newly observed ID
starts a separate reassembly window. DIODE retains its
backward-compatible `DIODE` wire prefix, 8-byte chunks, and separate
7,992 UTF-8 byte limit. Neither mode provides a delivery receipt: the sender
reports frames queued and the receiver reports success only after complete
authenticated reassembly.
The older AcousticAuth handshake keeps its separate 32-bit/8-hex tag format
for wire compatibility; that legacy tag is not used to authenticate SDAM1
message frames.
JVM tests cover deterministic frame encoding, AES-GCM round-trip and tamper
rejection, HMAC verification, same-verifier replay rejection, and the native
payload limit. The replay high-water mark is in memory only; a process restart
resets it, so SDAM1 replay rejection is not restart-resistant.
They do not emulate audio hardware. Speaker/microphone
loopback, range, frequency response, and cross-device key provisioning remain
unvalidated; separate devices cannot communicate securely until they share
compatible keys through a real provisioning flow.

At the physical layer it uses ggwave's **frequency-shift keyed (FSK) acoustic
codec**. The current stored default selects a high-frequency protocol
(`ULTRASOUND_FAST`); audible protocols are also selectable. The actual emitted
spectrum, human audibility, and frequency response have not been measured on
target devices, so the protocol label is not a safety or containment guarantee.

The near-ultrasonic, room-containment, stock-device compatibility, and
regulatory properties described by this product are design goals, not verified
guarantees. They require device-specific acoustic and regulatory validation.

---

## The Core Stack

```
┌─────────────────────────────────────────────────────────┐
│                    SDAM Android App                      │
│                                                          │
│  ┌──────────┐   ┌──────────────┐   ┌─────────────────┐  │
│  │  UI/UX   │   │  ViewModel   │   │  Foreground     │  │
│  │  Layer   │◄──│  + State     │◄──│ Service (planned)│  │
│  └──────────┘   └──────────────┘   └────────┬────────┘  │
│                                             │            │
│  ┌──────────────────────────────────────────▼──────────┐ │
│  │              Acoustic Engine (JNI)                  │ │
│  │   Vendored ggwave C++ core (build unverified)         │ │
│  │   AudioRecord (RX) · AudioTrack (TX)                │ │
│  └──────────────────────────────────────────┬──────────┘ │
│                                             │            │
│  ┌──────────────────────────────────────────▼──────────┐ │
│  │              Crypto Layer                           │ │
│  │   AES-256-GCM payload encryption                    │ │
│  │   HMAC-SHA256 session authentication                │ │
│  │   Android Keystore (hardware backing varies)          │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Use-Case Hierarchy

### Tier 1 — Encrypted Acoustic Data Diode *(design target; not deployment-ready)*

**Target:** SCIFs, nuclear facilities, power plants, air-gapped industrial
control systems. These are potential evaluation environments, not approved
or validated deployments.

**Problem it solves:** USB ports glued shut. Wi-Fi physically disabled.
Getting any data out of a secured machine is a manual, slow process.

**How it works:**
1. A compatible endpoint runs a transmitter that implements the SDAM wire
   protocol and uses a key shared with the Android receiver.
2. It plays an AES-256-GCM encrypted payload using a selected ggwave audio
   protocol; near-ultrasonic range, compression, and endpoint compatibility
   have not been validated.
3. An Android device decodes and decrypts it using a key stored through the
   Android Keystore API; hardware backing depends on the device and is not
   verified by this project.
4. The decrypted payload is logged, forwarded, or acted upon.

**Operational limits:**
- The acoustic data path does not intentionally transmit over RF, but the
  phone's radios and electronics may still emit RF.
- Sound can be audible, recorded, or transmitted through walls and structure;
  room containment has not been measured.
- The Android application does not implement a working cross-device key
  provisioning flow, so separate installs cannot currently establish secure
  communication by themselves.
- No regulatory or facility-approval conclusion is made; deployment requires
  independent device, acoustic, security, and jurisdiction-specific review.

### Tier 2 — Secure Industrial Telemetry

Potential future use: sensor nodes could broadcast readings acoustically for
compatible receivers. Sensor interfaces and telemetry aggregation are not
implemented.

### Tier 3 — Cross-Device Mesh / Relay

Potential future use: phones could relay acoustic messages in RF-constrained
environments. Relay routing and cross-device operation are not implemented.

### Tier 4 — Consumer / Field Tools

Metal detecting assist, environmental sensing, field comms. These are the
demo-friendly face of the same underlying stack.

These tiers describe intended applications, not currently delivered
capabilities. The implemented source path is encrypted/authenticated text;
sensor integration, relay behavior, cross-device key provisioning, native
Android packaging, and device-level acoustic performance are not validated.

---

## Design Principles

1. **Encryption first.** Standard, Secure, and DIODE payloads use AES-GCM
   before acoustic transmission. Plaintext is available only in explicit
   debug mode.
2. **Keystore API.** Keys are managed through Android Keystore; hardware
   backing and non-exportability have not been verified across devices.
3. **Protocol selection.** The UI exposes ggwave protocol choices; automatic
   noise-floor adaptation is not implemented.
4. **No containment guarantee.** Frequency response, audibility, and
   transmission through structures require device-specific measurement.
5. **Local transport.** The audio link needs no network server, but secure
   peer provisioning is not implemented and cross-device use requires shared
   compatible keys.
6. **Visible status.** The app keeps a bounded in-memory UI log of message,
   mode, timestamp, and status. It does not expose HMAC tags or provide a
   durable audit log.

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

The Android Studio project lives in `SDAM/app/`; native build and device validation status are tracked in `ROADMAP.md`.

---

## Key Dependencies

| Dependency | Source | Purpose |
|---|---|---|
| ggwave | Vendored C++ / Android NDK + JNI | FSK acoustic encode/decode core; hardware behavior still requires device validation |
| Android Keystore | Platform API | AES-256-GCM key management; hardware backing depends on device and has not been verified |
| AudioRecord / AudioTrack | Platform API | Raw PCM audio I/O |
| Hilt | Gradle | Dependency injection |
| Kotlin Coroutines | Gradle | Async audio pipeline |
| Material 3 | Gradle | UI components |

---

## Connections to the Wider Stack

- **`Gibberlink/scripts/`** — Python reference implementation; calibration data
  and protocol constants are authoritative here until the native app supersedes them.
- **`Unitary-Manifold/`** — The project uses the framework as conceptual
  context; no validated derivation connects its equations to this acoustic
  protocol or ggwave's error-correction behavior.
- **`BV9900Pro-HomeTest/`** — Intended physical validation device. Its
  waterproof membrane may affect acoustic response, but no frequency-response
  measurement or protocol workaround has been validated.
- **`public-site/az-apps/15-pentacorder.html`** — Browser companion that
  implements a real (simplified, single-tone-per-nibble FSK) acoustic
  transmit/decode link over `Web Audio API` oscillators and an `AnalyserNode`,
  alongside the Pentacorder field-sensor channels. It is a working proof of
  the acoustic channel for anyone without the native Android build — not a
  replacement for the full OFDM stack documented above.

---

*README.md — SDAM/ — v1.0 — 2026-04-19*
