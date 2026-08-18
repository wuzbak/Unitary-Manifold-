package com.gibbernode

import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gibbernode.gibberwave.AdaptiveStateHolder
import com.gibbernode.gibberwave.AdaptiveState
import com.gibbernode.gibberwave.AssistantAction
import com.gibbernode.gibberwave.AssistantEngine
import com.gibbernode.gibberwave.AssistantResponse
import com.gibbernode.gibberwave.CardSeverity
import com.gibbernode.gibberwave.InjectedCard
import com.gibbernode.gibberwave.MonitoringJob
import com.gibbernode.gibberwave.ResponseSource
import com.gibbernode.gibberwave.SensorBridge
import com.gibbernode.gibberwave.SensorBridgeSnapshot
import com.gibbernode.interpret.PentadState
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

private const val BATTERY_WARN_THROTTLE_MS  = 300_000L  // 5 min
private const val BATTERY_HOT_THROTTLE_MS   = 120_000L  // 2 min
private const val PRESSURE_WARN_THROTTLE_MS = 600_000L  // 10 min
private const val BIOMETRIC_WARN_THROTTLE_MS = 180_000L // 3 min

private const val HR_TACHYCARDIA_THRESHOLD  = 130
private const val HR_BRADYCARDIA_THRESHOLD  = 40
private const val HR_SEVERE_TACHY_THRESHOLD = 150
private const val HR_SEVERE_BRADY_THRESHOLD = 35
private const val SPO2_HYPOXIA_THRESHOLD    = 92

private const val NOTIF_CHANNEL = "pentacorder_assistant"

/**
 * AssistantViewModel — the living brain of the Pentacorder Assistant.
 *
 * Responsibilities:
 *  1. Manages the chat message history shown in [AssistantSheet].
 *  2. Executes [AssistantAction]s produced by [AssistantEngine]:
 *       - Navigate tabs via a callback provided by MainActivity
 *       - Mutate [AdaptiveStateHolder] (add/remove cards, pin metrics, inject hints)
 *       - Start/stop background monitoring coroutines
 *       - Post local notifications
 *       - Copy code to clipboard
 *  3. Proactive sentinel: watches [SensorBridge] and surfaces anomalies
 *     as assistant suggestions without the user asking.
 *  4. Persists API config and adaptive UI state across sessions.
 */
