package com.sdam.security

import javax.crypto.Cipher
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

internal object GcmPayloadCodec {
    private const val TRANSFORMATION = "AES/GCM/NoPadding"
    private const val TAG_BITS = 128
    const val IV_BYTES = 12

    fun encrypt(plaintext: ByteArray, key: SecretKey, iv: ByteArray): ByteArray {
        require(iv.size == IV_BYTES) { "AES-GCM requires a 12-byte IV" }
        val cipher = Cipher.getInstance(TRANSFORMATION).apply {
            init(Cipher.ENCRYPT_MODE, key, GCMParameterSpec(TAG_BITS, iv))
        }
        return cipher.doFinal(plaintext)
    }

    fun decrypt(ciphertextAndTag: ByteArray, key: SecretKey, iv: ByteArray): ByteArray {
        require(iv.size == IV_BYTES) { "AES-GCM requires a 12-byte IV" }
        val cipher = Cipher.getInstance(TRANSFORMATION).apply {
            init(Cipher.DECRYPT_MODE, key, GCMParameterSpec(TAG_BITS, iv))
        }
        return cipher.doFinal(ciphertextAndTag)
    }
}
