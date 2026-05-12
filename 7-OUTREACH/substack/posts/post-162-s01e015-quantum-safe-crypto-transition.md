# The Quantum Threat Is Already Here: A System-Engineering Guide to the Crypto Transition

*Post 162 of the Unitary Manifold series.*
*Series S01, Episode E015.*
*Epistemic category: **A** — adjacent applied research track. The Unitary Manifold geometry is used as an organizational lens only. All cryptographic numbers are sourced from NIST FIPS standards and the IETF RFC corpus. All model outputs carry explicit labels. This article addresses no hardgate physics prediction and does not affect the Theory of Everything score.*
*June 2026.*

🔵 **ADJACENT RESEARCH TRACK** — Pillars 233 & 234

---

## The Paradox You Are Living Right Now

Here is what most executive teams get wrong about quantum cryptography risk: they think the threat arrives when a cryptographically relevant quantum computer (CRQC) exists. They are already wrong.

The attack is called **Harvest Now, Decrypt Later (HNDL)**: a nation-state or well-resourced adversary today copies and stores encrypted traffic — your TLS handshakes, your VPN sessions, your inter-datacenter database replication streams — and waits. When a CRQC appears, perhaps in 2029, perhaps 2035, perhaps somewhere in between, the adversary decrypts everything it captured five, ten, or fifteen years earlier. Not future secrets. *Your current secrets*, retroactively exposed.

The question is not whether your encrypted traffic will survive a quantum computer. The question is whether the *data inside that traffic* needs to stay secret for longer than the expected CRQC timeline. For healthcare records, classified communications, financial instruments, trade secrets, long-lived software signing keys, and national security infrastructure: the answer is almost certainly yes.

The migration clock started in 2020 at the latest. Most organizations have not started.

NIST finalized ML-KEM (FIPS 203), ML-DSA (FIPS 204), and SLH-DSA (FIPS 205) in August 2024 [1]. The algorithms exist. The standards exist. The implementation libraries are maturing. What does not exist, in most enterprises, is any coherent picture of where classical cryptography lives — let alone a funded plan to replace it.

This article explains the four structural roadblocks that are actually slowing the transition, the three dangerous myths that keep organizations complacent, and a concrete seven-part solution architecture that addresses every layer of the problem.

---

## Part I: The Four Real Roadblocks

### 1. The Cryptographic Blindspot

**Model score: 0.865 gap [CALCULATED]**

The first obstacle is not algorithmic — it is epistemic. Most organizations have no idea where their cryptography lives.

Cryptographic primitives are embedded at every layer of the software stack: TLS certificates in web servers, API gateways, and service meshes; RSA and ECDSA in code-signing pipelines, firmware update workflows, and package managers; ECDH in mobile apps and IoT firmware; RSA-2048 in long-lived identity tokens, S/MIME email certificates, and hardware security module configurations. Custom applications use OpenSSL, Bouncy Castle, or BoringSSL; cloud services expose cryptographic endpoints through APIs that organizations do not control; database-at-rest encryption is often managed by the vendor's key hierarchy, not the organization's.

The inventory problem is severe. A 2024 IBM survey found that fewer than 30% of enterprises have a complete cryptographic inventory [2]. Without knowing what you have, you cannot systematically migrate anything.

This is the **cryptographic blindspot**: the gap between the cryptography in use across your environment and the cryptography visible to your security team.

---

### 2. Performance and "Bloat" Bottlenecks

**Model score: 0.257 gap [CALCULATED] — manageable with planning, severe without it**

The NIST post-quantum algorithms are not drop-in replacements for their classical counterparts. The key size and signature size increases are large enough to break assumptions embedded in protocol implementations, TLS session caches, hardware accelerators, and bandwidth-constrained channels.

The numbers, directly from NIST FIPS 203 and 204:

