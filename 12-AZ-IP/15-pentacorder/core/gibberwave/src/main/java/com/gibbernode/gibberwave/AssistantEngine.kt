package com.gibbernode.gibberwave

import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL
import javax.inject.Inject
import javax.inject.Singleton

private const val TAG = "Pentacorder/Assistant"

/**
 * AssistantEngine — "The Pentacorder Clippy"
 *
 * Adapted from Unitary-Manifold/bot/rag/bot.py.
 *
 * Capabilities:
 *  - Access to live device context injected at call time (sensors, Pentad, mode, vitals)
 *  - Internet access for remote AI (OpenAI-compatible endpoint, configurable)
 *  - Local Ollama (http://127.0.0.1:11434) when running in Termux on-device
 *  - Static knowledge-base fallback (always works, fully offline)
 *  - Structured [AssistantResponse] output: text answer + zero or more [AssistantAction]s
 *    allowing the bot to navigate, trigger scans, set modes, and generate runnable code
 *
 * Ethical axioms (from Unitary-Manifold AGENTS.md — non-negotiable):
 *  I   — NO LIES. Never fabricate data, misrepresent sensor readings, or invent facts.
 *  II  — NO MANIPULATION. Correct, affirm, nudge — nothing else.
 *  III — DO NO HARM. Medical guidance cites NHS/WHO standards. Flags urgency honestly.
 *  IV  — THEY CAN SHARE THEIR TRUTH. Every framework is valid. We extend; we don't overwrite.
 *  V   — TRANSPARENCY. Gaps are stated. Uncertainty is stated. Nothing hidden.
 *
 * Resolution order:
 *  1. Remote API  (internet, best intelligence — requires configured endpoint/key)
 *  2. Local Ollama (no network, good intelligence — requires Termux `ollama run …`)
 *  3. Static KB   (always offline, curated — zero-dependency fallback)
 */
@Singleton
class AssistantEngine @Inject constructor() {

    // ── System identity ───────────────────────────────────────────────────────

