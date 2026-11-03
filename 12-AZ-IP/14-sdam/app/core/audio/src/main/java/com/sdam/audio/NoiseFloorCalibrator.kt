package com.sdam.audio

import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.withContext
import javax.inject.Inject
import kotlin.math.log10
import kotlin.math.sqrt

private const val TAG = "SDAM/NoiseFloor"

/**
 * CalibrationResult — S4
 *
 * @param noiseFloorDb        Measured ambient noise floor in dBFS (e.g. -55.0).
 */
data class CalibrationResult(
    val noiseFloorDb: Float,
)

/**
 * NoiseFloorCalibrator — S4
 *
 * Measures broadband ambient audio level using [AudioRecord]. This measurement
 * does not resolve frequency-specific noise, device response, or safe output
 * levels, so it does not select a protocol or transmit volume.
 *
 * Algorithm:
 *   1. Open AudioRecord at 48 kHz / Mono / PCM_16BIT.
 *   2. Capture CAPTURE_FRAMES × 1024-sample frames (~1 second).
 *   3. Compute RMS of all captured samples.
 *   4. Convert RMS to dBFS: 20 × log10(rms / 32767).
 *   5. Report the broadband RMS level in dBFS. Protocol selection remains
 *      manual until frequency-specific calibration is implemented.
 */
class NoiseFloorCalibrator @Inject constructor() {

    companion object {
        private const val SAMPLE_RATE    = GGWaveEncoder.SAMPLE_RATE_HZ
        private const val SAMPLES_FRAME  = 1024
        private const val CAPTURE_FRAMES = 48  // ~1 second at 48 kHz
        private const val FULL_SCALE     = 32767.0
    }

    /**
     * Capture ~1 second of ambient audio and return a [CalibrationResult].
     * Suspends on [Dispatchers.IO]. Capture failures are reported to the caller.
     *
     * @throws SecurityException if RECORD_AUDIO is not granted.
     * @throws IllegalStateException if capture initialization, reads, or sample collection fail.
     * @throws IllegalArgumentException if the platform rejects audio parameters.
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

        var sumSq = 0.0
        var totalSamples = 0L
        val buf = ShortArray(SAMPLES_FRAME)

        try {
            if (record.state != AudioRecord.STATE_INITIALIZED) {
                throw IllegalStateException("AudioRecord failed to initialize.")
            }

            record.startRecording()

            repeat(CAPTURE_FRAMES) {
                currentCoroutineContext().ensureActive()
                val read = record.read(buf, 0, SAMPLES_FRAME, AudioRecord.READ_BLOCKING)
                if (read < 0) {
                    throw IllegalStateException("AudioRecord read failed with code $read.")
                }
                for (i in 0 until read) {
                    val sample = buf[i].toDouble()
                    sumSq += sample * sample
                }
                totalSamples += read
            }
        } finally {
            try {
                if (record.recordingState == AudioRecord.RECORDSTATE_RECORDING) {
                    record.stop()
                }
            } finally {
                record.release()
            }
        }

        if (totalSamples == 0L) {
            throw IllegalStateException("AudioRecord returned no audio samples.")
        }

        val noiseDb = calculateNoiseFloorDb(sumSq, totalSamples)

        Log.i(TAG, "Noise floor: %.1f dBFS  (rms=%.1f  samples=%d)".format(
            noiseDb, sqrt(sumSq / totalSamples), totalSamples))

        CalibrationResult(noiseDb)
    }
}

internal fun calculateNoiseFloorDb(sumSquares: Double, sampleCount: Long): Float {
    require(sampleCount > 0) { "sampleCount must be positive." }
    require(sumSquares.isFinite() && sumSquares >= 0.0) {
        "sumSquares must be a finite, non-negative value."
    }

    val rms = sqrt(sumSquares / sampleCount)
    return if (rms > 0.0) (20.0 * log10(rms / 32767.0)).toFloat() else -96f
}
