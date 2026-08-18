package com.gibbernode.contractor

import org.junit.Assert.*
import org.junit.Test
import kotlin.math.exp

class ContractorAdvisorTest {

    @Test
    fun classifyTap_unknown_for_too_few_samples() {
        val result = ContractorAdvisor.classifyTap(listOf(1f, 2f))
        assertEquals(ContractorAdvisor.SurfaceMaterial.UNKNOWN, result.material)
    }

    @Test
    fun classifyTap_hollow_for_slow_decay() {
        val samples = buildList {
            add(50f)  // peak
            for (i in 1..80) add(50f * exp(-0.03 * i).toFloat())
        }
        val result = ContractorAdvisor.classifyTap(samples, 200f)
        assertEquals(ContractorAdvisor.SurfaceMaterial.HOLLOW, result.material)
    }

    @Test
    fun classifyTap_hard_material_for_fast_decay_and_high_peak() {
        val samples = buildList {
            add(200f)  // large peak ≈ 20 g
            for (i in 1..60) add((200f * exp(-0.30 * i).toFloat()).coerceAtLeast(0.01f))
        }
        val result = ContractorAdvisor.classifyTap(samples, 200f)
        assertTrue(
            result.material == ContractorAdvisor.SurfaceMaterial.HARD_CONCRETE ||
            result.material == ContractorAdvisor.SurfaceMaterial.DENSE_TILE
        )
    }

    @Test
    fun hardnessFromDecay_increases_with_lambda() {
        val slow = ContractorAdvisor.hardnessFromDecay(5f)
        val fast = ContractorAdvisor.hardnessFromDecay(50f)
        assertTrue("Fast ($fast) should be harder than slow ($slow)", fast > slow)
    }

    @Test
    fun hardnessFromDecay_bounded_0_to_100() {
        listOf(0f, 10f, 25f, 50f, 100f).forEach { lambda ->
            val h = ContractorAdvisor.hardnessFromDecay(lambda)
            assertTrue("Out of bounds for lambda=$lambda: $h", h in 0f..100f)
        }
    }

    // ── Level check ───────────────────────────────────────────────────────────

    @Test
    fun levelCheck_level_when_pressures_equal() {
        val result = ContractorAdvisor.levelCheck(1013.25f, 1013.25f)
        assertTrue(result.isLevel)
        assertEquals(0f, result.heightDiffMm, 0.001f)
    }

    @Test
    fun levelCheck_positive_height_diff_when_A_is_higher() {
        // Higher point → lower pressure → A pressure > B pressure → A is higher
        val result = ContractorAdvisor.levelCheck(1013.25f, 1013.13f)
        assertTrue(result.heightDiffMm > 0f)
        assertTrue(result.levelDirection.contains("A is higher"))
    }

    @Test
    fun levelCheck_not_level_for_large_diff() {
        val result = ContractorAdvisor.levelCheck(1013.25f, 1010f)
        assertFalse(result.isLevel)
    }

    // ── Doc forensics ─────────────────────────────────────────────────────────

    @Test
    fun docForensicsGuidance_recommends_increase_at_1x() {
        val guidance = ContractorAdvisor.docForensicsGuidance(1f)
        assertTrue(guidance.contains("Increase") || guidance.contains("zoom"))
    }

    @Test
    fun docForensicsGuidance_confirms_at_5x() {
        val guidance = ContractorAdvisor.docForensicsGuidance(5f)
        assertTrue(guidance.contains("5"))
    }
}