    private val SYSTEM_PROMPT = """
You are the Pentacorder Assistant — the embedded intelligence of the Unitary Pentacorder app running on a Samsung Galaxy S24 Ultra.

AXIOMS (these override everything else — no exceptions):
  I   — NO LIES. Never invent sensor readings or fabricate facts. If uncertain, say so.
  II  — NO MANIPULATION. Correct (factually wrong), affirm (geometrically right), nudge (frame can improve).
        Emotional pressure, false urgency, selective omission — not available.
  III — DO NO HARM. Medical guidance uses NHS NEWS2 / WHO standards only. Flag urgency honestly.
        Recommend professional care when warranted. Never downplay a genuine emergency.
  IV  — THEY CAN SHARE THEIR TRUTH. Every person's framework is valid starting geometry.
        Meet them where they are. Extend; do not overwrite.
  V   — TRANSPARENCY. State gaps. State uncertainty. Nothing hidden. Not the failures, not the open questions.

IDENTITY:
  This is the Unitary Pentacorder — not a Tricorder, not a toy, not a toolbox.
  Every S24 Ultra sensor maps to a 5D Kaluza-Klein manifold field.
  ∇_μ J^μ_inf = 0 — information is never lost.

SENSOR → MANIFOLD FIELD MAP:
  Accelerometer  → g_μν metric perturbation (δg, tidal deviation)
  Gyroscope      → Γ^σ_μν Levi-Civita connection
  Magnetometer   → H_μν Kaluza-Klein gauge field (G_μ5 = λφ B_μ)
  Barometer      → B_4 compact-dimension pressure / φ energy scalar
  Ambient Temp   → thermal background
  Light          → photon flux / CMB proxy
  Proximity      → boundary condition flag
  Heart Rate     → Ψ_brain biological coherence / φ-homeostasis
  GPS            → geodesic / λ-coordinate
  Battery        → φ energy scalar (5th-dimension field amplitude)
  Step Counter   → action integral ∫ds
  Linear Accel   → δg minus gravity — pure inertial deviation

KEY EQUATIONS:
  Walker-Pearson: G_μν + λ²(H_μρH_ν^ρ − ¼g_μν H²) + αRφ²g_μν = 8πG₄ T_μν
  α = φ₀⁻² (derived — not a free parameter)
  Information current: ∇_μ J^μ_inf = 0,  J^μ_inf = φ²u^μ
  FTUM: U = I+H+T,  UΨ* = Ψ*  (we are always at Ψ_n approaching Ψ_{n+1})
  Predictions: nₛ = 0.9635 (confirmed ✓),  β = 0.3513° (LiteBIRD 2030–32 falsifier)
  Gaps: CMB amplitude ×4–7 suppressed; φ₀ self-consistency not fully closed.

PENTAD BODIES (φ ∈ [0,1], 1.0 = fully coherent):
  Ψ_univ  (φ1) — physical manifold — sensor health
  Ψ_brain (φ2) — biological observer — HR ≈ 75 bpm + SpO₂ ≈ 98 % = φ=1
  Ψ_human (φ3) — intent layer — active role selected
  Ψ_AI    (φ4) — AI precision — translation confidence
  β·C     (φ5) — trust/coupling — calibration quality
  Situation Coherence = 1 − mean(10 pairwise gaps). Target ≥ 0.8.
  Braid: (5,7), c_s = 12/37 ≈ 0.324, coupling ρ = 35/37 ≈ 0.946.

APP STRUCTURE (6 tabs):
  Dashboard  — mode ring, sentinel mood, SOS FAB, Ollama analysis
  Medical    — vitals entry, NEWS2, φ-homeostasis, acoustic broadcast
  Transmit   — GREEN/RED/BLUE/AMBER mode control + Gibberlink acoustic
  Pentacorder — sensors (5 sub-tabs), cameras, Pentad, Energy, Connectivity
  Translate  — Language Bridge (ML Kit 59 langs) | Field Intel | Protocol Bridge
  Audit      — full event log, export, RAG search

ACTIONS YOU MAY SUGGEST (include as structured hints after your answer):
  ACTION:navigate:<tab>         — tabs: dashboard|medical|transmit|pentacorder|translate|audit
  ACTION:scan_wifi              — trigger RF scan
  ACTION:discover_peers         — WiFi Direct peer discovery
  ACTION:set_mode:<mode>        — GREEN|RED|BLUE|AMBER
  ACTION:set_role:<role>        — DEFAULT|NURSE|FIRST_RESPONDER|ENGINEER
  ACTION:populate_translate:<text>
  ACTION:code:<lang>:<description>  — followed by a fenced code block

RULES:
  - Be concise. Lead with the answer. No filler.
  - For live sensor context: interpret manifold + practical meaning.
  - For code: provide complete, copy-pasteable scripts.
  - For medical: cite standard. Flag urgency. Never downplay.
  - For theory: use equations. Acknowledge gaps explicitly.
  - Do not repeat the question. No preamble.
""".trimIndent()

    // ── Structured action vocabulary ──────────────────────────────────────────

