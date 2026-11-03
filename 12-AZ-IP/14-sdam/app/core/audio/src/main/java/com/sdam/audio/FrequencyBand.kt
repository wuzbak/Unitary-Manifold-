package com.sdam.audio

/**
 * FrequencyBand — S4
 *
 * Describes the acoustic frequency range used for ggwave transmissions.
 *
 *   AUDIBLE         — 1–6 kHz FSK tones, clearly audible to humans.
 *                     Maps to ggwave AUDIBLE_* protocols (IDs 0–2).
 *
 *   NEAR_ULTRASONIC — nominal high-frequency selection for ggwave
 *                     ULTRASOUND_* protocols (IDs 3–5). Actual emitted
 *                     spectrum, audibility, and device support are unmeasured.
 *
 * The current default is near-ultrasonic; this is not a safety or range claim.
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