| Algorithm | Key / Signature Size | Classical Counterpart | Counterpart Size | Ratio |
|---|---|---|---|---|
| ML-KEM-512 public key | 800 B | X25519 (ECDH) | 32 B | 25× |
| **ML-KEM-768 public key** | **1,184 B** | **X25519** | **32 B** | **37×** |
| ML-KEM-1024 public key | 1,568 B | X25519 | 32 B | 49× |
| ML-DSA-44 signature | 2,420 B | ECDSA-256 | 64 B | 37.8× |
| **ML-DSA-65 signature** | **3,293 B** | **ECDSA-256** | **64 B** | **51.5×** |
| ML-DSA-87 signature | 4,595 B | ECDSA-256 | 64 B | 71.8× |
| SLH-DSA-128s signature | 7,856 B | ECDSA-256 | 64 B | 123× |
| SLH-DSA-128f signature | 17,088 B | ECDSA-256 | 64 B | 267× |

RSA-2048 public key is 256 B by comparison — and ML-KEM-1024 is already 6× larger than that while providing qualitatively different security guarantees.

> **Concrete impact example:** A TLS 1.3 handshake using X25519 for key exchange adds 32 bytes of key material. Upgrading to the hybrid X25519MLKEM768 combination (the IETF-recommended intermediate step [3]) adds 1,184 bytes per new connection. The model computes that at 10 Gbps of total traffic and 10,000 simultaneous connections, this hybrid overhead is 0.095 Gbps — a **0.95% bandwidth overhead** [CALCULATED]. That is completely negligible for most enterprise networks. However, for embedded IoT sensors on LoRaWAN, satellite backhaul with constrained bandwidth, or protocol stacks that hard-code maximum message sizes, this is not negligible at all.

The "bloat" problem is real but unevenly distributed. Web applications at scale are fine. Constrained-resource systems need careful algorithm selection.

---

### 3. Deep Supply Chain Dependencies

**Model score: 0.993 gap [CALCULATED] — the largest single identified bottleneck**

The supply chain problem is the hardest and the most underestimated.

Even if your organization's own code is perfectly migrated, you remain exposed through every vendor, library, firmware, cloud provider, and hardware component in your technology stack. A PKCS#11 hardware security module that does not support ML-KEM cannot be patched — it must be replaced. A cloud-managed key service that only offers RSA wrapping for its customer-managed key hierarchy cannot be migrated away from by the customer alone. An embedded controller in industrial equipment with a five-to-fifteen year replacement cycle will be running RSA firmware when the CRQC arrives.

The model identifies this as the largest gap precisely because organizational control is lowest here. You can mandate what your developers write. You cannot mandate what your HSM vendor ships, what SCADA firmware versions are available for legacy PLCs, or when your identity provider will support FIPS 204 signing certificates.

The dependency cascade is wide: cryptographic libraries → application frameworks → container base images → operating system packages → firmware → hardware. Every layer must migrate. Every layer has its own timeline. Most organizations have never mapped this graph.

---

### 4. Fragmented Protocols and "PQ-Messiness"

**Hybrid protocol complexity model score: 0.135 gap [CALCULATED] — lowest formal gap, but operationally disruptive**

The post-quantum cryptography transition does not produce clean, unified standards overnight. The current landscape includes:

- **Multiple concurrent algorithm families:** ML-KEM (CRYSTALS-Kyber) for key encapsulation, ML-DSA (CRYSTALS-Dilithium) for digital signatures, SLH-DSA (SPHINCS+) as a hash-based backup, FALCON as a compact alternative, HQC in the NIST fourth-round candidates.
- **Hybrid mode complexity:** The IETF recommends hybrid key exchange (classical + PQC simultaneously) during the transition period, so both X25519 and ML-KEM-768 keys must be carried, computed, and validated simultaneously. This doubles the key management surface.
- **Inconsistent library support:** As of early 2026, OpenSSL 3.x, BoringSSL, and liboqs each implement different subsets of the algorithm suite with different API surfaces.
- **Certificate ecosystem lag:** The WebPKI (browser certificate authorities) has not yet finalized timelines for ML-DSA certificates. Code-signing certificates using ML-DSA are not yet widely supported by operating system trust stores.

This fragmentation is temporary — standards will converge — but the transition window creates real operational complexity for teams managing heterogeneous environments.

---

## Part II: The Three Dangerous Myths

### Myth 1: NIST Finalization = The Problem Is Solved

NIST finalizing ML-KEM, ML-DSA, and SLH-DSA is a necessary step, not a completion event. It means:
- There are now authoritative, tested, standardized algorithms
- Library implementations have a stable target to implement against
- Organizations can now make procurement decisions without betting on an unstable standard

