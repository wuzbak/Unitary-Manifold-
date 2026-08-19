package com.gibbernode.feature.enviro

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gibbernode.enviro.WeatherAdvisor
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class EnviroViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
) : ViewModel(), SensorEventListener {

    private val sensorManager = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager

    private val _state = MutableStateFlow(EnviroUiState())
    val state: StateFlow<EnviroUiState> = _state.asStateFlow()

    // 30-minute pressure history for trend analysis
    private val pressureHistory = ArrayDeque<Pair<Long, Float>>(1800)

    // Light accumulator for circadian tracking
    private var lightAccumUmolM2 = 0f

    // Security tripwire state
    private var tripwireArmedAt: Long? = null
    private var tripwireLuxBaseline: Float = 0f

    // Reference pressure for indoor floor estimation
    private var pressureReference: Float? = null

    private var doorAlertJob: Job? = null

    init {
        sensorManager.getDefaultSensor(Sensor.TYPE_PRESSURE)?.let {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL)
        }
        sensorManager.getDefaultSensor(Sensor.TYPE_LIGHT)?.let {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL)
        }
    }

    // ── Sensor callbacks ──────────────────────────────────────────────────────

    override fun onSensorChanged(event: SensorEvent?) {
        when (event?.sensor?.type) {
            Sensor.TYPE_PRESSURE -> handlePressure(event.values[0])
            Sensor.TYPE_LIGHT    -> handleLight(event.values[0])
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}

    private fun handlePressure(hpa: Float) {
        val now = System.currentTimeMillis()
        if (pressureHistory.size >= 1800) pressureHistory.removeFirst()
        pressureHistory.addLast(now to hpa)

        val report   = WeatherAdvisor.analyseWeather(pressureHistory.toList())
        val floorEst = pressureReference?.let {
            WeatherAdvisor.estimateFloor(it, hpa)
        }
        val tornadoAlert = WeatherAdvisor.tornadoInflowDetected(pressureHistory.toList())

        _state.update { s ->
            s.copy(
                pressureHpa    = hpa,
                weatherReport  = report,
                floorEstimate  = floorEst,
                tornadoAlert   = tornadoAlert,
                pressureHistory = pressureHistory.toList().takeLast(360),  // last 30 min
            )
        }

        // Door/window detection: spike detection
        if (_state.value.doorAlertArmed) {
            val prev = pressureHistory.dropLast(1).lastOrNull()?.second ?: hpa
            if (kotlin.math.abs(hpa - prev) > 0.05f) {
                _state.update { it.copy(doorAlertTriggered = true) }
            }
        }
    }

    private fun handleLight(lux: Float) {
        val colorReport  = WeatherAdvisor.circadianReport(lux, lightAccumUmolM2)
        lightAccumUmolM2 = colorReport.blueExposureUmolM2
        val plantAdvice  = WeatherAdvisor.plantLightAdvice(lux)

        // Tripwire check
        val tripwireTriggered = tripwireArmedAt?.let {
            kotlin.math.abs(lux - tripwireLuxBaseline) > _state.value.tripwireSensitivityLux
        } ?: false

        _state.update { s ->
            s.copy(
                lightLux         = lux,
                circadianReport  = colorReport,
                plantLightAdvice = plantAdvice,
                tripwireTriggered = s.tripwireArmed && tripwireTriggered,
            )
        }
    }

    // ── Controls ──────────────────────────────────────────────────────────────

    /** Set current pressure as the ground-floor reference. */
    fun setFloorReference() {
        pressureReference = _state.value.pressureHpa
        _state.update { it.copy(pressureReferenceHpa = pressureReference) }
    }

    /** Arm the door/window pressure-spike alert. */
    fun armDoorAlert() = _state.update { it.copy(doorAlertArmed = true, doorAlertTriggered = false) }
    fun disarmDoorAlert() = _state.update { it.copy(doorAlertArmed = false, doorAlertTriggered = false) }
    fun clearDoorAlert() = _state.update { it.copy(doorAlertTriggered = false) }

    /** Arm the light-level tripwire security mode. */
    fun armTripwire() {
        tripwireArmedAt     = System.currentTimeMillis()
        tripwireLuxBaseline = _state.value.lightLux
        _state.update { it.copy(tripwireArmed = true, tripwireTriggered = false) }
    }
    fun disarmTripwire() {
        tripwireArmedAt = null
        _state.update { it.copy(tripwireArmed = false, tripwireTriggered = false) }
    }

    fun setTripwireSensitivity(lux: Float) = _state.update { it.copy(tripwireSensitivityLux = lux) }

    /** Reset circadian blue-light accumulator. */
    fun resetCircadian() {
        lightAccumUmolM2 = 0f
        _state.update { it.copy(circadianReport = it.circadianReport?.copy(blueExposureUmolM2 = 0f)) }
    }

    /** Export pressure history as CSV string. */
    fun exportPressureHistoryCsv(): String {
        val sb = StringBuilder("epoch_ms,pressure_hpa\n")
        pressureHistory.forEach { (t, p) -> sb.append("$t,$p\n") }
        return sb.toString()
    }

    override fun onCleared() {
        sensorManager.unregisterListener(this)
        super.onCleared()
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// UI State
// ─────────────────────────────────────────────────────────────────────────────

data class EnviroUiState(
    // Barometer
    val pressureHpa:        Float = 0f,
    val pressureReferenceHpa: Float? = null,
    val pressureHistory:    List<Pair<Long, Float>> = emptyList(),
    val weatherReport:      WeatherAdvisor.WeatherReport? = null,
    val floorEstimate:      WeatherAdvisor.FloorEstimate? = null,
    val tornadoAlert:       Boolean = false,

    // Door alert
    val doorAlertArmed:     Boolean = false,
    val doorAlertTriggered: Boolean = false,

    // Light lab
    val lightLux:           Float = 0f,
    val circadianReport:    WeatherAdvisor.CircadianReport? = null,
    val plantLightAdvice:   WeatherAdvisor.PlantLight = WeatherAdvisor.PlantLight.INSUFFICIENT,

    // Security tripwire
    val tripwireArmed:      Boolean = false,
    val tripwireTriggered:  Boolean = false,
    val tripwireSensitivityLux: Float = 30f,
)
