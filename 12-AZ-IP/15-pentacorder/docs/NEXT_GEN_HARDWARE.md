# NEXT_GEN_HARDWARE.md — Android Next-Generation Hardware Roadmap
## Optimising the Gibberlink/UPB stack for future Android silicon

---

## Overview

This document maps the trajectory of Android hardware improvements to specific
capability upgrades in the Gibberlink/UPB/Manifold stack. Each hardware
generation unlocks new features or dramatically improves existing ones.

---

## Current Baseline (2026)

| Device | Chip | NPU/APU | RAM | Audio | Status |
|---|---|---|---|---|---|
| BV9900 Pro | Helio P90 (MT6779) | APU 2.0 (~0.6 TOPS) | 8 GB | Dual mic, stereo | Operational |
| S24 Ultra | Snapdragon 8 Gen 3 | Hexagon NPU (~45 TOPS) | 12 GB | 4-mic array | Operational |

---

## 2026 — Generation: Snapdragon 8 Elite / Tensor G5

### Qualcomm Snapdragon 8 Elite (SM8750)
- **CPU:** 2× Oryon Prime @ 4.47 GHz + 6× Oryon Performance
- **NPU:** 45 TOPS (Hexagon, 2nd gen AI Engine)
- **Audio DSP:** Aqstic (hardware acoustic processing)
- **Devices:** Samsung Galaxy S25 Ultra, OnePlus 13, Xiaomi 15 Pro

**Gibberlink/UPB upgrade path:**

| Upgrade | How the hardware helps |
|---|---|
| ggwave decode on DSP | Aqstic DSP can offload FFT → reduces decode latency from ~20ms to ~2ms |
| On-device LLM (13B) | Oryon + 12 GB LPDDR5X can run Llama 3.1 13B in Termux reliably |
| Always-on mic pipeline | Hexagon Sensing Hub: run ggwave decode without waking main CPU |
| WiFi 7 multi-link | Q_NETWORK ingestor can receive from 3 bands simultaneously |

**Recommended next device (GREEN/BLUE hub):** Galaxy S25 Ultra

### Google Tensor G5 (Pixel 10)
- **Co-designed by Google + TSMC (3nm)**
- **NPU:** Purpose-built for Google's on-device AI (Gemini Nano)
- **Audio:** New "conversational AI" acoustic pipeline with hardware echo cancellation
- **Titan M3:** Next-gen hardware security chip for BLUE-mode key binding

**Gibberlink/UPB upgrade path:**

| Upgrade | How the hardware helps |
|---|---|
| Gemini Nano on-device | Intent engine with Google's architecture, no Ollama needed |
| Hardware echo cancellation | Improves ggwave decode in noisy/reverberant environments |
| Titan M3 StrongBox | BLUE-mode key material with hardware attestation |

**Recommended next device (BLUE-mode health node):** Pixel 10

---

## 2026–2027 — Generation: ARM Windows on Android (Cross-platform)

### Qualcomm Snapdragon X Elite on Android Tablets
- The same chip powering Copilot+ PCs is coming to Android tablets (Surface-class)
- 45 TOPS NPU + USB 3.2 + WiFi 7

**Gibberlink/UPB upgrade path:**

- Tablet form factor as a base station node (always plugged in, persistent
  ggwave listener running 24/7)
- USB 3.2 for fast ESP32-S3 CSI sniffer data ingestion
- DeX-like external display support for full UPB Hub dashboard

---

## 2027 — Generation: Qualcomm Snapdragon 8 Gen 5 (anticipated)

- **NPU:** ~70 TOPS (estimated based on roadmap)
- **Process:** TSMC 2nm
- **Wi-Fi:** Wi-Fi 7 with 6 GHz band MCS13 (theoretical 9.6 Gbps)
- **Bluetooth 6.0:** Channel Sounding (centimeter-level ranging)
- **Satellite:** Snapdragon Satellite (Iridium bidirectional) in mid-range tier

**Gibberlink/UPB upgrade path:**

