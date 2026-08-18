package com.gibbernode.enviro

import kotlin.math.abs
import kotlin.math.ln
import kotlin.math.pow

/**
 * WeatherAdvisor
 *
 * Pure stateless logic for barometer-based weather analysis, indoor floor
 * estimation, light-lab science, and building seal testing.
 * No Android SDK dependency — fully JVM-unit-testable.
 *
 * Physical basis:
 *   - Hypsometric formula (ISA): Δalt ≈ (Δhpa / 0.12 hPa) per metre near sea level
 *     Source: ICAO Doc 7488-CD standard lapse rate 0.0065 K/m at ISA MSL
 *   - Storm approach: Met Office / NOAA threshold ≥ 0.6 hPa drop per hour
 *   - Floor height: standard storey ≈ 3.0 m → Δhpa per floor ≈ 0.36 hPa
 *   - Building seal test: sealed room pressure spike when screen pressed
 *   - Lux thresholds: CIE S 017 (photometry), PPFD for plant growth (µmol/m²/s)
 *
 * All pressure inputs in hPa (== mbar).  Altitude in metres.  Lux in lx.
 */
object WeatherAdvisor {

    // ── Constants ─────────────────────────────────────────────────────────────

    /**
     * ISA pressure gradient near sea level: ~0.12 hPa per metre.
     * Source: ICAO Doc 7488-CD.
     */
    const val HPA_PER_METER   = 0.12f

    /**
     * Standard floor-to-floor height in a commercial building (metres).
     * ASHRAE standard corridor height; US mean ≈ 2.9 m, rounding to 3.0.
     */
    const val FLOOR_HEIGHT_M  = 3.0f

    /**
     * Pressure drop per standard floor (hPa).
     * = HPA_PER_METER × FLOOR_HEIGHT_M
     */
    val HPA_PER_FLOOR: Float  = HPA_PER_METER * FLOOR_HEIGHT_M  // ≈ 0.36 hPa

    // ── Storm Approach ────────────────────────────────────────────────────────

    /**
     * Storm-approach severity levels based on rate of pressure change.
     *
     * Thresholds from Met Office "Pressure Change Guidance" and NOAA NWS:
     *   SQUALL_LINE: ≥ 0.6 hPa/hr (rapid deepening, pre-frontal squall)
     *   WATCH:       ≥ 1.2 hPa/hr (fast-moving front)
     *   WARNING:     ≥ 2.0 hPa/hr (explosive cyclogenesis / tornado inflow)
     */
    enum class StormApproach(val label: String, val emoji: String, val hpaPerHour: Float) {
        CLEAR  ("Clear — stable",               "✅",  0.0f),
        WATCH  ("Watch — front approaching",    "🟡",  0.6f),
        WARNING("Warning — fast-moving front",  "🟠",  1.2f),
        IMMINENT("Imminent — explosive change", "🔴",  2.0f),
    }

    /** Result of a pressure-trend analysis. */
    data class WeatherReport(
        val pressureHpa:   Float,
        val trendHpaPerHr: Float,           // positive = rising, negative = falling
        val stormApproach: StormApproach,
        val minutesToArrival: Int?,         // estimated minutes; null if CLEAR
        val summary:       String,
    )

    // ── Indoor Navigation ─────────────────────────────────────────────────────

    /** Indoor floor estimate. */
    data class FloorEstimate(
        val floor:      Int,    // floor number relative to reference (0 = ground)
        val altitudeM:  Float,  // estimated altitude change from reference (m)
        val confidence: Float,  // 0–1 (higher with better baseline)
    )

    // ── Light Lab ─────────────────────────────────────────────────────────────

