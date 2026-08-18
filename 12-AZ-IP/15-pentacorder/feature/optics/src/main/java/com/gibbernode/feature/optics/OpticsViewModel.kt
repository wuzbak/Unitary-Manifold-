package com.gibbernode.feature.optics

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gibbernode.optics.ActiveNIRAdvisor
import com.gibbernode.optics.HyperspectralAdvisor
import com.gibbernode.optics.MotionMagnificationAdvisor
import com.gibbernode.optics.NightModeAdvisor
import com.gibbernode.optics.NLOSAdvisor
import com.gibbernode.optics.SyntheticApertureAdvisor
import com.gibbernode.optics.VisualMicrophoneAdvisor
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject
import kotlin.math.PI
import kotlin.math.sin
import kotlin.random.Random

/**
 * OpticsViewModel — powers the 7-tab Optical Physics Suite screen.
 *
 * Each tab corresponds to one of the camera-physics advisors in core:optics:
 *   Tab 0 — 👁️ NLOS          — NLOSAdvisor            (Non-Line-of-Sight scatter)
 *   Tab 1 — 🌈 Hyperspectral  — HyperspectralAdvisor   (NIR / dark-frame / red-edge)
 *   Tab 2 — 💓 Motion Mag    — MotionMagnificationAdvisor (Eulerian pulse/breathing)
 *   Tab 3 — 🎙️ Visual Mic    — VisualMicrophoneAdvisor (micro-vibration → audio)
 *   Tab 4 — 📸 Synth Aperture — SyntheticApertureAdvisor (gyro burst → virtual lens)
 *   Tab 5 — 🌑 Night Mode    — NightModeAdvisor        (16-in-1 binning + AI fusion)
 *   Tab 6 — 🔦 Active NIR    — ActiveNIRAdvisor        (850/940nm + CLAHE + thermal)
 *
 * Demo mode: each "Run" call executes the advisor on synthetic/demo data so the
 * screen is usable without a live camera session.  Real camera integration
 * (CameraX ImageAnalysis → OpticsViewModel) is a follow-up pipeline task.
 */
@HiltViewModel
class OpticsViewModel @Inject constructor() : ViewModel() {

    private val _state = MutableStateFlow(OpticsUiState())
    val state: StateFlow<OpticsUiState> = _state.asStateFlow()

    // ── Tab 0 — NLOS ─────────────────────────────────────────────────────────

    fun runNlos() {
        viewModelScope.launch {
            _state.update { it.copy(nlosRunning = true) }
            // Demo: synthetic scatter map with one echo at the centre
            val frame = FloatArray(25 * 25) { 0f }
            frame[312] = 0.82f    // bright echo near centre
            frame[287] = 0.41f
            val result = NLOSAdvisor.reconstruct(
                diffMaps   = List(8) { frame },
                frameWidth = 25, frameHeight = 25,
                tofPhaseLagS = 20e-9f,
            )
            _state.update { it.copy(nlosRunning = false, nlosResult = result) }
        }
    }

    // ── Tab 1 — Hyperspectral ─────────────────────────────────────────────────

    fun runHyperspectral() {
        viewModelScope.launch {
            _state.update { it.copy(hyperRunning = true) }
            // Demo: simulate a moderately stressed plant ROI
            val pixels = List(64) { i ->
                val t = i / 64f
                floatArrayOf(0.45f + t * 0.15f, 0.38f, 0.08f)
            }
            val darkFrame = List(64) { floatArrayOf(0.04f, 0.03f, 0.02f) }
            val result = HyperspectralAdvisor.analyse(pixels, darkFrame)
            _state.update { it.copy(hyperRunning = false, hyperResult = result) }
        }
    }

    // ── Tab 2 — Motion Magnification ─────────────────────────────────────────

