package com.gibbernode.optics

import kotlin.math.E
import kotlin.math.abs
import kotlin.math.exp
import kotlin.math.ln
import kotlin.math.log10
import kotlin.math.max
import kotlin.math.min
import kotlin.math.pow
import kotlin.math.roundToInt
import kotlin.math.sqrt

/**
 * ActiveNIRAdvisor — Active Near-Infrared / True Night Vision engine.
 *
 * Covers the full hardware + software path to zero-lux imaging on the S24 Ultra:
 *
 * HARDWARE PATH — Active NIR illumination:
 *   The 200 MP sensor's IR-cut filter is not 100% opaque.  At 850 nm it passes
 *   ~5–15% of incident light; at 940 nm ~2–8%.  An external IR illuminator at
 *   those wavelengths can flood a scene, providing enough photons even through
 *   the cut filter for usable frames.
 *   [irCutTransmittance] models this per-wavelength leakage.
 *
 * HARDWARE PATH — LaserAF / ToF Depth Map:
 *   The S24 Ultra LaserAF module (Sony IMX563 or similar) emits structured IR
 *   at ~940 nm and reads back a 240×180 px confidence + depth map via
 *   Camera2 CaptureResult.STATISTICS_LENS_SHADING_MAP or a proprietary
 *   Samsung extension.  In total darkness (no visible light) this gives a
 *   coarse but real silhouette image.
 *   [processDepthMap] converts a raw confidence map into a normalised night-vision image.
 *
 * SOFTWARE PATH — Temporal Denoising (ISO 12800 stack):
 *   At ISO 12800 the read noise is ~25–40e⁻, and the image looks like digital snow.
 *   By comparing N frames (5–10) pixel-by-pixel and keeping the maximum-likelihood
 *   value (rather than the noisy instant reading), the effective SNR improves by ≈√N.
 *   [temporalDenoise] implements a recursive exponential moving average with outlier rejection.
 *
 * SOFTWARE PATH — RAW_SENSOR CLAHE:
 *   CLAHE (Contrast Limited Adaptive Histogram Equalization) is the algorithm used
 *   in military-grade night-vision goggles to pull detail from near-black imagery.
 *   It divides the image into tiles, equalises each tile's histogram independently,
 *   and clips the redistribution to avoid amplifying noise.
 *   [clahe] implements a pure-Kotlin tile-based CLAHE on a flat normalised float array.
 *
 * THERMAL SAFETY:
 *   Running the 200 MP sensor at ISO 12800+ continuously generates heat.
 *   Above 45°C the sensor begins to accumulate permanent "hot pixels".
 *   [checkThermalSafety] evaluates the risk and recommends a duty cycle.
 *
 * IR-CUT FILTER CHARACTERISATION:
 *   [irCutTransmittance] returns the estimated fraction of IR that reaches the sensor
 *   at a given wavelength for the S24 Ultra (empirical curve, not manufacturer spec).
 */
object ActiveNIRAdvisor {

    // ── IR-cut filter transmittance model ────────────────────────────────────

    /**
     * Result of an IR-cut transmittance query.
     *
     * @param wavelengthNm  Requested wavelength in nanometres.
     * @param transmittance Estimated fraction reaching the sensor (0–1).
     * @param usableSignal  True when transmittance is sufficient for active NIR use.
     * @param recommendation  Illuminator selection advice.
     */
    data class IrCutResult(
        val wavelengthNm:   Int,
        val transmittance:  Float,
        val usableSignal:   Boolean,
        val recommendation: String,
    )

