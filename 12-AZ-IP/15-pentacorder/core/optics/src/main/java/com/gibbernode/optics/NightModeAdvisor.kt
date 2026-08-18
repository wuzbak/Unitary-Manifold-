package com.gibbernode.optics

import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.exp
import kotlin.math.ln
import kotlin.math.log10
import kotlin.math.max
import kotlin.math.min
import kotlin.math.roundToInt
import kotlin.math.sqrt

/**
 * NightModeAdvisor — Full-Colour Night Mode computational photography engine.
 *
 * Physical basis — the three pillars of S24 Ultra Nightography:
 *
 * 1. 16-in-1 Pixel Binning (Tetrapixel / Nonapixel architecture)
 *    The 200 MP sensor uses 0.6 µm pixels arranged in 4×4 (16-in-1) Bayer
 *    clusters.  In low light, 16 native pixels are summed into one "Super Pixel"
 *    of effective size 2.4 µm.  This increases the light-collecting area by
 *    16× compared to a single native pixel, directly reducing shot noise
 *    (σ_shot = √N → SNR = √(16×signal)).
 *
 *    The binned output is a 12.5 MP image with ~4× better SNR than the
 *    native 200 MP at the cost of resolution.  The AI ISP then restores
 *    resolution using learned upscaling.
 *
 * 2. Multi-Frame AI Burst Fusion (up to 30 frames)
 *    The phone takes a rapid burst of N frames (each already pixel-binned).
 *    The AI ISP performs:
 *      a. Ghost removal: identifies pixels that moved between frames (motion
 *         segmentation) and excludes them from the temporal stack.
 *      b. Noise estimation: models read noise + shot noise per pixel across
 *         the burst to compute the maximum-likelihood colour estimate.
 *      c. Colour reconstruction: at very low light, the Bayer CFA provides
 *         ambiguous colour (green channel has 2× more samples than R or B).
 *         The AI completes the colour by learning P(colour | brightness, context).
 *    SNR after N-frame fusion: SNR_fused = √N × SNR_single_binned.
 *
 * 3. OIS + Gyroscope Long-Exposure Stabilisation
 *    The S24 Ultra has a sensor-shift OIS system that physically moves the
 *    200 MP sensor in X/Y to counteract the angular tremor measured by the
 *    gyroscope.  This allows a single exposure of up to 4 seconds handheld
 *    without motion blur (for stationary subjects).
 *    OIS compensation bandwidth: ~100 Hz (IMU latency <2 ms).
 *    Equivalent full-frame exposure: up to EV −5 (starlight levels).
 *
 * This advisor computes:
 *   - Effective SNR gain from pixel binning
 *   - Expected noise reduction from multi-frame fusion
 *   - Maximum blur-free handheld exposure given OIS gyro data
 *   - Recommended ISO and exposure for a given scene lux
 *   - Colour temperature and white-balance confidence estimate
 */
object NightModeAdvisor {

    // ── Data classes ──────────────────────────────────────────────────────────

    /**
     * A gyroscope trace recorded during the exposure (or across burst frames).
     *
     * @param angularVelocitiesRad  Per-sample |ω| magnitude in rad/s.
     * @param sampleRateHz          IMU sample rate (100 Hz typical).
     */
    data class OisTrace(
        val angularVelocitiesRad: FloatArray,
        val sampleRateHz: Float = 100f,
    ) {
        override fun equals(other: Any?): Boolean =
            other is OisTrace && angularVelocitiesRad.contentEquals(other.angularVelocitiesRad)
        override fun hashCode(): Int = angularVelocitiesRad.contentHashCode()
    }

    /**
     * Per-frame radiance estimate from a dark / noisy input pixel.
     *
     * @param r Mean red value (0–1).
     * @param g Mean green value (0–1).
     * @param b Mean blue value (0–1).
     * @param iso ISO setting at capture.
     * @param exposureMs Shutter speed in milliseconds.
     */
    data class FrameSample(
        val r: Float,
        val g: Float,
        val b: Float,
        val iso: Int = 800,
        val exposureMs: Float = 50f,
    )

    /** Comprehensive result from the Night Mode computation pass. */
    data class NightModeResult(
        // SNR analysis
        val singlePixelSnrDb:      Float,   // SNR of one native 0.6 µm pixel at the given lux
        val binnedSnrDb:           Float,   // SNR after 16-in-1 binning
        val fusedSnrDb:            Float,   // SNR after N-frame burst fusion
        val snrGainOverSingleDb:   Float,   // total gain from single → fused

        // Exposure recommendations
        val recommendedIso:        Int,     // ISO for the computed scene lux
        val recommendedExposureMs: Float,   // shutter speed in ms
        val maxHandheldExposureMs: Float,   // max blur-free exposure given OIS trace

        // Colour reconstruction
        val fusedR:           Float,        // Bayesian-fused mean R channel (0–1)
        val fusedG:           Float,        // Bayesian-fused mean G channel (0–1)
        val fusedB:           Float,        // Bayesian-fused mean B channel (0–1)
        val colourTempK:      Float,        // estimated colour temperature (Kelvin)
        val whiteBalanceConf: Float,        // 0–1 confidence in colour temp estimate

        // Context
        val frameCount:       Int,
        val binFactor:        Int,          // pixel binning factor (16 for 200 MP)
        val disclaimer:       String = DISCLAIMER,
    )

