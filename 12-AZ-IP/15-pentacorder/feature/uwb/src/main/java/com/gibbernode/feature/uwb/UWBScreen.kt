package com.gibbernode.feature.uwb

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.gibbernode.uwb.UWBAdvisor
import com.gibbernode.ui.GibberBlue
import com.gibbernode.ui.GibberGreen
import com.gibbernode.ui.OnSurfaceDim
import com.gibbernode.ui.SurfaceDark
import kotlin.math.cos
import kotlin.math.sin

/**
 * UWBScreen — 📡 UWB Spatial Lab
 *
 * Sub-tabs:
 *  0 — 📍 Ranging     : live distance + azimuth compass
 *  1 — 🗺️ Room Map    : walk-through floor-plan builder
 *  2 — 🔦 Point & Control : azimuth-based device selection
 */
@Composable
fun UWBScreen(viewModel: UWBViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    var tab   by remember { mutableIntStateOf(0) }

    Column(modifier = Modifier.fillMaxSize()) {
        ScrollableTabRow(selectedTabIndex = tab, edgePadding = 0.dp) {
            Tab(selected = tab == 0, onClick = { tab = 0 }, text = { Text("📍 Ranging", fontSize = 13.sp) })
            Tab(selected = tab == 1, onClick = { tab = 1 }, text = { Text("🗺️ Room Map", fontSize = 13.sp) })
            Tab(selected = tab == 2, onClick = { tab = 2 }, text = { Text("🔦 Point & Control", fontSize = 13.sp) })
        }
        when (tab) {
            0 -> RangingTab(state, viewModel)
            1 -> RoomMapTab(state, viewModel)
            2 -> PointControlTab(state, viewModel)
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 0 — Ranging
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun RangingTab(state: UWBUiState, vm: UWBViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        if (state.devices.isEmpty()) {
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("📡 No UWB devices detected", style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(8.dp))
                    Text("Requires a UWB-capable anchor or Samsung SmartTag+.\nAndroid API 33+ needed for UwbManager.",
                        style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
                    Spacer(Modifier.height(8.dp))
                    Text("ℹ️ In production: UWB session starts from UwbClientSessionScope. Ranging results flow into UWBViewModel.updateDevice(…).",
                        style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                }
            }
        }

        state.devices.values.forEach { device ->
            UWBDeviceCard(device)
        }
    }
}

@Composable
private fun UWBDeviceCard(device: UWBAdvisor.UWBDevice) {
    Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(device.address, style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(8.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                Column(modifier = Modifier.weight(1f)) {
                    DeviceRow("Distance",  "%.2f m".format(device.distanceM))
                    DeviceRow("Azimuth",   "%.1f°".format(device.azimuthDeg))
                    DeviceRow("Elevation", "%.1f°".format(device.elevationDeg))
                    DeviceRow("RSSI",      "${device.rssi} dBm")
                }
                // Mini compass
                Canvas(modifier = Modifier.size(60.dp)) {
                    val cx = size.width / 2; val cy = size.height / 2; val r = cx * 0.9f
                    drawCircle(color = Color(0xFF263238), radius = r)
                    drawCircle(color = Color(0xFF37474F), radius = r, style = androidx.compose.ui.graphics.drawscope.Stroke(1f))
                    val az = Math.toRadians(device.azimuthDeg.toDouble())
                    drawLine(
                        color = Color(0xFF64B5F6),
                        start = Offset(cx, cy),
                        end   = Offset(cx + r * sin(az).toFloat() * 0.8f, cy - r * cos(az).toFloat() * 0.8f),
                        strokeWidth = 3f,
                    )
                    drawCircle(color = Color(0xFF64B5F6), radius = 4f, center = Offset(cx, cy))
                }
            }
            Spacer(Modifier.height(4.dp))
            Text(UWBAdvisor.signalQuality(device.distanceM, device.rssi), style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
        }
    }
}

@Composable
private fun DeviceRow(label: String, value: String) {
    Row(modifier = Modifier.fillMaxWidth().padding(vertical = 1.dp)) {
        Text(label, style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim, modifier = Modifier.weight(1f))
        Text(value, style = MaterialTheme.typography.labelSmall, fontFamily = FontFamily.Monospace)
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 1 — Room Map
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun RoomMapTab(state: UWBUiState, vm: UWBViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text("Walk through the space. Stamp your position every 1 m to build a floor plan.",
            style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = { vm.stampWaypoint(1013.25f) },
                enabled = state.trilateratedPosition != null,
                modifier = Modifier.weight(1f)) {
                Text("📍 Stamp Waypoint")
            }
            OutlinedButton(onClick = vm::clearMap, modifier = Modifier.weight(1f)) {
                Text("↺ Clear Map")
            }
        }

        state.trilateratedPosition?.let { pos ->
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Current Position (trilaterated)", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                    Text("X = %.2f m  Y = %.2f m".format(pos.x, pos.y), style = MaterialTheme.typography.bodyMedium, fontFamily = FontFamily.Monospace)
                    Text("Confidence: %.0f%%".format(pos.confidence * 100f), style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                }
            }
        }

        // Waypoint map
        if (state.mapWaypoints.size >= 2) {
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Floor Plan (${state.mapWaypoints.size} waypoints)", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(8.dp))
                    Canvas(modifier = Modifier.fillMaxWidth().height(200.dp)) {
                        val w = size.width; val h = size.height
                        val xs = state.mapWaypoints.map { it.x }
                        val ys = state.mapWaypoints.map { it.y }
                        val minX = xs.min(); val maxX = xs.max(); val rangeX = (maxX - minX).coerceAtLeast(0.1f)
                        val minY = ys.min(); val maxY = ys.max(); val rangeY = (maxY - minY).coerceAtLeast(0.1f)

                        fun tx(x: Float) = 20f + (x - minX) / rangeX * (w - 40f)
                        fun ty(y: Float) = 20f + (y - minY) / rangeY * (h - 40f)

                        for (i in 1 until state.mapWaypoints.size) {
                            val a = state.mapWaypoints[i - 1]; val b = state.mapWaypoints[i]
                            drawLine(color = Color(0xFF64B5F6), start = Offset(tx(a.x), ty(a.y)), end = Offset(tx(b.x), ty(b.y)), strokeWidth = 2f)
                        }
                        state.mapWaypoints.forEach { wp ->
                            drawCircle(color = Color(0xFF81C784), radius = 5f, center = Offset(tx(wp.x), ty(wp.y)))
                        }
                    }
                }
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 2 — Point & Control
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun PointControlTab(state: UWBUiState, vm: UWBViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text("Point the phone at a UWB device to select it. Tap the trigger when aligned.",
            style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)

        Button(onClick = vm::togglePointingMode, modifier = Modifier.fillMaxWidth(),
            colors = if (state.pointingModeActive) ButtonDefaults.buttonColors(containerColor = Color(0xFF1B5E20))
                     else ButtonDefaults.buttonColors()) {
            Text(if (state.pointingModeActive) "🎯 Pointing Mode ACTIVE" else "▶ Activate Pointing Mode")
        }

        state.pointingResult?.let { r ->
            val alignColor = if (r.isPointing) GibberGreen else androidx.compose.ui.graphics.Color(0xFFFF6D00)
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Target: ${r.targetDevice.address}", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(8.dp))
                    DeviceRow("Alignment", "%.1f°".format(r.alignmentDeg))
                    DeviceRow("Distance",  "%.2f m".format(r.targetDevice.distanceM))
                    DeviceRow("Confidence","%.0f%%".format(r.confidence * 100f))
                    Spacer(Modifier.height(8.dp))
                    if (r.isPointing) {
                        Text("✅ Aligned — ready to select", style = MaterialTheme.typography.bodyMedium,
                            color = GibberGreen, fontWeight = FontWeight.Bold)
                        Button(onClick = vm::selectPointedDevice, modifier = Modifier.fillMaxWidth()) {
                            Text("Select Device (SmartHome stub)")
                        }
                    } else {
                        Text("↻ Pan phone toward target device", style = MaterialTheme.typography.bodySmall, color = alignColor)
                    }
                }
            }
        }

        state.selectedDevice?.let { dev ->
            Card(colors = CardDefaults.cardColors(containerColor = GibberBlue.copy(alpha = 0.12f)), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("✅ Selected: ${dev.address}", style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Bold, color = GibberBlue)
                    Text("SmartThings webhook stub — action would fire here.",
                        style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
                }
            }
        }
    }
}
