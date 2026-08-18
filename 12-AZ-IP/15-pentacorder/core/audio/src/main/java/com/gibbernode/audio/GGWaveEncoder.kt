package com.gibbernode.audio

import android.util.Log
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

private const val TAG = "GibberNode/GGWaveEncoder"

/**
 * GGWaveEncoder
 *
 * Thread-safe wrapper around the native ggwave encode path.
 *
 * Typical usage:
 * ```kotlin
 * val encoder = GGWaveEncoder(sampleRate = 48_000)
 * val pcmSamples: ShortArray? = encoder.encode("GPS:37.77:-122.41:10:5:85",
 *                                               protocol = TxProtocol.AUDIBLE_NORMAL,
 *                                               volume = 80)
 * encoder.close()
 * ```
 *
 * This class is NOT a [java.io.Closeable] in the traditional sense because
 * it manages native memory via JNI.  Always call [close] when done.
 *
 * @param sampleRate    Audio sample rate (Hz).  Must match the AudioTrack configuration.
 * @param payloadLength Maximum payload length in bytes (-1 = library default ~140).
 */
class GGWaveEncoder(
    private val sampleRate: Int = SAMPLE_RATE_HZ,
    payloadLength: Int = -1,
) {
    private val mutex = Mutex()
    private val nativeHandle: Long

    init {
        nativeHandle = GGWaveNative.nativeInit(sampleRate, payloadLength)
        if (nativeHandle < 0L) {
            throw IllegalStateException(
                "GGWaveEncoder: ggwave_init failed (sampleRate=$sampleRate payloadLength=$payloadLength)"
            )
        }
        Log.i(TAG, "Encoder initialised  sampleRate=$sampleRate")
    }

    /**
     * Encode [payload] into PCM I16 samples.
     *
     * @param payload   The string to transmit.  UTF-8 encoded.
     * @param protocol  TX protocol selection (default [TxProtocol.AUDIBLE_NORMAL]).
     * @param volume    Amplitude 0–100 (100 = full scale, 80 = RED mode default).
     * @return          ShortArray of PCM I16 samples, or null if encoding failed.
     */
    suspend fun encode(
        payload: String,
        protocol: TxProtocol = TxProtocol.AUDIBLE_NORMAL,
        volume: Int = 50,
    ): ShortArray? = mutex.withLock {
        if (nativeHandle < 0L) {
            Log.e(TAG, "encode called on closed encoder")
            return@withLock null
        }
        val samples = GGWaveNative.nativeEncode(nativeHandle, payload, protocol.id, volume.coerceIn(0, 100))
        if (samples == null) {
            Log.w(TAG, "nativeEncode returned null for payload len=${payload.length}")
        }
        samples
    }

    /**
     * Release the native ggwave instance.  Idempotent.
     */
    suspend fun close() = mutex.withLock {
        GGWaveNative.nativeFree(nativeHandle)
        Log.i(TAG, "Encoder closed")
    }

    companion object {
        const val SAMPLE_RATE_HZ = 48_000
    }
}
