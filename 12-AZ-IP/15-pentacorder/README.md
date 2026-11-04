# Unitary Pentacorder
## Android App — Source and Setup Notes

- **Product:** Unitary Pentacorder
- **Package:** `com.axiomzero.pentacorder`
- **Platform target:** Android 8.0+ (API 26+); Galaxy S24 Ultra is a design target, not a validated device
- **Version:** 1.0.0
- **Status:** 🟡 In development — not validated or release-ready

The Gradle version catalog now pins the plugin/library aliases used by the
project, aligned with SDAM's Android/Kotlin/Compose toolchain. The PC Suite
platform workflow must resolve those dependencies and build the actual APK;
restoring the catalog alone is not build verification. The native ggwave
implementation is still a JNI stub; release signing and on-device field validation remain unfinished
(ROADMAP phases P7–P9). No production APK or hardware capability is claimed.

---

## What It Is

The **Unitary Pentacorder** is an Android sensor-dashboard and research
visualization project inspired by the tricorder concept. It reads selected
device inputs where Android, the hardware, and granted permissions allow, and
some screens derive illustrative values from those readings. It is not a
validated scientific instrument, medical device, or measurement of the
Unitary Manifold.

The app's model labels associate selected sensor inputs with framework
quantities for visualization. These associations do not establish that phone
sensors measure the corresponding physical fields:

| Device input | App visualization label | Limitation |
|--------|---------------|--------|
| Accelerometer | Metric perturbation (δg_μν) | App-defined transformation; not a measured metric |
| Gyroscope | Connection (Γ^σ_μν) | Sensor motion data; not a measured Levi-Civita connection |
| Magnetometer | Gauge-field analogue (H_μν) | Magnetic-field reading; not a measured Kaluza–Klein field |
| Barometer | Pressure / B₄ analogue | Barometric pressure where the device has a pressure sensor |
| GPS | Position / λ-coordinate analogue | OS location data; not a measured geodesic |
| Heart-rate input | φ₂ / homeostasis display | Optional hardware or camera estimate; not a clinical assessment |
| Battery | φ display input | Battery status; not a measured extra-dimensional field |
| Ambient light | Photon-flux proxy | Lux reading where available; not a CMB measurement |

The Pentad and “5D” screens show app-defined values derived from available
inputs (and, in some screens, synthetic demo data). Their state vectors,
coherence values, and field labels are illustrative software outputs, not
validated physical quantities or evidence that the framework has been measured.

---

## Six Tabs + AI Assistant

| Tab | What it does |
|-----|-------------|
| **Dashboard** | Mode selection and status displays. SOS-style controls are not a verified emergency service. |
| **Medical** | Manual vital entry, NEWS2 calculation, informational first-aid content, and experimental camera-based rPPG/skin-screen features. None is diagnostic or a substitute for clinical care. |
| **Transmit** | Gibberlink controls and payload preparation. Native ggwave audio encoding/decoding remains a JNI stub and is not a working, validated acoustic link. |
| **Pentacorder** | Selected Android sensor readings and app-defined visualizations; sensors and values vary by device and permission. |
| **Translate** | Translation, OCR, object-detection, and protocol screens; availability depends on models, network/download state, camera, language, and device support. |
| **Labs** | Experimental screens for EMF, UWB, optics, S Pen, environment, contractor, and science topics. Hardware-dependent functions may be unavailable; several views are advisory, simplified, or demo-only. |

**Pentacorder Assistant (✨ FAB)** — an assistant interface in a bottom sheet.
Where available, it can use app context and try a configured remote API or a
reachable local Ollama service, with a static knowledge-base fallback. Sensor
context, assistant responses, actions, alerts, and coherence displays are
informational software features; they are not guaranteed on every device and
are not validated monitoring or decision-support systems.

---

## Build & Install

### Prerequisites

- **Android Studio** (Electric Eel or later) with Android SDK 34
- **ADB** (Android Platform Tools) for device install
- USB Debugging enabled on the phone
- Android NDK is needed to complete the native ggwave implementation; the
  current JNI stub does not provide a validated working audio codec.

The commands below are build/install instructions, not a claim that the
current checkout builds or has been tested on the listed devices. The Gradle
version catalog is missing, and build configuration and on-device behavior
remain unvalidated.

### Install instructions (S24 Ultra; unvalidated)

```bash
# 1. Build the debug APK
cd 12-AZ-IP/15-pentacorder
./gradlew assembleDebug

# 2. Install to phone over USB
./scripts/install_s24ultra.sh --apk app/build/outputs/apk/debug/app-debug.apk
```

The install script is intended to:
1. Detect a connected phone via ADB
2. Install Termux + Termux:Boot + Termux:API for the separate Termux stack
3. Install a supplied Pentacorder APK
4. Bootstrap the Python/Gibberlink environment in Termux
5. Configure Termux:Boot for auto-start

