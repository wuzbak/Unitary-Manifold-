package com.gibbernode.feature.labs

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gibbernode.gibberwave.SensorBridge
import com.gibbernode.gibberwave.SensorBridgeSnapshot
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject
import kotlin.math.abs
import kotlin.math.sqrt

/**
 * ManifoldProbeViewModel
 *
 * Android port of S24Ultra/scripts/manifold_probe.py.
 *
 * Maps live sensor data from [SensorBridge] to the 5D Kaluza-Klein manifold
 * state vector Ψ(t) and runs a discrete-time RK4 field evolution step.
 *
 * Sensor → Manifold field mapping:
 *   Accelerometer [ax, ay, az]  →  g_μν  metric perturbation (δg = a/g_earth − ẑ)
 *   Magnetometer  [mag norm µT] →  B_μ   KK gauge field (norm: 45 µT Earth baseline)
 *   Barometer     [hPa]         →  φ     radion amplitude (norm: 1013.25 hPa ISA)
 *   Battery       [%]           →  φ₀    background radion / stabilisation target
 *   Ambient light [lux]         →  logged (photon flux proxy; not yet in field equations)
 *
 * Evolution outputs (each probe tick):
 *   - Manifold state Ψ [φ, B_norm, R_ricci, det_g, J_inf]
 *   - Constraint monitor (Ricci flag, B flag, φ flag)
 *   - Information current J^μ_inf (mean field divergence)
 *   - Plain-language status line
 */
