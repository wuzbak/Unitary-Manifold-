/**
 * sdam_jni.cpp
 *
 * JNI bridge between the Android/Kotlin layer and the ggwave C++ DSP library.
 *
 * Kotlin class: com.sdam.audio.GGWaveNative  (object with external funs)
 *
 * Threading contract:
 *   - nativeInit / nativeFree must be called on the same thread.
 *   - nativeEncode and nativeDecode are thread-hostile (ggwave instances are
 *     not re-entrant). The Kotlin wrapper serialises calls via a Mutex.
 *   - Do NOT share an instance pointer across threads without synchronisation.
 */

#include <jni.h>
#include <android/log.h>
#include <ggwave/ggwave.h>

#include <cstring>
#include <memory>
#include <string>
#include <vector>

#define LOG_TAG "SDAM/JNI"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO,  LOG_TAG, __VA_ARGS__)
#define LOGW(...) __android_log_print(ANDROID_LOG_WARN,  LOG_TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

// ── Helpers ──────────────────────────────────────────────────────────────────

/**
 * Cast a jlong opaque handle back to a ggwave_Instance (typedef int).
 * We store the int id as a jlong so Kotlin can hold it opaquely.
 */
static inline ggwave_Instance ptrFromJLong(jlong handle) {
    return static_cast<ggwave_Instance>(handle);
}

// ── JNI implementations ───────────────────────────────────────────────────────

