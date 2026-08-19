package com.gibbernode.gibberwave

import java.util.UUID

/**
 * CommonToken
 *
 * The universal normalised token that flows through the UPB Hub.
 * Kotlin port of the CommonToken dataclass in Gibberlink/scripts/upb_hub.py.
 *
 * Every physical-layer signal — acoustic ggwave frame, BLE advertisement,
 * SDR alert, USB sensor reading, system watchdog event — is normalised into
 * a CommonToken before reaching the Intent Engine.  The Intent Engine then
 * reasons over a homogeneous token stream without caring about transport.
 *
 * Wire format (for logging / RAG corpus):
 *   {id}|{timestamp}|{source}|{intent}|{payload}|{confidence}
 */
data class CommonToken(
    /** UUID for deduplication (RED-mode broadcasts repeat 3×). */
    val id: String = UUID.randomUUID().toString(),

    /** Unix epoch milliseconds at the moment of normalisation. */
    val timestamp: Long = System.currentTimeMillis(),

    /** Which physical protocol sourced this token. */
    val source: SourceProtocol,

    /** High-level semantic category. */
    val intent: IntentTag,

    /** Typed payload string — use [PayloadBuilder] to construct and [PayloadParser] to read. */
    val payload: String,

    /** Raw string before normalisation (for audit trail). */
    val rawPayload: String = payload,

    /**
     * Confidence [0.0, 1.0].  Acoustic payloads: ggwave decode success = 1.0.
     * Sensor estimates: proportional to SNR.
     */
    val confidence: Float = 1.0f,
) {
    /** Compact pipe-separated string for the RAG corpus (matches log_ingest.py output). */
    fun toLogLine(): String =
        "$id|$timestamp|${source.name}|${intent.name}|$payload|$confidence"
}

// ─────────────────────────────────────────────────────────────────────────────

/**
 * Source protocol — matches VALID_PROTOCOLS in upb_hub.py.
 */
enum class SourceProtocol {
    BLE,
    SDR,
    ACOUSTIC,
    SPEECH,
    USB,
    SYSTEM,
    NETWORK,
    CSI,
    ENERGY;

    companion object {
        fun fromString(s: String): SourceProtocol =
            entries.firstOrNull { it.name.equals(s, ignoreCase = true) } ?: SYSTEM
    }
}

/**
 * Intent tag — matches IntentTag in upb_hub.py.
 */
enum class IntentTag {
    ALERT,
    QUERY,
    TELEMETRY,
    HANDSHAKE,
    RELAY;

    companion object {
        fun fromString(s: String): IntentTag =
            entries.firstOrNull { it.name.equals(s, ignoreCase = true) } ?: TELEMETRY
    }
}

/**
 * Operational mode — GREEN / RED / BLUE / AMBER.
 * Matches modes.py in Gibberlink/scripts/.
 *
 * AMBER (Phase 10 TRANSLATE) — human-language translation/annotation mode.
 * Instructs the Intent Engine to convert received machine payloads into
 * plain-English descriptions and to accept TRANSLATE payloads for
 * cross-modal conversion (acoustic → speech, SDR → text, etc.).
 */
enum class OperationalMode(
    val displayName: String,
    val protocol: Int,        // ggwave TxProtocol id
    val volume: Int,          // 0–100
    val requiresAuth: Boolean,
    val redundancy: Int,       // number of repeated transmissions
    val rangeM: Float,         // approximate reliable range in metres
) {
    GREEN(
        displayName  = "Green — Sensor",
        protocol     = 1,   // AUDIBLE_FAST
        volume       = 15,
        requiresAuth = false,
        redundancy   = 1,
        rangeM       = 5f,
    ),
    RED(
        displayName  = "Red — Emergency",
        protocol     = 0,   // AUDIBLE_NORMAL (most robust)
        volume       = 80,
        requiresAuth = true,
        redundancy   = 3,
        rangeM       = 15f,
    ),
    BLUE(
        displayName  = "Blue — Health",
        protocol     = 1,   // AUDIBLE_FAST
        volume       = 20,
        requiresAuth = true,
        redundancy   = 1,
        rangeM       = 1f,
    ),
    AMBER(
        displayName  = "Amber — Translate",
        protocol     = 1,   // AUDIBLE_FAST
        volume       = 20,
        requiresAuth = false,
        redundancy   = 1,
        rangeM       = 5f,
    ),

    /**
     * DIODE — Air-Gap Bridge Mode (S6).
     *
     * One-way encrypted acoustic data channel.  The TX side encrypts every
     * payload with AES-256-GCM, signs it with HMAC, and optionally chunks large
     * payloads across multiple near-ultrasonic bursts.  The RX side assembles
     * and decrypts — but never transmits back.  This enforces the logical
     * "air-gap diode" property: information flows in exactly one direction.
     *
     * Use cases:
     *   - Injecting sensor readings into an isolated device without a wired link
     *   - Covert machine-to-machine updates across a physical air gap
     *   - One-way health data upload from a bedside monitor to a logging node
     *
     * Protocol: ULTRASOUND_FAST (near-ultrasonic, ~17–22 kHz) — inaudible to
     * most adults, above ambient speech frequencies, reduced environmental noise.
     */
    DIODE(
        displayName  = "Diode — Air-Gap",
        protocol     = 4,   // ULTRASOUND_FAST
        volume       = 60,
        requiresAuth = true,
        redundancy   = 2,
        rangeM       = 3f,
    );
}

/**
 * Sentinel health mood — mirrors --humanize output in sentinel_commentary.py.
 */
enum class SentinelMood(val emoji: String, val label: String) {
    CALM("🟢", "Device is calm"),
    STRESSED("🟡", "Device feels warm"),
    EXHAUSTED("🟠", "Device is exhausted"),
    CRITICAL("🔴", "Critical — device needs attention");
}
