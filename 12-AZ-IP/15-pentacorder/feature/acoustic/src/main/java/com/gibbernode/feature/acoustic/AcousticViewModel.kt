package com.gibbernode.feature.acoustic

import android.content.Context
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gibbernode.acoustic.AcousticAdvisor
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import javax.inject.Inject
import kotlin.math.PI
import kotlin.math.cos
import kotlin.math.log10
import kotlin.math.sqrt

/**
 * AcousticViewModel
 *
 * Manages continuous microphone capture, real-time FFT, and alert detection
 * via [AcousticAdvisor].
 *
 * FFT implementation: Cooley-Tukey radix-2 DIT FFT on the short-time
 * audio frames, windowed with a Hann window to reduce spectral leakage.
 * Frame size: 2048 samples at 44 100 Hz → ~46 ms resolution.
 */
@HiltViewModel
class AcousticViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
) : ViewModel() {

    private val _state = MutableStateFlow(AcousticUiState())
    val state: StateFlow<AcousticUiState> = _state.asStateFlow()

    private var audioRecord:  AudioRecord? = null
    private var captureJob:   Job? = null

    private val sampleRate = 44_100
    private val frameSize  = 2048   // power-of-2 for FFT

    private val diagnosticSpectra = mutableListOf<FloatArray>()

    // Oscilloscope: rolling raw PCM buffer (2 s worth at 44100)
    private val oscBuffer = ArrayDeque<Float>(sampleRate * 2)

    // ── Controls ──────────────────────────────────────────────────────────────

    fun startMonitoring() {
        if (_state.value.monitoring) return
        _state.update { it.copy(monitoring = true, alerts = emptyList()) }
        captureJob = viewModelScope.launch {
            captureLoop()
        }
    }

    fun stopMonitoring() {
        captureJob?.cancel()
        captureJob = null
        audioRecord?.stop()
        audioRecord?.release()
        audioRecord = null
        _state.update { it.copy(monitoring = false) }
    }

    fun setSensitivity(sensitivity: AcousticAdvisor.AlertSensitivity) =
        _state.update { it.copy(sensitivity = sensitivity) }

    fun dismissAlerts() = _state.update { it.copy(alerts = emptyList(), primaryAlert = AcousticAdvisor.AlertType.NONE) }

    // ── dB Meter controls ─────────────────────────────────────────────────────

    fun setDbCalibOffset(offset: Float) = _state.update { it.copy(dbCalibOffset = offset) }
    fun resetDbPeakMin()  = _state.update { it.copy(dbPeak = -120f, dbMin = 200f) }
    fun toggleAWeighting() = _state.update { it.copy(dbAWeighted = !it.dbAWeighted) }
    fun exportDbCsv(): String {
        val sb = StringBuilder("epoch_ms,db_spl\n")
        _state.value.dbHistory.forEach { (t, v) -> sb.append("$t,${"%.2f".format(v)}\n") }
        return sb.toString()
    }

    // ── Oscilloscope controls ─────────────────────────────────────────────────

    fun setOscTriggerLevel(level: Float) = _state.update { it.copy(oscTriggerLevel = level) }
    fun setOscTimeWindow(ms: Int)        = _state.update { it.copy(oscTimeWindowMs = ms) }
    fun freezeOscilloscope()             = _state.update { it.copy(oscFrozen = !it.oscFrozen) }

    fun startDiagnostic(mode: DiagnosticMode) {
        diagnosticSpectra.clear()
        _state.update { it.copy(diagnosticMode = mode, diagnosticResult = null) }
    }

    fun finishDiagnostic() {
        val result = when (_state.value.diagnosticMode) {
            DiagnosticMode.ENGINE   -> AcousticAdvisor.engineDiagnostic(diagnosticSpectra.toList(), sampleRate.toFloat())
            DiagnosticMode.PIPE     -> AcousticAdvisor.engineDiagnostic(diagnosticSpectra.toList(), sampleRate.toFloat())
                .copy(alertType = AcousticAdvisor.AlertType.PIPE_LEAK)
            null -> null
        }
        _state.update { it.copy(diagnosticResult = result, diagnosticMode = null) }
    }

    // ── Audio capture loop ────────────────────────────────────────────────────

    private suspend fun captureLoop() {
        val minBuf = AudioRecord.getMinBufferSize(
            sampleRate, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT,
        )
        try {
            val record = AudioRecord(
                MediaRecorder.AudioSource.MIC, sampleRate,
                AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT,
                minBuf.coerceAtLeast(frameSize * 2),
            )
            audioRecord = record
            record.startRecording()

            val pcm     = ShortArray(frameSize)
            val hann    = FloatArray(frameSize) { i -> (0.5f * (1f - cos(2f * PI.toFloat() * i / (frameSize - 1)))) }

            while (coroutineContext.isActive) {
                val read = record.read(pcm, 0, frameSize)
                if (read <= 0) continue

                val windowed = FloatArray(frameSize) { i -> pcm[i] / 32768f * hann[i] }
                val spectrum = fftMagnitude(windowed)

                val event = AcousticAdvisor.analyseFrame(spectrum, sampleRate.toFloat(), _state.value.sensitivity)

                // Accumulate spectra for diagnostic mode
                if (_state.value.diagnosticMode != null) diagnosticSpectra.add(spectrum)

                // Waterfall: keep last 60 frames
                val wf = (_state.value.waterfallFrames + spectrum).takeLast(60)

                val activeAlerts = if (event.alerts.isNotEmpty()) {
                    (_state.value.alerts + event.alerts.map { it.label }).distinct().takeLast(5)
                } else _state.value.alerts

                // ── dB SPL ──────────────────────────────────────────────────
                var sumSq = 0.0
                for (i in 0 until read) {
                    val s = pcm[i].toFloat() / 32768f
                    sumSq += s * s
                }
                val rms      = sqrt(sumSq / read).toFloat()
                // Reference: 0 dBFS full-scale → map to ~94 dB SPL (smartphone mic nominal)
                val dbRaw    = if (rms > 1e-8f) 20f * log10(rms) + 94f else -120f
                val s = _state.value
                val dbFinal  = dbRaw + s.dbCalibOffset + (if (s.dbAWeighted) aWeightingApprox(event.spectrumPeakHz) else 0f)
                val now = System.currentTimeMillis()
                val newDbHist = (s.dbHistory + (now to dbFinal)).takeLast(600)

                // ── Oscilloscope raw waveform ────────────────────────────────
                // Append raw samples to rolling buffer; extract window for display
                for (i in 0 until read) {
                    if (oscBuffer.size >= sampleRate * 2) oscBuffer.removeFirst()
                    oscBuffer.addLast(pcm[i].toFloat() / 32768f)
                }
                val waveform = if (!s.oscFrozen) {
                    val winSamples = (sampleRate * s.oscTimeWindowMs / 1000).coerceAtLeast(64)
                    val buf = oscBuffer.toFloatArray()
                    if (buf.size >= winSamples) {
                        // Simple trigger: find first sample crossing triggerLevel upward
                        val trig = s.oscTriggerLevel
                        var startIdx = buf.size - winSamples
                        if (trig != 0f) {
                            for (i in (buf.size - winSamples).coerceAtLeast(1) until buf.size - 1) {
                                if (buf[i - 1] < trig && buf[i] >= trig) { startIdx = i; break }
                            }
                        }
                        buf.copyOfRange(startIdx.coerceAtLeast(0), (startIdx + winSamples).coerceAtMost(buf.size))
                    } else buf
                } else s.oscWaveform

                _state.update { st ->
                    st.copy(
                        lastSpectrum    = spectrum,
                        waterfallFrames = wf,
                        overallLevel    = event.overallLevel,
                        spectrumPeakHz  = event.spectrumPeakHz,
                        primaryAlert    = event.primaryAlert,
                        alerts          = activeAlerts,
                        // dB meter
                        dbSpl           = dbFinal,
                        dbPeak          = maxOf(st.dbPeak, dbFinal),
                        dbMin           = if (st.dbMin > 200f) dbFinal else minOf(st.dbMin, dbFinal),
                        dbHistory       = newDbHist,
                        // oscilloscope
                        oscWaveform     = waveform,
                    )
                }
            }
        } catch (_: SecurityException) {
            // Permission not granted — show stub
            _state.update { it.copy(monitoring = false) }
        } finally {
            audioRecord?.stop()
            audioRecord?.release()
            audioRecord = null
        }
    }

    // ── Radix-2 DIT FFT (magnitude spectrum, one-sided) ───────────────────────

    private fun fftMagnitude(samples: FloatArray): FloatArray {
        val n  = samples.size
        val re = samples.copyOf()
        val im = FloatArray(n)

        // Bit-reversal permutation
        var j = 0
        for (i in 1 until n) {
            var bit = n shr 1
            while (j and bit != 0) { j = j xor bit; bit = bit shr 1 }
            j = j xor bit
            if (i < j) { re[i] = re[j].also { re[j] = re[i] }; im[i] = im[j].also { im[j] = im[i] } }
        }

        // FFT butterfly
        var len = 2
        while (len <= n) {
            val wRe = cos(2f * PI.toFloat() / len)
            val wIm = -sin(2f * PI.toFloat() / len)
            var i = 0
            while (i < n) {
                var curRe = 1f; var curIm = 0f
                for (k in 0 until len / 2) {
                    val uRe = re[i + k]; val uIm = im[i + k]
                    val vRe = re[i + k + len / 2] * curRe - im[i + k + len / 2] * curIm
                    val vIm = re[i + k + len / 2] * curIm + im[i + k + len / 2] * curRe
                    re[i + k]          = uRe + vRe; im[i + k]          = uIm + vIm
                    re[i + k + len / 2] = uRe - vRe; im[i + k + len / 2] = uIm - vIm
                    val tmpRe = curRe * wRe - curIm * wIm
                    curIm = curRe * wIm + curIm * wRe; curRe = tmpRe
                }
                i += len
            }
            len = len shl 1
        }

        // One-sided magnitude spectrum
        return FloatArray(n / 2) { i -> sqrt(re[i] * re[i] + im[i] * im[i]) / n }
    }

    private fun sin(v: Float) = kotlin.math.sin(v.toDouble()).toFloat()

    /**
     * Simplified broadband A-weighting correction (dB) based on the dominant
     * frequency of the current frame. Approximates the IEC 61672-1 curve.
     */
    private fun aWeightingApprox(hz: Float): Float = when {
        hz <= 0f      -> -70f
        hz < 100f     -> -19f
        hz < 500f     -> -3f
        hz < 1000f    ->  0f
        hz < 2000f    ->  1f
        hz < 4000f    ->  1f
        hz < 8000f    -> -1f
        else          -> -3f
    }

    override fun onCleared() {
        stopMonitoring()
        super.onCleared()
    }
}

