package com.gibbernode.audio

import android.media.AudioFormat
import android.media.AudioManager
import android.media.AudioRecord
import android.media.AudioTrack
import android.media.MediaRecorder
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

private const val TAG = "GibberNode/AudioEngine"

/**
 * AudioEngine
 *
 * Manages the Android AudioRecord (capture) and AudioTrack (playback) sessions,
 * wires them to [GGWaveDecoder] and [GGWaveEncoder], and provides a clean API
 * for the rest of the app.
 *
 * Lifecycle:
 *   start() → startListening()  — opens microphone, feeds PCM to decoder
 *   play(payload)               — encodes payload → queues to AudioTrack
 *   stopListening()             — closes mic
 *   release()                   — closes everything, releases native handles
 *
 * This class does NOT hold Android permissions — the caller (AudioLoopService)
 * must hold RECORD_AUDIO before calling [startListening].
 */
class AudioEngine {

    // ── Configuration ─────────────────────────────────────────────────────────
    private val sampleRate     = GGWaveEncoder.SAMPLE_RATE_HZ           // 48 000 Hz
    private val channelIn      = AudioFormat.CHANNEL_IN_MONO
    private val channelOut     = AudioFormat.CHANNEL_OUT_STEREO
    private val encoding       = AudioFormat.ENCODING_PCM_16BIT

    // Minimum AudioRecord buffer size, rounded up to a power-of-two multiple of 1024.
    private val minRecBufBytes = AudioRecord.getMinBufferSize(sampleRate, channelIn, encoding)
        .coerceAtLeast(4096)
        .let { min -> ((min + 1023) / 1024) * 1024 }

    // Samples per AudioRecord read (= samplesPerFrame agreed with JNI layer = 1024)
    private val samplesPerFrame = 1024
    private val bytesPerFrame   = samplesPerFrame * 2  // I16 = 2 bytes/sample

    // ── ggwave wrappers ───────────────────────────────────────────────────────
    private val decoder  = GGWaveDecoder(sampleRate)
    private val encoder  = GGWaveEncoder(sampleRate)

    /** Decoded Gibberlink payloads, emitted as they arrive from the mic. */
    val decodedPayloads: SharedFlow<String> = decoder.decodedPayloads

    // ── Android audio objects ─────────────────────────────────────────────────
    private var audioRecord: AudioRecord? = null
    private var audioTrack:  AudioTrack?  = null

    // ── Coroutine scope ───────────────────────────────────────────────────────
    private val engineScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var listenJob: Job? = null

    /** True while the microphone capture loop is running. */
    @Volatile var isListening: Boolean = false
        private set

    // ── Public API ─────────────────────────────────────────────────────────────

    /**
     * Open the microphone and begin feeding PCM frames to the decoder.
     * Idempotent: calling when already listening is a no-op.
     *
     * Requires: RECORD_AUDIO permission already granted.
     */
    fun startListening() {
        if (isListening) return

        val record = AudioRecord(
            MediaRecorder.AudioSource.MIC,
            sampleRate,
            channelIn,
            encoding,
            minRecBufBytes,
        )

        if (record.state != AudioRecord.STATE_INITIALIZED) {
            Log.e(TAG, "AudioRecord failed to initialise (minBufBytes=$minRecBufBytes)")
            record.release()
            return
        }

        audioRecord = record
        record.startRecording()
        isListening = true
        Log.i(TAG, "AudioRecord started  sampleRate=$sampleRate  bufBytes=$minRecBufBytes")

        listenJob = engineScope.launch {
            val buf = ShortArray(samplesPerFrame)
            while (isActive && isListening) {
                val read = record.read(buf, 0, samplesPerFrame, AudioRecord.READ_BLOCKING)
                when {
                    read > 0 -> decoder.feedSamples(
                        if (read == samplesPerFrame) buf else buf.copyOf(read)
                    )
                    read == AudioRecord.ERROR_INVALID_OPERATION ->
                        Log.w(TAG, "AudioRecord.read: ERROR_INVALID_OPERATION")
                    read == AudioRecord.ERROR_BAD_VALUE ->
                        Log.w(TAG, "AudioRecord.read: ERROR_BAD_VALUE")
                    read < 0 ->
                        Log.e(TAG, "AudioRecord.read returned $read — stopping listener")
                }
            }
            Log.i(TAG, "Capture loop exited")
        }
    }

    /**
     * Stop the microphone capture loop and release AudioRecord.
     * Non-blocking — the coroutine is signalled to stop, not joined.
     */
    fun stopListening() {
        isListening = false
        audioRecord?.let {
            it.stop()
            it.release()
        }
        audioRecord = null
        listenJob?.cancel()
        listenJob = null
        Log.i(TAG, "AudioRecord stopped")
    }

    /**
     * Encode [payload] using [protocol] at [volume] and play it through the speaker.
     *
     * This is a *suspend* function; it completes when the last audio sample has
     * been queued into AudioTrack (not when it finishes playing — AudioTrack
     * drains asynchronously).
     *
     * @param payload   UTF-8 string to transmit.
     * @param protocol  TX protocol (default AUDIBLE_NORMAL).
     * @param volume    0–100 amplitude (80 = RED mode, 50 = GREEN mode).
     */
    suspend fun play(
        payload: String,
        protocol: TxProtocol = TxProtocol.AUDIBLE_NORMAL,
        volume: Int = 50,
    ) {
        val samples = encoder.encode(payload, protocol, volume)
        if (samples == null || samples.isEmpty()) {
            Log.e(TAG, "play: encode returned empty samples for \"${payload.take(40)}\"")
            return
        }
        playSamples(samples)
    }

    /**
     * Write pre-encoded PCM I16 samples to the speaker.
     * Creates a one-shot AudioTrack in STATIC mode for low-latency playback.
     */
    private fun playSamples(samples: ShortArray) {
        val bufBytes = samples.size * 2

        val track = AudioTrack(
            AudioManager.STREAM_MUSIC,
            sampleRate,
            channelOut,
            encoding,
            bufBytes,
            AudioTrack.MODE_STATIC,
        )

        if (track.state != AudioTrack.STATE_INITIALIZED) {
            Log.e(TAG, "AudioTrack failed to initialise (bufBytes=$bufBytes)")
            track.release()
            return
        }

        track.write(samples, 0, samples.size)
        track.play()

        audioTrack?.let {
            it.stop()
            it.release()
        }
        audioTrack = track

        Log.i(TAG, "AudioTrack playing  samples=${samples.size}  bufBytes=$bufBytes")
    }

    /**
     * Release all native and Android audio resources.
     * Call this when the hosting service is destroyed.
     */
    suspend fun release() {
        stopListening()
        listenJob?.cancelAndJoin()
        audioTrack?.let {
            it.stop()
            it.release()
        }
        audioTrack = null
        decoder.close()
        encoder.close()
        Log.i(TAG, "AudioEngine released")
    }
}
