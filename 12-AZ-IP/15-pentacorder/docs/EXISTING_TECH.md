# EXISTING_TECH.md — What Works on Android Today
## Complete map of every Gibberlink/UPB component and its Android applicability

---

## Overview

Every script in `Gibberlink/scripts/` runs on Android via Termux without
modification. Every script in `BV9900Pro-HomeTest/scripts/` is designed to
run either via ADB from a laptop or directly in Termux on the device.

This document lists each component, its Android status, and any known quirks.

---

## Gibberlink Core Scripts

### `encode_message.py`
- **Android status:** ✅ Full functionality in Termux
- **Dependencies:** ggwave, numpy, pyaudio — all available via `pip`
- **Notes:** `--play` flag uses PortAudio → phone speaker directly.
  Ensure Termux has microphone/audio permissions.
- **Applicable flags:** `--mode`, `--auth`, `--calibrate`, `--session`,
  `--counter`, `--play`

### `decode_wav.py`
- **Android status:** ✅ Full functionality in Termux
- **Notes:** `--listen` flag opens real-time mic capture via PortAudio.
  This requires Termux to hold `RECORD_AUDIO` permission
  (granted under Settings → Apps → Termux → Permissions).
- **Applicable flags:** `--mode`, `--auth`, `--listen`, `--session`

### `roundtrip_test.py`
- **Android status:** ✅ Full functionality in Termux
- **Notes:** Encodes → plays → records → decodes in one session.
  Works well on BV9900Pro (dual mic noise cancelling).
  On S24 Ultra, Dolby Atmos EQ may slightly affect FSK decode — run
  calibration first and use `--calibrate` flag.

### `acoustic_auth.py`
- **Android status:** ✅ Full functionality in Termux
- **Notes:** Uses Python `hmac` + `secrets` standard library — no native
  crypto dependencies. Works identically on Android.

### `noise_calibrate.py`
- **Android status:** ✅ Full functionality in Termux
- **Important for Android:** BV9900Pro's IP68/IP69K waterproof membrane
  may roll off high frequencies. Always run calibration before deploying
  RED mode to identify the `safe_ceiling_hz`.

### `modes.py`
- **Android status:** ✅ Full functionality — pure Python, no audio I/O

### `broadcast.py`
- **Android status:** ✅ Full functionality in Termux
- **`--adb-gps` flag:** When running *on-device* in Termux, this flag
  uses `subprocess` to call `adb shell dumpsys location` — which on-device
  means it shells out to the device itself.
  **Workaround:** Use Android's location manager directly via
  `termux-location` (from Termux:API package) instead:
  ```bash
  pkg install termux-api
  python scripts/broadcast.py --mode red gps \
    --lat $(termux-location | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['latitude'])") \
    --lon $(termux-location | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['longitude'])")
  ```
- **`--sentinel` flag:** Works on-device — reads local JSONL files.

### `upb_hub.py`
- **Android status:** ✅ Full functionality in Termux
- **Notes:** All protocol queues (Q_BLE, Q_SDR, Q_ACOUSTIC, Q_SPEECH, Q_CSI)
  are thread-safe and work normally. The BLE ingestor requires `bleak` package
  (`pip install bleak`) which has Android backend via `dbus-python`.
  SDR ingestor requires `rtl-sdr` hardware + `rtlsdr` Python package.

### `manifest.py`
- **Android status:** ✅ Full functionality in Termux

### `accessory_manager.py`
- **Android status:** ✅ Full functionality in Termux
- **JIT UI (`--jit-ui`):** Requires Ollama running in Termux.
  Install with: `curl https://ollama.com/install.sh | bash`

### `usb_bridge.py`
- **Android status:** ✅ Works via USB-OTG with Termux
- **Notes:** Plug sensor into BV9900Pro USB-C OTG adapter.
  `pyserial` detects `/dev/ttyUSB0` or `/dev/ttyACM0`.
  Termux needs storage permission to access `/dev/ttyUSB*`.
  If port not visible: `ls /dev/tty*` in Termux.

