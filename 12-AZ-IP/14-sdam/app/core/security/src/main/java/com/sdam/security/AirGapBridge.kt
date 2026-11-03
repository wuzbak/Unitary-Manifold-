package com.sdam.security

import java.security.SecureRandom
import java.util.Base64

/**
 * AirGapBridge — S6: Encrypted Acoustic Data Diode
 *
 * One-way, MTU-aware encrypted acoustic channel for crossing physical air gaps.
 *
 * Wire formats:
 *   `DIODE:{seq}:{total}:{enc_chunk}` (legacy DIODE format)
 *   `MSG:{id}:{seq}:{total}:{base64url_gcm_chunk}` (Standard/Secure format)
 *
 *   seq    — 0-based chunk index
 *   total  — total number of chunks in this transmission
 *   enc    — AES-256-GCM encrypted portion of the plaintext (`ENC:…` string)
 *
 * Each chunk is independently encrypted so a tampered or dropped chunk does
 * NOT allow the receiver to reconstruct adjacent plaintext.
 *
 * Security properties:
 *   - AES-256-GCM: confidentiality + integrity per chunk
 *   - Independent per-chunk IVs: random, never reused
 *   - HMAC-SHA256 outer layer (added by [AuthenticatedFrameCodec]) with
 *     per-verifier, in-memory replay rejection (not restart-resistant)
 *
 * This class is pure JVM — no Android SDK dependency — enabling JVM unit tests
 * without an emulator or Keystore.
 */
object AirGapBridge {
    private const val DIODE_CHUNK_PLAINTEXT_BYTES = 8
    private const val MESSAGE_CHUNK_PLAINTEXT_BYTES = 5
    private const val DIODE_PREFIX = "DIODE"
    private const val MESSAGE_PREFIX = "MSG"
    private const val MESSAGE_ID_HEX_CHARS = 8
    private val messageIdRandom = SecureRandom()

    /**
     * Maximum number of characters for a DIODE chunk payload after the
     * `DIODE:seq:total:` prefix.
     */
    const val MTU_CHARS = 128
    const val MAX_CHUNKS = 999
    const val MAX_MESSAGE_UTF8_BYTES = DIODE_CHUNK_PLAINTEXT_BYTES * MAX_CHUNKS
    const val MAX_STANDARD_MESSAGE_UTF8_BYTES = MESSAGE_CHUNK_PLAINTEXT_BYTES * MAX_CHUNKS

    /**
     * Maximum plaintext UTF-8 bytes per chunk before encryption.
     *
     * AES-256-GCM adds 12-byte IV + 16-byte GCM tag = 28 bytes of overhead.
     * Base64 encoding expands by ~4/3.
     * The encrypted chunk is then wrapped in an authenticated SDAM1 frame.
     * Eight UTF-8 bytes leave room for both Base64 layers, a three-digit DIODE
     * header, the maximum 64-bit counter, and a 96-bit HMAC under ggwave's
     * 140-byte payload limit.
     */
    // ── TX (encode) ────────────────────────────────────────────────────────────

    /**
     * Encode [plaintext] into independently encrypted `DIODE:seq:total:enc` chunks.
     *
     * @param plaintext  UTF-8 string to transmit (any length).
     * @param encrypt    Function that encrypts a plain string → `ENC:…`.
     * @return           List of payload strings to broadcast in order.
     * @throws IllegalStateException if [encrypt] returns null (key not ready).
     */
    fun encode(
        plaintext: String,
        encrypt: (String) -> String?,
    ): List<String> = encodeWithPrefix(
        prefix = DIODE_PREFIX,
        plaintext = plaintext,
        label = "DIODE messages",
        chunkBytes = DIODE_CHUNK_PLAINTEXT_BYTES,
        encrypt = encrypt,
    )

