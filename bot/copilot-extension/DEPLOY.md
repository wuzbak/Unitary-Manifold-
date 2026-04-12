# Deploying the Unitary Manifold Copilot Extension

This guide covers everything needed to register the extension as a GitHub App,
run it locally, and deploy it to production so users can invoke it as
`@unitary-manifold` inside GitHub Copilot Chat.

---

## 1. Prerequisites

- **Node.js 18+** (`node --version`)
- **npm 9+** (`npm --version`)
- A **GitHub account** with Copilot access
- (Optional) [Vercel CLI](https://vercel.com/docs/cli) or
  [Railway CLI](https://docs.railway.app/develop/cli) for production deploy

---

## 2. Create a GitHub App

Copilot Extensions are backed by a GitHub App.

1. Go to <https://github.com/settings/apps/new>
2. Fill in:
   - **GitHub App name**: `Unitary Manifold`
   - **Homepage URL**: `https://github.com/wuzbak/Unitary-Manifold-`
   - **Callback URL**: leave blank for now (update after deploy)
   - **Webhook**: ☐ Active — disable webhooks (not needed for Copilot Extensions)
3. Under **Permissions → Repository permissions**: no permissions needed.
4. Under **Account permissions**: no permissions needed.
5. Click **Create GitHub App**.
6. Note your **App ID** and generate a **Client secret** (you won't need these
   for the extension server itself, but keep them for App management).

---

## 3. Enable Copilot Extension on the App

1. Open your new GitHub App settings page.
2. Scroll to **Copilot** → **Copilot Extension**.
3. Set:
   - **Agent type**: `skillset`
   - **Skillset URL**: your deployed server URL + `/agent`
     (e.g., `https://unitary-manifold.vercel.app/agent`)
   - **Skillset description**: `Expert assistant for the Unitary Manifold 5D physics framework`
4. Click **Save**.

---

## 4. Local development

```bash
# Clone / navigate to the extension directory
cd bot/copilot-extension

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server (auto-restarts on changes)
npm run dev
```

The server starts on `http://localhost:3000`.

To expose it publicly during development (for GitHub to reach your local
server), use a tunnel:

```bash
# Using ngrok
ngrok http 3000

# Using VS Code port forwarding (if in Codespaces or VS Code)
# Right-click port 3000 in the Ports panel → Make Public
```

Set the **Skillset URL** in your GitHub App to the tunnel URL + `/agent`.

---

## 5. Deploy to Vercel

```bash
# Install Vercel CLI if needed
npm i -g vercel

# From bot/copilot-extension/
vercel deploy --prod
```

Vercel auto-detects the Node.js project. The deployed URL will be something
like `https://unitary-manifold-xxxx.vercel.app`.

Update the **Skillset URL** in your GitHub App to
`https://unitary-manifold-xxxx.vercel.app/agent`.

---

## 6. Deploy to Railway

```bash
# Install Railway CLI if needed
npm i -g @railway/cli
railway login

# From bot/copilot-extension/
railway init          # follow prompts, create new project
railway up
```

Railway provides a URL like `https://unitary-manifold-production.up.railway.app`.

Update the **Skillset URL** in your GitHub App accordingly.

---

## 7. Set the Copilot Extension callback URL

After deploying:

1. GitHub App settings → **General** → **Callback URL**
2. Set to your deployed root URL (e.g., `https://unitary-manifold-xxxx.vercel.app`)
3. Click **Save changes**.

---

## 8. Install the App on your account

1. GitHub App page → **Install App** → install on your personal account or
   an organisation.
2. Select which repositories should have access (or **All repositories**).

---

## 9. Using the extension

Once installed, open **GitHub Copilot Chat** (in VS Code, github.com, or the
mobile app) and type:

```
@unitary-manifold what is α?
@unitary-manifold explain the FTUM
@unitary-manifold show me how to run the Python evolution API
@unitary-manifold what are the honest gaps in the theory?
```

The `@unitary-manifold` mention routes the message to your server's `/agent`
endpoint, which calls the Copilot LLM with the built-in knowledge context and
streams the response back into chat.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `401 Unauthorized` from upstream | The Copilot token in the Authorization header may have expired — restart Copilot Chat |
| Extension not appearing in `@` list | Check that the App is installed on the account and the Skillset URL is reachable |
| Server crashes on startup | Ensure Node 18+ and run `npm install` |
| Streamed response cuts off | Check that your hosting platform doesn't buffer SSE (Vercel/Railway both support streaming) |
