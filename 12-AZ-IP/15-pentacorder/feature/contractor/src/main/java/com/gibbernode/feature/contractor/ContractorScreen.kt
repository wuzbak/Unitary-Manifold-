package com.gibbernode.feature.contractor

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
import androidx.compose.ui.graphics.lerp
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.gibbernode.contractor.ContractorAdvisor
import com.gibbernode.emf.EMFAdvisor
import com.gibbernode.ui.GibberAmber
import com.gibbernode.ui.GibberBlue
import com.gibbernode.ui.GibberGreen
import com.gibbernode.ui.GibberRed
import com.gibbernode.ui.OnSurfaceDim
import com.gibbernode.ui.SurfaceDark

/**
 * ContractorScreen — 🏗️ Precision Contractor Suite
 *
 * Sub-tabs:
 *  0 — 🧱 Wall Scanner : stud-finder with EMF (magnetometer)
 *  1 — ⚖️ Level         : barometric precision level
 *  2 — 🔊 Tap Test     : acoustic impedance material classification
 *  3 — 📄 Doc Forensics: 200 MP camera guidance
 */
@Composable
fun ContractorScreen(viewModel: ContractorViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    var tab   by remember { mutableIntStateOf(0) }

    Column(modifier = Modifier.fillMaxSize()) {
        ScrollableTabRow(selectedTabIndex = tab, edgePadding = 0.dp) {
            Tab(selected = tab == 0, onClick = { tab = 0 }, text = { Text("🧱 Wall", fontSize = 13.sp) })
            Tab(selected = tab == 1, onClick = { tab = 1 }, text = { Text("⚖️ Level", fontSize = 13.sp) })
            Tab(selected = tab == 2, onClick = { tab = 2 }, text = { Text("🔊 Tap Test", fontSize = 13.sp) })
            Tab(selected = tab == 3, onClick = { tab = 3 }, text = { Text("📄 Doc Forensics", fontSize = 13.sp) })
        }
        when (tab) {
            0 -> WallScannerTab(state, viewModel)
            1 -> LevelTab(state, viewModel)
            2 -> TapTestTab(state, viewModel)
            3 -> DocForensicsTab(viewModel)
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 0 — Wall Scanner
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun WallScannerTab(state: ContractorUiState, vm: ContractorViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text("Hold phone flat against wall and slide horizontally. Lock baseline before scanning.",
            style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)

        // Live stud reading
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                    Column {
                        Text("|B| = %.2f µT".format(state.magMag), style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold, color = GibberAmber)
                        Text("Baseline: %.2f µT".format(state.magBaseline), style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                    }
                    state.studReading?.let { r ->
                        val c = if (r.material == EMFAdvisor.StudMaterial.LIVE_WIRE) GibberRed
                                else if (r.material != EMFAdvisor.StudMaterial.EMPTY) GibberAmber
                                else GibberGreen
                        Surface(shape = MaterialTheme.shapes.medium, color = c.copy(alpha = 0.15f)) {
                            Text("${r.material.emoji} ${r.material.label.take(20)}",
                                style = MaterialTheme.typography.labelMedium, color = c,
                                modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp))
                        }
                    }
                }
                Spacer(Modifier.height(8.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(onClick = vm::lockMagBaseline, enabled = !state.magLocked, modifier = Modifier.weight(1f)) {
                        Text(if (state.magLocked) "✅ Locked" else "🔒 Lock Baseline")
                    }
                }
            }
        }

        // Heatmap sparkline
        if (state.magHistory.isNotEmpty()) {
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Horizontal Scan (|B| history)", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                    Spacer(Modifier.height(8.dp))
                    Canvas(modifier = Modifier.fillMaxWidth().height(60.dp)) {
                        val w = size.width; val h = size.height
                        val hist = state.magHistory
                        if (hist.size < 2) return@Canvas
                        val minV = hist.min(); val maxV = hist.max()
                        val range = (maxV - minV).coerceAtLeast(0.1f)
                        hist.forEachIndexed { i, v ->
                            val frac = (v - minV) / range
                            val x = i * (w / hist.size)
                            drawLine(
                                color = lerp(Color(0xFF1565C0), Color(0xFFFF6D00), frac),
                                start = Offset(x, h), end = Offset(x, h * (1f - frac)), strokeWidth = w / hist.size,
                            )
                        }
                    }
                }
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 1 — Level
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun LevelTab(state: ContractorUiState, vm: ContractorViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text("Measure height difference between two points using barometric pressure.",
            style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
        Text("⚠️ Not a certified surveying instrument. For reference only.",
            style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)

        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Procedure", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                Text("1. Hold phone at Point A and tap 'Set Point A'.", style = MaterialTheme.typography.bodySmall)
                Text("2. Walk to Point B and tap 'Measure B'.", style = MaterialTheme.typography.bodySmall)
            }
        }

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = vm::setLevelModeSetA, modifier = Modifier.weight(1f)) {
                Text("📍 Set Point A")
            }
            Button(onClick = vm::setLevelModeMeasure, enabled = state.pressureAHpa > 0f, modifier = Modifier.weight(1f)) {
                Text("📐 Measure B")
            }
            OutlinedButton(onClick = vm::resetLevel, modifier = Modifier.weight(1f)) {
                Text("↺ Reset")
            }
        }

        // Status
        when (state.levelMode) {
            LevelMode.SETTING_A  -> StatusChip("Recording Point A…", GibberAmber)
            LevelMode.MEASURING  -> StatusChip("Recording Point B…", GibberBlue)
            LevelMode.IDLE       -> if (state.pressureAHpa > 0f) StatusChip("Point A set", GibberGreen)
        }

        state.levelResult?.let { r ->
            Card(colors = CardDefaults.cardColors(
                containerColor = if (r.isLevel) GibberGreen.copy(alpha = 0.1f) else GibberAmber.copy(alpha = 0.1f)
            ), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(if (r.isLevel) "✅ Level" else "↕ Height Difference",
                        style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold,
                        color = if (r.isLevel) GibberGreen else GibberAmber)
                    Spacer(Modifier.height(8.dp))
                    LevelRow("Height diff", "%.1f mm".format(r.heightDiffMm))
                    LevelRow("Pressure Δ", "%.4f hPa".format(r.deltaHpa))
                    Spacer(Modifier.height(4.dp))
                    Text(r.levelDirection, style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}

@Composable
private fun LevelRow(label: String, value: String) {
    Row(modifier = Modifier.fillMaxWidth().padding(vertical = 2.dp)) {
        Text(label, style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim, modifier = Modifier.weight(1f))
        Text(value, style = MaterialTheme.typography.bodySmall, fontFamily = FontFamily.Monospace)
    }
}

@Composable
private fun StatusChip(text: String, color: Color) {
    Surface(shape = MaterialTheme.shapes.small, color = color.copy(alpha = 0.15f)) {
        Text(text, style = MaterialTheme.typography.labelMedium, color = color,
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp))
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 2 — Tap Test
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun TapTestTab(state: ContractorUiState, vm: ContractorViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text("Tap the wall surface with the S Pen tip. The accelerometer captures the acoustic rebound.",
            style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)

        state.tapResult?.let { r ->
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("${r.material.emoji} ${r.material.label}", style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(8.dp))
                    LevelRow("Hardness",    "%.0f / 100".format(r.hardnessEstimate))
                    LevelRow("Decay λ",     "%.1f /s".format(r.decayConst))
                    LevelRow("Peak Accel",  "%.2f g".format(r.peakAccelG))
                    LevelRow("Confidence",  "%.0f%%".format(r.confidence * 100f))
                    Spacer(Modifier.height(8.dp))
                    LinearProgressIndicator(
                        progress = { r.hardnessEstimate / 100f },
                        modifier = Modifier.fillMaxWidth(),
                        color = GibberAmber,
                    )
                    Text("Hardness", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                }
            }
        } ?: Text("No tap detected yet. Tap the surface with the S Pen.", style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)

        // Waveform
        if (state.accelHistory.size > 4) {
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Accelerometer Waveform", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                    Spacer(Modifier.height(8.dp))
                    Canvas(modifier = Modifier.fillMaxWidth().height(80.dp)) {
                        val w = size.width; val h = size.height
                        val hist = state.accelHistory
                        val minV = hist.min(); val maxV = hist.max()
                        val range = (maxV - minV).coerceAtLeast(0.1f)
                        val step  = w / (hist.size - 1)
                        for (i in 1 until hist.size) {
                            val x0 = (i - 1) * step; val x1 = i * step
                            val y0 = h * (1f - (hist[i - 1] - minV) / range)
                            val y1 = h * (1f - (hist[i] - minV) / range)
                            drawLine(color = Color(0xFF81C784), start = Offset(x0, y0), end = Offset(x1, y1), strokeWidth = 2f)
                        }
                    }
                }
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 3 — Doc Forensics
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun DocForensicsTab(vm: ContractorViewModel) {
    var zoomLevel by remember { mutableFloatStateOf(1f) }
    val guidance  = remember(zoomLevel) { vm.docForensicsGuidance(zoomLevel) }

    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text("200 MP camera macro mode for document forensics and micro-print analysis.",
            style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)

        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Zoom Level", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                Text("${zoomLevel.toInt()}×", style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold, color = GibberBlue)
                Slider(
                    value = zoomLevel,
                    onValueChange = { zoomLevel = it },
                    valueRange = 1f..5f,
                    steps = 3,
                    modifier = Modifier.fillMaxWidth(),
                )
                Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                    Text("1× Wide", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                    Text("3× Standard", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                    Text("5× Periscope", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                }
                Spacer(Modifier.height(12.dp))
                Text(guidance, style = MaterialTheme.typography.bodySmall, color = GibberGreen)
            }
        }

        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Tips", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                listOf(
                    "📸 Capture RAW DNG for maximum detail and post-processing latitude",
                    "💡 Use a consistent side-light source to reveal fibre texture",
                    "🔍 5× periscope is optimal for serial numbers, micro-print, watermarks",
                    "📐 Hold phone parallel to document surface; use volume button shutter",
                    "🗂️ Save to high-res PDF using Files → Share → Print → Save as PDF",
                ).forEach { tip ->
                    Text(tip, style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(vertical = 2.dp))
                }
            }
        }
    }
}
