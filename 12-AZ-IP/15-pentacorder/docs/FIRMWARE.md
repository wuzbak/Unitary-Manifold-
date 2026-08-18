# FIRMWARE.md — Android Platform Firmware & Updates
## Security patches, OTA strategy, ADB firmware commands, and Android Keystore

---

## Overview

"Firmware" on Android covers three distinct layers:
1. **Android OS security patches** — monthly patches from Google/manufacturer
2. **Baseband firmware** — modem firmware (irrelevant to ggwave, important for
   cellular emergency broadcast fallback)
3. **Application layer updates** — Termux packages, Python, ggwave library

This document covers all three plus the Android Keystore integration roadmap.

---

## 1. Android OS Security Patch Cadence

### BV9900 Pro
- **Manufacturer:** Blackview
- **Chipset:** MediaTek Helio P90 (MT6779)
- **Update frequency:** Quarterly (typical for Blackview rugged phones)
- **Latest known patch level:** Check: Settings → About Phone → Android Security Patch Level
- **OTA check command:**
  ```bash
  adb shell settings get global software_version
  adb shell getprop ro.build.version.security_patch
  ```
- **Risk level:** Quarterly patch cadence is acceptable for a field sensor node
  that is not exposed to the open internet. Use ADB over USB (not TCP/IP) unless
  on a trusted network.

### Samsung Galaxy S24 Ultra
- **Manufacturer:** Samsung
- **Chipset:** Qualcomm Snapdragon 8 Gen 3
- **Update frequency:** Monthly (Samsung flagship guarantee: 4 years OS + 5 years security)
- **Check:**
  ```bash
  adb shell getprop ro.build.version.security_patch
  # Expected: 2026-03-01 or newer
  ```
- **Recommendation:** Keep the S24 Ultra on the latest available patch. It is a
  daily-driver with regular internet exposure.

### Minimum Acceptable Security Patch Level

| Device | Minimum acceptable patch | Reason |
|---|---|---|
| BV9900 Pro | 2024-01-01 | Baseline for Android 10 kernel vulnerabilities |
| S24 Ultra | Rolling (< 3 months old) | Daily-driver; full internet exposure |
| Generic Android node | 2024-01-01 | Covers CVE-2023-4863, Stagefright class |

---

## 2. Termux Package Updates

Run inside Termux on each device. Recommended: monthly, or before any
new Gibberlink session.

```bash
# Update all Termux packages
pkg update && pkg upgrade -y

# Update Python packages
pip install --upgrade ggwave numpy pyaudio requests

# Check ggwave version
python3 -c "import ggwave; print(ggwave.__version__)"
# Expected: 0.4.2 or newer

# Verify no breaking changes in ggwave API
python3 -c "
import ggwave
# Test encode still works
data = ggwave.encode('test', protocolId=1, volume=15)
print('encode OK, bytes:', len(data))
"
```

---

## 3. ggwave Library Version Policy

| ggwave version | Status | Notes |
|---|---|---|
| < 0.4.0 | ❌ Do not use | Missing `protocolId` parameter in Python bindings |
| 0.4.0 | ✅ Minimum | Stable encode/decode API |
| 0.4.2 | ✅ Recommended | Reed-Solomon ECC improvements |
| 0.5.x (future) | 🔲 Test before upgrade | Monitor for API changes in `encode()`/`decode()` signatures |

**Before upgrading ggwave:**
1. Run the full roundtrip test: `python scripts/roundtrip_test.py --auth`
2. Verify decode success rate is ≥ 90% before and after
3. Check `PROTOCOL.md` and `ROADMAP.md` — ggwave 0.5.x may add new protocol IDs

---

## 4. ADB Firmware Information Commands

Check device firmware state from a connected laptop:

```bash
# Android version
adb shell getprop ro.build.version.release

# Security patch date
adb shell getprop ro.build.version.security_patch

# Baseband (modem) firmware version
adb shell getprop gsm.version.baseband

# Kernel version
adb shell uname -r

# Build fingerprint (full firmware identifier)
adb shell getprop ro.build.fingerprint

# Available system updates (Samsung)
adb shell settings get global fota_update_status

# Storage state
adb shell df -h /data

# Battery health
adb shell dumpsys battery | grep -E "level|health|temperature|voltage"
```

