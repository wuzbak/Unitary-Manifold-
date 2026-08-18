package com.gibbernode.optics

import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.cos
import kotlin.math.exp
import kotlin.math.log10
import kotlin.math.sin
import kotlin.math.sqrt

/**
 * VisualMicrophoneAdvisor — Acoustic video reconstruction from micro-vibrations.
 *
 * Physical basis (Davis et al., SIGGRAPH 2014):
 *   Sound pressure waves cause tiny (<1 µm) oscillations in lightweight objects
 *   (chip bags, leaves, cups, aluminium foil).  A high-frame-rate camera can
 *   track these micro-vibrations via sub-pixel optical flow, and the extracted
 *   motion signal is a direct analogue of the acoustic pressure waveform.
 *
 * At 960 fps (S24 Ultra slow-motion) each frame represents ~1.04 ms,
 * giving a Nyquist frequency of ~480 Hz — sufficient for intelligible speech.
 * At 120 fps, Nyquist is 60 Hz: enough for fundamental pitch but not formants.
 *
 * Algorithm:
 *   1. Track a small (~8×8 px) high-contrast feature in consecutive frames
 *      using phase-based optical flow (or Lucas-Kanade).
 *   2. Extract the sub-pixel vertical displacement over time → vibration trace.
 *   3. Apply DFT to recover the frequency spectrum.
 *   4. Band-pass (300 Hz – Nyquist) to isolate speech frequencies.
 *   5. Optionally reconstruct waveform by inverse DFT.
 *
 * This advisor operates on pre-extracted displacement traces (step 2 output),
 * which decouples it from the OpenCV / GPU optical-flow implementation.
 */
object VisualMicrophoneAdvisor {

    // ── Data classes ──────────────────────────────────────────────────────────

    /**
     * A time-series of sub-pixel object displacements extracted from video.
     *
     * @param displacements  Per-frame vertical (or dominant axis) displacement in sub-pixels.
     * @param frameRateHz    Video capture frame rate.
     */
    data class VibrationTrace(
        val displacements: FloatArray,
        val frameRateHz:   Float,
    ) {
        override fun equals(other: Any?): Boolean =
            other is VibrationTrace &&
            displacements.contentEquals(other.displacements) &&
            frameRateHz == other.frameRateHz
        override fun hashCode(): Int =
            31 * displacements.contentHashCode() + frameRateHz.hashCode()
    }

    /** Frequency spectrum bin (Hz → amplitude). */
    data class SpectrumBin(val freqHz: Float, val amplitude: Float)

    /** Result of acoustic reconstruction from a vibration trace. */
    data class AcousticReconResult(
        val spectrum:           List<SpectrumBin>,  // frequency spectrum (up to Nyquist)
        val dominantFreqHz:     Float,               // peak frequency
        val rmsAmplitude:       Float,               // vibration energy
        val snrDb:              Float,               // signal to noise (dB)
        val speechLikely:       Boolean,             // heuristic: energy in 300–3000 Hz band
        val reconstructedPcm:   FloatArray,          // bandpass-filtered audio-proxy waveform
        val disclaimer:         String = DISCLAIMER,
    ) {
        override fun equals(other: Any?): Boolean =
            other is AcousticReconResult &&
            dominantFreqHz == other.dominantFreqHz &&
            reconstructedPcm.contentEquals(other.reconstructedPcm)
        override fun hashCode(): Int =
            31 * dominantFreqHz.hashCode() + reconstructedPcm.contentHashCode()
    }

    // ── Acoustic band constants ───────────────────────────────────────────────

    const val SPEECH_LOW_HZ:  Float = 300f
    const val SPEECH_HIGH_HZ: Float = 3000f

    // ── Public API ────────────────────────────────────────────────────────────

