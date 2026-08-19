package com.gibbernode.interpret

/**
 * PentadState — live snapshot of all five Unitary Pentad body φ values.
 *
 * Maps exactly to the Python PentadSystem in Unitary-Manifold/Unitary Pentad/unitary_pentad.py.
 *
 * Bodies:
 *   Ψ_univ  (φ1) — Physical manifold — driven by sensor data
 *   Ψ_brain (φ2) — Biological observer — driven by heart rate / biometrics
 *   Ψ_human (φ3) — Intent layer — driven by user role + action
 *   Ψ_AI    (φ4) — Operational precision — driven by translation confidence
 *   β·C     (φ5) — Trust / coupling field — driven by calibration + data quality
 *
 * The (5,7) braid stability bound: braided sound speed c_s = 12/37 ≈ 0.324.
 * Coupling fraction ρ = 35/37 ≈ 0.946.
 * Trust floor: φ_trust_min = 0.1.
 *
 * All φ values are normalised to [0, 1].  1.0 = fully coherent / healthy / trusted.
 */
data class PentadState(
    /** Ψ_univ — sensor coherence (barometer, GPS, accelerometer in stable ranges). */
    val phiUniv: Float  = 0.5f,

    /** Ψ_brain — biological coherence (HR, SpO₂, temperature within normal ranges). */
    val phiBrain: Float = 0.5f,

    /** Ψ_human — intent coherence (active role selected, translation in progress). */
    val phiHuman: Float = 0.5f,

    /** Ψ_AI — AI precision (translation confidence, LLM response quality). */
    val phiAI: Float    = 0.5f,

    /** β·C — trust/coupling field (calibration quality, sensor count, data freshness). */
    val phiTrust: Float = 0.5f,
) {
    companion object {
        const val TRUST_PHI_MIN       = 0.1f
        const val BRAIDED_SOUND_SPEED = 12f / 37f   // ≈ 0.324
        const val COUPLING_FRACTION   = 35f / 37f   // ≈ 0.946
    }

    /**
     * All 10 pairwise information gaps ΔI_{ij}.
     * Each gap is the absolute difference between the two body φ values.
     * In the Harmonic State all ten gaps → 0.
     */
    val pairwiseGaps: List<Pair<String, Float>> get() = listOf(
        "univ↔brain"  to kotlin.math.abs(phiUniv  - phiBrain),
        "univ↔human"  to kotlin.math.abs(phiUniv  - phiHuman),
        "univ↔ai"     to kotlin.math.abs(phiUniv  - phiAI),
        "univ↔trust"  to kotlin.math.abs(phiUniv  - phiTrust),
        "brain↔human" to kotlin.math.abs(phiBrain - phiHuman),
        "brain↔ai"    to kotlin.math.abs(phiBrain - phiAI),
        "brain↔trust" to kotlin.math.abs(phiBrain - phiTrust),
        "human↔ai"    to kotlin.math.abs(phiHuman - phiAI),
        "human↔trust" to kotlin.math.abs(phiHuman - phiTrust),
        "ai↔trust"    to kotlin.math.abs(phiAI    - phiTrust),
    )

    /**
     * Mean Information Gap — single scalar measure of how far the system is
     * from the Harmonic State.  0 = full coherence; 1 = maximum incoherence.
     */
    val meanInfoGap: Float get() = pairwiseGaps.map { it.second }.average().toFloat()

    /**
     * Situation Coherence — inverse of meanInfoGap, scaled to [0, 1].
     * 1.0 = "everyone understands what's happening" (Harmonic State).
     */
    val situationCoherence: Float get() = 1f - meanInfoGap

    /**
     * True when the trust field is above the minimum threshold and the
     * system is within the braided stability bound.
     */
    val isBraidStable: Boolean get() = phiTrust >= TRUST_PHI_MIN
}
