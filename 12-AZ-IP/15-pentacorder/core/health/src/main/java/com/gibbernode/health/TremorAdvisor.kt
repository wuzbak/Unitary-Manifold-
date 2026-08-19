package com.gibbernode.health

import kotlin.math.abs
import kotlin.math.sqrt

/**
 * TremorAdvisor
 *
 * Pure stateless logic for S Pen–based tremor screening.
 * No Android SDK dependency — fully JVM-unit-testable.
 *
 * Uses velocity data from S Pen strokes (delivered by SPenAdvisor.analyze()) to
 * compute:
 *   - Tremor score (0–10)
 *   - Dominant tremor frequency (Hz)
 *   - Per-session trend (improving / stable / worsening)
 *
 * Clinical context:
 *   Pathological tremor typically presents at 3–12 Hz (resting 3–6 Hz,
 *   essential 5–12 Hz).  The gyroscope-derived velocity signal approximates
 *   a surface EMG envelope for coarse screening.
 *
 * Medical disclaimer:
 *   This is a screening reference tool ONLY — not a certified medical device.
 *   It cannot diagnose Parkinson's disease or any other neurological condition.
 *   For clinical evaluation consult a neurologist.
 */
object TremorAdvisor {

    // ── Data ──────────────────────────────────────────────────────────────────

    /**
     * Result for a single stroke-based tremor assessment.
     *
     * @param tremorScore       0 (no tremor) – 10 (severe tremor)
     * @param dominantFreqHz    Dominant oscillation frequency in Hz
     * @param severity          Clinical severity label
     * @param confidence        0–1 (higher = more samples, more reliable)
     */
    data class TremorReading(
        val tremorScore:     Float,
        val dominantFreqHz:  Float,
        val severity:        TremorSeverity,
        val confidence:      Float,
        val disclaimer:      String = DISCLAIMER,
    )

    /**
     * Trend across a session (multiple consecutive strokes).
     */
    data class TremorSession(
        val readings:   List<TremorReading>,
        val meanScore:  Float,
        val trend:      TremorTrend,
        val summary:    String,
    )

    enum class TremorSeverity(val label: String, val emoji: String) {
        NONE     ("None — smooth",       "✅"),
        MILD     ("Mild",                "🟡"),
        MODERATE ("Moderate",            "🟠"),
        SEVERE   ("Severe",              "🔴"),
    }

    enum class TremorTrend(val label: String) {
        IMPROVING ("Improving"),
        STABLE    ("Stable"),
        WORSENING ("Worsening"),
        INSUFFICIENT("Insufficient data"),
    }

    // ── Public API ────────────────────────────────────────────────────────────

    /**
     * Compute a tremor reading from a velocity time-series (px/ms).
     *
     * Typically supplied by [SPenAdvisor.analyze] — use the [velocityMean],
     * [velocitySd], and [dominantFreqHz] fields from [SPenAdvisor.StrokeAnalysis].
     *
     * @param velocities      Inter-point velocity samples (px/ms) from one stroke.
     * @param sampleRateHz    Stroke sample rate (default 100 Hz for S Pen).
     */
    fun assess(velocities: List<Float>, sampleRateHz: Float = 100f): TremorReading {
        if (velocities.size < 4) {
            return TremorReading(0f, 0f, TremorSeverity.NONE, 0f)
        }

        val mean  = velocities.average().toFloat()
        val sdVal = sd(velocities)

        // Coefficient of variation as base tremor index (dimensionless)
        val cv    = (sdVal / (mean + 0.001f)).coerceIn(0f, 2f)
        // Scale to 0–10: CV of 0 = 0, CV ≥ 2.0 = 10
        val score = (cv * 5f).coerceIn(0f, 10f)

        val freqHz     = zeroCrossingFreq(velocities, sampleRateHz)
        val severity   = severityFromScore(score)
        val confidence = (velocities.size / 200f).coerceIn(0f, 1f)

        return TremorReading(score, freqHz, severity, confidence)
    }

    /**
     * Aggregate a sequence of [TremorReading]s into a session summary
     * with trend analysis.
     *
     * @param readings  Ordered list of readings (oldest → newest) from one session.
     */
    fun aggregateSession(readings: List<TremorReading>): TremorSession {
        if (readings.isEmpty()) {
            return TremorSession(emptyList(), 0f, TremorTrend.INSUFFICIENT, "No data")
        }
        val meanScore = readings.map { it.tremorScore }.average().toFloat()

        val trend = when {
            readings.size < 3 -> TremorTrend.INSUFFICIENT
            else -> {
                val first  = readings.take(readings.size / 2).map { it.tremorScore }.average()
                val second = readings.drop(readings.size / 2).map { it.tremorScore }.average()
                when {
                    second < first - 0.5  -> TremorTrend.IMPROVING
                    second > first + 0.5  -> TremorTrend.WORSENING
                    else                  -> TremorTrend.STABLE
                }
            }
        }

        val dominant = readings.map { it.dominantFreqHz }.average().toFloat()
        val severity = severityFromScore(meanScore)
        val summary  = buildSummary(meanScore, dominant, severity, trend)

        return TremorSession(readings, meanScore, trend, summary)
    }

    // ── Private helpers ───────────────────────────────────────────────────────

    private fun severityFromScore(score: Float): TremorSeverity = when {
        score < 1.5f -> TremorSeverity.NONE
        score < 4f   -> TremorSeverity.MILD
        score < 7f   -> TremorSeverity.MODERATE
        else         -> TremorSeverity.SEVERE
    }

    private fun buildSummary(
        score:    Float,
        freqHz:   Float,
        severity: TremorSeverity,
        trend:    TremorTrend,
    ): String {
        val freqNote = if (freqHz > 0f) " (dominant %.1f Hz)".format(freqHz) else ""
        return "${severity.emoji} ${severity.label} tremor — score %.1f/10$freqNote — ${trend.label}"
            .format(score)
    }

    private fun sd(values: List<Float>): Float {
        if (values.size < 2) return 0f
        val mean     = values.average()
        val variance = values.sumOf { v -> val d = v - mean; d * d } / (values.size - 1)
        return sqrt(variance.toFloat())
    }

    private fun zeroCrossingFreq(velocities: List<Float>, sampleRateHz: Float): Float {
        if (velocities.size < 4) return 0f
        val mean      = velocities.average().toFloat()
        var crossings = 0
        for (i in 1 until velocities.size) {
            if ((velocities[i - 1] - mean) * (velocities[i] - mean) < 0f) crossings++
        }
        val durationS = velocities.size / sampleRateHz
        return if (durationS > 0f) crossings / (2f * durationS) else 0f
    }

    const val DISCLAIMER =
        "Screening tool only — not a certified medical device. " +
        "Cannot diagnose Parkinson's disease or any neurological condition. " +
        "Consult a neurologist for clinical assessment."
}
