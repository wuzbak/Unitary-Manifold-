package com.sdam.audio

import org.junit.Assert.assertEquals
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

    // ── dBFS calculation ──────────────────────────────────────────────────────

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

    @Test
    fun noise_floor_calculation_reports_full_scale_sine() {
        val rms = 32767.0 / sqrt(2.0)
        val dbfs = calculateNoiseFloorDb(rms * rms * 2, 2)
        assertTrue("Full-scale sine ≈ -3 dBFS (got $dbfs)", dbfs > -4f && dbfs < -2f)
    }

    @Test
    fun zero_signal_uses_minus_96_dbfs_floor() {
        assertEquals(-96f, calculateNoiseFloorDb(0.0, 100), 0.0f)
    }

    @Test
    fun noise_floor_rejects_empty_measurement() {
        try {
            calculateNoiseFloorDb(0.0, 0)
            throw AssertionError("Expected empty measurement to be rejected.")
        } catch (_: IllegalArgumentException) {
            // Expected: an empty capture is not a measured noise floor.
        }
    }

}
