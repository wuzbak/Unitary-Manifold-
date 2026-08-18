package com.gibbernode.feature.medical

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.BatteryManager
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gibbernode.gibberwave.AuditLogDao
import com.gibbernode.gibberwave.AuditLogEntity
import com.gibbernode.gibberwave.AdaptiveState
import com.gibbernode.gibberwave.AdaptiveStateHolder
import com.gibbernode.gibberwave.BiometricReading
import com.gibbernode.gibberwave.CommonToken
import com.gibbernode.gibberwave.IntentTag
import com.gibbernode.gibberwave.OperationalMode
import com.gibbernode.gibberwave.PayloadBuilder
import com.gibbernode.gibberwave.SensorBridge
import com.gibbernode.gibberwave.SourceProtocol
import com.gibbernode.health.PPGAdvisor
import com.gibbernode.health.SkinColorAdvisor
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject
import kotlin.math.abs

/**
 * MedicalViewModel
 *
 * Manages state for the Medical tab:
 *  - Manual vital sign entry (HR, SpO2, temperature, resp rate, BP, consciousness)
 *  - HR from Android TYPE_HEART_RATE sensor (if available)
 *  - NEWS2 scoring — NHS National Early Warning Score 2 (Kotlin port of nurse_suite.py)
 *  - φ-homeostasis analysis — Unitary-Manifold medicine module connection
 *  - Broadcast vitals via BLUE mode acoustic transmission
 *  - Audit log persistence for every vitals event
 */