    fun runMotionMag() {
        viewModelScope.launch {
            _state.update { it.copy(motionRunning = true) }
            // Demo: synthesise a 1.1 Hz (66 bpm) cardiac signal in the green channel
            val fps = 30f; val n = 300
            val vals = FloatArray(n) { t ->
                0.018f * sin(2f * PI.toFloat() * 1.1f * t / fps) +
                0.005f * sin(2f * PI.toFloat() * 0.25f * t / fps) + // breathing component
                (Random.nextFloat() - 0.5f) * 0.003f            // noise
            }
            val trace  = MotionMagnificationAdvisor.ColourTrace(vals, fps)
            val cardiac = MotionMagnificationAdvisor.magnify(
                trace,
                lowHz  = MotionMagnificationAdvisor.CARDIAC_LOW_HZ,
                highHz = MotionMagnificationAdvisor.CARDIAC_HIGH_HZ,
            )
            val breath = MotionMagnificationAdvisor.magnify(
                trace,
                lowHz  = MotionMagnificationAdvisor.RESP_LOW_HZ,
                highHz = MotionMagnificationAdvisor.RESP_HIGH_HZ,
            )
            _state.update { it.copy(
                motionRunning   = false,
                motionCardiac   = cardiac,
                motionBreathing = breath,
            ) }
        }
    }

    // ── Tab 3 — Visual Microphone ─────────────────────────────────────────────

    fun runVisualMic() {
        viewModelScope.launch {
            _state.update { it.copy(visualMicRunning = true) }
            // Demo: 400 Hz vibration trace (within 960 fps Nyquist = 480 Hz)
            val fps = 960f; val n = 960
            val disp = FloatArray(n) { t ->
                0.08f * sin(2f * PI.toFloat() * 400f * t / fps) +
                0.03f * sin(2f * PI.toFloat() * 200f * t / fps) +
                (Random.nextFloat() - 0.5f) * 0.01f
            }
            val trace  = VisualMicrophoneAdvisor.VibrationTrace(disp, fps)
            val result = VisualMicrophoneAdvisor.reconstruct(trace)
            _state.update { it.copy(visualMicRunning = false, visualMicResult = result) }
        }
    }

    // ── Tab 4 — Synthetic Aperture ────────────────────────────────────────────

    fun runSynthAperture() {
        viewModelScope.launch {
            _state.update { it.copy(synthRunning = true) }
            // Demo: 100 ms burst pan with modest gyro (slow deliberate sweep)
            val samples = List(100) { i ->
                SyntheticApertureAdvisor.ImuSample(
                    gyroX = 0.003f, gyroY = 0f, gyroZ = 0.008f,
                    timestampMs = i * 10L,
                )
            }
            val result = SyntheticApertureAdvisor.compute(
                imuSamples        = samples,
                captureIntervalMs = 100f,
                frameCount        = 10,
                subjectDepthM     = 3f,
                backgroundDepthM  = 15f,
            )
            _state.update { it.copy(synthRunning = false, synthResult = result) }
        }
    }

    // ── Tab 5 — Night Mode ────────────────────────────────────────────────────

    fun runNightMode() {
        viewModelScope.launch {
            _state.update { it.copy(nightRunning = true) }
            // Demo: low-light 15-frame burst at ISO 3200, 1-lux scene
            val frames = List(15) { i ->
                NightModeAdvisor.FrameSample(
                    r = 0.04f + i * 0.001f,
                    g = 0.032f + i * 0.0008f,
                    b = 0.025f + i * 0.0005f,
                    iso = 3200, exposureMs = 150f,
                )
            }
            val oisTrace = NightModeAdvisor.OisTrace(FloatArray(150) { 0.015f }, 100f)
            val result = NightModeAdvisor.analyse(frames, sceneLux = 1f, oisTrace = oisTrace)
            _state.update { it.copy(nightRunning = false, nightResult = result) }
        }
    }

    // ── Tab 6 — Active NIR ────────────────────────────────────────────────────

