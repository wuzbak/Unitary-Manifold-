package com.gibbernode.gibberwave

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.update
import org.json.JSONArray
import org.json.JSONObject
import javax.inject.Inject
import javax.inject.Singleton

private val Context.adaptiveDataStore: DataStore<Preferences>
    by preferencesDataStore(name = "pentacorder_adaptive")

/**
 * AdaptiveStateHolder — the living memory of the Pentacorder Assistant.
 *
 * Persists every UI adaptation the assistant has made across sessions.
 * All screens observe [liveState] and render additional content when the
 * assistant has injected cards, hints, or pinned metrics for their context.
 *
 * Writes come from [AssistantViewModel] when the user taps an action chip.
 * Reads come from any screen via Hilt injection.
 *
 * Stored in DataStore so state survives process restarts.
 */
@Singleton
class AdaptiveStateHolder @Inject constructor(
    @ApplicationContext private val context: Context,
) {
    private val store = context.adaptiveDataStore

    // ── In-memory live state (hydrated from DataStore on first access) ─────────

    private val _liveState = MutableStateFlow(AdaptiveState())
    val liveState: StateFlow<AdaptiveState> = _liveState.asStateFlow()

    // ── Remote API config ─────────────────────────────────────────────────────

    val remoteApiKey: Flow<String> =
        store.data.map { it[KEY_API_KEY] ?: "" }

    val remoteApiEndpoint: Flow<String> =
        store.data.map { it[KEY_API_ENDPOINT] ?: "https://api.openai.com/v1/chat/completions" }

    val remoteApiModel: Flow<String> =
        store.data.map { it[KEY_API_MODEL] ?: "gpt-4o-mini" }

    suspend fun setApiKey(key: String) =
        store.edit { it[KEY_API_KEY] = key }

    suspend fun setApiEndpoint(endpoint: String) =
        store.edit { it[KEY_API_ENDPOINT] = endpoint }

    suspend fun setApiModel(model: String) =
        store.edit { it[KEY_API_MODEL] = model }

    // ── Adaptive UI mutations ─────────────────────────────────────────────────

    /** Add an assistant-generated card to the Dashboard. */
    fun addDashboardCard(card: InjectedCard) {
        _liveState.update { state ->
            val existing = state.dashboardCards.filterNot { it.id == card.id }
            state.copy(dashboardCards = existing + card)
        }
        persistState()
    }

    /** Remove an assistant-generated card by ID. */
    fun removeDashboardCard(id: String) {
        _liveState.update { it.copy(dashboardCards = it.dashboardCards.filterNot { c -> c.id == id }) }
        persistState()
    }

    /** Pin a manifold field name to the top of the Pentacorder sensor list. */
    fun pinMetric(fieldName: String) {
        _liveState.update { it.copy(pinnedMetrics = (it.pinnedMetrics + fieldName).distinct().take(3)) }
        persistState()
    }

    fun unpinMetric(fieldName: String) {
        _liveState.update { it.copy(pinnedMetrics = it.pinnedMetrics - fieldName) }
        persistState()
    }

    /** Inject a context-aware hint string into a named screen slot. */
    fun injectHint(screenKey: String, hint: String) {
        _liveState.update { it.copy(screenHints = it.screenHints + (screenKey to hint)) }
        persistState()
    }

    fun clearHint(screenKey: String) {
        _liveState.update { it.copy(screenHints = it.screenHints - screenKey) }
        persistState()
    }

    /** Register a named background monitoring job. */
    fun addMonitoringJob(job: MonitoringJob) {
        _liveState.update { state ->
            state.copy(activeJobs = state.activeJobs.filterNot { it.id == job.id } + job)
        }
        persistState()
    }

    fun removeMonitoringJob(id: String) {
        _liveState.update { it.copy(activeJobs = it.activeJobs.filterNot { j -> j.id == id }) }
        persistState()
    }

    /** Persist the current in-memory state to DataStore as JSON. */
    private fun persistState() {
        val state = _liveState.value
        val json = JSONObject().apply {
            put("dashboardCards", JSONArray(state.dashboardCards.map { c ->
                JSONObject().apply {
                    put("id", c.id); put("title", c.title); put("body", c.body)
                    put("severity", c.severity.name); put("icon", c.icon)
                }
            }))
            put("pinnedMetrics", JSONArray(state.pinnedMetrics))
            put("screenHints", JSONObject(state.screenHints))
            put("activeJobs", JSONArray(state.activeJobs.map { j ->
                JSONObject().apply {
                    put("id", j.id); put("label", j.label); put("sensorKey", j.sensorKey)
                    put("intervalSeconds", j.intervalSeconds); put("thresholdDescription", j.thresholdDescription)
                }
            }))
        }.toString()
        // Fire-and-forget via a separate coroutine in the calling scope
        // (callers are always in a coroutine context via ViewModel)
        _pendingPersist.value = json
    }

    // DataStore write is triggered by AssistantViewModel observing this flow
    private val _pendingPersist = MutableStateFlow<String?>(null)
    val pendingPersist: StateFlow<String?> = _pendingPersist.asStateFlow()

    suspend fun flushPersist(json: String) {
        store.edit { it[KEY_ADAPTIVE_STATE] = json }
    }

    /** Reload from DataStore (called once from AssistantViewModel init). */
    suspend fun hydrate() {
        store.data.map { it[KEY_ADAPTIVE_STATE] }.collect { raw ->
            if (!raw.isNullOrEmpty()) {
                runCatching {
                    val json    = JSONObject(raw)
                    val cards   = json.optJSONArray("dashboardCards")?.let { arr ->
                        (0 until arr.length()).mapNotNull { i ->
                            val obj = arr.optJSONObject(i) ?: return@mapNotNull null
                            InjectedCard(
                                id       = obj.optString("id"),
                                title    = obj.optString("title"),
                                body     = obj.optString("body"),
                                severity = runCatching { CardSeverity.valueOf(obj.optString("severity", "INFO")) }.getOrDefault(CardSeverity.INFO),
                                icon     = obj.optString("icon", "💡"),
                            )
                        }
                    } ?: emptyList()
                    val pinned  = json.optJSONArray("pinnedMetrics")?.let { arr ->
                        (0 until arr.length()).map { i -> arr.optString(i) }
                    } ?: emptyList()
                    val hints   = json.optJSONObject("screenHints")?.let { obj ->
                        obj.keys().asSequence().associateWith { k -> obj.optString(k) }
                    } ?: emptyMap()
                    val jobs    = json.optJSONArray("activeJobs")?.let { arr ->
                        (0 until arr.length()).mapNotNull { i ->
                            val obj = arr.optJSONObject(i) ?: return@mapNotNull null
                            MonitoringJob(
                                id                   = obj.optString("id"),
                                label                = obj.optString("label"),
                                sensorKey            = obj.optString("sensorKey"),
                                intervalSeconds      = obj.optInt("intervalSeconds", 60),
                                thresholdDescription = obj.optString("thresholdDescription", obj.optString("thresholdNote")),
                            )
                        }
                    } ?: emptyList()
                    _liveState.update { AdaptiveState(dashboardCards = cards, pinnedMetrics = pinned, screenHints = hints, activeJobs = jobs) }
                }.onFailure { e ->
                    android.util.Log.w("Pentacorder/Adaptive", "hydrate() failed to parse DataStore JSON: ${e.message}")
                }
            }
            // Single collection — stop after first read
            return@collect
        }
    }

    companion object {
        private val KEY_API_KEY        = stringPreferencesKey("remote_api_key")
        private val KEY_API_ENDPOINT   = stringPreferencesKey("remote_api_endpoint")
        private val KEY_API_MODEL      = stringPreferencesKey("remote_api_model")
        private val KEY_ADAPTIVE_STATE = stringPreferencesKey("adaptive_state_json")
    }
}

// ── Adaptive state model ──────────────────────────────────────────────────────

data class AdaptiveState(
    /** Assistant-injected cards shown on the Dashboard below the core cards. */
    val dashboardCards: List<InjectedCard>  = emptyList(),

    /** Sensor field names pinned to the top of the Pentacorder sensor view. */
    val pinnedMetrics:  List<String>         = emptyList(),

    /** Per-screen contextual hint strings. Key = screen route name. */
    val screenHints:    Map<String, String>  = emptyMap(),

    /** Active background monitoring jobs spawned by the assistant. */
    val activeJobs:     List<MonitoringJob>  = emptyList(),
)

data class InjectedCard(
    val id:       String,
    val title:    String,
    val body:     String,
    val severity: CardSeverity = CardSeverity.INFO,
    val icon:     String       = "💡",
)

enum class CardSeverity { INFO, CAUTION, WARNING, CRITICAL }

data class MonitoringJob(
    val id:                   String,
    val label:                String,
    val sensorKey:            String,   // e.g. "pressure_hpa", "heart_rate_bpm"
    val intervalSeconds:      Int    = 60,
    val thresholdDescription: String = "",
)
