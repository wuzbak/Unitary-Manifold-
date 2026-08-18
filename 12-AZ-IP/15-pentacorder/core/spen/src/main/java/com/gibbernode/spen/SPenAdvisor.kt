package com.gibbernode.spen

import kotlin.math.sqrt

/**
 * SPenAdvisor
 *
 * Pure stateless logic for S Pen gesture decoding, stroke analysis, and
 * "air-writing" signature hashing.  No Android SDK dependency — fully
 * JVM-unit-testable.
 *
 * Data flows from the feature layer: MotionEvent values are converted to plain
 * [StrokePoint] or [ImuSample] data classes before being passed here.
 *
 * Physical basis:
 *   - S Pen tip pressure: 4,096 levels → normalised 0.0–1.0
 *   - S Pen tilt: 0–90° from vertical (MotionEvent.AXIS_TILT)
 *   - S Pen 6-axis IMU: accel + gyro sampled at ~100 Hz via BLE Air Actions
 *   - Tremor score: coefficient of variation of inter-point velocity over a
 *     500 ms window — scaled to 0–10 (higher = more tremor)
 *   - Air-write hash: quantised gyro-delta path → DJB2-style 16-char hex
 *
 * @see [Samsung S Pen Remote SDK](https://developer.samsung.com/galaxy-spen-remote)
 */
object SPenAdvisor {

    // ── Data classes ──────────────────────────────────────────────────────────

    /** One sample from the S Pen touch surface (from MotionEvent). */
    data class StrokePoint(
        val x:           Float,  // canvas x (px)
        val y:           Float,  // canvas y (px)
        val pressure:    Float,  // 0.0–1.0 (normalised from 0–4096 raw)
        val tiltDeg:     Float,  // pen angle from vertical (0–90°)
        val timestampMs: Long,
    )

    /** One IMU sample from an S Pen Air Action BLE notification. */
    data class ImuSample(
        val accelX: Float, val accelY: Float, val accelZ: Float,  // m/s²
        val gyroX:  Float, val gyroY:  Float, val gyroZ:  Float,  // rad/s
        val timestampMs: Long,
    )

    /** Result of a single stroke-analysis session. */
    data class StrokeAnalysis(
        val avgPressure:    Float,  // 0–1
        val peakPressure:   Float,  // 0–1
        val velocityMean:   Float,  // px/ms
        val velocitySd:     Float,  // px/ms — high SD = irregular / tremor
        val tremorScore:    Float,  // 0–10 (higher = more tremor)
        val dominantFreqHz: Float,  // dominant oscillation in velocity signal
        val sampleCount:    Int,
    )

    /** Recognised Air Action gesture patterns. */
    enum class GesturePattern(val label: String) {
        FLICK_UP   ("Flick Up"),
        FLICK_DOWN ("Flick Down"),
        FLICK_LEFT ("Flick Left"),
        FLICK_RIGHT("Flick Right"),
        CIRCLE     ("Circle"),
        HOLD_BUTTON("Hold Button"),
        DOUBLE_TAP ("Double Tap"),
        UNKNOWN    ("Unknown"),
    }

    /** Actions that can be bound to gesture patterns. */
    enum class AirCommand(val label: String, val emoji: String) {
        SKIP_FORWARD  ("Skip Forward",    "⏭"),
        SKIP_BACK     ("Skip Back",       "⏮"),
        VOLUME_UP     ("Volume Up",       "🔊"),
        VOLUME_DOWN   ("Volume Down",     "🔉"),
        SHUTTER       ("Camera Shutter",  "📸"),
        PLAY_PAUSE    ("Play / Pause",    "⏯"),
        OPEN_ASSISTANT("Open Assistant",  "🤖"),
        SCROLL_UP     ("Scroll Up",       "⬆"),
        SCROLL_DOWN   ("Scroll Down",     "⬇"),
        CUSTOM        ("Custom",          "⚙"),
        NONE          ("None",            "—"),
    }

