/* ============================================================
   Unitary Manifold Chatbot Widget
   Self-contained — no dependencies. Drop-in for any HTML page.
   ============================================================ */
(function () {
  "use strict";

  // ---------------------------------------------------------------------------
  // Configuration
  // ---------------------------------------------------------------------------
  var API_ENDPOINT = "https://api.openai.com/v1/chat/completions";
  var DEFAULT_MODEL = "gpt-4o-mini";
  var STORAGE_KEY_APIKEY = "um_openai_key";

  var KNOWLEDGE_CONTEXT =
    "You are the Unitary Manifold Assistant \u2014 an expert on ThomasCory Walker-Pearson\u2019s 5D Kaluza-Klein gauge-geometric framework.\n\n" +
    "THEORY: The Second Law of Thermodynamics is a geometric identity, not a statistical postulate. " +
    "A 5th compact dimension contains an irreversibility field B_\u03bc. " +
    "After KK reduction this encodes the arrow of time directly into the 4D field equations.\n\n" +
    "KEY EQUATIONS:\n" +
    "Walker-Pearson: G_\u03bc\u03bd + \u03bb\u00b2(H_\u03bc\u03c1H_\u03bd^\u03c1 \u2212 \u00bcg_\u03bc\u03bd H\u00b2) + \u03b1R\u03c6\u00b2g_\u03bc\u03bd = 8\u03c0G\u2084 T_\u03bc\u03bd\n" +
    "Information current: \u2207_\u03bc J^\u03bc_inf = 0, J^\u03bc_inf = \u03c6\u00b2u^\u03bc\n" +
    "UEUM: \u1e8b^a + \u0393^a_{bc}\u1e8b^b\u1e8b^c = G_U^{ab}\u2207_b S_U + \u03b4/\u03b4X^a(\u03a3 A_{\u2202,i}/4G + Q_top)\n" +
    "FTUM: Fixed point \u03a8* of U = I+H+T such that U\u03a8* = \u03a8*\n" +
    "\u03b1 derived: \u03b1 = \u03c6\u2080\u207b\u00b2 (not a free parameter)\n\n" +
    "PREDICTIONS: n\u209b\u22480.9635 (Planck 1\u03c3), \u03b2\u2208{\u22480.273\u00b0,\u22480.331\u00b0} two SOS states (k_cs\u2208{61,74}; observed 0.35\u00b0\u00b10.14\u00b0), \u03b1=\u03c6\u2080\u207b\u00b2 derived, r_braided\u22480.0315 (BICEP/Keck <0.036)\n" +
    "GAPS: CMB amplitude suppressed \u00d74\u20137, \u03c6\u2080 self-consistency not fully closed\n" +
    "FALSIFIER: LiteBIRD \u03b2 measurement (2030\u20132032) \u2014 \u03b2 outside [0.22\u00b0,0.38\u00b0] falsifies the braided-winding mechanism\n" +
    "SCOPE: 26 geometric pillars (physics, chemistry, astronomy, geology, biology, atomic structure, cold fusion, recycling, medicine, justice, governance, neuroscience, ecology, climate, marine, psychology, genetics, materials) + Unitary Pentad HILS framework (independent, 16 modules)\n" +
    "REPO: https://github.com/wuzbak/Unitary-Manifold-\n" +
    "PYTHON API: src/core/metric.py, evolution.py (FieldState, run_evolution), holography/boundary.py, multiverse/fixed_point.py, core/braided_winding.py, core/kk_geodesic_reduction.py\n" +
    "TESTS: 4763 passing across all suites (tests/: 3411, recycling/: 316, Unitary Pentad/: 1036), 0 failures\n\n" +
    "Answer questions accurately. Acknowledge gaps honestly. Reference specific files when helpful. Be scientifically rigorous but accessible.";

  // ---------------------------------------------------------------------------
  // CSS
  // ---------------------------------------------------------------------------
  var css = "\n" +
    "#um-chat-btn {\n" +
    "  position: fixed; bottom: 24px; right: 24px; z-index: 9998;\n" +
    "  width: 54px; height: 54px; border-radius: 50%;\n" +
    "  background: #1a1a2e; color: #fff; font-size: 24px;\n" +
    "  border: 2px solid #4a90d9; cursor: pointer;\n" +
    "  box-shadow: 0 4px 16px rgba(0,0,0,0.3);\n" +
    "  display: flex; align-items: center; justify-content: center;\n" +
    "  transition: transform 0.2s ease;\n" +
    "}\n" +
    "#um-chat-btn:hover { transform: scale(1.1); }\n" +
    "#um-chat-panel {\n" +
    "  position: fixed; bottom: 88px; right: 24px; z-index: 9999;\n" +
    "  width: 360px; max-width: calc(100vw - 48px);\n" +
    "  height: 480px; max-height: calc(100vh - 120px);\n" +
    "  background: #fff; border: 1.5px solid #1a1a2e; border-radius: 12px;\n" +
    "  box-shadow: 0 8px 32px rgba(0,0,0,0.22);\n" +
    "  display: flex; flex-direction: column; overflow: hidden;\n" +
    "  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;\n" +
    "  animation: um-slide-in 0.22s ease;\n" +
    "}\n" +
    "@keyframes um-slide-in {\n" +
    "  from { opacity: 0; transform: translateY(16px); }\n" +
    "  to   { opacity: 1; transform: translateY(0); }\n" +
    "}\n" +
    "#um-chat-header {\n" +
    "  background: #1a1a2e; color: #fff; padding: 12px 16px;\n" +
    "  font-size: 14px; font-weight: 600;\n" +
    "  display: flex; align-items: center; justify-content: space-between;\n" +
    "  flex-shrink: 0;\n" +
    "}\n" +
    "#um-chat-header span { font-size: 11px; opacity: 0.7; margin-left: 8px; font-weight: 400; }\n" +
    "#um-chat-close {\n" +
    "  background: none; border: none; color: #fff; font-size: 18px;\n" +
    "  cursor: pointer; padding: 0 4px; line-height: 1;\n" +
    "}\n" +
    "#um-chat-messages {\n" +
    "  flex: 1; overflow-y: auto; padding: 12px 14px;\n" +
    "  display: flex; flex-direction: column; gap: 10px;\n" +
    "  scroll-behavior: smooth;\n" +
    "}\n" +
    ".um-msg {\n" +
    "  max-width: 88%; padding: 8px 12px; border-radius: 10px;\n" +
    "  font-size: 13px; line-height: 1.5; word-break: break-word;\n" +
    "}\n" +
    ".um-msg.user {\n" +
    "  align-self: flex-end; background: #1a1a2e; color: #fff;\n" +
    "  border-bottom-right-radius: 3px;\n" +
    "}\n" +
    ".um-msg.assistant {\n" +
    "  align-self: flex-start; background: #f0f4ff; color: #1a1a2e;\n" +
    "  border: 1px solid #d0d8f0; border-bottom-left-radius: 3px;\n" +
    "}\n" +
    ".um-msg.system {\n" +
    "  align-self: center; background: #fff8e1; color: #7a5a00;\n" +
    "  border: 1px solid #ffe082; font-size: 12px; text-align: center;\n" +
    "}\n" +
    ".um-msg code {\n" +
    "  background: rgba(0,0,0,0.08); padding: 1px 4px; border-radius: 3px;\n" +
    "  font-family: 'Courier New', monospace; font-size: 12px;\n" +
    "}\n" +
    ".um-msg pre {\n" +
    "  background: rgba(0,0,0,0.06); border-radius: 6px; padding: 8px;\n" +
    "  overflow-x: auto; margin: 6px 0;\n" +
    "}\n" +
    ".um-msg pre code { background: none; padding: 0; }\n" +
    "#um-chat-input-row {\n" +
    "  display: flex; gap: 6px; padding: 10px 12px;\n" +
    "  border-top: 1px solid #e0e6f0; flex-shrink: 0; background: #fafbff;\n" +
    "}\n" +
    "#um-chat-input {\n" +
    "  flex: 1; border: 1.5px solid #c0cce0; border-radius: 8px;\n" +
    "  padding: 7px 10px; font-size: 13px; outline: none;\n" +
    "  resize: none; font-family: inherit; line-height: 1.4;\n" +
    "  transition: border-color 0.2s;\n" +
    "}\n" +
    "#um-chat-input:focus { border-color: #4a90d9; }\n" +
    "#um-chat-send {\n" +
    "  background: #1a1a2e; color: #fff; border: none; border-radius: 8px;\n" +
    "  padding: 7px 14px; cursor: pointer; font-size: 13px; font-weight: 600;\n" +
    "  transition: background 0.2s;\n" +
    "}\n" +
    "#um-chat-send:hover { background: #4a90d9; }\n" +
    "#um-chat-send:disabled { background: #aab; cursor: default; }\n" +
    ".um-typing { opacity: 0.5; font-style: italic; }\n";

  // ---------------------------------------------------------------------------
  // Inject CSS
  // ---------------------------------------------------------------------------
  function injectCSS() {
    var style = document.createElement("style");
    style.textContent = css;
    document.head.appendChild(style);
  }

  // ---------------------------------------------------------------------------
  // Markdown rendering (bold, italics, inline code, code blocks)
  // ---------------------------------------------------------------------------
  function renderMarkdown(text) {
    // Code blocks first (```...```)
    text = text.replace(/```([^`]*?)```/gs, function (_, code) {
      return "<pre><code>" + escapeHtml(code.trim()) + "</code></pre>";
    });
    // Inline code
    text = text.replace(/`([^`]+?)`/g, function (_, code) {
      return "<code>" + escapeHtml(code) + "</code>";
    });
    // Bold
    text = text.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    // Italics
    text = text.replace(/\*(.+?)\*/g, "<em>$1</em>");
    // Newlines to <br>
    text = text.replace(/\n/g, "<br>");
    return text;
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  // ---------------------------------------------------------------------------
  // Build DOM
  // ---------------------------------------------------------------------------
  function buildWidget() {
    // Floating button
    var btn = document.createElement("button");
    btn.id = "um-chat-btn";
    btn.title = "Ask about the Unitary Manifold";
    btn.innerHTML = "\uD83D\uDCAC"; // 💬

    // Panel
    var panel = document.createElement("div");
    panel.id = "um-chat-panel";
    panel.style.display = "none";

    panel.innerHTML =
      '<div id="um-chat-header">' +
        '<div>\uD83C\uDF0C Unitary Manifold <span>Walker-Pearson 5D Theory</span></div>' +
        '<button id="um-chat-close" title="Close">\u00d7</button>' +
      '</div>' +
      '<div id="um-chat-messages"></div>' +
      '<div id="um-chat-input-row">' +
        '<textarea id="um-chat-input" rows="2" placeholder="Ask about the theory, equations, API\u2026"></textarea>' +
        '<button id="um-chat-send">Send</button>' +
      '</div>';

    document.body.appendChild(btn);
    document.body.appendChild(panel);

    return {
      btn: btn,
      panel: panel,
      messages: panel.querySelector("#um-chat-messages"),
      input: panel.querySelector("#um-chat-input"),
      send: panel.querySelector("#um-chat-send"),
      close: panel.querySelector("#um-chat-close"),
    };
  }

  // ---------------------------------------------------------------------------
  // Message helpers
  // ---------------------------------------------------------------------------
  function appendMessage(container, role, html, isHTML) {
    var div = document.createElement("div");
    div.className = "um-msg " + role;
    if (isHTML) {
      div.innerHTML = html;
    } else {
      div.textContent = html;
    }
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return div;
  }

  // ---------------------------------------------------------------------------
  // API key prompt
  // ---------------------------------------------------------------------------
  function promptForKey(container) {
    var msg = appendMessage(
      container,
      "system",
      "\uD83D\uDD11 Enter your OpenAI API key to start chatting. " +
        "Your key is stored only in your browser (localStorage) and sent directly to OpenAI.",
      false
    );

    var row = document.createElement("div");
    row.style.cssText = "display:flex;gap:6px;margin-top:8px;";
    var inp = document.createElement("input");
    inp.type = "password";
    inp.placeholder = "sk-...";
    inp.style.cssText =
      "flex:1;border:1px solid #aaa;border-radius:6px;padding:5px 8px;font-size:12px;";
    var saveBtn = document.createElement("button");
    saveBtn.textContent = "Save";
    saveBtn.style.cssText =
      "background:#1a1a2e;color:#fff;border:none;border-radius:6px;" +
      "padding:5px 10px;cursor:pointer;font-size:12px;";
    row.appendChild(inp);
    row.appendChild(saveBtn);
    msg.appendChild(row);
    container.scrollTop = container.scrollHeight;

    return new Promise(function (resolve) {
      function tryKey() {
        var k = inp.value.trim();
        if (!k) return;
        localStorage.setItem(STORAGE_KEY_APIKEY, k);
        msg.remove();
        resolve(k);
      }
      saveBtn.addEventListener("click", tryKey);
      inp.addEventListener("keydown", function (e) {
        if (e.key === "Enter") tryKey();
      });
    });
  }

  // ---------------------------------------------------------------------------
  // Stream chat completion
  // ---------------------------------------------------------------------------
  function streamChat(messages, apiKey, onToken, onDone, onError) {
    var body = JSON.stringify({
      model: DEFAULT_MODEL,
      messages: messages,
      stream: true,
    });

    fetch(API_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + apiKey,
      },
      body: body,
    })
      .then(function (resp) {
        if (!resp.ok) {
          resp.text().then(function (t) {
            onError("API error " + resp.status + ": " + t);
          });
          return;
        }
        var reader = resp.body.getReader();
        var decoder = new TextDecoder("utf-8");
        var buffer = "";

        function pump() {
          reader.read().then(function (result) {
            if (result.done) {
              onDone();
              return;
            }
            buffer += decoder.decode(result.value, { stream: true });
            var lines = buffer.split("\n");
            buffer = lines.pop(); // keep partial line
            lines.forEach(function (line) {
              if (!line.startsWith("data: ")) return;
              var data = line.slice(6).trim();
              if (data === "[DONE]") { onDone(); return; }
              try {
                var obj = JSON.parse(data);
                var delta = obj.choices && obj.choices[0] && obj.choices[0].delta;
                if (delta && delta.content) onToken(delta.content);
              } catch (_) {}
            });
            pump();
          });
        }
        pump();
      })
      .catch(function (err) {
        onError(err.message || String(err));
      });
  }

  // ---------------------------------------------------------------------------
  // Main widget logic
  // ---------------------------------------------------------------------------
  function init() {
    injectCSS();
    var el = buildWidget();
    var conversationHistory = [];
    var busy = false;

    // Show welcome message
    appendMessage(
      el.messages,
      "assistant",
      renderMarkdown(
        "**\uD83C\uDF0C Unitary Manifold Assistant**\n\n" +
          "Ask me anything about ThomasCory Walker-Pearson\u2019s 5D gauge-geometric framework. " +
          "I can explain the theory, equations, predictions (n\u209b\u22480.9635, \u03b2=0.3513\u00b0), " +
          "honest gaps, and the Python API.\n\n" +
          "_Source: [github.com/wuzbak/Unitary-Manifold-](https://github.com/wuzbak/Unitary-Manifold-)_"
      ),
      true
    );

    // Toggle panel
    el.btn.addEventListener("click", function () {
      var isOpen = el.panel.style.display !== "none";
      el.panel.style.display = isOpen ? "none" : "flex";
      if (!isOpen) el.input.focus();
    });

    el.close.addEventListener("click", function () {
      el.panel.style.display = "none";
    });

    // Send message
    async function sendMessage() {
      if (busy) return;
      var text = el.input.value.trim();
      if (!text) return;

      // Get or request API key
      var apiKey = localStorage.getItem(STORAGE_KEY_APIKEY) || "";
      if (!apiKey) {
        apiKey = await promptForKey(el.messages);
      }

      el.input.value = "";
      appendMessage(el.messages, "user", text, false);

      conversationHistory.push({ role: "user", content: text });

      var allMessages = [{ role: "system", content: KNOWLEDGE_CONTEXT }].concat(
        conversationHistory
      );

      var responseDiv = appendMessage(el.messages, "assistant um-typing", "\u22ef", false);
      responseDiv.className = "um-msg assistant";
      responseDiv.innerHTML = "";

      busy = true;
      el.send.disabled = true;

      var accumulated = "";

      streamChat(
        allMessages,
        apiKey,
        function onToken(token) {
          accumulated += token;
          responseDiv.innerHTML = renderMarkdown(accumulated);
          el.messages.scrollTop = el.messages.scrollHeight;
        },
        function onDone() {
          conversationHistory.push({ role: "assistant", content: accumulated });
          busy = false;
          el.send.disabled = false;
          el.input.focus();
        },
        function onError(errMsg) {
          responseDiv.innerHTML =
            '<span style="color:#c00;">\u26a0\ufe0f ' +
            escapeHtml(errMsg) +
            "</span>";
          // Clear bad API key if auth error
          if (errMsg.indexOf("401") !== -1) {
            localStorage.removeItem(STORAGE_KEY_APIKEY);
          }
          busy = false;
          el.send.disabled = false;
        }
      );
    }

    el.send.addEventListener("click", sendMessage);
    el.input.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Boot after DOM ready
  // ---------------------------------------------------------------------------
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
