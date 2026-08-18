package com.gibbernode.gibberwave

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * S1 Smoke test — PayloadBuilder and PayloadParser (pure Kotlin, no NDK required).
 *
 * These tests verify the Gibberlink wire-format codec without touching the JNI layer.
 * They run on the JVM and pass in CI without a connected device.
 */
class PayloadBuilderTest {

    // ── PayloadBuilder ────────────────────────────────────────────────────────

    @Test
    fun gps_format_roundtrip() {
        val payload = PayloadBuilder.gps(37.7749, -122.4194, 10.0, 5.0f, 85)
        assertTrue("GPS prefix", payload.startsWith("GPS:"))
        val parsed = PayloadParser.parse(payload) as? ParsedPayload.Gps
        assertNotNull("GPS parsed", parsed)
        assertEquals(37.7749, parsed!!.lat, 0.001)
        assertEquals(-122.4194, parsed.lon, 0.001)
        assertEquals(10.0, parsed.altM, 0.01)
        assertEquals(5.0f, parsed.accM, 0.01f)
        assertEquals(85, parsed.batPct)
    }

    @Test
    fun sys_format_roundtrip() {
        val payload = PayloadBuilder.sys("BV9900", 45.3f, 78, 2, "AUTO:THERMAL_THROTTLE")
        assertTrue("SYS prefix", payload.startsWith("SYS:"))
        val parsed = PayloadParser.parse(payload) as? ParsedPayload.Sys
        assertNotNull("SYS parsed", parsed)
        assertEquals("BV9900", parsed!!.deviceId)
        assertEquals(45.3f, parsed.cpuTempC, 0.1f)
        assertEquals(78, parsed.batPct)
        assertEquals(2, parsed.anomalyCount)
        assertEquals("AUTO:THERMAL_THROTTLE", parsed.intent)
    }

    @Test
    fun vitals_format_roundtrip() {
        val payload = PayloadBuilder.vitals(72, 98, 36.6f)
        assertTrue("VITALS prefix", payload.startsWith("VITALS:"))
        val parsed = PayloadParser.parse(payload) as? ParsedPayload.Vitals
        assertNotNull("VITALS parsed", parsed)
        assertEquals(72, parsed!!.hrBpm)
        assertEquals(98, parsed.spo2Pct)
        assertEquals(36.6f, parsed.tempC, 0.1f)
    }

    @Test
    fun env_format_roundtrip() {
        val payload = PayloadBuilder.env(1013.25f, 22.5f, 65.0f)
        assertTrue("ENV prefix", payload.startsWith("ENV:"))
        val parsed = PayloadParser.parse(payload) as? ParsedPayload.Env
        assertNotNull("ENV parsed", parsed)
        assertEquals(1013.25f, parsed!!.pressureHpa, 0.1f)
        assertEquals(22.5f, parsed.tempC, 0.1f)
        assertEquals(65.0f, parsed.humidityPct, 0.1f)
    }

    @Test
    fun alert_format_roundtrip() {
        val payload = PayloadBuilder.alert("OVERHEAT", "CPU above 80C")
        assertTrue("ALERT prefix", payload.startsWith("ALERT:"))
        val parsed = PayloadParser.parse(payload) as? ParsedPayload.Alert
        assertNotNull("ALERT parsed", parsed)
        assertEquals("OVERHEAT", parsed!!.code)
        assertEquals("CPU above 80C", parsed.message)
    }

    @Test
    fun translate_safe_colon_replacement() {
        val payload = PayloadBuilder.translate(
            sourceProtocol = "SPEECH",
            sourceId = "device01",
            inputText = "Hello: how are you?",
        )
        assertTrue("TRANSLATE prefix", payload.startsWith("TRANSLATE:"))
        // Colons in inputText must be replaced with semicolons for wire safety
        assertTrue("No bare colons in input text portion",
            !payload.substringAfterLast(":HUMAN_EN:").contains(":"))
    }

    @Test
    fun raw_passthrough() {
        val payload = PayloadBuilder.raw("arbitrary data 123")
        assertTrue("RAW prefix", payload.startsWith("RAW:"))
        val parsed = PayloadParser.parse(payload) as? ParsedPayload.Raw
        assertNotNull(parsed)
    }

    @Test
    fun unknown_type_falls_back_to_raw() {
        val payload = PayloadParser.parse("UNKNOWN:field1:field2")
        assertTrue("Unknown type maps to Raw", payload is ParsedPayload.Raw)
    }

    @Test
    fun allergy_format_roundtrip() {
        val payload = PayloadBuilder.allergy("P001", "penicillin,latex", "SEVERE")
        assertTrue("ALLERGY prefix", payload.startsWith("ALLERGY:"))
        val parsed = PayloadParser.parse(payload) as? ParsedPayload.Allergy
        assertNotNull(parsed)
        assertEquals("P001", parsed!!.patientId)
        assertEquals("SEVERE", parsed.severity)
    }

    @Test
    fun consent_format_roundtrip() {
        val payload = PayloadBuilder.consent("P001", "VITALS_SHARE", 1_700_000_000L, "DR_SMITH")
        assertTrue("CONSENT prefix", payload.startsWith("CONSENT:"))
        val parsed = PayloadParser.parse(payload) as? ParsedPayload.Consent
        assertNotNull(parsed)
        assertEquals("P001", parsed!!.patientId)
        assertEquals("VITALS_SHARE", parsed.action)
        assertEquals(1_700_000_000L, parsed.timestampS)
        assertEquals("DR_SMITH", parsed.operatorId)
    }

    // ── SourceProtocol / IntentTag helpers ────────────────────────────────────

    @Test
    fun source_protocol_fromString_unknown_defaults_to_system() {
        val proto = SourceProtocol.fromString("NONEXISTENT")
        assertEquals(SourceProtocol.SYSTEM, proto)
    }

    @Test
    fun intent_tag_fromString_case_insensitive() {
        val tag = IntentTag.fromString("alert")
        assertEquals(IntentTag.ALERT, tag)
    }

    // ── Edge cases ────────────────────────────────────────────────────────────

    @Test
    fun gps_zero_coords_accepted() {
        val payload = PayloadBuilder.gps(0.0, 0.0)
        assertTrue(payload.startsWith("GPS:"))
    }

    @Test
    fun empty_raw_survives_parse() {
        val parsed = PayloadParser.parse("RAW:")
        assertTrue(parsed is ParsedPayload.Raw)
    }
}
