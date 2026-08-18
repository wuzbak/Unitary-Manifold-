package com.gibbernode.health

import org.junit.Assert.*
import org.junit.Test

class TremorAdvisorTest {

    @Test
    fun `assess smooth velocities gives low score`() {
        val velocities = List(100) { 5f }   // constant velocity → zero SD
        val result = TremorAdvisor.assess(velocities)
        assertTrue("Expected low score, got ${result.tremorScore}", result.tremorScore < 1f)
        assertEquals(TremorAdvisor.TremorSeverity.NONE, result.severity)
    }

    @Test
    fun `assess erratic velocities gives higher score than smooth`() {
        val smooth  = List(100) { 5f }
        val erratic = List(100) { i -> if (i % 2 == 0) 1f else 20f }
        val smoothResult  = TremorAdvisor.assess(smooth)
        val erraticResult = TremorAdvisor.assess(erratic)
        assertTrue(erraticResult.tremorScore > smoothResult.tremorScore)
    }

    @Test
    fun `assess too few samples returns zero defaults`() {
        val result = TremorAdvisor.assess(listOf(1f, 2f))
        assertEquals(0f, result.tremorScore, 0.001f)
    }

    @Test
    fun `aggregateSession insufficient for fewer than 3 readings`() {
        val session = TremorAdvisor.aggregateSession(listOf(
            TremorAdvisor.TremorReading(2f, 5f, TremorAdvisor.TremorSeverity.MILD, 0.5f)
        ))
        assertEquals(TremorAdvisor.TremorTrend.INSUFFICIENT, session.trend)
    }

    @Test
    fun `aggregateSession IMPROVING when scores decrease`() {
        val readings = listOf(
            TremorAdvisor.TremorReading(7f, 5f, TremorAdvisor.TremorSeverity.SEVERE, 0.8f),
            TremorAdvisor.TremorReading(6f, 5f, TremorAdvisor.TremorSeverity.MODERATE, 0.8f),
            TremorAdvisor.TremorReading(2f, 4f, TremorAdvisor.TremorSeverity.MILD, 0.8f),
            TremorAdvisor.TremorReading(1f, 4f, TremorAdvisor.TremorSeverity.NONE, 0.8f),
        )
        val session = TremorAdvisor.aggregateSession(readings)
        assertEquals(TremorAdvisor.TremorTrend.IMPROVING, session.trend)
    }

    @Test
    fun `aggregateSession WORSENING when scores increase`() {
        val readings = listOf(
            TremorAdvisor.TremorReading(1f, 5f, TremorAdvisor.TremorSeverity.NONE, 0.8f),
            TremorAdvisor.TremorReading(2f, 5f, TremorAdvisor.TremorSeverity.MILD, 0.8f),
            TremorAdvisor.TremorReading(6f, 5f, TremorAdvisor.TremorSeverity.MODERATE, 0.8f),
            TremorAdvisor.TremorReading(8f, 5f, TremorAdvisor.TremorSeverity.SEVERE, 0.8f),
        )
        val session = TremorAdvisor.aggregateSession(readings)
        assertEquals(TremorAdvisor.TremorTrend.WORSENING, session.trend)
    }

    @Test
    fun `disclaimer is present in TremorReading`() {
        val result = TremorAdvisor.assess(List(10) { 5f })
        assertTrue(result.disclaimer.isNotEmpty())
    }
}

class SkinColorAdvisorTest {

    @Test
    fun `analyse normal skin gives NORMAL severity`() {
        // High R, medium G, low B — typical warm/fair skin
        val result = SkinColorAdvisor.analyse(200f, 140f, 100f, luxReading = 500f)
        assertEquals(SkinColorAdvisor.PallorSeverity.NORMAL, result.pallorSeverity)
    }

    @Test
    fun `analyse returns jaundice flag for elevated yellow`() {
        // R + G >> B → high yellow index
        val result = SkinColorAdvisor.analyse(240f, 220f, 30f, luxReading = 500f)
        assertTrue(result.jaundiceFlagged)
    }

    @Test
    fun `confidence degrades in low light`() {
        val bright = SkinColorAdvisor.analyse(200f, 140f, 100f, luxReading = 500f)
        val dim    = SkinColorAdvisor.analyse(200f, 140f, 100f, luxReading = 10f)
        assertTrue("Dim (${dim.confidence}) should be < bright (${bright.confidence})", dim.confidence < bright.confidence)
    }

    @Test
    fun `calibrateBaseline returns positive float`() {
        val baseline = SkinColorAdvisor.calibrateBaseline(200f, 140f, 100f)
        assertTrue(baseline > 0f)
    }

    @Test
    fun `disclaimer is present`() {
        val result = SkinColorAdvisor.analyse(200f, 140f, 100f)
        assertTrue(result.disclaimer.isNotEmpty())
    }
}
