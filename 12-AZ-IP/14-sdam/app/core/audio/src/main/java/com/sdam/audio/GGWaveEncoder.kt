package com.sdam.audio

import android.util.Log
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

private const val TAG = "SDAM/GGWaveEncoder"

/**
 * GGWaveEncoder
 *
 * Thread-safe wrapper around the native ggwave encode path.
 *
 * @param sampleRate    Audio sample rate (Hz).  Must match AudioTrack configuration.
 * @param payloadLength Maximum payload length in bytes (-1 = library default ~140).
 */
class GGWaveEncoder(
    private val sampleRate: Int = SAMPLE_RATE_HZ,
    payloadLength: Int = -1,
) {
    private val mutex = Mutex()
    private val nativeHandle: Long

    init {
        nativeHandle = if (GGWaveNative.isAvailable) {
            try {
                GGWaveNative.nativeInit(sampleRate, payloadLength)
            } catch (_: UnsatisfiedLinkError) {
                -1L
            }
        } else {
            -1L
        }
        if (nativeHandle >= 0L) Log.i(TAG, "Encoder initialised  sampleRate=$sampleRate")
        else Log.e(TAG, "Native ggwave codec unavailable")
    }

    val isAvailable: Boolean get() = nativeHandle >= 0L

    /**
     * Encode [payload] into PCM I16 samples.
     *
     * @param payload   The string to transmit.  UTF-8 encoded.
     * @param protocol  TX protocol selection.
     * @param volume    Amplitude 0–100.
     * @return          ShortArray of PCM I16 samples, or null if encoding failed.
     */
    suspend fun encode(
        payload: String,
        protocol: TxProtocol = TxProtocol.AUDIBLE_NORMAL,
        volume: Int = 50,
    ): ShortArray? = mutex.withLock {
        if (nativeHandle < 0L) {
            Log.e(TAG, "encode unavailable: native ggwave codec is not loaded")
            return@withLock null
        }
        val samples = try {
            GGWaveNative.nativeEncode(
                nativeHandle, payload, protocol.id, volume.coerceIn(0, 100)
            )
        } catch (_: UnsatisfiedLinkError) {
            null
        }
        if (samples == null) {
            Log.w(TAG, "nativeEncode returned null for payload len=${payload.length}")
        }
        samples
    }

    /** Release the native ggwave instance.  Idempotent. */
    suspend fun close() = mutex.withLock {
        if (nativeHandle >= 0L) GGWaveNative.nativeFree(nativeHandle)
        Log.i(TAG, "Encoder closed")
    }

    companion object {
        const val SAMPLE_RATE_HZ = 48_000
    }
}