    /**
     * Fragment a Standard/Secure message under the distinct `MSG` wire prefix.
     * Each fragment is independently encrypted; SDAM1 authenticates each frame.
     */
    fun encodeMessage(
        plaintext: String,
        encrypt: (String) -> String?,
        messageId: String = newMessageId(),
    ): List<String> {
        require(messageId.matches(Regex("[0-9a-f]{$MESSAGE_ID_HEX_CHARS}"))) {
            "Message ID must be $MESSAGE_ID_HEX_CHARS lowercase hexadecimal characters"
        }
        return encodeWithPrefix(
            prefix = "$MESSAGE_PREFIX:$messageId",
            plaintext = plaintext,
            label = "Standard/Secure messages",
            chunkBytes = MESSAGE_CHUNK_PLAINTEXT_BYTES,
            encrypt = encrypt,
        )
    }

    private fun newMessageId(): String =
        ByteArray(MESSAGE_ID_HEX_CHARS / 2)
            .also(messageIdRandom::nextBytes)
            .joinToString("") { "%02x".format(it) }

    private fun encodeWithPrefix(
        prefix: String,
        plaintext: String,
        label: String,
        chunkBytes: Int,
        encrypt: (String) -> String?,
    ): List<String> {
        require(plaintext.isNotEmpty()) { "$label must not be empty" }
        val maxBytes = chunkBytes * MAX_CHUNKS
        require(plaintext.toByteArray(Charsets.UTF_8).size <= maxBytes) {
            "$label are limited to $maxBytes UTF-8 bytes"
        }
        val chunks = chunkUtf8(plaintext, chunkBytes)
        val total = chunks.size
        require(total <= MAX_CHUNKS) { "$label are limited to $MAX_CHUNKS chunks" }
        return chunks.mapIndexed { seq, chunk ->
            val encrypted = encrypt(chunk)
                ?: error("$label encryption failed — no plaintext fallback")
            val wirePayload = if (prefix.startsWith("$MESSAGE_PREFIX:") && encrypted.startsWith("ENC:")) {
                val binary = Base64.getDecoder().decode(encrypted.removePrefix("ENC:"))
                Base64.getUrlEncoder().withoutPadding().encodeToString(binary)
            } else {
                encrypted
            }
            "$prefix:$seq:$total:$wirePayload"
        }
    }

    private fun chunkUtf8(plaintext: String, chunkBytes: Int): List<String> {
        val chunks = mutableListOf<String>()
        val current = StringBuilder()
        var currentBytes = 0
        var index = 0
        while (index < plaintext.length) {
            val codePoint = plaintext.codePointAt(index)
            val value = String(Character.toChars(codePoint))
            val size = value.toByteArray(Charsets.UTF_8).size
            if (currentBytes + size > chunkBytes && current.isNotEmpty()) {
                chunks += current.toString()
                current.setLength(0)
                currentBytes = 0
            }
            current.append(value)
            currentBytes += size
            index += Character.charCount(codePoint)
        }
        if (current.isNotEmpty()) chunks += current.toString()
        return chunks
    }

    // ── Predicate ─────────────────────────────────────────────────────────────

    /** True if [raw] is a DIODE chunk payload. */
    fun isDiode(raw: String): Boolean = raw.startsWith("$DIODE_PREFIX:")

    fun isMessageFragment(raw: String): Boolean = raw.startsWith("$MESSAGE_PREFIX:")

    // ── RX (assemble + decrypt) ────────────────────────────────────────────────

    /**
     * Stateful per-session assembler for the DIODE RX side.
     *
     * Instantiate one [Assembler] per logical session.  Thread-safe via [synchronized].
     *
     * The assembler:
     *   - Discards duplicate chunks (identical seq+enc).
     *   - Supports out-of-order arrival fully.
     *   - Resets automatically when a new `total` is seen (new transmission).
     */
    class Assembler {
        private val assembler = MessageAssembler(DIODE_PREFIX)

        /**
         * Feed one raw `DIODE:seq:total:enc` string.
         *
         * @param raw     The raw wire payload.
         * @param decrypt AES-256-GCM decrypt function → plaintext or null on tamper.
         * @return        The fully reassembled plaintext when all chunks are present;
         *                null when still waiting.
         */
        @Synchronized
        fun feed(raw: String, decrypt: (String) -> String?): String? {
            return when (val result = assembler.feed(raw, decrypt)) {
                is FragmentResult.Complete -> result.message
                is FragmentResult.Incomplete, is FragmentResult.Invalid -> null
            }
        }

