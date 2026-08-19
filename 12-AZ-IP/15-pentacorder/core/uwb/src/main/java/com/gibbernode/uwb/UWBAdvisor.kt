package com.gibbernode.uwb

import kotlin.math.abs
import kotlin.math.atan2
import kotlin.math.cos
import kotlin.math.sin
import kotlin.math.sqrt

/**
 * UWBAdvisor
 *
 * Pure stateless logic for Ultra-Wideband ranging, 2D trilateration, and
 * "point-to-control" azimuth matching.  No Android SDK dependency.
 *
 * Physical basis:
 *   - UWB ranging: two-way time-of-flight (TW-TOF) gives centimetre-precise
 *     distance to each anchor / tag.  Android API: `androidx.core.uwb`.
 *   - Trilateration: with ≥ 3 anchors at known positions, the phone's 2D
 *     position is solved by weighted least-squares.
 *   - "Point-to-control": the phone's compass bearing to a UWB device is
 *     derived from its UWB azimuth angle reading.  When the phone is pointed
 *     at the device (bearing ≈ azimuth), it is "selecting" that device.
 *
 * Note: actual UWB session management (UwbManager, UwbClientSessionScope)
 * lives in the feature layer (UWBViewModel).  This advisor only processes
 * the resulting distance / angle values.
 *
 * @see [Android UWB API](https://developer.android.com/guide/topics/connectivity/uwb)
 */
object UWBAdvisor {

    // ── Data ──────────────────────────────────────────────────────────────────

    /**
     * A discovered UWB peer / anchor with latest ranging measurement.
     *
     * @param address     Device address (hex string or friendly name).
     * @param distanceM   Measured distance (metres).
     * @param azimuthDeg  Horizontal angle to device (−90° to +90°; 0 = straight ahead).
     * @param elevationDeg Vertical angle (−90° to +90°; 0 = level).
     * @param rssi        Signal strength (dBm); optional, for display only.
     */
    data class UWBDevice(
        val address:      String,
        val distanceM:    Float,
        val azimuthDeg:   Float,
        val elevationDeg: Float = 0f,
        val rssi:         Int   = -80,
    )

    /** 2D position result from trilateration. */
    data class Position2D(
        val x:          Float,  // metres from anchor[0]
        val y:          Float,  // metres from anchor[0]
        val confidence: Float,  // 0–1
    )

    /** Result of point-to-control evaluation. */
    data class PointingResult(
        val targetDevice:  UWBDevice,
        val isPointing:    Boolean,
        val alignmentDeg:  Float,   // angular error between phone bearing and device azimuth
        val confidence:    Float,
    )

    /** Room-map waypoint stamped during a walk-through. */
    data class MapWaypoint(
        val x:           Float,  // metres from origin
        val y:           Float,
        val pressureHpa: Float,  // barometric tag for floor height
        val epochMs:     Long,
    )

    // ── Public API ────────────────────────────────────────────────────────────

    /**
     * Determine which UWB device the phone is currently pointing at.
     *
     * The phone "points at" a device when its UWB azimuth reading falls
     * within [toleranceDeg] of zero (i.e. the device is directly ahead).
     *
     * @param devices       List of currently-ranging UWB devices.
     * @param toleranceDeg  Angular window to count as "pointing at" (default 15°).
     */
    fun findPointingTarget(
        devices:       List<UWBDevice>,
        toleranceDeg:  Float = 15f,
    ): PointingResult? {
        if (devices.isEmpty()) return null

        // Closest device within tolerance — prefer nearer devices
        val candidate = devices
            .filter { abs(it.azimuthDeg) <= toleranceDeg }
            .minByOrNull { it.distanceM }
            ?: devices.minByOrNull { abs(it.azimuthDeg) }
            ?: return null

        val alignment = abs(candidate.azimuthDeg)
        val confidence = ((toleranceDeg - alignment) / toleranceDeg).coerceIn(0f, 1f)

        return PointingResult(
            targetDevice  = candidate,
            isPointing    = alignment <= toleranceDeg,
            alignmentDeg  = alignment,
            confidence    = confidence,
        )
    }

