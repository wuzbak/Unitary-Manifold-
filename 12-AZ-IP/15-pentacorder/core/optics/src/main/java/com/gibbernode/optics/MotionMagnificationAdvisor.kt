package com.gibbernode.optics

import kotlin.math.abs
import kotlin.math.cos
import kotlin.math.sin
import kotlin.math.PI
import kotlin.math.sqrt
import kotlin.math.exp

/**
 * MotionMagnificationAdvisor — Eulerian video magnification for sub-visual motion.
 *
 * Physical basis:
 *   The human body produces extremely subtle but real surface deformations with
 *   every heartbeat and breath.  A camera capturing 8K or even 4K video can
 *   detect these as per-pixel colour oscillations at:
 *     - Cardiac frequency: 0.7–3.0 Hz  (42–180 bpm)
 *     - Respiratory frequency: 0.1–0.6 Hz (6–36 breaths/min)
 *
 * Algorithm — Eulerian Motion Magnification (Wu et al., SIGGRAPH 2012):
 *   1. Decompose video into a Laplacian pyramid (spatial frequency bands).
 *   2. For each band, apply a temporal bandpass filter at the target frequency.
 *   3. Amplify the bandpassed signal by a user-chosen factor α.
 *   4. Collapse the pyramid to reconstruct the magnified video.
 *
 * Implementation here is 1D (per-pixel temporal signal) because we operate on
 * pre-extracted colour traces from a fixed skin ROI rather than full video
 * frames (which would require GPU processing).
 *
 * The output can be:
 *   - Pulse rate estimate: dominant frequency in the green channel of a
 *     forehead ROI (rPPG — remote PhotoPlethysmoGraphy).
 *   - Breathing rate: dominant frequency in the abdomen/chest ROI.
 *   - Micro-motion energy: total amplified signal power in a region.
 */
object MotionMagnificationAdvisor {

    // ── Data classes ──────────────────────────────────────────────────────────

    /**
     * A temporal colour trace from a fixed ROI, ready for magnification.
     *
     * @param values     Signal values over time (e.g., mean green channel per frame).
     * @param frameRateHz Capture frame rate in Hz (e.g., 30.0, 60.0, 120.0).
     */
    data class ColourTrace(
        val values:       FloatArray,
        val frameRateHz:  Float,
    ) {
        override fun equals(other: Any?): Boolean =
            other is ColourTrace && values.contentEquals(other.values) && frameRateHz == other.frameRateHz
        override fun hashCode(): Int = 31 * values.contentHashCode() + frameRateHz.hashCode()
    }

    /** Result from analysing one magnified colour trace. */
    data class MagnificationResult(
        val dominantFreqHz:    Float,   // dominant oscillation frequency
        val bpmEstimate:       Float,   // dominant frequency in beats per minute
        val magnifiedTrace:    FloatArray,  // amplified signal
        val signalPower:       Float,   // RMS of the magnified signal (motion energy)
        val snrDb:             Float,   // signal-to-noise estimate (dB)
        val interpretation:    String,  // human-readable label
    ) {
        override fun equals(other: Any?): Boolean =
            other is MagnificationResult &&
            dominantFreqHz == other.dominantFreqHz &&
            magnifiedTrace.contentEquals(other.magnifiedTrace)
        override fun hashCode(): Int =
            31 * dominantFreqHz.hashCode() + magnifiedTrace.contentHashCode()
    }

    // ── Band definitions ─────────────────────────────────────────────────────

    /** Cardiac bandpass: 0.7–3.0 Hz (42–180 bpm). */
    const val CARDIAC_LOW_HZ  = 0.7f
    const val CARDIAC_HIGH_HZ = 3.0f

    /** Respiratory bandpass: 0.1–0.6 Hz. */
    const val RESP_LOW_HZ  = 0.1f
    const val RESP_HIGH_HZ = 0.6f

    /** Default Eulerian magnification factor (α). */
    const val DEFAULT_ALPHA = 15f

    // ── Public API ────────────────────────────────────────────────────────────

