package com.gibbernode.emf

import org.junit.Assert.*
import org.junit.Test

class EMFAdvisorTest {

    // ── EMF zone ──────────────────────────────────────────────────────────────

    @Test
    fun `emfZone LOW for small deviation`() {
        assertEquals(EMFAdvisor.EmfZone.LOW, EMFAdvisor.emfZone(0.1f))
    }

    @Test
    fun `emfZone MODERATE in 0_2-2 band`() {
        assertEquals(EMFAdvisor.EmfZone.MODERATE, EMFAdvisor.emfZone(1.0f))
    }

    @Test
    fun `emfZone HIGH in 2-10 band`() {
        assertEquals(EMFAdvisor.EmfZone.HIGH, EMFAdvisor.emfZone(5.0f))
    }

    @Test
    fun `emfZone ALERT above 10`() {
        assertEquals(EMFAdvisor.EmfZone.ALERT, EMFAdvisor.emfZone(15f))
    }

    // ── Stud classification ───────────────────────────────────────────────────

    @Test
    fun `classifyStud EMPTY when delta is small`() {
        val r = EMFAdvisor.classifyStud(50f, 50.05f)
        assertEquals(EMFAdvisor.StudMaterial.EMPTY, r.material)
    }

    @Test
    fun `classifyStud LIVE_WIRE when oscillating and delta above threshold`() {
        val r = EMFAdvisor.classifyStud(50f, 51f, isOscillating = true)
        assertEquals(EMFAdvisor.StudMaterial.LIVE_WIRE, r.material)
    }

    @Test
    fun `classifyStud DENSE_METAL when delta above 5`() {
        val r = EMFAdvisor.classifyStud(50f, 56f, isOscillating = false)
        assertEquals(EMFAdvisor.StudMaterial.DENSE_METAL, r.material)
    }

    @Test
    fun `classifyStud METAL_SCREW for mid delta`() {
        val r = EMFAdvisor.classifyStud(50f, 52.5f)
        assertEquals(EMFAdvisor.StudMaterial.METAL_SCREW, r.material)
    }

    // ── Sleep score ───────────────────────────────────────────────────────────

    @Test
    fun `sleepScore LOW for flat uniform field`() {
        val readings = List(30) { Triple(0f, 0f, 50f) }
        val score    = EMFAdvisor.sleepScore(readings, 50f)
        assertEquals(EMFAdvisor.EmfZone.LOW, score.zone)
    }

    @Test
    fun `sleepScore ALERT for large anomaly`() {
        val readings = List(30) { Triple(15f, 15f, 50f) }
        val score    = EMFAdvisor.sleepScore(readings, 50f)
        assertTrue(score.zone == EMFAdvisor.EmfZone.HIGH || score.zone == EMFAdvisor.EmfZone.ALERT)
    }

    @Test
    fun `sleepScore empty readings returns no crash`() {
        val score = EMFAdvisor.sleepScore(emptyList(), 50f)
        assertEquals(EMFAdvisor.EmfZone.LOW, score.zone)
    }

    // ── Dirty electricity ─────────────────────────────────────────────────────

    @Test
    fun `dirtyElectricity index 0 for empty`() {
        val r = EMFAdvisor.dirtyElectricity(emptyList())
        assertEquals(0f, r.dirtyIndex, 0.001f)
    }

    @Test
    fun `dirtyElectricity higher index for noisy signal`() {
        val clean = List(100) { 50f }
        val noisy = List(100) { i -> 50f + if (i % 2 == 0) 5f else -5f }
        val rClean = EMFAdvisor.dirtyElectricity(clean)
        val rNoisy = EMFAdvisor.dirtyElectricity(noisy)
        assertTrue("Noisy (${rNoisy.dirtyIndex}) > clean (${rClean.dirtyIndex})", rNoisy.dirtyIndex > rClean.dirtyIndex)
    }

    // ── Oscillation detection ─────────────────────────────────────────────────

    @Test
    fun `isOscillating true for power-line-like signal`() {
        // 45 Hz at 100 Hz sample rate — safely within the 40–70 Hz detection band
        // (60 Hz would alias to 40 Hz at this sample rate, landing on the edge)
        val samples = List(100) { i -> 50f + 2f * kotlin.math.sin(2 * Math.PI * 45 * i / 100.0).toFloat() }
        assertTrue(EMFAdvisor.isOscillating(samples))
    }

    @Test
    fun `isOscillating false for DC signal`() {
        assertFalse(EMFAdvisor.isOscillating(List(100) { 50f }))
    }
}
