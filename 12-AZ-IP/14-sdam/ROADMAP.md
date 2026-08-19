# ROADMAP.md — SDAM Project
## Phased build plan: Software-Defined Acoustic Modem (Native Android)

---

## PHASE S0 — Project Scaffold ✅ (SESSION_001)

Goal: Clean folder, orientation docs, and a clear build plan in place.

- [x] `SDAM/AGENTS.md` — agent orientation
- [x] `SDAM/README.md` — architecture blueprint + use-case hierarchy
- [x] `SDAM/ROADMAP.md` — this file
- [x] `SDAM/sessions/` — session handoff directory
- [x] `SDAM/docs/` — technical reference directory

---

## PHASE S1 — Android Studio Project + JNI Shell

Goal: A buildable Android Studio project with the ggwave C++ core linked in
and a minimal "ping/pong" round-trip working end-to-end in the emulator.

- [ ] Scaffold Android Studio project
  - Min SDK: 26 (Android 8.0)
  - Target SDK: 35 (Android 15)
  - Language: Kotlin
  - Build: Kotlin DSL (build.gradle.kts)
  - DI: Hilt
- [ ] Add ggwave as a git submodule or CMake ExternalProject
  - Build target: `arm64-v8a` (primary), `x86_64` (emulator)
  - Output: `libggwave.so`
- [ ] Write JNI wrapper: `GgwaveJni.kt` + `ggwave_jni.cpp`
  - `ggwaveEncode(payload: ByteArray, protocol: Int, volume: Int): ShortArray`
  - `ggwaveDecode(pcm: ShortArray): ByteArray?`
- [ ] `AudioEngine.kt` — AudioRecord RX + AudioTrack TX wrappers
  - Sample rate: 48000 Hz (matches ggwave default)
  - Channel: MONO
  - Encoding: PCM_16BIT
- [ ] Smoke test: encode "HELLO" → play → record → decode → assert "HELLO"
  - Pass on emulator (x86_64)
  - Pass on BV9900Pro (arm64-v8a)
  - Pass on S24 Ultra (arm64-v8a)

---

## PHASE S2 — Crypto Layer + Android Keystore Integration

Goal: Every payload encrypted before it enters ggwave. Key never leaves device.

- [ ] `CryptoEngine.kt` — AES-256-GCM via Android Keystore
  - `generateKey(alias: String)` — creates hardware-backed key entry
  - `encrypt(alias: String, plaintext: ByteArray): EncryptedPayload`
  - `decrypt(alias: String, payload: EncryptedPayload): ByteArray`
  - `EncryptedPayload` = (iv: 12 bytes) + (ciphertext + tag: n+16 bytes)
- [ ] HMAC-SHA256 session authentication layer
  - Rolling counter per session (replay prevention)
  - 4-byte truncated HMAC tag appended to every ggwave frame
  - Matches wire format defined in `Gibberlink/docs/SECURITY.md`
- [ ] Key provisioning flow:
  - QR code scan OR near-field acoustic handshake to share session secret
  - Secret stored in Android Keystore, never in SharedPreferences or disk
- [ ] Smoke test: encrypt "SECRET DATA" → encode → play → record → decode →
  decrypt → assert "SECRET DATA"
- [ ] Verify key is not extractable (Android Keystore `setIsStrongBoxBacked(true)`)

---

## PHASE S3 — Foreground Service + Background Decode Loop

Goal: App listens continuously even when backgrounded. No missed packets.

- [ ] `AcousticModemService.kt` — Android Foreground Service
  - Persistent notification: "SDAM Sentinel — listening"
  - Starts `AudioEngine` RX loop on service start
  - Broadcasts decoded payloads via `LocalBroadcastManager`
  - Handles `START_LISTENING` / `STOP_LISTENING` intents
- [ ] `DecodePipeline.kt` — sliding PCM window → ggwave decode → crypto verify
  - 1024-sample sliding window at 48 kHz = ~21 ms resolution
  - On successful decode: HMAC verify → AES decrypt → emit to ViewModel
  - On HMAC failure: log tamper event, discard frame
- [ ] Battery optimisation: release `AudioRecord` on screen-off if no active
  session (configurable via settings)
- [ ] Test: background decode while screen off, device in pocket (BV9900Pro + S24)

---

## PHASE S4 — Frequency Agility + Noise Floor Calibration

Goal: Modem auto-selects the cleanest frequency band for the environment.

- [ ] `NoiseProfiler.kt` — ambient FFT snapshot
  - 4096-point FFT over 1-second audio window
  - Outputs per-band SNR map (0–24 kHz in 100 Hz bins)
  - Detects BV9900Pro waterproof membrane roll-off
- [ ] `FrequencySelector.kt` — band picker
  - Preferred band: 17–22 kHz (near-ultrasonic, inaudible)
  - Fallback band: 1–4 kHz (audible; field use when ultrasonic blocked)
  - Selects ggwave protocol enum (0–5) based on SNR map
