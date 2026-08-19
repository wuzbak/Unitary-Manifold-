package com.gibbernode.gibberwave

import java.util.Locale

/**
 * PayloadBuilder
 *
 * Constructs typed Gibberlink payload strings that exactly match the formats
 * defined in Gibberlink/scripts/broadcast.py and modes.py.
 *
 * All methods return a bare payload string (no auth suffix — authentication
 * is added by AcousticAuth.signPayload() before transmission).
 *
 * Payload type prefix is the first colon-separated token.  Parsers on the
 * receiving end (PayloadParser below) use it to dispatch to the right handler.
 *
 * Format reference (TOKEN_STANDARD.md):
 *   GPS       GPS:{lat}:{lon}:{alt_m}:{acc_m}:{bat_pct}
 *   SYS       SYS:{device_id}:{cpu_temp_c}:{bat_pct}:{anomaly_count}:{intent}
 *   ENV       ENV:{pressure_hpa}:{temp_c}:{humidity_pct}
 *   VITALS    VITALS:{hr_bpm}:{spo2_pct}:{temp_c}
 *   MNFT      MNFT:{device_id}:{seq}/{total}:{json_chunk}
 *   INTENT    INTENT:{source}:{intent}:{payload}
 *   ENERGY    ENERGY:{mode}:{bat_pct}:{harvest_uw}:{share_state}
 *   SPATIAL   SPATIAL:{source_id}:{zone_fp12}:{bssid}:{dist_m}:{n}:{flags}:{lat},{lon}
 *   ALERT     ALERT:{code}:{message}
 *   TRANSLATE TRANSLATE:{source_protocol}:{source_id}:{intent_tag}:{target_lang}:{input_text}
 *   ALLERGY   ALLERGY:{patient_id}:{allergens_csv}:{severity}
 *   CONSENT   CONSENT:{patient_id}:{action}:{timestamp_s}:{operator_id}
 *   RAW       RAW:{data}
 */
object PayloadBuilder {

    /** GPS position broadcast — used in RED emergency mode. */
    fun gps(
        lat: Double,
        lon: Double,
        altM: Double = 0.0,
        accM: Float = 0f,
        batPct: Int = -1,
    ): String = "GPS:${fmt(lat)}:${fmt(lon)}:${fmt(altM)}:${fmt(accM.toDouble())}:$batPct"

    /**
     * System health snapshot — equivalent to sentinel_watchdog.py JSONL record.
     *
     * @param deviceId       Short device identifier (e.g. "BV9900").
     * @param cpuTempC       CPU temperature in °C (-1 if unknown).
     * @param batPct         Battery percentage.
     * @param anomalyCount   Number of active anomalies detected by the Sentinel.
     * @param intent         Intent tag string (e.g. "AUTO:THERMAL_THROTTLE").
     */
    fun sys(
        deviceId: String,
        cpuTempC: Float,
        batPct: Int,
        anomalyCount: Int,
        intent: String = "AUTO:POLL",
    ): String = "SYS:$deviceId:${fmt(cpuTempC.toDouble())}:$batPct:$anomalyCount:$intent"

    /** Environmental reading from barometer / thermometer / hygrometer. */
    fun env(
        pressureHpa: Float,
        tempC: Float,
        humidityPct: Float,
    ): String = "ENV:${fmt(pressureHpa.toDouble())}:${fmt(tempC.toDouble())}:${fmt(humidityPct.toDouble())}"

    /** Biometric vitals — HR, SpO2, skin temperature. */
    fun vitals(
        hrBpm: Int,
        spo2Pct: Int,
        tempC: Float,
    ): String = "VITALS:$hrBpm:$spo2Pct:${fmt(tempC.toDouble())}"

    /**
     * Manifest fragment — large manifests are split across multiple ggwave
     * bursts.  seq is 1-based.
     */
    fun mnft(
        deviceId: String,
        seq: Int,
        total: Int,
        jsonChunk: String,
    ): String = "MNFT:$deviceId:$seq/$total:$jsonChunk"

    /** Cross-protocol intent wrapper. */
    fun intent(
        source: SourceProtocol,
        intent: IntentTag,
        innerPayload: String,
    ): String = "INTENT:${source.name}:${intent.name}:$innerPayload"

    /** Power layer state snapshot from energy_manager.py. */
    fun energy(
        mode: String,          // passive | harvest | active
        batPct: Int,
        harvestUw: Float,
        shareState: String,    // CRITICAL | FLOOR | BALANCED | SHARE_ELIGIBLE | SURPLUS
    ): String = "ENERGY:$mode:$batPct:${fmt(harvestUw.toDouble())}:$shareState"

