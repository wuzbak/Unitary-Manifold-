# Gibberlink — AI-to-AI Acoustic Communication

> **Goal:** Understand, decode, and experiment with the Gibberlink protocol —
> the open-source AI-to-AI "secret language" that uses acoustic data-over-sound
> to let machine agents communicate at ~80% greater efficiency than human speech.
> Extended in Session 003 to a **Common Acoustic Bus** for sensor, emergency,
> and health data across GREEN / RED / BLUE operational modes.

GibberLink was created by Anton Pidkuiko and Boris Starkov at the ElevenLabs ×
a16z London Hackathon (Feb 2025). It won first place and went viral.

The core idea: two AI voice agents start a conversation in natural language.
The moment both confirm the other is an AI, they negotiate a switch to
**ggwave** — a data-over-sound FSK protocol. To human ears it sounds like
modem chirps. To machines it is a clean, structured binary channel.

---

## Connections to Other Projects

| This project | Links to |
|---|---|
| ggwave audio transmission | BV9900Pro microphone + speaker hardware |
| Agent-to-agent signaling | Unitary-Manifold information channel topology |
| Acoustic data encoding | BV9900Pro sensor data exfiltration experiments |
| AI identity detection | Manifold observer / measurement theory |
| Emergency GPS broadcast | BV9900Pro as Red-mode field responder node |
| Environmental sensors | Green-mode field nodes → Manifold test inputs |
| Health vitals transfer | Blue-mode bedside encrypted data transfer |

The BV9900 Pro has a full audio pipeline (microphone array, stereo speaker).
It is a natural physical platform for transmitting and receiving ggwave signals.

---

## Folder Structure

| Folder | Purpose |
|---|---|
| `docs/` | Protocol deep-dives, setup guides, architecture notes |
| `scripts/` | Python / Node utilities for encoding, decoding, demoing |
| `experiments/` | Recorded audio samples, decode logs, calibration profiles |
| `sessions/` | Session notes following standard diary convention |

---

## Scripts

| Script | Purpose |
|---|---|
| `encode_message.py` | Encode text → ggwave .wav (`--auth`, `--mode`, `--calibrate`) |
| `decode_wav.py` | Decode .wav → text (`--auth`, `--mode`, success-rate logging) |
| `roundtrip_test.py` | Encode → play → record → decode (`--auth`, `--mode`, `--calibrate`) |
| `acoustic_auth.py` | HMAC-SHA256 session auth: handshake, sign, verify, heartbeat |
| `noise_calibrate.py` | Log-linear chirp sweep (20Hz→20kHz), BV9900 Pro membrane detection |
| `audit_log.py` | Centralized audit logger: transcript.log + audit.jsonl |
| `modes.py` | GREEN / RED / BLUE mode registry + typed payload helpers |
| `broadcast.py` | Typed sensor broadcast: GPS, SYS, ENV, VITALS via ADB |
| `adb_audio_bridge.sh` | ADB audio pipeline: BV9900 Pro ↔ laptop |

---

## Operational Modes

| Mode | Color | Protocol | Volume | Auth | Redundancy | Use case |
|------|-------|----------|--------|------|------------|---------|
| Green | 🟢 | 1 (FAST) | 15 | Optional | 1× | Passive sensor listening |
| Red | 🔴 | 0 (NORMAL) | 80 | Required | 3× | Emergency broadcast (air-gapped GPS) |
| Blue | 🔵 | 1 (FAST) | 20 | Mandatory | 1× | Secure health data (≤1 m range) |

```bash
python scripts/modes.py --all          # view all mode settings
python scripts/broadcast.py --mode red gps --lat 37.77 --lon -122.41
python scripts/broadcast.py --mode red --adb-gps   # live from BV9900 Pro
```

---

## Quick Technical Facts

- **Transport:** FSK (Frequency-Shift Keying) over audio
- **Bandwidth:** 8–16 bytes/sec depending on protocol parameters
- **Error correction:** Reed-Solomon ECC built in
- **Auth overhead:** ~18 chars per signed payload (4-byte HMAC tag)
- **Heartbeat:** 1s interval; 3s silence → automatic revert to speech
- **Dependencies:** ggwave (C++ core, Python + JS + WASM bindings)
- **AI layer:** ElevenLabs Conversational AI + any LLM with tool-calling
- **Switch trigger:** client-side tool named `gibbMode` called when both agents
  confirm AI identity — machine-generated session token, LLM not in security path
- **Efficiency gain:** ~80% vs. equivalent human speech for same payload
- **License:** ggwave = MIT; gibberlink demo = MIT

---

## Key References

| Resource | URL |
|---|---|
| Official GitHub repo | https://github.com/PennyroyalTea/gibberlink |
| Live demo | https://www.gbrl.ai/ |
| ggwave library | https://github.com/ggerganov/ggwave |
| ggwave web decoder | https://waver.ggerganov.com/ |
| ggwave Python package | `pip install ggwave` |
| ElevenLabs showcase | https://showcase.elevenlabs.io/projects/p/gibberlink |
| Entro Security auth hierarchy | https://entro.security/blog/authentication-hierarchy-ai-agents/ — Gibberlink implements levels 1 (rolling HMAC per message) and 4 (long-lived shared secret); see `docs/SECURITY.md` |

---

## Phase Overview

See `docs/SETUP.md` for local reproduction steps.  
See `docs/PROTOCOL.md` for the full technical protocol breakdown.  
See `docs/SECURITY.md` for the threat model, wire format, and secret management.  
See `docs/LOCAL_LLM_STACK.md` for running without ElevenLabs (Ollama + Piper).  
See `docs/BV9900PRO_INTEGRATION.md` for using the phone as a Gibberlink audio node.  
See `docs/HUMAN_IMPACT.md` for analysis of real-world impact.  
See `ROADMAP.md` for planned experiments.

---

## Quick Start

```bash
# 1. Install
pip install ggwave numpy pyaudio

# 2. Generate a shared secret
python scripts/acoustic_auth.py keygen
export GIBBERLINK_SECRET=<your-64-hex-chars>

# 3. Calibrate for your hardware (BV9900 Pro: run with --play for loopback)
python scripts/noise_calibrate.py --sweep

# 4. Encode a signed message
python scripts/encode_message.py "Hello" --mode blue --auth --play

# 5. Decode + verify
python scripts/decode_wav.py experiments/encoded.wav --mode blue --auth

# 6. Red mode GPS emergency broadcast
python scripts/broadcast.py --mode red gps --lat 37.7749 --lon -122.4194

# 7. View audit log
python scripts/audit_log.py --tail 20
```

---

*README.md — Gibberlink/ — v1.3 — 2026-04-21 — AxiomZero Technologies*
