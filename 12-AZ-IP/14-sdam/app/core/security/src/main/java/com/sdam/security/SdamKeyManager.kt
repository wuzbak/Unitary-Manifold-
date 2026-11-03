package com.sdam.security

import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import android.util.Log
import java.security.KeyStore
import java.security.SecureRandom
import javax.crypto.KeyGenerator
import javax.crypto.Mac
import javax.crypto.SecretKey
import javax.inject.Inject
import javax.inject.Singleton

private const val TAG           = "SDAM/KeyManager"
private const val KEYSTORE      = "AndroidKeyStore"
private const val KEY_ALIAS     = "sdam_hmac_key"
private const val AES_KEY_ALIAS = "sdam_aes_key"
private const val HMAC_ALGO     = "HmacSHA256"
private const val AES_KEY_SIZE  = 256
private const val GCM_IV_BYTES  = GcmPayloadCodec.IV_BYTES
private const val LEGACY_TAG_BYTES = 4
private const val FRAME_TAG_BYTES  = 12

/**
 * SdamKeyManager — S2: Android Keystore cryptographic key management
 *
 * Manages the HMAC-SHA256 and AES-256-GCM secrets used for SDAM session
 * authentication and payload encryption. The app does not verify whether a
 * device stores these keys in secure hardware. Cross-device QR provisioning
 * is not implemented.
 *
 * API surface:
 *   [ensureKeyExists]  — generates keys if absent (first launch).
 *   [sign]             — produces a legacy 8-char hex HMAC tag.
 *   [verify]           — verifies a legacy 8-char hex HMAC tag.
 *   [signFrame]        — produces a 24-char hex HMAC tag for SDAM1 frames.
 *   [verifyFrame]      — verifies a 24-char hex HMAC tag for SDAM1 frames.
 *   [encryptGcm]       — AES-256-GCM encrypt → `ENC:<Base64(IV‖ciphertext‖tag)>`.
 *   [decryptGcm]       — AES-256-GCM decrypt and verify.
 *   [exportQrPayload]  — fails explicitly because key export is unsupported.
 *   [importFromQrPayload] — returns false because key import is unsupported.
 */
@Singleton
class SdamKeyManager @Inject constructor() {

    // ── Key provisioning ───────────────────────────────────────────────────────

    /**
     * Ensure both the HMAC key and the AES-256-GCM key exist in Keystore.
     * Safe to call on every app start — no-ops for keys that are already present.
     */
    @Synchronized
    fun ensureKeyExists() {
        if (!keyExists(KEY_ALIAS)) {
            generateHmacKey(KEY_ALIAS)
            Log.i(TAG, "Master HMAC key generated: alias=$KEY_ALIAS")
        }
        if (!keyExists(AES_KEY_ALIAS)) {
            generateAesKey(AES_KEY_ALIAS)
            Log.i(TAG, "AES-256-GCM key generated: alias=$AES_KEY_ALIAS")
        }
    }

    /** True if the master HMAC key has been provisioned. */
    @Synchronized
    fun hasMasterKey(): Boolean = keyExists(KEY_ALIAS) && keyExists(AES_KEY_ALIAS)

    // ── HMAC operations ────────────────────────────────────────────────────────

    /**
     * Compute a 4-byte (8 hex char) HMAC-SHA256 tag over [message].
     *
     * @param message  The bytes to authenticate.
     * @return         8-character lowercase hex string.
     */
    @Synchronized
    fun sign(message: String): String {
        val mac  = getMac(KEY_ALIAS)
        val full = mac.doFinal(message.toByteArray(Charsets.UTF_8))
        return full.take(LEGACY_TAG_BYTES).joinToString("") { "%02x".format(it) }
    }

    /**
     * Verify that [tag] is the correct 4-byte HMAC tag for [message].
     * Uses constant-time comparison to prevent timing attacks.
     */
    @Synchronized
    fun verify(message: String, tag: String): Boolean {
        if (tag.length != LEGACY_TAG_BYTES * 2) return false
        val expected = sign(message)
        return constantTimeEquals(expected, tag)
    }

    /** Compute the 96-bit HMAC-SHA256 tag used only by SDAM1 frames. */
    @Synchronized
    fun signFrame(message: String): String {
        val full = getMac(KEY_ALIAS).doFinal(message.toByteArray(Charsets.UTF_8))
        return full.take(FRAME_TAG_BYTES).joinToString("") { "%02x".format(it) }
    }

    /** Verify an SDAM1 frame's 24-character, 96-bit lowercase hexadecimal tag. */
    @Synchronized
    fun verifyFrame(message: String, tag: String): Boolean {
        if (tag.length != FRAME_TAG_BYTES * 2) return false
        if (!tag.all { it in '0'..'9' || it in 'a'..'f' }) return false
        return constantTimeEquals(signFrame(message), tag)
    }

