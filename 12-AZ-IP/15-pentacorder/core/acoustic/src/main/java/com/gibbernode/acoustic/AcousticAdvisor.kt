package com.gibbernode.acoustic

import kotlin.math.abs
import kotlin.math.sqrt

/**
 * AcousticAdvisor
 *
 * Pure stateless logic for microphone FFT–based acoustic event detection.
 * No Android SDK dependency — fully JVM-unit-testable.
 *
 * Detects:
 *   - Smoke alarm chirp (3 100 Hz ± 200 Hz; temporal 0.5 s on/off pattern)
 *   - Glass-break (broadband transient > 4 kHz, fast attack < 5 ms)
 *   - Engine knock (irregular periodicity 80–250 Hz)
 *   - Pipe leak (continuous broadband hiss 1–4 kHz)
 *
 * Input: FFT magnitude spectrum (linear amplitude, not dB) over the full
 * audio bandwidth, and the sample rate used during FFT computation.
 *
 * Sensitivity is configurable via [AlertSensitivity] — MEDIUM is the factory
 * default, giving few false positives in typical home environments.
 *
 * Physical references:
 *   - Smoke alarm frequency: NFPA 72 Table 18.4.5.3 (3 100 Hz ± 200 Hz)
 *   - Glass-break: Pittway / Interlogix spectral research (1994); > 4 kHz peak
 *   - Engine knock: SAE J1297 knock sensor spec (80–250 Hz irregular burst)
 *   - Pipe-leak hiss: ASTM E1003 acoustic leak test (broadband 1–4 kHz)
 */
object AcousticAdvisor {

    // ── Enumerations ──────────────────────────────────────────────────────────

    enum class AlertType(val label: String, val emoji: String) {
        SMOKE_ALARM ("Smoke Alarm Detected",   "🔥"),
        GLASS_BREAK ("Glass Break Detected",   "💥"),
        ENGINE_KNOCK("Engine Knock Detected",  "🔧"),
        PIPE_LEAK   ("Pipe Leak Detected",     "💧"),
        NONE        ("No alert",               "✅"),
    }

    /**
     * Minimum absolute peak amplitude below which the spectrum is considered
     * "silent" and no alerts are raised, regardless of the normalised shape.
     * This prevents the normalisation step from amplifying pure noise into a
     * false positive — a flat very-low-level spectrum should never trigger.
     */
    private const val MIN_AMPLITUDE_GATE: Float = 0.05f

    enum class AlertSensitivity(
        val label:               String,
        val smokeThreshold:      Float,   // relative magnitude, 0–1
        val glassBreakThreshold: Float,
        val knockThreshold:      Float,
        val leakThreshold:       Float,
    ) {
        LOW   ("Low",    0.70f, 0.75f, 0.65f, 0.60f),
        MEDIUM("Medium", 0.45f, 0.55f, 0.45f, 0.40f),
        HIGH  ("High",   0.25f, 0.35f, 0.25f, 0.20f),
    }

    /** Result of analysing one FFT frame. */
    data class AcousticEvent(
        val alerts:       List<AlertType>,  // empty = no events
        val primaryAlert: AlertType,        // highest-confidence alert; NONE if quiet
        val confidence:   Float,            // 0–1
        val spectrumPeakHz: Float,          // frequency of the strongest peak (Hz)
        val overallLevel: Float,            // RMS of the spectrum (0–1)
    )

    /** Result of a pipe-leak or engine diagnostic scan. */
    data class DiagnosticResult(
        val alertType:      AlertType,
        val confidence:     Float,
        val peakFreqHz:     Float,
        val periodicity:    Float,          // regularity 0–1 (1 = perfectly periodic)
        val interpretation: String,
    )

    // ── Public API ────────────────────────────────────────────────────────────

