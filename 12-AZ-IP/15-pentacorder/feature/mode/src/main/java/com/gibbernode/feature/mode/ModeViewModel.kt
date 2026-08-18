package com.gibbernode.feature.mode

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gibbernode.audio.AudioEngine
import com.gibbernode.audio.FrequencyBand
import com.gibbernode.audio.NoiseFloorCalibrator
import com.gibbernode.audio.TxProtocol
import com.gibbernode.gibberwave.AuditLogDao
import com.gibbernode.gibberwave.AuditLogEntity
import com.gibbernode.gibberwave.CalibrationStore
import com.gibbernode.gibberwave.CommonToken
import com.gibbernode.gibberwave.IntentTag
import com.gibbernode.gibberwave.OperationalMode
import com.gibbernode.gibberwave.SourceProtocol
import com.gibbernode.security.AcousticAuth
import com.gibbernode.security.AirGapBridge
import com.gibbernode.security.PayloadCipher
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

@HiltViewModel
class ModeViewModel @Inject constructor(
    private val audioEngine:          AudioEngine,
    private val acousticAuth:         AcousticAuth,
    private val auditDao:             AuditLogDao,
    private val payloadCipher:        PayloadCipher,
    private val calibrationStore:     CalibrationStore,
    private val noiseFloorCalibrator: NoiseFloorCalibrator,
) : ViewModel() {

    private val _state = MutableStateFlow(ModeUiState())
    val state: StateFlow<ModeUiState> = _state.asStateFlow()

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
            _state.update { it.copy(
                calibratedProtocol = TxProtocol.fromId(proto),
                calibratedVolume   = vol,
                calibratedBand     = band,
                noiseFloorDb       = noise,
            )}
        }
    }

    // ── Tab navigation (S5) ───────────────────────────────────────────────────

    fun selectTab(tab: Int) = _state.update { it.copy(activeTab = tab) }

    // ── Mode / message ────────────────────────────────────────────────────────

    fun selectMode(mode: OperationalMode) = _state.update { it.copy(selectedMode = mode) }

    fun onMessageInput(text: String) = _state.update { it.copy(broadcastInput = text) }

    /**
     * Encode the current [broadcastInput] and transmit.
     *
     * S5: BLUE + [blueEncryptEnabled] → AES-256-GCM wraps the payload before HMAC.
     * S6: DIODE mode → [AirGapBridge.encode] chunks + encrypts independently per chunk.
     */
    fun broadcast() {
        val text = _state.value.broadcastInput.trim()
        if (text.isEmpty()) return
        val mode = _state.value.selectedMode
        _state.update { it.copy(isBroadcasting = true, broadcastInput = "") }
        viewModelScope.launch {
            val protocol = TxProtocol.fromId(mode.protocol)
            when (mode) {
                OperationalMode.DIODE -> broadcastDiode(text, protocol, mode)
                else                  -> broadcastStandard(text, protocol, mode)
            }
            _state.update { it.copy(isBroadcasting = false) }
        }
    }

    private suspend fun broadcastStandard(text: String, protocol: TxProtocol, mode: OperationalMode) {
        val wirePayload = when {
            mode == OperationalMode.BLUE && _state.value.blueEncryptEnabled ->
                payloadCipher.encryptIfNeeded(text)
            else -> text
        }
        val signed = if (mode.requiresAuth) acousticAuth.signPayload(wirePayload) ?: wirePayload
                     else wirePayload
        repeat(mode.redundancy) { iteration ->
            if (iteration > 0) kotlinx.coroutines.delay(300)
            audioEngine.play(signed, protocol, mode.volume)
        }
        appendTxLog(text, mode)
    }

    private suspend fun broadcastDiode(text: String, protocol: TxProtocol, mode: OperationalMode) {
        val chunks = try {
            AirGapBridge.encode(text, payloadCipher::encrypt)
        } catch (e: IllegalStateException) {
            android.util.Log.e("Pentacorder/ModeVM", "DIODE encode failed: ${e.message}")
            _state.update { it.copy(isBroadcasting = false) }
            return
        }
        for ((index, chunk) in chunks.withIndex()) {
            val signed = acousticAuth.signPayload(chunk) ?: chunk
            repeat(mode.redundancy) { iter ->
                if (iter > 0) kotlinx.coroutines.delay(200)
                audioEngine.play(signed, protocol, mode.volume)
            }
            if (index < chunks.size - 1) kotlinx.coroutines.delay(300)
        }
        val displayText = "${text.take(40)}${if (text.length > 40) "…" else ""}" +
                          " [${chunks.size} chunk${if (chunks.size > 1) "s" else ""}]"
        appendTxLog(displayText, mode)
        _state.update { it.copy(diodeTxChunkCount = chunks.size) }
    }

    // ── Receive ───────────────────────────────────────────────────────────────

    /**
     * Called by AudioLoopService binder when a new acoustic payload arrives.
     * S5: `ENC:…` payloads are auto-decrypted.
     * S6: `DIODE:…` chunks feed the [AirGapBridge.Assembler].
     */
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
        val entry = DecodeLogEntry(payload, source, hmacOk, System.currentTimeMillis())
        _state.update { s -> s.copy(decodeLog = (listOf(entry) + s.decodeLog).take(MAX_LOG_ENTRIES)) }
    }

    private fun appendTxLog(displayText: String, mode: OperationalMode) {
        val entry = DecodeLogEntry(displayText, "TX:${mode.name}", true, System.currentTimeMillis())
        _state.update { s -> s.copy(decodeLog = (listOf(entry) + s.decodeLog).take(MAX_LOG_ENTRIES)) }
        viewModelScope.launch {
            auditDao.insert(AuditLogEntity.fromToken(CommonToken(
                source  = SourceProtocol.ACOUSTIC,
                intent  = if (mode == OperationalMode.RED) IntentTag.ALERT else IntentTag.TELEMETRY,
                payload = displayText,
            )))
        }
    }

    // ── Translator ────────────────────────────────────────────────────────────

    fun toggleTranslator() = _state.update { it.copy(translatorEnabled = !it.translatorEnabled) }

    // ── Settings (S5) ─────────────────────────────────────────────────────────

    fun toggleBlueEncrypt() = _state.update { it.copy(blueEncryptEnabled = !it.blueEncryptEnabled) }

    // ── Calibrate tab — inline noise floor + loopback (S5) ───────────────────

    fun measureNoiseFloor() {
        calibrateJob?.cancel()
        calibrateJob = viewModelScope.launch {
            _state.update { it.copy(calibrateStatus = CalibrateStatus.MEASURING,
                                    calibrateMessage = "Measuring noise floor…") }
            val result = noiseFloorCalibrator.measure()
            _state.update { it.copy(
                calibrateStatus    = CalibrateStatus.IDLE,
                calibrateMessage   = "Noise floor: %.0f dBFS — %s recommended".format(
                    result.noiseFloorDb, result.recommendedBand.label),
                calibratedProtocol = result.recommendedProtocol,
                calibratedVolume   = result.recommendedVolume,
                calibratedBand     = result.recommendedBand,
                noiseFloorDb       = result.noiseFloorDb,
            )}
        }
    }

    fun selectCalibrateProtocol(protocol: TxProtocol) =
        _state.update { it.copy(calibratedProtocol = protocol) }

    fun selectCalibrateVolume(volume: Int) =
        _state.update { it.copy(calibratedVolume = volume.coerceIn(1, 100)) }

    fun runLoopback() {
        loopbackJob?.cancel()
        loopbackJob = viewModelScope.launch {
            _state.update { it.copy(calibrateStatus = CalibrateStatus.TESTING,
                                    calibrateMessage = "Playing test tone…") }
            audioEngine.play(LOOPBACK_PAYLOAD, _state.value.calibratedProtocol, _state.value.calibratedVolume)
            _state.update { it.copy(calibrateMessage = "Listening for loopback…") }
            val decoded = withTimeoutOrNull(LOOPBACK_TIMEOUT_MS) {
                audioEngine.decodedPayloads.first { it.contains(LOOPBACK_MARKER) }
            }
            _state.update {
                if (decoded != null)
                    it.copy(calibrateStatus = CalibrateStatus.PASSED,
                            calibrateMessage = "✓ Loopback received. Audio channel working.")
                else
                    it.copy(calibrateStatus = CalibrateStatus.FAILED,
                            calibrateMessage = "⚠ No loopback within ${LOOPBACK_TIMEOUT_MS / 1000}s.\n" +
                                "Try higher volume or a quieter environment.")
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

    override fun onCleared() {
        calibrateJob?.cancel()
        loopbackJob?.cancel()
        diodeAssembler.reset()
        super.onCleared()
    }

    private companion object {
        const val MAX_LOG_ENTRIES     = 100
        const val LOOPBACK_MARKER     = "GIBBER_CAL"
        const val LOOPBACK_PAYLOAD    = "GIBBER_CAL_TEST_001"
        const val LOOPBACK_TIMEOUT_MS = 12_000L
    }
}

// ─────────────────────────────────────────────────────────────────────────────

enum class CalibrateStatus { IDLE, MEASURING, TESTING, PASSED, FAILED }

data class ModeUiState(
    val activeTab:           Int              = ModeUiState.TAB_TRANSMIT,
    // Transmit
    val selectedMode:        OperationalMode  = OperationalMode.GREEN,
    val broadcastInput:      String           = "",
    val isBroadcasting:      Boolean          = false,
    // Receive
    val decodeLog:           List<DecodeLogEntry> = emptyList(),
    val translatorEnabled:   Boolean          = false,
    // Calibrate (S5 inline)
    val calibrateStatus:     CalibrateStatus  = CalibrateStatus.IDLE,
    val calibrateMessage:    String           = "",
    val calibratedProtocol:  TxProtocol       = TxProtocol.fromId(CalibrationStore.DEFAULT_PROTOCOL_ID),
    val calibratedVolume:    Int              = CalibrationStore.DEFAULT_VOLUME,
    val calibratedBand:      FrequencyBand    = CalibrationStore.DEFAULT_FREQ_BAND,
    val noiseFloorDb:        Float            = CalibrationStore.DEFAULT_NOISE_FLOOR_DB,
    // Settings (S5)
    val blueEncryptEnabled:  Boolean          = false,
    val keyProvisioned:      Boolean          = false,
    // DIODE (S6)
    val diodeTxChunkCount:   Int              = 0,
) {
    companion object {
        const val TAB_TRANSMIT  = 0
        const val TAB_RECEIVE   = 1
        const val TAB_CALIBRATE = 2
        const val TAB_SETTINGS  = 3
    }
}

data class DecodeLogEntry(
    val payload:   String,
    val source:    String,
    val hmacOk:    Boolean,
    val timestamp: Long,
)
