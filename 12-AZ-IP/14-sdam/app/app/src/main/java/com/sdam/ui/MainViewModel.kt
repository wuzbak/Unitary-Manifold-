package com.sdam.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sdam.audio.AudioEngine
import com.sdam.audio.CalibrationStore
import com.sdam.audio.FrequencyBand
import com.sdam.audio.NoiseFloorCalibrator
import com.sdam.audio.TxProtocol
import com.sdam.security.AcousticAuth
import com.sdam.security.AirGapBridge
import com.sdam.security.PayloadCipher
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.withTimeoutOrNull
import javax.inject.Inject

/**
 * TransmitMode
 *
 * SDAM-specific operational modes for the Transmit tab.
 *
 * STANDARD — unencrypted, audible-band transmission (GREEN equivalent).
 * SECURE   — AES-256-GCM encrypted payload, HMAC-SHA256 signed (BLUE equivalent).
 * DIODE    — Air-Gap Bridge mode: chunked AES-256-GCM for crossing physical
 *            air gaps (S6 Tier-1 use case).
 */
enum class TransmitMode(
    val displayName: String,
    val protocol: TxProtocol,
    val volume: Int,
    val encrypted: Boolean,
    val redundancy: Int,
) {
    STANDARD(
        displayName = "Standard",
        protocol    = TxProtocol.AUDIBLE_FAST,
        volume      = 50,
        encrypted   = false,
        redundancy  = 1,
    ),
    SECURE(
        displayName = "Secure (AES-256-GCM)",
        protocol    = TxProtocol.AUDIBLE_NORMAL,
        volume      = 50,
        encrypted   = true,
        redundancy  = 1,
    ),
    DIODE(
        displayName = "Air-Gap DIODE",
        protocol    = TxProtocol.AUDIBLE_FAST,
        volume      = 60,
        encrypted   = true,
        redundancy  = 1,
    );

    companion object {
        val DEFAULT = STANDARD
    }
}

// ─────────────────────────────────────────────────────────────────────────────

enum class CalibrateStatus { IDLE, MEASURING, TESTING, PASSED, FAILED }

data class DecodeEntry(
    val payload:   String,
    val source:    String,
    val hmacOk:    Boolean,
    val timestamp: Long,
)

data class MainUiState(
    val activeTab:          Int             = TAB_TRANSMIT,
    // Transmit
    val selectedMode:       TransmitMode    = TransmitMode.DEFAULT,
    val broadcastInput:     String          = "",
    val isBroadcasting:     Boolean         = false,
    val diodeTxChunkCount:  Int             = 0,
    // Receive
    val decodeLog:          List<DecodeEntry> = emptyList(),
    // Calibrate
    val calibrateStatus:    CalibrateStatus = CalibrateStatus.IDLE,
    val calibrateMessage:   String          = "",
    val calibratedProtocol: TxProtocol      = TxProtocol.fromId(CalibrationStore.DEFAULT_PROTOCOL_ID),
    val calibratedVolume:   Int             = CalibrationStore.DEFAULT_VOLUME,
    val calibratedBand:     FrequencyBand   = CalibrationStore.DEFAULT_FREQ_BAND,
    val noiseFloorDb:       Float           = CalibrationStore.DEFAULT_NOISE_FLOOR_DB,
    // Settings
    val keyProvisioned:     Boolean         = false,
    val debugMode:          Boolean         = false,
) {
    companion object {
        const val TAB_TRANSMIT  = 0
        const val TAB_RECEIVE   = 1
        const val TAB_CALIBRATE = 2
        const val TAB_SETTINGS  = 3
    }
}

// ─────────────────────────────────────────────────────────────────────────────

