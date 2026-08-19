package com.gibbernode.emf

import kotlin.math.abs
import kotlin.math.ln
import kotlin.math.sqrt

/**
 * EMFAdvisor
 *
 * Pure stateless logic for magnetometer-based stud-finding, EMF zone
 * classification, sleep-environment scoring, and "dirty electricity" analysis.
 * No Android SDK dependency — fully JVM-unit-testable.
 *
 * Physical basis (all values in microteslas, µT):
 *   - Earth's surface field: ~25–65 µT (IGRF-13 model, mid-lat ≈ 45 µT)
 *   - BioInitiative safety threshold: < 2 µT continuous AC field (WHO/EPA)
 *   - Live-wire detection: 50/60 Hz AC field ~0.1–1 µT at 1 m distance
 *   - Metal screw/stud: local field deviation 0.5–5 µT vs baseline
 *   - Dense metal (rebar, conduit): delta > 5 µT
 *
 * Inputs are raw TYPE_MAGNETIC_FIELD values (Bx, By, Bz in µT).
 */
object EMFAdvisor {

    // ── EMF Zone ─────────────────────────────────────────────────────────────

    /**
     * Ambient EMF zone — used for sleep-environment and general field advisory.
     *
     * Thresholds from BioInitiative 2012 Report (S12) and WHO EHC 238.
     */
    enum class EmfZone(
        val label: String,
        val emoji: String,
        val description: String,
    ) {
        LOW     ("Low",      "🟢", "< 0.2 µT — typical quiet environment"),
        MODERATE("Moderate", "🟡", "0.2–2 µT — near household wiring"),
        HIGH    ("High",     "🟠", "2–10 µT — near appliances or wiring runs"),
        ALERT   ("Alert",    "🔴", "> 10 µT — near large appliance or live wire"),
    }

    // ── Stud / Wall Material ──────────────────────────────────────────────────

    /**
     * Material inferred from the local magnetic field anomaly during wall scan.
     *
     * Discrimination:
     *   EMPTY       — delta < 0.5 µT (background noise)
     *   METAL_SCREW — delta 0.5–5 µT, point-like (screws / nails)
     *   METAL_PIPE  — delta 0.5–5 µT, sustained gradient (pipes)
     *   LIVE_WIRE   — oscillating delta at 50/60 Hz
     *   DENSE_METAL — delta > 5 µT (rebar, conduit, HVAC duct)
     */
    enum class StudMaterial(val label: String, val emoji: String) {
        EMPTY      ("No anomaly detected",           "✅"),
        METAL_SCREW("Metal — screw / nail",          "🔩"),
        METAL_PIPE ("Metal — pipe / duct",           "🚰"),
        LIVE_WIRE  ("Live wire (AC field detected)", "⚡"),
        DENSE_METAL("Dense metal — rebar / conduit", "🏗"),
    }

    /** Result of a stud scan at one position. */
    data class StudReading(
        val material:   StudMaterial,
        val deltaUt:    Float,   // field deviation from baseline (µT)
        val confidence: Float,   // 0–1
    )

    /** Result of a 30-second sleep-environment survey. */
    data class SleepEmfScore(
        val zone:          EmfZone,
        val maxDeltaUt:    Float,
        val avgDeltaUt:    Float,
        val worstAxisLabel: String,
        val advice:        String,
    )

    /** Dirty-electricity analysis for one time window. */
    data class DirtyElectricityReading(
        val varianceUt2:      Float,   // variance of |B| over the window (µT²)
        val dominantFreqBand: String,  // e.g. "50/60 Hz" or "Broadband"
        val dirtyIndex:       Float,   // 0–10 (0 = clean, 10 = very noisy)
    )

    // ── Public API ────────────────────────────────────────────────────────────

    /**
     * Classify the magnetic anomaly at one scan position.
     *
     * @param baselineUt   Field magnitude |B| recorded before scan started.
     * @param currentUt    Field magnitude |B| at this scan position.
     * @param isOscillating  True if AC oscillation detected in recent samples
     *                       (call [isOscillating] to determine this).
     */
    fun classifyStud(
        baselineUt:    Float,
        currentUt:     Float,
        isOscillating: Boolean = false,
    ): StudReading {
        val delta                = abs(currentUt - baselineUt)
        val (material, confidence) = when {
            isOscillating && delta > 0.3f -> StudMaterial.LIVE_WIRE   to 0.80f
            delta > 5f                    -> StudMaterial.DENSE_METAL  to 0.90f
            delta in 0.5f..5f             -> StudMaterial.METAL_SCREW  to 0.75f
            delta in 0.2f..0.5f           -> StudMaterial.METAL_PIPE   to 0.50f
            else                          -> StudMaterial.EMPTY        to 0.95f
        }
        return StudReading(material, delta, confidence)
    }

