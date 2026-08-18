# ROADMAP.md — Unitary Pentacorder
## Phased build plan + completion status

---

## ✅ PHASE P0 — Core Native App (COMPLETE)

All 109 Kotlin files implemented across 18 modules.

- [x] Single-Activity Compose host with Hilt DI
- [x] 6 bottom-nav tabs: Dashboard / Medical / Transmit / Pentacorder / Translate / Labs
- [x] 15 sensor-suite sub-screens in Labs grid
- [x] Calibration Wizard (runs on first launch)
- [x] `applicationId = com.axiomzero.pentacorder`, `minSdk = 26`, `targetSdk = 34`

---

## ✅ PHASE P1 — Sensor Stack (COMPLETE)

- [x] All Android sensors registered (accelerometer, gyro, mag, baro, light, proximity, gravity, rotation, linear accel, step counter, HR)
- [x] GPS via LocationManager (fine location)
- [x] Battery + thermal via BatteryManager
- [x] WiFi/BT/WiFiDirect/UWB connectivity state via ConnectivityAdvisor
- [x] S Pen IMU + Air Actions via SPenAdvisor
- [x] EnergyAdvisor (battery band + RF harvest + PowerShare governance)
- [x] Sensor → manifold field mapping: δg_μν, Γ^σ, H_μν, B_4, λ^μ, φ
- [x] SensorBridge singleton (cross-module StateFlow bus)

---

## ✅ PHASE P2 — Medical Suite (COMPLETE)

- [x] NEWS2 scoring (manual vitals entry: HR, RR, SpO₂, BP, temp, AVPU)
- [x] φ-homeostasis display (Ψ_brain coherence)
- [x] rPPG: contact-free HR + HRV from camera green channel (PPGAdvisor)
- [x] TremorAdvisor: dominant tremor frequency + session trend
- [x] SkinColorAdvisor: pallor + jaundice screen (medical disclaimer)
- [x] First-aid protocol cards (CPR, choking, bleeding, burns, fracture, anaphylaxis, stroke)
- [x] First-responder mode (RED mode + GPS share + emergency call)
- [x] Acoustic broadcast of vitals via Gibberlink

---

## ✅ PHASE P3 — AI Assistant (COMPLETE)

- [x] AssistantEngine: Remote API → Local Ollama → Static KB resolution
- [x] Static KB: 15 curated entries (Pentad, sensors, medical, theory, code generation)
- [x] 15 AssistantAction types: Navigate, GenerateCode, AddDashboardCard, StartMonitoring, PushNotification…
- [x] AdaptiveStateHolder (DataStore-persisted adaptive UI)
- [x] Per-screen hints: Dashboard / Medical / Tricorder / Translate
- [x] Pinned metrics on Pentacorder sensor view
- [x] Monitoring jobs: named coroutines with Active Monitors panel in AssistantSheet
- [x] Proactive sentinel: battery critical/hot, extreme pressure, severe HR/SpO₂ auto-alerts
- [x] Live Pentad coherence bar (GREEN/AMBER/RED) via SensorBridge.pentad flow
- [x] Code blocks with copy-to-clipboard in AssistantSheet
- [x] API Settings panel (collapsible): key / endpoint / model
- [x] Ethical axioms I–V embedded permanently in SYSTEM_PROMPT

---

## ✅ PHASE P4 — Translate + Protocol Bridge (COMPLETE)

- [x] ML Kit on-device translation (59 languages, offline)
- [x] Language auto-detect
- [x] TTS output
- [x] Quick-phrase cards per role (NURSE / RESPONDER / ENGINEER)
- [x] SensorInterpreter → SituationReport (role-aware narrative)
- [x] Gibberlink payload → natural language decode
- [x] Natural language → structured Gibberlink payload encode
- [x] Pentad state view with five φ body gauges

---

## ✅ PHASE P5 — Optics + Advanced Labs (COMPLETE)

7-mode optical suite:
- [x] NLOS (non-line-of-sight reflectance analysis)
- [x] Hyperspectral (camera channel ratio analysis)
- [x] Motion Magnification (micro-vibration via Eulerian video)
- [x] Visual Microphone (camera as acoustic sensor)
- [x] Synthetic Aperture (multi-frame super-resolution)
- [x] Night Mode (low-light sensor fusion)
- [x] Active NIR (camera NIR channel advisor)

Labs grid:
- [x] EMF & Structural Lab (magnetometer + barometer)
- [x] Environmental Science Hub (temperature, humidity, pressure)
- [x] Precision Contractor Suite (dimensions, material detect, laser level)
- [x] UWB Spatial Lab (Ultra-Wideband ranging + positioning)
- [x] Acoustic Intelligence (Gibberlink encode/decode, spectrum, auth)
- [x] Citizen Science Hub (sample logging, field notes, anomaly register)
- [x] S Pen Command Center (stroke pattern, pressure, air actions)
- [x] Sensor Status dashboard (all sensors registered + health)
- [x] Data Logger (CSV export of all sensor streams)
- [x] Manifold Probe (live 5D field equations on-device)
- [x] Photonic Probe (camera photon flux analysis)
- [x] Surface Scan (topographic scan via camera + accel fusion)

---

## ✅ PHASE P6 — Acoustic / Security Stack (COMPLETE)

- [x] GGWaveEncoder / GGWaveDecoder (JNI stub — production requires NDK build)
- [x] AES-256-GCM PayloadCipher
- [x] HMAC-SHA256 session authentication
- [x] GibberKeyManager (Android Keystore hardware-backed)
- [x] AcousticAuth (challenge-response handshake)
- [x] AudioLoopService foreground service
- [x] SentinelWorker (WorkManager periodic background scan)
- [x] UPBHubService (Universal Protocol Bridge)

---

## 🔲 PHASE P7 — Native ggwave NDK (Next)

For production APK release the JNI stub must be replaced with a real native build:

- [ ] Pull `ggwave` C++ source and compile for `arm64-v8a` via Android NDK
- [ ] Wire `GGWaveNative.kt` JNI bindings to the compiled `.so`
- [ ] Run loopback calibration on S24 Ultra: `noise_calibrate.py --sweep --play`
- [ ] Measure decode success at 0.5 m / 1 m / 2 m (target ≥ 95% @ 1 m)
- [ ] Validate Dolby Atmos EQ does not distort FSK bands

---

## 🔲 PHASE P8 — CI / Release (Next)

- [ ] GitHub Actions workflow: `./gradlew assembleRelease` → signed APK artifact
- [ ] Release tag `android-latest` in wuzbak/Private with `pentacorder-s24ultra.apk`
- [ ] Update `scripts/install_s24ultra.sh` RELEASE_APK_URL to point to the new artifact
- [ ] ProGuard rules review for Hilt + Compose + Room
- [ ] Signed release APK (keystore provisioned)

---

## 🔲 PHASE P9 — Field Validation

- [ ] Install on Samsung Galaxy S24 Ultra (primary test device)
- [ ] Complete Calibration Wizard in-person
- [ ] Assistant first session: "What's my Pentad state?"
- [ ] Verify proactive sentinel fires on battery drain
- [ ] Run noise_calibrate.py Gibberlink roundtrip BV9900Pro ↔ S24 Ultra
- [ ] RED mode SOS GPS broadcast verified received on second device

---

*ROADMAP.md — Unitary Pentacorder — v1.0 — 2026-05-05 — AxiomZero Technologies*
