# GitHub Pages Chatbot Widget

A self-contained JavaScript widget that adds a floating 💬 chat button to
any GitHub Pages / Jekyll site. Users enter their own OpenAI API key (saved to
`localStorage`) — no server required.

---

## Files

| File | Purpose |
|------|---------|
| `chatbot-widget.js` | Complete widget (CSS + JS, no dependencies) |

---

## Adding the widget to your GitHub Pages site

### Step 1 — Copy the widget file

```bash
cp bot/pages-chatbot/chatbot-widget.js docs/
```

### Step 2 — Add the script tag

**Option A — Single page** (add to any `.md` or `.html` page):

```html
<script src="/chatbot-widget.js"></script>
```

**Option B — All pages** (add to the Jekyll default layout):

Open or create `docs/_layouts/default.html`. If using a remote theme (e.g.,
`minima`), create this file to override the theme layout:

```html
---
# docs/_layouts/default.html
---
<!DOCTYPE html>
<html lang="{{ page.lang | default: site.lang | default: "en" }}">
  {%- include head.html -%}
  <body>
    {%- include header.html -%}
    <main class="page-content" aria-label="Content">
      <div class="wrapper">
        {{ content }}
      </div>
    </main>
    {%- include footer.html -%}
    <!-- Unitary Manifold chat widget -->
    <script src="{{ "/chatbot-widget.js" | relative_url }}"></script>
  </body>
</html>
```

### Step 3 — Commit and push

```bash
cd docs/
git add chatbot-widget.js _layouts/default.html
git commit -m "Add Unitary Manifold chat widget"
git push
```

GitHub Pages rebuilds automatically. The floating 💬 button will appear in the
bottom-right corner of every page.

---

## How it works

1. A 💬 button appears in the bottom-right corner of the page.
2. Clicking it opens a chat panel.
3. If no OpenAI API key is stored, the user is prompted to enter one.
   The key is saved to `localStorage` (never leaves the browser).
4. Messages are sent to the OpenAI Chat Completions API with streaming enabled.
5. The full theory knowledge context (Walker-Pearson equations, predictions,
   gaps) is included as a system prompt with every request.
6. Responses are streamed token-by-token into the chat panel.
7. Markdown (bold, italics, inline code, code blocks) is rendered in responses.

---

## Configuring a different API endpoint

By default the widget uses `https://api.openai.com/v1/chat/completions`. To
point it at a self-hosted proxy, edit `chatbot-widget.js` and change the
`API_ENDPOINT` constant near the top of the file.

---

## Privacy note

The widget never sends API keys or conversation history to any third party
other than OpenAI directly from the user's browser. The GitHub Pages server
never sees any API keys.
