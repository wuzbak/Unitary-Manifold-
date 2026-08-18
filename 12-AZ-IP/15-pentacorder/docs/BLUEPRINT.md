# BLUEPRINT.md — Android Platform Architecture
## Full system blueprint for the Gibberlink/UPB stack on Android

---

## System Overview

The Android deployment has two modes of operation:

1. **Termux mode** — immediate, no-build deployment of all Python scripts.
   All 14 Gibberlink scripts + Sentinel Watchdog run directly in Termux today.

2. **Native APK mode** — production-quality Android app using the ggwave C++
   library via NDK, Android AudioRecord/AudioTrack, and Android Keystore.
   This is Phase A9 work.

---

## Termux Architecture (Current)

```
┌────────────────────────────────────────────────────────────────┐
│  Android OS                                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Termux (com.termux)                                     │  │
│  │                                                          │  │
│  │  ~/diary/                                                │  │
│  │  ├── Gibberlink/                                         │  │
│  │  │   ├── scripts/                                        │  │
│  │  │   │   ├── upb_hub.py        ← Hub: all Q_* channels  │  │
│  │  │   │   ├── broadcast.py      ← Typed payload TX       │  │
│  │  │   │   ├── decode_wav.py     ← ggwave RX loop         │  │
│  │  │   │   ├── encode_message.py ← ggwave TX              │  │
│  │  │   │   ├── acoustic_auth.py  ← HMAC session auth      │  │
│  │  │   │   ├── modes.py          ← GREEN/RED/BLUE registry│  │
│  │  │   │   ├── manifest.py       ← Accessory manifest     │  │
│  │  │   │   ├── accessory_manager.py ← Registry + JIT UI   │  │
│  │  │   │   ├── usb_bridge.py     ← USB-OTG sensor bridge  │  │
│  │  │   │   ├── log_ingest.py     ← RAG corpus builder     │  │
│  │  │   │   └── audit_log.py      ← Centralized audit      │  │
│  │  │   └── experiments/          ← Logs, calibration JSON │  │
│  │  └── BV9900Pro-HomeTest/                                 │  │
│  │      └── scripts/                                        │  │
│  │          ├── sentinel_watchdog.py   ← ADB vitals daemon  │  │
│  │          └── sentinel_commentary.py ← LLM health hook   │  │
│  │                                                          │  │
│  │  Python 3.11 + ggwave + PyAudio + NumPy                  │  │
│  │  Ollama (optional, local LLM)                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  Android Audio HAL ←──→ PortAudio ←──→ PyAudio ←──→ ggwave   │
│  Android GPS API  ←──→ `adb shell dumpsys location`           │
│  Android Sensors  ←──→ `adb shell dumpsys sensorservice`      │
└────────────────────────────────────────────────────────────────┘
```

---

## Native APK Architecture (Phase A9)

```
┌────────────────────────────────────────────────────────────────┐
│  GibberNode Android App                                        │
│                                                                │
│  UI Layer (Jetpack Compose / Material 3)                       │
│  ├── ModeSelector (GREEN / RED / BLUE)                        │
│  ├── DecodeLogView (live transcript)                           │
│  ├── AccessoryRegistryView (MNFT devices)                      │
│  └── AuditLogView (session history)                            │
│                                                                │
│  Service Layer                                                 │
│  ├── GibberForegroundService     ← keeps decode loop alive    │
│  ├── SentinelWorkerService       ← periodic watchdog          │
│  └── UPBHubService               ← manages Q_* channels       │
│                                                                │
│  Domain Layer                                                  │
│  ├── GGWaveEncoder / GGWaveDecoder (JNI → C++ ggwave)         │
│  ├── AcousticAuth (HMAC-SHA256, Kotlin reimplementation)      │
│  ├── ModeRegistry (GREEN/RED/BLUE)                            │
│  ├── PayloadBuilder (GPS/VITALS/ENV/SYS/MNFT/INTENT)         │
│  └── RelayRouter (SDR/BLE/ALERT → RED broadcast)              │
│                                                                │
│  Data Layer                                                    │
│  ├── AuditLogRepository → Room DB (SQLite)                    │
│  ├── AccessoryRegistry  → Room DB                             │
│  └── CalibrationStore   → DataStore (Preferences)            │
│                                                                │
│  Security Layer                                               │
│  ├── GibberKeyManager   → Android Keystore / StrongBox        │
│  └── SecretRotation     → Key agreement (future: ECDH)        │
│                                                                │
│  Audio I/O                                                     │
│  ├── AudioRecord (mic, 48000 Hz, CHANNEL_IN_MONO, PCM_16BIT)  │
│  └── AudioTrack  (speaker, CHANNEL_OUT_STEREO)                │
│                                                                │
│  Android Platform APIs                                        │
│  ├── LocationManager    → GPS for RED-mode broadcasts         │
│  ├── SensorManager      → barometer, HR, SpO2, accel, gyro   │
│  └── UsbManager         → USB-OTG sensor bridge              │
└────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: GREEN Mode Sensor Node

```
[BV9900Pro sensors]
        ↓ adb shell dumpsys / SensorManager API
