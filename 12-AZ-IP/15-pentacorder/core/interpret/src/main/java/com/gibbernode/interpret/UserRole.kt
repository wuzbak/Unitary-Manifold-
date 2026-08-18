package com.gibbernode.interpret

/**
 * UserRole — the Ψ_human intent layer of the Unitary Pentad.
 *
 * Controls how sensor data and protocol payloads are interpreted.
 * The same barometric drop means different things to a nurse
 * (patient room conditions), a first responder (structural risk),
 * or an engineer (equipment state).
 *
 * Maps to pentad body 3: Ψ_human — semantic direction / judgment.
 */
enum class UserRole(
    val displayName: String,
    val emoji: String,
    val description: String,
) {
    /** Medical staff — triage, vitals monitoring, medication, patient translation. */
    NURSE(
        displayName = "Nurse / Medic",
        emoji       = "🏥",
        description = "Vitals-first lens: clinical interpretation of all sensor data",
    ),

    /** Emergency / rescue / disaster — hazard detection, victim location, triage. */
    FIRST_RESPONDER(
        displayName = "First Responder",
        emoji       = "🚨",
        description = "Threat-first lens: structural risk, hazmat, victim location",
    ),

    /** Infrastructure, industrial, mechanical — equipment state, fault diagnosis. */
    ENGINEER(
        displayName = "Engineer",
        emoji       = "🔧",
        description = "Systems-first lens: equipment faults, structural integrity, EM fields",
    ),

    /** Research, data collection, manifold science. */
    SCIENTIST(
        displayName = "Scientist",
        emoji       = "🔬",
        description = "Manifold-first lens: Ψ(t) field deviations, information gaps",
    ),

    /** No specific role — balanced general-purpose interpretation. */
    DEFAULT(
        displayName = "General",
        emoji       = "📱",
        description = "Balanced interpretation across all domains",
    ),
}
