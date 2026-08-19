package com.gibbernode.feature.contractor

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gibbernode.contractor.ContractorAdvisor
import com.gibbernode.emf.EMFAdvisor
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import javax.inject.Inject
import kotlin.math.sqrt

@HiltViewModel
class ContractorViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
) : ViewModel(), SensorEventListener {

    private val sensorManager = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager

    private val _state = MutableStateFlow(ContractorUiState())
    val state: StateFlow<ContractorUiState> = _state.asStateFlow()

    // Tap detection buffers
    private val accelBuffer = ArrayDeque<Float>(400)
    private var tapCapturing = false
    private var tapStartIdx  = 0

    // Stud-finder magnetic data
    private val magMagBuffer  = ArrayDeque<Float>(100)
    private var magBaseline   = 0f
    private var magLocked     = false

    // Pressure for level mode
    private var pressureAHpa  = 0f
    private var pressureBHpa  = 0f

    init {
        sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)?.let {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_FASTEST)
        }
        sensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD)?.let {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_GAME)
        }
        sensorManager.getDefaultSensor(Sensor.TYPE_PRESSURE)?.let {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL)
        }
    }

    // ── Sensor callbacks ──────────────────────────────────────────────────────

    override fun onSensorChanged(event: SensorEvent?) {
        when (event?.sensor?.type) {
            Sensor.TYPE_ACCELEROMETER  -> handleAccel(event)
            Sensor.TYPE_MAGNETIC_FIELD -> handleMag(event)
            Sensor.TYPE_PRESSURE       -> handlePressure(event.values[0])
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}

    private fun handleAccel(event: SensorEvent) {
        val ax = event.values[0]; val ay = event.values[1]; val az = event.values[2]
        val mag = sqrt(ax * ax + ay * ay + az * az)
        if (accelBuffer.size >= 400) accelBuffer.removeFirst()
        accelBuffer.addLast(mag)

        // Auto-detect tap: sharp transient > 3 g
        if (!tapCapturing && mag > 3f * 9.81f) {
            tapCapturing = true
            tapStartIdx  = accelBuffer.size - 1
        } else if (tapCapturing && accelBuffer.size - tapStartIdx >= 40) {
            // Collect 40 samples after tap onset
            val samples = accelBuffer.toList().drop(tapStartIdx).take(80)
            val result  = ContractorAdvisor.classifyTap(samples, sampleRateHz = 200f)
            _state.update { it.copy(tapResult = result, accelHistory = accelBuffer.toList().takeLast(200)) }
            tapCapturing = false
        }
    }

    private fun handleMag(event: SensorEvent) {
        val bx = event.values[0]; val by = event.values[1]; val bz = event.values[2]
        val mag = sqrt(bx * bx + by * by + bz * bz)

        if (magMagBuffer.size >= 100) magMagBuffer.removeFirst()
        magMagBuffer.addLast(mag)
        if (!magLocked) magBaseline = mag

        val isOsc     = EMFAdvisor.isOscillating(magMagBuffer.toList())
        val studRead  = EMFAdvisor.classifyStud(magBaseline, mag, isOsc)
        _state.update { s ->
            s.copy(
                magMag     = mag,
                studReading = studRead,
                magHistory  = (s.magHistory + mag).takeLast(120),
            )
        }
    }

    private fun handlePressure(hpa: Float) {
        _state.update { s ->
            when {
                s.levelMode == LevelMode.SETTING_A -> { pressureAHpa = hpa; s.copy(pressureAHpa = hpa) }
                s.levelMode == LevelMode.MEASURING  -> {
                    pressureBHpa = hpa
                    val lvl = ContractorAdvisor.levelCheck(pressureAHpa, hpa)
                    s.copy(pressureBHpa = hpa, levelResult = lvl)
                }
                else -> s
            }
        }
    }

    // ── Controls ──────────────────────────────────────────────────────────────

    fun lockMagBaseline() {
        magBaseline = _state.value.magMag
        magLocked   = true
        _state.update { it.copy(magBaseline = magBaseline, magLocked = true) }
    }

    fun setLevelModeSetA() = _state.update { it.copy(levelMode = LevelMode.SETTING_A) }
    fun setLevelModeMeasure() = _state.update { it.copy(levelMode = LevelMode.MEASURING) }
    fun resetLevel() {
        pressureAHpa = 0f; pressureBHpa = 0f
        _state.update { it.copy(levelMode = LevelMode.IDLE, levelResult = null, pressureAHpa = 0f, pressureBHpa = 0f) }
    }

    fun docForensicsGuidance(zoom: Float) =
        ContractorAdvisor.docForensicsGuidance(zoom)

    override fun onCleared() {
        sensorManager.unregisterListener(this)
        super.onCleared()
    }
}

// ─────────────────────────────────────────────────────────────────────────────

enum class LevelMode { IDLE, SETTING_A, MEASURING }

data class ContractorUiState(
    // Tap test
    val tapResult:    ContractorAdvisor.TapResult? = null,
    val accelHistory: List<Float> = emptyList(),

    // Stud finder
    val magMag:      Float = 0f,
    val magBaseline: Float = 0f,
    val magLocked:   Boolean = false,
    val studReading: EMFAdvisor.StudReading? = null,
    val magHistory:  List<Float> = emptyList(),

    // Level
    val levelMode:    LevelMode = LevelMode.IDLE,
    val pressureAHpa: Float = 0f,
    val pressureBHpa: Float = 0f,
    val levelResult:  ContractorAdvisor.LevelResult? = null,
)