[broadcast.py / PayloadBuilder]
        ↓ builds typed payload: GPS:lat:lon:alt:acc:bat
[encode_message.py / GGWaveEncoder]
        ↓ ggwave.encode(payload, protocol=1, volume=15)
[PyAudio / AudioTrack]
        ↓ plays .wav through phone speaker
        ~~~~~~~~~~~~~~~~~~ acoustic channel ~~~~~~~~~~~~~~~~~~
[PyAudio / AudioRecord on S24Ultra]
        ↓ continuous FFT sampling
[decode_wav.py / GGWaveDecoder]
        ↓ ggwave.decode(samples)
[acoustic_auth.py] → verify HMAC tag
        ↓
[upb_hub.py Q_ACOUSTIC drain]
        ↓ normalize_token()
[Q_INTENT → Ollama intent engine]
        ↓
[audit_log.py → experiments/audit.jsonl]
```

---

## Data Flow: RED Mode Emergency Broadcast

```
[Sentinel Watchdog detects anomaly OR manual trigger]
        ↓ intent: AUTO:THERMAL_THROTTLE or MANUAL:EMERGENCY
[upb_hub.py relay rule: SYSTEM/ALERT → red]
        ↓
[broadcast.py --mode red --adb-gps]
        ↓ pulls live GPS from device
        ↓ builds payload: GPS:lat:lon:alt:acc:bat
        ↓ encodes 3× with 300ms gaps (RED redundancy)
        ↓ volume=80 (maximum)
[3× acoustic transmissions]
        ↓ any device within range receives
[decode_wav.py --mode red on receiver]
        ↓ deduplicates by counter
[CommonToken: source=ACOUSTIC, intent=ALERT, payload=GPS:...]
        ↓ → relay router
[RELAY → forward to NETWORK, BLE, SDR if available]
```

---

## Key Design Decisions (Android)

### Why Termux + Python, not a native app (yet)?

The entire Gibberlink stack was designed as Python scripts for cross-platform
portability. Termux runs this stack on Android with zero modification. Building
a native app adds a 2–4 week development cycle and maintenance overhead. The
Termux path delivers 100% of the functionality today.

The native APK (Phase A9) is the right long-term destination when:
- Background reliability needs to exceed what Termux:Boot can provide
- Play Store / F-Droid distribution is needed
- Android Keystore hardware binding is required
- The UI needs to be usable by non-developers

### Why Android Keystore instead of .env?

On Android, the `.env` file lives on internal storage accessible to Termux.
On a non-rooted device this is app-sandboxed. But on a production device, the
Android Keystore provides hardware attestation — the key material never leaves
the Secure Enclave (StrongBox on Pixel, Knox on Samsung). This is the same
security model as mobile banking apps.

### Why PortAudio / PyAudio instead of AudioRecord?

PortAudio is a mature, battle-tested cross-platform audio library that ggwave
was designed to work with. Replacing it with Android's native AudioRecord would
require reimplementing the ggwave C++ decode pipeline in Java/Kotlin or writing
JNI bindings — that is Phase A9 work. For Termux deployments, PortAudio compiled
via the Termux package manager is the path of least resistance.

---

## Compatibility Matrix

| Android Version | API | Status | Notes |
|---|---|---|---|
| Android 8.0 (Oreo) | 26 | ✅ Minimum | Termux supported; audio permissions granted manually |
| Android 9.0 (Pie) | 28 | ✅ | Background mic restrictions; Termux:Boot workaround |
| Android 10 | 29 | ✅ | `ACCESS_BACKGROUND_LOCATION` permission needed for GPS in background |
| Android 11 | 30 | ✅ | Package visibility changes; Termux unaffected |
| Android 12 | 31 | ✅ | Bluetooth 5.3 scan changes; audio unaffected |
| Android 13 | 33 | ✅ | `RECORD_AUDIO` still runtime-grantable; granular media permissions |
| Android 14 | 34 | ✅ | Health Connect API for VITALS sourcing; new audio routing options |
| Android 15 | 35 | ✅ | Satellite API (Snapdragon Satellite on compatible devices) |
| Android 16 (anticipated) | 36 | 🔲 | Bluetooth 6.0 Channel Sounding; LE Audio |

---

*BLUEPRINT.md — Android/docs/ — v1.0 — 2026-04-18*
