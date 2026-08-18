package com.gibbernode.feature.dashboard

import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.BatteryManager
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gibbernode.gibberwave.AdaptiveState
import com.gibbernode.gibberwave.AdaptiveStateHolder
import com.gibbernode.gibberwave.CommonToken
import com.gibbernode.gibberwave.IntentEngine
import com.gibbernode.gibberwave.IntentTag
import com.gibbernode.gibberwave.OperationalMode
import com.gibbernode.gibberwave.SentinelBus
import com.gibbernode.gibberwave.SentinelMood
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * DashboardViewModel
 *
 * Holds all observable state for the Dashboard tab.
 * Sources data from:
 *   - [SentinelBus] — live SYS tokens from the watchdog worker
 *   - [IntentEngine] — Ollama interpretation of anomaly tokens
 *   - Android BatteryManager — instant battery reading
 */
@HiltViewModel
class DashboardViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
    private val intentEngine: IntentEngine,
    private val adaptive: AdaptiveStateHolder,
) : ViewModel() {

    private val _state = MutableStateFlow(DashboardUiState())
    val state: StateFlow<DashboardUiState> = _state.asStateFlow()

    /** Live adaptive state from the assistant (injected cards, hints, pinned metrics). */
    val adaptiveState: StateFlow<AdaptiveState> = adaptive.liveState

    init {
        // Poll immediate battery reading
        refreshBattery()

        // Subscribe to Sentinel token bus
        SentinelBus.tokens
            .onEach { token -> handleSentinelToken(token) }
            .launchIn(viewModelScope)
    }

    /** Manually request a fresh battery reading (e.g. on pull-to-refresh). */
    fun refreshBattery() {
        val bm = context.getSystemService(Context.BATTERY_SERVICE) as BatteryManager
        val pct  = bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
        val tempC = (context.registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
            ?.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, 0) ?: 0) / 10f
        _state.update { it.copy(batteryPct = pct, batteryTempC = tempC) }
    }

    /** Switch the active operational mode (GREEN / RED / BLUE). */
    fun setMode(mode: OperationalMode) {
        _state.update { it.copy(activeMode = mode) }
    }

    /** Clear any displayed Ollama analysis (e.g. when user dismisses the card). */
    fun dismissAnalysis() {
        _state.update { it.copy(ollamaAnalysis = null) }
    }

    /** Remove an assistant-injected Dashboard card. */
    fun removeDashboardCard(id: String) {
        adaptive.removeDashboardCard(id)
    }

    /** Clear an assistant-injected screen hint for the Dashboard. */
    fun clearDashboardHint() {
        adaptive.clearHint("dashboard")
    }

    // ── Private ───────────────────────────────────────────────────────────────

    private fun handleSentinelToken(token: CommonToken) {
        // Extract SYS fields from "SYS:BV9900:{cpu}:{bat}:{anomalies}:{intent}"
        val parts = token.payload.split(":")
        if (parts.firstOrNull() == "SYS" && parts.size >= 5) {
            val cpuTempC     = parts.getOrElse(2) { "0" }.toFloatOrNull() ?: 0f
            val batPct       = parts.getOrElse(3) { "0" }.toIntOrNull() ?: 0
            val anomalyCount = parts.getOrElse(4) { "0" }.toIntOrNull() ?: 0

            val mood = when {
                anomalyCount >= 3   -> SentinelMood.CRITICAL
                anomalyCount >= 1   -> SentinelMood.STRESSED
                cpuTempC > 45f      -> SentinelMood.EXHAUSTED
                else                -> SentinelMood.CALM
            }

            _state.update { state ->
                state.copy(
                    cpuTempC       = cpuTempC,
                    batteryPct     = batPct,
                    anomalyCount   = anomalyCount,
                    sentinelMood   = mood,
                    heartbeatCount = state.heartbeatCount + 1,
                    lastToken      = token,
                )
            }
        }

        // If there's an anomaly, ask Ollama for a human-readable explanation
        if (token.intent == IntentTag.ALERT) {
            viewModelScope.launch {
                val analysis = intentEngine.query(token)
                _state.update { it.copy(ollamaAnalysis = analysis) }
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────

/**
 * DashboardUiState — immutable snapshot of everything the Dashboard needs to render.
 */
data class DashboardUiState(
    val activeMode:     OperationalMode = OperationalMode.GREEN,
    val sentinelMood:   SentinelMood    = SentinelMood.CALM,
    val batteryPct:     Int             = -1,
    val batteryTempC:   Float           = 0f,
    val cpuTempC:       Float           = -1f,
    val anomalyCount:   Int             = 0,
    val heartbeatCount: Long            = 0L,
    val lastToken:      CommonToken?    = null,
    val ollamaAnalysis: String?         = null,
)