    // ── S24 Ultra sensor constants ────────────────────────────────────────────

    /** Native pixel pitch in micrometres (200 MP main sensor). */
    const val NATIVE_PIXEL_UM   = 0.6f

    /** Binning factor (4×4 = 16 pixels combined into 1 Super Pixel). */
    const val BIN_FACTOR        = 16

    /** Effective pixel pitch after 16-in-1 binning. */
    const val BINNED_PIXEL_UM   = NATIVE_PIXEL_UM * 4f  // 2.4 µm

    /** Full-well capacity of a single native pixel (electrons). */
    const val FULL_WELL_ELECTRONS = 3500f  // typical for 0.6 µm BSI pixel

    /** Read noise (electrons RMS) at ISO 800. */
    const val READ_NOISE_E = 2.8f

    /** Maximum single-frame exposure time with OIS (handheld, static scene). */
    const val MAX_OIS_EXPOSURE_S = 4.0f

    /** Maximum burst frame count for AI fusion. */
    const val MAX_BURST_FRAMES = 30

    // ── Public API ────────────────────────────────────────────────────────────

    /**
     * Full Night Mode analysis: compute SNR gains, fused colour, and exposure
     * recommendations for a given scene.
     *
     * @param frames     Burst of [FrameSample] instances (3–30 frames recommended).
     * @param sceneLux   Estimated ambient illuminance (lux).  0.01 = starlight,
     *                   1 = candlelight, 10 = dim room, 100 = indoor office.
     * @param oisTrace   Optional OIS gyro trace for max-exposure estimation.
     */
    fun analyse(
        frames:    List<FrameSample>,
        sceneLux:  Float = 10f,
        oisTrace:  OisTrace? = null,
    ): NightModeResult {
        val n         = frames.size.coerceIn(1, MAX_BURST_FRAMES)
        val iso       = frames.firstOrNull()?.iso ?: 800
        val expMs     = frames.firstOrNull()?.exposureMs ?: 50f

        // ── SNR computation ───────────────────────────────────────────────────
        // Signal (electrons) in one native pixel during one exposure:
        //   S = R_photons × QE × t_exp
        // Simplified: use scene lux → photon flux approximation
        // At ISO 100, ~1 lux ≈ 400 photons/pixel/ms for a 0.6 µm pixel
        val photonsPerNativePxPerMs = (sceneLux * 400f) / (iso / 100f)
        val signalE = (photonsPerNativePxPerMs * expMs * 0.7f)  // 70% QE
            .coerceAtLeast(0.1f)

        // Total noise: σ_total = √(σ_shot² + σ_read²) = √(signal + read²)
        // Shot noise (√signal) is incorporated directly into the combined formula below.
        // Total noise: σ_total = √(σ_shot² + read²)
        val totalNoiseE = sqrt(signalE + READ_NOISE_E * READ_NOISE_E)

        val singleSnrLinear = signalE / totalNoiseE.coerceAtLeast(1e-3f)
        val singleSnrDb     = 20f * log10(singleSnrLinear.coerceAtLeast(1e-6f))

        // After 16-in-1 binning: signal × 16, read noise stays (adds once for binned pixel)
        val binnedSignalE   = signalE * BIN_FACTOR
        val binnedNoiseE    = sqrt(binnedSignalE + READ_NOISE_E * READ_NOISE_E)
        val binnedSnrLinear = binnedSignalE / binnedNoiseE.coerceAtLeast(1e-3f)
        val binnedSnrDb     = 20f * log10(binnedSnrLinear.coerceAtLeast(1e-6f))

        // After N-frame fusion: SNR improves by √N (coherent average)
        val fusedSnrLinear  = binnedSnrLinear * sqrt(n.toFloat())
        val fusedSnrDb      = 20f * log10(fusedSnrLinear.coerceAtLeast(1e-6f))
        val snrGainDb       = fusedSnrDb - singleSnrDb

        // ── OIS maximum exposure ──────────────────────────────────────────────
        val maxHandheldMs = if (oisTrace != null) {
            computeMaxExposure(oisTrace)
        } else {
            // Rule of thumb: without OIS data assume 1/focal_length rule → ~100ms
            100f
        }

        // ── Exposure recommendations ──────────────────────────────────────────
        // Target: SNR ≥ 30 dB (linear SNR ≥ 31.6) after fusion
        val targetSignalE   = (31.6f * READ_NOISE_E).pow(2f) / BIN_FACTOR / n
        val recommendedExpMs = (targetSignalE / photonsPerNativePxPerMs.coerceAtLeast(1e-6f))
            .coerceIn(4f, maxHandheldMs)
        val recommendedIso  = when {
            sceneLux >= 100f -> 100
            sceneLux >= 10f  -> 400
            sceneLux >= 1f   -> 800
            else             -> 3200
        }

        // ── Bayesian colour fusion ────────────────────────────────────────────
        // Ghost-resistant weighted mean: weight = 1 / variance of each channel
        // For simplicity: compute per-channel mean and variance across burst
        val fusedR = bayesianMean(frames.map { it.r })
        val fusedG = bayesianMean(frames.map { it.g })
        val fusedB = bayesianMean(frames.map { it.b })

        // Colour temperature from R/B ratio (McCamy approximation)
        val colourTempK = estimateColorTemp(fusedR, fusedG, fusedB)
        val wbConf      = if (n >= 5 && sceneLux >= 1f) 0.85f else 0.45f

        return NightModeResult(
            singlePixelSnrDb      = singleSnrDb,
            binnedSnrDb           = binnedSnrDb,
            fusedSnrDb            = fusedSnrDb,
            snrGainOverSingleDb   = snrGainDb,
            recommendedIso        = recommendedIso,
            recommendedExposureMs = recommendedExpMs,
            maxHandheldExposureMs = maxHandheldMs,
            fusedR                = fusedR,
            fusedG                = fusedG,
            fusedB                = fusedB,
            colourTempK           = colourTempK,
            whiteBalanceConf      = wbConf,
            frameCount            = n,
            binFactor             = BIN_FACTOR,
        )
    }