---

## 5. Android Keystore Integration (Phase A9)

The Android Keystore replaces the `GIBBERLINK_SECRET` environment variable
with a hardware-backed key that never leaves the Secure Enclave.

### Architecture

```
Current (Termux):
  GIBBERLINK_SECRET=<hex> stored in .env (file on internal storage)
  ↓ loaded as environment variable
  acoustic_auth.py HMAC computation

Target (Native App):
  Key created in Android Keystore / StrongBox
  ↓ key ID only stored in app preferences
  ↓ HMAC computed inside Keystore (key never exposed)
  GibberKeyManager.computeHMAC(data) → tag
```

### Implementation (Phase A9)

```kotlin
// Create a non-exportable key in the Android Keystore
val keyGenerator = KeyGenerator.getInstance(
    KeyProperties.KEY_ALGORITHM_HMAC_SHA256,
    "AndroidKeyStore"
)
keyGenerator.init(
    KeyGenParameterSpec.Builder(
        "GibberSecretKey_${mode}",
        KeyProperties.PURPOSE_SIGN or KeyProperties.PURPOSE_VERIFY
    )
    .setKeySize(256)
    // Require StrongBox (hardware security module) if available
    .setIsStrongBoxBacked(true)
    .build()
)
keyGenerator.generateKey()

// Compute HMAC using the stored key (key never leaves hardware)
val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
val secretKey = keyStore.getKey("GibberSecretKey_${mode}", null) as SecretKey
val mac = Mac.getInstance(KeyProperties.KEY_ALGORITHM_HMAC_SHA256)
mac.init(secretKey)
val tag = mac.doFinal(data).take(4).toByteArray()
```

### StrongBox Availability

| Device | StrongBox | Notes |
|---|---|---|
| BV9900 Pro | ❌ No StrongBox | MediaTek Helio P90 does not include discrete HSM; uses TEE-based keystore instead |
| S24 Ultra | ✅ StrongBox | Samsung Knox with discrete security chip; hardware-attestable keys |
| Pixel 8 / 9 | ✅ Titan M2 | Google's purpose-built security chip |

**Fallback:** If StrongBox is unavailable, Android Keystore uses the ARM TrustZone
TEE (Trusted Execution Environment), which is still hardware-isolated and
significantly more secure than a plaintext `.env` file.

---

## 6. Over-the-Air Update Strategy

For production deployments with multiple Android nodes in the field:

### Termux-based OTA (current)

```bash
# On each device, pull latest repo
cd ~/diary && git pull

# Update Python packages
pip install --upgrade ggwave numpy pyaudio requests

# Restart services
pkill -f upb_hub.py
pkill -f sentinel_watchdog.py
~/.termux/boot/start-gibberlink.sh &
```

### Automated OTA (Phase A5+)

1. Add a `version.txt` to the repo with a semver string
2. `sentinel_watchdog.py` checks `version.txt` on each poll cycle
3. If local version < repo version: pull + restart (with audit log entry)
4. Add `SYSTEM:UPDATE_APPLIED` intent tag to the watchdog log

---

## 7. Security Hardening Checklist

Run this checklist before deploying any device in the field:

```
[ ] Android security patch < 3 months old
[ ] ADB disabled (Settings → Developer Options → USB Debugging → OFF)
    (Enable only during development sessions)
[ ] Screen lock enabled (PIN/biometric)
[ ] GIBBERLINK_SECRET unique per mode (separate RED, GREEN, BLUE secrets)
[ ] .env file present and not committed to git
[ ] Termux battery optimization exemption set
    (Settings → Battery → App battery usage → Termux → Unrestricted)
[ ] ggwave >= 0.4.2 installed
[ ] All scripts pass roundtrip test before field deployment
[ ] experiments/ directory writable (for audit logs)
```

---

*FIRMWARE.md — Android/docs/ — v1.0 — 2026-04-18*