@HiltViewModel
class MainViewModel @Inject constructor(
    private val audioEngine:          AudioEngine,
    private val acousticAuth:         AcousticAuth,
    private val payloadCipher:        PayloadCipher,
    private val calibrationStore:     CalibrationStore,
    private val noiseFloorCalibrator: NoiseFloorCalibrator,
) : ViewModel() {

    private val _state = MutableStateFlow(MainUiState())
    val state: StateFlow<MainUiState> = _state.asStateFlow()

    // S6: per-session DIODE RX assembler
    private val diodeAssembler = AirGapBridge.Assembler()

    private var calibrateJob: Job? = null
    private var loopbackJob:  Job? = null

    init {
        _state.update { it.copy(keyProvisioned = payloadCipher.canEncrypt()) }
        viewModelScope.launch {
            val proto = calibrationStore.protocolId.first()
            val vol   = calibrationStore.volume.first()
            val band  = calibrationStore.freqBand.first()
            val noise = calibrationStore.noiseFloorDb.first()
            _state.update {
                it.copy(
                    calibratedProtocol = TxProtocol.fromId(proto),
                    calibratedVolume   = vol,
                    calibratedBand     = band,
                    noiseFloorDb       = noise,
                )
            }
        }
        // Collect decoded payloads from the AudioEngine
        viewModelScope.launch {
            audioEngine.decodedPayloads.collect { raw -> onDecoded(raw, hmacOk = true) }
        }
    }

    // ── Tab navigation ────────────────────────────────────────────────────────

    fun selectTab(tab: Int) = _state.update { it.copy(activeTab = tab) }

    // ── Transmit ──────────────────────────────────────────────────────────────

    fun selectMode(mode: TransmitMode) = _state.update { it.copy(selectedMode = mode) }

    fun onMessageInput(text: String) = _state.update { it.copy(broadcastInput = text) }

    fun broadcast() {
        val text = _state.value.broadcastInput.trim()
        if (text.isEmpty()) return
        val mode = _state.value.selectedMode
        _state.update { it.copy(isBroadcasting = true, broadcastInput = "") }
        viewModelScope.launch {
            when (mode) {
                TransmitMode.DIODE -> broadcastDiode(text, mode)
                else               -> broadcastStandard(text, mode)
            }
            _state.update { it.copy(isBroadcasting = false) }
        }
    }

    private suspend fun broadcastStandard(text: String, mode: TransmitMode) {
        val wirePayload = if (mode.encrypted && !_state.value.debugMode) {
            payloadCipher.encryptIfNeeded(text)
        } else {
            text
        }
        val signed = if (mode == TransmitMode.SECURE) {
            acousticAuth.signPayload(wirePayload) ?: wirePayload
        } else {
            wirePayload
        }
        repeat(mode.redundancy) { iteration ->
            if (iteration > 0) kotlinx.coroutines.delay(300)
            audioEngine.play(signed, mode.protocol, mode.volume)
        }
        appendTxLog(text, mode)
    }

    private suspend fun broadcastDiode(text: String, mode: TransmitMode) {
        val chunks = try {
            AirGapBridge.encode(text, payloadCipher::encrypt)
        } catch (e: IllegalStateException) {
            android.util.Log.e("SDAM/MainVM", "DIODE encode failed: ${e.message}")
            _state.update { it.copy(isBroadcasting = false) }
            return
        }
        for ((index, chunk) in chunks.withIndex()) {
            val signed = acousticAuth.signPayload(chunk) ?: chunk
            repeat(mode.redundancy) { iter ->
                if (iter > 0) kotlinx.coroutines.delay(200)
                audioEngine.play(signed, mode.protocol, mode.volume)
            }
            if (index < chunks.size - 1) kotlinx.coroutines.delay(300)
        }
        val displayText = "${text.take(40)}${if (text.length > 40) "…" else ""}" +
                          " [${chunks.size} chunk${if (chunks.size > 1) "s" else ""}]"
        appendTxLog(displayText, mode)
        _state.update { it.copy(diodeTxChunkCount = chunks.size) }
    }

    // ── Receive ───────────────────────────────────────────────────────────────

    fun onDecoded(raw: String, hmacOk: Boolean) {
        when {
            AirGapBridge.isDiode(raw) -> {
                val plaintext = diodeAssembler.feed(raw, payloadCipher::decrypt)
                if (plaintext != null) appendRxLog(plaintext, "RX:DIODE", hmacOk)
            }
            payloadCipher.isEncrypted(raw) -> {
                val plain = payloadCipher.decrypt(raw) ?: raw
                appendRxLog(plain, "RX:ENC", hmacOk)
            }
            else -> appendRxLog(raw, "RX:ACOUSTIC", hmacOk)
        }
    }

    private fun appendRxLog(payload: String, source: String, hmacOk: Boolean) {
        val entry = DecodeEntry(payload, source, hmacOk, System.currentTimeMillis())
        _state.update { s -> s.copy(decodeLog = (listOf(entry) + s.decodeLog).take(MAX_LOG_ENTRIES)) }
    }

    private fun appendTxLog(displayText: String, mode: TransmitMode) {
        val entry = DecodeEntry(displayText, "TX:${mode.name}", true, System.currentTimeMillis())
        _state.update { s -> s.copy(decodeLog = (listOf(entry) + s.decodeLog).take(MAX_LOG_ENTRIES)) }
    }

    // ── Calibrate ─────────────────────────────────────────────────────────────

    fun measureNoiseFloor() {
        calibrateJob?.cancel()
        calibrateJob = viewModelScope.launch {
            _state.update {
                it.copy(
                    calibrateStatus  = CalibrateStatus.MEASURING,
                    calibrateMessage = "Measuring noise floor…",
                )
            }
            val result = noiseFloorCalibrator.measure()
            _state.update {
                it.copy(
                    calibrateStatus    = CalibrateStatus.IDLE,
                    calibrateMessage   = "Noise floor: %.0f dBFS — %s recommended".format(
                        result.noiseFloorDb, result.recommendedBand.label),
                    calibratedProtocol = result.recommendedProtocol,
                    calibratedVolume   = result.recommendedVolume,
                    calibratedBand     = result.recommendedBand,
                    noiseFloorDb       = result.noiseFloorDb,
                )
            }
        }
    }

    fun selectCalibrateProtocol(protocol: TxProtocol) =
        _state.update { it.copy(calibratedProtocol = protocol) }

    fun selectCalibrateVolume(volume: Int) =
        _state.update { it.copy(calibratedVolume = volume.coerceIn(1, 100)) }

    fun runLoopback() {
        loopbackJob?.cancel()
        loopbackJob = viewModelScope.launch {
            _state.update {
                it.copy(
                    calibrateStatus  = CalibrateStatus.TESTING,
                    calibrateMessage = "Playing test tone…",
                )
            }
            audioEngine.play(
                LOOPBACK_PAYLOAD,
                _state.value.calibratedProtocol,
                _state.value.calibratedVolume,
            )
            _state.update { it.copy(calibrateMessage = "Listening for loopback…") }
            val decoded = withTimeoutOrNull(LOOPBACK_TIMEOUT_MS) {
                audioEngine.decodedPayloads.first { it.contains(LOOPBACK_MARKER) }
            }
            _state.update {
                if (decoded != null)
                    it.copy(
                        calibrateStatus  = CalibrateStatus.PASSED,
                        calibrateMessage = "✓ Loopback received. Audio channel working.",
                    )
                else
                    it.copy(
                        calibrateStatus  = CalibrateStatus.FAILED,
                        calibrateMessage = "⚠ No loopback within ${LOOPBACK_TIMEOUT_MS / 1000}s.\n" +
                            "Try higher volume or quieter environment.",
                    )
            }
        }
    }

    fun cancelLoopback() {
        loopbackJob?.cancel()
        _state.update { it.copy(calibrateStatus = CalibrateStatus.IDLE, calibrateMessage = "") }
    }

    fun saveCalibrateSettings() {
        viewModelScope.launch {
            val s = _state.value
            calibrationStore.saveCalibration(
                protocolId   = s.calibratedProtocol.id,
                volume       = s.calibratedVolume,
                freqBand     = s.calibratedBand,
                noiseFloorDb = s.noiseFloorDb,
            )
            _state.update { it.copy(calibrateMessage = "✓ Settings saved.") }
        }
    }

    // ── Settings ──────────────────────────────────────────────────────────────

    fun toggleDebugMode() = _state.update { it.copy(debugMode = !it.debugMode) }

    override fun onCleared() {
        calibrateJob?.cancel()
        loopbackJob?.cancel()
        diodeAssembler.reset()
        super.onCleared()
    }

    private companion object {
        const val MAX_LOG_ENTRIES     = 100
        const val LOOPBACK_MARKER     = "SDAM_CAL"
        const val LOOPBACK_PAYLOAD    = "SDAM_CAL_TEST_001"
        const val LOOPBACK_TIMEOUT_MS = 12_000L
    }
}
