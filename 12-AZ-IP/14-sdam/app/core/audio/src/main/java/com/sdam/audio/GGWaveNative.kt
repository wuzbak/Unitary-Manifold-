package com.sdam.audio

/**
 * GGWaveNative
 *
 * Kotlin-side declarations for the native JNI functions in sdam_jni.cpp.
 * This is a singleton object — the shared library is loaded once per process.
 *
 * Thread safety: ggwave instances are NOT thread-safe internally. All callers
 * must serialise access through [GGWaveEncoder] / [GGWaveDecoder] which each
 * hold a Mutex around every native call.
 */
object GGWaveNative {

    init {
        System.loadLibrary("sdam")
    }

    /**
     * Allocate and initialise a new ggwave DSP instance.
     *
     * @param sampleRate    Audio sample rate in Hz (e.g. 48000).
     * @param payloadLength Maximum payload length in bytes.  Pass -1 for the
     *                      ggwave library default (~140 bytes).
     * @return              Opaque 64-bit handle.  Negative means initialisation failed.
     */
    external fun nativeInit(sampleRate: Int, payloadLength: Int): Long

    /** Destroy a ggwave instance and release all native memory. */
    external fun nativeFree(handle: Long)

    /**
     * Encode [payload] into PCM I16 audio samples.
     *
     * @param handle      Handle from [nativeInit].
     * @param payload     UTF-8 string to transmit.
     * @param protocolId  ggwave TX protocol ID (see [TxProtocol]).
     * @param volume      Amplitude 0–100.
     * @return            ShortArray of I16 PCM samples, or null on failure.
     */
    external fun nativeEncode(handle: Long, payload: String, protocolId: Int, volume: Int): ShortArray?

    /**
     * Feed a batch of PCM I16 samples to the ggwave streaming decoder.
     *
     * @param handle   Handle from [nativeInit].
     * @param samples  ShortArray from AudioRecord (PCM_16BIT).
     * @return         Decoded payload string when a complete message is received;
     *                 null while still accumulating frames.
     */
    external fun nativeDecode(handle: Long, samples: ShortArray): String?
}

/**
 * ggwave TX protocol IDs.  Match ggwave_TxProtocolId in the C++ header.
 */
enum class TxProtocol(val id: Int) {
    AUDIBLE_NORMAL(0),
    AUDIBLE_FAST(1),
    AUDIBLE_FASTEST(2),
    ULTRASOUND_NORMAL(3),
    ULTRASOUND_FAST(4),
    ULTRASOUND_FASTEST(5),
    DT_NORMAL(6),
    DT_FAST(7),
    DT_FASTEST(8);

    companion object {
        fun fromId(id: Int): TxProtocol =
            entries.firstOrNull { it.id == id } ?: AUDIBLE_NORMAL
    }
}
