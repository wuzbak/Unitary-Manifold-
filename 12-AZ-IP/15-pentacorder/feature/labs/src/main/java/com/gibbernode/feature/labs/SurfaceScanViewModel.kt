package com.gibbernode.feature.labs

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gibbernode.contractor.ContractorAdvisor
import com.gibbernode.gibberwave.SensorBridge
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject
import kotlin.math.abs
import kotlin.math.sqrt

/**
 * SurfaceScanViewModel
 *
 * Android port of S24Ultra/scripts/surface_scan.py.
 *
 * Two scan modes:
 *
 *  SURFACE — Acoustic tap material classification via accelerometer decay analysis.
 *    User taps the target surface firmly; the accelerometer records the vibration
 *    ringdown.  An exponential-decay fit on the post-peak envelope determines the
 *    decay constant λ and maps it to a [ContractorAdvisor.SurfaceMaterial] via
 *    [ContractorAdvisor.classifyTap].
 *
 *  LIFE_SIGN — Contact-free breathing / heartbeat detection via low-frequency FFT.
 *    Phone rests on a surface in contact with the subject (table beside them,
 *    or held lightly on chest).  A 10-second accelerometer recording is analysed:
 *      Breathing:  0.15–0.5 Hz band power → respiration rate estimate
 *      Heartbeat:  0.8–2.5  Hz band power → BPM estimate
 *
 * Both modes use the Android TYPE_ACCELEROMETER sensor directly (100 Hz).
 * Results are also compared to ContractorAdvisor.classifySurface() for
 * consistent cross-platform output.
 */