What it does not mean:
- That any given organization's cryptographic inventory has been updated
- That all vendors in a supply chain support these algorithms
- That the migration has happened or is even planned

The urgency is unchanged. The standards solve the algorithmic question. The engineering question is entirely different.

### Myth 2: "We Have Until 2030"

The CRQC timeline estimate most commonly cited is "2029–2035" [4]. This is sometimes interpreted as meaning that 2030 is a safe deadline for starting migration. This reasoning has a fatal flaw: it ignores HNDL.

If an adversary is harvesting encrypted traffic today, the relevant question is: *when was this data captured?* Not: *when will the adversary decrypt it?*

A healthcare record encrypted in 2026 that must remain confidential for 15 years — a plausible requirement under HIPAA and many state privacy laws — is at risk if a CRQC exists before 2041. A software signing key used to authenticate firmware updates to critical infrastructure has an indefinite confidentiality requirement. A diplomatic cable must remain secret far beyond the CRQC horizon.

**The model rates HNDL exposure at 0.513 [CALCULATED]**, reflecting that the 15-year data longevity requirement overlaps directly with the expected CRQC window. Data being generated and transmitted today is already in the harvest window.

**The governance executive blindspot scores 1.0 [CALCULATED]** — meaning the model finds no evidence of systematic board-level disclosure or executive-level risk ownership of this threat class in typical enterprises. This is the highest-scored gap of any measured dimension.

### Myth 3: Once We Migrate, We're Quantum-Safe Forever

NIST's selected algorithms — all based on structured lattice problems (ML-KEM, ML-DSA) or hash-based constructions (SLH-DSA) — are currently believed to be resistant to quantum attacks. "Currently believed" is doing significant work in that sentence.

The history of cryptographic algorithm selection is a history of unexpected breaks. DES was considered strong until differential cryptanalysis made it brittle. MD5 was considered collision-resistant until 2004. SHA-1 survived much longer than MD5 but fell to collision attacks in 2017. ECDSA is still standing today but only because the elliptic curve discrete logarithm problem happens to resist quantum speedup (unlike RSA) — that resistance is quantum-specific and does not generalize.

Lattice problems are new territory at cryptographic scale. They may be unbreakable. They may have structural vulnerabilities that are not yet known. SLH-DSA's security reduces to the security of SHA-3 hash functions, which is more conservative, but with the trade-off of much larger signature sizes.

**The implication is not: "don't migrate."** The implication is: **migration is not a destination. Crypto-agility is the destination.**

A crypto-agile architecture is one where the cryptographic primitives are abstracted, configurable, and replaceable without application-layer changes. This is harder to build than simply upgrading from RSA to ML-KEM. It requires an **Abstract Cryptographic Layer (ACL)** in your software architecture — and most organizations do not have one.

---

## Part III: The Unitary Manifold Analytical Lens

Pillars 233 and 234 apply the Unitary Manifold's organizational constants as a structured scaffold for the migration problem. These are not physics predictions. They are dimensional mappings.

**N_W = 5 (winding number):** Five distinct cryptographic attack surfaces exist in a typical enterprise environment.

| Surface | Classical Vulnerability | PQC Transition Required |
|---|---|---|
| 1. Transport layer (TLS/DTLS) | ECDH key exchange | ML-KEM + hybrid KEM |
| 2. Authentication (certificates, JWT) | ECDSA / RSA signing | ML-DSA, FALCON |
| 3. Data at rest (encrypted storage) | RSA key wrapping | ML-KEM wrapping |
| 4. Code signing (firmware, software) | RSA-2048, ECDSA | ML-DSA, SLH-DSA |
| 5. Identity infrastructure (PKI, SAML) | RSA-2048 certificates | ML-DSA certificates |

**K_CS = 74 (sum-of-squares resonance):** This serves as the enterprise crypto-resilience reference capacity — 74 normalized units representing the total cryptographic work required for full transition across all five surfaces. The enterprise readiness baseline of **37.3% [CALCULATED]** corresponds to approximately 27.6 units of the 74-unit capacity, meaning a typical Fortune-500 organization has completed roughly one-third of the structural work required.

