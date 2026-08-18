package com.gibbernode.feature.translate

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gibbernode.gibberwave.SensorBridge
import com.gibbernode.interpret.PentadState
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * PentadViewModel — live five-body Pentad state for the Translate tab.
 *
 * Manages [PentadState] — the snapshot of all five Unitary Pentad φ values:
 *   Ψ_univ  (φ1) — physical manifold coherence (from TricorderViewModel → SensorBridge)
 *   Ψ_brain (φ2) — biological coherence (from MedicalViewModel → SensorBridge biometrics)
 *   Ψ_human (φ3) — intent layer — driven by [SPenAdvisor.phiHuman] via SensorBridge
 *   Ψ_AI    (φ4) — AI precision (from TranslateViewModel translation confidence)
 *   β·C     (φ5) — trust/coupling field (static seed; updated by CalibrationViewModel)
 *
 * φ3 wiring path (SESSION_005):
 *   S Pen stroke → SPenAdvisor.phiHuman() → SPenViewModel.finaliseStroke()
 *     → SensorBridge.pushPhiHuman() → PentadViewModel.phiHuman StateFlow
 *       → PentadUiState.pentad.phiHuman
 *
 * All other bodies are updated via [updateFromBridge] which is called from the
 * shared SensorBridge; see individual update functions for the field mappings.
 */
@HiltViewModel
class PentadViewModel @Inject constructor(
    private val sensorBridge: SensorBridge,
) : ViewModel() {

    private val _state = MutableStateFlow(PentadUiState())
    val state: StateFlow<PentadUiState> = _state.asStateFlow()

    init {
        // φ3 — S Pen intent layer
        viewModelScope.launch {
            sensorBridge.phiHuman.collectLatest { phi ->
                _state.update { s ->
                    val updated = s.pentad.copy(phiHuman = phi)
                    s.copy(pentad = updated, lastPhiHumanSource = "S Pen stroke")
                }
            }
        }

        // φ1+φ2+φ5 — physical manifold and biometrics from the bridge pentad snapshot
        viewModelScope.launch {
            sensorBridge.pentad.collectLatest { snap ->
                _state.update { s ->
                    val updated = s.pentad.copy(
                        phiUniv  = snap.phiUniv,
                        phiBrain = snap.phiBrain,
                        phiAI    = snap.phiAI,
                        phiTrust = snap.phiTrust,
                        // phiHuman is owned here; preserve the S Pen value
                    )
                    s.copy(pentad = updated)
                }
            }
        }
    }

    /**
     * Directly update φ_human from any caller with an explicit source label.
     * Used when an S Pen stroke result is forwarded without going through
     * the SensorBridge (e.g., from [MedicalViewModel] tremor path).
     */
    fun updatePhiHuman(value: Float, source: String = "direct") {
        sensorBridge.pushPhiHuman(value)
        _state.update { s ->
            s.copy(
                pentad             = s.pentad.copy(phiHuman = value.coerceIn(0f, 1f)),
                lastPhiHumanSource = source,
            )
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// UI state
// ─────────────────────────────────────────────────────────────────────────────

data class PentadUiState(
    val pentad:             PentadState = PentadState(),
    val lastPhiHumanSource: String      = "—",
)
