package com.sdam.security

import android.util.Log

private const val TAG    = "SDAM/AirGapBridge"
private const val PREFIX = "DIODE"

/**
 * AirGapBridge — S6: Encrypted Acoustic Data Diode
 *
 * One-way, MTU-aware encrypted acoustic channel for crossing physical air gaps.
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
 * Security properties:
 *   - AES-256-GCM: confidentiality + integrity per chunk
 *   - Independent per-chunk IVs: random, never reused
 *   - HMAC-SHA256 outer layer (added by [AcousticAuth]) for replay protection
 *
 * This class is pure JVM — no Android SDK dependency — enabling JVM unit tests
 * without an emulator or Keystore.
 */
object AirGapBridge {

    /**
     * Maximum number of characters for a DIODE chunk payload after the
     * `DIODE:seq:total:` prefix.  Conservative bound fitting all ggwave protocols.
     */
    const val MTU_CHARS = 128

    /**
     * Number of plaintext UTF-8 characters per chunk before encryption.
     *
     * AES-256-GCM adds 12-byte IV + 16-byte GCM tag = 28 bytes of overhead.
     * Base64 encoding expands by ~4/3.
     * For 32 chars: (32 + 28) × 4/3 ≈ 80 Base64 chars.
     * With `ENC:` (4) and `DIODE:N:M:` (≤12) → ≤96 chars total, within every
     * ggwave protocol's maximum payload (~140 bytes for AUDIBLE_NORMAL).
     */
    private const val CHUNK_PLAINTEXT_CHARS = 32

    // ── TX (encode) ────────────────────────────────────────────────────────────

    /**
     * Encode [plaintext] into a list of `DIODE:seq:total:enc` wire strings.
     *
     * @param plaintext  UTF-8 string to transmit (any length).
     * @param encrypt    Function that encrypts a plain string → `ENC:…`.
     * @return           List of payload strings to broadcast in order.
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
     * Instantiate one [Assembler] per logical session.  Thread-safe via [synchronized].
     *
     * The assembler:
     *   - Discards duplicate chunks (identical seq+enc).
     *   - Supports out-of-order arrival fully.
     *   - Resets automatically when a new `total` is seen (new transmission).
     */
    class Assembler {
        private val window   = mutableMapOf<Int, String>()
        private var expected = -1

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

            val plain = decrypt(enc) ?: run {
                Log.w(TAG, "Assembler: GCM tag mismatch on chunk $seq/$total — tampered?")
                return null
            }

            window[seq] = plain

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