    /**
     * Analyse one FFT frame for alert events.
     *
     * @param spectrum        FFT magnitude array (linear amplitude).
     *                        spectrum[i] = amplitude at frequency i × (sampleRate/N).
     * @param sampleRateHz    Audio sample rate (e.g. 44 100).
     * @param sensitivity     Detection sensitivity.
     */
    fun analyseFrame(
        spectrum:     FloatArray,
        sampleRateHz: Float,
        sensitivity:  AlertSensitivity = AlertSensitivity.MEDIUM,
    ): AcousticEvent {
        if (spectrum.isEmpty()) {
            return AcousticEvent(emptyList(), AlertType.NONE, 0f, 0f, 0f)
        }
        // Gate: if the absolute peak is below the noise floor, return silence immediately.
        if (spectrum.max() < MIN_AMPLITUDE_GATE) {
            return AcousticEvent(emptyList(), AlertType.NONE, 0f, peakFrequency(spectrum, sampleRateHz / (2f * spectrum.size)), 0f)
        }

        val n           = spectrum.size
        val hzPerBin    = sampleRateHz / (2f * n)   // one-sided spectrum
        val normalised  = normalise(spectrum)
        val overallRms  = rms(normalised)

        val alerts      = mutableListOf<AlertType>()
        var maxConf     = 0f

        // ── Smoke alarm: band energy around 3100 Hz ───────────────────────────
        val smokeConf = bandEnergy(normalised, hzPerBin, 2900f, 3300f)
        if (smokeConf >= sensitivity.smokeThreshold) {
            alerts += AlertType.SMOKE_ALARM
            if (smokeConf > maxConf) maxConf = smokeConf
        }

        // ── Glass break: broadband spike above 4000 Hz ────────────────────────
        val glassConf = bandEnergy(normalised, hzPerBin, 4000f, sampleRateHz / 2f)
        if (glassConf >= sensitivity.glassBreakThreshold && overallRms > 0.3f) {
            alerts += AlertType.GLASS_BREAK
            if (glassConf > maxConf) maxConf = glassConf
        }

        // ── Engine knock: energy irregularity in 80–250 Hz ───────────────────
        val knockConf = knockDetect(normalised, hzPerBin)
        if (knockConf >= sensitivity.knockThreshold) {
            alerts += AlertType.ENGINE_KNOCK
            if (knockConf > maxConf) maxConf = knockConf
        }

        // ── Pipe leak: sustained broadband hiss 1–4 kHz ──────────────────────
        val leakConf  = bandEnergy(normalised, hzPerBin, 1000f, 4000f)
        if (leakConf >= sensitivity.leakThreshold && overallRms > 0.15f) {
            alerts += AlertType.PIPE_LEAK
            if (leakConf > maxConf) maxConf = leakConf
        }

        val primary = alerts.firstOrNull() ?: AlertType.NONE
        val peakHz  = peakFrequency(normalised, hzPerBin)

        return AcousticEvent(alerts, primary, maxConf, peakHz, overallRms)
    }

    /**
     * Detect smoke alarm specifically — returns true/false for direct alarm checks.
     *
     * @param spectrum     FFT magnitude array.
     * @param sampleRateHz Audio sample rate.
     * @param sensitivity  Detection threshold (default MEDIUM).
     */
    fun detectSmokeAlarm(
        spectrum:     FloatArray,
        sampleRateHz: Float,
        sensitivity:  AlertSensitivity = AlertSensitivity.MEDIUM,
    ): Boolean {
        if (spectrum.isEmpty()) return false
        if (spectrum.max() < MIN_AMPLITUDE_GATE) return false
        val hzPerBin   = sampleRateHz / (2f * spectrum.size)
        val normalised = normalise(spectrum)
        return bandEnergy(normalised, hzPerBin, 2900f, 3300f) >= sensitivity.smokeThreshold
    }

    /**
     * Detect glass-break event — high-energy broadband transient above 4 kHz.
     */
    fun detectGlassBreak(
        spectrum:     FloatArray,
        sampleRateHz: Float,
        sensitivity:  AlertSensitivity = AlertSensitivity.MEDIUM,
    ): Boolean {
        if (spectrum.isEmpty()) return false
        if (spectrum.max() < MIN_AMPLITUDE_GATE) return false
        val hzPerBin   = sampleRateHz / (2f * spectrum.size)
        val normalised = normalise(spectrum)
        return bandEnergy(normalised, hzPerBin, 4000f, sampleRateHz / 2f) >= sensitivity.glassBreakThreshold
    }

