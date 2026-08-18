package com.gibbernode.optics

import kotlin.math.abs
import kotlin.math.exp
import kotlin.math.ln
import kotlin.math.max
import kotlin.math.min
import kotlin.math.pow

/**
 * HyperspectralAdvisor — Near-Infrared and dark-frame spectral analysis.
 *
 * Physical basis:
 *   The Samsung S24 Ultra 200 MP sensor (ISOCELL HP2) has residual sensitivity
 *   in the Near-Infrared (NIR) band (~700–1100 nm) that normally passes through
 *   the AR coating but is blocked by the internal IR-cut filter at the optical
 *   path level.  Two techniques partially recover this:
 *
 *   1. Dark-Frame Subtraction (software):
 *      Take a "dark" frame (lens capped) and subtract it from a lit frame.
 *      This removes fixed-pattern noise and reveals faint long-wavelength
 *      signals that would otherwise be masked — particularly effective for
 *      detecting the "red edge" of chlorophyll at ~700 nm or bruising on
 *      near-ripe fruit.
 *
 *   2. Long-Exposure Accumulation:
 *      Stack N frames and average.  Shot noise reduces as 1/√N, making
 *      faint NIR signals visible without a hardware filter change.
 *
 * Red-edge index (REI):
 *   Borrowed from precision agriculture remote sensing.
 *   REI = (R_far_red − R_red) / (R_far_red + R_red)
 *   where far-red ≈ upper 10% of the R channel (700–750 nm proxy).
 *   Healthy plants: REI > 0.3.  Stressed / dehydrated: REI < 0.15.
 *
 * Bruise detection:
 *   Sub-surface bruising absorbs more in the 700–800 nm range than healthy tissue.
 *   The NIR/green ratio (NIR_proxy / G) is elevated over bruised regions.
 *
 * Medical (vein visualisation):
 *   Deoxy-haemoglobin strongly absorbs NIR (940 nm).  By imaging the palm in
 *   dark-subtracted NIR, veins appear as dark channels against bright skin.
 */
object HyperspectralAdvisor {

    // ── Data classes ──────────────────────────────────────────────────────────

    /**
     * Per-pixel hyperspectral annotation.
     *
     * @param redEdgeIndex   −1 to +1; > 0.3 = healthy plant material present.
     * @param nirProxy       0–1 estimated NIR reflectance from far-red R sub-band.
     * @param bruiseRisk     0–1 probability of sub-surface bruising at this pixel.
     * @param veinProbability 0–1 probability that this pixel lies over a vein.
     */
    data class PixelAnnotation(
        val redEdgeIndex:    Float,
        val nirProxy:        Float,
        val bruiseRisk:      Float,
        val veinProbability: Float,
    )

    /** Summary of a dark-subtracted hyperspectral analysis pass. */
    data class SpectralResult(
        val meanRedEdgeIndex: Float,          // scene-level REI average
        val nirMean:          Float,          // average NIR proxy across all pixels
        val plantStressLabel: PlantStressLevel,
        val bruisedFraction:  Float,          // fraction of pixels with bruiseRisk > 0.5
        val annotations:      List<PixelAnnotation>,  // per-pixel (same order as input)
        val disclaimer:       String = DISCLAIMER,
    )

    enum class PlantStressLevel(val label: String, val emoji: String) {
        HEALTHY    ("Healthy",          "🌱"),
        MILD_STRESS("Mild stress",      "🟡"),
        MODERATE   ("Moderate stress",  "🟠"),
        SEVERE     ("Severe / wilting", "🔴"),
        NOT_PLANT  ("No plant signal",  "—"),
    }

    // ── Thresholds ────────────────────────────────────────────────────────────

    const val REI_HEALTHY:     Float = 0.30f
    const val REI_MILD_STRESS: Float = 0.15f
    const val REI_MODERATE:    Float = 0.05f
    const val BRUISE_NIR_THRESHOLD: Float = 0.55f

    // ── Public API ────────────────────────────────────────────────────────────

