package com.gibbernode.feature.spen

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import androidx.lifecycle.ViewModel
import com.gibbernode.gibberwave.SensorBridge
import com.gibbernode.health.TremorAdvisor
import com.gibbernode.spen.SPenAdvisor
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import javax.inject.Inject

/**
 * SPenViewModel
 *
 * Manages S Pen gesture bindings, live stroke analysis, and air-writing
 * signature mode.
 *
 * Sensor wiring:
 *   - Gyroscope (TYPE_GYROSCOPE) → gesture classification + IMU display.
 *   - S Pen MotionEvent pressure / tilt → stroke analysis (injected by the
 *     composable via [addStrokePoint]).
 *   - Air Action events are received via the Samsung SPen Remote SDK;
 *     on devices without it, the gyroscope stream is used as proxy.
 */
@HiltViewModel
class SPenViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
    private val sensorBridge: SensorBridge,
) : ViewModel(), SensorEventListener {

    private val sensorManager = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager

    private val _state = MutableStateFlow(SPenUiState())
    val state: StateFlow<SPenUiState> = _state.asStateFlow()

    // IMU ring-buffer for gesture classification
    private val gyroBuffer = ArrayDeque<Float>(128)

    // Stroke buffer for current stroke
    private val strokeBuffer = mutableListOf<SPenAdvisor.StrokePoint>()

    // Custom gesture bindings (layered on top of defaults)
    private val customBindings =
        mutableMapOf<SPenAdvisor.GesturePattern, SPenAdvisor.AirCommand>()

    init {
        sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE)?.let { sensor ->
            sensorManager.registerListener(this, sensor, SensorManager.SENSOR_DELAY_GAME)
        }
    }

    // ── Sensor callbacks ──────────────────────────────────────────────────────

    override fun onSensorChanged(event: SensorEvent?) {
        if (event?.sensor?.type != Sensor.TYPE_GYROSCOPE) return
        val gx = event.values[0]
        val gy = event.values[1]
        val gz = event.values[2]
        val mag = kotlin.math.sqrt(gx * gx + gy * gy + gz * gz.toDouble()).toFloat()

        if (gyroBuffer.size >= 128) gyroBuffer.removeFirst()
        gyroBuffer.addLast(mag)

        _state.update { s ->
            s.copy(
                gyroX = gx,
                gyroY = gy,
                gyroZ = gz,
                gyroMag = mag,
            )
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}

    // ── Stroke ingestion ──────────────────────────────────────────────────────

    /** Called by the Composable for each MotionEvent point during S Pen drawing. */
    fun addStrokePoint(x: Float, y: Float, pressure: Float, tiltDeg: Float) {
        strokeBuffer += SPenAdvisor.StrokePoint(
            x           = x,
            y           = y,
            pressure    = pressure,
            tiltDeg     = tiltDeg,
            timestampMs = System.currentTimeMillis(),
        )
    }

    /** Called when the pen lifts (ACTION_UP) — finalise stroke analysis. */
    fun finaliseStroke() {
        if (strokeBuffer.size < 2) {
            strokeBuffer.clear()
            return
        }
        val analysis = SPenAdvisor.analyze(strokeBuffer.toList())
        val phiHuman = SPenAdvisor.phiHuman(analysis)
        val velocities = strokeBuffer.zipWithNext { a, b ->
            val dx = b.x - a.x; val dy = b.y - a.y
            val dt = (b.timestampMs - a.timestampMs).coerceAtLeast(1L)
            kotlin.math.sqrt((dx * dx + dy * dy).toDouble()).toFloat() / dt
        }
        val tremorReading = TremorAdvisor.assess(velocities)

        // Push φ_human (Ψ_human intent layer, φ3) to the shared bridge so
        // PentadViewModel picks it up without a direct cross-module reference.
        sensorBridge.pushPhiHuman(phiHuman)

        _state.update { s ->
            val history = (s.tremorHistory + tremorReading).takeLast(10)
            s.copy(
                lastStrokeAnalysis = analysis,
                phiHuman           = phiHuman,
                tremorHistory      = history,
            )
        }
        strokeBuffer.clear()
    }

    // ── Air writing ───────────────────────────────────────────────────────────

    /** Start recording a 3D air-writing gesture from the gyroscope. */
    fun startAirWrite() = _state.update { it.copy(airWriteActive = true, airWriteDeltas = emptyList()) }

    /** Stop recording and compute the air-write hash. */
    fun finishAirWrite() {
        val deltas = _state.value.airWriteDeltas
        val sig    = SPenAdvisor.airWriteHash(deltas)
        _state.update { it.copy(airWriteActive = false, lastAirSignature = sig) }
    }

    /** Feed latest gyro delta into the air-write buffer. */
    fun feedAirWriteDelta(dx: Float, dy: Float, dz: Float) {
        if (!_state.value.airWriteActive) return
        _state.update { s ->
            s.copy(airWriteDeltas = s.airWriteDeltas + Triple(dx, dy, dz))
        }
    }

    // ── Gesture classifier ────────────────────────────────────────────────────

    /** Run gesture classification on the current gyro ring-buffer. */
    fun classifyCurrentGesture() {
        val gesture = SPenAdvisor.classifyGesture(gyroBuffer.toList())
        val command = SPenAdvisor.resolveCommand(gesture, customBindings)
        _state.update { s ->
            s.copy(
                lastGesture = gesture,
                lastCommand = command,
                gestureLog  = (s.gestureLog + "$gesture → ${command.emoji} ${command.label}").takeLast(20),
            )
        }
    }

    // ── Binding editor ────────────────────────────────────────────────────────

    fun setBinding(gesture: SPenAdvisor.GesturePattern, command: SPenAdvisor.AirCommand) {
        customBindings[gesture] = command
        _state.update { it.copy(bindings = SPenAdvisor.defaultBindings + customBindings) }
    }

    fun resetBindings() {
        customBindings.clear()
        _state.update { it.copy(bindings = SPenAdvisor.defaultBindings) }
    }

    override fun onCleared() {
        sensorManager.unregisterListener(this)
        super.onCleared()
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// UI State
// ─────────────────────────────────────────────────────────────────────────────

data class SPenUiState(
    // Live IMU
    val gyroX:   Float = 0f,
    val gyroY:   Float = 0f,
    val gyroZ:   Float = 0f,
    val gyroMag: Float = 0f,

    // Stroke analysis
    val lastStrokeAnalysis: SPenAdvisor.StrokeAnalysis? = null,
    val phiHuman:           Float = 0.5f,

    // Tremor
    val tremorHistory: List<com.gibbernode.health.TremorAdvisor.TremorReading> = emptyList(),

    // Gestures
    val lastGesture: SPenAdvisor.GesturePattern? = null,
    val lastCommand: SPenAdvisor.AirCommand? = null,
    val gestureLog:  List<String> = emptyList(),

    // Bindings
    val bindings: Map<SPenAdvisor.GesturePattern, SPenAdvisor.AirCommand> =
        SPenAdvisor.defaultBindings,

    // Air write
    val airWriteActive:  Boolean = false,
    val airWriteDeltas:  List<Triple<Float, Float, Float>> = emptyList(),
    val lastAirSignature: SPenAdvisor.AirSignature? = null,
)
