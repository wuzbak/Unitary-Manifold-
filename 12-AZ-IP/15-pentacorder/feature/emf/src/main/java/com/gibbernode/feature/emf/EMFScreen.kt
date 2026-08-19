package com.gibbernode.feature.emf

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
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.gibbernode.emf.EMFAdvisor
import com.gibbernode.ui.GibberAmber
import com.gibbernode.ui.GibberBlue
import com.gibbernode.ui.GibberGreen
import com.gibbernode.ui.GibberRed
import com.gibbernode.ui.OnSurfaceDim
import com.gibbernode.ui.SurfaceDark

/**
 * EMFScreen — 🧲 EMF & Structural Lab
 *
 * Sub-tabs:
 *  0 — 🔍 Stud Finder : live |B| sparkline + material classification
 *  1 — 🌙 Sleep Check  : 30-second scan + sleep zone EMF score
 *  2 — ⚡ Dirty Electricity : variance chart + dirty index + frequency band
 */
@Composable
fun EMFScreen(viewModel: EMFViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    var tab   by remember { mutableIntStateOf(0) }

    Column(modifier = Modifier.fillMaxSize()) {
        ScrollableTabRow(selectedTabIndex = tab, edgePadding = 0.dp) {
            Tab(selected = tab == 0, onClick = { tab = 0 }, text = { Text("🔍 Stud Finder", fontSize = 13.sp) })
            Tab(selected = tab == 1, onClick = { tab = 1 }, text = { Text("🌙 Sleep Check", fontSize = 13.sp) })
            Tab(selected = tab == 2, onClick = { tab = 2 }, text = { Text("⚡ Dirty Elec.", fontSize = 13.sp) })
            Tab(selected = tab == 3, onClick = { tab = 3 }, text = { Text("🧭 Orientation", fontSize = 13.sp) })
        }
        when (tab) {
            0 -> StudFinderTab(state, viewModel)
            1 -> SleepCheckTab(state, viewModel)
            2 -> DirtyElecTab(state, viewModel)
            3 -> OrientationTab(state)
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 0 — Stud Finder
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun StudFinderTab(state: EMFUiState, vm: EMFViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text("Drag phone slowly across wall surface. Lock baseline first.",
            style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)

        // Current reading
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                    Column {
                        Text("Field Magnitude", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                        Text("%.2f µT".format(state.magMag), style = MaterialTheme.typography.headlineMedium,
                            fontWeight = FontWeight.Bold, color = GibberAmber)
                        Text("Baseline: %.2f µT".format(state.baselineUt), style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                    }
                    // EMF zone badge
                    val zoneColor = when (state.emfZone) {
                        EMFAdvisor.EmfZone.LOW      -> GibberGreen
                        EMFAdvisor.EmfZone.MODERATE -> GibberAmber
                        EMFAdvisor.EmfZone.HIGH     -> Color(0xFFFF6D00)
                        EMFAdvisor.EmfZone.ALERT    -> GibberRed
                    }
                    Surface(shape = MaterialTheme.shapes.medium, color = zoneColor.copy(alpha = 0.15f)) {
                        Text(
                            "${state.emfZone.emoji} ${state.emfZone.label}",
                            style = MaterialTheme.typography.labelMedium, color = zoneColor,
                            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                        )
                    }
                }
                Spacer(Modifier.height(8.dp))
                state.studReading?.let { r ->
                    Text("${r.material.emoji} ${r.material.label}", style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Bold, color = if (r.material == EMFAdvisor.StudMaterial.LIVE_WIRE) GibberRed else MaterialTheme.colorScheme.onSurface)
                    Text("Δ %.2f µT  conf %.0f%%".format(r.deltaUt, r.confidence * 100f),
                        style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                }
                if (state.isOscillating) {
                    Spacer(Modifier.height(4.dp))
                    Text("⚠️ AC oscillation detected — possible live wire", style = MaterialTheme.typography.labelSmall, color = GibberRed)
                }
            }
        }

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = vm::lockBaseline, enabled = !state.baselineLocked, modifier = Modifier.weight(1f)) {
                Text(if (state.baselineLocked) "✅ Baseline Locked" else "🔒 Lock Baseline")
            }
            OutlinedButton(onClick = vm::resetBaseline, modifier = Modifier.weight(1f)) {
                Text("↺ Reset")
            }
        }

        // Sparkline
        MagSparkline(history = state.magHistory, baseline = state.baselineUt)
    }
}

