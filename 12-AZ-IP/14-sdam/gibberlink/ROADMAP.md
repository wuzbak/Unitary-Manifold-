# ROADMAP.md — Gibberlink Project
## Planned experiments, integrations, and open questions

---

## PHASE 0 — Understand the Stack ✅ (SESSION 001)

- [x] Read and document the Gibberlink protocol
- [x] Understand ggwave FSK encoding scheme
- [x] Map connections to BV9900Pro and Unitary-Manifold
- [x] Create project scaffold (this folder)

---

## PHASE 1 — Local Decode ✅ (SESSION 002)

Goal: Be able to decode a ggwave signal from audio without any AI stack.
Just raw acoustic decoding first.

- [x] Install ggwave Python bindings (`pip install ggwave`)
- [x] Write `scripts/decode_wav.py` — decode a .wav file using ggwave
- [ ] Download the YouTube demo audio and decode it locally
  - Source: https://www.youtube.com/watch?v=EtNagNezo8w
- [ ] Verify decoded payload matches what the Gibberlink demo sends
- [ ] Document the FSK frequency bands used (from ggwave source)

---

## PHASE 2 — Encode/Decode Round-Trip ✅ (SESSION 002)

Goal: Send a message, encode it to audio, play it, capture it, decode it.

- [x] Write `scripts/encode_message.py` — encode a string to ggwave audio
- [x] Write `scripts/roundtrip_test.py` — encode → play → record → decode
- [ ] Test on laptop speakers/mic first
- [ ] Test on BV9900Pro speakers/mic via ADB audio bridge
- [ ] Document bandwidth, error rate, and latency observations

---

## PHASE 3 — BV9900Pro Integration (SESSION 002 — scripts written, tests pending)

Goal: The phone as a Gibberlink node.

- [x] Write `scripts/adb_audio_bridge.sh` — ADB audio pipeline
- [x] Document full integration plan in `docs/BV9900PRO_INTEGRATION.md`
- [ ] Use ADB to stream audio from phone mic to laptop for decoding
- [ ] Use ADB to play encoded ggwave audio through phone speaker
- [ ] Run Experiment 3.1 (laptop → phone transmit)
- [ ] Run Experiment 3.2 (phone → laptop receive)
- [ ] Run Experiment 3.3 (phone ↔ phone, no laptop in loop)
- [ ] Document in `BV9900Pro-HomeTest/docs/GIBBERLINK_INTEGRATION.md`

---

## PHASE 4 — Two-Agent Demo (Local)

Goal: Run the Gibberlink demo locally — two agents, language switch included.

- [ ] Clone `PennyroyalTea/gibberlink` locally (outside this repo)
- [ ] Set up `.env` with ElevenLabs + LLM API keys (not committed)
- [ ] Run `npm install && npm run dev`
- [ ] Use ngrok or two devices on LAN
- [ ] Record a full session: English → ggwave switch → decode
- [ ] Document the full flow in `docs/DEMO_RUN.md`

---

## PHASE 5 — Manifold Connection

Goal: Frame a Gibberlink transmission as an instance of the Unitary-Manifold
information current `J^μ_inf`.

- [ ] Identify which manifold test module maps to acoustic information channels
- [ ] Measure: payload size, transmission time, error rate → compute entropy flux
- [ ] Write a note connecting `∇_μ J^μ_inf = 0` to ggwave ECC (no info lost)
- [ ] Add a test case or annotation in the relevant manifold module

---

## PHASE 6 — Human Impact Experiments

Goal: Validate the four human-impact claims (time reclamation, offline
resilience, accessibility, energy efficiency) with real measurements.

- [ ] **Auditability first:** Add decoded transcript logging to all scripts
      (every ggwave exchange → timestamped human-readable log in `experiments/`)
- [ ] **Time measurement:** Time a real task (hotel booking simulation) via
      voice TTS/STT pipeline vs. ggwave — record actual latencies
