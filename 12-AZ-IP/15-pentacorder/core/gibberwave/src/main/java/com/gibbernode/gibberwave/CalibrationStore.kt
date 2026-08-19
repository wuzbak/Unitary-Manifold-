package com.gibbernode.gibberwave

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.floatPreferencesKey
import androidx.datastore.preferences.core.intPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.gibbernode.audio.FrequencyBand
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

private val Context.calibrationDataStore: DataStore<Preferences>
    by preferencesDataStore(name = "gibber_calibration")

/**
 * CalibrationStore
 *
 * DataStore-backed persistence for Pentacorder audio calibration results.
 * Stores the recommended ggwave TX protocol, volume level, frequency band,
 * and measured noise floor after the CalibrationWizard has run.
 *
 * Also tracks whether calibration has been performed so MainActivity can
 * redirect first-launch users to the wizard.
 *
 * S4 default: [DEFAULT_FREQ_BAND] = NEAR_ULTRASONIC (17–22 kHz).
 * S24 Ultra note: Dolby Atmos post-processing may attenuate certain
 * FSK frequencies. The wizard runs a loopback test to pick the safest
 * protocol automatically.
 */
@Singleton
class CalibrationStore @Inject constructor(
    @ApplicationContext private val context: Context,
) {
    private val store = context.calibrationDataStore

    /** True once the user has completed or skipped the CalibrationWizard. */
    val isCalibrated: Flow<Boolean> =
        store.data.map { it[KEY_CALIBRATED] ?: false }

    /**
     * ggwave TX protocol ID (0 = AUDIBLE_NORMAL, 1 = AUDIBLE_FAST, 2 = AUDIBLE_FASTEST,
     * 3 = ULTRASOUND_NORMAL, 4 = ULTRASOUND_FAST, 5 = ULTRASOUND_FASTEST).
     * Default is ULTRASOUND_FAST until a loopback test confirms a better one.
     */
    val protocolId: Flow<Int> =
        store.data.map { it[KEY_PROTOCOL_ID] ?: DEFAULT_PROTOCOL_ID }

    /** Amplitude (0–100). */
    val volume: Flow<Int> =
        store.data.map { it[KEY_VOLUME] ?: DEFAULT_VOLUME }

    /**
     * Frequency band ordinal ([FrequencyBand.ordinal]).
     * Default is NEAR_ULTRASONIC (17–22 kHz) per S4 specification.
     */
    val freqBandOrdinal: Flow<Int> =
        store.data.map { it[KEY_FREQ_BAND] ?: DEFAULT_FREQ_BAND.ordinal }

    /** Convenience flow returning the [FrequencyBand] enum. */
    val freqBand: Flow<FrequencyBand> =
        freqBandOrdinal.map { FrequencyBand.fromOrdinal(it) }

    /**
     * Measured ambient noise floor in dBFS (negative, e.g. -55.0).
     * -99f = not yet measured.
     */
    val noiseFloorDb: Flow<Float> =
        store.data.map { it[KEY_NOISE_FLOOR_DB] ?: DEFAULT_NOISE_FLOOR_DB }

    /**
     * Highest FSK carrier frequency (Hz) verified safe on this device.
     * Populated after the CalibrationWizard loopback test confirms the audio
     * path is clean up to this frequency.
     * Default is [DEFAULT_SAFE_CEILING_HZ] = 6 000 Hz (AUDIBLE_FASTEST) until
     * a device-specific calibration is saved.
     *
     * S24 Ultra note: if Dolby Atmos does not attenuate the near-ultrasonic band,
     * this will be 20 000 (ULTRASOUND_FAST) or 22 000 (ULTRASOUND_FASTEST).
     */
    val safeCeilingHz: Flow<Int> =
        store.data.map { it[KEY_SAFE_CEILING_HZ] ?: DEFAULT_SAFE_CEILING_HZ }

    /** Save full calibration results (protocol, volume, freq band, noise floor, safe ceiling). */
    suspend fun saveCalibration(
        protocolId: Int,
        volume: Int,
        freqBand: FrequencyBand = DEFAULT_FREQ_BAND,
        noiseFloorDb: Float = DEFAULT_NOISE_FLOOR_DB,
        safeCeilingHz: Int = DEFAULT_SAFE_CEILING_HZ,
    ) {
        store.edit { prefs ->
            prefs[KEY_CALIBRATED]      = true
            prefs[KEY_PROTOCOL_ID]     = protocolId.coerceIn(0, 8)
            prefs[KEY_VOLUME]          = volume.coerceIn(1, 100)
            prefs[KEY_FREQ_BAND]       = freqBand.ordinal
            prefs[KEY_NOISE_FLOOR_DB]  = noiseFloorDb.coerceIn(-99f, 0f)
            prefs[KEY_SAFE_CEILING_HZ] = safeCeilingHz.coerceAtLeast(0)
        }
    }

    /** Mark as calibrated with defaults — used when the user skips the wizard. */
    suspend fun markCalibrated() {
        store.edit { prefs ->
            prefs[KEY_CALIBRATED]      = true
            prefs[KEY_PROTOCOL_ID]     = DEFAULT_PROTOCOL_ID
            prefs[KEY_VOLUME]          = DEFAULT_VOLUME
            prefs[KEY_FREQ_BAND]       = DEFAULT_FREQ_BAND.ordinal
            prefs[KEY_NOISE_FLOOR_DB]  = DEFAULT_NOISE_FLOOR_DB
            prefs[KEY_SAFE_CEILING_HZ] = DEFAULT_SAFE_CEILING_HZ
        }
    }

    companion object {
        private val KEY_CALIBRATED      = booleanPreferencesKey("calibrated")
        private val KEY_PROTOCOL_ID     = intPreferencesKey("protocol_id")
        private val KEY_VOLUME          = intPreferencesKey("volume")
        private val KEY_FREQ_BAND       = intPreferencesKey("freq_band_ordinal")
        private val KEY_NOISE_FLOOR_DB  = floatPreferencesKey("noise_floor_db")
        private val KEY_SAFE_CEILING_HZ = intPreferencesKey("safe_ceiling_hz")

        /**
         * S4 default: NEAR_ULTRASONIC (17–22 kHz).
         * ULTRASOUND_FAST is balanced — robust but faster than NORMAL.
         */
        val DEFAULT_FREQ_BAND: FrequencyBand = FrequencyBand.NEAR_ULTRASONIC

        /** ULTRASOUND_FAST (id=4) — near-ultrasonic default per S4 spec. */
        const val DEFAULT_PROTOCOL_ID = 4   // TxProtocol.ULTRASOUND_FAST

        /** Default amplitude — moderate for near-ultrasonic where no noise profile exists. */
        const val DEFAULT_VOLUME = 40

        /** Sentinel value: noise floor not yet measured. */
        const val DEFAULT_NOISE_FLOOR_DB = -99f

        /**
         * Conservative default safe ceiling before a device-specific loopback test.
         * 6 000 Hz = AUDIBLE_FASTEST — safe on any Android device with a standard speaker.
         * The calibration wizard will update this to the actual verified ceiling
         * (typically 20 000–22 000 Hz on S24 Ultra if Dolby Atmos allows it through).
         */
        const val DEFAULT_SAFE_CEILING_HZ = 6_000
    }
}

