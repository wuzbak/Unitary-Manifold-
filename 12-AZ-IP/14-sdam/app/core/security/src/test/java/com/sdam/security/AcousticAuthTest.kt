package com.sdam.security

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
 * S1 Smoke tests — AcousticAuth three-way handshake (pure Kotlin, no Android Keystore).
 *
 * SdamKeyManager is mocked so these run on the JVM without hardware-backed Keystore.
 * Exercises the handshake state-machine, HMAC wire format, and abort paths.
 */
class AcousticAuthTest {

    private lateinit var keyManager: SdamKeyManager
    private lateinit var initiator:  AcousticAuth
    private lateinit var responder:  AcousticAuth

    @Before
    fun setUp() {
        keyManager = mockk(relaxed = true)

        // Deterministic sign: XOR bytes → 8-char hex
        every { keyManager.sign(any()) } answers {
            val msg  = firstArg<String>()
            val hash = msg.fold(0) { acc, c -> acc xor c.code } and 0xFF
            "%08x".format(hash)
        }

        // verify checks consistency with sign
        every { keyManager.verify(any(), any()) } answers {
            val msg = firstArg<String>()
            val tag = secondArg<String>()
            keyManager.sign(msg) == tag
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
        val ach = initiator.initiateHandshake()
        assertTrue(ach.startsWith("ACH:"))

        val ars = responder.processIncoming(ach)
        assertNotNull("ARS from responder", ars)
        assertTrue("ARS prefix", ars!!.startsWith("ARS:"))

        val aok = initiator.processIncoming(ars)
        assertNotNull("AOK from initiator", aok)
        assertTrue("AOK prefix", aok!!.startsWith("AOK:"))
        assertTrue("Initiator now Open", initiator.state.value is HandshakeState.Open)

        val final = responder.processIncoming(aok)
        assertNull("No response to AOK", final)
        assertTrue("Responder now Open", responder.state.value is HandshakeState.Open)
    }

    // ── Frame wire format ─────────────────────────────────────────────────────

    @Test
    fun ach_frame_has_three_colon_separated_fields() {
        val ach   = initiator.initiateHandshake()
        val parts = ach.split(":")
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
        assertNull("No heartbeat before session opens", initiator.heartbeat())
    }

    // ── Payload sign / verify ─────────────────────────────────────────────────

    @Test
    fun signPayload_appends_counter_and_tag_to_payload() {
        openBothSides()
        val raw    = "GPS:37.77:-122.41:10.0:5.0:85"
        val signed = initiator.signPayload(raw)
        assertNotNull("Signed payload", signed)
        assertTrue("Contains original payload", signed!!.startsWith(raw))
    }

    @Test
    fun verifyPayload_returns_bare_payload_on_valid_tag() {
        openBothSides()
        val raw     = "SYS:SDAM:45.0:80"
        val signed  = initiator.signPayload(raw)!!
        val verified = responder.verifyPayload(signed)
        assertNotNull("Verify passes", verified)
        assertEquals("Bare payload matches", raw, verified)
    }

    @Test
    fun verifyPayload_returns_null_for_tampered_payload() {
        openBothSides()
        val signed  = initiator.signPayload("VITALS:72:98:36.6")!!
        val tampered = signed.dropLast(1) + if (signed.last() == '0') '1' else '0'
        assertNull("Tampered payload rejected", responder.verifyPayload(tampered))
    }

    // ── Abort paths ───────────────────────────────────────────────────────────

    @Test
    fun processIncoming_hmac_mismatch_sends_ATO() {
        val ach      = initiator.initiateHandshake()
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
        val response = initiator.processIncoming("ATO:REMOTE_CLOSE")
        assertNull("No response to ATO", response)
        assertTrue("Aborted after remote ATO", initiator.state.value is HandshakeState.Aborted)
    }

    // ── SdamKeyManager interaction ────────────────────────────────────────────

    @Test
    fun initiateHandshake_calls_sign_exactly_once() {
        initiator.initiateHandshake()
        verify(exactly = 1) { keyManager.sign(any()) }
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private fun openBothSides() {
        val ach = initiator.initiateHandshake()
        val ars = responder.processIncoming(ach)!!
        val aok = initiator.processIncoming(ars)!!
        responder.processIncoming(aok)
    }
}
