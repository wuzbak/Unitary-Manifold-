package com.gibbernode.feature.labs

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
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
import kotlin.math.log10
import kotlin.math.sqrt

/**
 * DataLoggerViewModel
 *
 * Multi-sensor simultaneous recording with CSV export.
 * Sensor Logger parity — records selected channels to in-memory lists then
 * offers per-sensor CSV export for sharing via Android Share sheet.
 *
 * Channels: Accelerometer, Gyroscope, Magnetometer, Barometer, Light,
 *           GPS, Audio dB SPL.
 *
 * Experiment Trigger: optional threshold on |accel| to auto-start recording.
 */
@HiltViewModel
class DataLoggerViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
) : ViewModel() {

    private val sensorManager  = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private val locationManager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager

    private val _state = MutableStateFlow(DataLoggerUiState())
    val state: StateFlow<DataLoggerUiState> = _state.asStateFlow()

    // Per-channel in-memory storage: list of CSV rows (no header)
    private val rows = mutableMapOf<LogChannel, MutableList<String>>()
    private var startEpochMs = 0L

    private var sensorListener: SensorEventListener? = null
    private var locationListener: LocationListener? = null
    private var audioJob: Job? = null

    // ── Controls ──────────────────────────────────────────────────────────────

    fun toggleChannel(ch: LogChannel) {
        if (_state.value.recording) return
        _state.update { s ->
            val enabled = s.enabledChannels.toMutableSet()
            if (ch in enabled) enabled.remove(ch) else enabled.add(ch)
            s.copy(enabledChannels = enabled)
        }
    }

    fun setSessionName(name: String) = _state.update { it.copy(sessionName = name) }

    fun setTrigger(type: TriggerType, threshold: Float) =
        _state.update { it.copy(triggerType = type, triggerThreshold = threshold) }

    fun startRecording() {
        if (_state.value.recording) return
        startEpochMs = System.currentTimeMillis()
        _state.value.enabledChannels.forEach { rows[it] = mutableListOf() }
        val armed = _state.value.triggerType != TriggerType.IMMEDIATE
        _state.update { it.copy(recording = true, rowCount = 0, triggerArmed = armed, exportCsvMap = emptyMap()) }

        registerSensorListener()
        if (LogChannel.GPS in _state.value.enabledChannels) registerLocationListener()
        if (LogChannel.AUDIO_DB in _state.value.enabledChannels) startAudioCapture()
    }

    fun stopRecording() {
        if (!_state.value.recording) return
        unregisterAll()
        val csvMap = buildCsvMap()
        _state.update { it.copy(recording = false, triggerArmed = false, exportCsvMap = csvMap) }
    }

    /** Returns CSV string for all channels merged or individual per channel, keyed by channel name. */
    private fun buildCsvMap(): Map<String, String> {
        val result = mutableMapOf<String, String>()
        rows.forEach { (ch, lines) ->
            val header = csvHeader(ch)
            result[ch.label] = header + "\n" + lines.joinToString("\n")
        }
        return result
    }

    private fun csvHeader(ch: LogChannel) = when (ch) {
        LogChannel.ACCELEROMETER -> "epoch_ms,rel_ms,ax_ms2,ay_ms2,az_ms2,|a|_ms2"
        LogChannel.GYROSCOPE     -> "epoch_ms,rel_ms,gx_rads,gy_rads,gz_rads"
        LogChannel.MAGNETOMETER  -> "epoch_ms,rel_ms,bx_uT,by_uT,bz_uT,|B|_uT"
        LogChannel.BAROMETER     -> "epoch_ms,rel_ms,pressure_hPa"
        LogChannel.LIGHT         -> "epoch_ms,rel_ms,lux"
        LogChannel.GPS           -> "epoch_ms,rel_ms,lat,lon,alt_m,accuracy_m,speed_ms"
        LogChannel.AUDIO_DB      -> "epoch_ms,rel_ms,db_spl"
    }

    // ── Sensor registration ────────────────────────────────────────────────────

    private fun registerSensorListener() {
        val enabled = _state.value.enabledChannels
        val typeMap = mapOf(
            LogChannel.ACCELEROMETER to Sensor.TYPE_ACCELEROMETER,
            LogChannel.GYROSCOPE     to Sensor.TYPE_GYROSCOPE,
            LogChannel.MAGNETOMETER  to Sensor.TYPE_MAGNETIC_FIELD,
            LogChannel.BAROMETER     to Sensor.TYPE_PRESSURE,
            LogChannel.LIGHT         to Sensor.TYPE_LIGHT,
        )
        val listener = object : SensorEventListener {
            override fun onSensorChanged(event: SensorEvent?) {
                event ?: return
                val now    = System.currentTimeMillis()
                val relMs  = now - startEpochMs
                val v      = event.values
                val ch = when (event.sensor.type) {
                    Sensor.TYPE_ACCELEROMETER   -> LogChannel.ACCELEROMETER
                    Sensor.TYPE_GYROSCOPE       -> LogChannel.GYROSCOPE
                    Sensor.TYPE_MAGNETIC_FIELD  -> LogChannel.MAGNETOMETER
                    Sensor.TYPE_PRESSURE        -> LogChannel.BAROMETER
                    Sensor.TYPE_LIGHT           -> LogChannel.LIGHT
                    else -> return
                }
                if (ch !in enabled) return

                // Trigger check
                if (_state.value.triggerArmed) {
                    val s = _state.value
                    val triggered = when (s.triggerType) {
                        TriggerType.ACCEL_THRESHOLD -> {
                            ch == LogChannel.ACCELEROMETER &&
                            sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2]) >= s.triggerThreshold
                        }
                        else -> false
                    }
                    if (triggered) _state.update { it.copy(triggerArmed = false) }
                    else return
                }

                val row = when (ch) {
                    LogChannel.ACCELEROMETER -> {
                        val mag = sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2])
                        "$now,$relMs,${"%.4f".format(v[0])},${"%.4f".format(v[1])},${"%.4f".format(v[2])},${"%.4f".format(mag)}"
                    }
                    LogChannel.GYROSCOPE ->
                        "$now,$relMs,${"%.5f".format(v[0])},${"%.5f".format(v[1])},${"%.5f".format(v[2])}"
                    LogChannel.MAGNETOMETER -> {
                        val mag = sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2])
                        "$now,$relMs,${"%.2f".format(v[0])},${"%.2f".format(v[1])},${"%.2f".format(v[2])},${"%.2f".format(mag)}"
                    }
                    LogChannel.BAROMETER ->
                        "$now,$relMs,${"%.3f".format(v[0])}"
                    LogChannel.LIGHT ->
                        "$now,$relMs,${"%.1f".format(v[0])}"
                    else -> return
                }
                rows[ch]?.add(row)
                _state.update { it.copy(rowCount = it.rowCount + 1) }
            }
            override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}
        }
        sensorListener = listener
        typeMap.forEach { (ch, type) ->
            if (ch in enabled) {
                sensorManager.getDefaultSensor(type)?.let {
                    sensorManager.registerListener(listener, it, SensorManager.SENSOR_DELAY_GAME)
                }
            }
        }
    }

    private fun registerLocationListener() {
        val ll = object : LocationListener {
            override fun onLocationChanged(loc: Location) {
                if (!_state.value.recording || _state.value.triggerArmed) return
                val now   = System.currentTimeMillis()
                val relMs = now - startEpochMs
                val row   = "$now,$relMs,${"%.7f".format(loc.latitude)},${"%.7f".format(loc.longitude)}," +
                            "${"%.1f".format(loc.altitude)},${"%.1f".format(loc.accuracy)},${"%.2f".format(loc.speed)}"
                rows[LogChannel.GPS]?.add(row)
                _state.update { it.copy(rowCount = it.rowCount + 1) }
            }
        }
        locationListener = ll
        try {
            locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 1000L, 0f, ll)
        } catch (_: SecurityException) {}
    }

    private fun startAudioCapture() {
        val sampleRate = 44_100
        val frameSize  = 2048
        audioJob = viewModelScope.launch {
            try {
                val minBuf = AudioRecord.getMinBufferSize(
                    sampleRate, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT)
                val record = AudioRecord(
                    MediaRecorder.AudioSource.MIC, sampleRate,
                    AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT,
                    minBuf.coerceAtLeast(frameSize * 2),
                )
                record.startRecording()
                val pcm = ShortArray(frameSize)
                while (isActive && _state.value.recording) {
                    val read = record.read(pcm, 0, frameSize)
                    if (read <= 0) continue
                    if (_state.value.triggerArmed) continue
                    var sumSq = 0.0
                    for (i in 0 until read) { val s = pcm[i].toFloat() / 32768f; sumSq += s * s }
                    val rms = sqrt(sumSq / read).toFloat()
                    val db  = if (rms > 1e-8f) 20f * log10(rms) + 94f else -120f
                    val now   = System.currentTimeMillis()
                    val relMs = now - startEpochMs
                    rows[LogChannel.AUDIO_DB]?.add("$now,$relMs,${"%.2f".format(db)}")
                    _state.update { it.copy(rowCount = it.rowCount + 1) }
                }
                record.stop()
                record.release()
            } catch (_: SecurityException) {}
        }
    }

    private fun unregisterAll() {
        sensorListener?.let { sensorManager.unregisterListener(it) }
        sensorListener = null
        locationListener?.let { locationManager.removeUpdates(it) }
        locationListener = null
        audioJob?.cancel()
        audioJob = null
    }

    override fun onCleared() {
        unregisterAll()
        super.onCleared()
    }
}

