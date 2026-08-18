package com.gibbernode.feature.tricorder

import android.bluetooth.BluetoothManager
import android.content.BroadcastReceiver
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
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import android.net.NetworkRequest
import android.net.wifi.WifiManager
import android.net.wifi.p2p.WifiP2pManager
import android.os.BatteryManager
import android.os.Build
import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gibbernode.connectivity.ConnectivityAdvisor
import com.gibbernode.energy.EnergyAdvisor
import com.gibbernode.gibberwave.AdaptiveState
import com.gibbernode.gibberwave.AdaptiveStateHolder
import com.gibbernode.gibberwave.BiometricReading
import com.gibbernode.gibberwave.SensorBridge
import com.gibbernode.gibberwave.SensorBridgeSnapshot
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject
import kotlin.math.sqrt

private const val TAG = "Pentacorder/TricorderVM"

/**
 * TricorderViewModel
 *
 * Registers every Android sensor available on the S24 Ultra and assembles the
 * 5D Unitary-Manifold state vector Ψ(t) — an exact Android port of
 * S24Ultra/scripts/sensor_daemon.py.
 *
 * Sensor → Manifold field mapping (from S24Ultra/docs/SENSOR_MAP.md):
 *   Accelerometer    → g_μν  — metric perturbation / δg
 *   Gyroscope        → Γ^σ   — Levi-Civita connection
 *   Magnetometer     → H_μν  — Kaluza-Klein gauge field
 *   Barometer        → B_4   — compact-dimension pressure
 *   Ambient light    → photon flux / CMB proxy
 *   Proximity        → boundary condition flag
 *   Gravity          → g_μν  local frame (virtual)
 *   Rotation vector  → SO(3) frame orientation (virtual)
 *   Linear accel     → inertial 3-vector (virtual)
 *   Step counter     → phase-space path integral (virtual)
 *   Heart rate       → φ-homeostasis frequency
 *   GPS              → geodesic / λ-coordinate
 *   Battery/thermal  → φ — energy scalar
 *
 * Energy Advisory (EnergyAdvisor):
 *   Computes battery band (CRITICAL / FLOOR / BALANCED / SHARE_ELIGIBLE / SURPLUS),
 *   RF harvest estimate from WiFi RSSI scan, and PowerShare governance decision.
 *
 * Connectivity Advisor (ConnectivityAdvisor):
 *   Tracks best available tier (Carrier → WiFi → WiFi Direct → BT → Acoustic → Offline),
 *   GPS fix quality, and IMU dead-reckoning availability.
 */