    /**
     * Recommended light environment for common houseplants.
     * Based on Missouri Botanical Garden and Royal Horticultural Society guidance.
     */
    enum class PlantLight(
        val label: String,
        val emoji: String,
        val minLux: Float,
        val maxLux: Float,
        val examples: String,
    ) {
        INSUFFICIENT("Insufficient",  "🌑", 0f,     200f,  "Most plants — add grow light"),
        SHADE       ("Shade-tolerant","🌒", 200f,   800f,  "Ferns, peace lily, pothos"),
        INDIRECT    ("Bright indirect","🌤", 800f,  3000f, "Monstera, fiddle leaf fig, most tropicals"),
        DIRECT      ("Direct sun",    "☀️",3000f, 50000f, "Succulents, cacti, herbs, orchids"),
    }

    /**
     * Circadian blue-light exposure estimate.
     * CIE 026:2018 melanopic equivalent daylight illuminance model.
     */
    data class CircadianReport(
        val luxReading:        Float,
        val colorTempK:        Float,  // estimated colour temperature
        val melanopicEdi:      Float,  // melanopic EDI (lux-equivalent)
        val blueExposureUmolM2: Float, // cumulative since last reset (µmol/m²)
        val advice:            String,
    )

    // ── Public API ────────────────────────────────────────────────────────────

    /**
     * Analyse a pressure time-series and return a [WeatherReport].
     *
     * @param readings  List of (epochMs, pressureHpa) pairs ordered oldest→newest.
     *                  Should span at least 5 minutes for a meaningful trend.
     */
    fun analyseWeather(readings: List<Pair<Long, Float>>): WeatherReport {
        val current = readings.lastOrNull()?.second ?: 1013.25f
        if (readings.size < 2) {
            return WeatherReport(current, 0f, StormApproach.CLEAR, null, "Insufficient data")
        }

        val oldest  = readings.first()
        val newest  = readings.last()
        val spanHr  = ((newest.first - oldest.first) / 3_600_000f).coerceAtLeast(0.0001f)
        val trend   = (newest.second - oldest.second) / spanHr   // hPa/hr (negative = falling)
        val dropRate = -trend  // positive = pressure falling

        val approach = when {
            dropRate >= StormApproach.IMMINENT.hpaPerHour -> StormApproach.IMMINENT
            dropRate >= StormApproach.WARNING.hpaPerHour  -> StormApproach.WARNING
            dropRate >= StormApproach.WATCH.hpaPerHour    -> StormApproach.WATCH
            else                                          -> StormApproach.CLEAR
        }

        // Rough arrival estimate: assume front arrives when pressure drops 5 hPa
        val minutesToArrival = if (approach != StormApproach.CLEAR && dropRate > 0f) {
            ((5f / dropRate) * 60f).toInt().coerceIn(1, 999)
        } else null

        val summary = when (approach) {
            StormApproach.CLEAR   -> "Pressure stable at %.1f hPa".format(current)
            StormApproach.WATCH   -> "Pressure falling %.2f hPa/hr — front approaching".format(dropRate)
            StormApproach.WARNING -> "Pressure dropping fast (%.2f hPa/hr) — storm likely in ~${minutesToArrival ?: "?"}min".format(dropRate)
            StormApproach.IMMINENT-> "⚠️ RAPID DROP %.2f hPa/hr — seek shelter".format(dropRate)
        }

        return WeatherReport(current, trend, approach, minutesToArrival, summary)
    }

    /**
     * Estimate the floor level relative to a reference pressure reading.
     *
     * @param referencePressureHpa  Pressure at the reference floor (e.g. building entrance).
     * @param currentPressureHpa    Current pressure reading.
     */
    fun estimateFloor(referencePressureHpa: Float, currentPressureHpa: Float): FloorEstimate {
        val deltaHpa  = referencePressureHpa - currentPressureHpa  // positive = higher
        val altDeltaM = deltaHpa / HPA_PER_METER
        val floor     = (altDeltaM / FLOOR_HEIGHT_M).toInt()
        // Confidence degrades with larger absolute deltas (sensor noise accumulates)
        val confidence = (1f - abs(deltaHpa) / 50f).coerceIn(0.1f, 1f)
        return FloorEstimate(floor, altDeltaM, confidence)
    }

