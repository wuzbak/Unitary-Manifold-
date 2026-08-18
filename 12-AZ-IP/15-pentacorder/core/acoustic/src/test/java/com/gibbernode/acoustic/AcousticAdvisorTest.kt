package com.gibbernode.acoustic

import org.junit.Assert.*
import org.junit.Test

class AcousticAdvisorTest {

    // ── Smoke alarm detection ─────────────────────────────────────────────────

    @Test
    fun detectSmokeAlarm_true_for_3100Hz_spike() {
        val sampleRate = 44_100f
        val n          = 2048
        val spectrum   = buildSmokeAlarmSpectrum(n, sampleRate)
        assertTrue(AcousticAdvisor.detectSmokeAlarm(spectrum, sampleRate, AcousticAdvisor.AlertSensitivity.MEDIUM))
    }

    @Test
    fun detectSmokeAlarm_false_for_flat_spectrum() {
        val spectrum = FloatArray(1024) { 0.01f }
        assertFalse(AcousticAdvisor.detectSmokeAlarm(spectrum, 44_100f))
    }

    @Test
    fun detectSmokeAlarm_false_for_empty_spectrum() {
        assertFalse(AcousticAdvisor.detectSmokeAlarm(FloatArray(0), 44_100f))
    }

    // ── Glass break detection ─────────────────────────────────────────────────

    @Test
    fun detectGlassBreak_true_for_broadband_high_energy() {
        val sampleRate = 44_100f
        val n          = 2048
        val spectrum   = buildGlassBreakSpectrum(n, sampleRate)
        assertTrue(AcousticAdvisor.detectGlassBreak(spectrum, sampleRate, AcousticAdvisor.AlertSensitivity.MEDIUM))
    }

    @Test
    fun detectGlassBreak_false_for_low_frequency_only() {
        val sampleRate = 44_100f
        val n          = 1024
        val hzPerBin   = sampleRate / (2f * n)
        val spectrum   = FloatArray(n) { i ->
            if (i * hzPerBin < 1000f) 1.0f else 0.001f
        }
        assertFalse(AcousticAdvisor.detectGlassBreak(spectrum, sampleRate))
    }

    // ── analyseFrame ──────────────────────────────────────────────────────────

    @Test
    fun analyseFrame_returns_NONE_for_quiet_signal() {
        val spectrum = FloatArray(1024) { 0.001f }
        val event    = AcousticAdvisor.analyseFrame(spectrum, 44_100f)
        assertEquals(AcousticAdvisor.AlertType.NONE, event.primaryAlert)
    }

    @Test
    fun analyseFrame_returns_empty_for_empty_spectrum() {
        val event = AcousticAdvisor.analyseFrame(FloatArray(0), 44_100f)
        assertEquals(AcousticAdvisor.AlertType.NONE, event.primaryAlert)
        assertTrue(event.alerts.isEmpty())
    }

    // ── Engine diagnostic ─────────────────────────────────────────────────────

    @Test
    fun engineDiagnostic_no_alert_for_empty_spectra() {
        val result = AcousticAdvisor.engineDiagnostic(emptyList(), 44_100f)
        assertEquals(AcousticAdvisor.AlertType.NONE, result.alertType)
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private fun buildSmokeAlarmSpectrum(n: Int, sampleRate: Float): FloatArray {
        val hzPerBin = sampleRate / (2f * n)
        return FloatArray(n) { i ->
            val hz = i * hzPerBin
            if (hz in 2900f..3300f) 1.0f else 0.01f
        }
    }

    private fun buildGlassBreakSpectrum(n: Int, sampleRate: Float): FloatArray {
        val hzPerBin = sampleRate / (2f * n)
        return FloatArray(n) { i ->
            val hz = i * hzPerBin
            if (hz >= 4000f) 1.0f else 0.01f
        }
    }
}