These steps and the resulting app/Termux integration have not been validated
as an end-to-end deployment. The Termux acoustic scripts are separate from
the unfinished native Android codec.

### Windows

```bat
REM Enable USB Debugging, connect phone, then:
scripts\install_s24ultra.bat --apk app\build\outputs\apk\debug\app-debug.apk
```

### Manual install (Android ≥ API 26; if an APK is available, unvalidated)

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

---

## First Launch

1. If the calibration/setup screen is available, follow its prompts; an audio
   calibration does not validate the native Gibberlink codec.
2. The **✨ FAB** opens the assistant interface when present.
3. Example prompt: *"Interpret the available sensor readings."* Treat outputs
   as informational and verify important facts independently.

### Enable Local AI (Ollama in Termux — no cloud needed)

```bash
# In Termux on the phone:
pkg install curl
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2:3b
ollama serve &
# The assistant may use the service if it is reachable and configured
```

### Enable Remote AI (optional)

- Open assistant → tap **⚙️** → enter your OpenAI-compatible API key + endpoint

---

## Architecture (intended module layout)

```
Supported Android Sensors (availability varies by device/permission)
    │
    ▼
TricorderViewModel ──────────────────┐
MedicalViewModel  ──→ SensorBridge ──┤──→ TranslateViewModel
SPenViewModel     ──────────────────┘         (app-defined context)
                                               │
                                               ▼
                                        AssistantViewModel
                                           (assistant interface)
                                               │
                                        AssistantEngine
                                           │  Remote API (internet)
                                           │  Local Ollama (Termux)
                                           │  Static KB (offline)
                                           ▼
                                       AssistantAction
                                           │
                                  Navigate · GenerateCode · AddDashboardCard
                                  StartMonitoring · PushNotification
                                           │
                                    AdaptiveStateHolder (DataStore)
                                           │
                                    Dashboard · Medical · Tricorder · Translate screens
```

### Module map

```
app/                       ← MainActivity, AssistantViewModel, AssistantSheet
core/
  gibberwave/              ← SensorBridge, AssistantEngine, AdaptiveStateHolder
  audio/                   ← Audio interfaces; native ggwave codec remains stubbed
  security/                ← AES-256-GCM PayloadCipher, GibberKeyManager
  health/                  ← Experimental/advisory PPG, tremor, and skin-color calculations
  optics/                  ← NLOS, Hyperspectral, MotionMag, VisualMic, SynthApt
  interpret/               ← SensorInterpreter, PentadState, UserRole
  [+ emf, acoustic, spen, uwb, enviro, contractor, energy, connectivity]
feature/
  dashboard/               ← Mode ring, Sentinel health, Calibration wizard
  tricorder/               ← Sensor displays and app-defined visualizations
  medical/                 ← NEWS2 calculator and non-diagnostic experimental features
  translate/               ← Translation/OCR interfaces; model and device dependent
  mode/                    ← Mode selection and unfinished native audio controls
  labs/                    ← Experimental screens, including simplified/demo views
  [+ spen, emf, enviro, contractor, uwb, acoustic, science, optics]
```

---

## Permissions

| Permission | Purpose |
|---|---|
| `RECORD_AUDIO` | Acoustic/Gibberlink receive |
| `ACCESS_FINE_LOCATION` | GPS → geodesic coordinate |
| `CAMERA` | rPPG, optical suites, QR |
| `BODY_SENSORS` | Optional device heart-rate sensor access; SpO₂ is not guaranteed |
| `ACTIVITY_RECOGNITION` | Step counter / motion state |
| `NEARBY_WIFI_DEVICES` | WiFi Direct peer discovery |
| `POST_NOTIFICATIONS` | Proactive assistant alerts |

---

## Operational Modes

| UI mode | Colour | Intended label (not a verified service) |
|------|--------|-----|
| GREEN | 🟢 | Passive monitoring — normal operation |
| RED | 🔴 | Emergency-themed mode; SOS, GPS broadcast, and delivery are not validated |
| BLUE | 🔵 | Health-themed mode; acoustic vitals relay is not validated |
| AMBER | 🟡 | Field analysis — caution state, elevated monitoring |

---

## Assistant Guidance

The assistant prompt includes the following guidance (`AssistantEngine`):

```
I   — NO LIES. Never fabricate sensor readings or facts.
II  — NO MANIPULATION. Correct, affirm, nudge — nothing else.
III — DO NO HARM. Medical guidance: NHS NEWS2 / WHO standards only.
IV  — THEY CAN SHARE THEIR TRUTH. Every framework is valid.
V   — TRANSPARENCY. Gaps stated. Uncertainty stated. Nothing hidden.
```

---

## Unitary Manifold Connection

```
∇_μ J^μ_inf = 0
```

This equation is part of the framework's theoretical presentation. The
Pentacorder does not measure or test this law; its sensor displays and
model-derived values are app-level visualizations, not measurements of the
Walker-Pearson field equations.