// ─────────────────────────────────────────────────────────────────────────────

enum class LogChannel(val label: String, val emoji: String) {
    ACCELEROMETER("Accelerometer", "📐"),
    GYROSCOPE    ("Gyroscope",     "🌀"),
    MAGNETOMETER ("Magnetometer",  "🧲"),
    BAROMETER    ("Barometer",     "🌡️"),
    LIGHT        ("Ambient Light", "💡"),
    GPS          ("GPS",           "📍"),
    AUDIO_DB     ("Audio dB",      "🔊"),
}

enum class TriggerType(val label: String) {
    IMMEDIATE       ("Start immediately"),
    ACCEL_THRESHOLD ("Start when |accel| ≥ threshold"),
}

data class DataLoggerUiState(
    val sessionName:      String             = "session_1",
    val recording:        Boolean            = false,
    val enabledChannels:  Set<LogChannel>    = setOf(LogChannel.ACCELEROMETER, LogChannel.BAROMETER, LogChannel.LIGHT),
    val rowCount:         Int                = 0,
    val triggerType:      TriggerType        = TriggerType.IMMEDIATE,
    val triggerThreshold: Float              = 15f,  // m/s² ≈ 1.5 g
    val triggerArmed:     Boolean            = false,
    val exportCsvMap:     Map<String, String> = emptyMap(),
)
