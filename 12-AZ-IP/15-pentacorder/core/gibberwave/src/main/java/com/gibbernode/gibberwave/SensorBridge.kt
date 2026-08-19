package com.gibbernode.gibberwave

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject
import javax.inject.Singleton

/**
 * SensorBridge — Hilt singleton that carries live sensor/biometric data
 * across feature-module boundaries without creating circular dependencies.
 *
 * Writers:
 *   - TricorderViewModel  → pushes [SensorBridgeSnapshot] on every sensor tick
 *   - MedicalViewModel    → pushes [BiometricReading] on every HR/SpO₂ update
 *   - TranslateViewModel  → pushes [PentadSnapshot] after every interpretation pass
 *   - SPenViewModel       → pushes [phiHuman] after every finalised S Pen stroke
 *
 * Readers:
 *   - TranslateViewModel  → reads sensor/biometric flows to update Ψ_univ and Ψ_brain
 *   - AssistantViewModel  → reads [pentad] to keep the coherence bar live
 *   - PentadViewModel     → reads [phiHuman] to update Ψ_human (φ3)
 *
 * All flows start with null (no data yet) so consumers can distinguish
 * "never received" from "received a zero-value reading".
 */
@Singleton
class SensorBridge @Inject constructor() {

    // ── Physical-manifold snapshot (from TricorderViewModel) ──────────────────

    private val _sensorSnapshot = MutableStateFlow<SensorBridgeSnapshot?>(null)

    /**
     * Latest sensor snapshot pushed by TricorderViewModel.
     * Null until the first push arrives.
     */
    val sensorSnapshot: StateFlow<SensorBridgeSnapshot?> = _sensorSnapshot.asStateFlow()

    fun pushSensorSnapshot(snapshot: SensorBridgeSnapshot) {
        _sensorSnapshot.value = snapshot
    }

    // ── Biometric reading (from MedicalViewModel) ─────────────────────────────

    private val _biometrics = MutableStateFlow<BiometricReading?>(null)

    /**
     * Latest biometric reading pushed by MedicalViewModel.
     * Null until the first push arrives.
     */
    val biometrics: StateFlow<BiometricReading?> = _biometrics.asStateFlow()

    fun pushBiometrics(reading: BiometricReading) {
        _biometrics.value = reading
    }

    // ── Computed Pentad state (from TranslateViewModel) ───────────────────────

    private val _pentad = MutableStateFlow(PentadSnapshot())

    /**
     * Latest five-body Pentad snapshot computed by TranslateViewModel.
     * Starts at default values (all 0.5) until the first interpretation runs.
     * Read by AssistantViewModel to keep the coherence bar in AssistantSheet live.
     */
    val pentad: StateFlow<PentadSnapshot> = _pentad.asStateFlow()

    fun pushPentad(snapshot: PentadSnapshot) {
        _pentad.value = snapshot
    }

    // ── φ_human — S Pen intent layer (from SPenViewModel) ────────────────────

    private val _phiHuman = MutableStateFlow(0.5f)

    /**
     * Ψ_human intent-layer value (φ3) driven by the S Pen stroke advisor.
     * Updated by [SPenViewModel] after every finalized stroke via [pushPhiHuman].
     * Starts at 0.5 (neutral) until the first S Pen stroke is processed.
     */
    val phiHuman: StateFlow<Float> = _phiHuman.asStateFlow()

    fun pushPhiHuman(value: Float) {
        _phiHuman.value = value.coerceIn(0f, 1f)
    }
}

/**
 * Lightweight snapshot of the physical-manifold sensor fields.
 * Mirrors [com.gibbernode.interpret.SensorSnapshot] but lives in the core:gibberwave
 * module so all feature modules can share it without depending on core:interpret.
 */
data class SensorBridgeSnapshot(
    val accelX: Float       = 0f,
    val accelY: Float       = 0f,
    val accelZ: Float       = 0f,
    val accelMag: Float     = 0f,
    val linAccX: Float      = 0f,
    val linAccY: Float      = 0f,
    val linAccZ: Float      = 0f,
    val magMag: Float       = 0f,
    val pressureHpa: Float  = 0f,
    val ambientTempC: Float = 0f,
    val humidityPct: Float  = 0f,
    val lightLux: Float     = 0f,
    val latitude: Double    = 0.0,
    val longitude: Double   = 0.0,
    val altitude: Double    = 0.0,
    val gpsAccM: Float      = 0f,
    val gpsSpeedMs: Float   = 0f,
    val batteryPct: Int     = -1,
    val batteryTempC: Float = 0f,
    val heartRateBpm: Int   = 0,
)

/**
 * Latest HR and SpO₂ reading from the Medical tab.
 * [hrBpm] is null when no reading is available.
 * [spo2Pct] is null when no reading is available.
 */
data class BiometricReading(
    val hrBpm:   Int?,
    val spo2Pct: Int?,
)

/**
 * Lightweight Pentad snapshot — mirrors the five φ fields from
 * [com.gibbernode.interpret.PentadState] without creating a circular module
 * dependency (core:interpret already depends on core:gibberwave).
 *
 * Pushed by TranslateViewModel after every interpretation pass so that
 * AssistantViewModel can reflect the live situationCoherence in the sheet
 * header without needing a direct cross-module ViewModel reference.
 *
 * All fields default to 0.5 (mid-range) matching the PentadState defaults.
 */
data class PentadSnapshot(
    val phiUniv:            Float = 0.5f,
    val phiBrain:           Float = 0.5f,
    val phiHuman:           Float = 0.5f,
    val phiAI:              Float = 0.5f,
    val phiTrust:           Float = 0.5f,
    val situationCoherence: Float = 0.5f,
)
