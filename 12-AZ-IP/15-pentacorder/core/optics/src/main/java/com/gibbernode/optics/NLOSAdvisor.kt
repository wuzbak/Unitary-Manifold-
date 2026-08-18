package com.gibbernode.optics

import kotlin.math.PI
import kotlin.math.cos
import kotlin.math.exp
import kotlin.math.pow
import kotlin.math.sin
import kotlin.math.sqrt

/**
 * NLOSAdvisor — Non-Line-of-Sight imaging reconstruction.
 *
 * Physical basis:
 *   A camera + Time-of-Flight (LaserAF / structured-light) sensor can detect
 *   light scattered off a matte diffuse surface (e.g., a wall).  Objects
 *   hidden around a corner modulate this scattered field through occlusion
 *   and secondary reflection.
 *
 * Algorithm (streak-camera free / passive back-projection):
 *   1. Acquire N frames of the relay wall with the LaserAF in continuous mode.
 *   2. Compute inter-frame pixel difference (motion energy map).
 *   3. Model each bright spot as an echo source at depth z computed from the
 *      ToF round-trip: z = (c × Δt) / 2  [c = speed of light, Δt = phase lag].
 *   4. Back-project onto a hidden volume grid via confocal ellipsoid sweeping.
 *
 * Limitations:
 *   - Without raw ToF timestamps this is a coarse silhouette detector only.
 *   - Works best on flat matte walls within 2–5 m of the camera.
 *   - Requires sufficient ambient contrast; direct sunlight washes the signal.
 *
 * Disclaimer:
 *   Experimental / educational.  Not a surveillance device.  Do not use to
 *   observe persons without their knowledge or consent.
 */
object NLOSAdvisor {

    // ── Data classes ──────────────────────────────────────────────────────────

    /**
     * A single "echo" detected in the relay-wall scatter map.
     *
     * @param echoX       Reconstructed hidden-volume column (normalised 0–1, left→right).
     * @param echoY       Reconstructed hidden-volume row (normalised 0–1, near→far).
     * @param depthMeters Estimated depth behind the wall (metres).  Requires ToF data.
     * @param energy      Relative scatter energy of this echo (0–1).
     */
    data class NLOSEcho(
        val echoX:       Float,
        val echoY:       Float,
        val depthMeters: Float,
        val energy:      Float,
    )

    /** Summary from one back-projection pass over N wall frames. */
    data class NLOSResult(
        val echos:          List<NLOSEcho>,
        val silhouetteArea: Float,   // normalised 0–1; fraction of hidden volume with signal
        val confidence:     Float,   // 0–1; degrades with fewer frames and low contrast
        val disclaimer:     String = DISCLAIMER,
    )

    // ── Configuration ────────────────────────────────────────────────────────

    /** Speed of light in metres per second. */
    const val C_METRES_PER_S = 299_792_458f

    /** Minimum per-pixel contrast delta to register as an echo. */
    const val ECHO_ENERGY_GATE = 0.03f

    // ── Public API ────────────────────────────────────────────────────────────

    /**
     * Process a sequence of relay-wall pixel-difference maps and return
     * detected hidden echoes.
     *
     * @param diffMaps   List of per-pixel absolute difference frames.
     *                   Each inner list is a flat row-major pixel array (values 0–1).
     * @param frameWidth  Pixel width of each diff map.
     * @param frameHeight Pixel height of each diff map.
     * @param tofPhaseLagS Optional ToF phase lag in seconds; used to estimate depth.
     *                     Pass 0f when raw ToF is not available (depth will be 0).
     */
    fun reconstruct(
        diffMaps:    List<FloatArray>,
        frameWidth:  Int,
        frameHeight: Int,
        tofPhaseLagS: Float = 0f,
    ): NLOSResult {
        if (diffMaps.isEmpty() || frameWidth <= 0 || frameHeight <= 0) {
            return NLOSResult(emptyList(), 0f, 0f)
        }

        // Accumulate energy map by averaging all diff frames
        val energy = FloatArray(frameWidth * frameHeight)
        for (frame in diffMaps) {
            val len = minOf(frame.size, energy.size)
            for (i in 0 until len) energy[i] += frame[i]
        }
        val norm = diffMaps.size.toFloat()
        for (i in energy.indices) energy[i] /= norm

        // Simple local-maxima detection (3×3 non-maximum suppression)
        val echoes = mutableListOf<NLOSEcho>()
        for (row in 1 until frameHeight - 1) {
            for (col in 1 until frameWidth - 1) {
                val v = energy[row * frameWidth + col]
                if (v < ECHO_ENERGY_GATE) continue
                // Check 3×3 neighbourhood
                var isMax = true
                outer@ for (dr in -1..1) {
                    for (dc in -1..1) {
                        if (dr == 0 && dc == 0) continue
                        val nb = energy[(row + dr) * frameWidth + (col + dc)]
                        if (nb >= v) { isMax = false; break@outer }
                    }
                }
                if (isMax) {
                    val depth = if (tofPhaseLagS > 0f) C_METRES_PER_S * tofPhaseLagS / 2f else 0f
                    echoes += NLOSEcho(
                        echoX       = col.toFloat() / (frameWidth - 1),
                        echoY       = row.toFloat() / (frameHeight - 1),
                        depthMeters = depth,
                        energy      = v,
                    )
                }
            }
        }

        val silhouetteArea = energy.count { it >= ECHO_ENERGY_GATE }.toFloat() /
            (frameWidth * frameHeight)
        val confidence = (diffMaps.size / 10f).coerceIn(0f, 1f) *
            if (silhouetteArea > 0.01f) 0.9f else 0.3f

        return NLOSResult(
            echos          = echoes.sortedByDescending { it.energy },
            silhouetteArea = silhouetteArea,
            confidence     = confidence,
        )
    }

    const val DISCLAIMER =
        "NLOS imaging is an experimental research technique. " +
        "Do not use to observe persons without informed consent. " +
        "Results are probabilistic reconstructions, not surveillance-grade images."
}
