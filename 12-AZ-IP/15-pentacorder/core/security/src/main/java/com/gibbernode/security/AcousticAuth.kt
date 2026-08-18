package com.gibbernode.security

import android.util.Log
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject
import javax.inject.Singleton

private const val TAG              = "GibberNode/AcousticAuth"
private const val HANDSHAKE_TIMEOUT_MS = 3_000L   // 3 s to receive ARS/AOK
private const val HEARTBEAT_INTERVAL_MS = 1_000L  // 1 s between AHB frames

/**
 * AcousticAuth
 *
 * Kotlin port of Gibberlink/scripts/acoustic_auth.py.
 *
 * Implements the three-way HMAC-SHA256 handshake for Gibberlink sessions:
 *
 *   ACH:{counter}:{hmac}           — challenge (initiator → responder)
 *   ARS:{counter}:{hmac}           — response   (responder → initiator)
 *   AOK:{counter}:{hmac}           — ack         (initiator → responder)
 *   AHB:{counter}:{hmac}           — heartbeat   (both directions, 1 s)
 *   ATO:{reason}                   — abort       (either side)
 *
 * The [GibberKeyManager] provides the HMAC secret (lives in Android Keystore).
 * The rolling [counter] prevents replay of recorded acoustic chirps.
 *
 * Usage:
 *   - Call [initiateHandshake] to generate an ACH frame string.
 *   - Feed incoming frames via [processIncoming].
 *   - Observe [state] to react to transitions.
 *   - Call [signPayload] / [verifyPayload] inside an OPEN session.
 *   - Call [abort] / [close] when done.
 */