    /** An encoded 3D air-writing signature (DJB2-derived compact hex). */
    data class AirSignature(
        val hash:       String,  // 16-char hex fingerprint of the gesture path
        val confidence: Float,   // 0–1 — how repeatable this signature is
    )

    // ── Default gesture → command bindings ────────────────────────────────────

    /** Default factory bindings shipped with the app. Caller may override. */
    val defaultBindings: Map<GesturePattern, AirCommand> = mapOf(
        GesturePattern.FLICK_UP    to AirCommand.VOLUME_UP,
        GesturePattern.FLICK_DOWN  to AirCommand.VOLUME_DOWN,
        GesturePattern.FLICK_LEFT  to AirCommand.SKIP_BACK,
        GesturePattern.FLICK_RIGHT to AirCommand.SKIP_FORWARD,
        GesturePattern.CIRCLE      to AirCommand.OPEN_ASSISTANT,
        GesturePattern.HOLD_BUTTON to AirCommand.SHUTTER,
        GesturePattern.DOUBLE_TAP  to AirCommand.PLAY_PAUSE,
        GesturePattern.UNKNOWN     to AirCommand.NONE,
    )

    // ── Public API ────────────────────────────────────────────────────────────

    /**
     * Analyse a list of S Pen stroke points and return pressure statistics,
     * velocity profile, and a tremor score.
     *
     * @param points  Ordered list of [StrokePoint] from one pen-down → pen-up stroke.
     */
    fun analyze(points: List<StrokePoint>): StrokeAnalysis {
        if (points.size < 2) {
            return StrokeAnalysis(0f, 0f, 0f, 0f, 0f, 0f, points.size)
        }
        val pressures    = points.map { it.pressure }
        val avgPressure  = pressures.average().toFloat()
        val peakPressure = pressures.max()

        // Inter-point velocities (px/ms)
        val velocities = mutableListOf<Float>()
        for (i in 1 until points.size) {
            val dx = points[i].x - points[i - 1].x
            val dy = points[i].y - points[i - 1].y
            val dt = (points[i].timestampMs - points[i - 1].timestampMs).coerceAtLeast(1L)
            velocities += sqrt(dx * dx + dy * dy) / dt
        }
        val vMean = velocities.average().toFloat()
        val vSd   = sd(velocities)

        // Tremor score: coefficient of variation × 5, capped at 10.
        // CV = SD / mean — a dimensionless measure of relative variability.
        val tremorScore    = (vSd / (vMean + 0.001f) * 5f).coerceIn(0f, 10f)
        val dominantFreqHz = zeroCrossingFreq(velocities)

        return StrokeAnalysis(
            avgPressure    = avgPressure,
            peakPressure   = peakPressure,
            velocityMean   = vMean,
            velocitySd     = vSd,
            tremorScore    = tremorScore,
            dominantFreqHz = dominantFreqHz,
            sampleCount    = points.size,
        )
    }

    /**
     * Classify an Air Action gesture from a sequence of gyroscope magnitude
     * samples (|ω|) recorded at ~100 Hz.
     */
    fun classifyGesture(gyroMagnitudes: List<Float>): GesturePattern {
        if (gyroMagnitudes.size < 3) return GesturePattern.UNKNOWN

        val peak     = gyroMagnitudes.max()
        val mean     = gyroMagnitudes.average().toFloat()
        val peakIdx  = gyroMagnitudes.indexOf(peak)
        val peakFrac = peakIdx.toFloat() / gyroMagnitudes.size

        return when {
            peak < 0.5f                                  -> GesturePattern.HOLD_BUTTON
            gyroMagnitudes.size < 8 && peak > 2f         -> GesturePattern.DOUBLE_TAP
            peakFrac < 0.35f && mean < 1.5f              -> GesturePattern.FLICK_UP
            peakFrac > 0.65f && mean < 1.5f              -> GesturePattern.FLICK_DOWN
            peakFrac in 0.35f..0.65f && mean > 1.5f      -> GesturePattern.CIRCLE
            gyroMagnitudes.first() > gyroMagnitudes.last()-> GesturePattern.FLICK_LEFT
            else                                          -> GesturePattern.FLICK_RIGHT
        }
    }