Predictions discussed by the framework (not tested by this app):
- **nₛ = 0.9635** (CMB spectral index; external data claim, not a phone-sensor result)
- **β ∈ {≈0.273°, 0.331°}** (birefringence; future observational falsifier, not measurable by this app)

---

## Browser Companion — Pentacorder + SDAM Field Scanner

`public-site/az-apps/15-pentacorder.html` is a browser companion that attempts to
use selected browser APIs. Actual access depends on browser, OS, hardware,
secure-context requirements, and permission grants. It is not a substitute for
the native app, and its behavior has not been validated across devices. Its
screens include:

1. **📡 Field Scanner** — the 15-channel raw sensor readout (table below).
2. **🧰 Hardware Inventory** — feature-detection checklist and `navigator` device summary.
3. **🛠️ Tools** — an 11-tool sensor-driven multitool: spirit level, compass with
   bearing-to-target, decibel meter with hearing-safety exposure dose, chromatic
   tuner (autocorrelation pitch detection), flashlight/torch control, QR/barcode
   scanner (`BarcodeDetector`), camera steadiness meter, pedometer/step counter,
   fall/impact detector, magnetometer field scanner, and a stopwatch/lap timer.
   Every tool reuses the already-granted motion/mic/camera permissions instead of
   re-prompting, and honestly reports when a browser exposes no API for a tool
   (e.g. `BarcodeDetector` or `Magnetometer` where the browser does not expose
   the API).
4. **🫀 Vitals & Environment** — camera-based pulse estimation (remote
   photoplethysmography via red-channel autocorrelation; an experimental,
   device- and lighting-dependent estimate, **not a medical device**) plus
   ambient noise/light readouts.
5. **🧭 Navigation** — a live GNSS console (position/speed/course/accuracy),
   a haversine-integrated distance-travelled odometer, and a waypoint log
   exportable as GeoJSON.
6. **📶 Acoustic Modem** — a simple experimental browser audio link (table below);
   not the unfinished native ggwave codec.
7. **📄 Field Report** — exports a PDF dossier of the session's live readings.

| Channel | Browser API | Honesty behaviour |
|---|---|---|
| Accelerometer / gyroscope | `DeviceMotionEvent` | live reading or "no DeviceMotionEvent" |
| Compass heading | `DeviceOrientationEvent` | live reading or unavailable |
| Barometer / proximity / ambient light | — | always reported **unavailable** — no web standard exposes these sensors in any current browser |
| Flicker / focus distance | camera `getUserMedia` + `MediaStreamTrack.getCapabilities()` | luminance-proxy flicker estimate; focus distance only if the driver reports a `focusDistance` capability |
| Microphone level | `getUserMedia` + `AnalyserNode` | live dBFS from the real mic stream |
| S Pen / touch digitizer | `PointerEvent` (pressure, tilt, twist, altitude/azimuth, contact geometry) | live while drawing; pen-only fields marked "pen-only" for touch/mouse |
| NFC | `NDEFReader` (Web NFC) | live tag reads on Chrome/Android over HTTPS; unavailable elsewhere |
| Ultrasonic fingerprint | `PublicKeyCredential` / WebAuthn platform authenticator | enrol/verify a real passkey bound to the page's hostname — the ridge map itself is never exposed to the page |
| GNSS | `Geolocation` | live position/accuracy/altitude or denied/unavailable |
| Battery gas gauge | `Battery Status API` | live level/charging state where Chrome exposes it |
| Acoustic data link | `Web Audio API` (`OscillatorNode` + `AnalyserNode`) | Simple single-tone-per-nibble FSK implementation; experimental and not evidence that the native ggwave/OFDM codec works |
| Torch / flashlight | `MediaStreamTrack.applyConstraints({ torch })` | real LED control where the camera driver exposes a torch capability |
| QR / barcode | `BarcodeDetector` | live decode of real camera frames; unavailable on browsers without the API |
| Magnetic field | Generic Sensor API `Magnetometer` | live µT magnitude where supported; almost always reported unavailable today |

Readings are only available when the page obtains the relevant browser API,
hardware input, and permission. Some features may be unavailable or fail on a
given browser/device; do not treat browser estimates or generated reports as
validated measurements.

## Further Reading

| Document | Content |
|---|---|
| `ROADMAP.md` | Phased build plan and completion status |
| `AGENTS.md` | Agent orientation for this module |
| `scripts/` | ADB install/uninstall scripts for all devices |
| `sessions/` | Per-session handoff notes |
| `../../sessions/SESSION_006.md` | Session where the living assistant was integrated |
| `../../public-site/az-apps/15-pentacorder.html` | Browser companion; API and device support vary |

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

*README.md — Unitary Pentacorder — v1.0 — 2026-05-05 — AxiomZero Technologies*
