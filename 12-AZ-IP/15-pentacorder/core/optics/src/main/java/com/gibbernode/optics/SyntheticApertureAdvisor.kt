package com.gibbernode.optics

import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.cos
import kotlin.math.exp
import kotlin.math.sin
import kotlin.math.sqrt

/**
 * SyntheticApertureAdvisor — virtual aperture from gyro-aligned burst photography.
 *
 * Physical basis:
 *   A large aperture lens collects light from a wide angle, giving both shallow
 *   depth-of-field (bokeh) and lower shot noise.  A phone sensor is physically
 *   tiny (~1/1.3" on S24 Ultra), but by moving the phone *intentionally* between
 *   burst frames and using the gyroscope to record the precise 3D displacement,
 *   we can synthetically "fill" a much larger aperture.
 *
 *   This is Synthetic Aperture Radar (SAR) adapted for optical photography —
 *   the same principle used by satellite radar imagers.
 *
 * Pipeline:
 *   1. Capture a burst of N frames (200 MP each) while slowly panning.
 *   2. Record gyroscope + accelerometer data at ≥100 Hz during capture.
 *   3. Compute sub-pixel shift between consecutive frames using the IMU data:
 *      Δx = ωz × dt × focal_length_px
 *      Δy = ωx × dt × focal_length_px
 *   4. Shift-and-add (SAR coherent integration): align frames to sub-pixel
 *      accuracy and average → improves SNR by √N.
 *   5. The effective aperture diameter = physical_aperture + max_displacement.
 *   6. Apply a synthetic PSF (point spread function) blur to background
 *      pixels based on their estimated disparity → computational bokeh.
 *
 * This advisor computes:
 *   - Sub-pixel frame offsets from gyro data
 *   - Effective virtual aperture diameter
 *   - Expected SNR improvement
 *   - Bokeh blur kernel radius for a given subject depth
 */
object SyntheticApertureAdvisor {

    // ── Data classes ──────────────────────────────────────────────────────────

    /**
     * IMU sample captured during a burst.
     *
     * @param gyroX  Roll rate (rad/s)
     * @param gyroY  Pitch rate (rad/s)
     * @param gyroZ  Yaw rate (rad/s)
     * @param accelX Acceleration X (m/s²)
     * @param accelY Acceleration Y (m/s²)
     * @param accelZ Acceleration Z (m/s²)
     * @param timestampMs Capture timestamp
     */
    data class ImuSample(
        val gyroX:       Float,
        val gyroY:       Float,
        val gyroZ:       Float,
        val accelX:      Float = 0f,
        val accelY:      Float = 0f,
        val accelZ:      Float = 0f,
        val timestampMs: Long,
    )

    /** Sub-pixel frame offset computed from IMU integration. */
    data class FrameOffset(
        val frameIndex: Int,
        val dxPx:       Float,  // horizontal shift in pixels
        val dyPx:       Float,  // vertical shift in pixels
    )

    /** Result of a synthetic aperture computation pass. */
    data class ApertureResult(
        val frameOffsets:           List<FrameOffset>,
        val virtualApertureMm:      Float,   // effective aperture diameter in mm
        val physicalApertureMm:     Float,   // physical phone aperture
        val snrImprovementDb:       Float,   // √N gain expressed in dB
        val bokehBlurRadiusPx:      Float,   // blur kernel for background at given depth
        val maxDisplacementPx:      Float,   // total physical pan distance in pixels
        val apertureRatio:          Float,   // virtual / physical aperture ratio
        val coherenceQuality:       Float,   // 0–1; degrades with fast motion / blur
        val disclaimer:             String = DISCLAIMER,
    )

    // ── Physical constants (S24 Ultra 200 MP lens) ────────────────────────────

    /** Physical aperture of the 200 MP main camera (f/1.7). */
    const val PHYSICAL_APERTURE_MM = 1.3f

    /** Effective focal length of the 200 MP sensor in mm. */
    const val FOCAL_LENGTH_MM = 6.3f

    /** Pixel size of the 200 MP sensor in micrometres. */
    const val PIXEL_SIZE_UM = 0.6f

    /** Focal length in pixels (for sub-pixel shift estimation). */
    const val FOCAL_LENGTH_PX = FOCAL_LENGTH_MM * 1000f / PIXEL_SIZE_UM  // ≈ 10500 px

    // ── Public API ────────────────────────────────────────────────────────────