    /**
     * Compute the maximum blur-free handheld exposure from a gyroscope trace.
     *
     * Uses the 90th-percentile angular velocity to model worst-case hand tremor,
     * then computes the maximum shutter speed where the sensor's OIS keeps the
     * image-plane blur under 0.5 pixel (imperceptible at 200 MP).
     *
     * OIS bandwidth: ~100 Hz, effectively cancels tremor frequencies < 100 Hz.
     * High-frequency residual (> 100 Hz) sets the blur floor.
     */
    fun computeMaxExposure(oisTrace: OisTrace): Float {
        val ω = oisTrace.angularVelocitiesRad
        if (ω.isEmpty()) return 100f

        // 90th-percentile angular velocity (rad/s)
        val sorted = ω.copyOf().also { it.sort() }
        val p90Idx = (sorted.size * 0.9f).toInt().coerceIn(0, sorted.size - 1)
        val omegaP90 = sorted[p90Idx].coerceAtLeast(1e-4f)

        // Pixel motion at focal length 10500 px: δpx = ω × t × focal_length_px
        // Max tolerable δpx = 0.5 px → t_max = 0.5 / (ω × focal_px)
        val focalPx = SyntheticApertureAdvisor.FOCAL_LENGTH_PX
        val tMaxS   = 0.5f / (omegaP90 * focalPx)

        // OIS extends this by ~10× at the sensor level
        val oisExtendedMs = (tMaxS * 10f * 1000f).coerceIn(4f, MAX_OIS_EXPOSURE_S * 1000f)
        return oisExtendedMs
    }

    // ── Private helpers ───────────────────────────────────────────────────────

    /** Bayesian-weighted mean: robust to outliers via variance weighting. */
    private fun bayesianMean(values: List<Float>): Float {
        if (values.isEmpty()) return 0f
        if (values.size == 1) return values[0]
        val mean     = values.average().toFloat()
        val variance = values.map { (it - mean).let { d -> d * d } }.average().toFloat()
            .coerceAtLeast(1e-6f)
        // IQR gate: exclude values > 2σ from mean (ghost removal heuristic)
        val sigma    = sqrt(variance)
        val robust   = values.filter { abs(it - mean) <= 2f * sigma }
        return if (robust.isEmpty()) mean else robust.average().toFloat()
    }

    /** Estimate colour temperature in Kelvin from RGB (McCamy 1992 approximation). */
    private fun estimateColorTemp(r: Float, g: Float, b: Float): Float {
        val total = (r + g + b).coerceAtLeast(1e-3f)
        val x = r / total; val y = g / total
        val n = (x - 0.3320f) / (y - 0.1858f)
        return (-449f * n * n * n + 3525f * n * n - 6823.3f * n + 5520.33f)
            .coerceIn(1800f, 12000f)
    }

    private fun Float.pow(exp: Float): Float = exp(exp * ln(this.coerceAtLeast(1e-10f)))

    const val DISCLAIMER =
        "Night Mode analysis is a computational photography simulation. " +
        "Actual results depend on the ISP firmware, scene content, and camera hardware. " +
        "SNR values are theoretical estimates based on published sensor specifications. " +
        "Maximum exposure times are approximations; real-world OIS performance varies."
}
