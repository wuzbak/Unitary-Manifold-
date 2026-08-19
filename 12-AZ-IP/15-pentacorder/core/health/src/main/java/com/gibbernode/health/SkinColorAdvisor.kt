package com.gibbernode.health

/**
 * SkinColorAdvisor
 *
 * Pure stateless logic for skin-colour-based pallor and jaundice screening
 * from camera RGB pixel averages.  No Android SDK dependency — fully
 * JVM-unit-testable.
 *
 * Algorithm (simplified Rayleigh-inspired skin model):
 *   - Pallor index: deviation of R/(G+B) ratio from a calibrated baseline.
 *     Lower R ratio = reduced haemoglobin → pallor / anaemia indicator.
 *   - Jaundice flag: elevated yellow component — yellow = R + G − B.
 *     Normalised yellow fraction > 0.68 is associated with visible jaundice
 *     (Namba et al., Arch Dis Child 2016; smartphone bilirubin studies).
 *   - Confidence degrades in low-light or non-skin pixels.
 *
 * Calibration:
 *   A "normal" skin baseline (R, G, B) should be captured at first use for
 *   accurate personalised tracking.  Without calibration, population-mean
 *   values are used (Caucasian mid-tone reference, Fitzpatrick scale III).
 *
 * Medical disclaimer:
 *   This is a screening reference tool ONLY — not a certified medical device.
 *   It cannot diagnose anaemia, jaundice, or any medical condition.
 *   For clinical use consult a physician.
 */
object SkinColorAdvisor {

    // ── Reference baseline (population mean — Fitzpatrick scale III) ──────────

    /** Default reference R-fraction for healthy mid-tone skin (Fitzpatrick scale III).
     *  Represents the R-channel fraction (R / (R+G+B)) ≈ 0.45 for warm brown/tan skin.
     *  This is the denominator in the pallor index: pallorIndex = rNorm / baseline.
     *  Values ≈ 1.0 = healthy; < 1.0 = paler than the calibrated baseline.
     *  Users calibrate this to their own skin at first use via [calibrateBaseline].
     */
    const val DEFAULT_PALLOR_BASELINE: Float = 0.45f

    /** Yellow threshold: normalized yellow fraction for jaundice flag. */
    const val JAUNDICE_THRESHOLD: Float = 0.68f

    // ── Result types ─────────────────────────────────────────────────────────

    /**
     * Result of a skin-colour analysis.
     *
     * @param pallorIndex     0–1; < 1 = normal / healthy, lower = more pallor
     * @param pallorSeverity  Clinical severity label
     * @param jaundiceFlagged True when yellow index exceeds [JAUNDICE_THRESHOLD]
     * @param yellowIndex     0–1 normalised yellow-channel contribution
     * @param confidence      0–1 (degrades in low light or non-skin images)
     * @param advice          Plain-English summary
     * @param disclaimer      Mandatory medical disclaimer text
     */
    data class SkinAnalysis(
        val pallorIndex:    Float,
        val pallorSeverity: PallorSeverity,
        val jaundiceFlagged: Boolean,
        val yellowIndex:    Float,
        val confidence:     Float,
        val advice:         String,
        val disclaimer:     String = DISCLAIMER,
    )

    enum class PallorSeverity(val label: String, val emoji: String) {
        NORMAL        ("Normal",               "✅"),
        MILD_PALLOR   ("Mild pallor",          "🟡"),
        MODERATE_PALLOR("Moderate pallor",     "🟠"),
        MARKED_PALLOR ("Marked pallor",        "🔴"),
    }

    // ── Public API ────────────────────────────────────────────────────────────