// ─────────────────────────────────────────────────────────────────────────────

enum class DiagnosticMode { ENGINE, PIPE }

data class AcousticUiState(
    val monitoring:      Boolean = false,
    val sensitivity:     AcousticAdvisor.AlertSensitivity = AcousticAdvisor.AlertSensitivity.MEDIUM,
    val lastSpectrum:    FloatArray = FloatArray(0),
    val waterfallFrames: List<FloatArray> = emptyList(),
    val overallLevel:    Float = 0f,
    val spectrumPeakHz:  Float = 0f,
    val primaryAlert:    AcousticAdvisor.AlertType = AcousticAdvisor.AlertType.NONE,
    val alerts:          List<String> = emptyList(),
    val diagnosticMode:  DiagnosticMode? = null,
    val diagnosticResult: AcousticAdvisor.DiagnosticResult? = null,
    // dB SPL meter
    val dbSpl:          Float = -120f,
    val dbPeak:         Float = -120f,
    val dbMin:          Float = 200f,
    val dbCalibOffset:  Float = 0f,
    val dbAWeighted:    Boolean = false,
    val dbHistory:      List<Pair<Long, Float>> = emptyList(),
    // Oscilloscope
    val oscWaveform:    FloatArray = FloatArray(0),
    val oscTriggerLevel: Float = 0f,
    val oscTimeWindowMs: Int = 50,
    val oscFrozen:       Boolean = false,
)
