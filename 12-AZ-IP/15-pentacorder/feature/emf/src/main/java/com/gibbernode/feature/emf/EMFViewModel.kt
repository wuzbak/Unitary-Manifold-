package com.gibbernode.feature.emf

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gibbernode.emf.EMFAdvisor
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.delay
import javax.inject.Inject
import kotlin.math.atan2
import kotlin.math.sqrt

@HiltViewModel
class EMFViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
) : ViewModel(), SensorEventListener {

    private val sensorManager = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager

    private val _state = MutableStateFlow(EMFUiState())
    val state: StateFlow<EMFUiState> = _state.asStateFlow()

    // Rolling buffer for dirty-electricity / sleep scan (last 200 samples ≈ 2 s at 100 Hz)
    private val magBuffer = ArrayDeque<Triple<Float, Float, Float>>(200)
    private val magMagBuffer = ArrayDeque<Float>(200)

    private var baselineUt: Float = 0f
    private var baselineLocked = false

    // Latest raw values for orientation computation
    private var lastAccelValues = FloatArray(3)
    private var lastMagValues   = FloatArray(3)
    private var hasAccel        = false
    private var hasMag          = false

    init {
        sensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD)?.let { sensor ->
            sensorManager.registerListener(this, sensor, SensorManager.SENSOR_DELAY_GAME)
        }
        sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)?.let { sensor ->
            sensorManager.registerListener(this, sensor, SensorManager.SENSOR_DELAY_GAME)
        }
    }

    // ── Sensor callbacks ──────────────────────────────────────────────────────

    override fun onSensorChanged(event: SensorEvent?) {
        when (event?.sensor?.type) {
            Sensor.TYPE_MAGNETIC_FIELD -> {
                val bx = event.values[0]
                val by = event.values[1]
                val bz = event.values[2]
                val mag = sqrt(bx * bx + by * by + bz * bz)

                if (magBuffer.size >= 200) { magBuffer.removeFirst(); magMagBuffer.removeFirst() }
                magBuffer.addLast(Triple(bx, by, bz))
                magMagBuffer.addLast(mag)
                lastMagValues[0] = bx; lastMagValues[1] = by; lastMagValues[2] = bz
                hasMag = true

                if (!baselineLocked) baselineUt = mag

                val isOsc   = EMFAdvisor.isOscillating(magMagBuffer.toList())
                val reading = EMFAdvisor.classifyStud(baselineUt, mag, isOsc)

                _state.update { s ->
                    val history = (s.magHistory + mag).takeLast(120)
                    s.copy(
                        magX         = bx,
                        magY         = by,
                        magZ         = bz,
                        magMag       = mag,
                        baselineUt   = baselineUt,
                        studReading  = reading,
                        isOscillating = isOsc,
                        magHistory   = history,
                        emfZone      = EMFAdvisor.emfZone(kotlin.math.abs(mag - baselineUt)),
                    )
                }
                updateOrientation()
            }
            Sensor.TYPE_ACCELEROMETER -> {
                lastAccelValues[0] = event.values[0]
                lastAccelValues[1] = event.values[1]
                lastAccelValues[2] = event.values[2]
                hasAccel = true
                updateOrientation()
            }
        }
    }

    /** Compute orientation using SensorManager rotation matrix when both sensors available. */
    private fun updateOrientation() {
        if (!hasAccel || !hasMag) return
        val rotMatrix   = FloatArray(9)
        val inclMatrix  = FloatArray(9)
        val success = SensorManager.getRotationMatrix(rotMatrix, inclMatrix, lastAccelValues, lastMagValues)
        if (!success) return
        val orientation = FloatArray(3)
        SensorManager.getOrientation(rotMatrix, orientation)
        // orientation: [0]=azimuth, [1]=pitch, [2]=roll — all in radians
        val azimuthDeg = Math.toDegrees(orientation[0].toDouble()).toFloat().let { if (it < 0f) it + 360f else it }
        val pitchDeg   = Math.toDegrees(orientation[1].toDouble()).toFloat()
        val rollDeg    = Math.toDegrees(orientation[2].toDouble()).toFloat()
        _state.update { it.copy(azimuthDeg = azimuthDeg, pitchDeg = pitchDeg, rollDeg = rollDeg) }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}

    // ── Controls ──────────────────────────────────────────────────────────────

    /** Lock the current reading as the stud-finder baseline. */
    fun lockBaseline() {
        baselineUt = _state.value.magMag
        baselineLocked = true
        _state.update { it.copy(baselineUt = baselineUt, baselineLocked = true) }
    }

    /** Reset the baseline to the current reading. */
    fun resetBaseline() {
        baselineLocked = false
        _state.update { it.copy(baselineLocked = false) }
    }

    /** Run a 30-second sleep environment scan. */
    fun startSleepScan() {
        _state.update { it.copy(sleepScanRunning = true, sleepScore = null) }
        viewModelScope.launch {
            val snapshots = mutableListOf<Triple<Float, Float, Float>>()
            repeat(30) {
                delay(1_000L)
                snapshots += magBuffer.lastOrNull() ?: Triple(0f, 0f, 0f)
            }
            val score = EMFAdvisor.sleepScore(snapshots, baselineUt)
            _state.update { it.copy(sleepScanRunning = false, sleepScore = score) }
        }
    }

    /** Compute dirty-electricity reading from the current rolling buffer. */
    fun computeDirtyElectricity() {
        val reading = EMFAdvisor.dirtyElectricity(magMagBuffer.toList())
        _state.update { it.copy(dirtyElectricity = reading) }
    }

    override fun onCleared() {
        sensorManager.unregisterListener(this)
        super.onCleared()
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// UI State
// ─────────────────────────────────────────────────────────────────────────────

data class EMFUiState(
    val magX:          Float = 0f,
    val magY:          Float = 0f,
    val magZ:          Float = 0f,
    val magMag:        Float = 0f,
    val baselineUt:    Float = 0f,
    val baselineLocked: Boolean = false,
    val isOscillating: Boolean = false,
    val studReading:   EMFAdvisor.StudReading? = null,
    val emfZone:       EMFAdvisor.EmfZone = EMFAdvisor.EmfZone.LOW,
    val magHistory:    List<Float> = emptyList(),   // last 120 samples for sparkline
    val sleepScanRunning: Boolean = false,
    val sleepScore:    EMFAdvisor.SleepEmfScore? = null,
    val dirtyElectricity: EMFAdvisor.DirtyElectricityReading? = null,
    // Orientation / Compass
    val azimuthDeg:    Float = 0f,
    val pitchDeg:      Float = 0f,
    val rollDeg:       Float = 0f,
)