@HiltViewModel
class AssistantViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
    private val engine:          AssistantEngine,
    private val adaptive:        AdaptiveStateHolder,
    private val sensorBridge:    SensorBridge,
) : ViewModel() {

    // ── UI state ──────────────────────────────────────────────────────────────

    private val _uiState = MutableStateFlow(AssistantUiState())
    val uiState: StateFlow<AssistantUiState> = _uiState.asStateFlow()

    val adaptiveState: StateFlow<AdaptiveState> = adaptive.liveState

    // ── Navigation callback (wired by MainActivity) ───────────────────────────

    var onNavigate: ((String) -> Unit)? = null

    // ── Active monitoring jobs (coroutines keyed by job id) ───────────────────

    private val monitoringJobs = mutableMapOf<String, Job>()

    // ── Init ──────────────────────────────────────────────────────────────────

    init {
        createNotificationChannel()

        viewModelScope.launch {
            // Hydrate adaptive state from DataStore
            adaptive.hydrate()
        }

        // Flush DataStore writes whenever adaptive state flags a pending persist
        viewModelScope.launch {
            adaptive.pendingPersist.collectLatest { json ->
                json ?: return@collectLatest
                adaptive.flushPersist(json)
            }
        }

        // Restart any monitoring jobs persisted from a previous session
        viewModelScope.launch {
            adaptive.liveState.first().activeJobs.forEach { restartMonitoringJob(it) }
        }

        // Keep activeJobs in UI state in sync with adaptive live state so the
        // sheet can render the monitor list without exposing AdaptiveStateHolder
        viewModelScope.launch {
            adaptive.liveState.collect { s ->
                _uiState.update { it.copy(activeJobs = s.activeJobs) }
            }
        }

        // Wire live Pentad coherence from TranslateViewModel via the SensorBridge
        viewModelScope.launch {
            sensorBridge.pentad.collect { snap ->
                // PentadState.situationCoherence is a computed property (1 - meanInfoGap),
                // not a constructor parameter — it is automatically recomputed from the
                // five phi values below and does not need to be passed explicitly.
                currentPentad = PentadState(
                    phiUniv  = snap.phiUniv,
                    phiBrain = snap.phiBrain,
                    phiHuman = snap.phiHuman,
                    phiAI    = snap.phiAI,
                    phiTrust = snap.phiTrust,
                )
            }
        }

        // Proactive sentinel — watch sensor bridge for anomalies
        startProactiveSentinel()
    }

    // ── Chat interaction ──────────────────────────────────────────────────────

    fun onInputChanged(text: String) {
        _uiState.update { it.copy(input = text) }
    }

    fun sendMessage() {
        val text = _uiState.value.input.trim()
        if (text.isEmpty()) return

        val userMsg = ChatMessage(role = MessageRole.USER, text = text)
        _uiState.update { it.copy(
            messages = it.messages + userMsg,
            input    = "",
            isLoading = true,
        )}

        viewModelScope.launch {
            val apiKey      = adaptive.remoteApiKey.first()
            val apiEndpoint = adaptive.remoteApiEndpoint.first()
            val apiModel    = adaptive.remoteApiModel.first()
            val liveCtx     = buildLiveContext()

            val response = engine.ask(
                query       = text,
                liveContext = liveCtx,
                apiKey      = apiKey,
                apiEndpoint = apiEndpoint,
                apiModel    = apiModel,
            )

            val badge = when (response.source) {
                ResponseSource.REMOTE_API -> "🌐"
                ResponseSource.OLLAMA     -> "🦙"
                ResponseSource.STATIC_KB  -> "📚"
            }

            val assistantMsg = ChatMessage(
                role    = MessageRole.ASSISTANT,
                text    = response.text,
                badge   = badge,
                actions = response.actions,
            )

            _uiState.update { it.copy(
                messages  = it.messages + assistantMsg,
                isLoading = false,
            )}

            // Auto-execute unambiguous single-outcome actions
            response.actions.filterIsInstance<AssistantAction.InjectHint>().forEach { executeAction(it) }
            response.actions.filterIsInstance<AssistantAction.AddDashboardCard>().forEach { executeAction(it) }
        }
    }

    /** Execute an action from a tapped chip or auto-execution. */
    fun executeAction(action: AssistantAction) {
        when (action) {
            is AssistantAction.Navigate ->
                onNavigate?.invoke(action.tab)

            AssistantAction.ScanWifi ->
                appendSystemNote("📡 WiFi scan requested — open Pentacorder → Connectivity tab.")

            AssistantAction.DiscoverPeers ->
                appendSystemNote("📡 Peer discovery requested — open Pentacorder → Connectivity tab.")

            is AssistantAction.SetMode ->
                appendSystemNote("🔴 Mode change to ${action.mode} — open Transmit tab and select mode.")

            is AssistantAction.SetRole ->
                appendSystemNote("👤 Role set to ${action.role} — open Translate tab and select role.")

            is AssistantAction.PopulateTranslate ->
                appendSystemNote("📝 Populated translate field: \"${action.text}\" — open Translate tab.")

            is AssistantAction.GenerateCode -> {
                // Copy to clipboard automatically
                val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                clipboard.setPrimaryClip(ClipData.newPlainText("Pentacorder Code", action.code))
                appendSystemNote("📋 Copied to clipboard: ${action.description}")
            }

            is AssistantAction.AddDashboardCard -> {
                val severity = runCatching { CardSeverity.valueOf(action.severity) }.getOrDefault(CardSeverity.INFO)
                adaptive.addDashboardCard(InjectedCard(
                    id = action.id, title = action.title, body = action.body,
                    severity = severity, icon = action.icon,
                ))
                appendSystemNote("✅ Added card '${action.title}' to Dashboard.")
            }

            is AssistantAction.RemoveDashboardCard -> {
                adaptive.removeDashboardCard(action.id)
                appendSystemNote("🗑 Removed Dashboard card ${action.id}.")
            }

            is AssistantAction.PinMetric -> {
                adaptive.pinMetric(action.fieldName)
                appendSystemNote("📌 Pinned metric '${action.fieldName}' to Pentacorder top.")
            }

            is AssistantAction.UnpinMetric -> {
                adaptive.unpinMetric(action.fieldName)
                appendSystemNote("📌 Unpinned '${action.fieldName}'.")
            }

            is AssistantAction.InjectHint -> {
                adaptive.injectHint(action.screenKey, action.hint)
                appendSystemNote("💡 Hint injected into ${action.screenKey} screen.")
            }

            is AssistantAction.ClearHint -> {
                adaptive.clearHint(action.screenKey)
                appendSystemNote("🧹 Cleared hint from ${action.screenKey}.")
            }

            is AssistantAction.StartMonitoring -> {
                val job = MonitoringJob(
                    id = action.id, label = action.label, sensorKey = action.sensorKey,
                    intervalSeconds = action.intervalSeconds, thresholdDescription = action.thresholdDescription,
                )
                adaptive.addMonitoringJob(job)
                restartMonitoringJob(job)
                appendSystemNote("🔁 Started monitoring: ${action.label} every ${action.intervalSeconds}s.")
            }

            is AssistantAction.StopMonitoring -> {
                monitoringJobs.remove(action.id)?.cancel()
                adaptive.removeMonitoringJob(action.id)
                appendSystemNote("⏹ Stopped monitoring job: ${action.id}.")
            }

            is AssistantAction.PushNotification ->
                postNotification(action.title, action.message)
        }
    }

    // ── API config ────────────────────────────────────────────────────────────

    fun saveApiConfig(key: String, endpoint: String, model: String) {
        viewModelScope.launch {
            adaptive.setApiKey(key)
            adaptive.setApiEndpoint(endpoint)
            adaptive.setApiModel(model)
            appendSystemNote("⚙️ API config saved. Source: ${if (key.isNotBlank()) "Remote API" else "Ollama / KB"}.")
        }
    }

    // ── Proactive sentinel ─────────────────────────────────────────────────────

    /**
     * Watches the SensorBridge and fires unsolicited assistant notes
     * when notable conditions are detected.  Throttled to prevent flooding.
     */
    private fun startProactiveSentinel() {
        viewModelScope.launch {
            var lastBatWarning   = 0L
            var lastPressureWarn = 0L

            sensorBridge.sensorSnapshot.collectLatest { snap ->
                snap ?: return@collectLatest
                val now = System.currentTimeMillis()

                if (snap.batteryPct in 1..19 && now - lastBatWarning > BATTERY_WARN_THROTTLE_MS) {
                    lastBatWarning = now
                    fireProactiveNote(
                        icon    = "🔋",
                        message = "Battery at ${snap.batteryPct}% — CRITICAL. " +
                            "φ energy scalar is depleted. Recommend GREEN mode only.",
                        cardId  = "auto_bat_critical",
                        severity = CardSeverity.CRITICAL,
                    )
                }

                if (snap.batteryTempC > 45f && now - lastBatWarning > BATTERY_HOT_THROTTLE_MS) {
                    lastBatWarning = now
                    fireProactiveNote(
                        icon    = "🌡",
                        message = "Battery temp ${snap.batteryTempC.toInt()}°C — HOT. " +
                            "φ scalar overheated. Suspend PowerShare immediately.",
                        cardId  = "auto_bat_hot",
                        severity = CardSeverity.WARNING,
                    )
                }

                if (snap.pressureHpa > 0f && snap.pressureHpa < 960f && now - lastPressureWarn > PRESSURE_WARN_THROTTLE_MS) {
                    lastPressureWarn = now
                    fireProactiveNote(
                        icon    = "⛈",
                        message = "Pressure ${snap.pressureHpa.toInt()} hPa — EXTREME LOW. " +
                            "B_4 compact-dimension: severe weather or below-ground. " +
                            "Nurse: SpO₂ reads ~2% low — add correction.",
                        cardId  = "auto_pressure_extreme",
                        severity = CardSeverity.CRITICAL,
                    )
                }
            }
        }

        viewModelScope.launch {
            var lastBioWarn = 0L
            sensorBridge.biometrics.collectLatest { bio ->
                bio ?: return@collectLatest
                val now  = System.currentTimeMillis()
                val hr   = bio.hrBpm ?: return@collectLatest
                val spo2 = bio.spo2Pct

                if ((hr > HR_TACHYCARDIA_THRESHOLD || hr < HR_BRADYCARDIA_THRESHOLD) && now - lastBioWarn > BIOMETRIC_WARN_THROTTLE_MS) {
                    lastBioWarn = now
                    val severity = if (hr > HR_SEVERE_TACHY_THRESHOLD || hr < HR_SEVERE_BRADY_THRESHOLD) CardSeverity.CRITICAL else CardSeverity.WARNING
                    val msg = if (hr > HR_TACHYCARDIA_THRESHOLD)
                        "HR $hr bpm — SEVERE TACHYCARDIA. Ψ_brain severely deviated. NEWS2 escalation advised."
                    else
                        "HR $hr bpm — SEVERE BRADYCARDIA. Ψ_brain severely deviated. Seek clinical assessment."
                    fireProactiveNote(icon = "❤️", message = msg, cardId = "auto_hr_warn", severity = severity)
                }

                if (spo2 != null && spo2 < SPO2_HYPOXIA_THRESHOLD && now - lastBioWarn > BIOMETRIC_WARN_THROTTLE_MS) {
                    lastBioWarn = now
                    fireProactiveNote(
                        icon    = "🫁",
                        message = "SpO₂ $spo2% — HYPOXIA. O₂ supplementation indicated. " +
                            "If altitude > 2500 m: normal threshold adjustment applies.",
                        cardId  = "auto_spo2_warn",
                        severity = if (spo2 < 85) CardSeverity.CRITICAL else CardSeverity.WARNING,
                    )
                }
            }
        }
    }

    private fun fireProactiveNote(
        icon:     String,
        message:  String,
        cardId:   String,
        severity: CardSeverity,
    ) {
        val title = when (severity) {
            CardSeverity.CRITICAL -> "⚠ Critical Alert"
            CardSeverity.WARNING  -> "⚠ Warning"
            CardSeverity.CAUTION  -> "ℹ Caution"
            CardSeverity.INFO     -> "💡 Note"
        }
        // Add to chat as proactive assistant message
        val msg = ChatMessage(
            role    = MessageRole.ASSISTANT,
            text    = "$icon $message",
            badge   = "🔍",
            isProactive = true,
        )
        _uiState.update { it.copy(messages = it.messages + msg) }

        // Inject a Dashboard card
        adaptive.addDashboardCard(InjectedCard(
            id = cardId, title = title, body = message, severity = severity, icon = icon,
        ))

        // Post a notification for CRITICAL / WARNING
        if (severity in listOf(CardSeverity.CRITICAL, CardSeverity.WARNING)) {
            postNotification(title, message)
        }
    }

    // ── Background monitoring jobs ─────────────────────────────────────────────

    private fun restartMonitoringJob(jobDef: MonitoringJob) {
        monitoringJobs[jobDef.id]?.cancel()
        monitoringJobs[jobDef.id] = viewModelScope.launch {
            while (true) {
                delay(jobDef.intervalSeconds * 1_000L)
                val snap = sensorBridge.sensorSnapshot.value ?: continue
                val reading = readSensorValue(snap, jobDef.sensorKey)
                if (reading != null) {
                    val note = "${jobDef.label}: ${jobDef.sensorKey} = ${"%.2f".format(reading)}"
                    adaptive.addDashboardCard(InjectedCard(
                        id       = "monitor_${jobDef.id}",
                        title    = "📊 ${jobDef.label}",
                        body     = note + if (jobDef.thresholdDescription.isNotEmpty()) "\n${jobDef.thresholdDescription}" else "",
                        severity = CardSeverity.INFO,
                        icon     = "📊",
                    ))
                }
            }
        }
    }

    private fun readSensorValue(snap: SensorBridgeSnapshot, key: String): Float? = when (key) {
        "pressure_hpa"    -> snap.pressureHpa.takeIf { it > 0f }
        "heart_rate_bpm"  -> snap.heartRateBpm.toFloat().takeIf { it > 0f }
        "battery_pct"     -> snap.batteryPct.toFloat().takeIf { it >= 0 }
        "battery_temp_c"  -> snap.batteryTempC.takeIf { it > 0f }
        "accel_mag"       -> snap.accelMag.takeIf { it > 0f }
        "mag_ut"          -> snap.magMag.takeIf { it > 0f }
        "light_lux"       -> snap.lightLux.takeIf { it >= 0f }
        "humidity_pct"    -> snap.humidityPct.takeIf { it > 0f }
        "ambient_temp_c"  -> snap.ambientTempC.takeIf { it > 0f }
        "gps_acc_m"       -> snap.gpsAccM.takeIf { it > 0f }
        else              -> null
    }

    // ── Live context builder ──────────────────────────────────────────────────

    /**
     * Builds a compact context string injected into every AI prompt so the
     * assistant knows the current device state without being asked.
     */
    fun buildLiveContext(): String {
        val snap = sensorBridge.sensorSnapshot.value
        val bio  = sensorBridge.biometrics.value
        val sb   = StringBuilder()

        snap?.let { s ->
            if (s.batteryPct >= 0) sb.appendLine("Battery: ${s.batteryPct}% @ ${s.batteryTempC}°C")
            if (s.pressureHpa > 0f) sb.appendLine("Pressure: ${"%.1f".format(s.pressureHpa)} hPa")
            if (s.accelMag > 0f) sb.appendLine("Accel magnitude: ${"%.2f".format(s.accelMag)} m/s²")
            if (s.magMag > 0f) sb.appendLine("Magnetic field: ${"%.1f".format(s.magMag)} µT")
            if (s.lightLux >= 0f) sb.appendLine("Light: ${"%.0f".format(s.lightLux)} lux")
            if (s.latitude != 0.0) sb.appendLine("GPS: ${"%.4f".format(s.latitude)}, ${"%.4f".format(s.longitude)} ±${s.gpsAccM.toInt()}m")
            if (s.heartRateBpm > 0) sb.appendLine("HR (sensor): ${s.heartRateBpm} bpm")
        }
        bio?.let { b ->
            b.hrBpm?.let { sb.appendLine("HR (medical): $it bpm") }
            b.spo2Pct?.let { sb.appendLine("SpO₂: $it%") }
        }

        val jobs = adaptive.liveState.value.activeJobs
        if (jobs.isNotEmpty()) sb.appendLine("Active monitoring: ${jobs.joinToString { it.label }}")

        return sb.toString().trim()
    }

    /** Current Pentad to include in the context banner shown in the sheet. */
    var currentPentad: PentadState = PentadState()
        set(value) { field = value; _uiState.update { it.copy(pentad = value) } }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private fun appendSystemNote(text: String) {
        _uiState.update { it.copy(messages = it.messages + ChatMessage(
            role = MessageRole.SYSTEM, text = text, badge = "⚙️",
        ))}
    }

    private fun postNotification(title: String, message: String) {
        val nm = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val notif = NotificationCompat.Builder(context, NOTIF_CHANNEL)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle(title)
            .setContentText(message)
            .setStyle(NotificationCompat.BigTextStyle().bigText(message))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .build()
        nm.notify(System.currentTimeMillis().toInt(), notif)
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val nm = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            nm.createNotificationChannel(NotificationChannel(
                NOTIF_CHANNEL,
                "Pentacorder Assistant",
                NotificationManager.IMPORTANCE_HIGH,
            ).apply { description = "Proactive sensor alerts from the Pentacorder Assistant" })
        }
    }
}

// ── UI state ──────────────────────────────────────────────────────────────────

data class AssistantUiState(
    val messages:  List<ChatMessage> = listOf(
        ChatMessage(
            role  = MessageRole.ASSISTANT,
            text  = "Pentacorder Assistant online. ∇_μ J^μ_inf = 0.\n" +
                    "Ask me anything: sensor readings, theory, medical interpretation, " +
                    "or say \"watch battery\" / \"monitor pressure\" to start a live job.",
            badge = "🔮",
        )
    ),
    val input:      String             = "",
    val isLoading:  Boolean            = false,
    val pentad:     PentadState        = PentadState(),
    val activeJobs: List<MonitoringJob> = emptyList(),
)

data class ChatMessage(
    val role:       MessageRole,
    val text:       String,
    val badge:      String           = "",
    val actions:    List<AssistantAction> = emptyList(),
    val isProactive: Boolean         = false,
    val id:         Long             = System.currentTimeMillis(),
)

enum class MessageRole { USER, ASSISTANT, SYSTEM }
