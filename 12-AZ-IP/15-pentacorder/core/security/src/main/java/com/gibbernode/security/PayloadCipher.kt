package com.gibbernode.security

import android.util.Log
import javax.inject.Inject
import javax.inject.Singleton

private const val TAG = "GibberNode/PayloadCipher"

/**
 * PayloadCipher
 *
 * Session-level AES-256-GCM payload encryption / decryption for Gibberlink BLUE mode.
 *
 * This class sits on top of [GibberKeyManager] and provides a clean API:
 *   - [encrypt] wraps any Gibberlink payload string in `ENC:…` format
 *   - [decrypt] strips the `ENC:` prefix and returns the plaintext
 *   - [isEncrypted] tests whether a received payload was encrypted
 *
 * Security model (matches SECURITY.md §6):
 *   - AES-256-GCM provides both confidentiality *and* integrity (authenticated
 *     encryption).  The GCM tag covers the IV + ciphertext and is verified on
 *     every decrypt call.  Any bit-flip or truncation returns null, not garbage.
 *   - The key lives in Android Keystore / StrongBox — it never appears in app
 *     heap memory as raw bytes.
 *   - Per-call random IV is embedded in the wire payload so the receiver never
 *     needs out-of-band state.
 *   - The HMAC layer ([AcousticAuth]) still wraps the `ENC:…` outer payload,
 *     providing replay protection via the rolling counter.  Use both layers for
 *     BLUE mode transfers:
 *
 *         AcousticAuth.signPayload(PayloadCipher.encrypt("VITALS:72:98:36.6"))
 *         → "ENC:<base64>:{counter}:{hmac}"
 *
 * Usage note:
 *   Encryption is optional per session.  Call [canEncrypt] first; it returns
 *   false until [GibberKeyManager.ensureKeyExists] has been called (normally
 *   at app startup via [AppModule]).
 */
@Singleton
class PayloadCipher @Inject constructor(
    private val keyManager: GibberKeyManager,
) {

    /**
     * True if the AES key is provisioned and encryption is available.
     * Always true after [AppModule] runs [GibberKeyManager.ensureKeyExists].
     */
    fun canEncrypt(): Boolean = keyManager.hasMasterKey()

    /**
     * Encrypt [payload] and return the `ENC:<base64>` wire string.
     *
     * @param payload  A plain Gibberlink payload string (e.g. "VITALS:72:98:36.6").
     * @return         `ENC:<Base64(IV ‖ ciphertext ‖ GCM-tag)>`, or null if the
     *                 Keystore AES key is not yet provisioned.
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
     * @param encPayload  The `ENC:<base64>` string from [encrypt].
     * @return            The original plaintext payload, or null if decryption
     *                    fails (wrong key, tampered ciphertext, or bad format).
     */
    fun decrypt(encPayload: String): String? {
        val result = keyManager.decryptGcm(encPayload)
        if (result == null) {
            Log.w(TAG, "decrypt: GCM tag mismatch or bad format in \"${encPayload.take(40)}…\"")
        }
        return result
    }

    /**
     * True if [payload] is an encrypted wire payload (starts with `ENC:`).
     * Callers can use this to decide whether to decrypt before dispatching.
     */
    fun isEncrypted(payload: String): Boolean = payload.startsWith("ENC:")

    /**
     * Encrypt [payload] only when [isEncrypted] is false, and only when
     * encryption is available.  Pass-through otherwise.
     *
     * Convenience wrapper for callers that may receive a mix of plain and
     * encrypted payloads in the same channel.
     */
    fun encryptIfNeeded(payload: String): String {
        if (isEncrypted(payload)) return payload
        return encrypt(payload) ?: payload.also {
            Log.w(TAG, "encryptIfNeeded: falling back to plaintext (key not ready)")
        }
    }

    /**
     * Decrypt [payload] only when [isEncrypted] is true.  Pass-through otherwise.
     */
    fun decryptIfNeeded(payload: String): String? {
        return if (isEncrypted(payload)) decrypt(payload) else payload
    }
}