@HiltViewModel
class ManifoldProbeViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
    private val sensorBridge: SensorBridge,
) : ViewModel() {

    private val _state = MutableStateFlow(ManifoldProbeUiState())
    val state: StateFlow<ManifoldProbeUiState> = _state.asStateFlow()

    // ── Physical constants ────────────────────────────────────────────────────

    private val G_EARTH      = 9.80665f   // m/s² standard gravity
    private val PHI_ISA      = 1013.25f   // hPa  ISA sea-level pressure
    private val B_EARTH_UT   = 45f        // µT   Earth baseline field (mid-latitude IGRF-13)
    private val DT           = 0.1f       // s    RK4 step (10 Hz)
    private val RICCI_LIMIT  = 1.5f       // normalised Ricci scalar stability bound
    private val B_LIMIT      = 3.0f       // normalised B_norm stability bound
    private val PHI_LIMIT    = 1.5f       // radion amplitude stability bound

    // ── State vector [φ, B_norm, R_ricci] ─────────────────────────────────────

    private var stateVec = floatArrayOf(1f, 1f, 0f)  // φ, B_norm, R_ricci

    init {
        viewModelScope.launch {
            sensorBridge.sensorSnapshot.collectLatest { snap ->
                snap ?: return@collectLatest
                evolve(snap)
            }
        }
    }

    // ── RK4 evolution ─────────────────────────────────────────────────────────

    /** One evolution step driven by [snap]. */
    private fun evolve(snap: SensorBridgeSnapshot) {
        // Map sensors to field inputs
        val accelMag  = snap.accelMag
        val gNorm     = accelMag / G_EARTH                                // normalised accel
        val deltaG    = floatArrayOf(                                     // δg perturbation
            snap.accelX / G_EARTH - 0f,
            snap.accelY / G_EARTH - 0f,
            snap.accelZ / G_EARTH - 1f,
        )
        val deltaMag  = sqrt(deltaG.sumOf { (it * it).toDouble() }).toFloat()

        val bNorm     = snap.magMag / B_EARTH_UT                          // normalised B
        val phi       = if (snap.pressureHpa > 0) snap.pressureHpa / PHI_ISA else 1f
        val phi0      = if (snap.batteryPct > 0) snap.batteryPct / 100f else stateVec[0]

        // RK4 field derivatives (simplified Kaluza-Klein analogue)
        //   dφ/dt   = −λ·(φ − φ₀)          (radion relaxation toward battery stabilisation)
        //   dB/dt   = −μ·(B − bNorm)        (gauge field relaxation toward sensor value)
        //   dR/dt   = α·δg_mag − β·R        (Ricci driven by metric perturbation, damped)
        val lambda = 0.5f; val mu = 0.3f; val alpha = 0.8f; val beta = 0.6f

        fun deriv(v: FloatArray): FloatArray = floatArrayOf(
            -lambda * (v[0] - phi0),
            -mu     * (v[1] - bNorm),
            alpha * deltaMag - beta * v[2],
        )

        val k1 = deriv(stateVec)
        val k2 = deriv(floatArrayOf(
            stateVec[0] + DT / 2 * k1[0],
            stateVec[1] + DT / 2 * k1[1],
            stateVec[2] + DT / 2 * k1[2],
        ))
        val k3 = deriv(floatArrayOf(
            stateVec[0] + DT / 2 * k2[0],
            stateVec[1] + DT / 2 * k2[1],
            stateVec[2] + DT / 2 * k2[2],
        ))
        val k4 = deriv(floatArrayOf(
            stateVec[0] + DT * k3[0],
            stateVec[1] + DT * k3[1],
            stateVec[2] + DT * k3[2],
        ))

        for (i in stateVec.indices) {
            stateVec[i] += DT / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i])
        }

        val phiOut   = stateVec[0].coerceIn(0f, 2f)
        val bOut     = stateVec[1].coerceAtLeast(0f)
        val ricciOut = stateVec[2]

        // det(g) approximation from metric perturbation
        val detG = (1f + deltaMag).let { it * it * it * it }  // 4D metric determinant proxy

        // Information current J^μ_inf: mean absolute field gradient
        val jInf = (abs(phiOut - 1f) + abs(bOut - 1f) + abs(ricciOut)) / 3f

        // Constraint flags
        val ricciFlag = abs(ricciOut) > RICCI_LIMIT
        val bFlag     = bOut          > B_LIMIT
        val phiFlag   = phiOut        > PHI_LIMIT

        // Status summary
        val status = buildString {
            when {
                ricciFlag && bFlag -> append("⚠️ Curvature + gauge instability")
                ricciFlag          -> append("⚠️ Ricci curvature out of bounds")
                bFlag              -> append("⚠️ Gauge field B elevated")
                phiFlag            -> append("⚠️ Radion φ above stability bound")
                jInf < 0.05f       -> append("✅ Near Harmonic State — J^μ_inf → 0")
                jInf < 0.15f       -> append("🟡 Mild information gradient")
                else               -> append("🔴 Significant field divergence")
            }
            append(" | φ=%.3f B=%.2f R=%.3f J=%.3f".format(phiOut, bOut, ricciOut, jInf))
        }

        // Keep last 30 J_inf values for the sparkline
        val history = (_state.value.jInfHistory + jInf).takeLast(30)

        _state.update { it.copy(
            phi          = phiOut,
            bNorm        = bOut,
            ricciScalar  = ricciOut,
            detG         = detG,
            jInf         = jInf,
            jInfHistory  = history,
            ricciFlag    = ricciFlag,
            bFlag        = bFlag,
            phiFlag      = phiFlag,
            statusLine   = status,
            // raw inputs for display
            accelMag     = accelMag,
            magMag       = snap.magMag,
            pressureHpa  = snap.pressureHpa,
            batteryPct   = snap.batteryPct,
            lightLux     = snap.lightLux,
        )}
    }

    /** Run one evolution step with synthetic demo data (no sensors required). */
    fun runDemoStep() {
        val fakeMag   = 45f + (Math.random() * 10 - 5).toFloat()
        val fakePres  = 1013f + (Math.random() * 5 - 2.5).toFloat()
        val fakeBatt  = 75
        val fakeLux   = 300f
        val fakeAccX  = (Math.random() * 0.4 - 0.2).toFloat()
        val fakeAccY  = (Math.random() * 0.4 - 0.2).toFloat()
        val fakeAccZ  = 9.8f + (Math.random() * 0.2 - 0.1).toFloat()
        val fakeAccMag = sqrt((fakeAccX * fakeAccX + fakeAccY * fakeAccY + fakeAccZ * fakeAccZ).toDouble()).toFloat()

        evolve(SensorBridgeSnapshot(
            accelX = fakeAccX, accelY = fakeAccY, accelZ = fakeAccZ,
            accelMag = fakeAccMag,
            magMag = fakeMag,
            pressureHpa = fakePres,
            batteryPct = fakeBatt,
            lightLux = fakeLux,
        ))
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// UI State
// ─────────────────────────────────────────────────────────────────────────────

data class ManifoldProbeUiState(
    // Manifold state fields
    val phi:          Float        = 1f,   // radion amplitude (1.0 = ISA baseline)
    val bNorm:        Float        = 1f,   // gauge field normalised to Earth baseline
    val ricciScalar:  Float        = 0f,   // curvature scalar (0 = flat)
    val detG:         Float        = 1f,   // metric determinant proxy
    val jInf:         Float        = 0f,   // information current mean

    // History for sparkline
    val jInfHistory:  List<Float>  = emptyList(),

    // Constraint flags
    val ricciFlag:    Boolean      = false,
    val bFlag:        Boolean      = false,
    val phiFlag:      Boolean      = false,

    // Status
    val statusLine:   String       = "Awaiting sensor data…",

    // Raw sensor inputs for display
    val accelMag:     Float        = 0f,
    val magMag:       Float        = 0f,
    val pressureHpa:  Float        = 0f,
    val batteryPct:   Int          = -1,
    val lightLux:     Float        = 0f,
)