- [ ] `CalibrationProfile.kt` — saves/loads device-specific profile
  - Stored in encrypted SharedPreferences
  - Matches format of `Gibberlink/experiments/calibration.json`
- [ ] Auto-calibrate on first launch and on environment change (>3 dB SNR shift)
- [ ] Manual calibration: "Calibrate" button in settings → plays chirp sweep →
  saves profile

---

## PHASE S5 — Material 3 UI

Goal: Clean, functional interface for all use cases.

- [ ] Bottom navigation: 4 tabs
  - **Transmit** — compose + send encrypted payload
  - **Receive** — live decode feed + audit log
  - **Calibrate** — noise floor + frequency band picker
  - **Settings** — key management, mode, protocol, volume
- [ ] **Transmit screen**
  - Text input + payload type selector (GPS / SYS / ENV / VITALS / ALERT / RAW)
  - Mode selector: GREEN (passive) / RED (emergency) / BLUE (secure health)
  - "Send" button: encrypt → encode → play; shows waveform animation
  - RED mode: auto-repeats 3× with 300 ms gaps
- [ ] **Receive screen**
  - Live decode feed: timestamp + payload type + decrypted content
  - HMAC status indicator (✓ verified / ✗ tampered)
  - Export log (JSONL) button
- [ ] **Calibrate screen**
  - Live FFT waterfall (SurfaceView)
  - "Run calibration sweep" button
  - Current band in use indicator
- [ ] **Settings screen**
  - Key alias management (generate, rotate, delete)
  - ggwave protocol manual override
  - Volume control
  - Debug mode toggle (enables plaintext payloads for testing)

---

## PHASE S6 — Air-Gap Bridge Mode (Tier 1 Use Case)

Goal: Ship the "Encrypted Acoustic Data Diode" feature as a first-class mode.

- [ ] **Windows/Linux transmitter companion** (Python, self-contained binary)
  - Reads from stdin or file
  - Encrypts with pre-shared AES-256 key (loaded from env or config)
  - Encodes via ggwave Python bindings
  - Plays via sounddevice library
  - Near-ultrasonic band by default
  - Output: `sdam_transmit.py` in `SDAM/tools/`
- [ ] **Android Sentinel receiver**
  - Dedicated "Air-Gap" mode in the app
  - Displays received payloads in chronological log
  - Exports to encrypted file on SD card
  - Optional: forward via LAN to a collector endpoint
- [ ] **Key provisioning** for air-gap scenarios
  - Pre-shared key workflow: USB drive (read into Keystore, zero file)
  - QR code workflow: scan from air-gapped display
- [ ] Security audit checklist:
  - [ ] Verify AES-GCM nonce is never reused (counter-based nonce)
  - [ ] Verify replay window enforced (HMAC counter ± 5 tolerance)
  - [ ] Verify key is hardware-bound (StrongBox on supported devices)
  - [ ] Verify no plaintext in logcat in production builds

---

## PHASE S7 — Testing, Hardening, and First Release

Goal: Production-quality build ready for enterprise pilot.

- [ ] Unit tests: `CryptoEngine`, `AcousticEngine` (JNI mock), `DecodePipeline`
- [ ] Integration tests: full encode → transmit → receive → decode → verify chain
- [ ] Range tests:
  - 0.5 m / 1 m / 2 m / 5 m — indoor, hard surfaces
  - Through-glass test
  - Through-door test (confirm signal dies at thick concrete)
- [ ] Threat model review (matches `Gibberlink/docs/SECURITY.md`)
- [ ] ProGuard / R8 config — strip debug symbols in release
- [ ] APK signing with production keystore (not committed to repo)
- [ ] F-Droid submission (open-source tier)
- [ ] Enterprise pitch deck: "Acoustic Data Diode for Critical Infrastructure"

---

## OPEN QUESTIONS

- Can AES-256-GCM overhead (12-byte IV + 16-byte tag = 28 bytes) fit within
  ggwave's bandwidth budget at near-ultrasonic frequencies? (ggwave protocol 1
  max payload ~140 bytes — 28 bytes overhead leaves ~112 bytes/burst.)
- Does Android StrongBox hardware (Titan M / TrustZone) add measurable
  encrypt/decrypt latency to the real-time audio pipeline?
- Can the near-ultrasonic band (17–22 kHz) pass through a standard office
  window? If yes, the "room-contained" claim needs a range qualifier.
- What is the minimum practical SNR for reliable ggwave decode at protocol 1?
  (Calibration phase will measure this on BV9900Pro vs. S24 Ultra.)
- Is there a regulatory framework that classifies acoustic data transmission
  as a "communication device" under FCC Part 15? (Preliminary view: no.)

---

*ROADMAP.md — SDAM/ — v1.0 — 2026-04-19*
