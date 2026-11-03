package com.sdam.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.sdam.audio.AudioEngine
import com.sdam.audio.CalibrationStore
import com.sdam.audio.FrequencyBand
import com.sdam.audio.NoiseFloorCalibrator
import com.sdam.audio.TxProtocol
import com.sdam.security.AuthenticatedFrameCodec
import com.sdam.security.AirGapBridge
import com.sdam.security.PayloadCipher
import com.sdam.security.SdamKeyManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Job
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.withTimeoutOrNull
import java.util.concurrent.atomic.AtomicLong
import javax.inject.Inject

/**
 * TransmitMode
 *
 * SDAM-specific operational modes for the Transmit tab.
 *
 * STANDARD — AES-GCM encrypted, authenticated fragmented transmission.
 * SECURE   — AES-256-GCM encrypted, authenticated fragmented transmission.
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
        displayName = "Standard (encrypted)",
        protocol    = TxProtocol.AUDIBLE_FAST,
        volume      = 50,
        encrypted   = true,
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
    val status:    String = "",
)

data class MainUiState(
    val activeTab:          Int             = TAB_TRANSMIT,
    // Transmit
    val selectedMode:       TransmitMode    = TransmitMode.DEFAULT,
    val broadcastInput:     String          = "",
    val isBroadcasting:     Boolean         = false,
    val diodeTxChunkCount:  Int             = 0,
    val workflowStatus:     String          = "",
    val workflowError:      Boolean         = false,
    val nativeAudioAvailable: Boolean       = false,
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
    private val payloadCipher:        PayloadCipher,
    private val keyManager:           SdamKeyManager,
    private val calibrationStore:     CalibrationStore,
    private val noiseFloorCalibrator: NoiseFloorCalibrator,
) : ViewModel() {

    private val _state = MutableStateFlow(MainUiState())
    val state: StateFlow<MainUiState> = _state.asStateFlow()

    // Per-session assemblers; generic MSG carries a per-transmission ID.
    private val diodeAssembler = AirGapBridge.MessageAssembler("DIODE")
    private val messageAssembler = AirGapBridge.MessageAssembler()
    private val frameVerifier = AuthenticatedFrameCodec.Verifier(keyManager::verifyFrame)
    private val frameCounter = AtomicLong(System.currentTimeMillis())

    private var calibrateJob: Job? = null
    private var loopbackJob:  Job? = null

    init {
        val codecAvailable = audioEngine.isCodecAvailable
        _state.update {
            it.copy(
                keyProvisioned = payloadCipher.canEncrypt(),
                nativeAudioAvailable = codecAvailable,
                workflowStatus = if (codecAvailable) {
                    if (audioEngine.isListening) "Secure audio modem ready; listening for frames."
                    else "Native ggwave is ready; microphone is not active."
                } else {
                    "Native ggwave is unavailable; audio transmit and receive are disabled."
                },
                workflowError = !codecAvailable || !audioEngine.isListening,
            )
        }
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
            audioEngine.decodedPayloads.collect { raw -> onDecoded(raw, hmacOk = false) }
        }
    }

    // ── Tab navigation ────────────────────────────────────────────────────────

    fun selectTab(tab: Int) = _state.update { it.copy(activeTab = tab) }

    // ── Transmit ──────────────────────────────────────────────────────────────

    fun selectMode(mode: TransmitMode) = _state.update { it.copy(selectedMode = mode) }

    fun onMessageInput(text: String) = _state.update { it.copy(broadcastInput = text) }

    fun broadcast() {
        val text = _state.value.broadcastInput
        if (text.isBlank()) return
        val mode = _state.value.selectedMode
        if (!audioEngine.isCodecAvailable) {
            setWorkflowStatus("Transmit unavailable: native ggwave codec is not loaded.", true)
            return
        }
        _state.update { it.copy(isBroadcasting = true, broadcastInput = "") }
        viewModelScope.launch {
            try {
                if (!_state.value.debugMode && !payloadCipher.canEncrypt()) {
                    error("Encryption key is unavailable; no audio was transmitted.")
                }
                when (mode) {
                    TransmitMode.DIODE -> broadcastDiode(text, mode)
                    else               -> broadcastStandard(text, mode)
                }
            } catch (e: Exception) {
                setWorkflowStatus(
                    e.message ?: "Transmit failed; no success was reported.",
                    true,
                )
            } finally {
                _state.update { it.copy(isBroadcasting = false) }
            }
        }
    }

    private suspend fun broadcastStandard(text: String, mode: TransmitMode) {
        val debugMode = _state.value.debugMode
        val fragments = if (debugMode) {
            AirGapBridge.encodeMessage(text) { chunk -> "DBG:$chunk" }
        } else {
            AirGapBridge.encodeMessage(text, payloadCipher::encrypt)
        }
        for ((index, fragment) in fragments.withIndex()) {
            repeat(mode.redundancy) { iteration ->
                if (iteration > 0) kotlinx.coroutines.delay(300)
                transmitFrame(fragment, mode)
            }
            if (index < fragments.lastIndex) kotlinx.coroutines.delay(100)
        }
        val contentStatus = if (debugMode) "Explicit debug plaintext" else "AES-GCM encrypted"
        appendTxLog(
            text,
            mode,
            "$contentStatus; ${fragments.size} authenticated fragment(s) queued.",
        )
        setWorkflowStatus(
            "$contentStatus message queued as ${fragments.size} authenticated fragment(s); delivery/reassembly pending.",
            false,
        )
    }

    private suspend fun broadcastDiode(text: String, mode: TransmitMode) {
        val chunks = AirGapBridge.encode(text, payloadCipher::encrypt)
        for ((index, chunk) in chunks.withIndex()) {
            repeat(mode.redundancy) { iter ->
                if (iter > 0) kotlinx.coroutines.delay(200)
                transmitFrame(chunk, mode)
            }
            if (index < chunks.size - 1) kotlinx.coroutines.delay(300)
        }
        val displayText = "${text.take(40)}${if (text.length > 40) "…" else ""}" +
                          " [${chunks.size} chunk${if (chunks.size > 1) "s" else ""}]"
        appendTxLog(displayText, mode, "Encrypted chunks queued; authenticated receive pending.")
        _state.update { it.copy(diodeTxChunkCount = chunks.size) }
        setWorkflowStatus("Encrypted DIODE audio queued; waiting for authenticated frames.", false)
    }

    private suspend fun transmitFrame(payload: String, mode: TransmitMode) {
        val frame = AuthenticatedFrameCodec.encode(
            payload = payload,
            counter = frameCounter.incrementAndGet(),
            sign = keyManager::signFrame,
        )
        if (!audioEngine.play(frame, mode.protocol, mode.volume)) {
            error("Native ggwave/audio playback failed; frame was not reported as transmitted.")
        }
    }

    // ── Receive ───────────────────────────────────────────────────────────────

    fun onDecoded(raw: String, @Suppress("UNUSED_PARAMETER") hmacOk: Boolean = false) {
        when (val verified = frameVerifier.verify(raw)) {
            is AuthenticatedFrameCodec.Result.Invalid -> {
                appendRxLog(
                    "Rejected frame: ${verified.reason}",
                    "RX:ERROR",
                    false,
                    verified.reason,
                )
                setWorkflowStatus("Receive error: ${verified.reason}.", true)
            }
            is AuthenticatedFrameCodec.Result.Valid -> {
                val payload = verified.frame.payload
                when {
                    AirGapBridge.isMessageFragment(payload) ->
                        receiveFragment(payload, messageAssembler, "RX:SECURE")
                    AirGapBridge.isDiode(payload) ->
                        receiveFragment(payload, diodeAssembler, "RX:DIODE")
                    payloadCipher.isEncrypted(payload) -> receiveSingleEncrypted(payload)
                    payload.startsWith("DBG:") && _state.value.debugMode -> {
                        appendRxLog(payload.removePrefix("DBG:"), "RX:DEBUG", true, "Authenticated debug plaintext.")
                        setWorkflowStatus("Success: authenticated debug frame received (plaintext).", false)
                    }
                    else -> {
                        appendRxLog("Rejected unencrypted payload.", "RX:ERROR", false, "Encryption is required.")
                        setWorkflowStatus("Receive error: encrypted payload required.", true)
                    }
                }
            }
        }
    }

    private fun receiveFragment(
        raw: String,
        assembler: AirGapBridge.MessageAssembler,
        source: String,
    ) {
        val result = assembler.feed(raw) { encryptedChunk ->
            when {
                payloadCipher.isEncrypted(encryptedChunk) ->
                    payloadCipher.decrypt(encryptedChunk)
                encryptedChunk.startsWith("DBG:") && _state.value.debugMode ->
                    encryptedChunk.removePrefix("DBG:")
                else -> null
            }
        }
        when (result) {
            is AirGapBridge.FragmentResult.Incomplete -> {
                setWorkflowStatus(
                    "Authenticated fragment ${result.received}/${result.total} received; waiting for completion.",
                    false,
                )
            }
            is AirGapBridge.FragmentResult.Invalid -> {
                appendRxLog("Rejected fragment.", "RX:ERROR", false, result.reason)
                setWorkflowStatus("Receive error: ${result.reason}.", true)
            }
            is AirGapBridge.FragmentResult.Complete -> {
                val displaySource = if (source == "RX:DIODE") source else if (result.debug) "RX:DEBUG" else source
                appendRxLog(
                    result.message,
                    displaySource,
                    true,
                    if (result.debug) "Authenticated explicit debug fragments." else "All fragments authenticated and decrypted.",
                )
                setWorkflowStatus(
                    "Success: ${result.total} authenticated fragment(s) reassembled.",
                    false,
                )
            }
        }
    }

    private fun receiveSingleEncrypted(payload: String) {
        val plaintext = payloadCipher.decrypt(payload)
        if (plaintext == null) {
            appendRxLog("Decryption failed.", "RX:ERROR", false, "AES-GCM authentication failed.")
            setWorkflowStatus("Receive error: AES-GCM authentication/decryption failed.", true)
        } else {
            appendRxLog(plaintext, "RX:SECURE", true, "Authenticated and decrypted.")
            setWorkflowStatus("Success: HMAC authenticated and AES-GCM decrypted.", false)
        }
    }

    private fun appendRxLog(payload: String, source: String, hmacOk: Boolean, status: String = "") {
        val entry = DecodeEntry(payload, source, hmacOk, System.currentTimeMillis(), status)
        _state.update { s -> s.copy(decodeLog = (listOf(entry) + s.decodeLog).take(MAX_LOG_ENTRIES)) }
    }

    private fun appendTxLog(displayText: String, mode: TransmitMode, status: String) {
        val entry = DecodeEntry(displayText, "TX:${mode.name}", true, System.currentTimeMillis(), status)
        _state.update { s -> s.copy(decodeLog = (listOf(entry) + s.decodeLog).take(MAX_LOG_ENTRIES)) }
    }

    private fun setWorkflowStatus(message: String, isError: Boolean) {
        _state.update { it.copy(workflowStatus = message, workflowError = isError) }
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
            val result = try {
                noiseFloorCalibrator.measure()
            } catch (e: CancellationException) {
                throw e
            } catch (e: SecurityException) {
                _state.update {
                    it.copy(
                        calibrateStatus = CalibrateStatus.FAILED,
                        calibrateMessage = "Microphone permission is required for measurement.",
                    )
                }
                return@launch
            } catch (e: IllegalStateException) {
                _state.update {
                    it.copy(
                        calibrateStatus = CalibrateStatus.FAILED,
                        calibrateMessage = "Ambient level measurement failed: ${e.message}",
                    )
                }
                return@launch
            } catch (e: IllegalArgumentException) {
                _state.update {
                    it.copy(
                        calibrateStatus = CalibrateStatus.FAILED,
                        calibrateMessage = "Ambient level measurement is unavailable: ${e.message}",
                    )
                }
                return@launch
            }
            _state.update {
                it.copy(
                    calibrateStatus    = CalibrateStatus.IDLE,
                    calibrateMessage   = "Ambient level estimate: %.0f dBFS. Frequency response is not measured; protocol and volume are unchanged.".format(
                        result.noiseFloorDb),
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
            val marker = "$LOOPBACK_MARKER${System.nanoTime() % 1_000_000_000}"
            if (!payloadCipher.canEncrypt()) {
                _state.update {
                    it.copy(
                        calibrateStatus = CalibrateStatus.FAILED,
                        calibrateMessage = "Loopback unavailable: AES-GCM encryption failed.",
                    )
                }
                return@launch
            }
            val frames = try {
                AirGapBridge.encodeMessage(marker, payloadCipher::encrypt).map { fragment ->
                    AuthenticatedFrameCodec.encode(
                        fragment,
                        frameCounter.incrementAndGet(),
                        keyManager::signFrame,
                    )
                }
            } catch (e: Exception) {
                _state.update {
                    it.copy(
                        calibrateStatus = CalibrateStatus.FAILED,
                        calibrateMessage = "Loopback unavailable: secure frame could not be encoded.",
                    )
                }
                return@launch
            }
            _state.update {
                it.copy(
                    calibrateStatus  = CalibrateStatus.TESTING,
                    calibrateMessage = "Playing encrypted/authenticated loopback fragment(s)…",
                )
            }
            for (frame in frames) {
                val queued = audioEngine.play(
                    frame,
                    _state.value.calibratedProtocol,
                    _state.value.calibratedVolume,
                )
                if (!queued) {
                    _state.update {
                        it.copy(
                            calibrateStatus = CalibrateStatus.FAILED,
                            calibrateMessage = "Loopback unavailable: native codec or audio playback failed.",
                        )
                    }
                    return@launch
                }
                if (frame != frames.last()) kotlinx.coroutines.delay(100)
            }
            _state.update { it.copy(calibrateMessage = "Listening for loopback…") }
            val received = withTimeoutOrNull(LOOPBACK_TIMEOUT_MS) {
                state.first { current ->
                    current.decodeLog.any {
                        it.payload == marker && it.source == "RX:SECURE" && it.hmacOk
                    }
                }
            }
            _state.update {
                if (received != null)
                    it.copy(
                        calibrateStatus  = CalibrateStatus.PASSED,
                        calibrateMessage = "✓ Authenticated/decrypted audio loopback received.",
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

    fun cancelAudioOperation() {
        calibrateJob?.cancel()
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
        messageAssembler.reset()
        super.onCleared()
    }

    private companion object {
        const val MAX_LOG_ENTRIES     = 100
        const val LOOPBACK_MARKER     = "CAL-"
        const val LOOPBACK_TIMEOUT_MS = 12_000L
    }
}
