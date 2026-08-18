# 12-AZ-IP/apps — AxiomZero Applications

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

---

## Overview

This folder registers all **AxiomZero application-layer IP** — interactive front-ends, mobile clients,
and user-facing dashboards that expose the Unitary Manifold physics stack to end users.

---

## Registered Applications

### 1 · AxiomZero Android Client
| Field | Value |
|-------|-------|
| **Source path** | `AxiomZero/android/` |
| **Key files** | `__init__.py`, `client.py` |
| **Description** | Python-based Android client layer for the AxiomZero cognitive OS. Provides the mobile interface to the AxiomZero API, enabling remote physics queries, HILS governance interactions, and AI assistant access from Android devices. |
| **Status** | REGISTERED |
| **Category** | Mobile Application |

### 2 · AxiomZero Web Dashboard (UI)
| Field | Value |
|-------|-------|
| **Source path** | `AxiomZero/ui/dashboard.html` |
| **Description** | Browser-based control dashboard for the AxiomZero cognitive layer. Displays 7-manager × 5-sub-agent network status, active HILS sessions, φ-field decision metrics, and real-time system state. |
| **Status** | REGISTERED |
| **Category** | Web Application |

### 3 · Unitary Manifold Public Web App
| Field | Value |
|-------|-------|
| **Source path** | `public-site/` |
| **Key files** | `index.html`, `apps/index.html`, `explore/index.html`, `pentad/index.html`, `status/index.html`, `about/index.html`, `ip/index.html` |
| **Description** | Full static web application for the Unitary Manifold framework. Includes interactive physics calculators, 5D space explorer (WebGL), HILS Pentad simulator, status dashboard, and IP/products catalog. Deployable to GitHub Pages or any static host. |
| **Status** | REGISTERED |
| **Category** | Web Application |
| **Live URL** | `https://wuzbak.github.io/Unitary-Manifold-/` |

### 4 · UM-SOS Frontend (Scientific OS Dashboard)
| Field | Value |
|-------|-------|
| **Source path** | `10-UM-SOS/frontend/` |
| **Description** | Browser-based front-end for the Unitary Manifold Scientific Operating System. Visualizes the derivation DAG, preregistration registry, prediction status, and governance lane classification for all 590 pillars. |
| **Status** | REGISTERED |
| **Category** | Web Application |

### 5 · AxiomZero API Server
| Field | Value |
|-------|-------|
| **Source path** | `AxiomZero/api/server.py` |
| **Description** | REST API server exposing AxiomZero cognitive layer to external clients. Endpoints for physics queries, HILS certification, manager status, and φ-field evaluation. |
| **Status** | REGISTERED |
| **Category** | API / Backend Application |

### 6 · EIGE Governance App
| Field | Value |
|-------|-------|
| **Source path** | `EIGE/` |
| **Description** | The Emergent Intelligence Governance Engine — a full application stack (src, notebooks, tests, outreach, infra, schemas) for AI-augmented governance, adjudication, and disaster recovery. |
| **Status** | REGISTERED |
| **Category** | Governance Application |

---

## Assets Pending Integration from `wuzbak/Private`

> **Note:** The repository `wuzbak/Private` contains additional application assets that should be
> copied into this folder. Access requires owner authorization. Once accessed, copy each app's
> source files into the appropriate category subfolder and register them in `../IP_REGISTRY.json`.

The following categories are expected based on the problem statement:
- Additional mobile/web apps
- Engine front-ends
- OS management utilities

To integrate: grant repository access, then copy source files here and update `IP_REGISTRY.json`.

---

## Authorship

All applications were created under the **Human-in-the-Loop Systems (HILS)** framework:
- **Scientific direction, design, and product vision:** ThomasCory Walker-Pearson
- **Code architecture, test suites, documentation:** GitHub Copilot (AI)

---

*AxiomZero Apps Registry v1.0 — 2026-08-18*
