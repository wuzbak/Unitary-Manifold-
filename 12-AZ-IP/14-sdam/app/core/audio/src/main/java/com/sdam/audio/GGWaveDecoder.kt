package com.sdam.audio

import android.util.Log
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

private const val TAG = "SDAM/GGWaveDecoder"

/**
 * GGWaveDecoder
 *
 * Thread-safe streaming wrapper around the native ggwave decode path.
 *
 * Feed raw PCM I16 [ShortArray] buffers from AudioRecord into [feedSamples].
 * Decoded payloads are emitted on [decodedPayloads].
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

    /** Hot flow of decoded SDAM payload strings. Collect in a coroutine. */
    val decodedPayloads: SharedFlow<String> = _decodedPayloads.asSharedFlow()

    @Volatile var framesReceived: Long = 0L
        private set

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
     * Thread-safe: Mutex serialises access to the non-reentrant native instance.
     */
    suspend fun feedSamples(samples: ShortArray) {
        if (samples.isEmpty()) return
        mutex.withLock {
            framesReceived++
            val payload = GGWaveNative.nativeDecode(nativeHandle, samples)
            if (payload != null && payload.isNotEmpty()) {
                messagesDecoded++
                Log.i(TAG, "Decoded[$messagesDecoded]: \"${payload.take(60)}\"")
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