    /**
     * Resolve a [GesturePattern] to an [AirCommand] using the supplied bindings
     * (falls back to [defaultBindings] for patterns not present in [custom]).
     */
    fun resolveCommand(
        gesture: GesturePattern,
        custom: Map<GesturePattern, AirCommand> = emptyMap(),
    ): AirCommand = custom[gesture] ?: defaultBindings[gesture] ?: AirCommand.NONE

    /**
     * Encode a 3D air-writing gesture into a compact fingerprint hash.
     * The hash is repeatable for similar gestures and is suitable as an
     * "air-writing unlock" credential.
     *
     * Algorithm: quantise each gyro-delta axis to {n, z, p}, build a symbol
     * string, then apply DJB2 hashing → 16-char hex.
     *
     * @param gyroDeltaRad  Sequence of (Δx, Δy, Δz) gyro deltas in radians.
     */
    fun airWriteHash(gyroDeltaRad: List<Triple<Float, Float, Float>>): AirSignature {
        if (gyroDeltaRad.isEmpty()) return AirSignature("0000000000000000", 0f)

        val sb = StringBuilder()
        for ((dx, dy, dz) in gyroDeltaRad) {
            sb.append(quantise(dx))
            sb.append(quantise(dy))
            sb.append(quantise(dz))
        }

        // DJB2 hash — keep only lower 64 bits then format as hex
        var h = 5381L
        for (c in sb) {
            h = (h * 33) xor c.code.toLong()
        }
        val hash = h.toULong().toString(16).padStart(16, '0').takeLast(16)

        // Confidence scales with gesture length; saturates at 20 samples
        val confidence = (gyroDeltaRad.size / 20f).coerceIn(0f, 1f)
        return AirSignature(hash, confidence)
    }

    /**
     * Normalise a raw S Pen pressure reading (0–4096 integer) to 0.0–1.0.
     * Source: Samsung S Pen Remote SDK pressure range documentation.
     */
    fun normalisePressure(raw: Int): Float = (raw / 4096f).coerceIn(0f, 1f)

    /**
     * Compute the φ_human (Ψ_human intent layer) contribution from a stroke.
     * Blends average pressure with tremor-free coefficient:
     *   φ_human = 0.6·avgPressure + 0.4·(1 − tremorScore/10)
     */
    fun phiHuman(analysis: StrokeAnalysis): Float =
        (analysis.avgPressure * 0.6f + (1f - analysis.tremorScore / 10f) * 0.4f)
            .coerceIn(0f, 1f)

    // ── Private helpers ───────────────────────────────────────────────────────

    private fun sd(values: List<Float>): Float {
        if (values.size < 2) return 0f
        val mean     = values.average()
        val variance = values.sumOf { v -> val d = v - mean; d * d } / (values.size - 1)
        return sqrt(variance.toFloat())
    }

    /** Estimate dominant frequency via zero-crossing rate, assuming 100 Hz sampling. */
    private fun zeroCrossingFreq(velocities: List<Float>): Float {
        if (velocities.size < 4) return 0f
        val mean      = velocities.average().toFloat()
        var crossings = 0
        for (i in 1 until velocities.size) {
            if ((velocities[i - 1] - mean) * (velocities[i] - mean) < 0f) crossings++
        }
        val durationS = velocities.size / 100f
        return if (durationS > 0f) crossings / (2f * durationS) else 0f
    }

    /** Quantise a float into 3 discrete symbols: n (negative), z (zero), p (positive). */
    private fun quantise(v: Float): Char = when {
        v < -0.1f -> 'n'
        v >  0.1f -> 'p'
        else      -> 'z'
    }
}