    /**
     * Reconstruct acoustic content from an object vibration trace.
     *
     * @param trace     Per-frame displacement series from optical flow.
     * @param bandLow   Low cutoff for acoustic bandpass (default [SPEECH_LOW_HZ]).
     * @param bandHigh  High cutoff (default [SPEECH_HIGH_HZ], capped at Nyquist).
     */
    fun reconstruct(
        trace:    VibrationTrace,
        bandLow:  Float = SPEECH_LOW_HZ,
        bandHigh: Float = SPEECH_HIGH_HZ,
    ): AcousticReconResult {
        val sig = trace.displacements
        if (sig.size < 4) {
            return AcousticReconResult(emptyList(), 0f, 0f, Float.NEGATIVE_INFINITY,
                false, FloatArray(0))
        }

        val fps    = trace.frameRateHz
        val nyq    = fps / 2f
        val n      = sig.size
        val df     = fps / n

        // DC removal
        val mean    = sig.average().toFloat()
        val centred = FloatArray(n) { sig[it] - mean }

        // DFT spectrum (half-spectrum)
        val halfN = n / 2
        val spectrum = ArrayList<SpectrumBin>(halfN)
        for (k in 1..halfN) {
            var re = 0f; var im = 0f
            for (t in 0 until n) {
                val theta = -2.0 * PI * k * t / n
                re += centred[t] * cos(theta).toFloat()
                im += centred[t] * sin(theta).toFloat()
            }
            spectrum += SpectrumBin(k * df, sqrt(re * re + im * im) / n)
        }

        val peakBin     = spectrum.maxByOrNull { it.amplitude }
        val domFreq     = peakBin?.freqHz ?: 0f
        val rms         = sqrt(centred.map { it * it }.average().toFloat())

        // Bandpass filter
        val safeBandHigh = bandHigh.coerceAtMost(nyq)
        val filtered     = iirBandpass(centred, fps, bandLow, safeBandHigh)
        val filtRms      = sqrt(filtered.map { it * it }.average().toFloat())
            .coerceAtLeast(1e-7f)

        val snrDb = if (rms > 0f) 20f * log10(filtRms / rms.coerceAtLeast(1e-7f)) else Float.NEGATIVE_INFINITY

        val speechBand = spectrum.filter { it.freqHz in SPEECH_LOW_HZ..SPEECH_HIGH_HZ }
        val speechEnergy = speechBand.sumOf { it.amplitude.toDouble() }.toFloat()
        val totalEnergy  = spectrum.sumOf { it.amplitude.toDouble() }.toFloat().coerceAtLeast(1e-6f)
        val speechLikely = speechEnergy / totalEnergy > 0.3f

        return AcousticReconResult(
            spectrum         = spectrum,
            dominantFreqHz   = domFreq,
            rmsAmplitude     = rms,
            snrDb            = snrDb,
            speechLikely     = speechLikely,
            reconstructedPcm = filtered,
        )
    }

    // ── Private helpers ───────────────────────────────────────────────────────

    private fun iirBandpass(signal: FloatArray, fps: Float, low: Float, high: Float): FloatArray {
        val alphaH = (1f - exp(-2f * PI.toFloat() * high / fps)).coerceIn(0f, 1f)
        val alphaL = (1f - exp(-2f * PI.toFloat() * low  / fps)).coerceIn(0f, 1f)
        // High-pass at high cutoff
        val hp = FloatArray(signal.size)
        var pIn = 0f; var pHp = 0f
        for (i in signal.indices) {
            hp[i] = alphaH * (pHp + signal[i] - pIn); pIn = signal[i]; pHp = hp[i]
        }
        // Low-pass at low cutoff of the HP result
        val bp = FloatArray(signal.size)
        var pLp = 0f
        for (i in signal.indices) {
            bp[i] = pLp + alphaL * (hp[i] - pLp); pLp = bp[i]
        }
        return bp
    }

    const val DISCLAIMER =
        "Visual Microphone reconstruction is an experimental research capability. " +
        "Intelligibility depends on frame rate (>120 fps preferred), object material, " +
        "distance, and vibration amplitude. " +
        "At 120 fps, only sub-speech frequencies are recoverable. " +
        "Do not use for covert audio interception — this may be illegal in your jurisdiction."
}
