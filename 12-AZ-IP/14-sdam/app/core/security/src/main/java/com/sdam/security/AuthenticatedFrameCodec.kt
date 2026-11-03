package com.sdam.security

import java.nio.ByteBuffer
import java.nio.charset.CodingErrorAction
import java.util.Base64

/**
 * Text framing for encrypted payloads sent through the acoustic modem.
 *
 * Wire format: `SDAM1:<counter>:<base64url(payload)>:<24-hex-char HMAC>`
 * The HMAC covers the exact prefix, counter, and encoded payload.
 */
object AuthenticatedFrameCodec {
    const val MAX_FRAME_BYTES = 140
    private const val PREFIX = "SDAM1"
    private val tagPattern = Regex("[0-9a-f]{24}")

    data class Accepted(val counter: Long, val payload: String)

    sealed interface Result {
        data class Valid(val frame: Accepted) : Result
        data class Invalid(val reason: String) : Result
    }

    fun encode(payload: String, counter: Long, sign: (String) -> String): String {
        require(counter >= 0) { "counter must be non-negative" }
        require(payload.isNotEmpty()) { "payload must not be empty" }
        val body = Base64.getUrlEncoder().withoutPadding()
            .encodeToString(payload.toByteArray(Charsets.UTF_8))
        val authenticated = "$PREFIX:$counter:$body"
        val tag = sign(authenticated)
        require(tagPattern.matches(tag)) { "signer must return a 24-character lowercase hex tag" }
        val frame = "$authenticated:$tag"
        require(frame.toByteArray(Charsets.UTF_8).size <= MAX_FRAME_BYTES) {
            "frame exceeds the ggwave payload limit of $MAX_FRAME_BYTES bytes"
        }
        return frame
    }

    /**
     * Replay high-water mark exists only for this verifier instance. It is not
     * persisted and must not be treated as restart-resistant replay protection.
     */
    class Verifier(private val verifyTag: (String, String) -> Boolean) {
        private var lastCounter = -1L

        @Synchronized
        fun verify(raw: String): Result {
            if (raw.toByteArray(Charsets.UTF_8).size > MAX_FRAME_BYTES) {
                return Result.Invalid("Frame exceeds the ggwave payload limit")
            }
            val fields = raw.split(':')
            if (fields.size != 4 || fields[0] != PREFIX) {
                return Result.Invalid("Malformed or unsupported frame")
            }
            val counter = fields[1].toLongOrNull()
                ?: return Result.Invalid("Invalid frame counter")
            if (counter < 0) return Result.Invalid("Invalid frame counter")
            val tag = fields[3]
            if (!tagPattern.matches(tag)) return Result.Invalid("Malformed authentication tag")
            val authenticated = fields.take(3).joinToString(":")
            val authenticatedTag = try {
                verifyTag(authenticated, tag)
            } catch (_: Exception) {
                return Result.Invalid("Authentication unavailable")
            }
            if (!authenticatedTag) return Result.Invalid("Authentication failed")
            if (counter <= lastCounter) return Result.Invalid("Replayed frame")

            val bytes = try {
                Base64.getUrlDecoder().decode(fields[2])
            } catch (_: IllegalArgumentException) {
                return Result.Invalid("Malformed frame payload")
            }
            val payload = try {
                Charsets.UTF_8.newDecoder()
                    .onMalformedInput(CodingErrorAction.REPORT)
                    .onUnmappableCharacter(CodingErrorAction.REPORT)
                    .decode(ByteBuffer.wrap(bytes))
                    .toString()
            } catch (_: Exception) {
                return Result.Invalid("Frame payload is not valid UTF-8")
            }
            if (payload.isEmpty()) return Result.Invalid("Empty frame payload")
            lastCounter = counter
            return Result.Valid(Accepted(counter, payload))
        }
    }
}
