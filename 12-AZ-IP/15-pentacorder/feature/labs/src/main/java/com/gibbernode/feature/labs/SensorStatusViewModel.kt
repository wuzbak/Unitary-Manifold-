package com.gibbernode.feature.labs

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import androidx.lifecycle.ViewModel
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import javax.inject.Inject
import kotlin.math.sqrt

/**
 * SensorStatusViewModel
 *
 * Enumerates every sensor returned by SensorManager.getSensorList(Sensor.TYPE_ALL)
 * and maintains live reading values for each one.
 *
 * Sensor Box / Physics Toolbox feature: raw hardware sensor dashboard.
 */
@HiltViewModel
class SensorStatusViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
) : ViewModel() {

    private val sensorManager = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager

    private val _state = MutableStateFlow(SensorStatusUiState())
    val state: StateFlow<SensorStatusUiState> = _state.asStateFlow()

    // Map sensor index → listener (we register all sensors)
    private val listeners = mutableListOf<SensorEventListener>()

    init {
        val allSensors = sensorManager.getSensorList(Sensor.TYPE_ALL)
        val entries = allSensors.mapIndexed { idx, sensor ->
            SensorEntry(
                id         = idx,
                name       = sensor.name,
                type       = sensor.type,
                typeName   = sensorTypeName(sensor.type),
                vendor     = sensor.vendor,
                version    = sensor.version,
                rangeStr   = "%.3g".format(sensor.maximumRange),
                resolutionStr = "%.3g".format(sensor.resolution),
                powerMaStr = "%.3g mA".format(sensor.power),
                values     = FloatArray(0),
                valueStr   = "—",
                tsMs       = 0L,
            )
        }
        _state.update { it.copy(sensors = entries) }

        // Register listeners for all sensors
        allSensors.forEachIndexed { idx, sensor ->
            val listener = object : SensorEventListener {
                override fun onSensorChanged(event: SensorEvent?) {
                    event ?: return
                    val vals  = event.values.copyOf()
                    val ts    = System.currentTimeMillis()
                    val label = formatValues(sensor.type, vals)
                    _state.update { s ->
                        val updated = s.sensors.toMutableList()
                        if (idx < updated.size) {
                            updated[idx] = updated[idx].copy(values = vals, valueStr = label, tsMs = ts)
                        }
                        s.copy(sensors = updated)
                    }
                }
                override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}
            }
            listeners += listener
            sensorManager.registerListener(listener, sensor, SensorManager.SENSOR_DELAY_NORMAL)
        }
    }

    fun setFilter(text: String) = _state.update { it.copy(filterText = text) }

    override fun onCleared() {
        listeners.forEach { sensorManager.unregisterListener(it) }
        listeners.clear()
        super.onCleared()
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private fun formatValues(type: Int, v: FloatArray): String = when {
        v.isEmpty() -> "—"
        type == Sensor.TYPE_ACCELEROMETER || type == Sensor.TYPE_GRAVITY ||
        type == Sensor.TYPE_LINEAR_ACCELERATION ->
            "x=%.2f y=%.2f z=%.2f  |a|=%.2f m/s²"
                .format(v[0], v[1], v[2], sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2]))
        type == Sensor.TYPE_GYROSCOPE ->
            "x=%.3f y=%.3f z=%.3f rad/s".format(v[0], v[1], v[2])
        type == Sensor.TYPE_MAGNETIC_FIELD ->
            "x=%.1f y=%.1f z=%.1f  |B|=%.1f µT"
                .format(v[0], v[1], v[2], sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2]))
        type == Sensor.TYPE_ROTATION_VECTOR ->
            "x=%.3f y=%.3f z=%.3f".format(v[0], v[1], v.getOrElse(2) { 0f })
        v.size == 1 -> "%.4g".format(v[0])
        v.size == 2 -> "%.4g, %.4g".format(v[0], v[1])
        v.size == 3 -> "%.4g, %.4g, %.4g".format(v[0], v[1], v[2])
        else        -> v.take(4).joinToString { "%.3g".format(it) }
    }

    private fun sensorTypeName(type: Int): String = when (type) {
        Sensor.TYPE_ACCELEROMETER        -> "Accelerometer"
        Sensor.TYPE_MAGNETIC_FIELD       -> "Magnetometer"
        Sensor.TYPE_GYROSCOPE            -> "Gyroscope"
        Sensor.TYPE_LIGHT                -> "Ambient Light"
        Sensor.TYPE_PRESSURE             -> "Barometer"
        Sensor.TYPE_PROXIMITY            -> "Proximity"
        Sensor.TYPE_GRAVITY              -> "Gravity (virtual)"
        Sensor.TYPE_LINEAR_ACCELERATION  -> "Linear Accel (virtual)"
        Sensor.TYPE_ROTATION_VECTOR      -> "Rotation Vector (virtual)"
        Sensor.TYPE_RELATIVE_HUMIDITY    -> "Humidity"
        Sensor.TYPE_AMBIENT_TEMPERATURE  -> "Temperature"
        Sensor.TYPE_STEP_COUNTER         -> "Step Counter"
        Sensor.TYPE_STEP_DETECTOR        -> "Step Detector"
        Sensor.TYPE_HEART_RATE           -> "Heart Rate"
        Sensor.TYPE_GAME_ROTATION_VECTOR -> "Game Rotation (virtual)"
        Sensor.TYPE_SIGNIFICANT_MOTION   -> "Significant Motion"
        else                             -> "Type $type"
    }
}

// ─────────────────────────────────────────────────────────────────────────────

data class SensorEntry(
    val id:            Int,
    val name:          String,
    val type:          Int,
    val typeName:      String,
    val vendor:        String,
    val version:       Int,
    val rangeStr:      String,
    val resolutionStr: String,
    val powerMaStr:    String,
    val values:        FloatArray,
    val valueStr:      String,
    val tsMs:          Long,
)

data class SensorStatusUiState(
    val sensors:    List<SensorEntry> = emptyList(),
    val filterText: String            = "",
) {
    val filteredSensors: List<SensorEntry>
        get() = if (filterText.isBlank()) sensors
                else sensors.filter {
                    it.name.contains(filterText, ignoreCase = true) ||
                    it.typeName.contains(filterText, ignoreCase = true) ||
                    it.vendor.contains(filterText, ignoreCase = true)
                }
}
