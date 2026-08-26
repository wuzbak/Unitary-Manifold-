# AxiomZero SGE — System Security Governance Engine

**Version:** 1.0.0 | **Product:** 22 | **Status:** Production-ready — 229 tests, 0 failures  
**Epistemic label:** 🔵 ADJACENT TRACK — next-generation security governance application (not a physics claim)  
**Theory & scientific direction:** ThomasCory Walker-Pearson  
**Code architecture & implementation:** GitHub Copilot (AI)

---

## What Is the AZ-SGE?

The **AxiomZero System Security Governance Engine** (AZ-SGE) is a fully integrated, next-generation security protection suite providing:

- **Zero-day exploit protection** — seven independent heuristics detecting novel attacks without signature databases
- **Anti-malware** — YARA rule engine, entropy analysis, shellcode pattern matching, ransomware detection
- **Anti-hacking / intrusion detection** — signature + statistical anomaly IDS for network events and process events
- **Anti-surveillance** — DNS leak detection, tracker blocklist (200+ domains), canvas/WebRTC/font fingerprint defense
- **Firewall** — stateful packet-filter policy engine with default-deny-all and rate limiting
- **Vulnerability scanner** — dependency auditing (pip/npm/Cargo) against a curated CVE database
- **Threat intelligence** — live NVD CVE feed + MalwareBazaar + offline IOC registry
- **Quarantine & remediation** — automatic file quarantine, IP/domain blocking, patch advisories
- **SHA-512 rolling hash chain** — tamper-evident immutable audit ledger with Merkle root verification
- **AES-256-GCM + X25519 ECDH** — session encryption layer for all sensitive data

The AZ-SGE is the AxiomZero equivalent of Norton / CrowdStrike / Defender — built from first principles, with full source code, no black boxes, and cryptographic audit integrity.

---

## Architecture

```
22-az-sge/
├── engine/
│   ├── hash_chain.py          # SHA-512 rolling hash chain + Merkle forest
│   ├── encryption.py          # AES-256-GCM + X25519 ECDH + HKDF-SHA-512
│   ├── threat_intel.py        # NVD CVE, MalwareBazaar, custom IOC feeds
│   ├── malware_detector.py    # YARA engine, entropy, shellcode, ransomware
│   ├── zero_day.py            # 7 heuristic zero-day detectors
│   ├── intrusion_detector.py  # IDS: signature rules + anomaly baseline
│   ├── firewall.py            # Packet-filter policy engine + rate limiting
│   ├── surveillance_guard.py  # Anti-surveillance, tracker block, fingerprint
│   ├── vuln_scanner.py        # Dependency auditor + port scanner
│   ├── quarantine.py          # Quarantine vault + remediation orchestrator
│   └── sge_core.py            # Unified orchestrator — public API
├── app/
│   └── server.py              # HTTP dashboard server (7 API endpoints)
├── ui/
│   └── index.html             # Single-page security dashboard
├── tests/
│   └── test_az_sge.py         # 229 tests, 0 failures
├── run.py                     # CLI launcher
└── requirements.txt
```

---

## Protection Coverage

| Threat Class | Detection Method | Response |
|---|---|---|
| Known malware | SHA-256/MD5 IOC lookup (online + offline) | Quarantine + alert |
| Ransomware | YARA rules (WannaCry, LockBit, Conti, …), extension scan, canary files | Quarantine + operator alert |
| Zero-day exploit | 7 heuristics: entropy, shellcode, heap spray, ROP, memory corruption, exploit kit, drive-by | Quarantine if above threshold |
| SQL injection | Regex signature IDS | Alert + IP block |
| XSS | Pattern IDS | Alert |
| RCE / Command injection | Pattern IDS | Alert + IP block |
| XXE / SSRF / LDAP injection | Pattern IDS | Alert |
| Port scan | Stateful PortScanDetector | Alert |
| Brute force | Stateful BruteForceDetector | Alert + IP block |
| Suspicious process | Process rule IDS (Mimikatz, Cobalt Strike, PowerShell obfuscation, …) | Alert |
| Tracker surveillance | 200+ domain blocklist (Google Analytics, Hotjar, Mixpanel, …) | Block |
| Browser fingerprinting | Canvas, WebRTC, font enum, FingerprintJS detection | Alert |
| DNS leak | /etc/resolv.conf audit vs. approved resolvers | Alert |
| Vulnerable dependencies | pip/npm/Cargo audit vs. 25+ known CVEs | Patch advisory |
| Known CVEs | Live NVD feed + offline sample set | Alert + advisory |
| Network anomaly | Statistical Z-score baseline | Alert |

