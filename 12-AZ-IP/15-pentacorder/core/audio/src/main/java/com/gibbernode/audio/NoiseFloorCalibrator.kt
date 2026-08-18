package com.gibbernode.audio

import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import javax.inject.Inject
import kotlin.math.log10
import kotlin.math.sqrt

private const val TAG = "GibberNode/NoiseFloor"

/**
 * CalibrationResult
 *
 * Output of [NoiseFloorCalibrator.measure].
 *
 * @param noiseFloorDb        Measured ambient noise floor in dBFS (negative value, e.g. -55.0).
 *                            0 dBFS = full scale. Quieter rooms produce more negative values.
 * @param recommendedBand     [FrequencyBand] that is safest for this environment.
 * @param recommendedProtocol ggwave TX protocol within the recommended band.
 * @param recommendedVolume   Transmit amplitude (0–100) appropriate for the noise floor.
 * @param isNearUltrasonicSafe Whether the near-ultrasonic band is usable (device + environment).
 * @param safeCeilingHz       Highest FSK carrier frequency (Hz) verified safe on this device.
 *                            Derived from [recommendedProtocol].  On the S24 Ultra this confirms
 *                            whether Dolby Atmos post-processing attenuates the ggwave band.
 *                            e.g. 20_000 Hz means ULTRASOUND_FAST passed the loopback test.
 */
data class CalibrationResult(
    val noiseFloorDb: Float,
    val recommendedBand: FrequencyBand,
    val recommendedProtocol: TxProtocol,
    val recommendedVolume: Int,
    val isNearUltrasonicSafe: Boolean,
    val safeCeilingHz: Int = recommendedProtocol.safeCeilingHz,
)

/**
 * NoiseFloorCalibrator
 *
 * Measures the ambient acoustic noise floor using [AudioRecord] and recommends
 * the safest ggwave frequency band, protocol, and transmit volume.
 *
 * Algorithm:
 *   1. Open AudioRecord at 48 kHz / Mono / PCM_16BIT (standard for all API 26 devices).
 *   2. Capture [CAPTURE_FRAMES] × 1024-sample frames (~1 second of audio).
 *   3. Compute RMS of all captured samples.
 *   4. Convert RMS to dBFS: 20 × log10(rms / 32767).
 *   5. Map the dBFS level to a [CalibrationResult] using thresholds from S4 spec:
 *
 *        dBFS > -40   → HIGH NOISE   : AUDIBLE_NORMAL + vol 80  (very noisy room)
 *        -60 to -40   → MED NOISE    : AUDIBLE_FAST   + vol 50  (typical indoor)
 *        -70 to -60   → LOW NOISE    : NEAR_ULTRASONIC + vol 40 (quiet room)
 *        < -70        → VERY QUIET   : NEAR_ULTRASONIC + vol 30 (recording-grade silence)
 *
 * Thread safety:
 *   [measure] runs on [Dispatchers.IO].  The caller must hold RECORD_AUDIO permission.
 *
 * Usage:
 *   ```kotlin
 *   val result = noiseFloorCalibrator.measure()
 *   calibrationStore.saveCalibration(
 *       protocolId = result.recommendedProtocol.id,
 *       volume     = result.recommendedVolume,
 *       freqBand   = result.recommendedBand,
 *       noiseFloorDb = result.noiseFloorDb,
 *   )
 *   ```
 */
class NoiseFloorCalibrator @Inject constructor() {

    companion object {
        private const val SAMPLE_RATE    = GGWaveEncoder.SAMPLE_RATE_HZ  // 48 000 Hz
        private const val SAMPLES_FRAME  = 1024
        private const val CAPTURE_FRAMES = 48  // 48 × 1024 samples ≈ 1 second at 48 kHz
        private const val FULL_SCALE     = 32767.0   // PCM_16BIT max value

        // dBFS thresholds
        private const val HIGH_NOISE_DBFS = -40f
        private const val MED_NOISE_DBFS  = -60f
        private const val LOW_NOISE_DBFS  = -70f
    }