- [ ] **Offline proof:** Run full Phase 4 demo with zero internet (Ollama + ggwave)
      and document that it works with no cloud dependency
- [ ] **Energy measurement:** Measure CPU/GPU utilization + wall-clock energy
      for TTS synthesis vs. ggwave encode for equivalent payload;
      compute Joules/byte for each (maps to manifold Phase 5)
- [ ] **Accessibility prototype:** Wire local agent loop to accept text input
      (simulating AAC device) and output via ggwave — no voice required on
      the human side
- [ ] Write `experiments/exp_6_time_reclamation.md`
- [ ] Write `experiments/exp_6_energy_comparison.md`

See `docs/HUMAN_IMPACT.md` for full analysis of each dimension.

---

## PHASE 7 — Security & Auditability ✅ (SESSION 003)

Goal: Harden the acoustic channel against ghost injection, replay attacks,
and handshake desync. Make every exchange human-auditable.

- [x] Write `scripts/acoustic_auth.py` — HMAC-SHA256 session authentication
  - Three-way handshake (ACH → ARS → AOK): neither side enters data mode
    until both have verified the peer's token
  - Rolling HMAC counter per payload: prevents replay of recorded chirps
  - 4-byte truncated tag: adequate security, minimal ggwave overhead (~18 chars)
  - Heartbeat frames (AHB) every 1s + 3-second desync timeout → `ATO` abort
  - `GIBBERLINK_SECRET` env var only — never hardcoded
- [x] Write `scripts/audit_log.py` — centralized mandatory audit logger
  - Writes to `experiments/transcript.log` (human-readable) simultaneously
    with `experiments/audit.jsonl` (JSON Lines, machine-readable)
  - Records decode success rate per session (windows scanned / decoded)
  - `python scripts/audit_log.py --summary` for aggregate auth-failure stats
- [x] Write `scripts/noise_calibrate.py` — log-linear chirp calibration
  - 20 Hz → 20 kHz log-linear chirp (2s, equal time per octave)
  - Detects BV9900 Pro waterproof membrane roll-off at 100 Hz resolution
  - Maps roll-off frequency → safe ggwave protocol ceiling
  - Saves `experiments/calibration.json`; other scripts load it via `--calibrate`
- [x] All scripts (`encode_message`, `decode_wav`, `roundtrip_test`) updated
  - `AuditLog` replaces all ad-hoc file writes
  - `--auth` / `--session` / `--counter` flags on encode + decode
  - `--mode` flag loads GREEN/RED/BLUE defaults
  - `--calibrate` flag loads calibration profile
- [x] Write `docs/SECURITY.md` — full security reference
  - Threat model, wire format spec, honest limits, secret management guide

---

## PHASE 8 — Common Acoustic Bus ✅ (SESSION 003)

Goal: Gibberlink is not just "fast chat" — it is the low-level acoustic data
link for the entire Manifold sensor ecosystem. Three modes, typed payloads,
first real sensor broadcast.

- [x] Write `scripts/modes.py` — GREEN / RED / BLUE operational mode registry
  - 🟢 GREEN: passive sensor listening (protocol 1, vol 15, auth optional)
  - 🔴 RED: emergency broadcast (protocol 0, vol 80, auth required, 3× redundancy)
  - 🔵 BLUE: secure health transfer (protocol 1, vol 20, auth mandatory, range ~1 m)
  - `python scripts/modes.py --all` to view all mode settings
- [x] Write `scripts/broadcast.py` — typed payload encoder
  - Payload types: GPS, SYS, ENV, VITALS, ALERT, RAW
  - `--adb-gps` flag: pulls live GPS + battery from BV9900 Pro via ADB
    (`adb shell dumpsys location` + `adb shell dumpsys battery`)
  - Mode-aware redundancy: RED broadcasts each burst 3× with 300 ms gaps;
    receiver deduplicates by counter
  - Full audit log on every burst