@HiltViewModel
class TricorderViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
    private val sensorBridge: SensorBridge,
    private val adaptive: AdaptiveStateHolder,
) : ViewModel(), SensorEventListener {

    private val sensorManager       = context.getSystemService(Context.SENSOR_SERVICE)       as SensorManager
    private val locationManager     = context.getSystemService(Context.LOCATION_SERVICE)     as LocationManager
    private val batteryManager      = context.getSystemService(Context.BATTERY_SERVICE)      as BatteryManager
    private val wifiManager         = context.applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
    private val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
    private val wifiP2pManager      = context.getSystemService(Context.WIFI_P2P_SERVICE)     as? WifiP2pManager
    private val bluetoothAdapter    = (context.getSystemService(Context.BLUETOOTH_SERVICE) as? BluetoothManager)?.adapter
    private val wifiP2pChannel: WifiP2pManager.Channel? =
        wifiP2pManager?.initialize(context, context.mainLooper, null)

    private val _state = MutableStateFlow(TricorderUiState())
    val state: StateFlow<TricorderUiState> = _state.asStateFlow()

    /** Live adaptive state (hints + injected cards + pinned metrics) for this screen. */
    val adaptiveState: StateFlow<AdaptiveState> = adaptive.liveState

    private var locationListener:  LocationListener? = null
    private var batteryPollerJob:  kotlinx.coroutines.Job? = null
    private var networkCallbackRegistered    = false
    private var wifiScanReceiverRegistered   = false

    // GPS track logger
    private var gpsTrackStartMs: Long = 0L

    // ── WiFi scan receiver ─────────────────────────────────────────────────────

    private val wifiScanReceiver = object : BroadcastReceiver() {
        override fun onReceive(ctx: Context?, intent: Intent?) {
            updateWifiScanResults()
        }
    }

    // ── Network callback ───────────────────────────────────────────────────────

    private val networkCallback = object : ConnectivityManager.NetworkCallback() {
        override fun onCapabilitiesChanged(network: Network, caps: NetworkCapabilities) {
            updateConnectivityState(
                hasCarrier = caps.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR),
                hasWifi    = caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI),
            )
        }
        override fun onLost(network: Network) {
            updateConnectivityState(hasCarrier = false, hasWifi = false)
        }
    }

    // ── All sensor types to register ──────────────────────────────────────────

    private val sensorTypes = listOf(
        Sensor.TYPE_ACCELEROMETER,
        Sensor.TYPE_GYROSCOPE,
        Sensor.TYPE_MAGNETIC_FIELD,
        Sensor.TYPE_PRESSURE,
        Sensor.TYPE_AMBIENT_TEMPERATURE,
        Sensor.TYPE_RELATIVE_HUMIDITY,
        Sensor.TYPE_LIGHT,
        Sensor.TYPE_PROXIMITY,
        Sensor.TYPE_GRAVITY,
        Sensor.TYPE_ROTATION_VECTOR,
        Sensor.TYPE_LINEAR_ACCELERATION,
        Sensor.TYPE_STEP_COUNTER,
        Sensor.TYPE_HEART_RATE,
    )

    init {
        registerSensors()
        startLocationUpdates()
        startBatteryPoller()
        registerWifiScanReceiver()
        startNetworkCallback()
        seedInitialConnectivity()
    }

    // ── SensorEventListener ────────────────────────────────────────────────────

    override fun onSensorChanged(event: SensorEvent?) {
        event ?: return
        when (event.sensor.type) {
            Sensor.TYPE_ACCELEROMETER -> {
                val (x, y, z) = event.values
                val mag = sqrt((x * x + y * y + z * z).toDouble()).toFloat()
                _state.update { it.copy(accelX = x, accelY = y, accelZ = z, accelMag = mag) }
            }
            Sensor.TYPE_GYROSCOPE -> {
                val (x, y, z) = event.values
                val mag = sqrt((x * x + y * y + z * z).toDouble()).toFloat()
                _state.update { it.copy(gyroX = x, gyroY = y, gyroZ = z, gyroMag = mag) }
            }
            Sensor.TYPE_MAGNETIC_FIELD -> {
                val (x, y, z) = event.values
                val mag = sqrt((x * x + y * y + z * z).toDouble()).toFloat()
                _state.update { it.copy(magX = x, magY = y, magZ = z, magMag = mag) }
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
            Sensor.TYPE_LIGHT -> {
                _state.update { it.copy(lightLux = event.values[0]) }
            }
            Sensor.TYPE_PROXIMITY -> {
                _state.update { it.copy(proximityM = event.values[0]) }
            }
            Sensor.TYPE_GRAVITY -> {
                val (x, y, z) = event.values
                _state.update { it.copy(gravX = x, gravY = y, gravZ = z) }
            }
            Sensor.TYPE_ROTATION_VECTOR -> {
                _state.update { it.copy(
                    rotX = event.values[0],
                    rotY = event.values[1],
                    rotZ = event.values[2],
                )}
            }
            Sensor.TYPE_LINEAR_ACCELERATION -> {
                val (x, y, z) = event.values
                _state.update { it.copy(linAccX = x, linAccY = y, linAccZ = z) }
            }
            Sensor.TYPE_STEP_COUNTER -> {
                _state.update { it.copy(stepCount = event.values[0].toLong()) }
            }
            Sensor.TYPE_HEART_RATE -> {
                _state.update { it.copy(heartRateBpm = event.values[0].toInt()) }
                recomputeEnergyState()  // HR changes affect φ-homeostasis display
            }
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}

    // ── Public actions ─────────────────────────────────────────────────────────

    /** Trigger a WiFi RSSI scan and recompute the RF harvest advisory. */
    fun scanWifi() {
        try {
            @Suppress("DEPRECATION")
            wifiManager.startScan()  // deprecated API 28+; throttled but still usable for advisory
        } catch (e: SecurityException) {
            Log.w(TAG, "WiFi startScan permission denied: ${e.message}")
        }
        // Also read whatever cached results are available immediately
        updateWifiScanResults()
    }

    /** Discover WiFi Direct peers and update connectivity state. */
    fun discoverWifiDirect() {
        val manager = wifiP2pManager ?: run {
            Log.w(TAG, "WiFi Direct not supported on this device")
            return
        }
        val channel = wifiP2pChannel ?: return
        manager.discoverPeers(channel, object : WifiP2pManager.ActionListener {
            override fun onSuccess() { Log.d(TAG, "WiFi Direct discovery started") }
            override fun onFailure(reason: Int) { Log.w(TAG, "WiFi Direct discovery failed: reason=$reason") }
        })
        manager.requestPeers(channel) { peerList ->
            val count = peerList.deviceList.size
            val names = peerList.deviceList.map { it.deviceName }.take(5)
            _state.update { it.copy(
                hasWifiDirect       = count > 0,
                wifiDirectPeerCount = count,
                wifiDirectPeerNames = names,
            )}
            recomputeConnectivityTier()
        }
    }

    /** Update the assumed accessory battery % for the PowerShare governance display. */
    fun setAccessoryBattPct(pct: Int) {
        _state.update { it.copy(accessoryBattPct = pct.coerceIn(0, 100)) }
        recomputeEnergyState()
    }

    // ── GPS Track Logger ──────────────────────────────────────────────────────

    /** Start recording a GPS track. Clears any previous track. */
    fun startGpsTrack() {
        gpsTrackStartMs = System.currentTimeMillis()
        _state.update { it.copy(
            gpsTrackRecording = true,
            gpsTrackPoints    = emptyList(),
            gpsTrackDistanceM = 0f,
            gpsTrackStartMs   = gpsTrackStartMs,
        )}
    }

    /** Stop recording the GPS track. */
    fun stopGpsTrack() {
        _state.update { it.copy(gpsTrackRecording = false, gpsTrackEndMs = System.currentTimeMillis()) }
    }

    /** Export the current GPS track as a CSV string (lat,lon). */
    fun exportGpsTrackCsv(): String {
        val pts = _state.value.gpsTrackPoints
        if (pts.isEmpty()) return "lat,lon\n"
        return buildString {
            appendLine("lat,lon")
            pts.forEach { (lat, lon) -> appendLine("$lat,$lon") }
        }
    }

    // ── Helpers — distance ────────────────────────────────────────────────────

    /** Haversine distance in metres between two (lat, lon) pairs. */
    private fun haversineM(a: Pair<Double, Double>, b: Pair<Double, Double>): Float {
        val r    = 6_371_000.0
        val lat1 = Math.toRadians(a.first);  val lat2 = Math.toRadians(b.first)
        val dLat = Math.toRadians(b.first  - a.first)
        val dLon = Math.toRadians(b.second - a.second)
        val sinD = kotlin.math.sin(dLat / 2)
        val sinO = kotlin.math.sin(dLon / 2)
        val c    = 2 * kotlin.math.asin(kotlin.math.sqrt(
            sinD * sinD + kotlin.math.cos(lat1) * kotlin.math.cos(lat2) * sinO * sinO))
        return (r * c).toFloat()
    }

    // ── Helpers — sensors ──────────────────────────────────────────────────────

    private fun registerSensors() {
        val available = mutableListOf<String>()
        val missing   = mutableListOf<String>()
        sensorTypes.forEach { type ->
            val sensor = sensorManager.getDefaultSensor(type)
            if (sensor != null) {
                sensorManager.registerListener(this, sensor, SensorManager.SENSOR_DELAY_NORMAL)
                available.add(sensor.name)
            } else {
                missing.add("type_$type")
            }
        }
        Log.d(TAG, "Registered ${available.size} sensors. Missing: $missing")
        _state.update { it.copy(availableSensors = available, missingSensors = missing) }
    }

    private fun startLocationUpdates() {
        try {
            val provider = when {
                locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER) ->
                    LocationManager.GPS_PROVIDER
                locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER) ->
                    LocationManager.NETWORK_PROVIDER
                else -> return
            }
            locationListener = object : LocationListener {
                override fun onLocationChanged(location: Location) {
                    val newPt = location.latitude to location.longitude
                    _state.update { s ->
                        val updatedTrack = if (s.gpsTrackRecording) {
                            val pts  = s.gpsTrackPoints + newPt
                            val dist = s.gpsTrackDistanceM + if (pts.size >= 2) {
                                haversineM(pts[pts.size - 2], pts[pts.size - 1])
                            } else 0f
                            s.copy(
                                latitude          = location.latitude,
                                longitude         = location.longitude,
                                altitude          = location.altitude,
                                gpsAccM           = location.accuracy,
                                gpsSpeedMs        = location.speed,
                                gpsBearing        = location.bearing,
                                lastGpsEpoch      = System.currentTimeMillis(),
                                gpsTrackPoints    = pts,
                                gpsTrackDistanceM = dist,
                            )
                        } else {
                            s.copy(
                                latitude     = location.latitude,
                                longitude    = location.longitude,
                                altitude     = location.altitude,
                                gpsAccM      = location.accuracy,
                                gpsSpeedMs   = location.speed,
                                gpsBearing   = location.bearing,
                                lastGpsEpoch = System.currentTimeMillis(),
                            )
                        }
                        updatedTrack
                    }
                    recomputeConnectivityTier()  // GPS fix quality affects DR status
                }
            }
            locationManager.requestLocationUpdates(provider, 5_000L, 5f, locationListener!!)
        } catch (e: SecurityException) {
            Log.w(TAG, "Location permission not granted: ${e.message}")
        }
    }

    private fun startBatteryPoller() {
        batteryPollerJob = viewModelScope.launch {
            while (true) {
                val pct   = batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
                val tempC = (context.registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
                    ?.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, 0) ?: 0) / 10f
                _state.update { it.copy(batteryPct = pct, batteryTempC = tempC) }
                recomputeEnergyState()
                pushToBridge()
                delay(5_000)
            }
        }
    }

    // ── Helpers — WiFi / network ───────────────────────────────────────────────

    private fun registerWifiScanReceiver() {
        try {
            val filter = IntentFilter(WifiManager.SCAN_RESULTS_AVAILABLE_ACTION)
            context.registerReceiver(wifiScanReceiver, filter)
            wifiScanReceiverRegistered = true
        } catch (e: Exception) {
            Log.w(TAG, "WiFi scan receiver registration failed: ${e.message}")
        }
    }

    private fun startNetworkCallback() {
        try {
            val request = NetworkRequest.Builder()
                .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
                .build()
            connectivityManager.registerNetworkCallback(request, networkCallback)
            networkCallbackRegistered = true
        } catch (e: Exception) {
            Log.w(TAG, "Network callback registration failed: ${e.message}")
        }
    }

    private fun seedInitialConnectivity() {
        val caps = try {
            connectivityManager.getNetworkCapabilities(connectivityManager.activeNetwork)
        } catch (_: Exception) { null }
        updateConnectivityState(
            hasCarrier = caps?.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) ?: false,
            hasWifi    = caps?.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)     ?: false,
        )
    }

    private fun updateWifiScanResults() {
        val apMap = try {
            wifiManager.scanResults.orEmpty().associate { scan ->
                @Suppress("DEPRECATION")
                val ssid = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU)
                    scan.wifiSsid?.toString()?.trim('"')
                        ?.takeIf { it.isNotBlank() } ?: (scan.BSSID ?: "Unknown")
                else
                    scan.SSID?.takeIf { it.isNotBlank() } ?: (scan.BSSID ?: "Unknown")
                ssid to scan.level
            }
        } catch (e: SecurityException) {
            Log.w(TAG, "WiFi scan results: permission denied: ${e.message}")
            emptyMap()
        }
        val advisory = EnergyAdvisor.rfHarvestAdvisory(apMap)
        _state.update { it.copy(wifiScanAps = apMap, harvestAdvisory = advisory) }
        recomputeEnergyState()
    }

    private fun updateConnectivityState(hasCarrier: Boolean, hasWifi: Boolean) {
        _state.update { it.copy(hasCarrier = hasCarrier, hasWifi = hasWifi) }
        recomputeConnectivityTier()
    }

    // ── Helpers — energy ──────────────────────────────────────────────────────

    private fun recomputeEnergyState() {
        val s = _state.value
        val band = EnergyAdvisor.EnergyBand.from(s.batteryPct.coerceAtLeast(0))
        val shareDecision = EnergyAdvisor.powerShareDecision(
            sentinelPct  = s.batteryPct.coerceAtLeast(0),
            accessoryPct = s.accessoryBattPct,
            batTempC     = s.batteryTempC,
        )
        _state.update { it.copy(energyBand = band, powerShareDecision = shareDecision) }
    }

    // ── Helpers — connectivity ─────────────────────────────────────────────────

    private fun recomputeConnectivityTier() {
        val s  = _state.value
        val bt = try { bluetoothAdapter?.isEnabled == true } catch (_: SecurityException) { false }
        val tier = ConnectivityAdvisor.activeTier(
            hasCarrier    = s.hasCarrier,
            hasWifi       = s.hasWifi,
            hasWifiDirect = s.hasWifiDirect,
            hasBluetooth  = bt,
            hasAcoustic   = true,  // AudioLoopService is always running in the Unitary Pentacorder
        )
        val gpsFixSec = ConnectivityAdvisor.estimateGpsFixSec(s.hasCarrier, s.hasWifi)
        val drAvail = ConnectivityAdvisor.deadReckonAvailable(
            hasAccel = s.accelMag > 0f,
            hasGyro  = s.gyroMag  > 0f,
            hasMag   = s.magMag   > 0f,
        )
        val gpsHint = ConnectivityAdvisor.gpsQualityHint(s.gpsAccM, s.hasCarrier, s.hasWifi)
        _state.update { it.copy(
            connectivityTier    = tier,
            gpsFixEstimateSec   = gpsFixSec,
            deadReckonAvailable = drAvail,
            gpsQualityHint      = gpsHint,
        )}
    }

    // ── SensorBridge push ──────────────────────────────────────────────────────

    /**
     * Push the current sensor state to the SensorBridge so other ViewModels
     * (e.g. TranslateViewModel) can pick up live data without cross-module deps.
     * Called on the 5-second battery poller tick — coarse enough to avoid flooding.
     */
    private fun pushToBridge() {
        val s = _state.value
        sensorBridge.pushSensorSnapshot(SensorBridgeSnapshot(
            accelX      = s.accelX,
            accelY      = s.accelY,
            accelZ      = s.accelZ,
            accelMag    = s.accelMag,
            linAccX     = s.linAccX,
            linAccY     = s.linAccY,
            linAccZ     = s.linAccZ,
            magMag      = s.magMag,
            pressureHpa = s.pressureHpa,
            ambientTempC = s.ambientTempC,
            humidityPct = s.humidityPct,
            lightLux    = s.lightLux,
            latitude    = s.latitude,
            longitude   = s.longitude,
            altitude    = s.altitude,
            gpsAccM     = s.gpsAccM,
            gpsSpeedMs  = s.gpsSpeedMs,
            batteryPct  = s.batteryPct,
            batteryTempC = s.batteryTempC,
            heartRateBpm = s.heartRateBpm,
        ))
        // Also push biometrics in case HR arrived from the heart-rate sensor
        if (s.heartRateBpm > 0) {
            sensorBridge.pushBiometrics(BiometricReading(hrBpm = s.heartRateBpm, spo2Pct = null))
        }
    }

    // ── Lifecycle ──────────────────────────────────────────────────────────────

    override fun onCleared() {
        sensorManager.unregisterListener(this)
        locationListener?.let { locationManager.removeUpdates(it) }
        batteryPollerJob?.cancel()
        if (wifiScanReceiverRegistered) {
            try { context.unregisterReceiver(wifiScanReceiver) } catch (_: Exception) {}
        }
        if (networkCallbackRegistered) {
            try { connectivityManager.unregisterNetworkCallback(networkCallback) } catch (_: Exception) {}
        }
        wifiP2pChannel?.close()
        super.onCleared()
    }

    // ── Adaptive card/hint helpers ─────────────────────────────────────────────

    /** Remove an assistant-injected card from the shared adaptive state. */
    fun removeAdaptiveCard(id: String) {
        adaptive.removeDashboardCard(id)
    }

    /** Clear an assistant-injected hint for the Tricorder screen. */
    fun clearTricorderHint() {
        adaptive.clearHint("tricorder")
    }
}

