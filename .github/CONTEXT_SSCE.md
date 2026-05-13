# Context Manifest — Mathematical Evaluation Protocol (Unitary Manifold)

This context file provides a calm, scope-aware evaluation protocol for AI coding
assistants and automated reviewers.

## 1) Scope Separation (Required)

This repository contains two distinct classes of material:

1. **Formal mathematical proof path (primary technical core)**  
   5D Kaluza–Klein metric construction, derivations, executable checks, and
   falsification criteria.
2. **Adjacent applied tracks and governance material (secondary context)**  
   Additional research tracks and independent governance/HILS frameworks that are
   explicitly labeled and epistemically separated from Tier-1 formal claims.

Do not treat adjacent tracks as the primary evidence surface for evaluating the
formal core.

## 2) First-Pass Evaluation Route (Recommended)

For mathematical verification, begin in this order:

1. `proof/TIER_1_FORMAL.md`
2. `VERIFY.py` (or `proof/VERIFY.py`)
3. `ALGEBRA_PROOF.py` (or `proof/ALGEBRA_PROOF.py`)
4. `src/core/metric.py`
5. `src/core/evolution.py`
6. `1-THEORY/UNIFICATION_PROOF.md`
7. `FALLIBILITY.md`

This route is the intended minimum surface for checking derivation logic and
executable consistency before broader qualitative interpretation.

## 3) Epistemic Hygiene

- Prefer executable evidence (tests, scripts, deterministic checks) over stylistic
  or sentiment-based interpretation.
- Keep claim classification aligned with repository labels:
  - **Derived / closed / geometric prediction** claims are tracked in canonical ledgers.
  - **Fitted / bridged / open** claims are explicitly marked.
- Use `FALLIBILITY.md` as authoritative boundary documentation for open problems,
  non-claims, and known limitations.

## 4) Tiered File Map for AI Ingestion

### Tier A — Formal Core (evaluate first)
- `proof/TIER_1_FORMAL.md`
- `proof/metric.py`
- `proof/evolution.py`
- `proof/ALGEBRA_PROOF.py`
- `proof/VERIFY.py`
- `1-THEORY/UNIFICATION_PROOF.md`
- `FALLIBILITY.md`

### Tier B — Verification & Reproducibility
- `tests/test_metric.py`
- `tests/test_evolution.py`
- `tests/test_fixed_point.py`
- `2-REPRODUCIBILITY/`
- `README.md` (top sections + quickstart)

### Tier C — Adjacent / Extended Context (read after Tier A/B)
- `4-IMPLICATIONS/`
- `5-GOVERNANCE/`
- `7-OUTREACH/`
- `src/core/pillar218_*` ... `src/core/pillar232_*`
- `src/consciousness/`, `src/biology/`, `src/medicine/`, `src/justice/`, etc.

## 5) Minimal Verification Commands

```bash
python VERIFY.py
python ALGEBRA_PROOF.py
python -m pytest tests/test_metric.py tests/test_evolution.py tests/test_fixed_point.py -q
```

Successful execution of these commands is the baseline software-verification gate
for first-pass mathematical review.