    // ── AES-256-GCM payload encryption ────────────────────────────────────────

    /**
     * Encrypt [plaintext] with AES-256-GCM.
     *
     * Wire format: `ENC:<Base64(IV[12] ‖ ciphertext ‖ GCM-tag[16])>`
     */
    @Synchronized
    fun encryptGcm(plaintext: String): String? {
        return try {
            val iv = ByteArray(GCM_IV_BYTES).also { SecureRandom().nextBytes(it) }
            val ciphertext = GcmPayloadCodec.encrypt(
                plaintext.toByteArray(Charsets.UTF_8),
                getSecretKey(AES_KEY_ALIAS),
                iv,
            )
            val combined = iv + ciphertext
            "ENC:${Base64.encodeToString(combined, Base64.NO_WRAP)}"
        } catch (e: Exception) {
            Log.e(TAG, "encryptGcm failed", e)
            null
        }
    }

    /**
     * Decrypt an `ENC:…` wire payload.
     *
     * @return  The decrypted plaintext, or null if decryption or GCM tag verification fails.
     */
    @Synchronized
    fun decryptGcm(encPayload: String): String? {
        if (!encPayload.startsWith("ENC:")) {
            Log.w(TAG, "decryptGcm: not an ENC payload")
            return null
        }
        return try {
            val combined = Base64.decode(encPayload.removePrefix("ENC:"), Base64.NO_WRAP)
            if (combined.size < GCM_IV_BYTES + 1) {
                Log.w(TAG, "decryptGcm: payload too short")
                return null
            }
            val iv         = combined.sliceArray(0 until GCM_IV_BYTES)
            val ciphertext = combined.sliceArray(GCM_IV_BYTES until combined.size)
            GcmPayloadCodec.decrypt(ciphertext, getSecretKey(AES_KEY_ALIAS), iv)
                .toString(Charsets.UTF_8)
        } catch (e: Exception) {
            Log.w(TAG, "decryptGcm: failed (tampered or wrong key?)", e)
            null
        }
    }

    // ── Key export / import ───────────────────────────────────────────────────

    /**
     * Cross-device key export is not supported by the current provisioning flow.
     *
     * @throws UnsupportedOperationException because exporting an unrelated
     *         ephemeral key would falsely imply that peers can communicate.
     */
    @Synchronized
    fun exportQrPayload(): String {
        throw UnsupportedOperationException(
            "Cross-device key export is not implemented; no key was exported."
        )
    }

    /**
     * Cross-device key import is unsupported until a secure provisioning flow
     * exists. No key material is imported.
     */
    @Synchronized
    @Suppress("UNUSED_PARAMETER")
    fun importFromQrPayload(qrPayload: String, peerAlias: String): Boolean {
        Log.e(TAG, "Cross-device key import is not implemented; no key was imported.")
        return false
    }

    // ── Internal helpers ───────────────────────────────────────────────────────

    private fun keyExists(alias: String): Boolean {
        val ks = KeyStore.getInstance(KEYSTORE).apply { load(null) }
        return ks.containsAlias(alias)
    }

    private fun generateHmacKey(alias: String) {
        val spec = KeyGenParameterSpec.Builder(
            alias,
            KeyProperties.PURPOSE_SIGN or KeyProperties.PURPOSE_VERIFY
        )
            .setKeySize(256)
            .setDigests(KeyProperties.DIGEST_SHA256)
            .build()
        val kg = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_HMAC_SHA256, KEYSTORE)
        kg.init(spec)
        kg.generateKey()
    }

    private fun generateAesKey(alias: String) {
        val spec = KeyGenParameterSpec.Builder(
            alias,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT,
        )
            .setKeySize(AES_KEY_SIZE)
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setRandomizedEncryptionRequired(false) // we supply our own IV
            .build()
        val kg = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, KEYSTORE)
        kg.init(spec)
        kg.generateKey()
    }

    private fun getSecretKey(alias: String): SecretKey {
        val ks = KeyStore.getInstance(KEYSTORE).apply { load(null) }
        return (ks.getEntry(alias, null) as KeyStore.SecretKeyEntry).secretKey
    }

    private fun getMac(alias: String): Mac {
        val key = getSecretKey(alias)
        return Mac.getInstance(HMAC_ALGO).apply { init(key) }
    }

    private fun constantTimeEquals(a: String, b: String): Boolean {
        if (a.length != b.length) return false
        var diff = 0
        for (i in a.indices) diff = diff or (a[i].code xor b[i].code)
        return diff == 0
    }
}
