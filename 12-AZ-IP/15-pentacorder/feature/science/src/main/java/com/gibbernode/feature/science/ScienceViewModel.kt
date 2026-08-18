package com.gibbernode.feature.science

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gibbernode.emf.EMFAdvisor
import com.gibbernode.enviro.WeatherAdvisor
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import javax.inject.Inject
import kotlin.math.abs
import kotlin.math.sqrt

@HiltViewModel
class ScienceViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
) : ViewModel(), SensorEventListener {

    private val sensorManager = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager

    private val _state = MutableStateFlow(ScienceUiState())
    val state: StateFlow<ScienceUiState> = _state.asStateFlow()

    // Pressure history for crowd-pressure mode
    private val pressureHistory = ArrayDeque<Pair<Long, Float>>(600)

    // Magnetometer history for magneto-nav
    private val magHistory = ArrayDeque<Triple<Float, Float, Float>>(100)

    // Accelerometer buffer for oscillation detection (last 5 s)
    private val accelBuffer = ArrayDeque<Pair<Long, Float>>(500)

    private var radiationJob: Job? = null

    // G-Force: last raw accelerometer values
    private var lastAx = 0f; private var lastAy = 0f; private var lastAz = 0f

    init {
        sensorManager.getDefaultSensor(Sensor.TYPE_PRESSURE)?.let {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL)
        }
        sensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD)?.let {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL)
        }
        sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)?.let {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_GAME)
        }
    }

    // ── Sensor callbacks ──────────────────────────────────────────────────────

    override fun onSensorChanged(event: SensorEvent?) {
        when (event?.sensor?.type) {
            Sensor.TYPE_PRESSURE       -> handlePressure(event.values[0])
            Sensor.TYPE_MAGNETIC_FIELD -> handleMag(event.values[0], event.values[1], event.values[2])
            Sensor.TYPE_ACCELEROMETER  -> handleAccel(event.values[0], event.values[1], event.values[2])
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}

    private fun handlePressure(hpa: Float) {
        val now = System.currentTimeMillis()
        if (pressureHistory.size >= 600) pressureHistory.removeFirst()
        pressureHistory.addLast(now to hpa)

        val tornado = WeatherAdvisor.tornadoInflowDetected(pressureHistory.toList())
        val local   = pressureHistory.lastOrNull()?.second ?: hpa

        _state.update { s ->
            s.copy(
                pressureHpa      = local,
                tornadoAlert     = tornado,
                pressureHistory  = pressureHistory.toList().takeLast(360),
            )
        }
    }

    private fun handleMag(bx: Float, by: Float, bz: Float) {
        val mag = sqrt(bx * bx + by * by + bz * bz)
        if (magHistory.size >= 100) magHistory.removeFirst()
        magHistory.addLast(Triple(bx, by, bz))

        val savedMag = _state.value.magnetoNavWaypointMag
        val hint     = if (savedMag != null) {
            val diff = Math.abs(mag - savedMag)
            when {
                diff < 0.5f -> "🎯 At waypoint! Very close"
                diff < 2f   -> "🔥 Warm — getting closer"
                diff < 5f   -> "😐 Cool — keep moving"
                else        -> "🥶 Cold — move in another direction"
            }
        } else null

        _state.update { s ->
            s.copy(
                magMag             = mag,
                magnetoNavHint     = hint,
            )
        }
    }

    private fun handleAccel(ax: Float, ay: Float, az: Float) {
        lastAx = ax; lastAy = ay; lastAz = az
        val mag    = sqrt(ax * ax + ay * ay + az * az)
        val gForce = mag / 9.80665f
        val now    = System.currentTimeMillis()

        if (accelBuffer.size >= 500) accelBuffer.removeFirst()
        accelBuffer.addLast(now to mag)

        val freeFall = gForce < 0.1f
        val newPeak  = maxOf(_state.value.gPeakG, gForce)
        val waveform = accelBuffer.map { it.second / 9.80665f }

        // Oscillation detection: zero-crossing on mean-subtracted signal
        var oHz: Float? = _state.value.oscillationHz
        var oPeriod: Float? = _state.value.oscillationPeriodMs
        var oPeaks: Int = _state.value.oscillationPeakCount
        if (_state.value.oscillationArmed && accelBuffer.size >= 20) {
            val vals = accelBuffer.map { it.second }
            val mean = vals.average().toFloat()
            val crossings = mutableListOf<Long>()
            for (i in 1 until accelBuffer.size) {
                val prev = accelBuffer[i - 1].second - mean
                val curr = accelBuffer[i].second - mean
                if (prev < 0f && curr >= 0f) crossings += accelBuffer[i].first
            }
            if (crossings.size >= 4) {
                val periods = (1 until crossings.size).map { (crossings[it] - crossings[it - 1]).toFloat() }
                val medPeriod = periods.sorted()[periods.size / 2]
                // Each zero-crossing pair = half period
                val fullPeriod = medPeriod * 2f
                oPeriod = fullPeriod
                oHz     = if (fullPeriod > 0f) 1000f / fullPeriod else null
                oPeaks  = crossings.size / 2
            }
        }

        _state.update { s ->
            s.copy(
                gX = ax, gY = ay, gZ = az,
                gForce    = gForce,
                gPeakG    = if (s.gPeakResetted) gForce else newPeak,
                gPeakResetted = false,
                freeFallDetected = freeFall,
                accelWaveformG = waveform.takeLast(200),
                oscillationHz      = oHz,
                oscillationPeriodMs = oPeriod,
                oscillationPeakCount = oPeaks,
            )
        }
    }

    // ── Radiation detector ────────────────────────────────────────────────────

    /**
     * Simulate a cosmic-ray dark-frame capture session.
     * Real implementation: lock exposure, capture long-exposure dark frames
     * in CameraX, and run hot-pixel / streak classifier.
     *
     * For UI purposes, this starts a timed session and increments a counter.
     */
    fun startRadiationCapture() {
        if (_state.value.radiationCapturing) return
        _state.update { it.copy(radiationCapturing = true, radiationEvents = 0) }
        radiationJob = viewModelScope.launch {
            var sessionSec = 0
            while (isActive && sessionSec < 3600) {
                delay(60_000L)
                sessionSec += 60
                // Stub: realistic background cosmic-ray rate ≈ 1–4 events/min at sea level
                val newEvent = if (Math.random() < 0.7) 1 else 0
                _state.update { s ->
                    s.copy(
                        radiationEvents    = s.radiationEvents + newEvent,
                        radiationSessionSec = sessionSec,
                    )
                }
            }
            _state.update { it.copy(radiationCapturing = false) }
        }
    }

    fun stopRadiationCapture() {
        radiationJob?.cancel()
        radiationJob = null
        _state.update { it.copy(radiationCapturing = false) }
    }

    // ── Magneto-Nav ───────────────────────────────────────────────────────────

    /** Save current magnetic field magnitude as a navigation waypoint. */
    fun saveWaypoint() = _state.update { it.copy(magnetoNavWaypointMag = it.magMag) }
    fun clearWaypoint() = _state.update { it.copy(magnetoNavWaypointMag = null, magnetoNavHint = null) }

    // ── G-Force / Free-Fall ──────────────────────────────────────────────────

    fun resetGPeak() = _state.update { it.copy(gPeakG = 0f, gPeakResetted = true) }

    // ── Oscillation Experiment ───────────────────────────────────────────────

    fun armOscillation() {
        accelBuffer.clear()
        _state.update { it.copy(oscillationArmed = true, oscillationHz = null, oscillationPeriodMs = null, oscillationPeakCount = 0) }
    }

    fun disarmOscillation() = _state.update { it.copy(oscillationArmed = false) }

    fun exportOscillationCsv(): String {
        val sb = StringBuilder("epoch_ms,g_force\n")
        accelBuffer.forEach { (t, v) -> sb.append("$t,${"%.4f".format(v / 9.80665f)}\n") }
        return sb.toString()
    }

    // ── Crowd pressure ────────────────────────────────────────────────────────

    fun exportPressureCsv(): String {
        val sb = StringBuilder("epoch_ms,pressure_hpa\n")
        pressureHistory.forEach { (t, p) -> sb.append("$t,$p\n") }
        return sb.toString()
    }

    override fun onCleared() {
        radiationJob?.cancel()
        sensorManager.unregisterListener(this)
        super.onCleared()
    }
}

// ─────────────────────────────────────────────────────────────────────────────

data class ScienceUiState(
    // Radiation
    val radiationCapturing:   Boolean = false,
    val radiationEvents:      Int     = 0,
    val radiationSessionSec:  Int     = 0,

    // Crowd pressure
    val pressureHpa:          Float   = 0f,
    val tornadoAlert:         Boolean = false,
    val pressureHistory:      List<Pair<Long, Float>> = emptyList(),

    // Magneto-nav
    val magMag:               Float   = 0f,
    val magnetoNavWaypointMag: Float?  = null,
    val magnetoNavHint:       String? = null,

    // G-Force
    val gX:               Float   = 0f,
    val gY:               Float   = 0f,
    val gZ:               Float   = 0f,
    val gForce:           Float   = 1f,   // ~1g at rest
    val gPeakG:           Float   = 0f,
    val gPeakResetted:    Boolean = false,
    val freeFallDetected: Boolean = false,
    val accelWaveformG:   List<Float> = emptyList(),

    // Oscillation experiment
    val oscillationArmed:       Boolean = false,
    val oscillationHz:          Float?  = null,
    val oscillationPeriodMs:    Float?  = null,
    val oscillationPeakCount:   Int     = 0,
)