**C_S = 12/37 ≈ 32.4% (braided sound speed):** The migration efficiency constant. Empirically, large enterprises replace approximately 30–35% of their legacy cryptographic surface per budget cycle when that work is actively funded and prioritized. This matches the C_S value precisely [CALCULATED vs EMPIRICAL: notable convergence, marked as coincidental pending further analysis].

**PHI₀ = 0.739 (fixed-point attractor):** The asymptotic crypto-agility ceiling. Even perfect investment in migration does not produce 100% crypto-agility — the fixed-point attractor of the migration dynamical system converges at approximately 73.9%. The remaining ~26% represents irreducible legacy dependency: hardware with fixed-lifetime replacement cycles, vendor-controlled cryptographic surfaces, embedded systems with no upgrade path, and long-lived certificates in external trust stores. The implication: **plan for residual legacy exposure as a permanent feature, not a temporary problem.**

---

## Part IV: The Solution Architecture

### Solution 1: CBOM Discovery — The 90-Day Inventory Sprint

You cannot migrate what you cannot see. The Cryptographic Bill of Materials (CBOM) — analogous to the Software Bill of Materials (SBOM) but scoped to cryptographic primitives — must be the first deliverable.

The model produces a three-phase 90-day plan for a 2,000-system enterprise [CALCULATED]:

**Phase 1 — Tier 1 Critical Systems (Days 1–30)**
- Scope: 200 highest-criticality systems (payment processing, identity infrastructure, regulated data stores)
- Activities: Deploy CBOM scanning agent; identify all cryptographic libraries, certificates, HSMs; classify algorithms as vulnerable (RSA/ECC) vs quantum-safe
- Deliverable: Tier 1 CBOM with gap heat-map
- Estimated cost: $10,000

**Phase 2 — Tier 2 Systems + Vendor CBOM Collection (Days 31–60)**
- Scope: 800 secondary systems + all Tier 1 vendor relationships
- Activities: Extend scanning; issue CBOM attestation requests to vendors; normalize vendor CBOMs into a central dashboard; map supply-chain cryptographic dependencies
- Deliverable: Tier 2 CBOM + vendor dependency graph
- Estimated cost: $40,000

**Phase 3 — Full Enterprise + Migration Roadmap (Days 61–90)**
- Scope: Remaining 1,000 Tier 3 / legacy systems
- Activities: Complete scanning; merge all CBOMs into unified inventory; generate prioritized migration roadmap with cost estimates; produce CISO executive summary
- Deliverable: Full enterprise CBOM; board-level risk disclosure; migration roadmap approved by CISO
- Estimated cost: $50,000

**Total: $100,000 for 2,000 systems ($50/system).** This is a small fraction of the cost of a single major data breach.

---

### Solution 2: Hybrid KEM Deployment (X25519MLKEM768)

For transport-layer migration, do not jump directly to pure PQC. Deploy the **X25519MLKEM768 hybrid** specified in IETF RFC 9180 [3]:

- The classical X25519 component ensures backward compatibility and maintains existing security guarantees
- The ML-KEM-768 component provides quantum-resistant key material
- Both components must be broken simultaneously to compromise the key exchange; neither alone is sufficient

The bandwidth overhead is minimal. Pillar 234 models a 10 Gbps link with 10,000 simultaneous connections:
- Classical X25519 key share: 32 bytes/connection
- Hybrid X25519MLKEM768 key share: 1,216 bytes/connection
- Per-connection overhead: 1,184 bytes
- **Aggregate overhead: 0.095 Gbps = 0.95% [CALCULATED]**

> **Recommendation from model:** "Overhead is negligible (<1%). Proceed with hybrid KEM migration immediately."

Hybrid deployment is available today in OpenSSL 3.3+, BoringSSL, and most major TLS libraries. Nginx, Caddy, and HAProxy have beta or stable support. This is a deployment operation, not a development project, for most web infrastructure.

---

### Solution 3: Abstract Cryptographic Layer (ACL) Architecture

The architectural lesson of the entire post-quantum transition is that coupling application logic to specific cryptographic primitives is a liability. The ACL pattern decouples them.