### `log_ingest.py`
- **Android status:** ✅ Full functionality in Termux
- **Notes:** Reads log files from `experiments/` directory. All log paths
  are relative — works identically in Termux.

### `audit_log.py`
- **Android status:** ✅ Full functionality in Termux

### `adb_audio_bridge.sh`
- **Android status:** ✅ Designed for ADB use (from laptop)
- **Notes:** This script runs on the *laptop*, not on the phone. It bridges
  the phone's mic/speaker to the laptop's audio pipeline via ADB.

---

## BV9900Pro-HomeTest Scripts

### `sentinel_watchdog.py`
- **Android status:** ✅ Runs via ADB from laptop; ✅ runs in Termux on-device
- **On-device mode:** When running in Termux, replace ADB shell calls with
  direct Android API calls via Termux:API:
  ```bash
  pkg install termux-api
  ```
  - Battery: `termux-battery-status`
  - Temperature: `termux-sensor -s "Battery Temperature"` or `/sys/class/thermal/`
  - Storage: `df -h /data`

### `sentinel_commentary.py`
- **Android status:** ✅ Runs in Termux; requires Ollama or API key
- **`--humanize` flag:** Full support on Android

---

## Termux:API Integration

Install the Termux:API add-on for richer on-device sensor access:

```bash
pkg install termux-api
```

| Termux:API command | Android sensor | Replaces |
|---|---|---|
| `termux-location` | GPS | `adb shell dumpsys location` |
| `termux-battery-status` | Battery level + temp | `adb shell dumpsys battery` |
| `termux-sensor` | All sensor readings | `adb shell dumpsys sensorservice` |
| `termux-microphone-record` | Microphone (alternative) | PyAudio PortAudio |
| `termux-tts-speak` | Text-to-Speech | ElevenLabs TTS |
| `termux-notification` | Push notifications | Manual logging |

---

## ggwave Library on Android

| Feature | Status |
|---|---|
| Python bindings via pip | ✅ Works in Termux |
| C++ source compilation | ✅ Via Android NDK (arm64-v8a, armeabi-v7a) |
| WASM build | ✅ Via Chromium WebView in Android |
| JavaScript bindings | ✅ Via Node.js in Termux |
| Protocol 0 (NORMAL) | ✅ Best ECC, ~8 bytes/sec |
| Protocol 1 (FAST) | ✅ Higher throughput, ~16 bytes/sec |
| Protocol 2 (FASTEST) | ✅ Minimal ECC — avoid in noisy environments |
| DT variants | ✅ No-ECC — do not use in production |

---

## What Requires Modification for Android

| Component | Modification needed |
|---|---|
| `broadcast.py --adb-gps` | Replace ADB GPS pull with `termux-location` when running on-device |
| GIBBERLINK_SECRET | Replace `.env` file with Android Keystore for production APK |
| `sentinel_watchdog.py` battery/temp | Replace `adb shell dumpsys` calls with Termux:API equivalents when on-device |
| Background execution | Use Termux:Boot + `nohup` or `screen`; native app needs Foreground Service |

Everything else works without any modification.

---

## Dependency Version Matrix

| Package | Minimum version | Tested version | Source |
|---|---|---|---|
| Python | 3.9 | 3.11 | Termux `pkg install python` |
| ggwave | 0.4.0 | 0.4.2 | `pip install ggwave` |
| numpy | 1.21 | 1.26 | `pip install numpy` |
| pyaudio | 0.2.11 | 0.2.14 | `pip install pyaudio` |
| requests | 2.28 | 2.31 | `pip install requests` |
| bleak | 0.19 | 0.21 | `pip install bleak` (for BLE) |
| pyserial | 3.5 | 3.5 | `pip install pyserial` (for USB-OTG) |

---

*EXISTING_TECH.md — Android/docs/ — v1.0 — 2026-04-18*
