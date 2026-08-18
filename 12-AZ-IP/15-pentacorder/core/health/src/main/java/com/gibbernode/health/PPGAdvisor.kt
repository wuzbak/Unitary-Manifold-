package com.gibbernode.health

import kotlin.math.abs
import kotlin.math.sqrt

/**
 * PPGAdvisor
 *
 * Pure stateless logic for remote photoplethysmography (rPPG) from camera
 * green-channel averages, heart-rate variability (HRV), and stress index.
 * No Android SDK dependency — fully JVM-unit-testable.
 *
 * Algorithm:
 *   1. Green-channel pixel averages from a face or fingertip ROI are collected
 *      at ~30 Hz (standard CameraX preview frame rate).
 *   2. The signal is detrended (subtract a rolling mean) to remove illumination
 *      drift.
 *   3. Peak detection on the detrended signal identifies inter-beat intervals
 *      (IBIs) in milliseconds.
 *   4. BPM = 60 000 / mean(IBI).
 *   5. HRV (RMSSD) = sqrt(mean((successive_IBI_differences)²)).
 *   6. Stress index: approximation of the LF/HF ratio from RMSSD.
 *
 * Medical disclaimer:
 *   rPPG from a phone camera is NOT a certified medical device.
 *   Results are indicative only — not for clinical use.
 */
object PPGAdvisor {

    // ── Result types ─────────────────────────────────────────────────────────

    /** Heart-rate and HRV result from a rPPG session. */
    data class PPGResult(
        val bpm:           Int?,    // null if insufficient data
        val rmssdMs:       Float?,  // RMSSD in ms (HRV measure); null if < 2 IBIs
        val stressLevel:   StressLevel,
        val confidence:    Float,   // 0–1 (higher = more stable signal)
        val rrIntervalsMs: List<Float>,
        val disclaimer:    String = DISCLAIMER,
    )

    enum class StressLevel(val label: String, val emoji: String) {
        LOW   ("Low — relaxed",         "😌"),
        MEDIUM("Medium — alert",        "😐"),
        HIGH  ("High — elevated stress","😓"),
        UNKNOWN("Insufficient data",    "❓"),
    }

    // ── Public API ────────────────────────────────────────────────────────────

    /**
     * Compute heart rate and HRV from a sequence of green-channel pixel averages.
     *
     * @param greenAvgSamples  Ordered list of mean green pixel values (0–255)
     *                         at [sampleRateHz] frame rate.
     * @param sampleRateHz     Camera preview frame rate (typically 30.0 Hz).
     */
    fun analyse(greenAvgSamples: List<Float>, sampleRateHz: Float = 30f): PPGResult {
        if (greenAvgSamples.size < (sampleRateHz * 3f).toInt()) {
            return PPGResult(null, null, StressLevel.UNKNOWN, 0f, emptyList())
        }

        val detrended   = detrend(greenAvgSamples)
        val peaks       = detectPeaks(detrended, sampleRateHz)
        val rrMs        = computeRR(peaks, sampleRateHz)

        if (rrMs.size < 2) {
            return PPGResult(null, null, StressLevel.UNKNOWN, 0.2f, rrMs)
        }

        val meanRR  = rrMs.average().toFloat()
        val bpm     = (60_000f / meanRR).toInt().coerceIn(30, 220)
        val rmssd   = computeRMSSD(rrMs)
        val stress  = stressFromRMSSD(rmssd)

        // Confidence: more peaks + lower SD of RR = higher confidence
        val rrSd   = sd(rrMs)
        val conf   = ((peaks.size / 8f) * (1f - rrSd / (meanRR + 1f))).coerceIn(0f, 1f)

        return PPGResult(bpm, rmssd, stress, conf, rrMs)
    }

    /**
     * Compute RMSSD (Root Mean Square of Successive Differences) from a list
     * of RR intervals in milliseconds.
     *
     * RMSSD is a standard time-domain HRV metric (Task Force 1996, ESC/NASPE).
     */
    fun computeRMSSD(rrIntervalsMs: List<Float>): Float {
        if (rrIntervalsMs.size < 2) return 0f
        val diffs     = (1 until rrIntervalsMs.size).map { i ->
            val d = rrIntervalsMs[i] - rrIntervalsMs[i - 1]; d * d
        }
        return sqrt(diffs.average().toFloat())
    }

    /**
     * Estimate stress level from RMSSD.
     *
     * Reference ranges: RMSSD > 50 ms = good HRV / low stress (Shaffer & Ginsberg 2017).
     */
    fun stressFromRMSSD(rmssdMs: Float): StressLevel = when {
        rmssdMs >= 50f -> StressLevel.LOW
        rmssdMs >= 20f -> StressLevel.MEDIUM
        rmssdMs >  0f  -> StressLevel.HIGH
        else           -> StressLevel.UNKNOWN
    }

    // ── Private helpers ───────────────────────────────────────────────────────

    /** Remove linear trend by subtracting a centred rolling mean. */
    private fun detrend(signal: List<Float>, windowSize: Int = 15): List<Float> {
        val half   = windowSize / 2
        return signal.mapIndexed { i, v ->
            val lo   = (i - half).coerceAtLeast(0)
            val hi   = (i + half).coerceAtMost(signal.size - 1)
            val mean = signal.subList(lo, hi + 1).average().toFloat()
            v - mean
        }
    }

    /**
     * Detect positive peaks in the detrended signal.
     * A peak is a sample higher than its [minPeakDistance] neighbours and
     * above a noise threshold (0.15 × global amplitude).
     */
    private fun detectPeaks(signal: List<Float>, sampleRateHz: Float): List<Int> {
        val minDist = (sampleRateHz * 0.4f).toInt().coerceAtLeast(3)  // 0.4 s min IBI
        val signalAmplitude = signal.max() - signal.min()             // peak-to-peak range
        val threshold = signal.min() + signalAmplitude * 0.3f

        val peaks = mutableListOf<Int>()
        for (i in minDist until signal.size - minDist) {
            if (signal[i] < threshold) continue
            val isMax = (i - minDist..i + minDist).all { signal[it] <= signal[i] }
            if (isMax) {
                if (peaks.isEmpty() || i - peaks.last() >= minDist) peaks += i
            }
        }
        return peaks
    }

    /** Compute RR intervals (ms) from a list of peak sample indices. */
    private fun computeRR(peaks: List<Int>, sampleRateHz: Float): List<Float> {
        if (peaks.size < 2) return emptyList()
        return (1 until peaks.size).map { i ->
            (peaks[i] - peaks[i - 1]).toFloat() / sampleRateHz * 1000f
        }
    }

    private fun sd(values: List<Float>): Float {
        if (values.size < 2) return 0f
        val mean     = values.average()
        val variance = values.sumOf { v -> val d = v - mean; d * d } / (values.size - 1)
        return sqrt(variance.toFloat())
    }

    const val DISCLAIMER =
        "Reference only — not a certified medical device. For clinical use consult a physician."
}
