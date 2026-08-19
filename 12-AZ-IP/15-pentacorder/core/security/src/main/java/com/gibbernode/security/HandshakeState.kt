package com.gibbernode.security

/**
 * HandshakeState
 *
 * Sealed class representing every state a Gibberlink acoustic authentication
 * session can be in.  This mirrors the Python acoustic_auth.py state machine:
 *
 *   IDLE → CHALLENGE_SENT → RESPONSE_RECEIVED → OPEN → (session) → CLOSED
 *   Any state → ABORTED (timeout, bad HMAC, desync)
 *
 * The three-way handshake:
 *   1. Initiator sends ACH (challenge) with HMAC.
 *   2. Responder replies with ARS (response) carrying its own HMAC.
 *   3. Initiator sends AOK (ack) — session is OPEN on both sides.
 *   4. AHB (heartbeat) frames keep the session alive (1 s interval).
 *   5. ATO (abort) or 3-second silence → ABORTED on both sides.
 */
sealed class HandshakeState {

    /** No active session. */
    object Idle : HandshakeState()

    /**
     * We have sent a challenge (ACH frame) and are waiting for the peer's
     * ARS response.
     * @param counter     Our current rolling HMAC counter.
     * @param sentAt      System.currentTimeMillis() when we sent the ACH.
     */
    data class ChallengeSent(val counter: Long, val sentAt: Long) : HandshakeState()

    /**
     * We received an ARS from the peer and are verifying the HMAC tag.
     * @param counter      The counter value in the received ARS frame.
     * @param receivedTag  The 8-char hex tag from the peer.
     */
    data class ResponseReceived(val counter: Long, val receivedTag: String) : HandshakeState()

    /**
     * Both sides have authenticated.  Payload data exchange may proceed.
     * @param sessionId   8-char hex identifier for this session (= first 4 bytes of ACH HMAC).
     * @param counter     The rolling counter; increment before each transmitted payload.
     * @param openedAt    System.currentTimeMillis() when the session was opened.
     */
    data class Open(val sessionId: String, val counter: Long, val openedAt: Long) : HandshakeState()

    /**
     * Session terminated normally (AOK received, explicit close, or counter roll).
     */
    object Closed : HandshakeState()

    /**
     * Session aborted abnormally.
     * @param reason  Human-readable reason (logged and surfaced in audit trail).
     */
    data class Aborted(val reason: String) : HandshakeState()
}
