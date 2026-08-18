package com.gibbernode.audio

/**
 * GGWaveNative
 *
 * Kotlin-side declarations for the native JNI functions in gibbernode_jni.cpp.
 * This is a singleton object — the shared library is loaded once per process.
 *
 * Thread safety: ggwave instances are NOT thread-safe internally. All callers
 * must serialise access through [GGWaveEncoder] / [GGWaveDecoder] which each
 * hold a Mutex around every native call.
 */
object GGWaveNative {

    init {
        System.loadLibrary("gibbernode")
    }

    /**
     * Allocate and initialise a new ggwave DSP instance.
     *
     * @param sampleRate    Audio sample rate in Hz (e.g. 48000).  Must match the
     *                      rate used by AudioRecord / AudioTrack.
     * @param payloadLength Maximum payload length in bytes.  Pass -1 for the
     *                      ggwave library default (~140 bytes).
     * @return              Opaque 64-bit handle (ggwave_Instance id).  Negative means initialisation failed.
     */
    external fun nativeInit(sampleRate: Int, payloadLength: Int): Long

    /**
     * Destroy a ggwave instance and release all native memory.
     * Calling with a negative handle is a safe no-op.
     */
    external fun nativeFree(handle: Long)

    /**
     * Encode [payload] into PCM I16 audio samples.
     *
     * @param handle      Handle from [nativeInit].
     * @param payload     UTF-8 string to transmit.
     * @param protocolId  ggwave TX protocol ID (see [TxProtocol]).
     * @param volume      Amplitude 0–100.
     * @return            ShortArray of I16 PCM samples ready for AudioTrack, or
     *                    null if encoding failed (payload too long, instance null, …).
     */
    external fun nativeEncode(handle: Long, payload: String, protocolId: Int, volume: Int): ShortArray?

    /**
     * Feed a batch of PCM I16 samples to the ggwave streaming decoder.
     *
     * Pass each AudioRecord buffer through this function in a loop.  ggwave
     * accumulates preamble/data frames internally until a complete message
     * arrives, at which point this function returns the decoded string.
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
 *
 * AUDIBLE_NORMAL   — Robust, slower (~4 s for 32 bytes).  Best for noisy environments.
 * AUDIBLE_FAST     — Balanced (~2 s for 32 bytes).  Default for GREEN mode.
 * AUDIBLE_FASTEST  — Fastest (~1 s for 32 bytes).  Use in quiet rooms; higher error rate.
 *
 * The ULTRASOUND variants transmit above 18 kHz.  Disabled by default for BV9900 Pro
 * because the waterproof membrane attenuates high frequencies significantly.
 *
 * [safeCeilingHz] — highest FSK carrier frequency used by this protocol (Hz).
 * If a loopback test passes at this protocol, the device's audio path is verified
 * clean up to this frequency (e.g. Dolby Atmos does not attenuate this range).
 */
enum class TxProtocol(val id: Int, val safeCeilingHz: Int) {
    AUDIBLE_NORMAL(0,   3_500),
    AUDIBLE_FAST(1,     4_500),
    AUDIBLE_FASTEST(2,  6_000),
    ULTRASOUND_NORMAL(3, 18_000),
    ULTRASOUND_FAST(4,   20_000),
    ULTRASOUND_FASTEST(5, 22_000),
    DT_NORMAL(6,   8_000),
    DT_FAST(7,    10_000),
    DT_FASTEST(8, 12_000);

    companion object {
        fun fromId(id: Int): TxProtocol =
            entries.firstOrNull { it.id == id } ?: AUDIBLE_NORMAL
    }
}
