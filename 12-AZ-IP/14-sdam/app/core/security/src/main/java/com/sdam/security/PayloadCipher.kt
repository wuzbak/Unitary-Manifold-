package com.sdam.security

import android.util.Log
import javax.inject.Inject
import javax.inject.Singleton

private const val TAG = "SDAM/PayloadCipher"

/**
 * PayloadCipher — S2
 *
 * Session-level AES-256-GCM payload encryption / decryption.
 *
 * Sits on top of [SdamKeyManager] and provides a clean API:
 *   - [encrypt]       wraps any payload string in `ENC:…` format
 *   - [decrypt]       strips `ENC:` and returns the plaintext
 *   - [isEncrypted]   tests whether a received payload was encrypted
 *
 * The AES key is managed through Android Keystore; hardware backing depends
 * on the device and is not verified by this application.
 * Per-call random IV is embedded in the wire payload.
 * The authenticated acoustic frame wraps `ENC:…` for integrity and replay protection.
 */
@Singleton
class PayloadCipher @Inject constructor(
    private val keyManager: SdamKeyManager,
) {
    /** True if the AES key is provisioned and encryption is available. */
    fun canEncrypt(): Boolean = keyManager.hasMasterKey()

    /**
     * Encrypt [payload] and return the `ENC:<base64>` wire string.
     *
     * @return `ENC:<Base64(IV ‖ ciphertext ‖ GCM-tag)>`, or null if not yet provisioned.
     */
    fun encrypt(payload: String): String? {
        val result = keyManager.encryptGcm(payload)
        if (result == null) {
            Log.w(TAG, "encrypt: encryptGcm returned null — key not ready?")
        }
        return result
    }

    /**
     * Decrypt an `ENC:…` payload.
     *
     * @return The original plaintext, or null on failure.
     */
    fun decrypt(encPayload: String): String? {
        val result = keyManager.decryptGcm(encPayload)
        if (result == null) {
            Log.w(TAG, "decrypt: GCM tag mismatch or bad format in \"${encPayload.take(40)}…\"")
        }
        return result
    }

    /** True if [payload] is an encrypted wire payload (starts with `ENC:`). */
    fun isEncrypted(payload: String): Boolean = payload.startsWith("ENC:")

    /** Encrypt [payload] unless it is already encrypted. Fails closed if no key exists. */
    fun encryptIfNeeded(payload: String): String? {
        if (isEncrypted(payload)) return payload
        return encrypt(payload)
    }

    /** Decrypt [payload] only when [isEncrypted] is true.  Pass-through otherwise. */
    fun decryptIfNeeded(payload: String): String? {
        return if (isEncrypted(payload)) decrypt(payload) else payload
    }
}