extern "C" {

/**
 * Initialize a ggwave instance.
 *
 * @param sampleRate     Desired sample rate in Hz (should match AudioRecord/AudioTrack).
 *                       Typical values: 16000, 44100, 48000.
 * @param payloadLength  Maximum payload length in bytes (-1 = use ggwave default ~140 bytes).
 * @return               Opaque handle (ggwave_Instance id stored as jlong), or -1 on failure.
 */
JNIEXPORT jlong JNICALL
Java_com_sdam_audio_GGWaveNative_nativeInit(
    JNIEnv* /*env*/,
    jobject /*thiz*/,
    jint    sampleRate,
    jint    payloadLength)
{
    ggwave_Parameters params = ggwave_getDefaultParameters();

    params.sampleRateInp    = static_cast<float>(sampleRate);
    params.sampleRateOut    = static_cast<float>(sampleRate);
    params.samplesPerFrame  = 1024;  // 1024 samples ~= 21 ms @ 48 kHz; matches AudioRecord buffers

    // Audible + near-ultrasonic protocols
    params.operatingMode = GGWAVE_OPERATING_MODE_RX | GGWAVE_OPERATING_MODE_TX;

    if (payloadLength > 0) {
        params.payloadLength = payloadLength;
    }

    // I16 in/out matches AudioRecord(PCM_16BIT) and AudioTrack(PCM_16BIT)
    params.sampleFormatInp = GGWAVE_SAMPLE_FORMAT_I16;
    params.sampleFormatOut = GGWAVE_SAMPLE_FORMAT_I16;

    ggwave_Instance instance = ggwave_init(params);
    if (instance < 0) {
        LOGE("ggwave_init failed (sampleRate=%d payloadLength=%d)", sampleRate, payloadLength);
        return -1L;
    }

    LOGI("ggwave_init OK  sampleRate=%d  samplesPerFrame=%d  payloadLength=%d",
         sampleRate, params.samplesPerFrame, params.payloadLength);

    return static_cast<jlong>(instance);
}

/**
 * Release a ggwave instance and free all DSP resources.
 *
 * @param handle  The value returned by nativeInit().  Passing a negative value is a no-op.
 */
JNIEXPORT void JNICALL
Java_com_sdam_audio_GGWaveNative_nativeFree(
    JNIEnv* /*env*/,
    jobject /*thiz*/,
    jlong   handle)
{
    if (handle < 0L) return;
    ggwave_Instance instance = ptrFromJLong(handle);
    ggwave_free(instance);
    LOGI("ggwave_free OK");
}

/**
 * Encode a text payload into PCM I16 audio samples.
 *
 * @param handle      ggwave instance (from nativeInit).
 * @param payload     UTF-8 string to encode.
 * @param protocolId  ggwave protocol (0 = AUDIBLE_NORMAL, 1 = AUDIBLE_FAST,
 *                    2 = AUDIBLE_FASTEST, …).  See ggwave_ProtocolId enum.
 * @param volume      Amplitude 0–100 (100 = full scale).
 * @return            ShortArray of PCM I16 samples, or null on failure.
 */
JNIEXPORT jshortArray JNICALL
Java_com_sdam_audio_GGWaveNative_nativeEncode(
    JNIEnv* env,
    jobject /*thiz*/,
    jlong   handle,
    jstring payload,
    jint    protocolId,
    jint    volume)
{
    if (handle < 0L) {
        LOGE("nativeEncode: invalid instance");
        return nullptr;
    }

    const char* payloadCStr = env->GetStringUTFChars(payload, nullptr);
    if (!payloadCStr) {
        LOGE("nativeEncode: GetStringUTFChars failed");
        return nullptr;
    }

    int payloadLen = static_cast<int>(std::strlen(payloadCStr));

    ggwave_Instance instance = ptrFromJLong(handle);

    // First call with outputBuffer=nullptr returns the required buffer size in bytes.
    int requiredBytes = ggwave_encode(
        instance,
        payloadCStr,
        payloadLen,
        static_cast<ggwave_ProtocolId>(protocolId),
        volume,
        nullptr,  // query mode
        1         // query = true
    );

    if (requiredBytes <= 0) {
        LOGW("nativeEncode: query returned %d (payload too long?)", requiredBytes);
        env->ReleaseStringUTFChars(payload, payloadCStr);
        return nullptr;
    }

    // Allocate buffer and actually encode.
    std::vector<char> outputBuffer(static_cast<size_t>(requiredBytes), 0);

    int encodedBytes = ggwave_encode(
        instance,
        payloadCStr,
        payloadLen,
        static_cast<ggwave_ProtocolId>(protocolId),
        volume,
        outputBuffer.data(),
        0  // encode = false (produce output)
    );

    env->ReleaseStringUTFChars(payload, payloadCStr);

    if (encodedBytes != requiredBytes) {
        LOGE("nativeEncode: expected %d bytes, got %d", requiredBytes, encodedBytes);
        return nullptr;
    }

    // The output is I16 samples — divide byte count by 2 to get sample count.
    int sampleCount = encodedBytes / 2;
    jshortArray result = env->NewShortArray(sampleCount);
    if (!result) {
        LOGE("nativeEncode: NewShortArray(%d) failed (OOM?)", sampleCount);
        return nullptr;
    }

    env->SetShortArrayRegion(result, 0, sampleCount,
        reinterpret_cast<const jshort*>(outputBuffer.data()));

    LOGI("nativeEncode OK  protocolId=%d  volume=%d  samples=%d", protocolId, volume, sampleCount);
    return result;
}

/**
 * Feed PCM I16 samples to the ggwave decoder.
 *
 * This function is designed to be called in a streaming loop: pass AudioRecord
 * buffers one at a time.  ggwave accumulates state internally across calls until
 * a full message has been received.
 *
 * @param handle   ggwave instance (from nativeInit).
 * @param samples  ShortArray of PCM I16 samples from AudioRecord.
 * @return         Decoded UTF-8 string if a complete message was received in
 *                 this batch; null if still accumulating or on error.
 */
JNIEXPORT jstring JNICALL
Java_com_sdam_audio_GGWaveNative_nativeDecode(
    JNIEnv* env,
    jobject /*thiz*/,
    jlong       handle,
    jshortArray samples)
{
    if (handle < 0L) {
        LOGE("nativeDecode: invalid instance");
        return nullptr;
    }

    jsize sampleCount = env->GetArrayLength(samples);
    if (sampleCount <= 0) return nullptr;

    jshort* sampleData = env->GetShortArrayElements(samples, nullptr);
    if (!sampleData) {
        LOGE("nativeDecode: GetShortArrayElements failed");
        return nullptr;
    }

    // Decode buffer: ggwave's max payload is ~200 bytes; add a safe margin.
    char outputBuf[512] = {};

    int result = ggwave_decode(
        ptrFromJLong(handle),
        sampleData,
        static_cast<int>(sampleCount * sizeof(jshort)),  // byte count
        outputBuf
    );

    env->ReleaseShortArrayElements(samples, sampleData, JNI_ABORT);

    if (result <= 0) {
        // 0 = no message yet; negative = error.
        return nullptr;
    }

    LOGI("nativeDecode OK  payload_len=%d", result);
    return env->NewStringUTF(outputBuf);
}

} // extern "C"
