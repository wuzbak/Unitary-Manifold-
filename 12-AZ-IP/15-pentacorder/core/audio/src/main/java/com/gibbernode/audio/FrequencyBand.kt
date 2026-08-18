package com.gibbernode.audio

/**
 * FrequencyBand
 *
 * Describes the acoustic frequency range used for ggwave transmissions.
 *
 * Two bands are supported:
 *
 *   AUDIBLE        — 1–6 kHz FSK tones, clearly audible to humans.
 *                    Best for noisy environments where the listener may
 *                    need to confirm the chirp acoustically.
 *                    Maps to ggwave AUDIBLE_* protocols (IDs 0–2).
 *
 *   NEAR_ULTRASONIC — 17–22 kHz FSK tones, above the normal adult hearing
 *                    threshold but well within Android AudioRecord capability
 *                    at 48 kHz sample rate.  Preferred default for:
 *                    - Covert machine-to-machine channel (humans don't notice)
 *                    - Reduced interference from ambient speech / music
 *                    Maps to ggwave ULTRASOUND_* protocols (IDs 3–5).
 *
 * Near-ultrasonic is the **default band** for GibberNode.  The CalibrationWizard
 * switches to AUDIBLE only if the noise floor calibration detects strong HF
 * interference or if the device membrane roll-off makes near-ultrasonic unsafe.
 *
 * Reference: Gibberlink ROADMAP.md §S4 — "17–22 kHz near-ultrasonic default".
 */
enum class FrequencyBand(
    /** Human-readable label for the UI. */
    val label: String,
    /** Approximate frequency range in kHz. */
    val freqRangeKhz: String,
    /** Recommended base ggwave TX protocol when this band is active. */
    val baseProtocol: TxProtocol,
    /** Lower bound of the band in Hz (for noise floor FFT filtering). */
    val freqLowHz: Int,
    /** Upper bound of the band in Hz. */
    val freqHighHz: Int,
) {

    /**
     * Audible range — 1–6 kHz FSK.
     * AUDIBLE_FAST is the balanced default (2 s / 32-byte payload).
     */
    AUDIBLE(
        label       = "Audible",
        freqRangeKhz = "1–6 kHz",
        baseProtocol = TxProtocol.AUDIBLE_FAST,
        freqLowHz   = 1_000,
        freqHighHz  = 6_000,
    ),

    /**
     * Near-ultrasonic range — 17–22 kHz FSK.
     * ULTRASOUND_FAST is the default (inaudible to most adults, audible to pets).
     * Requires sample rate ≥ 44.1 kHz — AudioRecord at 48 kHz is sufficient.
     */
    NEAR_ULTRASONIC(
        label        = "Near-Ultrasonic",
        freqRangeKhz = "17–22 kHz",
        baseProtocol = TxProtocol.ULTRASOUND_FAST,
        freqLowHz    = 17_000,
        freqHighHz   = 22_000,
    );

    companion object {
        /** The default frequency band — near-ultrasonic per S4 spec. */
        val DEFAULT: FrequencyBand = NEAR_ULTRASONIC

        fun fromOrdinal(ordinal: Int): FrequencyBand =
            entries.getOrElse(ordinal) { DEFAULT }
    }
}
