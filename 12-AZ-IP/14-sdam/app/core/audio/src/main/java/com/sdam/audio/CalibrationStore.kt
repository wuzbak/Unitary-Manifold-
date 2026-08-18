package com.sdam.audio

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.floatPreferencesKey
import androidx.datastore.preferences.core.intPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

private val Context.calibrationDataStore: DataStore<Preferences>
    by preferencesDataStore(name = "sdam_calibration")

/**
 * CalibrationStore — S4
 *
 * DataStore-backed persistence for SDAM audio calibration results.
 * Stores the recommended ggwave TX protocol, volume level, frequency band,
 * and measured noise floor.
 *
 * Default band: NEAR_ULTRASONIC (17–22 kHz) per S4 specification.
 */
@Singleton
class CalibrationStore @Inject constructor(
    @ApplicationContext private val context: Context,
) {
    private val store = context.calibrationDataStore

    /** True once the user has completed or skipped calibration. */
    val isCalibrated: Flow<Boolean> =
        store.data.map { it[KEY_CALIBRATED] ?: false }

    /** ggwave TX protocol ID. */
    val protocolId: Flow<Int> =
        store.data.map { it[KEY_PROTOCOL_ID] ?: DEFAULT_PROTOCOL_ID }

    /** Amplitude (0–100). */
    val volume: Flow<Int> =
        store.data.map { it[KEY_VOLUME] ?: DEFAULT_VOLUME }

    /** Frequency band ordinal. */
    val freqBandOrdinal: Flow<Int> =
        store.data.map { it[KEY_FREQ_BAND] ?: DEFAULT_FREQ_BAND.ordinal }

    val freqBand: Flow<FrequencyBand> =
        freqBandOrdinal.map { FrequencyBand.fromOrdinal(it) }

    /** Measured noise floor in dBFS. -99f = not yet measured. */
    val noiseFloorDb: Flow<Float> =
        store.data.map { it[KEY_NOISE_FLOOR_DB] ?: DEFAULT_NOISE_FLOOR_DB }

    /** Save full calibration results. */
    suspend fun saveCalibration(
        protocolId: Int,
        volume: Int,
        freqBand: FrequencyBand = DEFAULT_FREQ_BAND,
        noiseFloorDb: Float = DEFAULT_NOISE_FLOOR_DB,
    ) {
        store.edit { prefs ->
            prefs[KEY_CALIBRATED]     = true
            prefs[KEY_PROTOCOL_ID]    = protocolId.coerceIn(0, 8)
            prefs[KEY_VOLUME]         = volume.coerceIn(1, 100)
            prefs[KEY_FREQ_BAND]      = freqBand.ordinal
            prefs[KEY_NOISE_FLOOR_DB] = noiseFloorDb.coerceIn(-99f, 0f)
        }
    }

    /** Mark as calibrated with defaults — used when the user skips calibration. */
    suspend fun markCalibrated() {
        store.edit { prefs ->
            prefs[KEY_CALIBRATED]     = true
            prefs[KEY_PROTOCOL_ID]    = DEFAULT_PROTOCOL_ID
            prefs[KEY_VOLUME]         = DEFAULT_VOLUME
            prefs[KEY_FREQ_BAND]      = DEFAULT_FREQ_BAND.ordinal
            prefs[KEY_NOISE_FLOOR_DB] = DEFAULT_NOISE_FLOOR_DB
        }
    }

    companion object {
        private val KEY_CALIBRATED     = booleanPreferencesKey("calibrated")
        private val KEY_PROTOCOL_ID    = intPreferencesKey("protocol_id")
        private val KEY_VOLUME         = intPreferencesKey("volume")
        private val KEY_FREQ_BAND      = intPreferencesKey("freq_band_ordinal")
        private val KEY_NOISE_FLOOR_DB = floatPreferencesKey("noise_floor_db")

        /** S4 default: NEAR_ULTRASONIC (17–22 kHz). */
        val DEFAULT_FREQ_BAND: FrequencyBand = FrequencyBand.NEAR_ULTRASONIC

        /** ULTRASOUND_FAST (id=4) — near-ultrasonic default per S4 spec. */
        const val DEFAULT_PROTOCOL_ID = 4

        /** Default amplitude — moderate for near-ultrasonic. */
        const val DEFAULT_VOLUME = 40

        /** Sentinel value: noise floor not yet measured. */
        const val DEFAULT_NOISE_FLOOR_DB = -99f
    }
}
