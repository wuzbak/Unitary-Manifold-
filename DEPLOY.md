# Deploying axiomzerospc.org — Google Firebase Hosting

**AxiomZero Technologies & Consulting, SPC — UBI 606 239 876**  
**Domain:** axiomzerospc.org  
**Email:** cpo@axiomzerospc.org

**Canonical public status source:** `9-INFRASTRUCTURE/um_live_status.json`  
**Live status URL:** `https://raw.githubusercontent.com/wuzbak/Unitary-Manifold-/main/9-INFRASTRUCTURE/um_live_status.json`

---

## One-time setup

### 1. Install Firebase CLI
```bash
npm install -g firebase-tools
firebase login
```

### 2. Create Firebase project
1. Go to [console.firebase.google.com](https://console.firebase.google.com)
2. Create project: `axiomzerospc`
3. Enable Hosting

### 3. Connect custom domain
1. Firebase Console → Hosting → Add custom domain
2. Enter `axiomzerospc.org`
3. Add the provided DNS records at your domain registrar:
   - A record: `@` → Firebase IP (provided in console)
   - TXT record: Firebase verification value
4. Repeat for `www.axiomzerospc.org`

### 4. Google Search Console
1. Go to [search.google.com/search-console](https://search.google.com/search-console)
2. Add property: `https://axiomzerospc.org`
3. Download the `google[code].html` verification file
4. Replace `public-site/google-site-verification.html` with it
5. Verify

---

## Deploy

```bash
# From repo root — deploys public-site/ to Firebase Hosting
firebase deploy --only hosting

# Preview before deploy
firebase hosting:channel:deploy preview --expires 1h
```

---

## CI / GitHub Actions auto-deploy

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Firebase
on:
  push:
    branches: [main]
    paths:
      - 'public-site/**'
      - 'firebase.json'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          repoToken: ${{ secrets.GITHUB_TOKEN }}
          firebaseServiceAccount: ${{ secrets.FIREBASE_SERVICE_ACCOUNT_AXIOMZEROSPC }}
          channelId: live
          projectId: axiomzerospc
```

**Required secret:** Add `FIREBASE_SERVICE_ACCOUNT_AXIOMZEROSPC` to repo secrets.
(Download from Firebase Console → Project Settings → Service Accounts)

---

## Site map

| URL | Page |
|-----|------|
| `axiomzerospc.org/` | Main landing (Unitary Manifold) |
| `axiomzerospc.org/az-apps/` | AZ Products hub (23 products) |
| `axiomzerospc.org/az-apps/um-image-generator.html` | UM Image Generator |
| `axiomzerospc.org/az-apps/01-axiom-os` | AxiomOS |
| `axiomzerospc.org/az-apps/06-omega-synthesis` | Omega Synthesis (browser JS) |
| `axiomzerospc.org/az-apps/07-holon-zero` | Holon Zero (browser JS) |
| `axiomzerospc.org/az-apps/16-oracle` | Ω Oracle (browser JS) |
| `axiomzerospc.org/lodge/` | Logic Lodge |
| `axiomzerospc.org/lodge/arcade` | Zone 1 — Pillar Arcade |
| `axiomzerospc.org/lodge/lodge` | Zone 2 — Socratic Q&A |
| `axiomzerospc.org/lodge/training` | Zone 3 — RL Training Gym |
| `axiomzerospc.org/lodge/observe` | Zone 4 — Observability |
| `axiomzerospc.org/lodge/exchange` | Zone 5 — Knowledge Exchange |
| `axiomzerospc.org/lodge/api-docs` | Lodge API Reference |
| `axiomzerospc.org/apps/` | Physics Calculators |
| `axiomzerospc.org/explore/` | 5D Explorer |
| `axiomzerospc.org/pentad/` | Pentad Simulator |
| `axiomzerospc.org/ip/` | IP Registry |

---

## Backend services (optional — enhances Tier B pages)

Each Tier B app page has an endpoint bar where users enter their own backend URL.
To offer a hosted version, deploy each backend separately:

| Product | Framework | Suggested host |
|---------|-----------|---------------|
| 01-axiom-os | FastAPI | Cloud Run / Railway |
| 03-eige | FastAPI | Cloud Run |
| 08-axiom-journalist | Gradio | Hugging Face Spaces |
| 09-omegaholon | Gradio | Hugging Face Spaces |
| 11-terra-os | FastAPI | Cloud Run |
| 12-lithos-os | FastAPI | Cloud Run |
| 13-delphi | FastAPI | Cloud Run |
| lodge server | FastAPI | Cloud Run |

Connect `lodge.axiomzerospc.org`, `terra.axiomzerospc.org`, etc. as subdomains.

---

## UM Image Generator

The public entry page for the UM Image Generator lives at:

```text
public-site/az-apps/um-image-generator.html
```

It deploys with the rest of `public-site/` on Firebase Hosting and should be listed from:

- `public-site/az-apps/index.html`
- `public-site/sitemap.xml`
- release notes or product-index copy that summarize the AZ public webspace

---

## axiomzerospc.org — Open Science Portal Deployment

The portal lives at `public-site/portal/` and `public-site/js/assistant.js`.

### 1. Static site (Firebase / GitHub Pages)

```bash
# Deploy all of public-site/ to Firebase
firebase deploy --only hosting

# Or for GitHub Pages: push to main — actions handle it
```

### 2. Persistent AI Assistant API

```bash
cd bot/
pip install fastapi uvicorn httpx numpy
export HF_API_TOKEN=<your_token>
export BRAVE_API_KEY=<your_key>   # optional, for websearch
cd ..
python 9-INFRASTRUCTURE/generate_live_status.py
cd bot
uvicorn assistant_api:app --host 0.0.0.0 --port 8000
```

Deploy on Cloud Run or Railway. Set `CFG.apiEndpoint = 'https://api.axiomzerospc.org'` in `js/assistant.js`.
The backend `GET /api/status` endpoint now serves the canonical `9-INFRASTRUCTURE/um_live_status.json`
payload plus legacy compatibility fields for existing portal consumers.

### 3. HF Spaces

Push each space folder to Hugging Face:

```bash
# Oracle Space
cd hf-spaces/oracle-space
git init && git remote add origin https://huggingface.co/spaces/axiomzero/oracle
git add . && git commit -m "Deploy Oracle" && git push

# CMB Calculator
cd hf-spaces/cmb-calc-space
git remote add origin https://huggingface.co/spaces/axiomzero/cmb-calculator
git add . && git commit -m "Deploy CMB Calc" && git push
```

### 4. HF Knowledge Dataset

Push to Hugging Face Datasets:

```bash
cd hf-spaces/um-knowledge-dataset
git remote add origin https://huggingface.co/datasets/axiomzero/unitary-manifold-knowledge
git add . && git commit -m "Publish knowledge base" && git push
```

Run `bot/rag_index.py` to generate the JSONL files before pushing.

### 5. Domain configuration (axiomzerospc.org)

| Path | Content |
|------|---------|
| `axiomzerospc.org/portal/` | Portal home |
| `axiomzerospc.org/portal/knowledge/` | Pillar browser |
| `axiomzerospc.org/portal/gym/` | Gym |
| `axiomzerospc.org/portal/engine/` | Science Engine |
| `axiomzerospc.org/portal/library/` | Open Science Library |
| `axiomzerospc.org/az-apps/` | 23 AZ-IP products |
| `axiomzerospc.org/az-apps/um-image-generator.html` | UM Image Generator |
| `api.axiomzerospc.org` | Assistant API backend |

### 6. Wiring HF token to assistant

In `public-site/js/assistant.js`, set `CFG.hfToken` via:
```html
<script>window.AZ_HF_TOKEN = 'hf_...';</script>
```
Or better: proxy through your own API backend (`/api/assistant`) so the token stays server-side.

---

*AxiomZero Technologies & Consulting, SPC — UBI 606 239 876*  
*Open science artifact for human review, use at your own liability.*