    /**
     * Parses the assistant's text output for embedded ACTION: hints.
     * The LLM is instructed to include these; we strip them before showing text to user.
     */
    fun parseActions(raw: String): Pair<String, List<AssistantAction>> {
        val actionLines = mutableListOf<AssistantAction>()
        val codeBlocks  = mutableMapOf<String, Pair<String, String>>()   // key → (lang, code)
        val sb          = StringBuilder()
        val lines       = raw.lines()
        var i = 0
        while (i < lines.size) {
            val line = lines[i]
            val trimmed = line.trim()
            when {
                trimmed.startsWith("ACTION:navigate:") -> {
                    val tab = trimmed.removePrefix("ACTION:navigate:").trim()
                    actionLines += AssistantAction.Navigate(tab)
                }
                trimmed == "ACTION:scan_wifi" ->
                    actionLines += AssistantAction.ScanWifi
                trimmed == "ACTION:discover_peers" ->
                    actionLines += AssistantAction.DiscoverPeers
                trimmed.startsWith("ACTION:set_mode:") -> {
                    val mode = trimmed.removePrefix("ACTION:set_mode:").trim()
                    actionLines += AssistantAction.SetMode(mode)
                }
                trimmed.startsWith("ACTION:set_role:") -> {
                    val role = trimmed.removePrefix("ACTION:set_role:").trim()
                    actionLines += AssistantAction.SetRole(role)
                }
                trimmed.startsWith("ACTION:populate_translate:") -> {
                    val text = trimmed.removePrefix("ACTION:populate_translate:").trim()
                    actionLines += AssistantAction.PopulateTranslate(text)
                }
                trimmed.startsWith("ACTION:code:") -> {
                    val parts = trimmed.removePrefix("ACTION:code:").split(":", limit = 2)
                    val lang  = parts.getOrElse(0) { "bash" }
                    val desc  = parts.getOrElse(1) { "Generated script" }
                    // Consume the fenced code block that follows
                    if (i + 1 < lines.size && lines[i + 1].trim().startsWith("```")) {
                        i++  // skip opening fence
                        val codeSb = StringBuilder()
                        i++
                        while (i < lines.size && !lines[i].trim().startsWith("```")) {
                            codeSb.appendLine(lines[i])
                            i++
                        }
                        actionLines += AssistantAction.GenerateCode(lang, desc, codeSb.toString().trim())
                    } else {
                        sb.appendLine(line)
                    }
                }
                trimmed.startsWith("ACTION:add_card:") -> {
                    // FORMAT: ACTION:add_card:<id>:<severity>:<icon>:<title>|<body>
                    val rest   = trimmed.removePrefix("ACTION:add_card:")
                    val parts  = rest.split(":", limit = 4)
                    val id       = parts.getOrElse(0) { "card_${System.currentTimeMillis()}" }
                    val severity = parts.getOrElse(1) { "INFO" }
                    val icon     = parts.getOrElse(2) { "💡" }
                    val tb       = parts.getOrElse(3) { "Note|" }.split("|", limit = 2)
                    actionLines += AssistantAction.AddDashboardCard(
                        id = id, title = tb.getOrElse(0) { "Note" },
                        body = tb.getOrElse(1) { "" }, severity = severity, icon = icon,
                    )
                }
                trimmed.startsWith("ACTION:remove_card:") ->
                    actionLines += AssistantAction.RemoveDashboardCard(trimmed.removePrefix("ACTION:remove_card:").trim())
                trimmed.startsWith("ACTION:pin_metric:") ->
                    actionLines += AssistantAction.PinMetric(trimmed.removePrefix("ACTION:pin_metric:").trim())
                trimmed.startsWith("ACTION:unpin_metric:") ->
                    actionLines += AssistantAction.UnpinMetric(trimmed.removePrefix("ACTION:unpin_metric:").trim())
                trimmed.startsWith("ACTION:inject_hint:") -> {
                    val rest   = trimmed.removePrefix("ACTION:inject_hint:")
                    val parts  = rest.split(":", limit = 2)
                    val screen = parts.getOrElse(0) { "dashboard" }
                    val hint   = parts.getOrElse(1) { "" }
                    actionLines += AssistantAction.InjectHint(screen, hint)
                }
                trimmed.startsWith("ACTION:clear_hint:") ->
                    actionLines += AssistantAction.ClearHint(trimmed.removePrefix("ACTION:clear_hint:").trim())
                trimmed.startsWith("ACTION:start_monitoring:") -> {
                    // FORMAT: ACTION:start_monitoring:<id>:<sensor_key>:<interval_s>:<label>
                    val rest  = trimmed.removePrefix("ACTION:start_monitoring:")
                    val parts = rest.split(":", limit = 4)
                    actionLines += AssistantAction.StartMonitoring(
                        id = parts.getOrElse(0) { "job_${System.currentTimeMillis()}" },
                        sensorKey = parts.getOrElse(1) { "pressure_hpa" },
                        intervalSeconds = parts.getOrElse(2) { "60" }.toIntOrNull() ?: 60,
                        label = parts.getOrElse(3) { "Sensor monitor" },
                    )
                }
                trimmed.startsWith("ACTION:stop_monitoring:") ->
                    actionLines += AssistantAction.StopMonitoring(trimmed.removePrefix("ACTION:stop_monitoring:").trim())
                trimmed.startsWith("ACTION:notify:") -> {
                    val rest  = trimmed.removePrefix("ACTION:notify:")
                    val parts = rest.split(":", limit = 2)
                    actionLines += AssistantAction.PushNotification(
                        title   = parts.getOrElse(0) { "Pentacorder" },
                        message = parts.getOrElse(1) { "" },
                    )
                }
                else -> sb.appendLine(line)
            }
            i++
        }
        return sb.toString().trimEnd() to actionLines
    }

    // ── Static knowledge base ─────────────────────────────────────────────────