@Singleton
class AcousticAuth @Inject constructor(
    private val keyManager: GibberKeyManager,
) {
    private val _state = MutableStateFlow<HandshakeState>(HandshakeState.Idle)
    val state: StateFlow<HandshakeState> = _state.asStateFlow()

    // Rolling counter — persisted in DataStore in the full implementation;
    // here we start from a process-local value that still provides replay
    // protection within a session.
    @Volatile private var counter: Long = System.currentTimeMillis() / 1000L

    // ── Session initiation ─────────────────────────────────────────────────────

    /**
     * Generate an ACH (challenge) frame to kick off a new handshake.
     * Transitions state: Idle → ChallengeSent.
     *
     * @return  Frame string to transmit over the acoustic channel.
     */
    fun initiateHandshake(): String {
        val c = nextCounter()
        val frame = buildFrame("ACH", c, "")
        _state.value = HandshakeState.ChallengeSent(c, System.currentTimeMillis())
        Log.i(TAG, "Handshake initiated: $frame")
        return frame
    }

    // ── Incoming frame processing ─────────────────────────────────────────────

    /**
     * Process a frame string received from the acoustic channel.
     *
     * @param raw  The raw decoded Gibberlink payload string.
     * @return     A response frame to transmit back, or null if no response needed.
     */
    fun processIncoming(raw: String): String? {
        // ATO frames use a 2-part format ("ATO:reason") and carry no counter or
        // HMAC tag.  Handle them before the general 3-part minimum check so that
        // a peer abort is always recognized, even if the session isn't fully open.
        if (raw.startsWith("ATO:")) {
            val reason = raw.removePrefix("ATO:")
            Log.w(TAG, "Remote abort received: $reason")
            _state.value = HandshakeState.Aborted("REMOTE:$reason")
            return null
        }

        val parts = raw.split(":")
        if (parts.size < 3) {
            Log.w(TAG, "processIncoming: malformed frame \"${raw.take(60)}\"")
            return null
        }
        val type    = parts[0]
        val counter = parts[1].toLongOrNull() ?: run {
            Log.w(TAG, "processIncoming: non-numeric counter in \"$raw\"")
            return null
        }
        val tag     = parts[2]
        val payload = if (parts.size > 3) parts.drop(3).joinToString(":") else ""

        // Verify HMAC on the inbound frame using the same format as buildFrame():
        // omit the trailing colon when payload is absent so the signed and verified
        // strings are identical.
        val messageToVerify = if (payload.isEmpty()) "$type:$counter" else "$type:$counter:$payload"
        if (!keyManager.verify(messageToVerify, tag)) {
            Log.w(TAG, "processIncoming: HMAC mismatch on $type frame")
            return abortWithReason("HMAC_MISMATCH:$type")
        }

        return when (type) {
            "ACH" -> handleChallenge(counter)
            "ARS" -> handleResponse(counter, tag)
            "AOK" -> handleAck(counter)
            "AHB" -> handleHeartbeat(counter)
            else  -> {
                Log.w(TAG, "processIncoming: unknown frame type $type")
                null
            }
        }
    }

    // ── Frame handlers ─────────────────────────────────────────────────────────

    /** Received ACH from initiator — we are the responder. Send ARS. */
    private fun handleChallenge(challengeCounter: Long): String {
        val c = nextCounter().coerceAtLeast(challengeCounter + 1)
        val frame = buildFrame("ARS", c, "")
        Log.i(TAG, "Sending ARS in response to ACH")
        return frame
    }

    /** Received ARS — we are the initiator. Verify and send AOK. */
    private fun handleResponse(arsCounter: Long, @Suppress("UNUSED_PARAMETER") tag: String): String? {
        val current = _state.value
        if (current !is HandshakeState.ChallengeSent) {
            Log.w(TAG, "handleResponse: unexpected ARS in state $current")
            return abortWithReason("UNEXPECTED_ARS")
        }
        if (System.currentTimeMillis() - current.sentAt > HANDSHAKE_TIMEOUT_MS) {
            return abortWithReason("TIMEOUT_ARS")
        }
        val c = nextCounter().coerceAtLeast(arsCounter + 1)
        val sessionId = keyManager.sign("SESSION:$c").take(8)
        _state.value = HandshakeState.Open(sessionId, c, System.currentTimeMillis())
        val frame = buildFrame("AOK", c, sessionId)
        Log.i(TAG, "Session opened sessionId=$sessionId — sending AOK")
        return frame
    }

    /** Received AOK — we are the responder. Session is now open. */
    private fun handleAck(aokCounter: Long): String? {
        val sessionId = keyManager.sign("SESSION:$aokCounter").take(8)
        _state.value = HandshakeState.Open(sessionId, aokCounter, System.currentTimeMillis())
        Log.i(TAG, "Session opened (AOK received) sessionId=$sessionId")
        return null  // no further response required
    }

    /** Heartbeat received — update last-seen time (full impl: reset watchdog timer). */
    private fun handleHeartbeat(counter: Long): String? {
        val s = _state.value
        if (s is HandshakeState.Open) {
            _state.value = s.copy(counter = counter)
        }
        return null
    }

    // ── Payload signing (open session) ─────────────────────────────────────────

    /**
     * Sign a data payload within an open session.
     *
     * @param payload  The raw Gibberlink payload string (e.g. "GPS:37.77:-122.41:…").
     * @return         Authenticated frame: "{payload}:{counter}:{hmac}", or null if
     *                 no session is open.
     */
    fun signPayload(payload: String): String? {
        val s = _state.value as? HandshakeState.Open ?: run {
            Log.w(TAG, "signPayload called outside open session")
            return null
        }
        val c = nextCounter()
        val tag = keyManager.sign("$payload:$c")
        _state.value = s.copy(counter = c)
        return "$payload:$c:$tag"
    }

    /**
     * Verify an inbound signed payload within an open session.
     *
     * Expected format: "{payload}:{counter}:{hmac}"
     *
     * @return The bare [payload] portion if verification passes, null otherwise.
     */
    fun verifyPayload(raw: String): String? {
        _state.value as? HandshakeState.Open ?: run {
            Log.w(TAG, "verifyPayload called outside open session")
            return null
        }
        val lastColon = raw.lastIndexOf(":")
        if (lastColon <= 0) return null
        val secondLastColon = raw.lastIndexOf(":", lastColon - 1)
        if (secondLastColon <= 0) return null

        val tag     = raw.substring(lastColon + 1)
        val counter = raw.substring(secondLastColon + 1, lastColon).toLongOrNull() ?: return null
        val payload = raw.substring(0, secondLastColon)

        return if (keyManager.verify("$payload:$counter", tag)) payload else null
    }

    // ── Heartbeat generation ──────────────────────────────────────────────────

    /**
     * Generate a heartbeat (AHB) frame for the current open session.
     * The caller is responsible for transmitting this at [HEARTBEAT_INTERVAL_MS].
     *
     * @return Heartbeat frame string or null if no session is open.
     */
    fun heartbeat(): String? {
        val s = _state.value as? HandshakeState.Open ?: return null
        val c = nextCounter()
        _state.value = s.copy(counter = c)
        return buildFrame("AHB", c, "")
    }

    // ── Session teardown ──────────────────────────────────────────────────────

    /**
     * Cleanly close the session and return an ATO frame to inform the peer.
     */
    fun close(): String {
        _state.value = HandshakeState.Closed
        return "ATO:NORMAL_CLOSE"
    }

    /**
     * Abort the session with a reason string.
     * @return  ATO frame to transmit.
     */
    fun abort(reason: String = "MANUAL_ABORT"): String = abortWithReason(reason)

    // ── Helpers ───────────────────────────────────────────────────────────────

    private fun abortWithReason(reason: String): String {
        _state.value = HandshakeState.Aborted(reason)
        Log.w(TAG, "Session aborted: $reason")
        return "ATO:$reason"
    }

    /**
     * Build an authenticated frame string.
     * Format: "{type}:{counter}:{hmac4}[:{payload}]"
     */
    private fun buildFrame(type: String, counter: Long, payload: String): String {
        val message = if (payload.isEmpty()) "$type:$counter" else "$type:$counter:$payload"
        val tag = keyManager.sign(message)
        return if (payload.isEmpty()) "$type:$counter:$tag" else "$type:$counter:$tag:$payload"
    }

    @Synchronized
    private fun nextCounter(): Long = ++counter

    companion object {
        /** Heartbeat interval (ms) — exposed for callers to schedule AHB frames. */
        const val HEARTBEAT_INTERVAL_MS: Long = 1_000L
    }
}
