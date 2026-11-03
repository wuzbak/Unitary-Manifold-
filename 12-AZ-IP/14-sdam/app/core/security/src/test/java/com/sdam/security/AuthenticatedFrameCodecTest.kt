package com.sdam.security

import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class AuthenticatedFrameCodecTest {
    private val key = ByteArray(32) { it.toByte() }

    private fun sign(message: String): String {
        val mac = Mac.getInstance("HmacSHA256")
        mac.init(SecretKeySpec(key, "HmacSHA256"))
        return mac.doFinal(message.toByteArray(Charsets.UTF_8))
            .take(12).joinToString("") { "%02x".format(it) }
    }

    private fun verifier() = AuthenticatedFrameCodec.Verifier { message, tag ->
        sign(message) == tag
    }

    @Test
    fun encodes_deterministic_utf8_frame_and_authenticates_it() {
        val frame = AuthenticatedFrameCodec.encode("ENC:payload", 42, ::sign)
        val tag = frame.substringAfterLast(':')
        assertEquals(24, tag.length)
        assertTrue(tag.matches(Regex("[0-9a-f]{24}")))
        assertEquals(
            "SDAM1:42:RU5DOnBheWxvYWQ",
            frame.substringBeforeLast(':'),
        )
        val verified = verifier().verify(frame) as AuthenticatedFrameCodec.Result.Valid
        assertEquals(42L, verified.frame.counter)
        assertEquals("ENC:payload", verified.frame.payload)
    }

    @Test
    fun rejects_modified_payload_and_tag() {
        val frame = AuthenticatedFrameCodec.encode("ENC:payload", 42, ::sign)
        val fields = frame.split(':').toMutableList()
        fields[2] = fields[2].dropLast(1) + if (fields[2].last() == 'A') "B" else "A"
        val tampered = fields.joinToString(":")
        assertTrue(verifier().verify(tampered) is AuthenticatedFrameCodec.Result.Invalid)
        val badTag = frame.dropLast(1) + if (frame.last() == '0') "1" else "0"
        assertEquals(
            "Authentication failed",
            (verifier().verify(badTag) as AuthenticatedFrameCodec.Result.Invalid).reason,
        )
    }

    @Test
    fun rejects_wrong_size_tags_for_encoding_and_verification() {
        listOf(8, 23, 25, 26).forEach { size ->
            val badTag = "a".repeat(size)
            val encodeError = runCatching {
                AuthenticatedFrameCodec.encode("ENC:payload", 42) { badTag }
            }.exceptionOrNull()
            assertEquals(
                "signer must return a 24-character lowercase hex tag",
                encodeError?.message,
            )
            val malformed = "SDAM1:42:RU5DOnBheWxvYWQ:$badTag"
            assertEquals(
                "Malformed authentication tag",
                (verifier().verify(malformed) as AuthenticatedFrameCodec.Result.Invalid).reason,
            )
        }
    }

    @Test
    fun rejects_replayed_frame_and_malformed_wire_data() {
        val frame = AuthenticatedFrameCodec.encode("ENC:payload", 42, ::sign)
        val verifier = verifier()
        assertTrue(verifier.verify(frame) is AuthenticatedFrameCodec.Result.Valid)
        assertEquals(
            "Replayed frame",
            (verifier.verify(frame) as AuthenticatedFrameCodec.Result.Invalid).reason,
        )
        assertTrue(
            "A new verifier has no persisted high-water mark",
            AuthenticatedFrameCodec.Verifier { message, tag -> sign(message) == tag }
                .verify(frame) is AuthenticatedFrameCodec.Result.Valid,
        )
        assertTrue(verifier().verify("not-a-frame") is AuthenticatedFrameCodec.Result.Invalid)
    }

    @Test
    fun reports_authentication_unavailable_without_accepting_frame() {
        val frame = AuthenticatedFrameCodec.encode("ENC:payload", 42, ::sign)
        val result = AuthenticatedFrameCodec.Verifier { _, _ ->
            error("keystore unavailable")
        }.verify(frame)
        assertEquals(
            "Authentication unavailable",
            (result as AuthenticatedFrameCodec.Result.Invalid).reason,
        )
    }

    @Test
    fun rejects_frames_larger_than_native_payload_limit() {
        val error = runCatching {
            AuthenticatedFrameCodec.encode("ENC:${"x".repeat(200)}", 42, ::sign)
        }.exceptionOrNull()
        assertEquals(
            "frame exceeds the ggwave payload limit of 140 bytes",
            error?.message,
        )
        val oversizedWire = "SDAM1:42:${"A".repeat(150)}:00000000"
        assertEquals(
            "Frame exceeds the ggwave payload limit",
            (verifier().verify(oversizedWire) as AuthenticatedFrameCodec.Result.Invalid).reason,
        )
    }
}