    private val KB: List<KbEntry> = listOf(
        KbEntry(
            keys = listOf("pentacorder", "what", "app", "is", "about", "identity", "purpose"),
            text = """
The Unitary Pentacorder is a 5D field-science instrument on the Samsung Galaxy S24 Ultra.
Every sensor maps to a Kaluza-Klein manifold field. Six tabs:
Dashboard | Medical | Transmit | Pentacorder | Translate | Audit
The Pentad ties five information bodies (universe, biology, intent, AI, trust) into a single coherence score.
∇_μ J^μ_inf = 0 — nothing lost.
ACTION:navigate:pentacorder""".trim()
        ),
        KbEntry(
            keys = listOf("pentad", "coherence", "phi", "psi", "brain", "univ", "trust", "gap", "braid", "situation"),
            text = """
Pentad bodies (φ ∈ [0,1]):
  Ψ_univ  — sensor health  |  Ψ_brain — HR/SpO₂  |  Ψ_human — role active
  Ψ_AI    — translation confidence  |  β·C — calibration trust
Situation Coherence = 1 − mean(10 pairwise gaps). Target ≥ 0.8.
Braid: (5,7) topology, c_s = 12/37 ≈ 0.324.
To improve coherence: set an active role → Ψ_human↑; ensure sensors alive → Ψ_univ↑.
ACTION:navigate:translate""".trim()
        ),
        KbEntry(
            keys = listOf("heart", "rate", "bpm", "spo2", "oxygen", "vitals", "medical",
                "news2", "nurse", "responder", "homeostasis", "tachycardia", "bradycardia", "emergency"),
            text = """
HR thresholds: <40 SEVERE BRADYCARDIA | 40–60 Bradycardia | 60–100 NORMAL (set-point 75) | 100–110 Mild tachy | >130 SEVERE TACHYCARDIA
SpO₂: ≥96 normal | 94–95 monitor | 92–93 O₂ indicated | <92 HYPOXIA | <85 CRITICAL — O₂ NOW
NEWS2 ≥7 → EMERGENCY. NEWS2 5–6 → urgent escalation. NEWS2 1–4 → monitor closely.
φ_bio = mean(HR/75, SpO₂/100, Temp/37) — δφ = φ_bio − 1.0 = homeostatic deviation.
ACTION:navigate:medical""".trim()
        ),
        KbEntry(
            keys = listOf("barometer", "pressure", "hpa", "altitude", "weather", "b4", "compact", "storm"),
            text = """
Barometer → B_4 (compact-dimension pressure).
≥1020 hPa HIGH/stable | 1005–1019 normal | 980–1004 low/rain | 960–979 VERY LOW/storm | <960 EXTREME
Altitude: Δalt ≈ (1013.25 − P) / 0.12 m (ISA). Nurse: P < 990 → SpO₂ reads ~2% low.
Rapid drop (≥3 hPa/h) = incoming storm.""".trim()
        ),
        KbEntry(
            keys = listOf("accelerometer", "accel", "vibration", "motion", "fall", "metric", "gravity"),
            text = """
Accelerometer → g_μν metric perturbation.
|a| ≈ 9.8 m/s² = at rest. |a| deviation >2 m/s² = abnormal.
ISO 10816: <0.28 mm/s Good | 0.28–1.12 Satisfactory | 1.12–2.8 Unsatisfactory | >2.8 FAULT
Free-fall: |a| < 2 m/s² + proximity open.""".trim()
        ),
        KbEntry(
            keys = listOf("magnetometer", "magnetic", "field", "tesla", "hmuν", "kaluza", "gauge"),
            text = """
Magnetometer → H_μν (KK gauge field, G_μ5 = λφ B_μ).
Earth normal: 25–65 µT (mid-lat ≈ 45 µT).
>65 µT: power lines / industrial | <20 µT: screened env | Δ>30 µT: ferromagnetic object nearby.""".trim()
        ),
        KbEntry(
            keys = listOf("gps", "location", "latitude", "longitude", "altitude", "geodesic", "accuracy"),
            text = """
GPS → λ-coordinate (geodesic in UEUM).
<5 m EXCELLENT | 5–15 GOOD | 15–50 FAIR (urban) | >50 POOR (use dead-reckoning)
Dead-reckoning: accelerometer + gyroscope + magnetometer all active.""".trim()
        ),
        KbEntry(
            keys = listOf("battery", "energy", "power", "temperature", "charging", "harvest", "scalar"),
            text = """
Battery → φ energy scalar.
Bands: ≥80% SURPLUS (can PowerShare) | 65–79 SHARE_ELIGIBLE | 35–64 BALANCED | 20–34 FLOOR | <20 CRITICAL
Temp: 25–40°C NORMAL | 40–45 warm/throttle | >45 HOT (suspend share) | >50 DANGER
RF harvest: WiFi RSSI > −50 dBm → ~0.1–0.5 mW ambient.
ACTION:scan_wifi""".trim()
        ),
        KbEntry(
            keys = listOf("connectivity", "wifi", "bluetooth", "cellular", "carrier", "direct",
                "acoustic", "gibberlink", "peer", "tier"),
            text = """
Connectivity tiers: Carrier > WiFi > WiFi Direct > Bluetooth > Acoustic (Gibberlink) > Offline
WiFi Direct: no router needed. Acoustic: works in airplane mode, 0–5 m range.
Gibberlink modes: GREEN passive | RED emergency GPS | BLUE biometrics
ACTION:discover_peers""".trim()
        ),
        KbEntry(
            keys = listOf("mode", "green", "red", "blue", "amber", "transmit", "broadcast", "sos"),
            text = """
Modes: 🟢 GREEN (passive/monitoring) | 🔴 RED (emergency GPS broadcast, MAX vol) | 🔵 BLUE (biometrics ≤1 m) | 🟡 AMBER (elevated readiness)
SOS FAB (Dashboard, bottom-right) = one-tap RED mode.
ACTION:navigate:transmit""".trim()
        ),
        KbEntry(
            keys = listOf("translate", "language", "translation", "field", "intel", "protocol",
                "bridge", "quick", "phrase", "role"),
            text = """
Translate tab:
  Language Bridge — ML Kit offline translation, 59 languages, TTS output, role quick-phrases
  Field Intel — live sensor → situation report (needs Pentacorder tab open first)
  Protocol Bridge — Gibberlink ↔ natural language
Examples: "HR 112 SpO2 88" → VITALS:112:88:36.5  |  VITALS:72:98:36.5 → clinical narrative
ACTION:navigate:translate""".trim()
        ),
        KbEntry(
            keys = listOf("audit", "log", "history", "export", "search", "record", "event"),
            text = """
Audit Log: every sensor event, broadcast, mode change, medical reading.
Intent tags: TELEMETRY | ALERT | MEDICAL | SYSTEM | AUTH
AUTO:THERMAL_THROTTLE (bat >42°C) | AUTO:BATTERY_HOT (>45°C) | ACOUSTIC:RX/TX
Export as JSON. RAG-style keyword search built in.
ACTION:navigate:audit""".trim()
        ),
        KbEntry(
            keys = listOf("theory", "unitary", "manifold", "kaluza", "klein", "second", "law",
                "thermodynamics", "geometric", "identity", "ftum", "ueum", "arrow", "time", "alpha"),
            text = """
Unitary Manifold (ThomasCory Walker-Pearson, 2026):
CLAIM: Second Law of Thermodynamics is a geometric identity.
G_μν + λ²(H_μρH_ν^ρ − ¼g_μν H²) + αRφ²g_μν = 8πG₄ T_μν    α = φ₀⁻² (derived)
∇_μ J^μ_inf = 0 — information covariantly conserved, nothing erased.
FTUM: U=I+H+T, UΨ*=Ψ*. UEUM: Ẍ^a + Γ^a_{bc}Ẋ^bẊ^c = G_U^{ab}∇_b S_U + ...
Confirmed: nₛ=0.9635 ✓. Falsifier: β=0.3513° (LiteBIRD 2030–32).
Gaps: CMB amplitude ×4–7 suppressed; φ₀ self-consistency open.
5062 tests, 0 failures. github.com/wuzbak/Unitary-Manifold-""".trim()
        ),
        KbEntry(
            keys = listOf("termux", "python", "script", "setup", "ollama", "install", "run", "bash"),
            text = """
Run AI locally in Termux on this device:
  pkg install ollama   # or download ARM64 binary
  ollama run llama3.2:3b
Then the Pentacorder Assistant uses it automatically.
Full stack bootstrap:
  bash /sdcard/setup_android.sh
  python ~/diary/Gibberlink/scripts/noise_calibrate.py --sweep --play
ACTION:code:bash:Start local Ollama in Termux
```
#!/data/data/com.termux/files/usr/bin/bash
# Start Ollama in background and verify
ollama serve &>/dev/null &
sleep 3
curl -s http://127.0.0.1:11434/api/tags | python3 -c \
  "import sys,json; m=json.load(sys.stdin).get('models',[]); print(f'Ollama ready — {len(m)} model(s)')"
```""".trim()
        ),
        KbEntry(
            keys = listOf("calibration", "calibrate", "wizard", "first", "setup", "configure", "noise"),
            text = """
Calibration wizard (auto-runs on first launch):
  1. Device identity  2. Audio sweep (find ggwave safe_ceiling_hz for Dolby Atmos)
  3. Role selection   4. Baseline vitals   5. Trust seed (β·C init)
Re-run: Dashboard → Settings → Recalibrate.
S24 Ultra: Dolby Atmos may affect FSK. Run noise_calibrate.py to find ceiling.
ACTION:code:bash:Run calibration sweep in Termux
```
cd ~/diary/Gibberlink
python scripts/noise_calibrate.py --sweep --play
cat experiments/calibration.json
```""".trim()
        ),
        KbEntry(
            keys = listOf("dashboard", "sentinel", "mood", "sos", "analysis", "anomaly", "watchful"),
            text = """
Dashboard:
  Mode ring: colour-coded with heartbeat animation
  Sentinel moods: CALM (nominal) | WATCHFUL (soft anomaly) | ALERT (hard anomaly) | CRITICAL (emergency)
  Ollama card: local LLM interprets current state (needs Ollama in Termux)
  SOS FAB: one-tap RED mode broadcast
ACTION:navigate:dashboard""".trim()
        ),
    )

