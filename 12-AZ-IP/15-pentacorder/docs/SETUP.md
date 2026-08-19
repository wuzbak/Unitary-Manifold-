# SETUP.md — Android Platform Full Install Guide
## Step-by-step for BV9900Pro, S24 Ultra, and generic Android

---

## Prerequisites

- Android 8.0+ (API 26 minimum; Android 12+ recommended)
- Termux installed from F-Droid: https://f-droid.org/packages/com.termux/
- Termux:Boot installed from F-Droid (for auto-start): https://f-droid.org/packages/com.termux.boot/
- Developer Options enabled (Settings → About Phone → tap Build Number 7×)
- USB Debugging enabled (Settings → Developer Options → USB Debugging)
- ADB installed on your laptop (Platform Tools package)

---

## Part 1 — Automated Setup (Recommended)

Run the setup script inside Termux:

```bash
# Download and run
curl -fsSL https://raw.githubusercontent.com/wuzbak/diary/main/Android/scripts/setup_android.sh | bash

# OR if the repo is already cloned
bash ~/diary/Android/scripts/setup_android.sh
```

This script handles Steps 1–7 automatically. Skip to Part 3 after it completes.

---

## Part 2 — Manual Setup (Step by Step)

### Step 1 — Update Termux

```bash
pkg update && pkg upgrade -y
```

### Step 2 — Install system dependencies

```bash
pkg install -y python python-pip portaudio libzmq git curl wget
```

**Why portaudio?** Termux's PyAudio package is compiled against PortAudio, which
provides the cross-platform audio I/O that ggwave requires for live mic capture
and speaker playback.

### Step 3 — Install Python packages

```bash
pip install ggwave numpy pyaudio requests
```

Verify:
```bash
python3 -c "import ggwave; print('OK')"
python3 -c "import pyaudio; print('OK')"
```

If `pyaudio` fails, try:
```bash
pkg install portaudio-dev
pip install pyaudio --no-binary :all:
```

### Step 4 — Clone the repo

```bash
git clone https://github.com/wuzbak/diary.git ~/diary
cd ~/diary/Gibberlink
```

### Step 5 — Generate a Gibberlink session secret

```bash
python scripts/acoustic_auth.py keygen
# Output: a 64-character hex string
echo "GIBBERLINK_SECRET=<paste-output-here>" > .env
export GIBBERLINK_SECRET=$(grep GIBBERLINK_SECRET .env | cut -d= -f2)
```

**Important:** Share this secret with peer devices via QR code, NFC tap, or
manual entry — out of band, never over the air. Each mode (GREEN/RED/BLUE)
should use a separate secret in production.

### Step 6 — Create experiments directory

```bash
mkdir -p ~/diary/Gibberlink/experiments
```

### Step 7 — Verify the full stack

```bash
cd ~/diary/Gibberlink
python scripts/acoustic_auth.py challenge
# Should print: ACH:xxxx:yyyyyyyy
python scripts/modes.py --all
# Should print: GREEN / RED / BLUE mode tables
```

---

## Part 3 — Device Calibration

Calibration maps your device's speaker/mic response curve so ggwave protocols
stay within the reliable frequency range.

### BV9900Pro calibration

The BV9900Pro has a waterproof membrane that may attenuate frequencies above
a certain threshold. Identify the safe ceiling before deploying RED mode.

```bash
# Loopback test: play through speaker and record with mic simultaneously
python scripts/noise_calibrate.py --sweep --play
# Saves: experiments/calibration.json
# Review: cat experiments/calibration.json | python -m json.tool
```

Expected output: a `safe_ceiling_hz` field. If below 8 kHz, use Protocol 0
(NORMAL) instead of Protocol 1 (FAST) for RED mode broadcasts.

### S24 Ultra calibration

```bash
python scripts/noise_calibrate.py --sweep --play
# Note: Dolby Atmos EQ may affect FSK response. Check calibration.json.
```

### Generic device