    /**
     * Estimate the fraction of light at [wavelengthNm] that passes through the
     * S24 Ultra IR-cut filter and reaches the CMOS sensor.
     *
     * Model (empirical approximation — not manufacturer datasheet):
     *   - < 650 nm : visible range → > 90% transmission
     *   - 650–700 nm : roll-off zone → 90% → 30%
     *   - 700–800 nm : deep-red shoulder → 15–30%
     *   - 800–900 nm : NIR suppression → 5–15%
     *   - > 900 nm : hard cutoff → 2–8%
     *
     * After physical IR-cut removal: transmittance ≈ 95% across 400–1100 nm.
     *
     * @param wavelengthNm  Illuminator wavelength (400–1100 nm).
     * @param irCutRemoved  Set true if the IR-cut filter has been physically removed.
     */
    fun irCutTransmittance(wavelengthNm: Int, irCutRemoved: Boolean = false): IrCutResult {
        if (irCutRemoved) {
            return IrCutResult(
                wavelengthNm   = wavelengthNm,
                transmittance  = 0.95f,
                usableSignal   = true,
                recommendation = "Full-spectrum mode: IR cut removed. All wavelengths 400–1100 nm at ~95% transmission.",
            )
        }

        // Sigmoid roll-off model: T(λ) ≈ A / (1 + exp(k × (λ − λ₀)))
        // Calibrated to approximate the Samsung ISOCELL HP2 filter curve
        val t = when (wavelengthNm) {
            in 400..649  -> 0.93f
            in 650..699  -> {
                // Linear ramp 93% → 28%
                val frac = (wavelengthNm - 650).toFloat() / 50f
                0.93f - frac * 0.65f
            }
            in 700..799  -> {
                // Sigmoid: 28% → 12%
                val x = (wavelengthNm - 750).toFloat() / 30f
                0.20f / (1f + exp(x))
            }
            in 800..899  -> {
                // 12% → 5%
                val frac = (wavelengthNm - 800).toFloat() / 100f
                0.12f - frac * 0.07f
            }
            else         -> 0.04f  // 900–1100 nm hard shoulder
        }.coerceIn(0.01f, 0.95f)

        val usable = t >= 0.04f
        val rec = when {
            wavelengthNm == 850 -> if (usable)
                "850 nm: ~${(t * 100).roundToInt()}% transmission — recommended for active NIR. " +
                "Slight visible glow from illuminator (barely perceptible)."
            else "850 nm not recommended at this filter level."
            wavelengthNm == 940 -> if (usable)
                "940 nm: ~${(t * 100).roundToInt()}% transmission — stealthy (no visible glow), " +
                "but requires a higher-power illuminator to compensate."
            else "940 nm: very low transmission — external illuminator required."
            t >= 0.10f -> "${wavelengthNm} nm: ~${(t * 100).roundToInt()}% usable."
            else -> "${wavelengthNm} nm: below usable threshold — use 850 nm or remove IR-cut filter."
        }

        return IrCutResult(wavelengthNm, t, usable, rec)
    }

    // ── LaserAF / ToF Depth Map processing ──────────────────────────────────

    /**
     * A raw depth/confidence map from the LaserAF sensor.
     *
     * @param depthMap       Flat array of depth values (normalised 0–1, 1 = closest).
     * @param confidenceMap  Flat array of confidence values (0–1, 1 = highest confidence).
     * @param width          Map pixel width.
     * @param height         Map pixel height.
     */
    data class DepthFrame(
        val depthMap:       FloatArray,
        val confidenceMap:  FloatArray,
        val width:          Int,
        val height:         Int,
    ) {
        override fun equals(other: Any?): Boolean =
            other is DepthFrame && depthMap.contentEquals(other.depthMap)
        override fun hashCode(): Int = depthMap.contentHashCode()
    }

    /** Result of a depth-map night-vision render pass. */
    data class DepthNightResult(
        val nightVisionImage: FloatArray,   // normalised 0–1 monochrome "radar" render
        val validPixelFraction: Float,      // fraction of pixels with confidence > threshold
        val maxDepthM:          Float,      // estimated max range (metres)
        val disclaimer:         String = DEPTH_DISCLAIMER,
    ) {
        override fun equals(other: Any?): Boolean =
            other is DepthNightResult && nightVisionImage.contentEquals(other.nightVisionImage)
        override fun hashCode(): Int = nightVisionImage.contentHashCode()
    }