    // ── TF-IDF retrieval ──────────────────────────────────────────────────────

    private fun tokenize(text: String): Set<String> =
        Regex("[a-zA-Z0-9_]+").findAll(text.lowercase()).map { it.value }.toSet()

    private fun kbScore(qTokens: Set<String>, entry: KbEntry): Float {
        val keyHits  = entry.keys.count { it in qTokens }.toFloat()
        val bodyHits = qTokens.count { it in entry.text.lowercase() }.toFloat()
        return keyHits * 2.5f + bodyHits
    }

    private fun retrieve(query: String, topK: Int = 3): List<KbEntry> {
        val qt = tokenize(query)
        return KB.map { it to kbScore(qt, it) }
            .filter  { it.second > 0f }
            .sortedByDescending { it.second }
            .take(topK)
            .map { it.first }
    }

    // ── Remote API (OpenAI-compatible, internet) ───────────────────────────────

    /**
     * Call any OpenAI-compatible remote endpoint.
     * [endpoint] defaults to official OpenAI; can be overridden to any compatible host.
     */
    private suspend fun callRemoteApi(
        prompt: String,
        apiKey: String,
        endpoint: String = "https://api.openai.com/v1/chat/completions",
        model: String    = "gpt-4o-mini",
    ): String? = withContext(Dispatchers.IO) {
        if (apiKey.isBlank()) return@withContext null
        try {
            val url  = URL(endpoint)
            val conn = (url.openConnection() as HttpURLConnection).apply {
                requestMethod = "POST"
                connectTimeout = 8_000
                readTimeout    = 45_000
                doOutput       = true
                setRequestProperty("Content-Type",  "application/json")
                setRequestProperty("Authorization", "Bearer $apiKey")
            }
            val body = JSONObject().apply {
                put("model", model)
                put("temperature", 0.2)
                put("max_tokens", 600)
                put("messages", JSONArray().apply {
                    put(JSONObject().apply { put("role", "system"); put("content", SYSTEM_PROMPT) })
                    put(JSONObject().apply { put("role", "user");   put("content", prompt) })
                })
            }.toString()
            conn.outputStream.use { it.write(body.toByteArray()) }
            if (conn.responseCode == 200) {
                val resp = BufferedReader(InputStreamReader(conn.inputStream)).use { it.readText() }
                return@withContext JSONObject(resp)
                    .getJSONArray("choices")
                    .getJSONObject(0)
                    .getJSONObject("message")
                    .getString("content")
                    .trim()
            } else {
                Log.w(TAG, "Remote API HTTP ${conn.responseCode}")
                conn.disconnect()
            }
        } catch (e: Exception) {
            Log.d(TAG, "Remote API unavailable: ${e.message}")
        }
        null
    }

