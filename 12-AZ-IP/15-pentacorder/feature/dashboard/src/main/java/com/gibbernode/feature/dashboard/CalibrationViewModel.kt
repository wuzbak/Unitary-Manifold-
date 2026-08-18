package com.gibbernode.feature.dashboard

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gibbernode.audio.AudioEngine
import com.gibbernode.audio.FrequencyBand
import com.gibbernode.audio.NoiseFloorCalibrator
import com.gibbernode.audio.TxProtocol
import com.gibbernode.gibberwave.CalibrationStore
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

private const val TAG = "Pentacorder/CalibrationVM"

@HiltViewModel
class CalibrationViewModel @Inject constructor(
    private val audioEngine:         AudioEngine,
    private val calibrationStore:    CalibrationStore,
    private val noiseFloorCalibrator: NoiseFloorCalibrator,
) : ViewModel() {

    private val _state = MutableStateFlow(CalibrationUiState())
    val state: StateFlow<CalibrationUiState> = _state.asStateFlow()

    private var testJob: Job? = null

    // ── Wizard navigation ─────────────────────────────────────────────────────

    fun nextStep() = _state.update { it.copy(currentStep = (it.currentStep + 1).coerceAtMost(STEP_DONE)) }
    fun prevStep() = _state.update { it.copy(currentStep = (it.currentStep - 1).coerceAtLeast(STEP_WELCOME)) }

    // ── Audio loopback test ───────────────────────────────────────────────────

    /**
     * Encode a short test payload through the speaker, then listen on the mic
     * for the loopback decode.  If the decode comes back within [LOOPBACK_TIMEOUT_MS],
     * the test passes and [CalibrationUiState.testStatus] becomes [TestStatus.PASSED].
     *
     * Notes:
     *  - The AudioLoopService / AudioEngine must already be running (startListening).
     *  - Hardware AEC (Acoustic Echo Cancellation) is OFF for AudioSource.MIC on
     *    Android when not in a call, so the loopback should be audible to the decoder.
     *  - S24 Ultra: Dolby Atmos EQ is active. If the test fails, manually selecting
     *    AUDIBLE_NORMAL (most robust) is the safe fallback.
     */
    fun startAudioTest() {
        testJob?.cancel()
        testJob = viewModelScope.launch {
            _state.update { it.copy(testStatus = TestStatus.TESTING, testMessage = "Playing test tone through speaker…") }

            val protocol = _state.value.selectedProtocol
            val volume   = _state.value.selectedVolume

            // Encode and play the calibration test payload
            audioEngine.play(TEST_PAYLOAD, protocol, volume)

            _state.update { it.copy(testMessage = "Listening for loopback on mic…") }

            val decoded = withTimeoutOrNull(LOOPBACK_TIMEOUT_MS) {
                audioEngine.decodedPayloads.first { raw -> raw.contains(TEST_MARKER) }
            }

            if (decoded != null) {
                // Loopback succeeded — recommend the tested protocol
                _state.update {
                    it.copy(
                        testStatus        = TestStatus.PASSED,
                        testMessage       = "✓ Loopback received. Audio channel is working.",
                        recommendedProtocol = protocol,
                        safeCeilingHz     = protocol.safeCeilingHz,
                    )
                }
            } else {
                // Loopback timed out — suggest falling back to AUDIBLE_NORMAL
                _state.update {
                    it.copy(
                        testStatus        = TestStatus.FAILED,
                        testMessage       = "⚠ No loopback within ${LOOPBACK_TIMEOUT_MS / 1000}s.\n" +
                                           "Try a higher volume or quieter environment.\n" +
                                           "AUDIBLE_NORMAL is set as safe default.",
                        recommendedProtocol = TxProtocol.AUDIBLE_NORMAL,
                        selectedProtocol    = TxProtocol.AUDIBLE_NORMAL,
                        safeCeilingHz       = TxProtocol.AUDIBLE_NORMAL.safeCeilingHz,
                    )
                }
            }
        }
    }

    fun cancelTest() {
        testJob?.cancel()
        _state.update { it.copy(testStatus = TestStatus.IDLE, testMessage = "") }
    }

    // ── Noise floor calibration ───────────────────────────────────────────────

    /**
     * Run a ~1-second ambient noise floor capture and pre-fill the recommended
     * protocol, volume, and frequency band before the loopback test.
     *
     * Requires RECORD_AUDIO permission — callers must have it granted.
     */
    fun measureNoiseFloor() {
        viewModelScope.launch {
            _state.update { it.copy(testStatus = TestStatus.TESTING, testMessage = "Measuring noise floor…") }
            val result = noiseFloorCalibrator.measure()
            _state.update {
                it.copy(
                    testStatus          = TestStatus.IDLE,
                    testMessage         = "Noise floor: %.0f dBFS — %s recommended".format(
                        result.noiseFloorDb,
                        result.recommendedBand.label,
                    ),
                    selectedProtocol    = result.recommendedProtocol,
                    selectedVolume      = result.recommendedVolume,
                    recommendedBand     = result.recommendedBand,
                    noiseFloorDb        = result.noiseFloorDb,
                    recommendedProtocol = result.recommendedProtocol,
                    safeCeilingHz       = result.safeCeilingHz,
                )
            }
        }
    }

    // ── Protocol / volume selection ───────────────────────────────────────────

    fun selectProtocol(protocol: TxProtocol) = _state.update { it.copy(selectedProtocol = protocol) }
    fun selectVolume(newVolume: Int) = _state.update { it.copy(selectedVolume = newVolume.coerceIn(1, 100)) }

    // ── Save / skip ───────────────────────────────────────────────────────────

    fun saveAndComplete() {
        viewModelScope.launch {
            val s = _state.value
            calibrationStore.saveCalibration(
                protocolId    = s.selectedProtocol.id,
                volume        = s.selectedVolume,
                freqBand      = s.recommendedBand,
                noiseFloorDb  = s.noiseFloorDb,
                safeCeilingHz = s.safeCeilingHz,
            )
            _state.update { it.copy(isDone = true) }
        }
    }

    fun skip() {
        viewModelScope.launch {
            calibrationStore.markCalibrated()
            _state.update { it.copy(isDone = true) }
        }
    }

    override fun onCleared() {
        testJob?.cancel()
        super.onCleared()
    }

    companion object {
        private const val TEST_MARKER        = "GIBBER_CAL"
        private const val TEST_PAYLOAD       = "GIBBER_CAL_TEST_001"
        private const val LOOPBACK_TIMEOUT_MS = 12_000L

        const val STEP_WELCOME  = 0
        const val STEP_TEST     = 1
        const val STEP_PROTOCOL = 2
        const val STEP_DONE     = 3
    }
}

// ── State ─────────────────────────────────────────────────────────────────────

enum class TestStatus { IDLE, TESTING, PASSED, FAILED }

data class CalibrationUiState(
    val currentStep:         Int          = CalibrationViewModel.STEP_WELCOME,
    val testStatus:          TestStatus   = TestStatus.IDLE,
    val testMessage:         String       = "",
    val selectedProtocol:    TxProtocol   = TxProtocol.fromId(CalibrationStore.DEFAULT_PROTOCOL_ID),
    val selectedVolume:      Int          = CalibrationStore.DEFAULT_VOLUME,
    val recommendedProtocol: TxProtocol?  = null,
    val recommendedBand:     FrequencyBand = CalibrationStore.DEFAULT_FREQ_BAND,
    val noiseFloorDb:        Float        = CalibrationStore.DEFAULT_NOISE_FLOOR_DB,
    val safeCeilingHz:       Int          = CalibrationStore.DEFAULT_SAFE_CEILING_HZ,
    val isDone:              Boolean      = false,
)
