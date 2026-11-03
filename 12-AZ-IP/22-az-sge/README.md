# AxiomZero SGE — System Security Governance Engine

**Version:** 1.0.0 | **Product:** 22 | **Status:** Local security analysis and policy engine; host enforcement is not implemented<br>
**Epistemic label:** 🔵 ADJACENT TRACK — next-generation security governance application (not a physics claim)  
**Theory & scientific direction:** ThomasCory Walker-Pearson  
**Code architecture & implementation:** GitHub Copilot (AI)

---

## What Is the AZ-SGE?

The **AxiomZero System Security Governance Engine** (AZ-SGE) is a local security-analysis application providing:

- **Suspicious-content triage** — seven heuristics that flag patterns; they do not prove or prevent zero-day exploits
- **File analysis** — YARA rules, entropy analysis, byte-pattern checks, and ransomware-related indicators
- **Event analysis** — signature and statistical anomaly checks for events explicitly submitted by a caller
- **Privacy checks** — DNS configuration audit, local tracker-domain lookup, and browser fingerprinting indicators
- **Firewall policy evaluation** — stateful in-process rules and rate limiting for submitted events; no host firewall is changed
- **Vulnerability scanner** — dependency auditing (pip/npm/Cargo) against a curated CVE database
- **Threat intelligence** — live NVD CVE feed + MalwareBazaar + offline IOC registry
- **Response records** — local vault copies, block recommendations, and patch advisories; no host action is implied
- **SHA-512 rolling hash chain** — process-local event-integrity checking with Merkle-root calculation
- **AES-256-GCM + X25519 ECDH** — cryptography-backed session encryption; refuses operation if the provider is unavailable

AZ-SGE is not an endpoint protection product and does not replace a host firewall, anti-malware service, EDR, or incident-response process.

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
└── tests/
│   └── test_az_sge.py         # Unit and integration coverage
├── run.py                     # CLI launcher
└── requirements.txt
```

---

## Analysis Coverage

| Threat Class | Detection Method | Response |
|---|---|---|
| Known malware | SHA-256/MD5 IOC lookup (online + offline) | Store a local vault copy; original remains untouched |
| Ransomware indicators | YARA rules, extension checks, optional canaries | Record indicators; no automatic recovery or file isolation |
| Suspicious content | 7 heuristics: entropy, shellcode, heap spray, ROP, memory corruption, exploit kit, drive-by | Heuristic triage; not zero-day prevention |
| SQL injection | Regex signature IDS on submitted events | Alert record and optional local block recommendation |
| XSS | Pattern IDS | Alert |
| RCE / Command injection | Pattern IDS | Alert record and optional local block recommendation |
| XXE / SSRF / LDAP injection | Pattern IDS | Alert |
| Port scan | Stateful PortScanDetector | Alert |
| Brute force | Stateful BruteForceDetector | Alert record and optional local block recommendation |
| Suspicious process | Process rule IDS (Mimikatz, Cobalt Strike, PowerShell obfuscation, …) | Alert |
| Tracker surveillance | Domain blocklist (Google Analytics, Hotjar, Mixpanel, …) | Local lookup result; no browser or resolver enforcement |
| Browser fingerprint indicators | Canvas, WebRTC, font enumeration, FingerprintJS patterns | Alert |
| DNS leak | /etc/resolv.conf audit vs. approved resolvers | Alert |
| Vulnerable dependencies | pip/npm/Cargo audit vs. 25+ known CVEs | Patch advisory |
| Known CVEs | Live NVD feed + offline sample set | Alert + advisory |
| Network anomaly | Statistical Z-score baseline | Alert |

---

## Quick Start

```bash
# Install required runtime dependencies
pip install -r requirements.txt

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

1. **Explicit policy result** — the in-process firewall evaluator defaults to deny for events passed to it; it does not filter host traffic
2. **Process-local audit chain** — events are appended to a SHA-512 hash chain and verifiable during this process lifetime; the chain is not durably stored or externally anchored
3. **Layered analysis** — file, event, dependency, and privacy analyzers operate on supplied inputs; they do not monitor the host automatically
4. **Offline-first** — all critical detections (known malware, core CVEs, tracker domains) work without network access
5. **Transparent** — full Python source, no binary blobs, no external black-box dependencies
6. **Least privilege** — the vault uses owner-only permissions where supported; the dashboard binds to 127.0.0.1 by default
7. **Cryptographic integrity** — cryptography-backed AES-256-GCM with random IV, X25519 ECDH, and HKDF-SHA-512. If `cryptography` is missing, encryption and SGE startup fail explicitly; no substitute cipher is used.

The encryption keypair is generated in memory at startup and is not persisted. Encrypted data created by one process lifetime cannot be decrypted after restart unless the caller independently retains the key material.

## Deployment limits

AZ-SGE currently analyzes files and events supplied to its Python API and evaluates policy in process. It does not collect host telemetry, install kernel hooks, terminate processes, change operating-system firewall/DNS rules, or prevent a flagged source file from running. “Vaulted” means a copy is stored in the local vault; the original is deliberately left in place. The dashboard, IOC lists, and audit chain are process-local and are not an operational SOC, durable evidence store, or verified malware-prevention system.

---

## Process-Local Hash Chain (SHA-512 Rolling Hash)

The AZ-SGE implements the SHA-512 rolling hash protocol first developed in the EIGE product (03-eige):

```
state_{n+1} = SHA-512( state_n ‖ K_CS ‖ SHA-512(payload_n) ‖ timestamp_n )
```

where `K_CS = 74 = 5² + 7²` (Chern-Simons constant from the Unitary Manifold).

In-process properties:
- **Non-commutative** — inserting or reordering any event disrupts all subsequent links
- **HMAC-authenticated** — each link is signed with a device-local 512-bit key
- **Merkle-verifiable** — the entire chain can be batched into a Merkle root for quick integrity checks
- **Tamper-evident within the process** — changing a prior link is detected by verification; the chain is not persisted or externally anchored

---

## Testing

```bash
# Run the product suite
pytest tests/ -v

# Expected: 255 passed, 0 failed
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
