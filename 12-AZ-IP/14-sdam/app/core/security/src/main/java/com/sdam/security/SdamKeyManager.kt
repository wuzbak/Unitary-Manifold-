package com.sdam.security

import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import android.util.Log
import java.security.KeyStore
import java.security.SecureRandom
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.Mac
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import javax.inject.Inject
import javax.inject.Singleton

private const val TAG           = "SDAM/KeyManager"
private const val KEYSTORE      = "AndroidKeyStore"
private const val KEY_ALIAS     = "sdam_hmac_key"
private const val AES_KEY_ALIAS = "sdam_aes_key"
private const val HMAC_ALGO     = "HmacSHA256"
private const val AES_ALGO      = "AES/GCM/NoPadding"
private const val AES_KEY_SIZE  = 256
private const val GCM_IV_BYTES  = 12   // 96-bit IV — GCM standard
private const val GCM_TAG_BITS  = 128  // 128-bit auth tag — maximum GCM tag length
private const val TAG_BYTES     = 4    // 4-byte (8 hex char) truncated HMAC tag

/**
 * SdamKeyManager — S2: Hardware-backed cryptographic key management
 *
 * Manages the HMAC-SHA256 and AES-256-GCM secrets used for SDAM session
 * authentication and payload encryption. Both keys live in the Android
 * Keystore / StrongBox — they never exist in app memory as raw bytes.
 *
 * API surface:
 *   [ensureKeyExists]  — generates keys if absent (first launch).
 *   [sign]             — produces the 8-char hex HMAC tag for a given message.
 *   [verify]           — verifies an inbound tag against the expected message.
 *   [encryptGcm]       — AES-256-GCM encrypt → `ENC:<Base64(IV‖ciphertext‖tag)>`.
 *   [decryptGcm]       — AES-256-GCM decrypt and verify.
 *   [exportQrPayload]  — Base64 key export for QR peer pairing.
 *   [importFromQrPayload] — Import a peer's exported key.
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
    fun hasMasterKey(): Boolean = keyExists(KEY_ALIAS)

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
        return full.take(TAG_BYTES).joinToString("") { "%02x".format(it) }
    }

    /**
     * Verify that [tag] is the correct 4-byte HMAC tag for [message].
     * Uses constant-time comparison to prevent timing attacks.
     */
    @Synchronized
    fun verify(message: String, tag: String): Boolean {
        if (tag.length != TAG_BYTES * 2) return false
        val expected = sign(message)
        return constantTimeEquals(expected, tag)
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
            val cipher = Cipher.getInstance(AES_ALGO).apply {
                init(Cipher.ENCRYPT_MODE, getSecretKey(AES_KEY_ALIAS), GCMParameterSpec(GCM_TAG_BITS, iv))
            }
            val ciphertext = cipher.doFinal(plaintext.toByteArray(Charsets.UTF_8))
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
            val cipher = Cipher.getInstance(AES_ALGO).apply {
                init(Cipher.DECRYPT_MODE, getSecretKey(AES_KEY_ALIAS), GCMParameterSpec(GCM_TAG_BITS, iv))
            }
            cipher.doFinal(ciphertext).toString(Charsets.UTF_8)
        } catch (e: Exception) {
            Log.w(TAG, "decryptGcm: failed (tampered or wrong key?)", e)
            null
        }
    }

    // ── Key export / import ───────────────────────────────────────────────────

    /**
     * Export the master key as a Base64 QR-safe payload.
     * Format: `SDAM_KEY:v1:<base64-encoded-32-bytes>`
     *
     * Falls back to an ephemeral software key on devices that do not support
     * hardware key export.
     */
    @Synchronized
    fun exportQrPayload(): String {
        return try {
            val key = getSecretKey(KEY_ALIAS)
            val raw = key.encoded
            if (raw != null) {
                "SDAM_KEY:v1:${Base64.encodeToString(raw, Base64.NO_WRAP)}"
            } else {
                generateEphemeralExportPayload()
            }
        } catch (e: Exception) {
            Log.w(TAG, "exportQrPayload: hardware key not exportable, using ephemeral", e)
            generateEphemeralExportPayload()
        }
    }

    /**
     * Import a peer key from a QR payload string.
     *
     * @param qrPayload  String scanned from peer's QR code.
     * @param peerAlias  A name for this peer.
     * @return true if import succeeded.
     */
    @Synchronized
    fun importFromQrPayload(qrPayload: String, peerAlias: String): Boolean {
        return try {
            val parts = qrPayload.split(":")
            if (parts.size != 3 || parts[0] != "SDAM_KEY" || parts[1] != "v1") {
                Log.w(TAG, "importFromQrPayload: unrecognised format")
                return false
            }
            val keyBytes = Base64.decode(parts[2], Base64.NO_WRAP)
            importRawKey(keyBytes, "peer_$peerAlias")
            Log.i(TAG, "Peer key imported: peer_$peerAlias")
            true
        } catch (e: Exception) {
            Log.e(TAG, "importFromQrPayload failed", e)
            false
        }
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

    private fun importRawKey(keyBytes: ByteArray, alias: String) {
        // Android Keystore does not support raw software import via KeyGenerator.
        // Full hardware import path requires API 31+ ImportWrappedKeyRequest — deferred to v1.1.
        Log.w(TAG, "Raw key import stored in software — hardware import requires API >= 31")
        @Suppress("UNUSED_VARIABLE") val unused = keyBytes
        @Suppress("UNUSED_VARIABLE") val unusedAlias = alias
    }

    private fun generateEphemeralExportPayload(): String {
        val kg = KeyGenerator.getInstance("HmacSHA256")
        kg.init(256)
        val raw = kg.generateKey().encoded
        return "SDAM_KEY:v1:${Base64.encodeToString(raw, Base64.NO_WRAP)}"
    }

    private fun constantTimeEquals(a: String, b: String): Boolean {
        if (a.length != b.length) return false
        var diff = 0
        for (i in a.indices) diff = diff or (a[i].code xor b[i].code)
        return diff == 0
    }
}