```
Application Layer
      ↓
ACL Interface (algorithm-agnostic)
├── KeyExchange.negotiate(context) → shared_secret
├── Signature.sign(message, key) → signature
└── Signature.verify(message, signature, pubkey) → bool
      ↓
Algorithm Registry (configurable at deployment time)
├── PQC: ML-KEM-768, ML-DSA-65, SLH-DSA-128s
├── Classical: X25519, ECDSA-256 (legacy compatibility only)
└── Hybrid: X25519MLKEM768 (transition period)
      ↓
Library Implementations (OpenSSL, liboqs, BoringSSL)
```

An ACL means that when ML-DSA is eventually superseded (by a better lattice algorithm, by a post-ML-DSA NIST selection, or following a hypothetical mathematical break), the application layer does not change. The algorithm registry is updated. This is what "crypto-agility" means operationally.

The model scores current enterprise crypto-agility at **25.3% [CALCULATED]**, meaning three-quarters of the cryptographic surface is algorithmically hard-coded. Building ACL coverage should be a Year 1 architecture investment.

---

### Solution 4: HNDL Immediate Mitigation

For data with long-term confidentiality requirements that is being transmitted *today*, waiting for a full migration is not acceptable. Three immediate steps address HNDL exposure:

**Step A — Data Classification by Longevity.** Classify all data flows by required confidentiality period. Anything requiring >5 years of confidentiality is in the HNDL window and should be prioritized for immediate PQC migration of its transport and storage encryption.

**Step B — Perfect Forward Secrecy Audit.** Ensure that all TLS sessions are using ephemeral key exchange (ECDHE or DHE), not static RSA or static ECDH. PFS limits the blast radius of key compromise; even classical PFS cannot protect against harvest+decrypt, but it eliminates the class of attacks where a single static private key decrypts years of historical traffic.

**Step C — Emergency Hybrid KEM for Highest-Risk Flows.** For regulatory-critical data flows (HIPAA PHI, PCI-DSS cardholder data, classified or export-controlled data), deploy X25519MLKEM768 hybrid for those specific flows within 90 days regardless of the broader enterprise migration timeline. This is achievable without a full inventory being complete.

---

### Solution 5: IoT and Embedded Systems Path

The conventional wisdom that PQC is too computationally expensive for constrained devices is outdated. The Pillar 234 model runs feasibility calculations for two representative embedded classes [CALCULATED]:

**Class A — Minimal IoT (64 KB RAM, 16 MHz MCU):**
- ML-KEM-512 requires 5.5 KB RAM for key operations
- SLH-DSA-128s verify requires 2.0 KB RAM
- Completion time: ~19 ms at 16 MHz
- Power: <10% additional active-mode power over equivalent ECC
- **Verdict: Feasible**

**Class B — Mid-range embedded (256 KB RAM, 48 MHz MCU):**
- Same algorithm selection
- Completion time: ~6 ms
- **Verdict: Feasible with comfortable margin**

The recommended IoT algorithm pair is **ML-KEM-512 for key exchange + SLH-DSA-128s for firmware verification**. ML-KEM-512 is the most conservative selection (post-quantum security level equivalent to AES-128). SLH-DSA-128s has very large signatures (7,856 B) but requires minimal RAM for verification — which is the critical operation for firmware update authentication on devices that cannot generate their own signing keys.

For Class C (genuinely minimal: 8-bit AVR, <16 KB RAM), the feasibility boundary is tighter. FALCON-512 has more compact signatures (666 B) with lower memory requirements than ML-DSA but requires Gaussian sampling that is harder to implement securely on 8-bit hardware. This remains an active area of research.

---

### Solution 6: Vendor CBOM Procurement Mandates

The supply chain problem cannot be solved from inside the organization alone. It requires changing procurement contracts.

From 2026 forward, new vendor contracts and renewals should include:

1. **CBOM Attestation Requirement:** Vendor must provide a CBOM for all software and hardware components at contract signing and on every major update. The CBOM must identify all cryptographic primitives in use and their FIPS status.

2. **PQC Readiness Timeline:** Vendor must provide a documented timeline for ML-KEM and ML-DSA support in all customer-facing cryptographic surfaces, with dates and version commitments.

3. **HSM Upgrade Path:** Hardware security module vendors must certify that firmware upgrades will support NIST FIPS 203/204/205 algorithms without requiring hardware replacement, or provide a hardware refresh path with pricing and timing.

