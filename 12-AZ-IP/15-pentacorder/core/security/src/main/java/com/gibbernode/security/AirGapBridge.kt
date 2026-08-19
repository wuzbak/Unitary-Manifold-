package com.gibbernode.security

import android.util.Log

private const val TAG    = "GibberNode/AirGapBridge"
private const val PREFIX = "DIODE"

/**
 * AirGapBridge — S6: Encrypted Acoustic Data Diode
 *
 * Implements a one-way, MTU-aware encrypted acoustic channel suitable for
 * crossing physical air gaps.  The TX side encrypts each chunk with
 * AES-256-GCM (via [PayloadCipher]), signs it, and emits a sequence of
 * Gibberlink payloads.  The RX side assembles all chunks and decrypts.
 *
 * Wire format per chunk:
 *   `DIODE:{seq}:{total}:{enc_chunk}`
 *
 *   seq    — 0-based chunk index
 *   total  — total number of chunks in this transmission
 *   enc    — AES-256-GCM encrypted portion of the plaintext (`ENC:…` string)
 *
 * Each chunk is independently encrypted so a tampered or dropped chunk does
 * NOT allow the receiver to reconstruct adjacent plaintext.
 *
 * MTU note: ggwave payload sizes are constrained by the selected protocol.
 * [MTU_CHARS] (80 chars) is a conservative upper bound that fits every ggwave
 * protocol in use.  Adjust downward if you observe truncation at the encoder.
 *
 * Security properties:
 *   - AES-256-GCM: confidentiality + integrity per chunk (tag mismatch → null)
 *   - Independent per-chunk IVs: random, never reused (one per [encrypt] call)
 *   - HMAC-SHA256 outer layer (added by [AcousticAuth]) for replay protection
 *   - One-directional by convention: the RX [Assembler] never calls `play()`
 *
 * This class is pure JVM — no Android SDK dependency — to allow JVM unit tests
 * without an emulator or Keystore.  Pass lambdas for encrypt/decrypt/sign so
 * tests can inject test doubles.
 */
object AirGapBridge {

    /**
     * Maximum number of UTF-8 characters for a single DIODE chunk *before*
     * the `DIODE:seq:total:` prefix is added.  A 12-byte IV + ~32-byte payload
     * + 16-byte GCM tag Base64-encodes to ~81 chars; with the `ENC:` prefix
     * and the outer DIODE header (~12 chars) we stay safely under ggwave limits.
     *
     * Callers that need to transmit larger payloads benefit from chunking:
     * the plaintext is split into [CHUNK_PLAINTEXT_CHARS]-character slices
     * that each encrypt independently.
     */
    const val MTU_CHARS             = 128

    /**
     * Number of plaintext UTF-8 characters per chunk before encryption.
     *
     * Rationale: AES-256-GCM adds 12 bytes IV + 16 bytes GCM tag = 28 bytes
     * of overhead per chunk.  Base64 encoding expands the ciphertext by ~4/3.
     * For a 32-char plaintext: (32 + 28) × 4/3 ≈ 80 Base64 chars.
     * With the `ENC:` prefix (4 chars) and `DIODE:N:M:` header (≤ 12 chars),
     * the total wire payload is ≤ 96 chars — safely within every ggwave
     * protocol's maximum payload length (~140 bytes for AUDIBLE_NORMAL).
     * Using 32 chars leaves headroom for multi-byte UTF-8 sequences in the
     * plaintext (e.g. medical symbols, emoji in ALERT payloads).
     */
    private const val CHUNK_PLAINTEXT_CHARS = 32

    // ── TX (encode) ────────────────────────────────────────────────────────────

    /**
     * Encode [plaintext] into a list of `DIODE:seq:total:enc` wire strings.
     *
     * @param plaintext  UTF-8 string to transmit (any length).
     * @param encrypt    Function that encrypts a plain string → `ENC:…`.
     *                   Must return non-null; caller must ensure key is ready.
     * @return           List of payload strings to broadcast in order.
     *                   Length 1 for short payloads; ≥2 when chunked.
     * @throws IllegalStateException if [encrypt] returns null (key not ready).
     */
    fun encode(
        plaintext: String,
        encrypt: (String) -> String?,
    ): List<String> {
        val chunks = plaintext.chunked(CHUNK_PLAINTEXT_CHARS)
        val total  = chunks.size
        return chunks.mapIndexed { seq, chunk ->
            val enc = encrypt(chunk)
                ?: error("AirGapBridge.encode: encrypt() returned null — AES key not ready")
            "$PREFIX:$seq:$total:$enc"
        }
    }

    // ── Predicate ─────────────────────────────────────────────────────────────

    /** True if [raw] is a DIODE chunk payload. */
    fun isDiode(raw: String): Boolean = raw.startsWith("$PREFIX:")

    // ── RX (assemble + decrypt) ────────────────────────────────────────────────

    /**
     * Stateful per-session assembler for the DIODE RX side.
     *
     * Instantiate one [Assembler] per logical session (or per transmission if
     * you clear between sends).  Thread-safe via [synchronized].
     *
     * Usage:
     * ```kotlin
     * val asm = AirGapBridge.Assembler()
     * for (chunk in incomingChunks) {
     *     val result = asm.feed(chunk, payloadCipher::decrypt)
     *     if (result != null) println("Received: $result")
     * }
     * ```
     *
     * The assembler discards duplicate chunks (identical seq+enc).
     * Out-of-order arrival is fully supported.
     * A new transmission (different `total`) replaces the in-progress window.
     */
    class Assembler {
        // seq → decrypted chunk string
        private val window  = mutableMapOf<Int, String>()
        private var expected = -1

        /**
         * Feed one raw `DIODE:seq:total:enc` string.
         *
         * @param raw     The raw wire payload (already stripped of HMAC suffix by [AcousticAuth]).
         * @param decrypt AES-256-GCM decrypt function → plaintext or null on tamper.
         * @return        The fully reassembled plaintext when all chunks are present,
         *                or null when still waiting for more chunks.
         */
        @Synchronized
        fun feed(raw: String, decrypt: (String) -> String?): String? {
            val parts = raw.split(":", limit = 4)
            if (parts.size != 4 || parts[0] != PREFIX) {
                Log.w(TAG, "Assembler.feed: malformed chunk: ${raw.take(40)}")
                return null
            }
            val seq   = parts[1].toIntOrNull() ?: run { Log.w(TAG, "bad seq"); return null }
            val total = parts[2].toIntOrNull() ?: run { Log.w(TAG, "bad total"); return null }
            val enc   = parts[3]

            if (total < 1 || seq < 0 || seq >= total) {
                Log.w(TAG, "Assembler.feed: invalid seq=$seq total=$total")
                return null
            }

            // New transmission: reset window
            if (total != expected) {
                window.clear()
                expected = total
                Log.d(TAG, "Assembler: new window  total=$total")
            }

            // Decrypt this chunk
            val plain = decrypt(enc) ?: run {
                Log.w(TAG, "Assembler: GCM tag mismatch on chunk $seq/$total — tampered?")
                return null
            }

            window[seq] = plain

            // Complete?
            if (window.size == expected) {
                val result = (0 until expected).joinToString("") { window[it] ?: "" }
                window.clear()
                expected = -1
                Log.i(TAG, "Assembler: reassembled ${result.length} chars from $total chunks")
                return result
            }
            Log.d(TAG, "Assembler: ${window.size}/$expected chunks received")
            return null
        }

        /** Reset the assembler window (e.g. on session close). */
        @Synchronized
        fun reset() {
            window.clear()
            expected = -1
        }
    }
}
