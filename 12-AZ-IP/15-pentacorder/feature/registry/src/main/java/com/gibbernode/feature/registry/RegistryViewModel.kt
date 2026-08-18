package com.gibbernode.feature.registry

import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.BatteryManager
import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

private const val TAG = "Pentacorder/RegistryVM"

@HiltViewModel
class RegistryViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
) : ViewModel(), SensorEventListener {

    private val sensorManager  = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private val locationManager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager
    private val batteryManager = context.getSystemService(Context.BATTERY_SERVICE) as BatteryManager

    private val _state = MutableStateFlow(RegistryUiState())
    val state: StateFlow<RegistryUiState> = _state.asStateFlow()

    // ── Registered accessories (MNFT devices) ─────────────────────────────────
    private val accessories = mutableListOf<AccessoryEntry>()

    init {
        registerSensors()
        refreshBattery()
        startLocationUpdates()
    }

    /** Parse and register a received MNFT payload. */
    fun onMnftReceived(payload: String) {
        // MNFT:{device_id}:{seq}/{total}:{json_chunk}
        val parts = payload.split(":")
        if (parts.size < 3) return
        val deviceId = parts.getOrElse(1) { return }
        val existing = accessories.firstOrNull { it.deviceId == deviceId }
        if (existing == null) {
            accessories.add(AccessoryEntry(deviceId = deviceId, rawManifest = payload))
            _state.update { it.copy(accessories = accessories.toList()) }
            Log.i(TAG, "Registered new accessory: $deviceId")
        } else {
            val idx = accessories.indexOf(existing)
            accessories[idx] = existing.copy(
                rawManifest = payload,
                lastSeenMs  = System.currentTimeMillis()
            )
            _state.update { it.copy(accessories = accessories.toList()) }
        }
    }

    // ── Android sensor callbacks ───────────────────────────────────────────────

    override fun onSensorChanged(event: SensorEvent?) {
        event ?: return
        when (event.sensor.type) {
            Sensor.TYPE_ACCELEROMETER -> {
                val (x, y, z) = event.values
                _state.update { it.copy(accelX = x, accelY = y, accelZ = z) }
            }
            Sensor.TYPE_PRESSURE -> {
                _state.update { it.copy(pressureHpa = event.values[0]) }
            }
            Sensor.TYPE_AMBIENT_TEMPERATURE -> {
                _state.update { it.copy(ambientTempC = event.values[0]) }
            }
            Sensor.TYPE_RELATIVE_HUMIDITY -> {
                _state.update { it.copy(humidityPct = event.values[0]) }
            }
            // Heart rate — available on BV9900 Pro via com.blackview.toolbox bridge
            Sensor.TYPE_HEART_RATE -> {
                _state.update { it.copy(heartRateBpm = event.values[0].toInt()) }
            }
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) { /* no-op */ }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private fun registerSensors() {
        val types = listOf(
            Sensor.TYPE_ACCELEROMETER,
            Sensor.TYPE_PRESSURE,
            Sensor.TYPE_AMBIENT_TEMPERATURE,
            Sensor.TYPE_RELATIVE_HUMIDITY,
            Sensor.TYPE_HEART_RATE,
        )
        types.forEach { type ->
            sensorManager.getDefaultSensor(type)?.let { sensor ->
                sensorManager.registerListener(this, sensor, SensorManager.SENSOR_DELAY_NORMAL)
                Log.d(TAG, "Registered sensor: ${sensor.name}")
            }
        }
    }

    private fun refreshBattery() {
        val pct  = batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
        val tempC = (context.registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
            ?.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, 0) ?: 0) / 10f
        _state.update { it.copy(batteryPct = pct, batteryTempC = tempC) }
    }

    // Kept as a field so onCleared() can unregister it and prevent GPS leak
    private var locationListener: LocationListener? = null

    private fun startLocationUpdates() {
        try {
            // GPS_PROVIDER first; fallback to NETWORK_PROVIDER
            val provider = when {
                locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER) ->
                    LocationManager.GPS_PROVIDER
                locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER) ->
                    LocationManager.NETWORK_PROVIDER
                else -> return
            }
            locationListener = object : LocationListener {
                override fun onLocationChanged(location: Location) {
                    _state.update { it.copy(
                        latitude  = location.latitude,
                        longitude = location.longitude,
                        altitude  = location.altitude,
                        gpsAccM   = location.accuracy,
                    )}
                }
            }
            // minTime=5s, minDist=5m
            locationManager.requestLocationUpdates(provider, 5_000L, 5f, locationListener!!)
        } catch (e: SecurityException) {
            Log.w(TAG, "Location permission not granted: ${e.message}")
        }
    }

    override fun onCleared() {
        sensorManager.unregisterListener(this)
        locationListener?.let { locationManager.removeUpdates(it) }
        super.onCleared()
    }
}

// ─────────────────────────────────────────────────────────────────────────────

data class RegistryUiState(
    // Sensors
    val accelX:      Float   = 0f,
    val accelY:      Float   = 0f,
    val accelZ:      Float   = 0f,
    val pressureHpa: Float   = 0f,
    val ambientTempC: Float  = 0f,
    val humidityPct: Float   = 0f,
    val heartRateBpm: Int    = 0,
    // Battery
    val batteryPct:  Int     = -1,
    val batteryTempC: Float  = 0f,
    // Location
    val latitude:    Double  = 0.0,
    val longitude:   Double  = 0.0,
    val altitude:    Double  = 0.0,
    val gpsAccM:     Float   = 0f,
    // Accessories
    val accessories: List<AccessoryEntry> = emptyList(),
)

data class AccessoryEntry(
    val deviceId:    String,
    val rawManifest: String,
    val lastSeenMs:  Long = System.currentTimeMillis(),
)