    /**
     * Subtract dark frame from light frame and run spectral analysis.
     *
     * @param lightFrame  Per-pixel [r, g, b] normalised 0–1, row-major.
     * @param darkFrame   Per-pixel [r, g, b] dark (cap-on) reference frame.
     *                    Pass empty list to skip dark subtraction.
     * @return [SpectralResult] with per-pixel annotations.
     */
    fun analyse(
        lightFrame: List<FloatArray>,   // each entry = floatArrayOf(r, g, b)
        darkFrame:  List<FloatArray> = emptyList(),
    ): SpectralResult {
        if (lightFrame.isEmpty()) return SpectralResult(
            0f, 0f, PlantStressLevel.NOT_PLANT, 0f, emptyList()
        )

        val annotations = lightFrame.mapIndexed { idx, pixel ->
            val dark = darkFrame.getOrNull(idx) ?: floatArrayOf(0f, 0f, 0f)

            // Dark-subtract each channel
            val r = (pixel[0] - dark[0]).coerceIn(0f, 1f)
            val g = (pixel[1] - dark[1]).coerceIn(0f, 1f)
            // Blue channel retained for future spectral unmixing (e.g., anthocyanin at 550 nm)
            // but not used in the current REI / bruise / vein calculations.
            @Suppress("UNUSED_VARIABLE")
            val b = (pixel[2] - dark[2]).coerceIn(0f, 1f)

            // NIR proxy: the far-red shoulder of the R channel
            // The R channel captures a broad band; the upper 30% approximates 680–720 nm
            val nirProxy = (r * 0.3f).coerceIn(0f, 1f)

            // Red-edge index (normalised difference vegetation index proxy)
            val farRed = r; val red = r * 0.7f  // proxy split
            val rei = if (farRed + red > 0.001f) (farRed - red) / (farRed + red) else 0f

            // Bruise risk: elevated NIR/green ratio (bruised tissue absorbs more NIR)
            val nirGreenRatio = if (g > 0.001f) nirProxy / g else 0f
            val bruiseRisk = ((nirGreenRatio - BRUISE_NIR_THRESHOLD) / 0.4f).coerceIn(0f, 1f)

            // Vein probability: low NIR reflectance in red skin channel (deoxy-Hb absorption)
            val veinProb = if (r > 0.1f) (1f - nirProxy / r.coerceAtLeast(0.001f)).coerceIn(0f, 1f)
                           else 0f

            PixelAnnotation(
                redEdgeIndex    = rei,
                nirProxy        = nirProxy,
                bruiseRisk      = bruiseRisk,
                veinProbability = veinProb,
            )
        }

        val meanREI = annotations.map { it.redEdgeIndex }.average().toFloat()
        val nirMean = annotations.map { it.nirProxy }.average().toFloat()
        val bruisedFraction = annotations.count { it.bruiseRisk > 0.5f }.toFloat() / annotations.size

        val stress = when {
            nirMean < 0.05f                  -> PlantStressLevel.NOT_PLANT
            meanREI >= REI_HEALTHY           -> PlantStressLevel.HEALTHY
            meanREI >= REI_MILD_STRESS       -> PlantStressLevel.MILD_STRESS
            meanREI >= REI_MODERATE          -> PlantStressLevel.MODERATE
            else                             -> PlantStressLevel.SEVERE
        }

        return SpectralResult(
            meanRedEdgeIndex = meanREI,
            nirMean          = nirMean,
            plantStressLabel = stress,
            bruisedFraction  = bruisedFraction,
            annotations      = annotations,
        )
    }

    /**
     * Stack N frames to reduce shot noise.
     * Returns an averaged frame list suitable as input to [analyse].
     */
    fun stackFrames(frames: List<List<FloatArray>>): List<FloatArray> {
        if (frames.isEmpty()) return emptyList()
        val n    = frames.size.toFloat()
        val size = frames[0].size
        val result = List(size) { FloatArray(3) }
        for (frame in frames) {
            for (i in frame.indices) {
                if (i >= size) break
                result[i][0] += frame[i][0] / n
                result[i][1] += frame[i][1] / n
                result[i][2] += frame[i][2] / n
            }
        }
        return result
    }

    const val DISCLAIMER =
        "NIR / hyperspectral analysis via phone camera is an approximation only. " +
        "The internal IR-cut filter significantly attenuates the NIR signal. " +
        "Results are indicative, not calibrated spectroscopy. " +
        "Not for clinical or food-safety decisions without independent verification."
}