    /**
     * Classify ambient EMF zone from the peak field deviation observed.
     *
     * @param maxDeltaUt  Maximum deviation from Earth baseline (µT).
     */
    fun emfZone(maxDeltaUt: Float): EmfZone = when {
        maxDeltaUt < 0.2f  -> EmfZone.LOW
        maxDeltaUt < 2f    -> EmfZone.MODERATE
        maxDeltaUt < 10f   -> EmfZone.HIGH
        else               -> EmfZone.ALERT
    }

    /**
     * Score a 30-second magnetometer scan for sleep-environment suitability.
     *
     * @param readings   List of (Bx, By, Bz) triples in µT from TYPE_MAGNETIC_FIELD.
     * @param baseline   Earth-normal field magnitude at this location (µT).
     */
    fun sleepScore(
        readings:  List<Triple<Float, Float, Float>>,
        baseline:  Float,
    ): SleepEmfScore {
        if (readings.isEmpty()) {
            return SleepEmfScore(EmfZone.LOW, 0f, 0f, "—", "No data collected")
        }
        val magnitudes = readings.map { (x, y, z) -> sqrt(x * x + y * y + z * z) }
        val deltas     = magnitudes.map { abs(it - baseline) }
        val maxDelta   = deltas.max()
        val avgDelta   = deltas.average().toFloat()
        val zone       = emfZone(maxDelta)

        // Determine which axis shows the most variation
        val axisX = readings.map { abs(it.first  - readings[0].first) }.average()
        val axisY = readings.map { abs(it.second - readings[0].second) }.average()
        val axisZ = readings.map { abs(it.third  - readings[0].third) }.average()
        val worstAxis = when {
            axisX >= axisY && axisX >= axisZ -> "X axis (East-West)"
            axisY >= axisX && axisY >= axisZ -> "Y axis (North-South)"
            else                             -> "Z axis (Vertical)"
        }
        val advice = when (zone) {
            EmfZone.LOW      -> "✅ Excellent sleep environment — EMF well within safe range"
            EmfZone.MODERATE -> "😐 Acceptable — consider moving devices away from bed"
            EmfZone.HIGH     -> "⚠️ Elevated — check for appliances / wiring on $worstAxis"
            EmfZone.ALERT    -> "🚨 High EMF — locate and remove source on $worstAxis"
        }
        return SleepEmfScore(zone, maxDelta, avgDelta, worstAxis, advice)
    }

    /**
     * Compute dirty-electricity index from a time-series of |B| magnitudes.
     * High variance in a 50/60 Hz band indicates power-line harmonics.
     *
     * @param magnitudesUt  Time-series of |B| readings at ~100 Hz sample rate.
     */
    fun dirtyElectricity(magnitudesUt: List<Float>): DirtyElectricityReading {
        if (magnitudesUt.size < 2) return DirtyElectricityReading(0f, "N/A", 0f)

        val mean     = magnitudesUt.average()
        val variance = magnitudesUt.sumOf { v -> val d = v - mean; d * d } / magnitudesUt.size

        // Zero-crossing rate → dominant frequency band (assumes 100 Hz sampling)
        val crossings = (1 until magnitudesUt.size).count {
            (magnitudesUt[it - 1] - mean) * (magnitudesUt[it] - mean) < 0
        }
        val durationS = (magnitudesUt.size / 100f).coerceAtLeast(0.01f)
        val freqHz    = crossings / (2f * durationS)
        val band      = when {
            freqHz in 45f..65f   -> "50/60 Hz (power-line fundamental)"
            freqHz in 100f..130f -> "100/120 Hz (2nd harmonic)"
            freqHz < 10f         -> "< 10 Hz (slow drift)"
            else                 -> "Broadband (${freqHz.toInt()} Hz)"
        }

        // Log-scale dirty index 0–10
        val dirtyIndex = (ln(variance.toFloat() + 1f) * 2f).coerceIn(0f, 10f)
        return DirtyElectricityReading(variance.toFloat(), band, dirtyIndex)
    }

    /**
     * Return true if the recent |B| time-series shows an AC oscillation
     * consistent with 50 Hz or 60 Hz power-line interference.
     *
     * Uses zero-crossing rate estimation (assumes ~100 Hz sampling).
     */
    fun isOscillating(magnitudesUt: List<Float>): Boolean {
        if (magnitudesUt.size < 6) return false
        val mean      = magnitudesUt.average()
        val crossings = (1 until magnitudesUt.size).count {
            (magnitudesUt[it - 1] - mean) * (magnitudesUt[it] - mean) < 0
        }
        val freqHz = crossings / (2f * (magnitudesUt.size / 100f).coerceAtLeast(0.01f))
        return freqHz in 40f..70f || freqHz in 90f..130f
    }
}