    /**
     * Compute frame offsets and virtual aperture from burst IMU data.
     *
     * @param imuSamples     IMU samples collected during the burst.
     * @param captureIntervalMs Nominal time between burst frames (ms).
     * @param frameCount     Number of burst frames captured.
     * @param subjectDepthM  Estimated subject distance (metres); used for bokeh.
     * @param backgroundDepthM Estimated background distance (metres).
     * @param physicalApertureMm Physical aperture (default S24 Ultra main cam).
     */
    fun compute(
        imuSamples:        List<ImuSample>,
        captureIntervalMs: Float = 100f,
        frameCount:        Int   = 10,
        subjectDepthM:     Float = 2f,
        backgroundDepthM:  Float = 10f,
        physicalApertureMm: Float = PHYSICAL_APERTURE_MM,
    ): ApertureResult {
        if (imuSamples.isEmpty() || frameCount < 2) {
            return ApertureResult(
                frameOffsets        = emptyList(),
                virtualApertureMm   = physicalApertureMm,
                physicalApertureMm  = physicalApertureMm,
                snrImprovementDb    = 0f,
                bokehBlurRadiusPx   = 0f,
                maxDisplacementPx   = 0f,
                apertureRatio       = 1f,
                coherenceQuality    = 0f,
            )
        }

        // Integrate gyro to get cumulative angular displacement per frame
        val offsets = mutableListOf<FrameOffset>()
        var cumDxPx = 0f
        var cumDyPx = 0f
        var maxDisp = 0f

        // Group IMU samples into per-frame buckets
        for (frameIdx in 0 until frameCount) {
            val tStart = imuSamples.first().timestampMs + frameIdx * captureIntervalMs.toLong()
            val tEnd   = tStart + captureIntervalMs.toLong()
            val frameSamples = imuSamples.filter { it.timestampMs in tStart..tEnd }

            var dxFrame = 0f; var dyFrame = 0f
            var prevFrameTs = tStart
            for (s in frameSamples) {
                val dtS = (s.timestampMs - prevFrameTs) / 1000f
                // Angular displacement → pixel shift via focal length
                dxFrame += s.gyroZ * dtS * FOCAL_LENGTH_PX   // yaw → horizontal
                dyFrame += s.gyroX * dtS * FOCAL_LENGTH_PX   // pitch → vertical
                prevFrameTs = s.timestampMs
            }

            cumDxPx += dxFrame
            cumDyPx += dyFrame
            val disp = sqrt(cumDxPx * cumDxPx + cumDyPx * cumDyPx)
            if (disp > maxDisp) maxDisp = disp

            offsets += FrameOffset(frameIdx, cumDxPx, cumDyPx)
        }

        // Virtual aperture = physical aperture + equivalent aperture from displacement
        // displacement in px → mm: px × pixel_size_um / 1000
        val dispMm           = maxDisp * PIXEL_SIZE_UM / 1000f
        val virtualApertureMm = physicalApertureMm + dispMm * 0.5f  // 50% efficiency

        // SNR improvement: √N frames coherently stacked
        val snrImprovementDb = 10f * kotlin.math.log10(frameCount.toFloat())

        // Bokeh: circle of confusion diameter = aperture × |1/subj − 1/bg| × focal²
        // Simplified: CoC_mm = (virtualAperture / focalLength) × |subj − bg| / bg × focal
        val cocMm = (virtualApertureMm / FOCAL_LENGTH_MM) *
            abs(subjectDepthM - backgroundDepthM) / backgroundDepthM *
            FOCAL_LENGTH_MM
        val bokehPx = (cocMm * 1000f / PIXEL_SIZE_UM).coerceIn(0f, 200f)

        val apertureRatio = virtualApertureMm / physicalApertureMm.coerceAtLeast(0.001f)

        // Coherence quality degrades if frames moved too much (>50 px max)
        val coherence = (1f - (maxDisp / 50f)).coerceIn(0f, 1f)

        return ApertureResult(
            frameOffsets        = offsets,
            virtualApertureMm   = virtualApertureMm,
            physicalApertureMm  = physicalApertureMm,
            snrImprovementDb    = snrImprovementDb,
            bokehBlurRadiusPx   = bokehPx / 2f,
            maxDisplacementPx   = maxDisp,
            apertureRatio       = apertureRatio,
            coherenceQuality    = coherence,
        )
    }

    const val DISCLAIMER =
        "Synthetic aperture photogrammetry requires a calibrated burst mode and sub-pixel " +
        "optical flow alignment. Results depend on scene depth, camera motion path, and " +
        "IMU calibration accuracy. This is an estimation — not a substitute for a large-format camera."
}