// ─────────────────────────────────────────────────────────────────────────────

data class TricorderUiState(
    // ── Accelerometer — δg_μν ─────────────────────────────────────────────────
    val accelX:   Float = 0f,
    val accelY:   Float = 0f,
    val accelZ:   Float = 0f,
    val accelMag: Float = 0f,

    // ── Gyroscope — Γ^σ_μν ───────────────────────────────────────────────────
    val gyroX:   Float = 0f,
    val gyroY:   Float = 0f,
    val gyroZ:   Float = 0f,
    val gyroMag: Float = 0f,

    // ── Magnetometer — H_μν ──────────────────────────────────────────────────
    val magX:   Float = 0f,
    val magY:   Float = 0f,
    val magZ:   Float = 0f,
    val magMag: Float = 0f,

    // ── Barometer / environment — B_4 ────────────────────────────────────────
    val pressureHpa:  Float = 0f,
    val ambientTempC: Float = 0f,
    val humidityPct:  Float = 0f,

    // ── Photon / CMB proxy ───────────────────────────────────────────────────
    val lightLux: Float = 0f,

    // ── Boundary condition ───────────────────────────────────────────────────
    val proximityM: Float = -1f,

    // ── Virtual sensors ──────────────────────────────────────────────────────
    val gravX:   Float = 0f,
    val gravY:   Float = 0f,
    val gravZ:   Float = 0f,
    val rotX:    Float = 0f,
    val rotY:    Float = 0f,
    val rotZ:    Float = 0f,
    val linAccX: Float = 0f,
    val linAccY: Float = 0f,
    val linAccZ: Float = 0f,
    val stepCount: Long = 0L,

    // ── Biometric — φ-homeostasis ────────────────────────────────────────────
    val heartRateBpm: Int = 0,

    // ── GPS — geodesic / λ ───────────────────────────────────────────────────
    val latitude:     Double = 0.0,
    val longitude:    Double = 0.0,
    val altitude:     Double = 0.0,
    val gpsAccM:      Float  = 0f,
    val gpsSpeedMs:   Float  = 0f,
    val gpsBearing:   Float  = 0f,
    val lastGpsEpoch: Long   = 0L,

    // ── Battery — φ energy scalar ────────────────────────────────────────────
    val batteryPct:   Int   = -1,
    val batteryTempC: Float = 0f,

    // ── Sensor inventory ─────────────────────────────────────────────────────
    val availableSensors: List<String> = emptyList(),
    val missingSensors:   List<String> = emptyList(),

    // ── Energy Advisory ──────────────────────────────────────────────────────
    val energyBand:         EnergyAdvisor.EnergyBand          = EnergyAdvisor.EnergyBand.BALANCED,
    val harvestAdvisory:    EnergyAdvisor.HarvestAdvisory     = EnergyAdvisor.NO_ADVISORY,
    val powerShareDecision: EnergyAdvisor.PowerShareDecision  = EnergyAdvisor.PowerShareDecision(false, "Pending"),
    val wifiScanAps:        Map<String, Int>                  = emptyMap(),
    val accessoryBattPct:   Int                               = -1,

    // ── Connectivity ─────────────────────────────────────────────────────────
    val connectivityTier:    ConnectivityAdvisor.ConnectivityTier = ConnectivityAdvisor.ConnectivityTier.OFFLINE,
    val hasCarrier:          Boolean = false,
    val hasWifi:             Boolean = false,
    val hasWifiDirect:       Boolean = false,
    val wifiDirectPeerCount: Int     = 0,
    val wifiDirectPeerNames: List<String> = emptyList(),
    val gpsFixEstimateSec:   Int     = 60,
    val deadReckonAvailable: Boolean = false,
    val gpsQualityHint:      String  = "Awaiting fix…",

    // ── GPS Track Logger ──────────────────────────────────────────────────────
    val gpsTrackRecording: Boolean                 = false,
    val gpsTrackPoints:    List<Pair<Double,Double>> = emptyList(),
    val gpsTrackDistanceM: Float                   = 0f,
    val gpsTrackStartMs:   Long                    = 0L,
    val gpsTrackEndMs:     Long                    = 0L,
)