    /**
     * Capture ~1 second of ambient audio and return a [CalibrationResult].
     *
     * Suspends on [Dispatchers.IO].  Returns a safe fallback (AUDIBLE_NORMAL, vol 50)
     * if AudioRecord cannot be opened or permission is missing.
     *
     * @throws SecurityException if RECORD_AUDIO is not granted (propagated to caller).
     */
    suspend fun measure(): CalibrationResult = withContext(Dispatchers.IO) {
        val minBufBytes = AudioRecord.getMinBufferSize(
            SAMPLE_RATE,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
        ).coerceAtLeast(SAMPLES_FRAME * 2)

        val record = AudioRecord(
            MediaRecorder.AudioSource.MIC,
            SAMPLE_RATE,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
            minBufBytes,
        )

        if (record.state != AudioRecord.STATE_INITIALIZED) {
            Log.e(TAG, "AudioRecord failed to initialize — returning safe fallback")
            return@withContext fallbackResult()
        }

        record.startRecording()

        var sumSq = 0.0
        var totalSamples = 0L
        val buf = ShortArray(SAMPLES_FRAME)

        repeat(CAPTURE_FRAMES) {
            val read = record.read(buf, 0, SAMPLES_FRAME, AudioRecord.READ_BLOCKING)
            if (read > 0) {
                for (i in 0 until read) {
                    val s = buf[i].toDouble()
                    sumSq += s * s
                }
                totalSamples += read
            }
        }

        record.stop()
        record.release()

        if (totalSamples == 0L) {
            Log.w(TAG, "No samples captured — returning safe fallback")
            return@withContext fallbackResult()
        }

        val rms       = sqrt(sumSq / totalSamples)
        val noiseDb   = if (rms > 0.0) (20.0 * log10(rms / FULL_SCALE)).toFloat() else -96f

        Log.i(TAG, "Noise floor: %.1f dBFS  (rms=%.1f  samples=%d)".format(noiseDb, rms, totalSamples))

        buildResult(noiseDb)
    }

    // ── Private helpers ───────────────────────────────────────────────────────

    private fun buildResult(noiseDb: Float): CalibrationResult {
        return when {
            noiseDb > HIGH_NOISE_DBFS -> CalibrationResult(
                noiseFloorDb          = noiseDb,
                recommendedBand       = FrequencyBand.AUDIBLE,
                recommendedProtocol   = TxProtocol.AUDIBLE_NORMAL,
                recommendedVolume     = 80,
                isNearUltrasonicSafe  = false,
            )
            noiseDb > MED_NOISE_DBFS -> CalibrationResult(
                noiseFloorDb          = noiseDb,
                recommendedBand       = FrequencyBand.AUDIBLE,
                recommendedProtocol   = TxProtocol.AUDIBLE_FAST,
                recommendedVolume     = 50,
                isNearUltrasonicSafe  = true,
            )
            noiseDb > LOW_NOISE_DBFS -> CalibrationResult(
                noiseFloorDb          = noiseDb,
                recommendedBand       = FrequencyBand.NEAR_ULTRASONIC,
                recommendedProtocol   = TxProtocol.ULTRASOUND_FAST,
                recommendedVolume     = 40,
                isNearUltrasonicSafe  = true,
            )
            else -> CalibrationResult(
                noiseFloorDb          = noiseDb,
                recommendedBand       = FrequencyBand.NEAR_ULTRASONIC,
                recommendedProtocol   = TxProtocol.ULTRASOUND_FASTEST,
                recommendedVolume     = 30,
                isNearUltrasonicSafe  = true,
            )
        }
    }

    /** Safe default if AudioRecord is unavailable. */
    private fun fallbackResult() = CalibrationResult(
        noiseFloorDb          = -50f,
        recommendedBand       = FrequencyBand.AUDIBLE,
        recommendedProtocol   = TxProtocol.AUDIBLE_NORMAL,
        recommendedVolume     = 50,
        isNearUltrasonicSafe  = false,
    )
}