| Upgrade | How the hardware helps |
|---|---|
| Bluetooth 6.0 Channel Sounding | Q_BLE ingestor gets centimeter spatial positions — UWB-class accuracy without UWB hardware |
| Snapdragon Satellite | RED-mode GPS broadcast with satellite relay — true air-gap, no local infrastructure |
| 70 TOPS NPU | Run 30B LLM on-device; intent engine handles complex multi-sensor reasoning |
| Wi-Fi 7 MCS13 | Q_NETWORK ingestor throughput → real-time video stream analysis |

---

## 2027–2028 — Generation: IEEE 802.11bf (Wi-Fi Sensing Standard)

The 802.11bf standard (finalized ~2024, devices arriving ~2027) formalizes
Wi-Fi CSI-based sensing as a standard feature of Wi-Fi chips.

**Current workaround:** ESP32-S3 CSI sniffer via USB-OTG (see `Gibberlink/docs/RF_SPATIAL.md`)

**With 802.11bf devices:**
- No external hardware needed — the phone's own Wi-Fi chip provides CSI data
  via standard kernel API
- Q_CSI ingestor reads directly from `/sys/kernel/wifi_sensing/csi`
- Eliminates the ESP32-S3 bridge entirely
- Room-scale spatial mapping without any additional hardware

**Action item:** When first 802.11bf Android devices ship (anticipated Pixel 11
or Samsung Galaxy S27 Ultra), update `usb_bridge.py` to detect the standard
kernel interface and add a direct CSI ingestor to `upb_hub.py`.

---

## 2028+ — Generation: Neuromorphic + Photonic

### Intel Loihi 3 (if Android-compatible)
- Spike-based neural computation: event-driven, not clock-driven
- Perfectly suited for acoustic event detection (ggwave chirp = spike event)
- Power consumption: milliwatts vs. ~2W for current NPU decode
- **Application:** Always-on ggwave decode with <1mW idle power

### Photonic Communication Chips
- Li-Fi (IEEE 802.11bb ratified 2023, devices arriving ~2026)
- Optical FSK at 100+ Mbps vs. acoustic ggwave at 16 bytes/sec
- **Application:** BLUE-mode optical health data transfer at centimeter range
  — camera as RX, IR LED as TX
- The Gibberlink token format is transport-agnostic — same payload types,
  same HMAC auth, same UPB Hub integration

---

## Rugged Hardware Next-Gen

### BV9900 Pro Successor (Blackview BV13 Pro or equivalent, ~2026)
Anticipated specs based on Blackview roadmap:
- MediaTek Dimensity 8300 (4nm, 6 TOPS APU)
- 12 GB RAM, 256 GB UFS 3.1
- IP69K unchanged (rugged advantage)
- Android 14 out of box

**Gibberlink/UPB upgrade path:**
- APU 3.0: real-time ggwave decode without waking main CPU (Sensing Hub)
- 6 TOPS: run Llama 3.2 3B on-device for intent engine
- Android 14: Health Connect integration for VITALS payloads

### Recommendation: Evaluate Crosscall Core-T6 (2026)
- French rugged phone designed for emergency services
- Certified for TETRA radio integration
- **Synergy:** Crosscall + Gibberlink RED mode = acoustic fallback alongside
  TETRA radio for true multi-layer 1st responder communication

---

## Hardware Upgrade Priority Matrix

| Priority | Hardware | Justification |
|---|---|---|
| 🔴 HIGH | BV9900Pro → Dimensity 8300 rugged (2026) | APU 3.0 enables always-on ggwave decode |
| 🔴 HIGH | Pixel 10 as BLUE-mode health node | Titan M3 StrongBox for HIPAA-adjacent key binding |
| 🟡 MEDIUM | Galaxy S25 Ultra as GREEN/BLUE hub | Aqstic DSP for real-time FSK decode offload |
| 🟡 MEDIUM | ESP32-S3 CSI bridge (now) | Phase A8 — Wi-Fi spatial awareness without waiting for 802.11bf |
| 🟢 LOW | 802.11bf device (2027) | Replaces ESP32-S3 bridge with native kernel API |
| 🟢 LOW | Satellite-capable Android device | Snapdragon Satellite for RED-mode air-gap GPS |

---

*NEXT_GEN_HARDWARE.md — Android/docs/ — v1.0 — 2026-04-18*
