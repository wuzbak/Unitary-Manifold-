package com.sdam.security

import java.util.Base64
import java.nio.ByteBuffer
import javax.crypto.spec.SecretKeySpec
import javax.crypto.Mac
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class SecureMessageRoundTripTest {
    private val aesKey = SecretKeySpec(ByteArray(32) { (it + 1).toByte() }, "AES")
    private val hmacKey = ByteArray(32) { (it + 31).toByte() }
    private val iv = ByteArray(GcmPayloadCodec.IV_BYTES) { it.toByte() }
    private var nonceCounter = 0L

    private fun encryptChunk(plaintext: String): String? {
        val nonce = ByteArray(GcmPayloadCodec.IV_BYTES).also {
            ByteBuffer.wrap(it).putLong(nonceCounter++)
        }
        val ciphertext = GcmPayloadCodec.encrypt(plaintext.toByteArray(Charsets.UTF_8), aesKey, nonce)
        return "ENC:" + Base64.getEncoder().encodeToString(nonce + ciphertext)
    }

    private fun sign(message: String): String {
        val mac = Mac.getInstance("HmacSHA256")
        mac.init(SecretKeySpec(hmacKey, "HmacSHA256"))
        return mac.doFinal(message.toByteArray(Charsets.UTF_8))
            .take(12).joinToString("") { "%02x".format(it) }
    }

    @Test
    fun encrypts_frames_authenticates_and_decrypts_message() {
        val plaintext = "secure audio"
        val encryptedBytes = GcmPayloadCodec.encrypt(
            plaintext.toByteArray(Charsets.UTF_8),
            aesKey,
            iv,
        )
        val encryptedPayload = "ENC:" + Base64.getEncoder().encodeToString(iv + encryptedBytes)
        val wireFrame = AuthenticatedFrameCodec.encode(encryptedPayload, 7, ::sign)
        val verified = AuthenticatedFrameCodec.Verifier { message, tag ->
            sign(message) == tag
        }.verify(wireFrame) as AuthenticatedFrameCodec.Result.Valid

        assertEquals(
            plaintext,
            decryptPayload(verified.frame.payload).toString(Charsets.UTF_8),
        )
    }

    @Test
    fun rejects_modified_gcm_ciphertext_even_when_frame_is_resigned() {
        val encryptedBytes = GcmPayloadCodec.encrypt("secret".toByteArray(), aesKey, iv)
        val changed = encryptedBytes.copyOf().also { it[0] = (it[0].toInt() xor 1).toByte() }
        val encryptedPayload = "ENC:" + Base64.getEncoder().encodeToString(iv + changed)
        val resignedFrame = AuthenticatedFrameCodec.encode(encryptedPayload, 8, ::sign)
        val verified = AuthenticatedFrameCodec.Verifier { message, tag ->
            sign(message) == tag
        }.verify(resignedFrame) as AuthenticatedFrameCodec.Result.Valid

        val failure = runCatching { decryptPayload(verified.frame.payload) }.exceptionOrNull()
        assertTrue("GCM must reject tampered ciphertext", failure != null)
    }

    @Test
    fun secure_diode_chunk_fits_native_frame_limit_at_maximum_counter_size() {
        var nonceCounter = 0L
        val chunks = AirGapBridge.encode("x".repeat(AirGapBridge.MAX_MESSAGE_UTF8_BYTES)) {
            val nonce = ByteArray(GcmPayloadCodec.IV_BYTES).also {
                ByteBuffer.wrap(it).putLong(nonceCounter++)
            }
            val encrypted = GcmPayloadCodec.encrypt(it.toByteArray(Charsets.UTF_8), aesKey, nonce)
            "ENC:" + Base64.getEncoder().encodeToString(nonce + encrypted)
        }
        assertEquals(AirGapBridge.MAX_CHUNKS, chunks.size)
        val largestChunk = chunks.last()
        assertTrue(largestChunk.startsWith("DIODE:998:999:"))
        val frame = AuthenticatedFrameCodec.encode(largestChunk, Long.MAX_VALUE, ::sign)
        assertEquals(139, frame.toByteArray(Charsets.UTF_8).size)
        assertTrue(frame.toByteArray(Charsets.UTF_8).size <= AuthenticatedFrameCodec.MAX_FRAME_BYTES)
        assertTrue(
            runCatching {
                AirGapBridge.encode("x".repeat(AirGapBridge.MAX_MESSAGE_UTF8_BYTES + 1)) {
                    "ENC:unused"
                }
            }.isFailure
        )
    }

    @Test
    fun diode_rejects_multibyte_input_that_would_exceed_three_digit_chunk_headers() {
        val error = runCatching {
            AirGapBridge.encode("🔒x".repeat(1_000)) { "ENC:" + "A".repeat(48) }
        }.exceptionOrNull()
        assertEquals("DIODE messages are limited to 999 chunks", error?.message)
    }

    @Test
    fun diode_chunks_utf8_without_splitting_codepoints_and_frames_fit_native_limit() {
        val original = "a".repeat(8) + "🔒" + "z".repeat(8)
        val chunks = AirGapBridge.encode(original) { part ->
            val encrypted = GcmPayloadCodec.encrypt(part.toByteArray(Charsets.UTF_8), aesKey, iv)
            "ENC:" + Base64.getEncoder().encodeToString(iv + encrypted)
        }
        val recovered = chunks.map { chunk ->
            val fields = chunk.split(':', limit = 4)
            val combined = Base64.getDecoder().decode(fields[3].removePrefix("ENC:"))
            GcmPayloadCodec.decrypt(
                combined.copyOfRange(GcmPayloadCodec.IV_BYTES, combined.size),
                aesKey,
                combined.copyOfRange(0, GcmPayloadCodec.IV_BYTES),
            ).toString(Charsets.UTF_8)
        }.joinToString("")

        assertEquals(original, recovered)
        chunks.forEachIndexed { index, chunk ->
            val frame = AuthenticatedFrameCodec.encode(chunk, index + 1L, ::sign)
            assertTrue(frame.toByteArray(Charsets.UTF_8).size <= AuthenticatedFrameCodec.MAX_FRAME_BYTES)
        }
    }

    @Test
    fun standard_secure_fragments_round_trip_multibyte_utf8_through_authenticated_frames() {
        val original = "A🔒message with several independently encrypted fragments"
        val chunks = AirGapBridge.encodeMessage(original, ::encryptChunk, "0123abcd")
        assertTrue(chunks.size > 1)
        assertTrue(chunks.all { it.startsWith("MSG:0123abcd:") })

        val verifier = AuthenticatedFrameCodec.Verifier { message, tag -> sign(message) == tag }
        val assembler = AirGapBridge.MessageAssembler()
        var result: AirGapBridge.FragmentResult? = null
        chunks.forEachIndexed { index, fragment ->
            val frame = AuthenticatedFrameCodec.encode(fragment, index + 1L, ::sign)
            val verified = verifier.verify(frame) as AuthenticatedFrameCodec.Result.Valid
            result = assembler.feed(verified.frame.payload) { decryptPayload(it).toString(Charsets.UTF_8) }
        }
        val complete = result as AirGapBridge.FragmentResult.Complete
        assertEquals(original, complete.message)
        assertEquals(chunks.size, complete.total)
        assertTrue(!complete.debug)
    }

    @Test
    fun standard_secure_reports_incomplete_and_rejects_malformed_or_mixed_fragments() {
        val firstMessage = AirGapBridge.encodeMessage("first message", ::encryptChunk, "11112222")
        val otherMessage = AirGapBridge.encodeMessage("second message", ::encryptChunk, "33334444")
        val assembler = AirGapBridge.MessageAssembler()
        assertTrue(
            assembler.feed(firstMessage.first()) { decryptPayload(it).toString(Charsets.UTF_8) }
                is AirGapBridge.FragmentResult.Incomplete
        )
        assertTrue(
            assembler.feed("MSG:bad-id:0:2:invalid") { null }
                is AirGapBridge.FragmentResult.Invalid
        )
        assertTrue(
            assembler.feed(otherMessage.last()) { decryptPayload(it).toString(Charsets.UTF_8) }
                is AirGapBridge.FragmentResult.Incomplete
        )
        assertTrue(
            assembler.feed(firstMessage.last()) { decryptPayload(it).toString(Charsets.UTF_8) }
                is AirGapBridge.FragmentResult.Incomplete
        )
    }

    @Test
    fun standard_secure_maximum_message_and_maximum_header_fit_frame_limit() {
        nonceCounter = 0
        val chunks = AirGapBridge.encodeMessage(
            "x".repeat(AirGapBridge.MAX_STANDARD_MESSAGE_UTF8_BYTES),
            ::encryptChunk,
            "a1b2c3d4",
        )
        assertEquals(AirGapBridge.MAX_CHUNKS, chunks.size)
        val maximumHeader = chunks.last()
        assertTrue(maximumHeader.startsWith("MSG:a1b2c3d4:998:999:"))
        val frame = AuthenticatedFrameCodec.encode(maximumHeader, Long.MAX_VALUE, ::sign)
        assertEquals(138, frame.toByteArray(Charsets.UTF_8).size)
        assertTrue(frame.toByteArray(Charsets.UTF_8).size <= AuthenticatedFrameCodec.MAX_FRAME_BYTES)
        assertTrue(
            runCatching {
                AirGapBridge.encodeMessage(
                    "x".repeat(AirGapBridge.MAX_STANDARD_MESSAGE_UTF8_BYTES + 1),
                    ::encryptChunk,
                    "a1b2c3d4",
                )
            }.isFailure
        )
    }

    @Test
    fun standard_secure_rejects_invalid_sequence_or_missing_decryption() {
        val assembler = AirGapBridge.MessageAssembler()
        val malformed = assembler.feed("MSG:01020304:1:1:AAAA") { null }
        assertTrue(malformed is AirGapBridge.FragmentResult.Invalid)
        val noKey = AirGapBridge.encodeMessage("hello", ::encryptChunk, "01020304").single()
        assertTrue(
            assembler.feed(noKey) { null } is AirGapBridge.FragmentResult.Invalid
        )
    }

    @Test
    fun explicit_debug_message_fragments_remain_distinguishable_from_ciphertext() {
        val fragments = AirGapBridge.encodeMessage("debug-only text", { "DBG:$it" }, "feedcafe")
        val assembler = AirGapBridge.MessageAssembler()
        var result: AirGapBridge.FragmentResult? = null
        fragments.forEach { fragment ->
            result = assembler.feed(fragment) { chunk ->
                chunk.removePrefix("DBG:")
            }
        }
        val complete = result as AirGapBridge.FragmentResult.Complete
        assertEquals("debug-only text", complete.message)
        assertTrue(complete.debug)
    }

    private fun decryptPayload(payload: String): ByteArray {
        val bytes = Base64.getDecoder().decode(payload.removePrefix("ENC:"))
        val nonce = bytes.copyOfRange(0, GcmPayloadCodec.IV_BYTES)
        val ciphertext = bytes.copyOfRange(GcmPayloadCodec.IV_BYTES, bytes.size)
        return GcmPayloadCodec.decrypt(ciphertext, aesKey, nonce)
    }
}