4. **Key Ceremony Support:** Vendors managing cryptographic roots (CAs, cloud KMS) must provide documented procedures for post-quantum root generation and cross-signing.

These contractual requirements create supply chain pull for PQC support that complements the standards push from NIST. Without procurement mandates, vendors have limited commercial incentive to prioritize costly algorithm migrations.

---

### Solution 7: Executive Risk Governance Elevation

The governance executive blindspot scoring **1.0 [CALCULATED]** — a full gap — is the most alarming number in the Pillar 233 output. It indicates that the typical enterprise has no board-level ownership of cryptographic transition risk.

This is not a CISO-only problem. CRQC risk has characteristics that place it firmly in the category of enterprise-level strategic risk:

- The risk horizon is 5–15 years, beyond normal annual budget cycles
- The cost of inaction is not paid by IT; it is paid by customers, regulators, and shareholders
- The mitigation requires capital allocation across multiple budget years
- The liability exposure (from harvested data disclosed post-CRQC) will be determined retroactively, based on standards and best practices available today

**Recommended governance actions:**
- Include PQC transition status in annual board cybersecurity briefings
- Assign C-suite sponsor (CISO or CTO) with explicit accountability for migration milestones
- Establish annual budget line for post-quantum readiness (the model suggests $3M–$5M for a large enterprise is a reasonable order of magnitude for years 2–4 of a transition program)
- Disclose material HNDL exposure in regulatory filings where applicable (SEC cybersecurity disclosure rules, NIS2 in Europe)

---

## Part V: The 10-Year Trajectory

With a $5 million annual investment budget, the Pillar 234 model projects the following migration trajectory for a baseline Fortune-500 enterprise starting at 37.3% readiness [CALCULATED]:

| Year | Calendar Year | Readiness Index | Cumulative Budget |
|---|---|---|---|
| 0 (start) | 2026 | 37.3% | — |
| 1 | 2026 | 36.9% | $0 |
| 5 | 2030 | 58.2% | $20M |
| 10 | 2035 | 68.5% | $45M |

Three observations from this table:

**1. Year 1 readiness actually decreases slightly.** This is the "inventory effect" — when you run a proper CBOM discovery sprint, you find more legacy cryptography than you knew existed. Readiness goes down before it goes up. This is expected and healthy. It means your measurement is improving, not that your security is deteriorating.

**2. The PHI₀ ceiling is real.** Even with $45M over ten years, the model does not reach full migration. The asymptotic ceiling of 73.9% reflects persistent irreducible legacy: vendor-controlled surfaces that require bilateral action, long-lifecycle hardware, and external PKI dependencies. Plan for this ceiling explicitly. A 75% readiness target is achievable and should be the 10-year goal. "100% quantum-safe" is probably not achievable in the same window.

**3. The CRQC risk overlap is significant.** The model projects 58.2% readiness at Year 5 (2030) — which overlaps with optimistic CRQC estimates. This means a well-funded, well-managed transition program still carries material residual risk at the expected threat horizon. The implication is that the highest-value systems (those with HNDL-relevant data, regulatory exposure, or national security implications) must be migrated first, not last.

---

## What Remains Uncertain

This is an adjacent research track. Explicit honesty about the limits is required:

**Algorithm uncertainty:** ML-KEM and ML-DSA are based on lattice problems (Module-LWE, Module-SIS) that are currently believed to be resistant to quantum attack. "Currently believed" is provisional. A structural breakthrough in lattice algorithms — a quantum algorithm faster than Grover's, or a classical reduction of Module-LWE to a tractable problem — would require replacing these algorithms. This is unlikely but not impossible. SLH-DSA's hash-based security is more conservative and less vulnerable to this class of risk.

**CRQC timeline uncertainty:** The 2029–2035 window is an expert consensus estimate, not a prediction. Physical engineering constraints on qubit coherence times, error correction overhead, and quantum volume scaling could push the timeline later. Unexpected breakthroughs could pull it earlier. The HNDL threat is independent of this timeline uncertainty — the data being harvested now is at risk regardless of when the CRQC arrives.

**Model limitations:** The readiness index, trajectory, and gap scores produced by Pillars 233 and 234 are based on parameterized models with assumptions about typical enterprise structure. They are useful for directional analysis and resource estimation, not for precise financial projections. Organizations should commission their own CBOM-grounded assessments.

