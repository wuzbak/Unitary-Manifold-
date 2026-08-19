package com.sdam.audio

/**
 * FrequencyBand — S4
 *
 * Describes the acoustic frequency range used for ggwave transmissions.
 *
 *   AUDIBLE         — 1–6 kHz FSK tones, clearly audible to humans.
 *                     Maps to ggwave AUDIBLE_* protocols (IDs 0–2).
 *
 *   NEAR_ULTRASONIC — 17–22 kHz FSK tones, above the normal adult hearing
 *                     threshold but within Android AudioRecord capability at
 *                     48 kHz sample rate.
 *                     Maps to ggwave ULTRASOUND_* protocols (IDs 3–5).
 *
 * Near-ultrasonic is the **default band** per S4 specification.
 */
enum class FrequencyBand(
    val label: String,
    val freqRangeKhz: String,
    val baseProtocol: TxProtocol,
    val freqLowHz: Int,
    val freqHighHz: Int,
) {

    AUDIBLE(
        label        = "Audible",
        freqRangeKhz = "1–6 kHz",
        baseProtocol = TxProtocol.AUDIBLE_FAST,
        freqLowHz    = 1_000,
        freqHighHz   = 6_000,
    ),

    NEAR_ULTRASONIC(
        label        = "Near-Ultrasonic",
        freqRangeKhz = "17–22 kHz",
        baseProtocol = TxProtocol.ULTRASOUND_FAST,
        freqLowHz    = 17_000,
        freqHighHz   = 22_000,
    );

    companion object {
        /** Default: near-ultrasonic per S4 spec. */
        val DEFAULT: FrequencyBand = NEAR_ULTRASONIC

        fun fromOrdinal(ordinal: Int): FrequencyBand =
            entries.getOrElse(ordinal) { DEFAULT }
    }
}
