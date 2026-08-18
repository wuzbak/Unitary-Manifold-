# Pillar 235 — Solar Physics Open Questions Engine

**Status:** 🔵 ADJACENT RESEARCH TRACK (non-hardgate)  
**Author:** ThomasCory Walker-Pearson · Code: GitHub Copilot (AI)  
**Date:** 2026  
**Module:** `src/core/pillar235_solar_physics_open_questions_engine.py`

---

## 1. Executive Summary

Pillar 235 introduces a quantitative framework for 12 high-priority unsolved
solar-physics questions. The module does **not** claim final closure of those
questions. Instead, it contributes:

1. deterministic diagnostics from explicit observable inputs,
2. falsification conditions per question,
3. integrated portfolio scoring across all 12 questions,
4. Monte Carlo uncertainty propagation for robustness testing.

This is explicitly an adjacent applied-research lane.

---

## 2. The Twelve Questions Addressed

1. Coronal heating problem
2. Internal mechanics of the solar dynamo
3. Origins of the slow solar wind
4. Trigger conditions for flares and CMEs
5. North–South polar temperature asymmetry
6. Core rotation / neutrino-constraint consistency
7. Solar metallicity discrepancy
8. Faint young Sun paradox
9. Alfvén-wave acceleration mechanism
10. SEP shock acceleration microphysics
11. Grand-minimum intermittency (Maunder-type)
12. Source geometry of the IBEX ribbon

---

## 3. Core Method

The module defines `SolarObservables` and computes per-question diagnostics with
closure scores in `[0,1]`. Each question output contains:

- `question`
- `diagnostic` (quantified metrics + closure score)
- `derived_solution` (testable mechanism candidate)
- `epistemic_status`
- `falsification_condition`

A portfolio layer aggregates mean/median/min closure scores and identifies the
current weakest lane.

---

## 4. Simulation Layer

`monte_carlo_question_stability()` perturbs observational inputs (Gaussian,
configurable relative sigma) and returns per-question mean/std/min/max closure
scores.

Purpose:

- test sensitivity to observational uncertainty,
- identify fragile vs robust explanatory lanes,
- prioritize instrument and campaign design.

---

## 5. Scientific Boundary Conditions

- This module is **not** a claim that mainstream solar physics is solved.
- It is a falsifiable synthesis and prioritization scaffold.
- Failure of this adjacent track does not alter hardgate ToE scoring lanes.

---

## 6. Falsifiability

Pillar 235 fails if one or more of the following hold repeatedly on independent
datasets:

- diagnostic closures are systematically anti-correlated with observational fit,
- proposed mechanism lanes fail across multi-mission cross-validation,
- uncertainty analyses show no stable explanatory ranking under realistic noise.

---

## 7. Intended Use

- mission planning support (Parker Solar Probe, Solar Orbiter, DKIST, future ENA missions),
- hypothesis ranking for resource allocation,
- transparent communication of where uncertainty remains largest.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
