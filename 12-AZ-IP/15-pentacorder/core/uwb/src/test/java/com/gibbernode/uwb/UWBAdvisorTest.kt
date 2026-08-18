package com.gibbernode.uwb

import org.junit.Assert.*
import org.junit.Test

class UWBAdvisorTest {

    private fun device(addr: String, dist: Float, az: Float) =
        UWBAdvisor.UWBDevice(addr, dist, az)

    // ── Point-to-control ──────────────────────────────────────────────────────

    @Test
    fun findPointingTarget_null_for_empty_list() {
        assertNull(UWBAdvisor.findPointingTarget(emptyList()))
    }

    @Test
    fun findPointingTarget_selects_closest_within_tolerance() {
        val near = device("A", 1f,  5f)
        val far  = device("B", 10f, 3f)
        val result = UWBAdvisor.findPointingTarget(listOf(near, far), 15f)
        assertNotNull(result)
        assertEquals("A", result!!.targetDevice.address)
    }

    @Test
    fun findPointingTarget_isPointing_true_when_within_tolerance() {
        val d = device("X", 2f, 10f)
        val r = UWBAdvisor.findPointingTarget(listOf(d), 15f)
        assertTrue(r!!.isPointing)
    }

    @Test
    fun findPointingTarget_isPointing_false_when_outside_tolerance() {
        val d = device("X", 2f, 50f)
        val r = UWBAdvisor.findPointingTarget(listOf(d), 15f)
        assertFalse(r!!.isPointing)
    }

    // ── Trilateration ─────────────────────────────────────────────────────────

    @Test
    fun trilaterate_returns_null_for_fewer_than_3_anchors() {
        val anchors = listOf(
            device("A", 3f, 0f) to floatArrayOf(0f, 0f),
            device("B", 4f, 0f) to floatArrayOf(5f, 0f),
        )
        assertNull(UWBAdvisor.trilaterate(anchors))
    }

    @Test
    fun trilaterate_returns_position_for_3_anchors() {
        // Three anchors at corners of a right triangle; phone at (3, 4)
        val phone = floatArrayOf(3f, 4f)
        fun dist(ax: Float, ay: Float) = kotlin.math.sqrt((3 - ax) * (3 - ax) + (4 - ay) * (4 - ay))
        val anchors = listOf(
            device("A", dist(0f, 0f), 0f) to floatArrayOf(0f, 0f),
            device("B", dist(10f, 0f), 0f) to floatArrayOf(10f, 0f),
            device("C", dist(0f, 10f), 0f) to floatArrayOf(0f, 10f),
        )
        val pos = UWBAdvisor.trilaterate(anchors)
        assertNotNull(pos)
        assertEquals(3f, pos!!.x, 0.5f)
        assertEquals(4f, pos.y, 0.5f)
    }

    // ── Signal quality ────────────────────────────────────────────────────────

    @Test
    fun signalQuality_excellent_for_close_strong_signal() {
        assertTrue(UWBAdvisor.signalQuality(0.5f, -60).contains("Excellent"))
    }

    @Test
    fun signalQuality_weak_for_far_device() {
        assertTrue(UWBAdvisor.signalQuality(20f, -90).contains("Weak"))
    }

    // ── Waypoints ────────────────────────────────────────────────────────────

    @Test
    fun stampWaypoint_appends_to_list() {
        val pos = UWBAdvisor.Position2D(1f, 2f, 0.8f)
        val result = UWBAdvisor.stampWaypoint(emptyList(), pos, 1013f)
        assertEquals(1, result.size)
        assertEquals(1f, result[0].x, 0.001f)
        assertEquals(2f, result[0].y, 0.001f)
    }

    @Test
    fun waypointDistance_correct() {
        val a = UWBAdvisor.MapWaypoint(0f, 0f, 1013f, 0)
        val b = UWBAdvisor.MapWaypoint(3f, 4f, 1013f, 1)
        assertEquals(5f, UWBAdvisor.waypointDistance(a, b), 0.001f)
    }
}
