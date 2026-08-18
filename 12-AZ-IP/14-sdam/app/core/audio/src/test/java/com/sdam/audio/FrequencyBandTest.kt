package com.sdam.audio

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import kotlin.math.log10
import kotlin.math.sqrt

/**
 * S4 Smoke tests — FrequencyBand defaults and NoiseFloorCalibrator math.
 *
 * No AudioRecord is touched — these run on the JVM.
 */
class FrequencyBandTest {

    // ── FrequencyBand defaults ────────────────────────────────────────────────

    @Test
    fun default_band_is_near_ultrasonic() {
        assertEquals(FrequencyBand.NEAR_ULTRASONIC, FrequencyBand.DEFAULT)
    }

    @Test
    fun near_ultrasonic_base_protocol_is_ultrasound_fast() {
        assertEquals(TxProtocol.ULTRASOUND_FAST, FrequencyBand.NEAR_ULTRASONIC.baseProtocol)
    }

    @Test
    fun near_ultrasonic_freq_range_is_17_to_22_kHz() {
        assertEquals(17_000, FrequencyBand.NEAR_ULTRASONIC.freqLowHz)
        assertEquals(22_000, FrequencyBand.NEAR_ULTRASONIC.freqHighHz)
    }

    @Test
    fun audible_freq_range_is_1_to_6_kHz() {
        assertEquals(1_000, FrequencyBand.AUDIBLE.freqLowHz)
        assertEquals(6_000, FrequencyBand.AUDIBLE.freqHighHz)
    }

    @Test
    fun fromOrdinal_valid_index() {
        assertEquals(FrequencyBand.AUDIBLE,         FrequencyBand.fromOrdinal(0))
        assertEquals(FrequencyBand.NEAR_ULTRASONIC, FrequencyBand.fromOrdinal(1))
    }

    @Test
    fun fromOrdinal_out_of_range_returns_default() {
        assertEquals(FrequencyBand.DEFAULT, FrequencyBand.fromOrdinal(999))
        assertEquals(FrequencyBand.DEFAULT, FrequencyBand.fromOrdinal(-1))
    }

    // ── TxProtocol IDs ────────────────────────────────────────────────────────

    @Test
    fun ultrasound_protocols_have_expected_ids() {
        assertEquals(3, TxProtocol.ULTRASOUND_NORMAL.id)
        assertEquals(4, TxProtocol.ULTRASOUND_FAST.id)
        assertEquals(5, TxProtocol.ULTRASOUND_FASTEST.id)
    }

    // ── dBFS formula (NoiseFloorCalibrator math) ──────────────────────────────

    @Test
    fun dbfs_full_scale_sine_is_near_minus_3() {
        val rms  = 32767.0 / sqrt(2.0)
        val dbfs = 20.0 * log10(rms / 32767.0)
        assertTrue("Full-scale sine ≈ -3 dBFS (got $dbfs)", dbfs > -4.0 && dbfs < -2.0)
    }

    @Test
    fun dbfs_quiet_signal_is_around_minus_40() {
        val rms  = 327.0
        val dbfs = 20.0 * log10(rms / 32767.0)
        assertTrue("1% amplitude ≈ -40 dBFS (got $dbfs)", dbfs < -38.0 && dbfs > -42.0)
    }

    @Test
    fun dbfs_very_quiet_is_below_minus_60() {
        val rms  = 10.0
        val dbfs = 20.0 * log10(rms / 32767.0)
        assertTrue("Very quiet < -60 dBFS (got $dbfs)", dbfs < -60.0)
    }

    // ── CalibrationResult threshold mapping ──────────────────────────────────

    @Test
    fun high_noise_maps_to_audible_normal() {
        val result = buildResultForTest(-35f)
        assertEquals(FrequencyBand.AUDIBLE, result.recommendedBand)
        assertEquals(TxProtocol.AUDIBLE_NORMAL, result.recommendedProtocol)
        assertFalse("Near-ultrasonic not safe in high noise", result.isNearUltrasonicSafe)
        assertEquals(80, result.recommendedVolume)
    }

    @Test
    fun medium_noise_maps_to_audible_fast() {
        val result = buildResultForTest(-50f)
        assertEquals(FrequencyBand.AUDIBLE, result.recommendedBand)
        assertEquals(TxProtocol.AUDIBLE_FAST, result.recommendedProtocol)
        assertTrue("Near-ultrasonic safe in medium noise", result.isNearUltrasonicSafe)
        assertEquals(50, result.recommendedVolume)
    }

    @Test
    fun low_noise_maps_to_near_ultrasonic_fast() {
        val result = buildResultForTest(-65f)
        assertEquals(FrequencyBand.NEAR_ULTRASONIC, result.recommendedBand)
        assertEquals(TxProtocol.ULTRASOUND_FAST, result.recommendedProtocol)
        assertTrue(result.isNearUltrasonicSafe)
        assertEquals(40, result.recommendedVolume)
    }

    @Test
    fun very_quiet_maps_to_near_ultrasonic_fastest() {
        val result = buildResultForTest(-80f)
        assertEquals(FrequencyBand.NEAR_ULTRASONIC, result.recommendedBand)
        assertEquals(TxProtocol.ULTRASOUND_FASTEST, result.recommendedProtocol)
        assertTrue(result.isNearUltrasonicSafe)
        assertEquals(30, result.recommendedVolume)
    }

    // ── Helper — replicates NoiseFloorCalibrator.buildResult without AudioRecord ──

    private fun buildResultForTest(noiseDb: Float): CalibrationResult {
        val HIGH = -40f; val MED = -60f; val LOW = -70f
        return when {
            noiseDb > HIGH -> CalibrationResult(noiseDb, FrequencyBand.AUDIBLE,         TxProtocol.AUDIBLE_NORMAL,     80, false)
            noiseDb > MED  -> CalibrationResult(noiseDb, FrequencyBand.AUDIBLE,         TxProtocol.AUDIBLE_FAST,       50, true)
            noiseDb > LOW  -> CalibrationResult(noiseDb, FrequencyBand.NEAR_ULTRASONIC, TxProtocol.ULTRASOUND_FAST,    40, true)
            else           -> CalibrationResult(noiseDb, FrequencyBand.NEAR_ULTRASONIC, TxProtocol.ULTRASOUND_FASTEST, 30, true)
        }
    }
}
