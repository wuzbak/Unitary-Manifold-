package com.gibbernode.feature.uwb

import androidx.lifecycle.ViewModel
import com.gibbernode.uwb.UWBAdvisor
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import javax.inject.Inject

/**
 * UWBViewModel
 *
 * Manages UWB ranging state, trilateration, and room-map waypoint accumulation.
 *
 * Note: Actual UWB session management (UwbManager, UwbClientSessionScope)
 * requires API 33+ and a UWB-capable device.  On devices without UWB support
 * the screen shows an informational stub.  This ViewModel holds all the
 * pure-logic state; hardware binding happens in the Composable's LaunchedEffect
 * (which checks `PackageManager.FEATURE_UWB`).
 *
 * UWB ranging results (distance, azimuth, elevation) are injected via
 * [updateDevice] — called by the Composable whenever a new UwbRangingResult
 * arrives from the Android UWB session.
 */
@HiltViewModel
class UWBViewModel @Inject constructor() : ViewModel() {

    private val _state = MutableStateFlow(UWBUiState())
    val state: StateFlow<UWBUiState> = _state.asStateFlow()

    // Mutable anchor positions for trilateration (address → [x, y] metres)
    private val anchorPositions = mutableMapOf<String, FloatArray>()

    // ── Device registry ───────────────────────────────────────────────────────

    /** Inject a fresh ranging result for a specific device address. */
    fun updateDevice(address: String, distanceM: Float, azimuthDeg: Float, elevationDeg: Float = 0f, rssi: Int = -80) {
        val device = UWBAdvisor.UWBDevice(address, distanceM, azimuthDeg, elevationDeg, rssi)
        _state.update { s ->
            val devices  = s.devices.toMutableMap().apply { put(address, device) }
            val pointing = UWBAdvisor.findPointingTarget(devices.values.toList())
            s.copy(devices = devices, pointingResult = pointing)
        }
    }

    fun removeDevice(address: String) = _state.update { s ->
        s.copy(devices = s.devices - address)
    }

    fun clearDevices() = _state.update { it.copy(devices = emptyMap(), pointingResult = null) }

    // ── Anchor management ─────────────────────────────────────────────────────

    /** Define a known anchor position for trilateration. */
    fun setAnchorPosition(address: String, x: Float, y: Float) {
        anchorPositions[address] = floatArrayOf(x, y)
        refreshTrilateration()
    }

    private fun refreshTrilateration() {
        val devices = _state.value.devices
        val anchors = anchorPositions.entries
            .mapNotNull { (addr, pos) -> devices[addr]?.let { dev -> dev to pos } }
        val position = if (anchors.size >= 3) UWBAdvisor.trilaterate(anchors) else null
        _state.update { it.copy(trilateratedPosition = position) }
    }

    // ── Room map ──────────────────────────────────────────────────────────────

    /** Stamp the current trilaterated position as a map waypoint. */
    fun stampWaypoint(pressureHpa: Float) {
        val pos = _state.value.trilateratedPosition ?: return
        _state.update { s ->
            s.copy(mapWaypoints = UWBAdvisor.stampWaypoint(s.mapWaypoints, pos, pressureHpa))
        }
    }

    fun clearMap() = _state.update { it.copy(mapWaypoints = emptyList()) }

    // ── Point-to-control ─────────────────────────────────────────────────────

    /** Called when user toggles "point & select" mode. */
    fun togglePointingMode() = _state.update { it.copy(pointingModeActive = !it.pointingModeActive) }

    /** Simulate selecting the currently pointed-at device (SmartHome webhook stub). */
    fun selectPointedDevice() {
        val target = _state.value.pointingResult?.targetDevice ?: return
        _state.update { it.copy(selectedDevice = target) }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// UI State
// ─────────────────────────────────────────────────────────────────────────────

data class UWBUiState(
    val devices:              Map<String, UWBAdvisor.UWBDevice> = emptyMap(),
    val pointingResult:       UWBAdvisor.PointingResult? = null,
    val trilateratedPosition: UWBAdvisor.Position2D? = null,
    val mapWaypoints:         List<UWBAdvisor.MapWaypoint> = emptyList(),
    val pointingModeActive:   Boolean = false,
    val selectedDevice:       UWBAdvisor.UWBDevice? = null,
)