    /**
     * Trilaterate a 2D position from 3 or more anchors.
     *
     * Uses a linearised least-squares approach (Fang's method for 3 anchors;
     * iterative WLS for > 3).
     *
     * @param anchors  List of (anchor, knownPosition [x, y]) pairs where
     *                 [UWBDevice.distanceM] holds the measured range.
     */
    fun trilaterate(anchors: List<Pair<UWBDevice, FloatArray>>): Position2D? {
        if (anchors.size < 3) return null

        // Build linearised system: ||p − a_i||² = d_i²
        // Subtract first anchor equation from others → linear in (x, y).
        val a0    = anchors[0]
        val x0    = a0.second[0]; val y0 = a0.second[1]; val d0 = a0.first.distanceM

        val rows = anchors.drop(1).map { (dev, pos) ->
            val xi  = pos[0]; val yi = pos[1]; val di = dev.distanceM
            // Linearised: 2(x0−xi)·x + 2(y0−yi)·y = di²−d0²−xi²+x0²−yi²+y0²
            val a   = 2f * (x0 - xi)
            val b   = 2f * (y0 - yi)
            val c   = di * di - d0 * d0 - xi * xi + x0 * x0 - yi * yi + y0 * y0
            Triple(a, b, c)
        }

        if (rows.size == 1) return null  // need at least 2 rows after subtraction

        // Least-squares via normal equations (A^T A)^−1 A^T b
        val sumAA = rows.sumOf { (a, _, _) -> (a * a).toDouble() }.toFloat()
        val sumBB = rows.sumOf { (_, b, _) -> (b * b).toDouble() }.toFloat()
        val sumAB = rows.sumOf { (a, b, _) -> (a * b).toDouble() }.toFloat()
        val sumAC = rows.sumOf { (a, _, c) -> (a * c).toDouble() }.toFloat()
        val sumBC = rows.sumOf { (_, b, c) -> (b * c).toDouble() }.toFloat()

        val det = sumAA * sumBB - sumAB * sumAB
        if (abs(det) < 1e-6f) return null

        val x   = (sumBB * sumAC - sumAB * sumBC) / det
        val y   = (sumAA * sumBC - sumAB * sumAC) / det

        // Confidence: residual RMS vs mean distance
        val residuals = anchors.map { (dev, pos) ->
            val dx = x - pos[0]; val dy = y - pos[1]
            abs(sqrt(dx * dx + dy * dy) - dev.distanceM)
        }
        val rmsResidual = sqrt(residuals.map { it * it }.average().toFloat())
        val meanDist    = anchors.map { it.first.distanceM }.average().toFloat()
        val confidence  = (1f - rmsResidual / (meanDist + 0.01f)).coerceIn(0f, 1f)

        return Position2D(x, y, confidence)
    }

    /**
     * Signal quality label for a given UWB distance reading.
     */
    fun signalQuality(distanceM: Float, rssi: Int): String = when {
        distanceM < 1f && rssi > -70 -> "Excellent ✅"
        distanceM < 5f && rssi > -80 -> "Good 🟢"
        distanceM < 15f              -> "Fair 🟡"
        else                         -> "Weak 🔴"
    }

    /**
     * Accumulate waypoints during a room-mapping walk.
     * Stamps current position (derived from UWB + barometer) into the map.
     * Returns the updated waypoint list with the new stamp appended.
     */
    fun stampWaypoint(
        existing:    List<MapWaypoint>,
        position:    Position2D,
        pressureHpa: Float,
    ): List<MapWaypoint> = existing + MapWaypoint(
        x           = position.x,
        y           = position.y,
        pressureHpa = pressureHpa,
        epochMs     = System.currentTimeMillis(),
    )

    /**
     * Compute the straight-line distance between two waypoints (metres).
     */
    fun waypointDistance(a: MapWaypoint, b: MapWaypoint): Float {
        val dx = a.x - b.x; val dy = a.y - b.y
        return sqrt(dx * dx + dy * dy)
    }
}
