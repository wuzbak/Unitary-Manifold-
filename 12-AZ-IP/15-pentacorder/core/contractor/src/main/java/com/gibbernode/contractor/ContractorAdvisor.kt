package com.gibbernode.contractor

import kotlin.math.abs
import kotlin.math.exp
import kotlin.math.ln

/**
 * ContractorAdvisor
 *
 * Pure stateless logic for acoustic-tap material classification, barometric
 * precision levelling, and document-forensics guidance.
 * No Android SDK dependency — fully JVM-unit-testable.
 *
 * Physical basis:
 *   - Acoustic impedance: Z = ρ·c (density × sound speed).
 *     Hard surfaces return energy quickly (fast rise, fast decay).
 *     Hollow or damped surfaces show slow decay and lower peak.
 *   - Decay constant λ: amplitude ~ A·e^(−λ·t).  Fit exponential to the
 *     post-peak tail of the accelerometer signal after an S Pen tap.
 *   - Barometric level: Δhpa / 0.12 → Δm (ISA near sea level).
 *
 * Input:  accelerometer magnitude samples (m/s²) at ~200 Hz after a tap.
 * Output: [SurfaceMaterial] classification + confidence.
 *
 * This is a Kotlin port of the tap-test logic in
 * S24Ultra/scripts/surface_scan.py — see that file for Python reference.
 */
object ContractorAdvisor {

    // ── Surface Material ──────────────────────────────────────────────────────

    /**
     * Classified surface material from acoustic tap rebound.
     *
     * λ = exponential decay constant of the post-tap accelerometer envelope:
     *   HARD_CONCRETE  — fast rise, very fast decay (λ > 40 /s)
     *   DENSE_TILE     — fast rise, fast decay     (λ 20–40 /s)
     *   DRYWALL        — moderate rise, slow decay  (λ 8–20 /s)
     *   HOLLOW         — low peak, very slow decay  (λ < 8 /s)
     *   WOOD           — medium peak, medium decay  (λ 15–30 /s, peak ≈ 2–5 g)
     */
    enum class SurfaceMaterial(
        val label:     String,
        val emoji:     String,
        val hardness:  Float,   // 0–100 relative hardness
    ) {
        HARD_CONCRETE("Hard concrete / stone", "🪨", 95f),
        DENSE_TILE   ("Dense tile / masonry",  "🏗", 75f),
        WOOD         ("Wood stud / timber",    "🪵", 55f),
        DRYWALL      ("Drywall / plasterboard","🧱", 30f),
        HOLLOW       ("Hollow / air gap",      "🌬", 5f),
        UNKNOWN      ("Unknown material",      "❓", 0f),
    }

    /** Result of a single tap-test assessment. */
    data class TapResult(
        val material:     SurfaceMaterial,
        val decayConst:   Float,    // fitted λ (1/s)
        val peakAccelG:   Float,    // peak acceleration in units of g (9.81 m/s²)
        val confidence:   Float,    // 0–1
        val hardnessEstimate: Float,// 0–100
    )

    /** Precision level result (barometric method). */
    data class LevelResult(
        val deltaHpa:        Float,   // pressure difference
        val heightDiffMm:    Float,   // estimated height difference (mm)
        val isLevel:         Boolean, // true if within ±5 mm
        val levelDirection:  String,  // "Point A is higher" / "Level" / "Point B is higher"
    )

    // ── Public API ────────────────────────────────────────────────────────────

    /**
     * Classify a surface from a post-tap accelerometer magnitude time-series.
     *
     * @param samples       Accelerometer |a| samples (m/s²) starting from tap event.
     *                      Typically 40–200 samples at 200 Hz.
     * @param sampleRateHz  Sensor sample rate.
     */
    fun classifyTap(samples: List<Float>, sampleRateHz: Float = 200f): TapResult {
        if (samples.size < 4) {
            return TapResult(SurfaceMaterial.UNKNOWN, 0f, 0f, 0f, 0f)
        }
        val peakIdx     = samples.indexOf(samples.max())
        val peakAccelMs = samples[peakIdx]
        val peakAccelG  = peakAccelMs / 9.81f

        // Fit exponential decay to post-peak tail
        val tail = samples.drop(peakIdx + 1).take(40).map { it.coerceAtLeast(0.01f) }
        val lambda = fitDecayLambda(tail, sampleRateHz)

        val (material, confidence) = classifyByLambdaAndPeak(lambda, peakAccelG)
        return TapResult(
            material         = material,
            decayConst       = lambda,
            peakAccelG       = peakAccelG,
            confidence       = confidence,
            hardnessEstimate = material.hardness,
        )
    }