---

## Quick Start

```bash
# Install (numpy only required; cryptography optional for hardware AES)
pip install -r requirements.txt

# Optionally install cryptography for real AES-256-GCM and X25519:
pip install cryptography

# Start the dashboard (demo events included)
python run.py --demo

# Dashboard → http://127.0.0.1:7622/

# Scan a file for malware
python run.py --scan /path/to/suspicious.exe

# Check a domain against tracker/C2 lists
python run.py --check-domain google-analytics.com

# Look up a file hash
python run.py --check-hash 44d88612fea8a8f36de82e1278abb02f

# Look up a CVE
python run.py --check-cve CVE-2024-21762

# Audit dependencies in a project directory
python run.py --audit-deps /path/to/project

# Print engine status JSON
python run.py --status
```

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/status` | Full engine status |
| GET | `/api/events` | Recent 100 security events |
| GET | `/api/chain` | Hash chain head + Merkle root + integrity |
| GET | `/api/threats` | Threat intel summary |
| GET | `/api/firewall` | Firewall audit summary |
| GET | `/api/quarantine` | Quarantine summary + records |
| POST | `/api/scan-url` | Scan URL payload for zero-day |
| POST | `/api/check-domain` | Check domain against blocklist |
| POST | `/api/check-hash` | Check file hash vs. threat intel |
| POST | `/api/check-cve` | Look up CVE in threat intel |

---

## Security Design Principles

1. **Default deny all** — the firewall default policy blocks everything not explicitly allowed
2. **Immutable audit trail** — every security event is committed to an append-only SHA-512 hash chain; any tampering is cryptographically detectable
3. **Defence in depth** — no single layer is relied upon; malware detection + zero-day + IDS + firewall operate independently
4. **Offline-first** — all critical detections (known malware, core CVEs, tracker domains) work without network access
5. **Transparent** — full Python source, no binary blobs, no external black-box dependencies
6. **Least privilege** — quarantine vault uses 0700 permissions; dashboard binds to 127.0.0.1 only by default
7. **Cryptographic integrity** — AES-256-GCM with random IV, HMAC-SHA-512 chain links, HKDF-SHA-512 key derivation

---

## Hash Chain Protocol (SHA-512 Rolling Hash)

The AZ-SGE implements the SHA-512 rolling hash protocol first developed in the EIGE product (03-eige):

```
state_{n+1} = SHA-512( state_n ‖ K_CS ‖ SHA-512(payload_n) ‖ timestamp_n )
```

where `K_CS = 74 = 5² + 7²` (Chern-Simons constant from the Unitary Manifold).

Properties:
- **Non-commutative** — inserting or reordering any event disrupts all subsequent links
- **HMAC-authenticated** — each link is signed with a device-local 512-bit key
- **Merkle-verifiable** — the entire chain can be batched into a Merkle root for quick integrity checks
- **Tamper-evident** — any single-byte modification in any prior link is immediately detectable

---

## Testing

```bash
# Run all 229 tests
pytest tests/test_az_sge.py -v

# Expected: 229 passed, 0 failed
```

Coverage:
- `TestHashChain` (15 tests) — chain integrity, tamper detection, Merkle, HMAC
- `TestEncryption` (13 tests) — AES-GCM, ECDH, HKDF, SecureEnvelope
- `TestThreatIntel` (15 tests) — offline/online feed lookups, deduplication
- `TestMalwareDetector` (19 tests) — YARA, entropy, shellcode, macro, baseline
- `TestZeroDay` (13 tests) — all 7 heuristics + verdict logic
- `TestIntrusionDetector` (18 tests) — all signature rules, stateful detectors, anomaly
- `TestFirewall` (16 tests) — policy rules, rate limiting, stateful, JSON compiler
- `TestSurveillanceGuard` (13 tests) — tracker block, fingerprint, privacy audit
- `TestDependencyAuditor` (12 tests) — pip/npm/cargo parsing + CVE matching
- `TestQuarantineOrchestrator` (6 tests) — vault, quarantine, chain linkage
- `TestSGECore` (21 tests) — end-to-end orchestration
- Extra coverage classes (14 classes, 68 tests) — deep module coverage

---

## Epistemic Status

This product is an **adjacent track** — a security engineering application built on top of the AxiomZero platform. It is not a hardgate physics claim. The SHA-512 rolling hash protocol borrows the `K_CS = 74` constant from the Unitary Manifold as a non-linearity parameter; the security properties hold independently of the underlying physics.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