Same command. Run it in a quiet room. The result tells you which ggwave
protocol is safe for your hardware.

---

## Part 4 — Verify Core Scripts

```bash
cd ~/diary/Gibberlink
export GIBBERLINK_SECRET=$(grep GIBBERLINK_SECRET .env | cut -d= -f2)

# Test encode
python scripts/encode_message.py "test" --mode green --auth
# Should create experiments/encoded.wav

# Test decode
python scripts/decode_wav.py experiments/encoded.wav --mode green --auth
# Should print: test

# Test broadcast (dry run — no audio played)
python scripts/broadcast.py --mode red gps --lat 37.77 --lon -122.41 --dry-run

# Test UPB Hub status
python scripts/upb_hub.py status
```

---

## Part 5 — Termux:Boot Auto-Start

After installing Termux:Boot from F-Droid:

```bash
mkdir -p ~/.termux/boot

cat > ~/.termux/boot/start-gibberlink.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
# Auto-start Gibberlink stack on device boot

source ~/diary/Gibberlink/.env
export GIBBERLINK_SECRET

cd ~/diary/Gibberlink

# UPB Hub (acoustic relay + intent engine)
python scripts/upb_hub.py relay >> ~/diary/Gibberlink/experiments/upb_boot.log 2>&1 &

# Sentinel Watchdog (on BV9900Pro only — remove on S24 Ultra if not wanted)
python ~/diary/BV9900Pro-HomeTest/scripts/sentinel_watchdog.py \
    >> ~/diary/BV9900Pro-HomeTest/sessions/watchdog_boot.log 2>&1 &

echo "Gibberlink stack started at $(date)" >> ~/diary/Gibberlink/experiments/boot.log
EOF

chmod +x ~/.termux/boot/start-gibberlink.sh
```

Test by rebooting the device. After boot, check:
```bash
cat ~/diary/Gibberlink/experiments/boot.log
```

---

## Part 6 — ADB Setup (Laptop Side)

Install Android Platform Tools on your laptop:
- **macOS:** `brew install android-platform-tools`
- **Windows:** Download from https://developer.android.com/tools/releases/platform-tools
- **Linux:** `sudo apt install android-tools-adb`

Connect the phone via USB, then:

```bash
adb devices
# Should show: <serial>   device

# Enable TCP/IP ADB (for wireless after initial USB connection)
adb tcpip 5555
adb connect <phone-ip>:5555
# Find phone IP: Settings → Wi-Fi → tap network → IP address
```

Now you can run all scripts remotely:
```bash
adb shell "cd ~/diary/Gibberlink && python scripts/upb_hub.py status"
```

---

## Part 7 — Ollama Local LLM (Optional but Recommended)

For the intent engine without cloud dependency:

```bash
# Install Ollama in Termux (ARM64 build)
curl -fsSL https://ollama.com/install.sh | bash

# Pull a small model (fits in 4 GB RAM)
ollama pull llama3.2:3b   # ~2 GB
# Or for higher quality on S24 Ultra (12 GB RAM):
ollama pull llama3.2:8b   # ~5 GB

# Verify
ollama run llama3.2:3b "Hello"

# Wire to accessory_manager.py
cd ~/diary/Gibberlink
python scripts/accessory_manager.py test --jit-ui
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `pyaudio` install fails | `pkg install portaudio-dev && pip install pyaudio --no-binary :all:` |
| `ggwave` install fails | Check Python version: `python --version` (need 3.9+); try `pip install ggwave==0.4.2` |
| No audio output | Check Termux audio permission: Settings → Apps → Termux → Permissions → Microphone |
| ADB not found | Install platform-tools; on macOS check `~/Library/Android/sdk/platform-tools/` |
| Background process killed | Enable Termux in battery optimization exclusion list |
| Calibration shows `safe_ceiling_hz < 3000` | Try running in a quieter environment; check for waterproof membrane attenuation |

---

*SETUP.md — Android/docs/ — v1.0 — 2026-04-18*