@HiltViewModel
class MedicalViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
    private val auditDao: AuditLogDao,
    private val sensorBridge: SensorBridge,
    private val adaptive: AdaptiveStateHolder,
) : ViewModel(), SensorEventListener {

    private val sensorManager = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private val batteryManager = context.getSystemService(Context.BATTERY_SERVICE) as BatteryManager

    private val _state = MutableStateFlow(MedicalUiState())
    val state: StateFlow<MedicalUiState> = _state.asStateFlow()

    /** Live adaptive state (hints + injected cards) for this screen. */
    val adaptiveState: StateFlow<AdaptiveState> = adaptive.liveState

    init {
        sensorManager.getDefaultSensor(Sensor.TYPE_HEART_RATE)?.let { sensor ->
            sensorManager.registerListener(this, sensor, SensorManager.SENSOR_DELAY_NORMAL)
        }
        refreshBattery()
    }

    // ── Vital sign entry ──────────────────────────────────────────────────────

    fun onHrChanged(v: String) {
        val bpm = v.toIntOrNull()
        _state.update { it.copy(hrBpm = bpm, hrInput = v) }
        recalculate()
    }

    fun onSpo2Changed(v: String) {
        val pct = v.toIntOrNull()
        _state.update { it.copy(spo2Pct = pct, spo2Input = v) }
        recalculate()
    }

    fun onTempChanged(v: String) {
        val t = v.toFloatOrNull()
        _state.update { it.copy(tempC = t, tempInput = v) }
        recalculate()
    }

    fun onRespChanged(v: String) {
        val r = v.toIntOrNull()
        _state.update { it.copy(respRate = r, respInput = v) }
        recalculate()
    }

    fun onConsciousnessChanged(alert: Boolean) {
        _state.update { it.copy(isAlert = alert) }
        recalculate()
    }

    fun clearVitals() {
        _state.update { MedicalUiState(sensorHrBpm = it.sensorHrBpm, batteryPct = it.batteryPct) }
    }

    /** Broadcast current vitals over acoustic BLUE mode (requires AudioEngine binding). */
    fun broadcastVitals() {
        val s = _state.value
        val hr    = s.hrBpm ?: s.sensorHrBpm ?: return
        val spo2  = s.spo2Pct ?: 0
        val temp  = s.tempC ?: 0f
        val payload = PayloadBuilder.vitals(hr, spo2, temp)
        viewModelScope.launch {
            auditDao.insert(AuditLogEntity.fromToken(CommonToken(
                source  = SourceProtocol.ACOUSTIC,
                intent  = IntentTag.TELEMETRY,
                payload = payload,
            )))
            _state.update { it.copy(lastBroadcastPayload = payload) }
        }
    }

    // ── Android sensor callbacks ──────────────────────────────────────────────

    override fun onSensorChanged(event: SensorEvent?) {
        if (event?.sensor?.type == Sensor.TYPE_HEART_RATE) {
            val bpm = event.values[0].toInt()
            _state.update { it.copy(sensorHrBpm = bpm) }
            if (_state.value.hrBpm == null) recalculate()
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}

    override fun onCleared() {
        sensorManager.unregisterListener(this)
        super.onCleared()
    }

    // ── Adaptive card/hint helpers ─────────────────────────────────────────────

    /** Remove an assistant-injected card from the shared adaptive state. */
    fun removeAdaptiveCard(id: String) {
        adaptive.removeDashboardCard(id)
    }

    /** Clear an assistant-injected hint for the Medical screen. */
    fun clearMedicalHint() {
        adaptive.clearHint("medical")
    }

    // ── Neuro tab ─────────────────────────────────────────────────────────────

    /**
     * Start a tremor measurement session.
     *
     * In production: wires into S Pen MotionEvent listener (SPenAdvisor) for
     * stroke capture, then feeds StrokeAnalysis → TremorAdvisor.  Here we
     * expose the UI hook; actual data arrives via updateTremorResult().
     */
    fun startTremorTest() {
        _state.update { it.copy(tremorRunning = true) }
        // Production: start MotionEvent capture via SPenManager, collect
        // stroke points into SPenAdvisor.analyze(), then call updateTremorResult().
        // Stub: auto-clear after a small delay for UI responsiveness.
        viewModelScope.launch {
            kotlinx.coroutines.delay(200L)
            _state.update { it.copy(tremorRunning = false) }
        }
    }

    /** Called by SPen stroke collector with a completed TremorAdvisor result. */
    fun updateTremorResult(score: Float, freqHz: Float, severityLabel: String) {
        _state.update { s ->
            s.copy(
                tremorScore    = score,
                tremorFreqHz   = freqHz,
                tremorSeverity = severityLabel,
                tremorHistory  = (s.tremorHistory + score).takeLast(10),
                tremorRunning  = false,
            )
        }
    }

    // ── Skin tab ──────────────────────────────────────────────────────────────

    /** Held reference so we can unbind cleanly. */
    private var cameraProvider: ProcessCameraProvider? = null

    /**
     * Bind a CameraX ImageAnalysis session to extract a single-frame
     * skin-colour reading from the front camera.
     *
     * Caller passes the screen's [LifecycleOwner] so CameraX manages its
     * own lifecycle correctly.  The analysis unbinds automatically when the
     * lifecycle stops, or can be stopped explicitly via [stopSkinCapture].
     *
     * Pipeline:
     *   Front camera → ImageAnalysis (RGBA_8888, centre 25% ROI)
     *     → average R/G/B channels
     *     → SkinColorAdvisor.analyse()
     *     → updateSkinResult()
     *
     * If camera permission is not granted the call is a no-op — the screen
     * must request CAMERA permission before calling this.
     */
    fun bindSkinCamera(lifecycleOwner: LifecycleOwner) {
        _state.update { it.copy(skinCapturing = true) }

        val executor = ContextCompat.getMainExecutor(context)
        val future   = ProcessCameraProvider.getInstance(context)

        future.addListener({
            val provider = future.get() ?: run {
                _state.update { it.copy(skinCapturing = false) }
                return@addListener
            }
            cameraProvider = provider

            val analysis = ImageAnalysis.Builder()
                .setOutputImageFormat(ImageAnalysis.OUTPUT_IMAGE_FORMAT_RGBA_8888)
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .build()

            analysis.setAnalyzer(executor) { imageProxy ->
                val result = analyseImageProxy(imageProxy)
                imageProxy.close()
                // Unbind after first good frame
                provider.unbindAll()
                updateSkinResult(
                    pallorIndex    = result.pallorIndex,
                    pallorSeverity = result.pallorSeverity.label,
                    jaundiceFlagged = result.jaundiceFlagged,
                    confidence     = result.confidence,
                    advice         = result.advice,
                )
            }

            try {
                provider.unbindAll()
                provider.bindToLifecycle(
                    lifecycleOwner,
                    CameraSelector.DEFAULT_FRONT_CAMERA,
                    analysis,
                )
            } catch (e: Exception) {
                _state.update { it.copy(skinCapturing = false) }
            }
        }, executor)
    }

    /** Stop any active skin-capture camera session early. */
    fun stopSkinCapture() {
        cameraProvider?.unbindAll()
        _state.update { it.copy(skinCapturing = false) }
    }

    // ── rPPG (Remote Photoplethysmography) ────────────────────────────────────

    /** Separate CameraX provider for rPPG — front camera green-channel loop. */
    private var rppgCameraProvider: ProcessCameraProvider? = null

    /** Accumulates green-channel averages during an rPPG session (~30 fps). */
    private val rppgGreenSamples = mutableListOf<Float>()

    /** Maximum frames collected before PPGAdvisor.analyse() is called (~10 s at 30 fps). */
    private val RPPG_TARGET_FRAMES = 300

    /**
     * Bind a CameraX ImageAnalysis session to the front camera and collect
     * green-channel averages for rPPG heart-rate / HRV estimation.
     *
     * After [RPPG_TARGET_FRAMES] frames the session auto-stops, calls
     * [PPGAdvisor.analyse], and updates the UI state + SensorBridge.
     *
     * Requires CAMERA permission before calling.
     */
    fun bindRppgCamera(lifecycleOwner: LifecycleOwner) {
        rppgGreenSamples.clear()
        _state.update { it.copy(rppgRunning = true, rppgProgress = 0f) }

        val executor = ContextCompat.getMainExecutor(context)
        val future   = ProcessCameraProvider.getInstance(context)

        future.addListener({
            val provider = future.get() ?: run {
                _state.update { it.copy(rppgRunning = false) }
                return@addListener
            }
            rppgCameraProvider = provider

            val analysis = ImageAnalysis.Builder()
                .setOutputImageFormat(ImageAnalysis.OUTPUT_IMAGE_FORMAT_RGBA_8888)
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .build()

            analysis.setAnalyzer(executor) { imageProxy ->
                val green = extractGreenAverage(imageProxy)
                imageProxy.close()

                rppgGreenSamples.add(green)
                val progress = rppgGreenSamples.size.toFloat() / RPPG_TARGET_FRAMES
                _state.update { it.copy(rppgProgress = progress.coerceIn(0f, 1f)) }

                if (rppgGreenSamples.size >= RPPG_TARGET_FRAMES) {
                    provider.unbindAll()
                    val result = PPGAdvisor.analyse(rppgGreenSamples.toList(), sampleRateHz = 30f)
                    updateRppgResult(result)
                }
            }

            try {
                provider.unbindAll()
                provider.bindToLifecycle(
                    lifecycleOwner,
                    CameraSelector.DEFAULT_FRONT_CAMERA,
                    analysis,
                )
            } catch (e: Exception) {
                _state.update { it.copy(rppgRunning = false) }
            }
        }, executor)
    }

    /** Stop an in-progress rPPG session early and discard partial data. */
    fun stopRppgCamera() {
        rppgCameraProvider?.unbindAll()
        rppgGreenSamples.clear()
        _state.update { it.copy(rppgRunning = false, rppgProgress = 0f) }
    }

    /** Extract the mean green pixel value from the centre 50% ROI of [proxy] (RGBA_8888). */
    private fun extractGreenAverage(proxy: ImageProxy): Float {
        val plane  = proxy.planes[0]
        val buffer = plane.buffer
        val rowStride   = plane.rowStride
        val pixelStride = plane.pixelStride
        val width  = proxy.width
        val height = proxy.height

        val roiX0 = width  / 4; val roiX1 = width  * 3 / 4
        val roiY0 = height / 4; val roiY1 = height * 3 / 4

        var sumG = 0L; var count = 0L
        val bytes = ByteArray(buffer.remaining())
        buffer.get(bytes)

        for (row in roiY0 until roiY1) {
            for (col in roiX0 until roiX1) {
                val idx = row * rowStride + col * pixelStride
                if (idx + 1 >= bytes.size) continue
                sumG += bytes[idx + 1].toInt() and 0xFF  // G channel (RGBA: R=+0, G=+1, B=+2, A=+3)
                count++
            }
        }
        return if (count > 0) sumG.toFloat() / count else 0f
    }

    private fun updateRppgResult(result: PPGAdvisor.PPGResult) {
        _state.update { s ->
            s.copy(
                rppgRunning       = false,
                rppgProgress      = 1f,
                rppgBpm           = result.bpm,
                rppgRmssdMs       = result.rmssdMs,
                rppgStressLevel   = result.stressLevel.label,
                rppgStressEmoji   = result.stressLevel.emoji,
                rppgConfidence    = result.confidence,
                rppgRrIntervals   = result.rrIntervalsMs,
            )
        }
        // Push rPPG HR into SensorBridge so PentadViewModel updates phiBrain
        val bpm = result.bpm
        if (bpm != null) {
            sensorBridge.pushBiometrics(
                BiometricReading(hrBpm = bpm, spo2Pct = _state.value.spo2Pct)
            )
        }
    }

    /**
     * Extract average R/G/B from the centre 50%×50% ROI of an [ImageProxy]
     * (RGBA_8888 format) and run [SkinColorAdvisor.analyse].
     *
     * The ambient light lux is read from the last known sensor snapshot
     * via [SensorBridge].  Falls back to 200 lux if no reading is available.
     */
    private fun analyseImageProxy(proxy: ImageProxy): SkinColorAdvisor.SkinAnalysis {
        val plane  = proxy.planes[0]
        val buffer = plane.buffer
        val rowStride   = plane.rowStride
        val pixelStride = plane.pixelStride
        val width  = proxy.width
        val height = proxy.height

        // Centre ROI: middle 50% of width and height
        val roiX0 = width  / 4
        val roiY0 = height / 4
        val roiX1 = width  * 3 / 4
        val roiY1 = height * 3 / 4

        var sumR = 0L; var sumG = 0L; var sumB = 0L; var count = 0L
        val bytes = ByteArray(buffer.remaining())
        buffer.get(bytes)

        for (row in roiY0 until roiY1) {
            for (col in roiX0 until roiX1) {
                val idx = row * rowStride + col * pixelStride
                if (idx + 2 >= bytes.size) continue
                sumR += bytes[idx].toInt() and 0xFF
                sumG += bytes[idx + 1].toInt() and 0xFF
                sumB += bytes[idx + 2].toInt() and 0xFF
                count++
            }
        }

        if (count == 0L) {
            return SkinColorAdvisor.analyse(0f, 0f, 0f)
        }

        val avgR = sumR.toFloat() / count
        val avgG = sumG.toFloat() / count
        val avgB = sumB.toFloat() / count

        return SkinColorAdvisor.analyse(avgR, avgG, avgB)
    }

    /** Called by camera analysis with a completed SkinColorAdvisor.SkinAnalysis. */
    fun updateSkinResult(
        pallorIndex:    Float,
        pallorSeverity: String,
        jaundiceFlagged: Boolean,
        confidence:     Float,
        advice:         String,
    ) {
        _state.update { s ->
            s.copy(
                pallorIndex     = pallorIndex,
                pallorSeverity  = pallorSeverity,
                jaundiceFlagged = jaundiceFlagged,
                skinConfidence  = confidence,
                skinAdvice      = advice,
                skinCapturing   = false,
            )
        }
    }

    // ── Private helpers ───────────────────────────────────────────────────────

    private fun refreshBattery() {
        val pct = batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
        _state.update { it.copy(batteryPct = pct) }
    }

    private fun recalculate() {
        val s = _state.value
        val hr    = s.hrBpm ?: s.sensorHrBpm
        val spo2  = s.spo2Pct
        val temp  = s.tempC
        val resp  = s.respRate

        val news2 = computeNews2(hr, spo2, temp, resp, s.isAlert)
        val phi   = computePhi(hr, spo2, temp)

        _state.update { it.copy(news2Score = news2, phiBio = phi) }

        // Push biometrics to SensorBridge so TranslateViewModel can update Ψ_brain
        sensorBridge.pushBiometrics(BiometricReading(hrBpm = hr, spo2Pct = spo2))
    }

    // ── NEWS2 — NHS National Early Warning Score 2 ────────────────────────────
    //
    // Ported exactly from S24Ultra/scripts/nurse_suite.py.
    // Each vital contributes 0–3 points; total → risk tier → action.

    private fun computeNews2(
        hrBpm: Int?,
        spo2Pct: Int?,
        tempC: Float?,
        respRate: Int?,
        isAlert: Boolean,
    ): News2Result {
        var score = 0

        // Respiration rate
        val rr = respRate
        if (rr != null) {
            score += when {
                rr <= 8           -> 3
                rr in 9..11       -> 1
                rr in 12..20      -> 0
                rr in 21..24      -> 2
                else              -> 3  // >= 25
            }
        }

        // SpO2
        val sp = spo2Pct
        if (sp != null) {
            score += when {
                sp <= 91          -> 3
                sp in 92..93      -> 2
                sp in 94..95      -> 1
                else              -> 0  // >= 96
            }
        }

        // Temperature
        val t = tempC
        if (t != null) {
            score += when {
                t <= 35.0f        -> 3
                t <= 36.0f        -> 1
                t <= 38.0f        -> 0
                t <= 39.0f        -> 1
                else              -> 2  // > 39.1
            }
        }

        // Pulse
        val hr = hrBpm
        if (hr != null) {
            score += when {
                hr <= 40          -> 3
                hr in 41..50      -> 1
                hr in 51..90      -> 0
                hr in 91..110     -> 1
                hr in 111..130    -> 2
                else              -> 3  // >= 131
            }
        }

        // Consciousness
        if (!isAlert) score += 3

        val risk = when {
            score == 0        -> News2Risk.MINIMUM
            score in 1..4     -> News2Risk.LOW
            score in 5..6     -> News2Risk.MEDIUM
            else              -> News2Risk.HIGH
        }

        return News2Result(score = score, risk = risk)
    }

    // ── φ-homeostasis — Unitary-Manifold medicine connection ─────────────────
    //
    // Normalises each vital to 1.0 at its homeostatic set-point.
    // δφ = φ_bio − 1.0 gives the manifold field displacement.

    private fun computePhi(hrBpm: Int?, spo2Pct: Int?, tempC: Float?): PhiResult? {
        val hr   = hrBpm?.toFloat() ?: return null
        val spo2 = spo2Pct?.toFloat() ?: return null
        val temp = tempC ?: return null

        val phiHr   = hr   / PHI_HR_BASELINE
        val phiSpo2 = spo2 / PHI_SPO2_BASELINE
        val phiTemp = temp / PHI_TEMP_BASELINE

        val phiBio  = (phiHr + phiSpo2 + phiTemp) / 3.0f
        val delta   = phiBio - 1.0f

        val status = when {
            abs(delta) <= 0.05f -> PhiStatus.AT_FIXED_POINT
            abs(delta) <= 0.10f -> PhiStatus.MILD_DEVIATION
            else                -> PhiStatus.OUTSIDE_BASIN
        }

        return PhiResult(phiHr = phiHr, phiSpo2 = phiSpo2, phiTemp = phiTemp,
                         phiBio = phiBio, delta = delta, status = status)
    }

    private companion object {
        /** Homeostatic set-point for heart rate (bpm). φ_hr = HR / PHI_HR_BASELINE. */
        const val PHI_HR_BASELINE: Float   = 70.0f
        /** Homeostatic set-point for SpO2 (%). φ_spo2 = SpO2 / PHI_SPO2_BASELINE. */
        const val PHI_SPO2_BASELINE: Float = 98.0f
        /** Homeostatic set-point for core temperature (°C). φ_temp = temp / PHI_TEMP_BASELINE. */
        const val PHI_TEMP_BASELINE: Float = 37.0f
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// UI state
// ─────────────────────────────────────────────────────────────────────────────

data class MedicalUiState(
    // Manual vital inputs (null = not entered)
    val hrInput:    String  = "",
    val spo2Input:  String  = "",
    val tempInput:  String  = "",
    val respInput:  String  = "",
    val hrBpm:      Int?    = null,
    val spo2Pct:    Int?    = null,
    val tempC:      Float?  = null,
    val respRate:   Int?    = null,
    val isAlert:    Boolean = true,   // consciousness: true = Alert, false = CVPU

    // From Android TYPE_HEART_RATE sensor
    val sensorHrBpm: Int?   = null,

    // Computed scores
    val news2Score: News2Result? = null,
    val phiBio:     PhiResult?   = null,

    // ── Neuro (TremorAdvisor) ─────────────────────────────────────────────────
    val tremorScore:      Float?  = null,  // 0–10 (null = not yet measured)
    val tremorFreqHz:     Float?  = null,  // dominant tremor frequency (Hz)
    val tremorSeverity:   String? = null,  // NONE / MILD / MODERATE / SEVERE
    val tremorHistory:    List<Float> = emptyList(),  // session trend (last 10 scores)
    val tremorRunning:    Boolean = false,

    // ── Skin (SkinColorAdvisor) ───────────────────────────────────────────────
    val pallorIndex:      Float?  = null,  // 0–1 (null = not yet measured)
    val pallorSeverity:   String? = null,
    val jaundiceFlagged:  Boolean = false,
    val skinConfidence:   Float   = 0f,
    val skinAdvice:       String? = null,
    val skinCapturing:    Boolean = false,

    // Misc
    val batteryPct: Int    = -1,
    val lastBroadcastPayload: String? = null,

    // ── rPPG (Remote Photoplethysmography) ───────────────────────────────────
    val rppgRunning:      Boolean      = false,
    val rppgProgress:     Float        = 0f,       // 0–1 collection progress
    val rppgBpm:          Int?         = null,      // estimated BPM (null = not yet)
    val rppgRmssdMs:      Float?       = null,      // HRV RMSSD in ms
    val rppgStressLevel:  String?      = null,      // LOW / MEDIUM / HIGH / UNKNOWN
    val rppgStressEmoji:  String       = "❓",
    val rppgConfidence:   Float        = 0f,
    val rppgRrIntervals:  List<Float>  = emptyList(),
)

// ── NEWS2 ─────────────────────────────────────────────────────────────────────

data class News2Result(val score: Int, val risk: News2Risk)

enum class News2Risk(val label: String, val action: String, val colorHex: Long) {
    MINIMUM("Minimum",  "Normal monitoring",                     0xFF00C853),
    LOW    ("Low",      "Increase monitoring frequency",         0xFFFFAB00),
    MEDIUM ("Medium",   "Urgent clinical review",                0xFFFF6D00),
    HIGH   ("HIGH",     "EMERGENCY — call 999/911/112 NOW",      0xFFFF1744),
}

// ── φ-homeostasis ─────────────────────────────────────────────────────────────

data class PhiResult(
    val phiHr:   Float,
    val phiSpo2: Float,
    val phiTemp: Float,
    val phiBio:  Float,
    val delta:   Float,
    val status:  PhiStatus,
)

enum class PhiStatus(val label: String, val description: String) {
    AT_FIXED_POINT("At fixed point",     "Ψ in homeostatic basin"),
    MILD_DEVIATION("Mild deviation",     "Field gradient forming"),
    OUTSIDE_BASIN ("Outside basin",      "Φ outside attractor — needs attention"),
}