    /**
     * Analyse skin RGB averages from a camera ROI.
     *
     * @param r          Mean red channel value (0–255).
     * @param g          Mean green channel value (0–255).
     * @param b          Mean blue channel value (0–255).
     * @param baseline   Calibrated normal pallor ratio for this user;
     *                   defaults to [DEFAULT_PALLOR_BASELINE].
     * @param luxReading Ambient lux (used to estimate confidence).
     */
    fun analyse(
        r:        Float,
        g:        Float,
        b:        Float,
        baseline: Float = DEFAULT_PALLOR_BASELINE,
        luxReading: Float = 200f,
    ): SkinAnalysis {
        val total     = (r + g + b).coerceAtLeast(1f)
        val rNorm     = r / total
        val gNorm     = g / total
        val bNorm     = b / total

        // Pallor index: normalised R-fraction relative to the personal baseline.
        // Value ≈ 1.0 = healthy; < 1.0 = paler than baseline (possible pallor).
        val pallorIndex   = (rNorm / baseline.coerceAtLeast(0.001f)).coerceIn(0f, 1.5f)

        // Clamp to 0–1 for classification (1.5 headroom so slight over-baseline
        // doesn't reduce to an artifactually low value after normalisation)
        val pallorClamped = (pallorIndex / 1.5f).coerceIn(0f, 1f)

        // Yellow index: (R + G − B) / total — elevated in jaundice
        val yellowIndex = ((r + g - b) / total).coerceIn(0f, 1f)

        val severity = when {
            pallorClamped >= 0.55f -> PallorSeverity.NORMAL
            pallorClamped >= 0.45f -> PallorSeverity.MILD_PALLOR
            pallorClamped >= 0.33f -> PallorSeverity.MODERATE_PALLOR
            else                   -> PallorSeverity.MARKED_PALLOR
        }

        val jaundiced = yellowIndex >= JAUNDICE_THRESHOLD

        // Confidence: lower in poor light or if pixel values are near-uniform (non-skin)
        val luxConf    = (luxReading / 500f).coerceIn(0.1f, 1f)
        val pixelConf  = when {
            total < 30f  -> 0.1f   // too dark
            total > 700f -> 0.5f   // overexposed
            else         -> 0.9f
        }
        val confidence = (luxConf * pixelConf).coerceIn(0f, 1f)

        val advice = buildAdvice(severity, jaundiced, confidence)

        return SkinAnalysis(
            pallorIndex     = pallorClamped,
            pallorSeverity  = severity,
            jaundiceFlagged = jaundiced,
            yellowIndex     = yellowIndex,
            confidence      = confidence,
            advice          = advice,
        )
    }

    /**
     * Update the personal pallor baseline from a known-healthy reading.
     * Returns the R-fraction (0–1) to store as the new calibration baseline.
     *
     * Use when the user captures a reference frame of their own skin in
     * good lighting conditions.
     */
    fun calibrateBaseline(r: Float, g: Float, b: Float): Float {
        val total = (r + g + b).coerceAtLeast(1f)
        return (r / total)
    }

    // ── Private ───────────────────────────────────────────────────────────────

    private fun buildAdvice(
        severity:   PallorSeverity,
        jaundiced:  Boolean,
        confidence: Float,
    ): String {
        val confNote = if (confidence < 0.5f) " (low confidence — improve lighting)" else ""
        val jaundiceNote = if (jaundiced) " ⚠️ Yellow index elevated — consult doctor" else ""
        return when (severity) {
            PallorSeverity.NORMAL          -> "✅ Normal skin colour$jaundiceNote$confNote"
            PallorSeverity.MILD_PALLOR     -> "🟡 Mild pallor detected$jaundiceNote$confNote"
            PallorSeverity.MODERATE_PALLOR -> "🟠 Moderate pallor — consider medical review$jaundiceNote$confNote"
            PallorSeverity.MARKED_PALLOR   -> "🔴 Marked pallor — seek medical advice$jaundiceNote$confNote"
        }
    }

    const val DISCLAIMER =
        "Screening reference only — not a certified medical device. " +
        "Cannot diagnose anaemia, jaundice, or any medical condition. " +
        "Consult a physician for clinical assessment."
}