    /**
     * Test building seal quality.
     *
     * When the user briefly presses the screen with their palm in a sealed room,
     * a temporary pressure rise should be detectable.  Returns true if the
     * test passed (sealed — pressure spiked), false if likely compromised.
     *
     * @param baselineHpa   Pressure before pressing.
     * @param peakHpa       Maximum pressure recorded during press.
     * @param threshold     Minimum spike required (hPa) to consider sealed. Default 0.05.
     */
    fun sealTestPassed(baselineHpa: Float, peakHpa: Float, threshold: Float = 0.05f): Boolean =
        (peakHpa - baselineHpa) >= threshold

    /**
     * Classify current lux reading for houseplant suitability.
     */
    fun plantLightAdvice(lux: Float): PlantLight =
        PlantLight.entries.lastOrNull { lux >= it.minLux } ?: PlantLight.INSUFFICIENT

    /**
     * Estimate melanopic EDI and circadian blue-light exposure.
     *
     * Simplified model: colour temperature estimated from lux (bright → warmer
     * display → more blue).  For daylight, blue component scales with lux.
     *
     * @param lux               Current lux reading.
     * @param accumulatedUmolM2 Running exposure since last reset (µmol/m²).
     * @param estimatedColorTempK  If known from hardware; otherwise estimated.
     */
    fun circadianReport(
        lux:                Float,
        accumulatedUmolM2:  Float = 0f,
        estimatedColorTempK: Float? = null,
    ): CircadianReport {
        // Estimate colour temperature: use 6500 K for daylight proxy, lower for warm
        val colorTempK = estimatedColorTempK ?: when {
            lux > 5000f -> 6500f
            lux > 1000f -> 5500f
            lux > 200f  -> 4000f
            else        -> 2700f
        }

        // Melanopic EDI coefficient (ratio to photopic) varies by colour temp.
        // Approximate from CIE 026 S/P ratios: 6500 K ≈ 0.88, 2700 K ≈ 0.45.
        val melanopicCoeff = 0.45f + (colorTempK - 2700f) / (6500f - 2700f) * 0.43f
        val melanopicEdi   = lux * melanopicCoeff.coerceIn(0.1f, 1.2f)

        // Blue-light flux (µmol/m²/s): approximation from lux × blue fraction
        val blueFraction     = ((colorTempK - 2700f) / 6500f * 0.3f).coerceIn(0.02f, 0.35f)
        val blueFluxUmolM2s  = lux * blueFraction * 0.0185f  // conversion factor
        val newAccumulated   = accumulatedUmolM2 + blueFluxUmolM2s  // per-call delta

        val advice = when {
            colorTempK > 5500f && lux > 50f ->
                "⚠️ High blue-light (${colorTempK.toInt()} K) — consider night mode after 9 pm"
            melanopicEdi < 10f              ->
                "🌑 Very low light — may suppress daytime alertness"
            else                            ->
                "✅ Light profile OK"
        }
        return CircadianReport(lux, colorTempK, melanopicEdi, newAccumulated, advice)
    }

    /**
     * Tornado/severe-storm inflow detector.
     * Returns true if pressure dropped > 4 hPa in under 10 minutes.
     *
     * Based on NWS crowdsourced barometric research: a 4+ hPa/10min drop is
     * a strong precursor to severe weather / tornado inflow.
     */
    fun tornadoInflowDetected(readings: List<Pair<Long, Float>>): Boolean {
        if (readings.size < 2) return false
        val newest  = readings.last()
        val tenMinsAgoMs = newest.first - 10 * 60_000L
        val oldest  = readings.firstOrNull { it.first >= tenMinsAgoMs } ?: readings.first()
        val dropHpa = oldest.second - newest.second
        return dropHpa >= 4f
    }
}