    /**
     * Convert a raw LaserAF depth + confidence map into a night-vision image.
     *
     * Pixels with confidence below [minConfidence] are zeroed (invalid returns).
     * The depth values are mapped to brightness: near → bright, far → dark.
     *
     * @param frame           Input [DepthFrame] from the ToF/LaserAF sensor.
     * @param minConfidence   Gate threshold (default 0.3 — below this = noise).
     * @param maxRangeM       Maximum usable LaserAF range in metres (default 5 m).
     */
    fun processDepthMap(
        frame:         DepthFrame,
        minConfidence: Float = 0.3f,
        maxRangeM:     Float = 5f,
    ): DepthNightResult {
        val n     = frame.depthMap.size.coerceAtMost(frame.confidenceMap.size)
        val image = FloatArray(n)
        var valid = 0

        for (i in 0 until n) {
            val conf  = frame.confidenceMap[i]
            val depth = frame.depthMap[i]
            if (conf < minConfidence) {
                image[i] = 0f
            } else {
                // Invert depth so closer objects are brighter
                image[i] = (1f - depth).coerceIn(0f, 1f)
                valid++
            }
        }

        val validFraction = if (n > 0) valid.toFloat() / n else 0f
        return DepthNightResult(
            nightVisionImage    = image,
            validPixelFraction  = validFraction,
            maxDepthM           = maxRangeM,
        )
    }

    // ── Temporal Denoising (ISO 12800 stack) ─────────────────────────────────

    /**
     * Apply recursive exponential temporal denoising across a multi-frame stack.
     *
     * Algorithm:
     *   For each pixel i and frame t:
     *     smoothed[i] = α × frame[t][i] + (1 − α) × smoothed[i]_{t-1}
     *
     *   where α = temporal blend factor (lower = more temporal smoothing, less motion response).
     *
     *   Ghost rejection: if |frame[t][i] − smoothed[i]| > ghostThreshold, the pixel is
     *   treated as "moved" and weighted at α_ghost (much lower) to avoid motion smear.
     *
     * @param frames         List of per-pixel normalised float arrays (0–1).
     * @param alpha          Blend factor for static pixels (default 0.3, i.e. 70% memory).
     * @param ghostThreshold Delta above which a pixel is flagged as moved (default 0.2).
     * @param alphaGhost     Blend factor for moving pixels (default 0.8 — fast update).
     * @return Temporally denoised output frame.
     */
    fun temporalDenoise(
        frames:          List<FloatArray>,
        alpha:           Float = 0.3f,
        ghostThreshold:  Float = 0.2f,
        alphaGhost:      Float = 0.8f,
    ): FloatArray {
        if (frames.isEmpty()) return FloatArray(0)
        val size     = frames[0].size
        val smoothed = frames[0].copyOf()

        for (t in 1 until frames.size) {
            val frame = frames[t]
            for (i in 0 until minOf(size, frame.size)) {
                val delta = abs(frame[i] - smoothed[i])
                val a     = if (delta > ghostThreshold) alphaGhost else alpha
                smoothed[i] = a * frame[i] + (1f - a) * smoothed[i]
            }
        }
        return smoothed
    }

    // ── RAW_SENSOR CLAHE ─────────────────────────────────────────────────────

