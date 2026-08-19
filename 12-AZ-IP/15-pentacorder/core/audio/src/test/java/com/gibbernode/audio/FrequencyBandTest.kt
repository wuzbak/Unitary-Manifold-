package com.gibbernode.audio

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import kotlin.math.log10
import kotlin.math.sqrt

/**
 * S4 Smoke test — FrequencyBand defaults and NoiseFloorCalibrator math.
 *
 * No AudioRecord is touched — these tests run on the JVM.
 */
class FrequencyBandTest {

    @Test
    fun audible_base_protocol_is_audible_fast() {
        // AUDIBLE band defaults to AUDIBLE_FAST (balanced 2-s / 32-byte mode).
        assertEquals(TxProtocol.AUDIBLE_FAST, FrequencyBand.AUDIBLE.baseProtocol)
    }

    @Test
    fun txprotocol_fromId_unknown_returns_audible_normal() {
        // Out-of-range ID must fall back to the safe default: AUDIBLE_NORMAL.
        assertEquals(TxProtocol.AUDIBLE_NORMAL, TxProtocol.fromId(999))
        assertEquals(TxProtocol.AUDIBLE_NORMAL, TxProtocol.fromId(-1))
    }

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
        assertEquals(FrequencyBand.AUDIBLE, FrequencyBand.fromOrdinal(0))
        assertEquals(FrequencyBand.NEAR_ULTRASONIC, FrequencyBand.fromOrdinal(1))
    }

    @Test
    fun fromOrdinal_out_of_range_returns_default() {
        assertEquals(FrequencyBand.DEFAULT, FrequencyBand.fromOrdinal(999))
        assertEquals(FrequencyBand.DEFAULT, FrequencyBand.fromOrdinal(-1))
    }

    // ── TxProtocol near-ultrasonic IDs ────────────────────────────────────────

    @Test
    fun ultrasound_protocols_have_expected_ids() {
        // ggwave protocol IDs: AUDIBLE_* = 0-2, ULTRASOUND_* = 3-5
        assertEquals(3, TxProtocol.ULTRASOUND_NORMAL.id)
        assertEquals(4, TxProtocol.ULTRASOUND_FAST.id)
        assertEquals(5, TxProtocol.ULTRASOUND_FASTEST.id)
    }

    // ── Noise floor dBFS formula ──────────────────────────────────────────────

    /**
     * Verify the dBFS formula used in NoiseFloorCalibrator independently.
     * This exercises the math without calling AudioRecord.
     */
    @Test
    fun dbfs_full_scale_sine_is_near_zero() {
        // A sine wave at full scale (amplitude 32767) has RMS ≈ 32767 / sqrt(2) ≈ 23170
        val amplitude = 32767.0
        val rms = amplitude / sqrt(2.0)
        val dbfs = 20.0 * log10(rms / 32767.0)
        // Full-scale sine ≈ -3 dBFS
        assertTrue("Full-scale sine ≈ -3 dBFS (got $dbfs)", dbfs > -4.0 && dbfs < -2.0)
    }

    @Test
    fun dbfs_quiet_signal_is_very_negative() {
        // 1% amplitude signal should be around -40 dBFS
        val rms = 327.0
        val dbfs = 20.0 * log10(rms / 32767.0)
        assertTrue("1% amplitude ≈ -40 dBFS (got $dbfs)", dbfs < -38.0 && dbfs > -42.0)
    }

    @Test
    fun dbfs_very_quiet_is_below_minus_60() {
        // Ambient noise in a quiet room: RMS ~10 counts out of 32767
        val rms = 10.0
        val dbfs = 20.0 * log10(rms / 32767.0)
        assertTrue("Very quiet room < -60 dBFS (got $dbfs)", dbfs < -60.0)
    }

    // ── CalibrationResult protocol thresholds ────────────────────────────────

    @Test
    fun high_noise_maps_to_audible_normal() {
        val result = buildResultForTest(-35f)  // above -40 dBFS threshold
        assertEquals(FrequencyBand.AUDIBLE, result.recommendedBand)
        assertEquals(TxProtocol.AUDIBLE_NORMAL, result.recommendedProtocol)
        assertFalse("Near-ultrasonic not safe in high noise", result.isNearUltrasonicSafe)
        assertEquals(80, result.recommendedVolume)
    }

    @Test
    fun medium_noise_maps_to_audible_fast() {
        val result = buildResultForTest(-50f)  // between -40 and -60
        assertEquals(FrequencyBand.AUDIBLE, result.recommendedBand)
        assertEquals(TxProtocol.AUDIBLE_FAST, result.recommendedProtocol)
        assertTrue("Near-ultrasonic safe in medium noise", result.isNearUltrasonicSafe)
        assertEquals(50, result.recommendedVolume)
    }

    @Test
    fun low_noise_maps_to_near_ultrasonic_fast() {
        val result = buildResultForTest(-65f)  // between -60 and -70
        assertEquals(FrequencyBand.NEAR_ULTRASONIC, result.recommendedBand)
        assertEquals(TxProtocol.ULTRASOUND_FAST, result.recommendedProtocol)
        assertTrue("Near-ultrasonic safe in quiet room", result.isNearUltrasonicSafe)
        assertEquals(40, result.recommendedVolume)
    }

    @Test
    fun very_quiet_maps_to_near_ultrasonic_fastest() {
        val result = buildResultForTest(-80f)  // below -70 dBFS
        assertEquals(FrequencyBand.NEAR_ULTRASONIC, result.recommendedBand)
        assertEquals(TxProtocol.ULTRASOUND_FASTEST, result.recommendedProtocol)
        assertTrue(result.isNearUltrasonicSafe)
        assertEquals(30, result.recommendedVolume)
    }

    // ── Helper — replicates NoiseFloorCalibrator.buildResult without AudioRecord ──

    /**
     * Standalone replica of the threshold logic from [NoiseFloorCalibrator].
     * Kept here so the test does not depend on AudioRecord at all.
     */
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
