package com.gibbernode.audio

import android.util.Log
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

private const val TAG = "GibberNode/GGWaveDecoder"

/**
 * GGWaveDecoder
 *
 * Thread-safe streaming wrapper around the native ggwave decode path.
 *
 * Feed raw PCM I16 [ShortArray] buffers from AudioRecord into [feedSamples].
 * Decoded payloads are emitted on [decodedPayloads].
 *
 * Design: ggwave is a stateful FSM internally — it accumulates preamble and data
 * frames across many calls to ggwave_decode before producing a payload.  This
 * class hides that complexity: callers just feed buffers and subscribe to results.
 *
 * @param sampleRate    Must match AudioRecord's configuration.
 * @param payloadLength Maximum expected payload length (-1 = library default).
 */
class GGWaveDecoder(
    private val sampleRate: Int = GGWaveEncoder.SAMPLE_RATE_HZ,
    payloadLength: Int = -1,
) {
    private val mutex = Mutex()
    private val nativeHandle: Long

    private val _decodedPayloads = MutableSharedFlow<String>(
        extraBufferCapacity = 64,
        replay = 0,
    )

    /** Hot flow of decoded Gibberlink payload strings. Collect in a coroutine. */
    val decodedPayloads: SharedFlow<String> = _decodedPayloads.asSharedFlow()

    /** Running count of PCM frames submitted (for diagnostics). */
    @Volatile var framesReceived: Long = 0L
        private set

    /** Running count of successfully decoded messages. */
    @Volatile var messagesDecoded: Long = 0L
        private set

    init {
        nativeHandle = GGWaveNative.nativeInit(sampleRate, payloadLength)
        if (nativeHandle < 0L) {
            throw IllegalStateException(
                "GGWaveDecoder: ggwave_init failed (sampleRate=$sampleRate)"
            )
        }
        Log.i(TAG, "Decoder initialised  sampleRate=$sampleRate")
    }

    /**
     * Submit a buffer of PCM I16 samples to the streaming decoder.
     *
     * This is safe to call from any thread/coroutine — the Mutex serialises
     * access to the non-reentrant native ggwave instance.
     *
     * @param samples  PCM I16 ShortArray directly from AudioRecord.read().
     */
    suspend fun feedSamples(samples: ShortArray) {
        if (samples.isEmpty()) return
        mutex.withLock {
            framesReceived++
            val payload = GGWaveNative.nativeDecode(nativeHandle, samples)
            if (payload != null && payload.isNotEmpty()) {
                messagesDecoded++
                Log.i(TAG, "Decoded payload[$messagesDecoded]: \"${payload.take(60)}\"")
                _decodedPayloads.tryEmit(payload)
            }
        }
    }

    /** Release the native ggwave instance.  Idempotent. */
    suspend fun close() = mutex.withLock {
        GGWaveNative.nativeFree(nativeHandle)
        Log.i(TAG, "Decoder closed  framesReceived=$framesReceived  messagesDecoded=$messagesDecoded")
    }
}