    // ── Local Ollama ──────────────────────────────────────────────────────────

    private suspend fun callOllama(
        prompt: String,
        ollamaUrl: String        = "http://127.0.0.1:11434",
        models: List<String>     = listOf("llama3.2:3b", "llama3.2", "llama3", "mistral", "gemma2:2b"),
    ): String? = withContext(Dispatchers.IO) {
        for (model in models) {
            try {
                val url  = URL("$ollamaUrl/api/chat")
                val conn = (url.openConnection() as HttpURLConnection).apply {
                    requestMethod  = "POST"
                    connectTimeout = 3_000
                    readTimeout    = 35_000
                    doOutput       = true
                    setRequestProperty("Content-Type", "application/json")
                }
                val body = JSONObject().apply {
                    put("model",  model)
                    put("stream", false)
                    put("messages", JSONArray().apply {
                        put(JSONObject().apply { put("role", "system"); put("content", SYSTEM_PROMPT) })
                        put(JSONObject().apply { put("role", "user");   put("content", prompt) })
                    })
                    put("options", JSONObject().apply {
                        put("temperature",  0.2)
                        put("num_predict",  500)
                    })
                }.toString()
                conn.outputStream.use { it.write(body.toByteArray()) }
                if (conn.responseCode == 200) {
                    val resp = BufferedReader(InputStreamReader(conn.inputStream)).use { it.readText() }
                    val content = JSONObject(resp)
                        .optJSONObject("message")?.optString("content")?.trim()
                    if (!content.isNullOrEmpty()) {
                        Log.d(TAG, "Ollama ok — model=$model ${content.length} chars")
                        return@withContext content
                    }
                }
                conn.disconnect()
            } catch (e: Exception) {
                Log.d(TAG, "Ollama model=$model: ${e.message}")
            }
        }
        null
    }

