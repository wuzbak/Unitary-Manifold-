package com.sdam.security

/**
 * HandshakeState — S1
 *
 * Sealed class representing every state a SDAM acoustic authentication
 * session can be in.
 *
 *   IDLE → CHALLENGE_SENT → OPEN → CLOSED
 *   Any state → ABORTED (timeout, bad HMAC, desync)
 */
sealed class HandshakeState {

    /** No active session. */
    object Idle : HandshakeState()

    /**
     * Challenge (ACH) has been sent; waiting for the peer's ARS response.
     *
     * @param counter  Our current rolling HMAC counter.
     * @param sentAt   System.currentTimeMillis() when we sent the ACH.
     */
    data class ChallengeSent(val counter: Long, val sentAt: Long) : HandshakeState()

    /**
     * Received ARS from the peer and are verifying the HMAC tag.
     *
     * @param counter      The counter value in the received ARS frame.
     * @param receivedTag  The 8-char hex tag from the peer.
     */
    data class ResponseReceived(val counter: Long, val receivedTag: String) : HandshakeState()

    /**
     * Both sides have authenticated — payload data exchange may proceed.
     *
     * @param sessionId   8-char hex session identifier.
     * @param counter     Rolling counter; increment before each transmitted payload.
     * @param openedAt    System.currentTimeMillis() when the session was opened.
     */
    data class Open(val sessionId: String, val counter: Long, val openedAt: Long) : HandshakeState()

    /** Session terminated normally. */
    object Closed : HandshakeState()

    /**
     * Session aborted abnormally.
     * @param reason  Human-readable reason string.
     */
    data class Aborted(val reason: String) : HandshakeState()
}