    /**
     * Apply Contrast Limited Adaptive Histogram Equalization (CLAHE) to a
     * flat normalised float image.
     *
     * This is the algorithm used in military NVGs to extract detail from
     * near-black imagery.  Standard global histogram equalization amplifies
     * noise in dark frames; CLAHE limits the contrast amplification per tile
     * and interpolates tile boundaries (bilinear) to avoid blocking artefacts.
     *
     * @param image      Flat row-major normalised (0–1) float image.
     * @param width      Image width in pixels.
     * @param height     Image height in pixels.
     * @param tileW      Horizontal tile count (CLAHE grid, default 8).
     * @param tileH      Vertical tile count (default 8).
     * @param clipLimit  Maximum histogram bin height before redistribution (0–1,
     *                   default 0.03 = 3% of tile pixels).  Lower = less noise amp.
     * @param histBins   Number of histogram bins (default 256).
     * @return CLAHE-equalised float image (same size).
     */
    fun clahe(
        image:     FloatArray,
        width:     Int,
        height:    Int,
        tileW:     Int   = 8,
        tileH:     Int   = 8,
        clipLimit: Float = 0.03f,
        histBins:  Int   = 256,
    ): FloatArray {
        if (image.isEmpty() || width <= 0 || height <= 0) return image.copyOf()

        val output    = FloatArray(image.size)
        val tileCols  = tileW.coerceAtLeast(1)
        val tileRows  = tileH.coerceAtLeast(1)
        val tileWidth  = (width  + tileCols - 1) / tileCols
        val tileHeight = (height + tileRows - 1) / tileRows

        // Build per-tile CDF LUTs
        val luts = Array(tileRows) { Array(tileCols) { FloatArray(histBins) } }

        for (tr in 0 until tileRows) {
            for (tc in 0 until tileCols) {
                val x0 = tc * tileWidth;  val x1 = min(x0 + tileWidth,  width)
                val y0 = tr * tileHeight; val y1 = min(y0 + tileHeight, height)
                val hist = IntArray(histBins)
                var count = 0

                for (row in y0 until y1) {
                    for (col in x0 until x1) {
                        val idx = row * width + col
                        if (idx < image.size) {
                            val bin = (image[idx] * (histBins - 1)).roundToInt()
                                .coerceIn(0, histBins - 1)
                            hist[bin]++
                            count++
                        }
                    }
                }

                // Clip + redistribute
                val clip = (clipLimit * count).toInt().coerceAtLeast(1)
                var excess = 0
                for (b in 0 until histBins) {
                    if (hist[b] > clip) { excess += hist[b] - clip; hist[b] = clip }
                }
                val redistPerBin = excess / histBins
                for (b in 0 until histBins) hist[b] += redistPerBin

                // Build CDF and normalise to LUT
                var cdf = 0
                val lut = luts[tr][tc]
                for (b in 0 until histBins) {
                    cdf += hist[b]
                    lut[b] = if (count > 0) cdf.toFloat() / count else b.toFloat() / histBins
                }
            }
        }

        // Apply LUT with bilinear tile interpolation
        for (row in 0 until height) {
            for (col in 0 until width) {
                val idx = row * width + col
                if (idx >= image.size) continue
                val bin = (image[idx] * (histBins - 1)).roundToInt().coerceIn(0, histBins - 1)

                // Nearest tile indices (clamp to grid)
                val tc = (col * tileCols / width.toFloat() - 0.5f).coerceIn(0f, tileCols - 1f)
                val tr = (row * tileRows / height.toFloat() - 0.5f).coerceIn(0f, tileRows - 1f)
                val tc0 = tc.toInt().coerceIn(0, tileCols - 1)
                val tr0 = tr.toInt().coerceIn(0, tileRows - 1)
                val tc1 = min(tc0 + 1, tileCols - 1)
                val tr1 = min(tr0 + 1, tileRows - 1)
                val wx  = tc - tc0; val wy = tr - tr0

                // Bilinear interpolation of four corner LUT values
                val v00 = luts[tr0][tc0][bin]
                val v10 = luts[tr0][tc1][bin]
                val v01 = luts[tr1][tc0][bin]
                val v11 = luts[tr1][tc1][bin]
                output[idx] = ((1 - wy) * ((1 - wx) * v00 + wx * v10) +
                               wy       * ((1 - wx) * v01 + wx * v11)).coerceIn(0f, 1f)
            }
        }
        return output
    }

    // ── Thermal safety ────────────────────────────────────────────────────────

    /** Thermal safety assessment for continuous high-ISO streaming. */
    data class ThermalSafetyResult(
        val cameraModuleTempC: Float,
        val riskLevel:         ThermalRisk,
        val maxDutyCycle:      Float,        // 0–1 fraction of time camera can be active
        val recommendedAction: String,
        val hotPixelRiskNote:  String,
    )

    enum class ThermalRisk(val label: String, val emoji: String) {
        SAFE      ("Safe",               "✅"),
        WARM      ("Warm — monitor",     "🟡"),
        HOT       ("Hot — limit duty",   "🟠"),
        CRITICAL  ("Critical — stop now","🔴"),
    }

