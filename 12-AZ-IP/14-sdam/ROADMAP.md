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

- [x] Scaffold Android Studio project
  - Min SDK: 26 (Android 8.0)
  - Target SDK: 35 (Android 15)
  - Language: Kotlin
  - Build: Kotlin DSL (build.gradle.kts)
  - DI: Hilt
- [x] Vendor ggwave v0.4.2 and configure its CMake build
  - Build target: `arm64-v8a` (primary), `x86_64` (emulator)
  - Output: `libggwave.so`
- [x] Write JNI wrapper: `GGWaveNative.kt` + `sdam_jni.cpp`
  - `ggwaveEncode(payload: ByteArray, protocol: Int, volume: Int): ShortArray`
  - `ggwaveDecode(pcm: ShortArray): ByteArray?`
- [x] `AudioEngine.kt` — AudioRecord RX + AudioTrack TX wrappers
  - Sample rate: 48000 Hz (matches ggwave default)
  - Channel: MONO
  - Encoding: PCM_16BIT
- [ ] Hardware loopback: encode "HELLO" → play → record → decode → assert "HELLO"
  - Not yet validated on emulator, BV9900Pro, or S24 Ultra. Native source/build
    integration is present; a successful software build is not hardware proof.

---

## PHASE S2 — Crypto Layer + Android Keystore Integration

Goal: Production payloads use AES-GCM before ggwave. Keys are managed through
Android Keystore, but hardware backing is device-dependent and unverified;
cross-device key provisioning is not implemented.

- [ ] `CryptoEngine.kt` — AES-256-GCM via Android Keystore
  - `generateKey(alias: String)` — creates an Android Keystore key; hardware backing varies by device
  - `encrypt(alias: String, plaintext: ByteArray): EncryptedPayload`
  - `decrypt(alias: String, payload: EncryptedPayload): ByteArray`
  - `EncryptedPayload` = (iv: 12 bytes) + (ciphertext + tag: n+16 bytes)
- [ ] HMAC-SHA256 session authentication layer
  - SDAM1 replay high-water mark is in-memory only; not restart-resistant
  - SDAM1 data frames use a 12-byte (96-bit) truncated HMAC tag
  - Legacy AcousticAuth handshake retains its separate 4-byte tag for wire compatibility
- [ ] Key provisioning flow:
  - QR code scan OR near-field acoustic handshake to share session secret
  - Secret stored in Android Keystore, never in SharedPreferences or disk
- [ ] Smoke test: encrypt "SECRET DATA" → encode → play → record → decode →
  decrypt → assert "SECRET DATA"
- [ ] Verify key is not extractable (Android Keystore `setIsStrongBoxBacked(true)`)

### Verified secure text path delivered

- [x] Text transmit encrypts with AES-GCM (except explicit debug mode), wraps
  the payload in a countered HMAC-SHA256 frame, and queues it through native
  ggwave/AudioTrack.
- [x] Receive decodes native ggwave frames, verifies the HMAC and replay
  counter for the lifetime of the in-memory verifier, decrypts AES-GCM, and
  shows explicit success or rejection/error.
- [x] If native ggwave is unavailable or playback fails, transmit reports an
  error and does not create a success log entry.
- [x] Deterministic JVM tests cover frame encoding/decoding, AES-GCM round-trip
  and tamper rejection, HMAC tampering, replay rejection, malformed frames,
  24-hex frame tag size, wrong-size tags, maximum counter/chunk frame sizing,
  multi-fragment UTF-8 round-trip, incomplete/malformed fragment rejection,
  explicit maximum-size rejection, and the 140-byte native payload limit.
- [x] Replay rejection is explicitly process-local; the high-water mark is
  neither persisted nor restart-resistant.
- [x] Standard/Secure messages use separately AES-GCM-encrypted, authenticated
  `MSG` fragments and reassemble up to 4,995 UTF-8 bytes (999 five-byte chunks);
  DIODE retains its distinct backward-compatible prefix and 7,992-byte limit
  (999 eight-byte chunks). Both reject larger inputs explicitly, including
  multibyte messages that would exceed 999 fragments.
