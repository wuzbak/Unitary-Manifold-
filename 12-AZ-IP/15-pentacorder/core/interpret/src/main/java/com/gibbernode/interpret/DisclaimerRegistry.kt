package com.gibbernode.interpret

/**
 * DisclaimerRegistry
 *
 * Maps sensor-feature IDs to the mandatory disclaimer text that must be shown
 * to the user before they can use that feature.
 *
 * Each entry is shown once per feature "install" — the feature layer (ViewModel)
 * tracks whether the user has acknowledged the disclaimer and calls
 * [isAcknowledgedKey] to generate a DataStore / SharedPreferences key.
 *
 * Design principles:
 *   - Offline-first: all disclaimer text is bundled; no network fetch.
 *   - Stateless: this object only supplies text.  Acknowledgement state is
 *     managed by the feature ViewModel (persisted in DataStore).
 *   - Safety: medical and professional-use disclaimers are mandatory (not
 *     dismissible with a blank button).  Non-professional features are
 *     informational-only.
 */
object DisclaimerRegistry {

    // ── Feature IDs ───────────────────────────────────────────────────────────

    const val FEATURE_TREMOR_SCREEN    = "tremor_screen"
    const val FEATURE_SKIN_COLOR       = "skin_color"
    const val FEATURE_PPG_HEART_RATE   = "ppg_heart_rate"
    const val FEATURE_ULTRASONIC_PULSE = "ultrasonic_pulse"
    const val FEATURE_EMF_LIVE_WIRE    = "emf_live_wire"
    const val FEATURE_CONTRACTOR_LEVEL = "contractor_level"
    const val FEATURE_BAROMETER_LUNG   = "barometer_lung"
    const val FEATURE_COSMIC_RAY       = "cosmic_ray"
    const val FEATURE_ACOUSTIC_ALERT   = "acoustic_alert"

    // ── Disclaimer entries ────────────────────────────────────────────────────

    /**
     * Lookup table: feature ID → [DisclaimerEntry].
     * Returns null for features that have no mandatory disclaimer.
     */
    private val entries: Map<String, DisclaimerEntry> = mapOf(

        FEATURE_TREMOR_SCREEN to DisclaimerEntry(
            title    = "⚠️ Tremor Screening — Not a Medical Device",
            body     = "This tool uses S Pen stroke velocity to estimate hand tremor. " +
                       "It is a screening reference only and CANNOT diagnose Parkinson's " +
                       "disease, essential tremor, or any neurological condition. " +
                       "Results must not be used for medical decision-making. " +
                       "Consult a neurologist for clinical assessment.",
            isMedical = true,
        ),

        FEATURE_SKIN_COLOR to DisclaimerEntry(
            title    = "⚠️ Skin Colour Screening — Not a Medical Device",
            body     = "This tool uses front-camera RGB averages to estimate pallor and " +
                       "a jaundice indicator. It is NOT a certified medical device and " +
                       "CANNOT diagnose anaemia, jaundice, or any medical condition. " +
                       "Results depend on lighting, skin tone, and camera quality. " +
                       "Consult a physician for any health concerns.",
            isMedical = true,
        ),

        FEATURE_PPG_HEART_RATE to DisclaimerEntry(
            title    = "⚠️ Camera Heart Rate — Not a Medical Device",
            body     = "Heart rate estimated via remote photoplethysmography (rPPG) " +
                       "from the camera green channel is INDICATIVE ONLY. " +
                       "Accuracy is affected by motion, lighting, and skin tone. " +
                       "Do not use for cardiac monitoring. Use a certified pulse oximeter " +
                       "or ECG device for clinical measurements.",
            isMedical = true,
        ),

        FEATURE_EMF_LIVE_WIRE to DisclaimerEntry(
            title    = "⚠️ Live Wire Detection — Do Not Open Walls",
            body     = "The magnetometer-based live-wire detector is an INDICATIVE TOOL. " +
                       "It cannot guarantee detection of all live wires or " +
                       "replace a certified non-contact voltage tester. " +
                       "NEVER open walls, cut cables, or work on live circuits " +
                       "based solely on this reading. Consult a licensed electrician.",
            isMedical = false,
        ),

        FEATURE_CONTRACTOR_LEVEL to DisclaimerEntry(
            title    = "⚠️ Barometric Level — Not a Surveying Instrument",
            body     = "The barometric precision level is an ESTIMATION TOOL. " +
                       "Results may be affected by HVAC, weather changes, and device " +
                       "temperature. Do not use for structural engineering, safety-critical " +
                       "levelling, or regulatory compliance without a certified instrument.",
            isMedical = false,
        ),

        FEATURE_BAROMETER_LUNG to DisclaimerEntry(
            title    = "⚠️ Barometric Lung Capacity — Reference Only",
            body     = "The charging-port pitot method for peak expiratory flow estimation " +
                       "is an experimental reference tool. It is NOT a certified spirometer. " +
                       "Do not use for asthma management or clinical pulmonary evaluation. " +
                       "Consult a respiratory physician and use a certified peak flow meter.",
            isMedical = true,
        ),

        FEATURE_ACOUSTIC_ALERT to DisclaimerEntry(
            title    = "⚠️ Acoustic Alert Monitor — Supplemental Only",
            body     = "The acoustic event detector (smoke alarm, glass-break) is a " +
                       "SUPPLEMENTAL NOTIFICATION TOOL. It does not replace certified " +
                       "smoke detectors, CO alarms, or security systems. " +
                       "Always install certified life-safety devices. " +
                       "Missed detections can occur due to background noise or distance.",
            isMedical = false,
        ),

        FEATURE_COSMIC_RAY to DisclaimerEntry(
            title    = "ℹ️ Cosmic Ray Detector — Citizen Science",
            body     = "The camera dark-frame radiation detector is for educational " +
                       "and citizen-science purposes only. It cannot measure " +
                       "ionising radiation dose and must not be used as a dosimeter. " +
                       "If you suspect hazardous radiation, contact local authorities " +
                       "and use a certified Geiger counter.",
            isMedical = false,
        ),
    )

    // ── Public API ────────────────────────────────────────────────────────────

    /**
     * Retrieve the disclaimer entry for a feature, or null if none is required.
     */
    fun get(featureId: String): DisclaimerEntry? = entries[featureId]

    /**
     * Return true if a disclaimer exists AND is classified as medical.
     * The UI uses this to decide whether to require an active "I understand"
     * tap rather than a passive dismiss.
     */
    fun isMedical(featureId: String): Boolean = entries[featureId]?.isMedical == true

    /**
     * Generate the DataStore / SharedPreferences key used to persist whether
     * the user has acknowledged this disclaimer.
     * e.g. "disclaimer_ack_tremor_screen"
     */
    fun isAcknowledgedKey(featureId: String): String = "disclaimer_ack_$featureId"

    // ── Data ─────────────────────────────────────────────────────────────────

    /**
     * One disclaimer entry.
     *
     * @param title     Short heading shown in the disclaimer dialog.
     * @param body      Full disclaimer text.
     * @param isMedical True → requires explicit "I understand this is not a
     *                  medical device" confirmation tap; false → passive dismiss OK.
     */
    data class DisclaimerEntry(
        val title:     String,
        val body:      String,
        val isMedical: Boolean,
    )
}