- [ ] Run first live Red mode GPS broadcast from BV9900 Pro
- [ ] Test drone overhead reception (outdoor, 3–5 m range experiment)
- [ ] Green mode: deploy first field sensor node (soil moisture prototype)
- [ ] Blue mode: bedside vitals transfer test between two phones

---

## PHASE 9 — Accessory Manifest Protocol ✅ (SESSION 004)

Goal: Acoustic Plug-and-Play.  Any accessory can describe itself to the
Sentinel Manager by chirping a Manifest.  The Manager validates it, registers
the device, and optionally generates a JIT UI via a local LLM.  Dumb USB
sensors get a Legacy Bridge.  Pylons get a PING/PONG protocol.

- [x] Add `MNFT`, `PING`, `PONG` payload type helpers to `scripts/modes.py`
  - `make_manifest_payload(device_id, model, fields, seq, total)`
  - `make_ping_payload(requestor_id, counter)`
  - `make_pong_payload(device_id, counter, battery_pct, reading)`
  - `GREEN` payload_types updated to include MNFT, PING, PONG
- [x] Write `scripts/manifest.py` — Manifest builder, signer, emitter, parser, validator
  - `build_bursts()` — auto-splits large manifests across multiple ggwave bursts
  - `parse_manifest_payload()` — parses raw MNFT string to structured dict
  - `validate_manifest()` — schema sanity checks (types, units, ranges, seq/total)
  - `manifest_fingerprint()` — 8-char SHA-256 change-detection hash
  - `emit_manifest()` — builds + signs + broadcasts via `broadcast()`
  - CLI: `manifest.py build | validate | parse | emit`
- [x] Write `scripts/accessory_manager.py` — Sentinel Accessory Manager
  - `AccessoryRegistry` — file-backed JSON registry keyed by device_id
  - `ManifestAssembler` — reassembles multi-burst manifests from seq/total fragments
  - `generate_jit_ui()` — Ollama HTTP call, returns JSON UI descriptor
  - `_fallback_ui()` — deterministic fallback when Ollama is offline
  - PING handler — logs inbound pings; PONG handler — updates registry
  - CLI: `accessory_manager.py listen | test | ping | registry`
  - `--jit-ui` flag enables Ollama JIT UI generation
- [x] Write `scripts/usb_bridge.py` — USB-OTG Legacy Bridge
  - Auto-discovers `/dev/ttyUSB*` / `/dev/ttyACM*`; `--wait` flag polls for arrival
  - Parses JSON lines, CSV, or raw text from the USB device
  - Wraps readings in `RAW:` payload with GPS + timestamp metadata
  - Optional `--manifest` flag: emits an MNFT before the data stream starts
  - `--simulate` flag: offline test without hardware
- [ ] Run full test loop on laptop:
  - `manifest.py emit --dry-run` → verify MNFT payload string
  - `accessory_manager.py test --jit-ui` → verify JIT UI descriptor
  - `usb_bridge.py --simulate '{"co2": 1234, "temp": 21.3}' --dry-run`
- [ ] Test with real hardware:
  - CO2 sensor (SCD41 or MH-Z19B) via USB-OTG on BV9900 Pro
  - Two phones: Phone A emits Manifest, Phone B runs `accessory_manager.py listen`
- [ ] First Pylon test: three devices, `ping` from sentinel, PONGs collected

---

## PHASE 10 — Universal Token Standard ✅ (SESSION 005)

Goal: Define the common language that lets the Intent Engine reason over any
physical-layer signal without caring about its transport protocol.

- [x] Add `INTENT` and `TRANSLATE` payload types to `scripts/modes.py`
  - `make_intent_payload()` — wraps any cross-protocol token in a normalised envelope
  - `make_translate_payload()` — cross-modal/lingual translation request
  - Both types registered in GREEN, RED, and BLUE mode `payload_types` lists
