package com.gibbernode.security

import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test

/**
 * S1 Smoke test — AcousticAuth three-way handshake (pure Kotlin, no Android Keystore).
 *
 * GibberKeyManager is mocked so these tests run on the JVM without hardware-backed Keystore.
 * They verify the handshake state-machine transitions, HMAC tag wire format, and abort paths.
 */
class AcousticAuthTest {

    private lateinit var keyManager: GibberKeyManager
    private lateinit var initiator: AcousticAuth
    private lateinit var responder: AcousticAuth

    @Before
    fun setUp() {
        // Both sides share the same pre-distributed secret (stub sign/verify pair)
        keyManager = mockk(relaxed = true)

        // sign always returns a fixed 8-char hex tag for deterministic test assertions
        every { keyManager.sign(any()) } answers {
            val msg = firstArg<String>()
            // Deterministic "hash": XOR bytes mod 0xFF, return 8-char hex
            val hash = msg.fold(0) { acc, c -> acc xor c.code } and 0xFF
            "%08x".format(hash)
        }

        // verify checks that the provided tag matches what sign would produce
        every { keyManager.verify(any(), any()) } answers {
            val msg = firstArg<String>()
            val tag = secondArg<String>()
            val expected = keyManager.sign(msg)
            expected == tag
        }

        initiator = AcousticAuth(keyManager)
        responder = AcousticAuth(keyManager)
    }

    // ── State machine transitions ─────────────────────────────────────────────

    @Test
    fun initial_state_is_idle() {
        assertTrue(initiator.state.value is HandshakeState.Idle)
    }

    @Test
    fun initiateHandshake_emits_ACH_frame_and_transitions_to_ChallengeSent() {
        val ach = initiator.initiateHandshake()
        assertTrue("ACH prefix", ach.startsWith("ACH:"))
        assertTrue("State after initiate", initiator.state.value is HandshakeState.ChallengeSent)
    }

    @Test
    fun full_three_way_handshake_opens_session_on_both_sides() {
        // Step 1: Initiator sends ACH
        val ach = initiator.initiateHandshake()
        assertTrue(ach.startsWith("ACH:"))

        // Step 2: Responder receives ACH, sends ARS
        val ars = responder.processIncoming(ach)
        assertNotNull("ARS from responder", ars)
        assertTrue("ARS prefix", ars!!.startsWith("ARS:"))

        // Step 3: Initiator receives ARS, sends AOK
        val aok = initiator.processIncoming(ars)
        assertNotNull("AOK from initiator", aok)
        assertTrue("AOK prefix", aok!!.startsWith("AOK:"))
        assertTrue("Initiator now Open", initiator.state.value is HandshakeState.Open)

        // Step 4: Responder receives AOK — session is open, no further response
        val final = responder.processIncoming(aok)
        assertNull("No response to AOK", final)
        assertTrue("Responder now Open", responder.state.value is HandshakeState.Open)
    }

    // ── Frame wire format ─────────────────────────────────────────────────────

    @Test
    fun ach_frame_has_three_colon_separated_fields() {
        val ach = initiator.initiateHandshake()
        val parts = ach.split(":")
        // ACH:{counter}:{hmac} — exactly 3 parts
        assertEquals("ACH frame parts", 3, parts.size)
        assertEquals("ACH", parts[0])
        assertNotNull("Numeric counter", parts[1].toLongOrNull())
        assertEquals("8-char HMAC tag", 8, parts[2].length)
    }

    @Test
    fun heartbeat_frame_starts_with_AHB_in_open_session() {
        openBothSides()
        val hb = initiator.heartbeat()
        assertNotNull("Heartbeat in open session", hb)
        assertTrue("AHB prefix", hb!!.startsWith("AHB:"))
    }

    @Test
    fun heartbeat_returns_null_when_not_in_open_session() {
        val hb = initiator.heartbeat()
        assertNull("No heartbeat before session opens", hb)
    }

    // ── Payload sign / verify ─────────────────────────────────────────────────

    @Test
    fun signPayload_appends_counter_and_tag_to_payload() {
        openBothSides()
        val raw = "GPS:37.77:-122.41:10.0:5.0:85"
        val signed = initiator.signPayload(raw)
        assertNotNull("Signed payload", signed)
        assertTrue("Contains original payload", signed!!.startsWith(raw))
        val parts = signed.split(":")
        assertTrue("At least 3 extra parts (counter + tag)", parts.size > raw.split(":").size + 1)
    }

    @Test
    fun verifyPayload_returns_bare_payload_on_valid_tag() {
        openBothSides()
        val raw = "SYS:BV9900:45.0:80:0:AUTO:POLL"
        val signed = initiator.signPayload(raw)!!
        val verified = responder.verifyPayload(signed)
        assertNotNull("Verify passes", verified)
        assertEquals("Bare payload matches", raw, verified)
    }

    @Test
    fun verifyPayload_returns_null_for_tampered_payload() {
        openBothSides()
        val signed = initiator.signPayload("VITALS:72:98:36.6")!!
        // Tamper by flipping one digit in the tag
        val tampered = signed.dropLast(1) + if (signed.last() == '0') '1' else '0'
        val verified = responder.verifyPayload(tampered)
        assertNull("Tampered payload rejected", verified)
    }

    // ── Abort paths ───────────────────────────────────────────────────────────

    @Test
    fun processIncoming_hmac_mismatch_sends_ATO() {
        val ach = initiator.initiateHandshake()
        // Corrupt the HMAC tag by replacing last char
        val tampered = ach.dropLast(1) + if (ach.last() == 'a') 'b' else 'a'
        val response = responder.processIncoming(tampered)
        assertNotNull("Response to tampered ACH", response)
        assertTrue("ATO on HMAC mismatch", response!!.startsWith("ATO:"))
    }

    @Test
    fun abort_transitions_to_Aborted_and_returns_ATO_frame() {
        val ato = initiator.abort("TEST_REASON")
        assertTrue("ATO frame", ato.startsWith("ATO:"))
        assertTrue("Aborted state", initiator.state.value is HandshakeState.Aborted)
    }

    @Test
    fun close_transitions_to_Closed() {
        initiator.close()
        assertEquals(HandshakeState.Closed, initiator.state.value)
    }

    @Test
    fun remote_ATO_received_transitions_to_Aborted() {
        openBothSides()
        val atoFrame = "ATO:REMOTE_CLOSE"
        val response = initiator.processIncoming(atoFrame)
        assertNull("No response to ATO", response)
        assertTrue("Aborted after remote ATO", initiator.state.value is HandshakeState.Aborted)
    }

    // ── GibberKeyManager interaction ──────────────────────────────────────────

    @Test
    fun initiateHandshake_calls_sign_exactly_once() {
        initiator.initiateHandshake()
        verify(exactly = 1) { keyManager.sign(any()) }
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    /** Run through the full handshake to get both sides into Open state. */
    private fun openBothSides() {
        val ach = initiator.initiateHandshake()
        val ars = responder.processIncoming(ach)!!
        val aok = initiator.processIncoming(ars)!!
        responder.processIncoming(aok)
    }
}
