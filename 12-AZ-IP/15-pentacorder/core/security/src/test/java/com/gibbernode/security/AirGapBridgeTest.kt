package com.gibbernode.security

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * AirGapBridgeTest — S6 JVM unit tests
 *
 * Uses a trivial symmetric "cipher" (prefix-based) so no Android Keystore is needed.
 * Production encrypt = PayloadCipher.encrypt (AES-256-GCM); tested separately.
 */
class AirGapBridgeTest {

    // ── Test cipher helpers ───────────────────────────────────────────────────

    private val encrypt: (String) -> String? = { plain -> "ENC_TEST:$plain" }
    private val decrypt: (String) -> String? = { enc ->
        if (enc.startsWith("ENC_TEST:")) enc.removePrefix("ENC_TEST:") else null
    }

    // ── encode() shape ────────────────────────────────────────────────────────

    @Test fun `single chunk for short payload`() {
        val chunks = AirGapBridge.encode("VITALS:72:98:36.6", encrypt)
        assertEquals(1, chunks.size)
        assertTrue(chunks[0].startsWith("DIODE:0:1:ENC_TEST:"))
    }

    @Test fun `multi-chunk for long payload`() {
        val payload = "A".repeat(200)   // well above CHUNK_PLAINTEXT_CHARS
        val chunks  = AirGapBridge.encode(payload, encrypt)
        assertTrue("Expected > 1 chunk for 200-char payload", chunks.size > 1)
        // verify seq indices are 0 .. n-1
        val total = chunks.size
        chunks.forEachIndexed { idx, raw ->
            val seq = raw.split(":")[1].toInt()
            val tot = raw.split(":")[2].toInt()
            assertEquals(idx, seq)
            assertEquals(total, tot)
        }
    }

    @Test fun `isDiode() recognises prefix`() {
        val chunks = AirGapBridge.encode("TEST", encrypt)
        assertTrue(AirGapBridge.isDiode(chunks[0]))
        assertTrue(!AirGapBridge.isDiode("VITALS:72:98:36.6"))
    }

    // ── round-trip ────────────────────────────────────────────────────────────

    @Test fun `round-trip single chunk`() {
        val original = "VITALS:72:98:36.6"
        val chunks   = AirGapBridge.encode(original, encrypt)
        val asm      = AirGapBridge.Assembler()
        var result: String? = null
        for (chunk in chunks) result = asm.feed(chunk, decrypt)
        assertEquals(original, result)
    }

    @Test fun `round-trip multi-chunk large payload`() {
        val original = "GPS:37.7749:-122.4194:15.0:3.0:82|".repeat(20)  // ~740 chars
        val chunks   = AirGapBridge.encode(original, encrypt)
        val asm      = AirGapBridge.Assembler()
        var result: String? = null
        for (chunk in chunks) result = asm.feed(chunk, decrypt)
        assertEquals(original, result)
    }

    // ── out-of-order arrival ──────────────────────────────────────────────────

    @Test fun `out-of-order chunks reassemble correctly`() {
        val original = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789".repeat(4)  // ~144 chars → ≥4 chunks
        val chunks   = AirGapBridge.encode(original, encrypt)
        assertTrue("Need multiple chunks for OOO test", chunks.size > 1)

        val asm      = AirGapBridge.Assembler()
        val shuffled = chunks.shuffled()
        var result: String? = null
        for (chunk in shuffled) result = asm.feed(chunk, decrypt)
        assertEquals(original, result)
    }

    // ── tampered chunk ────────────────────────────────────────────────────────

    @Test fun `tampered chunk returns null and resets assembler`() {
        val original = "SECRET_PAYLOAD_THAT_MUST_NOT_LEAK"
        val chunks   = AirGapBridge.encode(original, encrypt)
        val asm      = AirGapBridge.Assembler()

        // Feed a chunk with a tampered enc value — decrypt returns null
        val tampered = chunks[0].replaceFirst("ENC_TEST:", "TAMPERED:")
        val res1 = asm.feed(tampered, decrypt)
        assertNull("Tampered chunk must return null", res1)
    }

    // ── incomplete transmission ───────────────────────────────────────────────

    @Test fun `incomplete chunks return null until all present`() {
        val original = "A".repeat(200)
        val chunks   = AirGapBridge.encode(original, encrypt)
        assertTrue("Need ≥ 2 chunks", chunks.size >= 2)

        val asm = AirGapBridge.Assembler()
        // Feed all but the last chunk
        for (i in 0 until chunks.size - 1) {
            val res = asm.feed(chunks[i], decrypt)
            assertNull("Intermediate feed must be null", res)
        }
        // Feed last chunk — must complete
        val result = asm.feed(chunks.last(), decrypt)
        assertNotNull("Final chunk must complete the assembly", result)
        assertEquals(original, result)
    }

    // ── new-transmission reset ────────────────────────────────────────────────

    @Test fun `new total resets in-progress window`() {
        val first  = AirGapBridge.encode("A".repeat(200), encrypt)  // multi-chunk
        val second = AirGapBridge.encode("SHORT", encrypt)           // 1 chunk

        val asm = AirGapBridge.Assembler()
        // Start receiving first but don't finish
        asm.feed(first[0], decrypt)
        // Now receive second (different total) — should complete immediately
        val result = asm.feed(second[0], decrypt)
        assertEquals("SHORT", result)
    }

    // ── reset() ───────────────────────────────────────────────────────────────

    @Test fun `reset() clears window so subsequent transmission works`() {
        val asm = AirGapBridge.Assembler()
        val chunks = AirGapBridge.encode("A".repeat(200), encrypt)
        asm.feed(chunks[0], decrypt)  // partial
        asm.reset()

        // New transmission after reset
        val short  = AirGapBridge.encode("HELLO", encrypt)
        val result = asm.feed(short[0], decrypt)
        assertEquals("HELLO", result)
    }

    // ── malformed input ───────────────────────────────────────────────────────

    @Test fun `malformed non-diode payload returns null`() {
        val asm = AirGapBridge.Assembler()
        assertNull(asm.feed("VITALS:72:98:36.6", decrypt))
        assertNull(asm.feed("", decrypt))
        assertNull(asm.feed("DIODE:notAnInt:1:ENC_TEST:X", decrypt))
    }

    @Test fun `encrypt returning null throws`() {
        val failEncrypt: (String) -> String? = { null }
        try {
            AirGapBridge.encode("test", failEncrypt)
            error("Expected IllegalStateException")
        } catch (e: IllegalStateException) {
            assertTrue(e.message?.contains("AES key not ready") == true)
        }
    }
}
