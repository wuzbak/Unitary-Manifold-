package com.gibbernode.gibberwave

import android.app.Service
import android.content.Intent
import android.os.Binder
import android.os.IBinder
import android.util.Log
import com.gibbernode.audio.AudioEngine
import com.gibbernode.audio.TxProtocol
import com.gibbernode.security.AcousticAuth
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

private const val TAG = "Pentacorder/UPBHub"

/**
 * UPBHubService
 *
 * Universal Protocol Bridge Hub — Android Service edition.
 * Kotlin port of Gibberlink/scripts/upb_hub.py.
 *
 * Manages five named input queues:
 *   Q_ACOUSTIC  — decoded Gibberlink ggwave payloads (from AudioLoopService)
 *   Q_BLE       — BLE accessory advertisements / readings
 *   Q_SYSTEM    — Sentinel Watchdog records
 *   Q_CSI       — RF spatial tokens (WiFi RSSI / ESP32 CSI)
 *   Q_ENERGY    — Energy manager state tokens
 *
 * Every token is normalised into [CommonToken], pushed to Q_INTENT, checked
 * against the [RelayRouter] table, and (if matched) re-broadcast acoustically.
 *
 * Callers access this service via [LocalBinder] after binding.
 */
@AndroidEntryPoint
class UPBHubService : Service() {

    @Inject lateinit var audioEngine: AudioEngine
    @Inject lateinit var acousticAuth: AcousticAuth
    @Inject lateinit var relayRouter: RelayRouter

    private val hubScope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    // ── Per-protocol input channels (capacity 256 per channel) ────────────────
    val qAcoustic: Channel<CommonToken> = Channel(256)
    val qBle:      Channel<CommonToken> = Channel(256)
    val qSystem:   Channel<CommonToken> = Channel(256)
    val qCsi:      Channel<CommonToken> = Channel(256)
    val qEnergy:   Channel<CommonToken> = Channel(256)

    // ── Unified intent output ─────────────────────────────────────────────────
    private val _qIntent = MutableSharedFlow<CommonToken>(
        replay = 20,
        extraBufferCapacity = 256,
    )
    /** Hot flow of all normalised tokens.  UI components subscribe here. */
    val qIntent: SharedFlow<CommonToken> = _qIntent.asSharedFlow()

    private val drainJobs = mutableListOf<Job>()

    // ── Binder ────────────────────────────────────────────────────────────────
    inner class LocalBinder : Binder() {
        fun getHub(): UPBHubService = this@UPBHubService
    }
    private val binder = LocalBinder()
    override fun onBind(intent: Intent): IBinder = binder

    // ── Lifecycle ─────────────────────────────────────────────────────────────

    override fun onCreate() {
        super.onCreate()
        startDrainLoop(qAcoustic, SourceProtocol.ACOUSTIC)
        startDrainLoop(qBle,      SourceProtocol.BLE)
        startDrainLoop(qSystem,   SourceProtocol.SYSTEM)
        startDrainLoop(qCsi,      SourceProtocol.CSI)
        startDrainLoop(qEnergy,   SourceProtocol.ENERGY)

        // Wire acoustic decoder output → Q_ACOUSTIC
        drainJobs += hubScope.launch {
            audioEngine.decodedPayloads.collect { raw ->
                val token = normalise(raw, SourceProtocol.ACOUSTIC)
                qAcoustic.trySend(token)
            }
        }

        Log.i(TAG, "UPB Hub started — 5 channels active")
    }

    override fun onDestroy() {
        drainJobs.forEach { it.cancel() }
        hubScope.cancel()
        Log.i(TAG, "UPB Hub stopped")
        super.onDestroy()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int = START_STICKY

    // ── Ingest API ─────────────────────────────────────────────────────────────

    /**
     * Submit a raw payload string from any source.
     * The token is normalised and pushed to the appropriate queue.
     */
    fun ingest(raw: String, source: SourceProtocol) {
        val token = normalise(raw, source)
        val queue = when (source) {
            SourceProtocol.ACOUSTIC -> qAcoustic
            SourceProtocol.BLE      -> qBle
            SourceProtocol.SYSTEM   -> qSystem
            SourceProtocol.CSI      -> qCsi
            SourceProtocol.ENERGY   -> qEnergy
            else                    -> qSystem
        }
        queue.trySend(token).also { result ->
            if (result.isFailure) {
                Log.w(TAG, "ingest: queue full for source=${source.name}, dropping token")
            }
        }
    }

    // ── Internal ───────────────────────────────────────────────────────────────

    /**
     * Start a drain coroutine for [channel] that:
     * 1. Emits tokens to [_qIntent] (all consumers see every token).
     * 2. Checks the relay table — if a rule fires, re-broadcasts on the target mode.
     */
    private fun startDrainLoop(
        channel: Channel<CommonToken>,
        @Suppress("UNUSED_PARAMETER") protocol: SourceProtocol,
    ) {
        drainJobs += hubScope.launch {
            for (token in channel) {
                // 1. Emit to the unified intent stream
                _qIntent.emit(token)

                // 2. Relay if a rule matches
                val mode = relayRouter.match(token)
                if (mode != null) {
                    relay(token, mode)
                }
            }
        }
    }

    /**
     * Re-broadcast [token] on the acoustic channel using [mode] settings.
     * RED mode broadcasts are repeated [OperationalMode.redundancy] times
     * with 300 ms gaps (matches broadcast.py behaviour).
     */
    private fun relay(token: CommonToken, mode: OperationalMode) {
        hubScope.launch(Dispatchers.IO) {
            Log.i(TAG, "Relay: ${token.source}/${token.intent} → ${mode.name}")
            val payload = acousticAuth.signPayload(token.payload) ?: token.payload
            repeat(mode.redundancy) { iteration ->
                if (iteration > 0) kotlinx.coroutines.delay(300)
                audioEngine.play(payload, TxProtocol.fromId(mode.protocol), mode.volume)
            }
        }
    }

    /**
     * Normalise a raw payload string into a [CommonToken].
     * Intent is inferred from the payload prefix (ALERT: → ALERT, else TELEMETRY).
     */
    private fun normalise(raw: String, source: SourceProtocol): CommonToken {
        val prefix = raw.substringBefore(":")
        val intent = when {
            prefix.equals("ALERT", ignoreCase = true) -> IntentTag.ALERT
            prefix.equals("INTENT", ignoreCase = true) -> IntentTag.RELAY
            else -> IntentTag.TELEMETRY
        }
        return CommonToken(
            source     = source,
            intent     = intent,
            payload    = raw,
            rawPayload = raw,
        )
    }
}