@HiltViewModel
class SurfaceScanViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
    private val sensorBridge: SensorBridge,
) : ViewModel(), SensorEventListener {

    private val _state = MutableStateFlow(SurfaceScanUiState())
    val state: StateFlow<SurfaceScanUiState> = _state.asStateFlow()

    private val sensorManager = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private val accelSensor    = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)

    // Captured accelerometer magnitude samples during scan
    private val accelSamples   = mutableListOf<Float>()
    private val SURFACE_SAMPLES = 200   // ~2 s at 100 Hz
    private val LIFESIGN_SAMPLES = 1000 // ~10 s at 100 Hz

    // ─────────────────────────────────────────────────────────────────────────
    // Public API
    // ─────────────────────────────────────────────────────────────────────────

    /**
     * Start a surface tap-test.  User should tap the surface firmly once.
     * Uses [ContractorAdvisor.classifyTap] to classify the surface from the
     * post-tap accelerometer decay.
     */
    fun startSurfaceScan() {
        accelSamples.clear()
        _state.update { it.copy(
            mode         = ScanMode.SURFACE,
            scanning     = true,
            progress     = 0f,
            surfaceResult = null,
            lifeSignResult = null,
            error        = null,
        )}
        sensorManager.registerListener(this, accelSensor, SensorManager.SENSOR_DELAY_GAME)
        scheduleScanStop(SURFACE_SAMPLES, ::processSurfaceSamples)
    }

    /** Start a life-sign detection session.  Hold phone still on a surface ~10 s. */
    fun startLifeSignScan() {
        accelSamples.clear()
        _state.update { it.copy(
            mode         = ScanMode.LIFE_SIGN,
            scanning     = true,
            progress     = 0f,
            surfaceResult = null,
            lifeSignResult = null,
            error        = null,
        )}
        sensorManager.registerListener(this, accelSensor, SensorManager.SENSOR_DELAY_GAME)
        scheduleScanStop(LIFESIGN_SAMPLES, ::processLifeSignSamples)
    }

    /** Cancel any active scan. */
    fun cancelScan() {
        sensorManager.unregisterListener(this)
        accelSamples.clear()
        _state.update { it.copy(scanning = false, progress = 0f) }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // SensorEventListener
    // ─────────────────────────────────────────────────────────────────────────

    override fun onSensorChanged(event: SensorEvent?) {
        if (event?.sensor?.type != Sensor.TYPE_ACCELEROMETER) return
        val (x, y, z) = event.values
        val mag = sqrt((x * x + y * y + z * z).toDouble()).toFloat()
        accelSamples.add(mag)
        val targetCount = if (_state.value.mode == ScanMode.SURFACE) SURFACE_SAMPLES else LIFESIGN_SAMPLES
        val progress = accelSamples.size.toFloat() / targetCount
        _state.update { it.copy(progress = progress.coerceIn(0f, 1f)) }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}

    // ─────────────────────────────────────────────────────────────────────────
    // Scan scheduling
    // ─────────────────────────────────────────────────────────────────────────

    private fun scheduleScanStop(targetSamples: Int, process: () -> Unit) {
        viewModelScope.launch {
            // Poll until we have enough samples (or 15 s timeout)
            var waited = 0
            while (accelSamples.size < targetSamples && waited < 150) {
                delay(100L)
                waited++
            }
            sensorManager.unregisterListener(this@SurfaceScanViewModel)
            if (accelSamples.size < 10) {
                _state.update { it.copy(scanning = false,
                    error = "Insufficient sensor data (${accelSamples.size} samples). " +
                            "Ensure accelerometer permission is granted.") }
            } else {
                process()
            }
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Surface scan — exponential decay analysis + ContractorAdvisor
    // ─────────────────────────────────────────────────────────────────────────

    private fun processSurfaceSamples() {
        val samples = accelSamples.toList()
        try {
            // Use ContractorAdvisor for consistent cross-platform results
            val advisorResult = ContractorAdvisor.classifyTap(samples, sampleRateHz = 100f)

            // Manifold φ-surface interpretation
            val phiSurface = phiFromHardness(advisorResult.material.hardness)

            // Build advice string from material properties
            val advice = buildString {
                append("${advisorResult.material.emoji} ${advisorResult.material.label}")
                append(" · hardness ${advisorResult.material.hardness.toInt()}/100")
                if (advisorResult.confidence > 0.7f) append(" · high confidence")
                else if (advisorResult.confidence > 0.4f) append(" · moderate confidence")
                else append(" · low confidence — try a firmer tap")
            }

            _state.update { it.copy(
                scanning      = false,
                progress      = 1f,
                surfaceResult = SurfaceResult(
                    material    = advisorResult.material.label,
                    emoji       = advisorResult.material.emoji,
                    decayConst  = advisorResult.decayConst,
                    peakAccelG  = advisorResult.peakAccelG,
                    confidence  = advisorResult.confidence,
                    phiSurface  = phiSurface,
                    hardness    = advisorResult.hardnessEstimate,
                    advice      = advice,
                    sampleCount = samples.size,
                ),
            )}
        } catch (e: Exception) {
            _state.update { it.copy(scanning = false, error = "Analysis failed: ${e.message}") }
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Life-sign — FFT-based breathing / heartbeat detection
    // ─────────────────────────────────────────────────────────────────────────

    private fun processLifeSignSamples() {
        val samples = accelSamples.toList()
        try {
            val sampleRateHz = 100f   // SENSOR_DELAY_GAME ≈ 100 Hz

            // DC removal: subtract mean (gravity component)
            val mean   = samples.average().toFloat()
            val acDc   = samples.map { it - mean }

            // Simple DFT on the AC component (O(n²) but n ≤ 1000 is fine)
            val n       = acDc.size
            val freqRes = sampleRateHz / n   // Hz per bin

            // Band power sums
            var breathPower  = 0.0
            var heartPower   = 0.0
            var breathFreq   = 0f   // dominant frequency in breath band
            var heartFreq    = 0f   // dominant frequency in heart band
            var breathPeak   = 0.0
            var heartPeak    = 0.0

            for (k in 1 until n / 2) {
                val freq = k * freqRes
                // DFT magnitude at bin k
                var re = 0.0; var im = 0.0
                for (t in acDc.indices) {
                    val angle = 2 * Math.PI * k * t / n
                    re += acDc[t] * Math.cos(angle)
                    im += acDc[t] * Math.sin(angle)
                }
                val mag = Math.sqrt(re * re + im * im)

                when {
                    freq in 0.15f..0.5f -> {   // Breathing band
                        breathPower += mag
                        if (mag > breathPeak) { breathPeak = mag; breathFreq = freq }
                    }
                    freq in 0.8f..2.5f -> {    // Heartbeat band
                        heartPower += mag
                        if (mag > heartPeak) { heartPeak = mag; heartFreq = freq }
                    }
                }
            }

            val breathRpm = (breathFreq * 60f).let { if (it > 0f) it else null }
            val heartBpm  = (heartFreq  * 60f).let { if (it > 0f) it else null }

            // Signal-to-noise: compare band power to broadband noise floor
            val totalPower = acDc.sumOf { v -> v.toDouble() * v.toDouble() }
            val breathSnr  = if (totalPower > 0) (breathPower / totalPower * 100).toFloat() else 0f
            val heartSnr   = if (totalPower > 0) (heartPower  / totalPower * 100).toFloat() else 0f

            val lifeSignDetected = breathSnr > 0.5f || heartSnr > 0.5f

            _state.update { it.copy(
                scanning       = false,
                progress       = 1f,
                lifeSignResult = LifeSignResult(
                    breathingRpm    = breathRpm,
                    heartBpm        = heartBpm,
                    breathSnrPct    = breathSnr,
                    heartSnrPct     = heartSnr,
                    lifeSignDetected = lifeSignDetected,
                    sampleCount     = samples.size,
                ),
            )}
        } catch (e: Exception) {
            _state.update { it.copy(scanning = false, error = "Life-sign analysis failed: ${e.message}") }
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Manifold φ mapping
    // ─────────────────────────────────────────────────────────────────────────

    /**
     * Maps surface hardness (0–100) to the φ-homeostasis surface field value.
     * Hard surfaces return energy to the manifold geodesic (φ ≈ 1.0).
     * Damped surfaces absorb energy into the internal φ-field (φ > 1.0).
     */
    private fun phiFromHardness(hardness: Float): Float {
        return 1f + (1f - hardness / 100f) * 0.5f
    }

    override fun onCleared() {
        sensorManager.unregisterListener(this)
        super.onCleared()
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// UI State
// ─────────────────────────────────────────────────────────────────────────────

enum class ScanMode(val label: String, val emoji: String) {
    SURFACE   ("Surface Classify", "🏗️"),
    LIFE_SIGN ("Life Sign",        "🫀"),
}

data class SurfaceResult(
    val material:   String,
    val emoji:      String,
    val decayConst: Float,      // λ (1/s)
    val peakAccelG: Float,      // peak acceleration in g
    val confidence: Float,
    val phiSurface: Float,      // manifold φ
    val hardness:   Float,
    val advice:     String,
    val sampleCount: Int,
)

data class LifeSignResult(
    val breathingRpm:    Float?,   // estimated breaths per minute (null if undetected)
    val heartBpm:        Float?,   // estimated heart BPM (null if undetected)
    val breathSnrPct:    Float,    // breathing band signal fraction (%)
    val heartSnrPct:     Float,    // heartbeat band signal fraction (%)
    val lifeSignDetected: Boolean,
    val sampleCount:     Int,
)

data class SurfaceScanUiState(
    val mode:          ScanMode      = ScanMode.SURFACE,
    val scanning:      Boolean       = false,
    val progress:      Float         = 0f,
    val surfaceResult: SurfaceResult?  = null,
    val lifeSignResult: LifeSignResult? = null,
    val error:         String?       = null,
)