    /**
     * Run Eulerian magnification on a colour trace and estimate the dominant
     * oscillation frequency.
     *
     * @param trace      The input [ColourTrace] (typically the mean green channel
     *                   from a forehead or fingertip ROI).
     * @param lowHz      Bandpass lower cutoff in Hz.
     * @param highHz     Bandpass upper cutoff in Hz.
     * @param alpha      Magnification factor (default [DEFAULT_ALPHA]).
     */
    fun magnify(
        trace:  ColourTrace,
        lowHz:  Float = CARDIAC_LOW_HZ,
        highHz: Float = CARDIAC_HIGH_HZ,
        alpha:  Float = DEFAULT_ALPHA,
    ): MagnificationResult {
        val signal = trace.values
        if (signal.size < 8) {
            return MagnificationResult(0f, 0f, FloatArray(0), 0f, Float.NEGATIVE_INFINITY, "Too few frames")
        }

        // 1. Remove DC (mean subtraction)
        val mean       = signal.average().toFloat()
        val centred    = FloatArray(signal.size) { signal[it] - mean }

        // 2. Temporal bandpass via simple IIR Butterworth-inspired filter
        val filtered   = bandpass(centred, trace.frameRateHz, lowHz, highHz)

        // 3. Amplify
        val magnified  = FloatArray(filtered.size) { filtered[it] * alpha }

        // 4. Dominant frequency via DFT zero-crossing rate
        val domFreq    = dominantFrequency(filtered, trace.frameRateHz, lowHz, highHz)
        val bpm        = domFreq * 60f

        // Signal metrics
        val rms        = sqrt(magnified.map { it * it }.average().toFloat())
        val noiseFloor = sqrt(centred.map { it * it }.average().toFloat()).coerceAtLeast(1e-6f)
        val snrDb      = if (noiseFloor > 0f) 20f * (kotlin.math.log10(rms / noiseFloor)).toFloat()
                         else Float.NEGATIVE_INFINITY

        val label = buildLabel(domFreq, lowHz, highHz)

        return MagnificationResult(
            dominantFreqHz = domFreq,
            bpmEstimate    = bpm,
            magnifiedTrace = magnified,
            signalPower    = rms,
            snrDb          = snrDb,
            interpretation = label,
        )
    }

    // ── Private helpers ───────────────────────────────────────────────────────

    /**
     * Simple 1st-order IIR bandpass: apply low-pass then subtract another
     * low-pass (the difference gives a bandpass).
     * α_low  = 1 − exp(−2π × cutoffLow  / fps)
     * α_high = 1 − exp(−2π × cutoffHigh / fps)
     */
    private fun bandpass(signal: FloatArray, fps: Float, low: Float, high: Float): FloatArray {
        val alphaHigh = (1f - exp(-2f * PI.toFloat() * high / fps)).coerceIn(0f, 1f)
        val alphaLow  = (1f - exp(-2f * PI.toFloat() * low  / fps)).coerceIn(0f, 1f)

        // High-pass component
        val hp = FloatArray(signal.size)
        var prevIn = 0f; var prevHp = 0f
        for (i in signal.indices) {
            hp[i] = alphaHigh * (prevHp + signal[i] - prevIn)
            prevIn = signal[i]; prevHp = hp[i]
        }

        // Low-pass component of the high-pass
        val bp = FloatArray(signal.size)
        var prevLp = 0f
        for (i in signal.indices) {
            bp[i] = prevLp + alphaLow * (hp[i] - prevLp)
            prevLp = bp[i]
        }
        return bp
    }

    /** Estimate dominant frequency in a bandpassed signal via DFT bin search. */
    private fun dominantFrequency(
        signal: FloatArray,
        fps: Float,
        low: Float,
        high: Float,
    ): Float {
        val n   = signal.size
        val df  = fps / n
        var maxPow = 0f; var bestFreq = 0f
        val lowBin  = (low  / df).toInt().coerceAtLeast(1)
        val highBin = (high / df).toInt().coerceAtMost(n / 2)
        for (k in lowBin..highBin) {
            var re = 0f; var im = 0f
            for (t in 0 until n) {
                val theta = -2.0 * PI * k * t / n
                re += signal[t] * cos(theta).toFloat()
                im += signal[t] * sin(theta).toFloat()
            }
            val pow = re * re + im * im
            if (pow > maxPow) { maxPow = pow; bestFreq = k * df }
        }
        return bestFreq
    }

    private fun buildLabel(freqHz: Float, low: Float, high: Float): String = when {
        freqHz <= 0f        -> "No dominant oscillation detected"
        low >= RESP_LOW_HZ && high <= RESP_HIGH_HZ ->
            "Breathing: %.1f breaths/min".format(freqHz * 60f)
        low >= CARDIAC_LOW_HZ ->
            "Cardiac: %.0f bpm (%.2f Hz)".format(freqHz * 60f, freqHz)
        else                -> "Oscillation at %.2f Hz (%.0f events/min)".format(freqHz, freqHz * 60f)
    }
}