@Composable
private fun MagSparkline(history: List<Float>, baseline: Float) {
    Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("|B| History (last 120 samples)", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
            Spacer(Modifier.height(8.dp))
            Canvas(modifier = Modifier.fillMaxWidth().height(80.dp)) {
                val w = size.width; val h = size.height
                if (history.size < 2) return@Canvas
                val minV = history.min(); val maxV = history.max()
                val range = (maxV - minV).coerceAtLeast(0.1f)
                val step  = w / (history.size - 1)
                // Baseline reference line
                val baseY = h * (1f - (baseline - minV) / range)
                drawLine(color = Color(0xFF4CAF50).copy(alpha = 0.5f), start = Offset(0f, baseY), end = Offset(w, baseY), strokeWidth = 1f)
                for (i in 1 until history.size) {
                    val x0 = (i - 1) * step; val x1 = i * step
                    val y0 = h * (1f - (history[i - 1] - minV) / range)
                    val y1 = h * (1f - (history[i] - minV) / range)
                    drawLine(color = Color(0xFFFFAB00), start = Offset(x0, y0), end = Offset(x1, y1), strokeWidth = 2f)
                }
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 1 — Sleep Check
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun SleepCheckTab(state: EMFUiState, vm: EMFViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text("Place phone on your bed / mattress and run a 30-second scan.",
            style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)

        Button(
            onClick = vm::startSleepScan,
            enabled = !state.sleepScanRunning,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(if (state.sleepScanRunning) "⏳ Scanning…" else "🌙 Start 30s Sleep Scan")
        }

        if (state.sleepScanRunning) {
            LinearProgressIndicator(modifier = Modifier.fillMaxWidth())
        }

        state.sleepScore?.let { score ->
            val zoneColor = when (score.zone) {
                EMFAdvisor.EmfZone.LOW      -> GibberGreen
                EMFAdvisor.EmfZone.MODERATE -> GibberAmber
                EMFAdvisor.EmfZone.HIGH     -> Color(0xFFFF6D00)
                EMFAdvisor.EmfZone.ALERT    -> GibberRed
            }
            Card(colors = CardDefaults.cardColors(containerColor = zoneColor.copy(alpha = 0.08f)), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("${score.zone.emoji} ${score.zone.label}", style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold, color = zoneColor)
                    Spacer(Modifier.height(8.dp))
                    Text(score.advice, style = MaterialTheme.typography.bodySmall)
                    Spacer(Modifier.height(8.dp))
                    SleepRow("Peak Δ",     "%.2f µT".format(score.maxDeltaUt))
                    SleepRow("Avg Δ",      "%.2f µT".format(score.avgDeltaUt))
                    SleepRow("Worst Axis", score.worstAxisLabel)
                }
            }
        }
    }
}

@Composable
private fun SleepRow(label: String, value: String) {
    Row(modifier = Modifier.fillMaxWidth().padding(vertical = 2.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(label, style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim, modifier = Modifier.weight(1f))
        Text(value, style = MaterialTheme.typography.bodySmall, fontFamily = FontFamily.Monospace)
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 2 — Dirty Electricity
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun DirtyElecTab(state: EMFUiState, vm: EMFViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text("Detects power-line harmonic interference in the magnetic field.",
            style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)

        Button(onClick = vm::computeDirtyElectricity, modifier = Modifier.fillMaxWidth()) {
            Text("⚡ Analyse Current Window")
        }

        state.dirtyElectricity?.let { r ->
            val idxColor = when {
                r.dirtyIndex < 2f  -> GibberGreen
                r.dirtyIndex < 5f  -> GibberAmber
                else               -> GibberRed
            }
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Dirty Electricity Index", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(8.dp))
                    Text("%.1f / 10".format(r.dirtyIndex), style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold, color = idxColor)
                    LinearProgressIndicator(progress = { r.dirtyIndex / 10f }, modifier = Modifier.fillMaxWidth(), color = idxColor)
                    Spacer(Modifier.height(8.dp))
                    SleepRow("Dominant Band", r.dominantFreqBand)
                    SleepRow("Field Variance", "%.4f µT²".format(r.varianceUt2))
                }
            }
        }

        // Live |B| sparkline
        MagSparkline(history = state.magHistory, baseline = state.baselineUt)
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 3 — Orientation / Compass
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun OrientationTab(state: EMFUiState) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        val azimuth = state.azimuthDeg
        val compassLabel = when {
            azimuth < 22.5f  || azimuth >= 337.5f -> "N"
            azimuth < 67.5f  -> "NE"
            azimuth < 112.5f -> "E"
            azimuth < 157.5f -> "SE"
            azimuth < 202.5f -> "S"
            azimuth < 247.5f -> "SW"
            azimuth < 292.5f -> "W"
            else             -> "NW"
        }

        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Text("🧭 Compass", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(12.dp))
                Canvas(modifier = Modifier.size(160.dp)) {
                    val cx = size.width / 2f; val cy = size.height / 2f
                    val r  = size.width * 0.42f
                    drawCircle(color = Color(0xFF263238), radius = r, center = Offset(cx, cy))
                    drawCircle(color = Color(0xFF455A64), radius = r, center = Offset(cx, cy),
                        style = androidx.compose.ui.graphics.drawscope.Stroke(width = 2f))
                    for (deg in 0 until 360 step 10) {
                        val rad    = Math.toRadians(deg.toDouble())
                        val isCard = deg % 90 == 0
                        val len    = if (isCard) r * 0.2f else r * 0.1f
                        val x0 = cx + (r - len) * kotlin.math.sin(rad).toFloat()
                        val y0 = cy - (r - len) * kotlin.math.cos(rad).toFloat()
                        val x1 = cx + r * kotlin.math.sin(rad).toFloat()
                        val y1 = cy - r * kotlin.math.cos(rad).toFloat()
                        drawLine(color = if (isCard) Color.White else Color(0xFF607D8B),
                            start = Offset(x0, y0), end = Offset(x1, y1), strokeWidth = if (isCard) 2f else 1f)
                    }
                    rotate(degrees = azimuth, pivot = Offset(cx, cy)) {
                        drawLine(color = GibberRed,   start = Offset(cx, cy), end = Offset(cx, cy - r * 0.65f), strokeWidth = 6f)
                        drawLine(color = Color.White, start = Offset(cx, cy), end = Offset(cx, cy + r * 0.45f), strokeWidth = 4f)
                    }
                    drawCircle(color = Color(0xFFECEFF1), radius = 6f, center = Offset(cx, cy))
                }
                Spacer(Modifier.height(8.dp))
                Text("%.1f°  $compassLabel".format(azimuth),
                    style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace)
            }
        }

        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Tilt", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                OrientRow("Pitch", "%.1f°".format(state.pitchDeg),
                    ((state.pitchDeg + 90f) / 180f).coerceIn(0f, 1f), GibberBlue)
                Spacer(Modifier.height(6.dp))
                OrientRow("Roll",  "%.1f°".format(state.rollDeg),
                    ((state.rollDeg + 180f) / 360f).coerceIn(0f, 1f), GibberAmber)
                Spacer(Modifier.height(8.dp))
                Text("Pitch: −90° = face-up, +90° = face-down. Roll: ±180° = left/right tilt.",
                    style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
            }
        }

        val levelOk = kotlin.math.abs(state.rollDeg) < 3f && kotlin.math.abs(state.pitchDeg) < 3f
        Card(colors = CardDefaults.cardColors(
            containerColor = if (levelOk) GibberGreen.copy(alpha = 0.1f) else SurfaceDark
        ), modifier = Modifier.fillMaxWidth()) {
            Row(modifier = Modifier.padding(16.dp).fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp), verticalAlignment = Alignment.CenterVertically) {
                Text(if (levelOk) "✅" else "↕️", fontSize = 28.sp)
                Column {
                    Text(if (levelOk) "Level" else "Not level",
                        style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold,
                        color = if (levelOk) GibberGreen else OnSurfaceDim)
                    Text("Within ±3° of horizontal", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                }
            }
        }
    }
}

@Composable
private fun OrientRow(label: String, value: String, progress: Float, color: Color) {
    Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(label, style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim, modifier = Modifier.width(40.dp))
        LinearProgressIndicator(progress = { progress }, modifier = Modifier.weight(1f), color = color)
        Text(value, style = MaterialTheme.typography.bodySmall, fontFamily = FontFamily.Monospace, modifier = Modifier.width(64.dp))
    }
}