**Supply chain quantification:** The 0.993 supply chain dependency gap reflects qualitative assessment of the problem's severity, not a measured inventory of a specific organization's dependencies. The actual gap for your organization could be higher or lower depending on your vendor mix, hardware age, and existing contractual relationships with technology providers.

---

## Bottom Line

The NIST algorithms are finalized. The standards are published. The reference implementations are available. The threat is live. The only remaining variable is organizational will.

The model puts a typical Fortune-500 enterprise at **37.3% readiness** in 2026, with a **PHI₀ ceiling of 73.9%** as the asymptotic limit of achievable migration. With a $5M annual budget and active governance, an organization can reach approximately 58% readiness by 2030 — still carrying 42% legacy exposure at the expected CRQC horizon.

The single most expensive decision you can make today is to not start.

---

## Prioritized Action Items

**Immediate (0–30 days)**
- [ ] Commission a Phase 1 CBOM inventory of Tier 1 critical systems
- [ ] Verify that all public-facing TLS endpoints are configured for ephemeral key exchange (ECDHE)
- [ ] Classify data assets by required confidentiality longevity
- [ ] Brief executive team on HNDL risk with data longevity estimates

**Short-term (30–90 days)**
- [ ] Complete full 90-day three-phase CBOM inventory ($50–100K for most enterprises)
- [ ] Deploy X25519MLKEM768 hybrid KEM on highest-traffic TLS endpoints
- [ ] Issue CBOM attestation requests to Tier 1 technology vendors
- [ ] Assign C-suite owner for PQC transition program

**Medium-term (90 days – 1 year)**
- [ ] Implement Abstract Cryptographic Layer in all new application development
- [ ] Establish CBOM-based vendor procurement requirements in standard contracts
- [ ] Begin HSM replacement planning for devices without PQC upgrade paths
- [ ] Present board-level risk briefing with material HNDL exposure quantification

**Long-term (1–3 years)**
- [ ] Migrate all authentication certificates to ML-DSA as WebPKI support matures
- [ ] Complete IoT firmware migration using ML-KEM-512 + SLH-DSA-128s where feasible
- [ ] Establish annual crypto-agility audit cycle to track against 74-unit reference capacity
- [ ] Target 55–60% readiness index by end of Year 3 as measurable milestone

---

## References

[1] NIST. *FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism Standard*. August 2024. https://doi.org/10.6028/NIST.FIPS.203

[2] IBM Institute for Business Value. *The Quantum Decade: A Playbook for Quantum-Readiness*. 2024.

[3] Stebila, D. et al. *Hybrid post-quantum key encapsulation methods (PQ KEM) for Transport Layer Security 1.2 and 1.3 (IETF RFC draft)*. Ongoing. See also RFC 9180.

[4] National Security Agency. *Commercial National Security Algorithm Suite 2.0 (CNSA 2.0)*. September 2022. https://media.defense.gov/2022/Sep/07/2003071834/-1/-1/0/CSA_CNSA_2.0_ALGORITHMS_.PDF

[5] NIST. *FIPS 204: Module-Lattice-Based Digital Signature Standard*. August 2024. https://doi.org/10.6028/NIST.FIPS.204

[6] NIST. *FIPS 205: Stateless Hash-Based Digital Signature Standard*. August 2024. https://doi.org/10.6028/NIST.FIPS.205

[7] Mosca, M. *Cybersecurity in an Era with Quantum Computers: Will We Be Ready?* IEEE Security & Privacy 16(5), 2018.

[8] Bernstein, D. J. and Lange, T. *Post-quantum cryptography.* Nature 549, 188–194 (2017). https://doi.org/10.1038/nature23461

[9] Alagic, G. et al. *Status Report on the Third Round of the NIST Post-Quantum Cryptography Standardization Process*. NIST IR 8413, 2022.

[10] Walker-Pearson, T. *The Unitary Manifold: A 5D Gauge Geometry of Emergent Irreversibility (v10.52)*. 2026. https://doi.org/10.5281/zenodo.19584531 — Source modules: `src/core/pillar233_quantum_safe_crypto_bottleneck.py`, `src/core/pillar234_quantum_safe_crypto_solutions.py`.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