    /**
     * RF-Spatial token from wifi_rssi_mapper.py / csi_processor.py.
     *
     * @param sourceId   Device identifier.
     * @param zoneFp12   12-char zone fingerprint (RSSI AP BSSID hash).
     * @param bssid      Strongest AP BSSID.
     * @param distM      Estimated distance in metres.
     * @param n          Number of APs used in the estimate.
     * @param flags      Flag chars: M=movement, G=GPS-fused, C=CSI, -=none.
     * @param lat        GPS latitude (0.0 if not available).
     * @param lon        GPS longitude (0.0 if not available).
     */
    fun spatial(
        sourceId: String,
        zoneFp12: String,
        bssid: String,
        distM: Float,
        n: Int,
        flags: String = "-",
        lat: Double = 0.0,
        lon: Double = 0.0,
    ): String = "SPATIAL:$sourceId:$zoneFp12:$bssid:${fmt(distM.toDouble())}:$n:$flags:${fmt(lat)},${fmt(lon)}"

    /** Generic alert with a short machine code and human message. */
    fun alert(code: String, message: String): String = "ALERT:$code:$message"

    /** Raw untyped data pass-through. */
    fun raw(data: String): String = "RAW:$data"

    /**
     * Phase 10 TRANSLATE payload — instructs the Intent Engine to convert
     * input from one representation into another (speech → acoustic, etc.).
     *
     * @param sourceProtocol   Physical source channel (e.g. "SPEECH", "BLE", "SDR").
     * @param sourceId         Node or device ID of the originator.
     * @param intentTag        Typically "QUERY" or "RELAY".
     * @param targetLang       Target modality/language (e.g. "ACOUSTIC", "HUMAN_EN").
     * @param inputText        Text to translate (colons replaced by semicolons).
     */
    fun translate(
        sourceProtocol: String,
        sourceId: String,
        intentTag: String = "QUERY",
        targetLang: String = "HUMAN_EN",
        inputText: String,
    ): String {
        val safe = inputText.replace(":", ";")
        return "TRANSLATE:${sourceProtocol.uppercase()}:$sourceId:${intentTag.uppercase()}:${targetLang.uppercase()}:$safe"
    }

    /**
     * Allergy record — broadcast in BLUE mode before medical procedures.
     *
     * @param patientId    Anonymised or consented patient identifier.
     * @param allergensCsv Comma-separated allergen list (e.g. "penicillin,latex").
     * @param severity     "MILD", "MODERATE", or "SEVERE".
     */
    fun allergy(
        patientId: String,
        allergensCsv: String,
        severity: String = "UNKNOWN",
    ): String = "ALLERGY:$patientId:${allergensCsv.replace(":", ";")}:${severity.uppercase()}"

    /**
     * Consent record — logs a patient's informed consent event.
     *
     * @param patientId    Anonymised or consented patient identifier.
     * @param action       What was consented to (e.g. "VITALS_SHARE").
     * @param timestampS   Unix epoch seconds at time of consent.
     * @param operatorId   Operator or witness identifier.
     */
    fun consent(
        patientId: String,
        action: String,
        timestampS: Long = System.currentTimeMillis() / 1000,
        operatorId: String = "SELF",
    ): String = "CONSENT:$patientId:${action.uppercase()}:$timestampS:$operatorId"

    // ── Helpers ───────────────────────────────────────────────────────────────

    private fun fmt(d: Double): String = String.format(Locale.US, "%.4f", d)
}

// ─────────────────────────────────────────────────────────────────────────────

/**
 * PayloadParser
 *
 * Parses a Gibberlink payload string back into structured data.
 * Returns a [ParsedPayload] sealed class instance.
 */
object PayloadParser {

