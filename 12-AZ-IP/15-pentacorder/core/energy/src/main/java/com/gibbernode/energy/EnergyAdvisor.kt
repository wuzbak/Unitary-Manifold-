package com.gibbernode.energy

import kotlin.math.pow

/**
 * EnergyAdvisor
 *
 * Pure stateless logic for battery governance and ambient RF harvest advisory.
 * No Android SDK dependency — fully unit-testable on the JVM.
 *
 * Implements the battery state machine and harvest advisory described in
 * BV9900Pro-HomeTest/docs/ENERGY_HARVESTING.md Part 5.
 *
 * Physics:
 *   P_mW = 10^(RSSI_dBm / 10)                 — dBm → milliwatts (linear)
 *   P_harvest_µW = ΣP_mW × η × 1e3            — η ≈ 0.5 rectenna efficiency; ×1e3 = mW→µW
 *
 * The harvest estimate is advisory only — actual energy delivery requires an
 * external rectenna chip (e.g. Powercast P2110B) connected via USB-C.
 */
object EnergyAdvisor {

    // ── Battery state machine ─────────────────────────────────────────────────

    /**
     * Battery state bands — mirrors the five-state machine in ENERGY_HARVESTING.md.
     *
     * CRITICAL      < 10%   Emergency only — no sharing, no new sensors
     * FLOOR         10–20%  Read-only, harvest mode active, no sharing
     * BALANCED      20–60%  Normal operation, harvest if available
     * SHARE_ELIGIBLE 60–80% Normal + sharing allowed
     * SURPLUS       > 80%   Active sharing offer to accessories
     */
    enum class EnergyBand(
        val label:    String,
        val emoji:    String,
        val minPct:   Int,
    ) {
        CRITICAL("Critical",        "🔴", 0),
        FLOOR("Floor",              "🟠", 10),
        BALANCED("Balanced",        "🟡", 20),
        SHARE_ELIGIBLE("Share-OK",  "🟢", 60),
        SURPLUS("Surplus",          "💚", 80);

        companion object {
            fun from(battPct: Int): EnergyBand = when {
                battPct < 10 -> CRITICAL
                battPct < 20 -> FLOOR
                battPct < 60 -> BALANCED
                battPct < 80 -> SHARE_ELIGIBLE
                else         -> SURPLUS
            }
        }
    }

    // ── RF Harvest Advisory ────────────────────────────────────────────────────

    /**
     * @param rfEstimateUw  Estimated ambient RF harvest in µW (advisory only).
     * @param bestSsid      SSID of the strongest access point.
     * @param bestRssiDbm   RSSI of the strongest access point in dBm.
     * @param totalAps      Number of access points detected.
     * @param hint          Human-readable placement hint.
     */
    data class HarvestAdvisory(
        val rfEstimateUw: Double,
        val bestSsid:     String,
        val bestRssiDbm:  Int,
        val totalAps:     Int,
        val hint:         String,
    )

    /** Empty advisory returned before any scan has completed. */
    val NO_ADVISORY = HarvestAdvisory(
        rfEstimateUw = 0.0,
        bestSsid     = "—",
        bestRssiDbm  = -100,
        totalAps     = 0,
        hint         = "Tap 'Scan WiFi' to compute harvest advisory",
    )

    /**
     * Compute an RF harvest advisory from a WiFi RSSI scan.
     *
     * @param apRssiMap  Map of SSID (or BSSID) → RSSI in dBm.
     */
    fun rfHarvestAdvisory(apRssiMap: Map<String, Int>): HarvestAdvisory {
        if (apRssiMap.isEmpty()) {
            return HarvestAdvisory(0.0, "—", -100, 0, "No WiFi APs detected — move to a WiFi-rich environment")
        }

        val best = apRssiMap.maxByOrNull { it.value }!!

        // Σ linear power (mW) across all APs
        val sumLinearMw = apRssiMap.values.sumOf { rssi ->
            10.0.pow(rssi / 10.0)
        }

        // Dimensional analysis:
        //   10^(rssi/10) = power in mW (by definition of dBm)
        //   Σ mW across all APs = total incident linear power
        //   × η (0.5) = rectenna conversion efficiency
        //   × 1e3 = mW → µW
        //   The result is the estimated harvestable power in µW for a 1 cm² aperture.
        //   (Aperture-area scaling is implicit — real antennas vary; this is advisory.)
        val harvestUw = sumLinearMw * 0.5 * 1e3

        val hint = buildString {
            when {
                best.value > -40 -> append("Excellent RF — ${best.key} (${best.value} dBm).  Hold device steady.")
                best.value > -55 -> append("Good RF — stay near ${best.key} (${best.value} dBm).")
                best.value > -70 -> append("Moderate RF — move closer to ${best.key} (${best.value} dBm).")
                else             -> append("Weak RF (${best.value} dBm) — seek a stronger WiFi source.")
            }
            append("  External rectenna required for actual power delivery.")
        }

        return HarvestAdvisory(
            rfEstimateUw = harvestUw,
            bestSsid     = best.key,
            bestRssiDbm  = best.value,
            totalAps     = apRssiMap.size,
            hint         = hint,
        )
    }

    // ── PowerShare governance ─────────────────────────────────────────────────

    /**
     * @param canShare      Whether the Sentinel is allowed to share power now.
     * @param reason        Human-readable decision reason.
     * @param fillTargetPct Target charge level for the accessory (default 50%).
     */
    data class PowerShareDecision(
        val canShare:      Boolean,
        val reason:        String,
        val fillTargetPct: Int = 50,
    )

    /**
     * Evaluate whether the device should activate Wireless PowerShare.
     *
     * Safe by design: returns canShare=false for any condition that could damage
     * battery health or compromise the device's own mission readiness.
     *
     * @param sentinelPct   Sentinel (this device) battery percentage.
     * @param accessoryPct  Accessory battery percentage (−1 = unknown).
     * @param batTempC      Battery temperature in °C.
     */
    fun powerShareDecision(
        sentinelPct:  Int,
        accessoryPct: Int,
        batTempC:     Float = 25f,
    ): PowerShareDecision = when {
        sentinelPct < 0  ->
            PowerShareDecision(false, "Battery level unknown — cannot evaluate")
        batTempC > 40f   ->
            PowerShareDecision(false, "Battery too hot (%.1f°C) — thermal protection active".format(batTempC))
        sentinelPct < 20 ->
            PowerShareDecision(false, "Sentinel at ${sentinelPct}% — below floor (20%). Lockdown.")
        sentinelPct < 60 ->
            PowerShareDecision(false, "Sentinel at ${sentinelPct}% — need ≥ 60% to share safely")
        accessoryPct < 0 ->
            PowerShareDecision(false, "Accessory battery unknown — enter level to evaluate")
        accessoryPct > 50 ->
            PowerShareDecision(false, "Accessory at ${accessoryPct}% — already at fill target (50%)")
        else ->
            PowerShareDecision(
                canShare      = true,
                reason        = "Sentinel surplus (${sentinelPct}%) → share to accessory at ${accessoryPct}%",
                fillTargetPct = 50,
            )
    }
}