        /** Reset the assembler window (e.g. on session close). */
        @Synchronized
        fun reset() {
            assembler.reset()
        }
    }

    sealed interface FragmentResult {
        data class Complete(val message: String, val total: Int, val debug: Boolean) : FragmentResult
        data class Incomplete(val received: Int, val total: Int) : FragmentResult
        data class Invalid(val reason: String) : FragmentResult
    }

    /** Stateful reassembly for authenticated MSG fragments or legacy DIODE chunks. */
    class MessageAssembler constructor(private val prefix: String = MESSAGE_PREFIX) {
        private val window = mutableMapOf<Int, String>()
        private var expected = -1
        private var activeMessageId: String? = null
        private var activeDebug: Boolean? = null

        @Synchronized
        fun feed(raw: String, decode: (String) -> String?): FragmentResult {
            val fields = raw.split(':', limit = if (prefix == MESSAGE_PREFIX) 5 else 4)
            val isMessage = prefix == MESSAGE_PREFIX
            val expectedFieldCount = if (isMessage) 5 else 4
            if (fields.size != expectedFieldCount || fields[0] != prefix) {
                return FragmentResult.Invalid("Malformed $prefix fragment")
            }
            val messageId = if (isMessage) fields[1] else null
            if (isMessage && messageId?.matches(Regex("[0-9a-f]{$MESSAGE_ID_HEX_CHARS}")) != true) {
                return FragmentResult.Invalid("Invalid message ID")
            }
            val seqIndex = if (isMessage) 2 else 1
            val totalIndex = seqIndex + 1
            val payloadIndex = totalIndex + 1
            val seq = fields[seqIndex].toIntOrNull()
                ?: return FragmentResult.Invalid("Invalid fragment sequence")
            val total = fields[totalIndex].toIntOrNull()
                ?: return FragmentResult.Invalid("Invalid fragment total")
            if (total !in 1..MAX_CHUNKS || seq !in 0 until total) {
                return FragmentResult.Invalid("Fragment sequence/total out of range")
            }
            val debug = isMessage && fields[payloadIndex].startsWith("DBG:")
            if (activeMessageId != null && isMessage && activeMessageId != messageId) {
                reset()
            }
            if (expected != -1 && total != expected) {
                if (isMessage) {
                    return FragmentResult.Invalid("Fragment total changed within a message")
                }
                reset()
            }
            if (activeDebug != null && activeDebug != debug) {
                return FragmentResult.Invalid("Mixed debug and encrypted fragments")
            }
            if (expected == -1) {
                window.clear()
                expected = total
                activeMessageId = messageId
                activeDebug = debug
            }
            val encodedPayload = fields[payloadIndex]
            val decodePayload = if (isMessage && !debug) {
                try {
                    "ENC:" + Base64.getEncoder().encodeToString(
                        Base64.getUrlDecoder().decode(encodedPayload),
                    )
                } catch (_: IllegalArgumentException) {
                    return FragmentResult.Invalid("Malformed encrypted fragment")
                }
            } else {
                encodedPayload
            }
            val plaintext = decode(decodePayload)
                ?: return FragmentResult.Invalid("Fragment authentication/decryption failed")
            val chunkBytes = if (isMessage) MESSAGE_CHUNK_PLAINTEXT_BYTES else DIODE_CHUNK_PLAINTEXT_BYTES
            if (plaintext.isEmpty() ||
                plaintext.toByteArray(Charsets.UTF_8).size > chunkBytes
            ) {
                return FragmentResult.Invalid("Fragment plaintext exceeds $chunkBytes UTF-8 bytes")
            }
            val prior = window[seq]
            if (prior != null && prior != plaintext) {
                return FragmentResult.Invalid("Conflicting duplicate fragment")
            }
            window[seq] = plaintext
            if (window.size != expected) {
                return FragmentResult.Incomplete(window.size, expected)
            }
            val complete = (0 until expected).joinToString("") { window.getValue(it) }
            val completedTotal = expected
            val completedDebug = activeDebug == true
            reset()
            return FragmentResult.Complete(complete, completedTotal, completedDebug)
        }

        @Synchronized
        fun reset() {
            window.clear()
            expected = -1
            activeMessageId = null
            activeDebug = null
        }
    }
}