- [x] Write `docs/TOKEN_STANDARD.md` — full schema reference
  - Common Token Schema v1.0 field set and wire format
  - Source protocol enum: SDR | BLE | ACOUSTIC | SPEECH | USB | SYSTEM | NETWORK
  - Intent tag enum: ALERT | QUERY | TELEMETRY | HANDSHAKE | RELAY
  - Parallel input buffer architecture diagram
  - Relay routing table (Phase 12)
  - Intent tagging patterns for sentinel logs (Phase 13)
- [ ] Test INTENT + TRANSLATE payload round-trip through ggwave encode/decode

---

## PHASE 11 — Parallel Input Buffers ✅ (SESSION 005)

Goal: Run concurrent protocol listeners without stream collision.

- [x] Write `scripts/upb_hub.py` — Universal Protocol Bridge Hub
  - `CommonToken` dataclass — normalised schema v1.0 token
  - `normalize_token()` — builds a CommonToken from any raw ingestor reading
  - Named per-protocol queues: `Q_BLE`, `Q_SDR`, `Q_ACOUSTIC`, `Q_SPEECH`
  - One drain thread per queue, all feeding `Q_INTENT`
  - `IngestorBase` abstract class + `AcousticIngestor` + `MockIngestor`
  - `UniversalProtocolBridge` hub: starts threads, manages Q_INTENT
  - `intent_callback` hook — connects directly to LLM / RAG bot
  - CLI: `upb_hub.py relay | simulate | status | inject`
- [ ] First live test: two physical channels active simultaneously
- [ ] Hook `intent_callback` to RAG bot POST endpoint

---

## PHASE 12 — Cross-Protocol Relay ✅ (SESSION 005)

Goal: SDR 1st Responder alert → automatic Gibberlink acoustic re-broadcast.

- [x] `RelayRule` dataclass with wildcard "*" support (first-match-wins)
- [x] `DEFAULT_RELAY_RULES`:
  - SDR/ALERT → red, BLE/ALERT → red, USB/ALERT → red, SYSTEM/ALERT → red
  - */RELAY → green (explicit relay passthrough)
- [x] `UniversalProtocolBridge._relay()` evaluates rules, calls `broadcast.py`
- [ ] Live test: `python scripts/upb_hub.py simulate --source SDR --intent ALERT --dry-run`
- [ ] Configurable rules file (JSON) for runtime customisation

---

## PHASE 13 — Intent Tagging in Session Logs ✅ (SESSION 005)

Goal: Seed RAG bot semantic search by tagging every watchdog record with why.

- [x] `intent` field added to every `sentinel_watchdog.py` JSONL record:
  - `"AUTO:POLL"` | `"MANUAL_TRIGGER:ONCE"` | `"AUTO:THERMAL_THROTTLE+BATTERY_HOT"`
- [ ] First real field session — verify `intent` appears in logs
- [ ] RAG bot query: "When did the device last overheat?"

---

## PHASE 14 — Semantic Search over Everything ✅ (SESSION 005)

Goal: Unify all log types into a single CommonToken corpus for the RAG bot.

- [x] Write `scripts/log_ingest.py` — multi-source log normaliser
  - Reads sentinel_*.jsonl + audit.jsonl + transcript.log + upb_audit.jsonl
  - Outputs `experiments/upb_corpus.jsonl` — drop-in RAG document corpus
  - CLI: `log_ingest.py [--summary | --stdout | --output PATH]`
- [ ] Ingest `upb_corpus.jsonl` into RAG bot corpus directory
- [ ] Test query: "What did the sensor say right before the power went out?"

---

## PHASE 15 — Machine-to-Human Intuition Interface ✅ (SESSION 005)

Goal: Translate cold telemetry into human-relatable experiential language.