    fun runActiveNir(wavelengthNm: Int = 850) {
        viewModelScope.launch {
            _state.update { it.copy(nirRunning = true) }
            val irResult  = ActiveNIRAdvisor.irCutTransmittance(wavelengthNm)
            val camera2   = ActiveNIRAdvisor.recommendCamera2Params(
                illuminatorWavelengthNm = wavelengthNm,
                sceneLux  = 0f,
                useRawCapture = true,
            )
            val thermal   = ActiveNIRAdvisor.checkThermalSafety(32f) // demo: cool device

            // Demo: synthetic dark-frame + CLAHE
            val rawImage  = FloatArray(64) { it / 64f * 0.12f }  // very dark
            val denoised  = ActiveNIRAdvisor.temporalDenoise(
                List(8) { FloatArray(64) { i -> rawImage[i] + (Random.nextFloat() - 0.5f) * 0.03f } }
            )
            val claheOut  = ActiveNIRAdvisor.clahe(denoised, 8, 8)

            _state.update { it.copy(
                nirRunning   = false,
                nirIrResult  = irResult,
                nirCamera2   = camera2,
                nirThermal   = thermal,
                nirClaheGain = if (rawImage.average() > 0.001)
                    (claheOut.average() / rawImage.average()).toFloat() else 0f,
            ) }
        }
    }

    // ── Tab 7 — Ultra Dark / Zero-Lux ────────────────────────────────────────

    fun runUltraDark() {
        viewModelScope.launch {
            _state.update { it.copy(ultraDarkRunning = true) }
            // Simulate a zero-lux (< 0.01 lux) scene: 30-frame stack at ISO 12800 + max binning
            val frames = List(30) { i ->
                NightModeAdvisor.FrameSample(
                    r = 0.002f + i * 0.0002f,
                    g = 0.0015f + i * 0.00015f,
                    b = 0.001f + i * 0.0001f,
                    iso = 12800, exposureMs = 4000f,
                )
            }
            val oisTrace = NightModeAdvisor.OisTrace(FloatArray(300) { 0.022f }, 100f)
            val result = NightModeAdvisor.analyse(frames, sceneLux = 0.005f, oisTrace = oisTrace)
            _state.update { it.copy(ultraDarkRunning = false, ultraDarkResult = result) }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// UI State
// ─────────────────────────────────────────────────────────────────────────────

data class OpticsUiState(
    // NLOS
    val nlosRunning: Boolean = false,
    val nlosResult:  NLOSAdvisor.NLOSResult? = null,

    // Hyperspectral
    val hyperRunning: Boolean = false,
    val hyperResult:  HyperspectralAdvisor.SpectralResult? = null,

    // Motion Magnification
    val motionRunning:   Boolean = false,
    val motionCardiac:   MotionMagnificationAdvisor.MagnificationResult? = null,
    val motionBreathing: MotionMagnificationAdvisor.MagnificationResult? = null,

    // Visual Microphone
    val visualMicRunning: Boolean = false,
    val visualMicResult:  VisualMicrophoneAdvisor.AcousticReconResult? = null,

    // Synthetic Aperture
    val synthRunning: Boolean = false,
    val synthResult:  SyntheticApertureAdvisor.ApertureResult? = null,

    // Night Mode
    val nightRunning: Boolean = false,
    val nightResult:  NightModeAdvisor.NightModeResult? = null,

    // Active NIR
    val nirRunning:   Boolean = false,
    val nirIrResult:  ActiveNIRAdvisor.IrCutResult? = null,
    val nirCamera2:   ActiveNIRAdvisor.Camera2Params? = null,
    val nirThermal:   ActiveNIRAdvisor.ThermalSafetyResult? = null,
    val nirClaheGain: Float = 0f,

    // Ultra Dark / Zero-Lux
    val ultraDarkRunning: Boolean = false,
    val ultraDarkResult:  NightModeAdvisor.NightModeResult? = null,
)