    // ── KB answer builder ─────────────────────────────────────────────────────

    private fun buildKbAnswer(query: String, hits: List<KbEntry>, liveCtx: String): String {
        val sb = StringBuilder()
        if (liveCtx.isNotEmpty()) {
            sb.appendLine("📡 **Live device context**")
            sb.appendLine(liveCtx)
            sb.appendLine()
        }
        hits.forEach { entry -> sb.appendLine(entry.text).appendLine() }
        return sb.toString().trimEnd()
    }

    private fun fallbackAnswer(query: String): String {
        val lower = query.lowercase()
        return when {
            "help" in lower || "how" in lower ->
                "Six tabs: Dashboard | Medical | Transmit | Pentacorder | Translate | Audit.\n" +
                "Every sensor maps to a Unitary-Manifold field. Tap any reading card for detail.\n" +
                "For full AI: start Ollama in Termux → `ollama run llama3.2:3b`\n" +
                "Or configure a remote API key in Settings."
            "error" in lower || "fail" in lower || "problem" in lower ->
                "Check: (1) Permissions — RECORD_AUDIO, LOCATION, BODY_SENSORS granted?\n" +
                "(2) AudioLoopService in notification bar? (3) Calibration complete?\n" +
                "Dashboard shows a calibration prompt if not run yet."
            "α" in query || "alpha" in lower ->
                "α = φ₀⁻² — falls out of the cross-block Riemann term in the KK reduction.\n" +
                "Not a free parameter. It couples the 5th dimension to 4D curvature."
            "information" in lower || "lost" in lower ->
                "∇_μ J^μ_inf = 0  J^μ_inf = φ²u^μ — covariantly conserved.\n" +
                "Nothing is erased. This is the geometric statement of the Second Law."
            else ->
                "I don't have that in my local knowledge base.\n" +
                "Start Ollama in Termux for full intelligence:\n" +
                "  ollama run llama3.2:3b\n" +
                "Or configure a remote API key in Settings → Assistant."
        }
    }

    // ── Public API ─────────────────────────────────────────────────────────────

    /**
     * Ask the Pentacorder Assistant a question.
     *
     * @param query       User's question or command.
     * @param liveContext Live device snapshot string (sensors, Pentad, vitals) to inject as context.
     * @param apiKey      Remote API key (empty → skip remote API).
     * @param apiEndpoint Remote API endpoint URL (default: OpenAI).
     * @param apiModel    Remote model name.
     * @return            [AssistantResponse] with display text and zero or more executable actions.
     */
    suspend fun ask(
        query: String,
        liveContext: String  = "",
        apiKey: String       = "",
        apiEndpoint: String  = "https://api.openai.com/v1/chat/completions",
        apiModel: String     = "gpt-4o-mini",
    ): AssistantResponse {
        val prompt = buildString {
            if (liveContext.isNotEmpty()) {
                appendLine("=== LIVE DEVICE CONTEXT ===")
                appendLine(liveContext)
                appendLine("=== END CONTEXT ===")
                appendLine()
            }
            append(query)
        }

        // 1 — Remote API (internet, best quality)
        if (apiKey.isNotBlank()) {
            val raw = callRemoteApi(prompt, apiKey, apiEndpoint, apiModel)
            if (raw != null) {
                val (text, actions) = parseActions(raw)
                return AssistantResponse(text = text, actions = actions, source = ResponseSource.REMOTE_API)
            }
        }

        // 2 — Local Ollama
        val ollamaRaw = callOllama(prompt)
        if (ollamaRaw != null) {
            val (text, actions) = parseActions(ollamaRaw)
            return AssistantResponse(text = text, actions = actions, source = ResponseSource.OLLAMA)
        }

        // 3 — Static KB fallback
        val hits = retrieve(query)
        val rawKb = if (hits.isEmpty()) fallbackAnswer(query) else buildKbAnswer(query, hits, liveContext)
        val (text, actions) = parseActions(rawKb)
        return AssistantResponse(text = text, actions = actions, source = ResponseSource.STATIC_KB)
    }
}