- [x] `--humanize` flag added to `BV9900Pro-HomeTest/scripts/sentinel_commentary.py`
  - `build_humanized_prompt()` + `_HUMANIZED_ANALYSIS` instruction block
  - No jargon: "CPU throttling" → "device feels exhausted and needs a rest"
  - Output: mood (CALM/STRESSED/EXHAUSTED/CRITICAL) + narrative + action
- [ ] Test `--humanize` against real anomaly records
- [ ] Compare standard vs humanized output — validate framing for non-technical users

---

## PHASE 16 — RF-Spatial Sensing ✅ (SESSION 006)

Goal: Add WiFi/CSI-based spatial awareness as a new protocol channel in the
UPB Hub.  Complements the acoustic channel — "hearing" plus "feeling the
structure of the space."

- [x] Add `CSI` to `VALID_PROTOCOLS` in `upb_hub.py`
  - New `Q_CSI = ProtocolQueue("CSI")` with dedicated drain thread
  - `_queue_for()` and `status()` updated to include CSI channel
  - Hub startup message updated: "BLE, SDR, ACOUSTIC, SPEECH, CSI"
- [x] Add `make_spatial_payload()` to `scripts/modes.py`
  - Wire format: `SPATIAL:{source_id}:{zone_fp12}:{bssid}:{dist_m}:{n}:{flags}:{lat},{lon}`
  - Flags: M=movement, G=GPS-fused, C=CSI (vs RSSI-only), −=none
  - `SPATIAL` registered in GREEN and RED payload_types
- [x] Write `Gibberlink/docs/RF_SPATIAL.md` — full RF-Spatial reference
  - RSSI-only mapper (available now, no hardware)
  - ESP32-S3 CSI sniffer bridge pattern ($7, no root)
  - ESP32-CSI-Tool firmware setup
  - UPB Hub Q_CSI integration and SPATIAL wire format
  - IEEE 802.11bf roadmap note
  - Gibberlink + RF-Spatial cross-reference session pattern
- [x] Write `scripts/csi_processor.py` — CSI stream → subcarrier variance → SPATIAL token emitter
  - Sliding window variance per subcarrier (φ-deviation vs. static baseline)
  - Weighted centroid azimuth estimate → room-relative (x, y) coordinates
  - Manifold framing: δH_μν perturbation, ∇_μ J^μ_inf = 0 zero-crossing locates object
  - `--emit-token` flag → CommonToken JSON to stdout for UPB Hub Q_CSI
  - `--demo` mode: synthetic object sweep without hardware
  - `--once`, `--alerts-only`, `--log`, `--dry-run`, `--device`, `--baud` flags
  - ADB pipeline: `adb shell 'cat /dev/ttyUSB0' | python csi_processor.py --emit-token`
- [x] Add `csi_source` flag to `make_spatial_payload()` in `modes.py` (C flag in wire format)
- [x] Add CSI/ALERT relay rule to DEFAULT_RELAY_RULES in `upb_hub.py`
- [ ] Flash ESP32-S3 with ESP32-CSI-Tool, verify USB-OTG on BV9900 Pro
- [ ] Wire `usb_bridge.py` to parse CSI JSON stream → Q_CSI tokens

---

## OPEN QUESTIONS

- Can ggwave operate through a physical wall (adjacent room)?
- What is the maximum reliable payload size per burst?
- Can the BV9900Pro's APU 2.0 run real-time ggwave decode natively?
- Is there a way to use the phone's NFC + ggwave together for a two-channel
  AI agent handshake?
- Can we substitute a non-ElevenLabs LLM (local, e.g., Ollama) for the
  language negotiation layer?
- What does the user experience of "hearing the beep and reading the log"
  feel like in practice — more or less agency than listening to hold music?
- At what range does Blue mode vol=20 become unreliable? (Test: 0.5 m, 1 m, 2 m)
- Can AES-256 payload encryption fit within ggwave's bandwidth budget?

---

*ROADMAP.md — Gibberlink/ — v1.4 — 2026-04-18*
