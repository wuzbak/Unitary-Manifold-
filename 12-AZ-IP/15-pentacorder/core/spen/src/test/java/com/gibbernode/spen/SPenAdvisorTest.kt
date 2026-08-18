package com.gibbernode.spen

import org.junit.Assert.*
import org.junit.Test

class SPenAdvisorTest {

    // ── StrokeAnalysis ────────────────────────────────────────────────────────

    @Test
    fun `analyze returns zero score for single point`() {
        val result = SPenAdvisor.analyze(listOf(
            SPenAdvisor.StrokePoint(0f, 0f, 0.5f, 10f, 0L)
        ))
        assertEquals(0f, result.tremorScore, 0.001f)
        assertEquals(1, result.sampleCount)
    }

    @Test
    fun `analyze smooth stroke gives low tremor score`() {
        val points = (0..49).map { i ->
            SPenAdvisor.StrokePoint(i * 10f, 0f, 0.5f, 0f, i * 10L)
        }
        val result = SPenAdvisor.analyze(points)
        assertTrue("Expected low tremor score, got ${result.tremorScore}", result.tremorScore < 1.5f)
    }

    @Test
    fun `analyze erratic stroke gives higher tremor score than smooth stroke`() {
        // Smooth: uniform timing
        val smooth = (0..49).map { i -> SPenAdvisor.StrokePoint(i * 10f, 0f, 0.5f, 0f, i * 10L) }
        // Erratic: alternating dt
        val erratic = mutableListOf<SPenAdvisor.StrokePoint>()
        var x = 0f; var t = 0L
        for (i in 0..49) {
            val dt = if (i % 2 == 0) 1L else 50L
            x += 10f; t += dt
            erratic += SPenAdvisor.StrokePoint(x, 0f, 0.5f, 0f, t)
        }
        val smoothScore  = SPenAdvisor.analyze(smooth).tremorScore
        val erraticScore = SPenAdvisor.analyze(erratic).tremorScore
        assertTrue("Erratic ($erraticScore) should exceed smooth ($smoothScore)", erraticScore > smoothScore)
    }

    @Test
    fun `normalisePressure clamps to 0-1`() {
        assertEquals(0f,   SPenAdvisor.normalisePressure(-1),   0.001f)
        assertEquals(0.5f, SPenAdvisor.normalisePressure(2048), 0.001f)
        assertEquals(1f,   SPenAdvisor.normalisePressure(4096), 0.001f)
        assertEquals(1f,   SPenAdvisor.normalisePressure(9999), 0.001f)
    }

    // ── Gesture classification ────────────────────────────────────────────────

    @Test
    fun `classifyGesture UNKNOWN for too few samples`() {
        assertEquals(SPenAdvisor.GesturePattern.UNKNOWN, SPenAdvisor.classifyGesture(emptyList()))
    }

    @Test
    fun `classifyGesture HOLD_BUTTON for low magnitude`() {
        assertEquals(SPenAdvisor.GesturePattern.HOLD_BUTTON, SPenAdvisor.classifyGesture(List(20) { 0.1f }))
    }

    // ── Bindings ──────────────────────────────────────────────────────────────

    @Test
    fun `resolveCommand uses custom override`() {
        val custom = mapOf(SPenAdvisor.GesturePattern.FLICK_UP to SPenAdvisor.AirCommand.SHUTTER)
        assertEquals(SPenAdvisor.AirCommand.SHUTTER, SPenAdvisor.resolveCommand(SPenAdvisor.GesturePattern.FLICK_UP, custom))
    }

    @Test
    fun `resolveCommand falls back to defaults`() {
        assertEquals(SPenAdvisor.AirCommand.VOLUME_UP, SPenAdvisor.resolveCommand(SPenAdvisor.GesturePattern.FLICK_UP))
    }

    // ── Air-writing hash ──────────────────────────────────────────────────────

    @Test
    fun `airWriteHash zero hash for empty input`() {
        val sig = SPenAdvisor.airWriteHash(emptyList())
        assertEquals("0000000000000000", sig.hash)
    }

    @Test
    fun `airWriteHash deterministic`() {
        val d = List(10) { Triple(0.2f, -0.1f, 0.05f) }
        assertEquals(SPenAdvisor.airWriteHash(d).hash, SPenAdvisor.airWriteHash(d).hash)
    }

    @Test
    fun `airWriteHash differs for different inputs`() {
        val a = List(10) { Triple(0.5f, 0.1f, 0f) }
        val b = List(10) { Triple(-0.5f, -0.1f, 0f) }
        assertNotEquals(SPenAdvisor.airWriteHash(a).hash, SPenAdvisor.airWriteHash(b).hash)
    }

    // ── phiHuman ──────────────────────────────────────────────────────────────

    @Test
    fun `phiHuman bounded to 0-1`() {
        val low = SPenAdvisor.StrokeAnalysis(0f, 0f, 0f, 0f, 10f, 0f, 1)
        val hi  = SPenAdvisor.StrokeAnalysis(1f, 1f, 1f, 0f, 0f, 0f, 1)
        assertTrue(SPenAdvisor.phiHuman(low) in 0f..1f)
        assertTrue(SPenAdvisor.phiHuman(hi)  in 0f..1f)
    }

    @Test
    fun `phiHuman max for perfect stroke`() {
        val analysis = SPenAdvisor.StrokeAnalysis(1f, 1f, 1f, 0f, 0f, 0f, 10)
        assertEquals(1f, SPenAdvisor.phiHuman(analysis), 0.001f)
    }
}