- [x] Standard/Secure fragments carry a random 32-bit message grouping ID;
  frames are authenticated individually and only a fully received group is
  reported as successful reassembly.
- [ ] Device speaker/microphone loopback and cross-device key provisioning.
  Separate installs currently have different Keystore keys; cross-device
  secure delivery must not be inferred from local JVM tests.
- [ ] Gradle Android build and native packaging could not be verified in this
  environment because the Android Gradle Plugin repository was unreachable.

---

## PHASE S3 — Foreground Service + Background Decode Loop

Goal: Explore background capture within Android lifecycle and resource limits;
packet loss remains possible and must be reported.

- [ ] `AcousticModemService.kt` — Android Foreground Service
  - Persistent notification: "SDAM Sentinel — listening"
  - Starts `AudioEngine` RX loop on service start
  - Broadcasts decoded payloads via `LocalBroadcastManager`
  - Handles `START_LISTENING` / `STOP_LISTENING` intents
- [ ] `DecodePipeline.kt` — sliding PCM window → ggwave decode → crypto verify
  - 1024-sample sliding window at 48 kHz = ~21 ms resolution
  - On successful decode: HMAC verify → AES decrypt → emit to ViewModel
  - On HMAC failure: log tamper event, discard frame; replay checks are scoped
    to the current in-memory verifier and do not survive process restart
- [ ] Battery optimisation: release `AudioRecord` on screen-off if no active
  session (configurable via settings)
- [ ] Test: background decode while screen off, device in pocket (BV9900Pro + S24)

---

## PHASE S4 — Frequency Agility + Noise Floor Calibration

Goal: Modem auto-selects the cleanest frequency band for the environment.

- [ ] `NoiseProfiler.kt` — ambient FFT snapshot
  - 4096-point FFT over 1-second audio window
  - Outputs per-band SNR map (0–24 kHz in 100 Hz bins)
  - Measures device-specific acoustic response; no BV9900Pro roll-off result is established
- [ ] `FrequencySelector.kt` — band picker
  - Compare measured performance across selected ggwave protocols; do not infer inaudibility from protocol labels
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
  - Specify and review a cross-device key agreement or wrapped-key protocol;
    do not claim USB/QR provisioning until Android Keystore import behavior,
    peer authentication, and recovery are implemented and tested.
- [ ] Security audit checklist:
  - [ ] Verify generated AES-GCM IVs use a cryptographic RNG and assess
    collision risk for the expected message volume.
  - [ ] Verify the implemented SDAM1 high-water replay policy, including its
    process-local lifetime and behavior after restart.
  - [ ] Record whether each supported device actually provides StrongBox or
    other secure-hardware backing; do not assume it.
  - [ ] Verify no plaintext in logcat in production builds

---

## PHASE S7 — Testing, Hardening, and First Release

Goal: Production-quality build ready for enterprise pilot.

- [ ] Unit tests: `CryptoEngine`, `AcousticEngine` (JNI mock), `DecodePipeline`
- [ ] Integration tests: full encode → transmit → receive → decode → verify chain
- [ ] Acoustic performance tests (measure outcomes; do not assert containment):
  - 0.5 m / 1 m / 2 m / 5 m — indoor, hard surfaces
  - Through-glass and through-door attenuation / decode success
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
- What spectrum do target devices actually emit for each selected protocol, and
  how do audibility and attenuation vary by device and environment? No
  room-containment property is currently claimed.
- What is the minimum practical SNR for reliable ggwave decode at protocol 1?
  (Calibration phase will measure this on BV9900Pro vs. S24 Ultra.)
- What jurisdiction-specific regulatory requirements apply to the hardware and
  its acoustic emissions? No exemption or regulatory conclusion is assumed.

---

*ROADMAP.md — SDAM/ — v1.0 — 2026-04-19*