    fun parse(raw: String): ParsedPayload {
        val parts = raw.split(":")
        return when (parts.firstOrNull()) {
            "GPS"     -> parseGps(parts)
            "SYS"     -> parseSys(parts)
            "ENV"     -> parseEnv(parts)
            "VITALS"  -> parseVitals(parts)
            "MNFT"    -> ParsedPayload.Mnft(raw = raw)
            "INTENT"  -> ParsedPayload.Intent(
                source  = SourceProtocol.fromString(parts.getOrElse(1) { "SYSTEM" }),
                intent  = IntentTag.fromString(parts.getOrElse(2) { "TELEMETRY" }),
                payload = parts.drop(3).joinToString(":"),
            )
            "ENERGY"  -> ParsedPayload.Energy(raw = raw)
            "SPATIAL" -> ParsedPayload.Spatial(raw = raw)
            "ALERT"   -> ParsedPayload.Alert(
                code    = parts.getOrElse(1) { "UNKNOWN" },
                message = parts.drop(2).joinToString(":"),
            )
            "TRANSLATE" -> ParsedPayload.Translate(
                sourceProtocol = parts.getOrElse(1) { "UNKNOWN" },
                sourceId       = parts.getOrElse(2) { "" },
                intentTag      = parts.getOrElse(3) { "QUERY" },
                targetLang     = parts.getOrElse(4) { "HUMAN_EN" },
                inputText      = parts.drop(5).joinToString(":"),
            )
            "ALLERGY"   -> ParsedPayload.Allergy(
                patientId    = parts.getOrElse(1) { "" },
                allergensCsv = parts.getOrElse(2) { "" },
                severity     = parts.getOrElse(3) { "UNKNOWN" },
            )
            "CONSENT"   -> ParsedPayload.Consent(
                patientId  = parts.getOrElse(1) { "" },
                action     = parts.getOrElse(2) { "" },
                timestampS = parts.getOrElse(3) { "0" }.toLongOrNull() ?: 0L,
                operatorId = parts.getOrElse(4) { "SELF" },
            )
            else      -> ParsedPayload.Raw(raw = raw)
        }
    }

    private fun parseGps(p: List<String>) = ParsedPayload.Gps(
        lat    = p.getOrElse(1) { "0" }.toDoubleOrNull() ?: 0.0,
        lon    = p.getOrElse(2) { "0" }.toDoubleOrNull() ?: 0.0,
        altM   = p.getOrElse(3) { "0" }.toDoubleOrNull() ?: 0.0,
        accM   = p.getOrElse(4) { "0" }.toFloatOrNull() ?: 0f,
        batPct = p.getOrElse(5) { "-1" }.toIntOrNull() ?: -1,
    )

    private fun parseSys(p: List<String>) = ParsedPayload.Sys(
        deviceId      = p.getOrElse(1) { "" },
        cpuTempC      = p.getOrElse(2) { "0" }.toFloatOrNull() ?: 0f,
        batPct        = p.getOrElse(3) { "0" }.toIntOrNull() ?: 0,
        anomalyCount  = p.getOrElse(4) { "0" }.toIntOrNull() ?: 0,
        intent        = p.getOrElse(5) { "AUTO:POLL" },
    )

    private fun parseEnv(p: List<String>) = ParsedPayload.Env(
        pressureHpa  = p.getOrElse(1) { "0" }.toFloatOrNull() ?: 0f,
        tempC        = p.getOrElse(2) { "0" }.toFloatOrNull() ?: 0f,
        humidityPct  = p.getOrElse(3) { "0" }.toFloatOrNull() ?: 0f,
    )

    private fun parseVitals(p: List<String>) = ParsedPayload.Vitals(
        hrBpm   = p.getOrElse(1) { "0" }.toIntOrNull() ?: 0,
        spo2Pct = p.getOrElse(2) { "0" }.toIntOrNull() ?: 0,
        tempC   = p.getOrElse(3) { "0" }.toFloatOrNull() ?: 0f,
    )
}

// ─────────────────────────────────────────────────────────────────────────────

sealed class ParsedPayload {
    data class Gps(val lat: Double, val lon: Double, val altM: Double, val accM: Float, val batPct: Int) : ParsedPayload()
    data class Sys(val deviceId: String, val cpuTempC: Float, val batPct: Int, val anomalyCount: Int, val intent: String) : ParsedPayload()
    data class Env(val pressureHpa: Float, val tempC: Float, val humidityPct: Float) : ParsedPayload()
    data class Vitals(val hrBpm: Int, val spo2Pct: Int, val tempC: Float) : ParsedPayload()
    data class Mnft(val raw: String) : ParsedPayload()
    data class Intent(val source: SourceProtocol, val intent: IntentTag, val payload: String) : ParsedPayload()
    data class Energy(val raw: String) : ParsedPayload()
    data class Spatial(val raw: String) : ParsedPayload()
    data class Alert(val code: String, val message: String) : ParsedPayload()
    data class Translate(
        val sourceProtocol: String,
        val sourceId: String,
        val intentTag: String,
        val targetLang: String,
        val inputText: String,
    ) : ParsedPayload()
    data class Allergy(val patientId: String, val allergensCsv: String, val severity: String) : ParsedPayload()
    data class Consent(val patientId: String, val action: String, val timestampS: Long, val operatorId: String) : ParsedPayload()
    data class Raw(val raw: String) : ParsedPayload()
}
