package com.sdam.audio

import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import javax.inject.Inject
import kotlin.math.log10
import kotlin.math.sqrt

private const val TAG = "SDAM/NoiseFloor"

/**
 * CalibrationResult — S4
 *
 * @param noiseFloorDb        Measured ambient noise floor in dBFS (e.g. -55.0).
 * @param recommendedBand     [FrequencyBand] safest for this environment.
 * @param recommendedProtocol ggwave TX protocol within the recommended band.
 * @param recommendedVolume   Transmit amplitude (0–100).
 * @param isNearUltrasonicSafe Whether the near-ultrasonic band is usable.
 */
data class CalibrationResult(
    val noiseFloorDb: Float,
    val recommendedBand: FrequencyBand,
    val recommendedProtocol: TxProtocol,
    val recommendedVolume: Int,
    val isNearUltrasonicSafe: Boolean,
)

/**
 * NoiseFloorCalibrator — S4
 *
 * Measures the ambient acoustic noise floor using [AudioRecord] and recommends
 * the safest ggwave frequency band, protocol, and transmit volume.
 *
 * Algorithm:
 *   1. Open AudioRecord at 48 kHz / Mono / PCM_16BIT.
 *   2. Capture CAPTURE_FRAMES × 1024-sample frames (~1 second).
 *   3. Compute RMS of all captured samples.
 *   4. Convert RMS to dBFS: 20 × log10(rms / 32767).
 *   5. Map dBFS level to a [CalibrationResult]:
 *
 *        dBFS > -40   → HIGH NOISE   : AUDIBLE_NORMAL + vol 80
 *        -60 to -40   → MED NOISE    : AUDIBLE_FAST   + vol 50
 *        -70 to -60   → LOW NOISE    : NEAR_ULTRASONIC + vol 40
 *        < -70        → VERY QUIET   : NEAR_ULTRASONIC + vol 30
 */
class NoiseFloorCalibrator @Inject constructor() {

    companion object {
        private const val SAMPLE_RATE    = GGWaveEncoder.SAMPLE_RATE_HZ
        private const val SAMPLES_FRAME  = 1024
        private const val CAPTURE_FRAMES = 48  // ~1 second at 48 kHz
        private const val FULL_SCALE     = 32767.0

        private const val HIGH_NOISE_DBFS = -40f
        private const val MED_NOISE_DBFS  = -60f
        private const val LOW_NOISE_DBFS  = -70f
    }

    /**
     * Capture ~1 second of ambient audio and return a [CalibrationResult].
     * Suspends on [Dispatchers.IO]. Returns a safe fallback if AudioRecord fails.
     *
     * @throws SecurityException if RECORD_AUDIO is not granted.
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

        val rms     = sqrt(sumSq / totalSamples)
        val noiseDb = if (rms > 0.0) (20.0 * log10(rms / FULL_SCALE)).toFloat() else -96f

        Log.i(TAG, "Noise floor: %.1f dBFS  (rms=%.1f  samples=%d)".format(
            noiseDb, rms, totalSamples))

        buildResult(noiseDb)
    }

    private fun buildResult(noiseDb: Float): CalibrationResult = when {
        noiseDb > HIGH_NOISE_DBFS -> CalibrationResult(
            noiseFloorDb         = noiseDb,
            recommendedBand      = FrequencyBand.AUDIBLE,
            recommendedProtocol  = TxProtocol.AUDIBLE_NORMAL,
            recommendedVolume    = 80,
            isNearUltrasonicSafe = false,
        )
        noiseDb > MED_NOISE_DBFS -> CalibrationResult(
            noiseFloorDb         = noiseDb,
            recommendedBand      = FrequencyBand.AUDIBLE,
            recommendedProtocol  = TxProtocol.AUDIBLE_FAST,
            recommendedVolume    = 50,
            isNearUltrasonicSafe = true,
        )
        noiseDb > LOW_NOISE_DBFS -> CalibrationResult(
            noiseFloorDb         = noiseDb,
            recommendedBand      = FrequencyBand.NEAR_ULTRASONIC,
            recommendedProtocol  = TxProtocol.ULTRASOUND_FAST,
            recommendedVolume    = 40,
            isNearUltrasonicSafe = true,
        )
        else -> CalibrationResult(
            noiseFloorDb         = noiseDb,
            recommendedBand      = FrequencyBand.NEAR_ULTRASONIC,
            recommendedProtocol  = TxProtocol.ULTRASOUND_FASTEST,
            recommendedVolume    = 30,
            isNearUltrasonicSafe = true,
        )
    }

    private fun fallbackResult() = CalibrationResult(
        noiseFloorDb         = -50f,
        recommendedBand      = FrequencyBand.AUDIBLE,
        recommendedProtocol  = TxProtocol.AUDIBLE_NORMAL,
        recommendedVolume    = 50,
        isNearUltrasonicSafe = false,
    )
}