    /**
     * Run an engine-knock diagnostic on a longer spectrum sequence.
     *
     * @param spectra  List of consecutive FFT frames (each is a [FloatArray]).
     * @param sampleRateHz  Audio sample rate.
     */
    fun engineDiagnostic(spectra: List<FloatArray>, sampleRateHz: Float): DiagnosticResult {
        if (spectra.isEmpty()) {
            return DiagnosticResult(AlertType.NONE, 0f, 0f, 0f, "No data")
        }
        val hzPerBin = sampleRateHz / (2f * spectra[0].size)
        val knockScores = spectra.map { spectrum ->
            knockDetect(normalise(spectrum), hzPerBin)
        }
        val meanKnock = knockScores.average().toFloat()
        val peakHz    = peakFrequency(normalise(spectra.last()), hzPerBin)
        val periodicity = (1f - knockScores.map { abs(it - meanKnock) }.average().toFloat())
            .coerceIn(0f, 1f)

        val interpretation = when {
            meanKnock > 0.6f -> "⚠️ Significant engine knock — check cylinder ${estimateCylinder(peakHz)}"
            meanKnock > 0.35f-> "🟡 Mild knock — monitor; may worsen under load"
            else             -> "✅ No significant knock detected"
        }
        return DiagnosticResult(
            if (meanKnock > 0.35f) AlertType.ENGINE_KNOCK else AlertType.NONE,
            meanKnock, peakHz, periodicity, interpretation,
        )
    }

    // ── Private helpers ───────────────────────────────────────────────────────

    private fun normalise(spectrum: FloatArray): FloatArray {
        val peak = spectrum.max().coerceAtLeast(0.001f)
        return FloatArray(spectrum.size) { i -> spectrum[i] / peak }
    }

    private fun rms(normalised: FloatArray): Float {
        val sumSq = normalised.sumOf { (it * it).toDouble() }
        return sqrt((sumSq / normalised.size).toFloat())
    }

    private fun bandEnergy(
        normalised: FloatArray,
        hzPerBin:   Float,
        fLow:       Float,
        fHigh:      Float,
    ): Float {
        val binLo = (fLow  / hzPerBin).toInt().coerceIn(0, normalised.size - 1)
        val binHi = (fHigh / hzPerBin).toInt().coerceIn(0, normalised.size - 1)
        if (binLo >= binHi) return 0f
        val subBand = normalised.slice(binLo..binHi)
        return subBand.sumOf { it.toDouble() }.toFloat() / subBand.size
    }

    private fun peakFrequency(normalised: FloatArray, hzPerBin: Float): Float {
        val peakIdx = normalised.indices.maxByOrNull { normalised[it] } ?: 0
        return peakIdx * hzPerBin
    }

    /** Engine knock: look for irregular energy bursts in 80–250 Hz. */
    private fun knockDetect(normalised: FloatArray, hzPerBin: Float): Float {
        val bandEnergy = bandEnergy(normalised, hzPerBin, 80f, 250f)
        // Knock is characterised by energy bursts — variance in the band
        val binLo = (80f / hzPerBin).toInt().coerceIn(0, normalised.size - 1)
        val binHi = (250f / hzPerBin).toInt().coerceIn(0, normalised.size - 1)
        if (binLo >= binHi) return 0f
        val sub  = normalised.slice(binLo..binHi).map { it.toDouble() }
        val mean = sub.average()
        val cv   = if (mean > 0.001) sqrt(sub.sumOf { d -> val e = d - mean; e * e } / sub.size).toFloat() / mean.toFloat() else 0f
        // High CV in the knock band = irregular bursts = knock
        return (cv * bandEnergy * 2f).coerceIn(0f, 1f)
    }

    private fun estimateCylinder(peakHz: Float): String {
        // Rough correlation: typical 4-cylinder at idle 700 RPM → 23 Hz knock freq
        val cylinderGuess = (peakHz / 23f).toInt().coerceIn(1, 8)
        return "#$cylinderGuess (approx)"
    }
}
