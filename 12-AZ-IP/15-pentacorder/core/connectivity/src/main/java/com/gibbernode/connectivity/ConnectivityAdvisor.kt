package com.gibbernode.connectivity

/**
 * ConnectivityAdvisor
 *
 * Pure stateless logic for resilient connectivity tier selection and GPS
 * fix quality estimation.  No Android SDK dependency — fully JVM-testable.
 *
 * The tier stack implements graceful degradation:
 *   Carrier → WiFi → WiFi Direct mesh → Bluetooth relay →
 *   Gibberlink acoustic → Offline (cache-and-forward queue)
 *
 * GPS fix behaviour:
 *   With AGPS (carrier or WiFi available): ~4 s warm/hot fix
 *   Without AGPS (GNSS only):             ~60 s cold fix
 *
 * Dead reckoning is available when the three core IMU sensors
 * (accelerometer, gyroscope, magnetometer) are all present and reporting.
 */
object ConnectivityAdvisor {

    // ── Connectivity tier stack ───────────────────────────────────────────────

    /**
     * Connectivity tiers ordered from best to worst.
     *
     * CARRIER          — LTE / 5G via cell tower
     * WIFI             — any reachable WiFi access point
     * WIFI_DIRECT      — WiFi Direct peer mesh (no AP needed)
     * BLUETOOTH        — BT relay chain (~50 m per hop)
     * GIBBERLINK_ACOUSTIC — acoustic ggwave channel (~5 m, always available)
     * OFFLINE          — no real-time link; data queued to UPBHub for later sync
     */
    enum class ConnectivityTier(
        val label:   String,
        val emoji:   String,
        val maxBps:  Long,      // approximate throughput ceiling
    ) {
        CARRIER(         "Carrier (LTE/5G)",        "📶", 100_000_000L),
        WIFI(            "WiFi",                    "🛜",  50_000_000L),
        WIFI_DIRECT(     "WiFi Direct Mesh",        "📡",  25_000_000L),
        BLUETOOTH(       "Bluetooth Relay",         "🔵",       3_000L),
        GIBBERLINK_ACOUSTIC("Gibberlink Acoustic",  "🔊",          50L),
        OFFLINE(         "Offline — queue active",  "💾",           0L),
    }

    /**
     * Select the best available connectivity tier.
     *
     * @param hasCarrier    True if a mobile data network is active.
     * @param hasWifi       True if a WiFi network is connected.
     * @param hasWifiDirect True if at least one WiFi Direct peer is visible.
     * @param hasBluetooth  True if Bluetooth is enabled.
     * @param hasAcoustic   True if the Gibberlink AudioLoopService is running.
     */
    fun activeTier(
        hasCarrier:    Boolean,
        hasWifi:       Boolean,
        hasWifiDirect: Boolean,
        hasBluetooth:  Boolean,
        hasAcoustic:   Boolean,
    ): ConnectivityTier = when {
        hasCarrier    -> ConnectivityTier.CARRIER
        hasWifi       -> ConnectivityTier.WIFI
        hasWifiDirect -> ConnectivityTier.WIFI_DIRECT
        hasBluetooth  -> ConnectivityTier.BLUETOOTH
        hasAcoustic   -> ConnectivityTier.GIBBERLINK_ACOUSTIC
        else          -> ConnectivityTier.OFFLINE
    }

    // ── GPS fix quality ───────────────────────────────────────────────────────

    /**
     * Estimate time to first GPS fix in seconds.
     *
     * With AGPS (carrier or WiFi): 2–5 s (almanac/ephemeris downloaded).
     * Without AGPS (raw GNSS):    30–90 s cold fix.
     *
     * Returns the pessimistic estimate for each case.
     */
    fun estimateGpsFixSec(hasCarrier: Boolean, hasWifi: Boolean): Int =
        if (hasCarrier || hasWifi) 5 else 60

    /**
     * Human-readable description of the GPS fix quality.
     *
     * @param accM    Horizontal accuracy in metres from the last Location fix.
     * @param hasCarrier Active mobile data connection.
     * @param hasWifi    Active WiFi connection.
     */
    fun gpsQualityHint(accM: Float, hasCarrier: Boolean, hasWifi: Boolean): String = when {
        accM <= 0f   -> "No fix — GNSS acquiring  (est. fix: ${estimateGpsFixSec(hasCarrier, hasWifi)} s)"
        accM <= 3f   -> "✅ Excellent fix  (±${accM.toInt()} m)"
        accM <= 10f  -> "✅ Good fix  (±${accM.toInt()} m)"
        accM <= 30f  -> "⚠ Fair fix  (±${accM.toInt()} m) — partial sky view"
        accM <= 100f -> "⚠ Coarse fix  (±${accM.toInt()} m) — limited satellites"
        else         -> "🚨 Poor fix  (±${accM.toInt()} m) — obstructed sky"
    }

    // ── Dead reckoning ────────────────────────────────────────────────────────

    /**
     * True if IMU dead reckoning can supplement or replace GPS.
     *
     * Requires all three core inertial sensors:
     *   Accelerometer — measures force (gravity + linear)
     *   Gyroscope     — measures rotation rate
     *   Magnetometer  — provides absolute heading reference
     *
     * @param hasAccel True if TYPE_ACCELEROMETER is returning data.
     * @param hasGyro  True if TYPE_GYROSCOPE is returning data.
     * @param hasMag   True if TYPE_MAGNETIC_FIELD is returning data.
     */
    fun deadReckonAvailable(hasAccel: Boolean, hasGyro: Boolean, hasMag: Boolean): Boolean =
        hasAccel && hasGyro && hasMag
}