    /**
     * Compute precision height difference between two barometer readings.
     *
     * Uses the ISA hypsometric formula: Δalt ≈ Δhpa / 0.12 m/hPa.
     *
     * @param pressureAHpa  Pressure at reference point A (hPa).
     * @param pressureBHpa  Pressure at measurement point B (hPa).
     * @param levelToleranceMm  Max height difference to be considered "level" (default 5 mm).
     */
    fun levelCheck(
        pressureAHpa:      Float,
        pressureBHpa:      Float,
        levelToleranceMm:  Float = 5f,
    ): LevelResult {
        val deltaHpa     = pressureAHpa - pressureBHpa
        val heightDiffM  = deltaHpa / 0.12f
        val heightDiffMm = heightDiffM * 1000f

        val isLevel     = abs(heightDiffMm) <= levelToleranceMm
        val direction   = when {
            isLevel             -> "Level ✅"
            heightDiffMm > 0f   -> "Point A is higher by %.1f mm".format(abs(heightDiffMm))
            else                -> "Point B is higher by %.1f mm".format(abs(heightDiffMm))
        }
        return LevelResult(deltaHpa, heightDiffMm, isLevel, direction)
    }

    /**
     * Compute the acoustic hardness estimate (0–100) directly from the decay
     * constant.  Fast decay = hard material.
     */
    fun hardnessFromDecay(lambdaPerSec: Float): Float = when {
        lambdaPerSec > 40f -> 90f + (lambdaPerSec - 40f).coerceAtMost(10f)
        lambdaPerSec > 20f -> 65f + (lambdaPerSec - 20f) / 20f * 25f
        lambdaPerSec > 8f  -> 25f + (lambdaPerSec - 8f) / 12f * 40f
        else               -> (lambdaPerSec / 8f * 25f).coerceIn(0f, 25f)
    }.coerceIn(0f, 100f)

    /**
     * Provide a doc-forensics zoom guidance message for the 200 MP camera.
     *
     * @param currentZoom  Current optical zoom level (1 = 1×, 5 = 5× periscope).
     */
    fun docForensicsGuidance(currentZoom: Float): String = when {
        currentZoom < 2f  -> "📸 Increase zoom to 3–5× for micro-print visibility"
        currentZoom < 3f  -> "🔍 Try 5× periscope for fibre / watermark detail"
        currentZoom >= 5f -> "✅ 5× telephoto active — capture RAW for maximum detail"
        else              -> "📐 Zoom at ${currentZoom}× — tap on suspect area to focus"
    }

    // ── Private helpers ───────────────────────────────────────────────────────

    /**
     * Fit an exponential decay λ to a post-peak tail using log-linear regression.
     *  ln(a_i) = ln(A₀) − λ·t_i  →  least-squares slope = −λ
     */
    private fun fitDecayLambda(tail: List<Float>, sampleRateHz: Float): Float {
        if (tail.size < 3) return 0f
        val dt   = 1f / sampleRateHz
        val lnVals = tail.mapIndexed { i, v -> i * dt to ln(v) }
        // Simple slope via first/last point (robust enough for classification)
        val tFirst  = lnVals.first().first
        val tLast   = lnVals.last().first
        val vFirst  = lnVals.first().second
        val vLast   = lnVals.last().second
        val slope   = if (tLast > tFirst) (vLast - vFirst) / (tLast - tFirst) else 0f
        return (-slope).coerceAtLeast(0f)
    }

    private fun classifyByLambdaAndPeak(
        lambda:     Float,
        peakG:      Float,
    ): Pair<SurfaceMaterial, Float> = when {
        lambda > 40f && peakG > 5f  -> SurfaceMaterial.HARD_CONCRETE to 0.85f
        lambda > 20f && peakG > 3f  -> SurfaceMaterial.DENSE_TILE    to 0.80f
        lambda in 15f..30f          -> SurfaceMaterial.WOOD          to 0.70f
        lambda in 8f..20f           -> SurfaceMaterial.DRYWALL       to 0.70f
        lambda < 8f                 -> SurfaceMaterial.HOLLOW        to 0.75f
        else                        -> SurfaceMaterial.UNKNOWN       to 0.40f
    }
}