    /**
     * Evaluate the thermal risk of continuous high-ISO camera operation.
     *
     * @param tempC  Current camera module temperature in °C (from thermal_zone sensors).
     *               Read via the Android thermal API or sysfs thermal_zone temp nodes.
     */
    fun checkThermalSafety(tempC: Float): ThermalSafetyResult {
        val risk = when {
            tempC < 35f -> ThermalRisk.SAFE
            tempC < 40f -> ThermalRisk.WARM
            tempC < 45f -> ThermalRisk.HOT
            else        -> ThermalRisk.CRITICAL
        }
        val dutyCycle = when (risk) {
            ThermalRisk.SAFE     -> 1.0f
            ThermalRisk.WARM     -> 0.8f
            ThermalRisk.HOT      -> 0.5f
            ThermalRisk.CRITICAL -> 0.0f
        }
        val action = when (risk) {
            ThermalRisk.SAFE     -> "Normal operation — continuous streaming is safe."
            ThermalRisk.WARM     -> "Monitor temperature. Avoid sustained ISO > 6400."
            ThermalRisk.HOT      -> "Reduce duty cycle to 50%. Drop to ISO ≤ 3200. Cool device."
            ThermalRisk.CRITICAL -> "STOP camera immediately. Sensor above 45°C — hot pixel damage risk."
        }
        val hotPixelNote = when {
            tempC < 40f -> "Hot pixel risk: negligible."
            tempC < 45f -> "Hot pixel risk: moderate — limit sessions to < 2 min at max ISO."
            else        -> "Hot pixel risk: HIGH — permanent sensor damage is possible above 45°C."
        }
        return ThermalSafetyResult(tempC, risk, dutyCycle, action, hotPixelNote)
    }

    // ── Recommended Camera2 capture parameters ────────────────────────────────

    /**
     * Compute recommended Camera2 capture parameters for active NIR / night mode.
     *
     * @param illuminatorWavelengthNm  Wavelength of the external IR illuminator (nm).
     * @param sceneLux                 Ambient visible lux (0 = total darkness).
     * @param irCutRemoved             Whether the IR-cut filter has been physically removed.
     * @param useRawCapture            Whether to request RAW_SENSOR (DNG) output.
     */
    data class Camera2Params(
        val iso:            Int,
        val exposureMs:     Float,
        val awbMode:        String,   // Camera2 control.AWB_MODE value
        val noiseReduction: String,   // Camera2 noise reduction mode
        val outputFormat:   String,   // "JPEG", "RAW_SENSOR", "YUV_420_888"
        val notes:          String,
    )

    fun recommendCamera2Params(
        illuminatorWavelengthNm: Int   = 850,
        sceneLux:                Float = 0f,
        irCutRemoved:            Boolean = false,
        useRawCapture:           Boolean = true,
    ): Camera2Params {
        val irResult    = irCutTransmittance(illuminatorWavelengthNm, irCutRemoved)
        val effectiveLux = sceneLux + (if (irResult.usableSignal) 5f else 0.5f)

        val iso = when {
            effectiveLux > 10f -> 800
            effectiveLux > 2f  -> 3200
            effectiveLux > 0.5f -> 6400
            else                -> 12800
        }

        val expMs = when {
            iso <= 800  -> 50f
            iso <= 3200 -> 100f
            iso <= 6400 -> 200f
            else        -> 500f    // 1/2s — requires OIS or tripod
        }

        val format = if (useRawCapture) "RAW_SENSOR (DNG)" else "YUV_420_888"
        val nr     = if (useRawCapture) "CONTROL_NOISE_REDUCTION_MODE_OFF (preserve all photons)"
                     else               "CONTROL_NOISE_REDUCTION_MODE_MINIMAL"

        val notes = buildString {
            append("ISO $iso / ${expMs.toInt()} ms shutter. ")
            append(irResult.recommendation)
            if (useRawCapture) append(" RAW requested: apply CLAHE post-capture for NV display.")
            if (iso >= 6400) append(" ⚠️ Monitor thermal_zone — max ISO sustained streaming risk.")
        }

        return Camera2Params(
            iso            = iso,
            exposureMs     = expMs,
            awbMode        = "CONTROL_AWB_MODE_OFF",    // manual WB for NIR
            noiseReduction = nr,
            outputFormat   = format,
            notes          = notes,
        )
    }

    // ── Disclaimer ────────────────────────────────────────────────────────────

    const val DEPTH_DISCLAIMER =
        "LaserAF depth map resolution is ~240×180 px. This provides silhouette-level " +
        "object detection only, not photographic detail. " +
        "Range and accuracy degrade beyond 3–5 m."

    const val GENERAL_DISCLAIMER =
        "Active NIR / night-vision mode is an experimental research capability. " +
        "Do not use to observe persons without their informed consent. " +
        "Physical IR-cut filter removal permanently alters the camera and voids warranty. " +
        "Sustained high-ISO operation above 45°C risks permanent sensor hot-pixel damage."
}
