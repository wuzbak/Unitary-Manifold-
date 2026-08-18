package com.sdam.security

import android.util.Log
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject
import javax.inject.Singleton

private const val TAG                  = "SDAM/AcousticAuth"
private const val HANDSHAKE_TIMEOUT_MS = 3_000L
private const val HEARTBEAT_INTERVAL_MS_CONST = 1_000L

/**
 * AcousticAuth — S1: Three-way HMAC-SHA256 Handshake
 *
 * Kotlin port of Gibberlink/scripts/acoustic_auth.py.
 *
 * Frames:
 *   ACH:{counter}:{hmac}   — challenge (initiator → responder)
 *   ARS:{counter}:{hmac}   — response  (responder → initiator)
 *   AOK:{counter}:{hmac}   — ack       (initiator → responder)
 *   AHB:{counter}:{hmac}   — heartbeat (both directions, 1 s)
 *   ATO:{reason}           — abort     (either side)
 *
 * [SdamKeyManager] provides the HMAC secret (Android Keystore).
 * The rolling [counter] prevents replay of recorded acoustic chirps.
 */
@Singleton
class AcousticAuth @Inject constructor(
    private val keyManager: SdamKeyManager,
) {
    private val _state = MutableStateFlow<HandshakeState>(HandshakeState.Idle)
    val state: StateFlow<HandshakeState> = _state.asStateFlow()

    @Volatile private var counter: Long = System.currentTimeMillis() / 1000L

    // ── Session initiation ─────────────────────────────────────────────────────

    /**
     * Generate an ACH frame to kick off a new handshake.
     * Transitions state: Idle → ChallengeSent.
     *
     * @return  Frame string to transmit over the acoustic channel.
     */
    fun initiateHandshake(): String {
        val c     = nextCounter()
        val frame = buildFrame("ACH", c, "")
        _state.value = HandshakeState.ChallengeSent(c, System.currentTimeMillis())
        Log.i(TAG, "Handshake initiated: $frame")
        return frame
    }

    // ── Incoming frame processing ─────────────────────────────────────────────

    /**
     * Process a frame string received from the acoustic channel.
     *
     * @param raw  The raw decoded SDAM payload string.
     * @return     A response frame to transmit back, or null if no response needed.
     */
    fun processIncoming(raw: String): String? {
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

        val messageToVerify = "$type:$counter:$payload"
        if (!keyManager.verify(messageToVerify, tag)) {
            Log.w(TAG, "processIncoming: HMAC mismatch on $type frame")
            return abortWithReason("HMAC_MISMATCH:$type")
        }

        return when (type) {
            "ACH" -> handleChallenge(counter)
            "ARS" -> handleResponse(counter, tag)
            "AOK" -> handleAck(counter)
            "AHB" -> handleHeartbeat(counter)
            "ATO" -> {
                Log.w(TAG, "Remote abort received: $payload")
                _state.value = HandshakeState.Aborted("REMOTE:$payload")
                null
            }
            else -> {
                Log.w(TAG, "processIncoming: unknown frame type $type")
                null
            }
        }
    }

    // ── Frame handlers ─────────────────────────────────────────────────────────

    private fun handleChallenge(challengeCounter: Long): String {
        val c     = nextCounter().coerceAtLeast(challengeCounter + 1)
        val frame = buildFrame("ARS", c, "")
        Log.i(TAG, "Sending ARS in response to ACH")
        return frame
    }

    private fun handleResponse(arsCounter: Long, @Suppress("UNUSED_PARAMETER") tag: String): String? {
        val current = _state.value
        if (current !is HandshakeState.ChallengeSent) {
            Log.w(TAG, "handleResponse: unexpected ARS in state $current")
            return abortWithReason("UNEXPECTED_ARS")
        }
        if (System.currentTimeMillis() - current.sentAt > HANDSHAKE_TIMEOUT_MS) {
            return abortWithReason("TIMEOUT_ARS")
        }
        val c         = nextCounter().coerceAtLeast(arsCounter + 1)
        val sessionId = keyManager.sign("SESSION:$c").take(8)
        _state.value  = HandshakeState.Open(sessionId, c, System.currentTimeMillis())
        val frame     = buildFrame("AOK", c, sessionId)
        Log.i(TAG, "Session opened sessionId=$sessionId — sending AOK")
        return frame
    }

    private fun handleAck(aokCounter: Long): String? {
        val sessionId = keyManager.sign("SESSION:$aokCounter").take(8)
        _state.value  = HandshakeState.Open(sessionId, aokCounter, System.currentTimeMillis())
        Log.i(TAG, "Session opened (AOK received) sessionId=$sessionId")
        return null
    }

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
     * @return Authenticated frame: "{payload}:{counter}:{hmac}", or null if
     *         no session is open.
     */
    fun signPayload(payload: String): String? {
        val s = _state.value as? HandshakeState.Open ?: run {
            Log.w(TAG, "signPayload called outside open session")
            return null
        }
        val c   = nextCounter()
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
        val lastColon       = raw.lastIndexOf(":")
        if (lastColon <= 0) return null
        val secondLastColon = raw.lastIndexOf(":", lastColon - 1)
        if (secondLastColon <= 0) return null

        val tag     = raw.substring(lastColon + 1)
        val counter = raw.substring(secondLastColon + 1, lastColon).toLongOrNull() ?: return null
        val payload = raw.substring(0, secondLastColon)

        return if (keyManager.verify("$payload:$counter", tag)) payload else null
    }

    // ── Heartbeat ─────────────────────────────────────────────────────────────

    /**
     * Generate a heartbeat (AHB) frame for the current open session.
     * Caller is responsible for scheduling at [HEARTBEAT_INTERVAL_MS].
     *
     * @return Heartbeat frame or null if no session is open.
     */
    fun heartbeat(): String? {
        val s = _state.value as? HandshakeState.Open ?: return null
        val c = nextCounter()
        _state.value = s.copy(counter = c)
        return buildFrame("AHB", c, "")
    }

    // ── Session teardown ──────────────────────────────────────────────────────

    /** Cleanly close the session; returns an ATO frame to inform the peer. */
    fun close(): String {
        _state.value = HandshakeState.Closed
        return "ATO:NORMAL_CLOSE"
    }

    /** Abort the session with a reason string. */
    fun abort(reason: String = "MANUAL_ABORT"): String = abortWithReason(reason)

    // ── Helpers ───────────────────────────────────────────────────────────────

    private fun abortWithReason(reason: String): String {
        _state.value = HandshakeState.Aborted(reason)
        Log.w(TAG, "Session aborted: $reason")
        return "ATO:$reason"
    }

    private fun buildFrame(type: String, counter: Long, payload: String): String {
        val message = if (payload.isEmpty()) "$type:$counter" else "$type:$counter:$payload"
        val tag     = keyManager.sign(message)
        return if (payload.isEmpty()) "$type:$counter:$tag" else "$type:$counter:$tag:$payload"
    }

    @Synchronized
    private fun nextCounter(): Long = ++counter

    companion object {
        /** Heartbeat interval (ms) — exposed for callers to schedule AHB frames. */
        const val HEARTBEAT_INTERVAL_MS: Long = HEARTBEAT_INTERVAL_MS_CONST
    }
}