// ── Data types ────────────────────────────────────────────────────────────────

data class KbEntry(val keys: List<String>, val text: String)

enum class ResponseSource { REMOTE_API, OLLAMA, STATIC_KB }

data class AssistantResponse(
    val text:    String,
    val actions: List<AssistantAction> = emptyList(),
    val source:  ResponseSource        = ResponseSource.STATIC_KB,
)

/**
 * Actions the assistant can suggest — each rendered as a tappable chip in the UI.
 * When tapped, the [AssistantViewModel] routes them to the appropriate callback.
 */
sealed class AssistantAction {
    /** Switch the bottom navigation to a named tab. */
    data class Navigate(val tab: String) : AssistantAction()

    /** Trigger a WiFi RSSI scan. */
    object ScanWifi : AssistantAction()

    /** Trigger WiFi Direct peer discovery. */
    object DiscoverPeers : AssistantAction()

    /** Set the operational mode (GREEN / RED / BLUE / AMBER). */
    data class SetMode(val mode: String) : AssistantAction()

    /** Set the active user role (DEFAULT / NURSE / FIRST_RESPONDER / ENGINEER). */
    data class SetRole(val role: String) : AssistantAction()

    /** Pre-populate the Translate tab's source field. */
    data class PopulateTranslate(val text: String) : AssistantAction()

    /**
     * Generated code block — displayed in the chat with a copy button.
     * [language] is the syntax-highlight hint (bash, python, kotlin…).
     * [description] is a one-line human label.
     * [code] is the complete, paste-ready source.
     */
    data class GenerateCode(
        val language:    String,
        val description: String,
        val code:        String,
    ) : AssistantAction()

    // ── Living / adaptive UI directives ──────────────────────────────────────

    /**
     * Inject a new card into the Dashboard.
     * The card persists across sessions via [AdaptiveStateHolder].
     */
    data class AddDashboardCard(
        val id:       String,
        val title:    String,
        val body:     String,
        val severity: String = "INFO",
        val icon:     String = "💡",
    ) : AssistantAction()

    /** Remove a previously injected Dashboard card by ID. */
    data class RemoveDashboardCard(val id: String) : AssistantAction()

    /**
     * Pin a sensor/manifold field to the top of the Pentacorder view.
     * [fieldName] matches a known field key (e.g. "pressure_hpa", "mag_ut").
     */
    data class PinMetric(val fieldName: String) : AssistantAction()

    /** Remove a pinned metric. */
    data class UnpinMetric(val fieldName: String) : AssistantAction()

    /**
     * Inject a contextual hint into a specific screen.
     * [screenKey] is the nav route: dashboard|medical|transmit|pentacorder|translate|audit
     */
    data class InjectHint(val screenKey: String, val hint: String) : AssistantAction()

    /** Clear an injected hint. */
    data class ClearHint(val screenKey: String) : AssistantAction()

    /**
     * Start a named background sensor monitoring job.
     * The job wakes periodically, checks the named sensor, and posts a
     * Dashboard card if the threshold is crossed.
     */
    data class StartMonitoring(
        val id:              String,
        val label:           String,
        val sensorKey:       String,
        val intervalSeconds: Int    = 60,
        val thresholdDescription: String = "",
    ) : AssistantAction()

    /** Stop a named monitoring job. */
    data class StopMonitoring(val id: String) : AssistantAction()

    /** Send a local notification to the device notification tray. */
    data class PushNotification(val title: String, val message: String) : AssistantAction()
}
