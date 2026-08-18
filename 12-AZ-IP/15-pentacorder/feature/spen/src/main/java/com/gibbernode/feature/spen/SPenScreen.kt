package com.gibbernode.feature.spen

import android.view.MotionEvent
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.ExperimentalComposeUiApi
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import kotlin.math.toDegrees
import androidx.compose.ui.input.pointer.pointerInteropFilter
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.gibbernode.spen.SPenAdvisor
import com.gibbernode.ui.GibberAmber
import com.gibbernode.ui.GibberBlue
import com.gibbernode.ui.GibberGreen
import com.gibbernode.ui.GibberRed
import com.gibbernode.ui.OnSurfaceDim
import com.gibbernode.ui.SurfaceDark

/**
 * SPenScreen — 🖊️ S Pen Command Center
 *
 * Three sub-tabs:
 *  0 — ✋ Gestures  : live Air Action log, gesture→command mapper
 *  1 — 📝 Stroke Lab: pressure waveform + tremor score
 *  2 — 🎯 Air Control: 3D gyro orientation + air-writing unlock
 */
@Composable
fun SPenScreen(viewModel: SPenViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    var tab   by remember { mutableIntStateOf(0) }

    Column(modifier = Modifier.fillMaxSize()) {
        ScrollableTabRow(selectedTabIndex = tab, edgePadding = 0.dp) {
            Tab(selected = tab == 0, onClick = { tab = 0 }, text = { Text("✋ Gestures", fontSize = 13.sp) })
            Tab(selected = tab == 1, onClick = { tab = 1 }, text = { Text("📝 Stroke Lab", fontSize = 13.sp) })
            Tab(selected = tab == 2, onClick = { tab = 2 }, text = { Text("🎯 Air Control", fontSize = 13.sp) })
        }
        when (tab) {
            0 -> GesturesTab(state, viewModel)
            1 -> StrokeLabTab(state, viewModel)
            2 -> AirControlTab(state, viewModel)
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 0 — Gestures
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun GesturesTab(state: SPenUiState, vm: SPenViewModel) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        // Last detected gesture + command
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Last Air Action", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                state.lastGesture?.let { g ->
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Chip(g.label, GibberBlue)
                        state.lastCommand?.let { c -> Chip("${c.emoji} ${c.label}", GibberGreen) }
                    }
                } ?: Text("No gesture detected yet", style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
                Spacer(Modifier.height(8.dp))
                Button(onClick = vm::classifyCurrentGesture, modifier = Modifier.fillMaxWidth()) {
                    Text("🔍 Classify Current Gyro Sample")
                }
            }
        }

        // Gesture bindings editor
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("Gesture Bindings", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                    TextButton(onClick = vm::resetBindings) { Text("Reset", fontSize = 12.sp) }
                }
                Spacer(Modifier.height(8.dp))
                state.bindings.entries.forEach { (gesture, command) ->
                    BindingRow(gesture, command)
                }
            }
        }

        // Gesture log
        if (state.gestureLog.isNotEmpty()) {
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Recent Gestures", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(8.dp))
                    state.gestureLog.reversed().take(8).forEach { entry ->
                        Text(entry, style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim,
                            fontFamily = FontFamily.Monospace)
                    }
                }
            }
        }
    }
}

@Composable
private fun BindingRow(gesture: SPenAdvisor.GesturePattern, command: SPenAdvisor.AirCommand) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 3.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(gesture.label, style = MaterialTheme.typography.bodySmall, color = GibberBlue, modifier = Modifier.weight(1f))
        Text("→", style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim, modifier = Modifier.padding(horizontal = 8.dp))
        Text("${command.emoji} ${command.label}", style = MaterialTheme.typography.bodySmall, color = GibberGreen)
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 1 — Stroke Lab
// ─────────────────────────────────────────────────────────────────────────────

@OptIn(ExperimentalComposeUiApi::class)
@Composable
private fun StrokeLabTab(state: SPenUiState, vm: SPenViewModel) {
    // Collect stroke points rendered so far for the canvas overlay
    val strokePoints = remember { mutableStateListOf<Offset>() }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(
            "📝 Draw with the S Pen to record a stroke analysis.",
            style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim,
        )

        // ── S Pen drawing canvas ──────────────────────────────────────────────
        //
        // Uses pointerInteropFilter to receive raw MotionEvent from the Android
        // view hierarchy, extracting S Pen-specific axes that the Compose pointer
        // API does not yet expose:
        //   AXIS_PRESSURE  — pen tip force (0–1, normalised from 4096 raw levels)
        //   AXIS_TILT      — pen angle from vertical (0–90°)
        //
        // On devices without an S Pen the standard touch pressure is used instead.
        Card(
            colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Canvas(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(200.dp)
                    .pointerInteropFilter { event ->
                        val x        = event.x
                        val y        = event.y
                        // AXIS_PRESSURE (2) = S Pen tip pressure; fallback to touch pressure
                        val pressure = event.getAxisValue(MotionEvent.AXIS_PRESSURE)
                            .takeIf { it > 0f } ?: event.pressure
                        // AXIS_TILT (25) = pen angle from vertical in degrees
                        val tiltDeg  = event.getAxisValue(MotionEvent.AXIS_TILT)
                            .toDouble().toDegrees().toFloat()

                        when (event.action) {
                            MotionEvent.ACTION_DOWN -> {
                                strokePoints.clear()
                                strokePoints += Offset(x, y)
                                vm.addStrokePoint(x, y, pressure, tiltDeg)
                                true
                            }
                            MotionEvent.ACTION_MOVE -> {
                                // Batch historical points for smooth capture at high sample rate
                                for (i in 0 until event.historySize) {
                                    val hx = event.getHistoricalX(i)
                                    val hy = event.getHistoricalY(i)
                                    val hp = event.getHistoricalPressure(i)
                                    val ht = event.getHistoricalAxisValue(MotionEvent.AXIS_TILT, i)
                                        .toDouble().toDegrees().toFloat()
                                    strokePoints += Offset(hx, hy)
                                    vm.addStrokePoint(hx, hy, hp, ht)
                                }
                                strokePoints += Offset(x, y)
                                vm.addStrokePoint(x, y, pressure, tiltDeg)
                                true
                            }
                            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                                vm.finaliseStroke()
                                true
                            }
                            else -> false
                        }
                    },
            ) {
                // Render stroke path
                for (i in 1 until strokePoints.size) {
                    drawLine(
                        color       = Color(0xFF64B5F6),
                        start       = strokePoints[i - 1],
                        end         = strokePoints[i],
                        strokeWidth = 3f,
                    )
                }
                // Hint text drawn when canvas is empty
                if (strokePoints.isEmpty()) {
                    drawCircle(
                        color  = Color(0x22FFFFFF),
                        radius = size.minDimension / 4f,
                        center = center,
                    )
                }
            }
        }

        // Tremor score gauge
        state.tremorHistory.lastOrNull()?.let { reading ->
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Tremor Score", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(8.dp))

                    val scoreColor = when {
                        reading.tremorScore < 2f  -> GibberGreen
                        reading.tremorScore < 5f  -> GibberAmber
                        else                      -> GibberRed
                    }
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                        Text(
                            "%.1f / 10".format(reading.tremorScore),
                            style = MaterialTheme.typography.headlineMedium,
                            fontWeight = FontWeight.Bold,
                            color = scoreColor,
                        )
                        Column {
                            Text(reading.severity.label, style = MaterialTheme.typography.bodySmall, color = scoreColor, fontWeight = FontWeight.Bold)
                            if (reading.dominantFreqHz > 0f)
                                Text("%.1f Hz".format(reading.dominantFreqHz), style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        }
                    }
                    Spacer(Modifier.height(8.dp))
                    LinearProgressIndicator(
                        progress = { reading.tremorScore / 10f },
                        modifier = Modifier.fillMaxWidth(),
                        color = scoreColor,
                    )
                    Spacer(Modifier.height(8.dp))
                    Text(reading.disclaimer, style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                }
            }
        }

        // Stroke analysis details
        state.lastStrokeAnalysis?.let { a ->
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Last Stroke", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(8.dp))
                    MetricRow("Avg Pressure",  "%.3f".format(a.avgPressure),  "normalised")
                    MetricRow("Peak Pressure", "%.3f".format(a.peakPressure), "normalised")
                    MetricRow("Velocity Mean", "%.3f px/ms".format(a.velocityMean), "")
                    MetricRow("Velocity SD",   "%.3f px/ms".format(a.velocitySd),  "")
                    MetricRow("φ_human",       "%.3f".format(state.phiHuman), "intent layer input")
                    MetricRow("Samples",       "${a.sampleCount}", "points")
                }
            }
        }

        // Tremor history trend
        if (state.tremorHistory.size >= 2) {
            TremorHistoryChart(state.tremorHistory.map { it.tremorScore })
        }
    }
}

@Composable
private fun TremorHistoryChart(scores: List<Float>) {
    Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Session Trend", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(8.dp))
            Canvas(modifier = Modifier.fillMaxWidth().height(80.dp)) {
                val w = size.width; val h = size.height
                val step = if (scores.size > 1) w / (scores.size - 1) else w
                for (i in 1 until scores.size) {
                    val x0 = (i - 1) * step; val x1 = i * step
                    val y0 = h * (1f - scores[i - 1] / 10f)
                    val y1 = h * (1f - scores[i] / 10f)
                    drawLine(color = Color(0xFF64B5F6), start = Offset(x0, y0), end = Offset(x1, y1), strokeWidth = 2f)
                }
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 2 — Air Control
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun AirControlTab(state: SPenUiState, vm: SPenViewModel) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        // Live IMU orientation
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("3D Gyroscope  (S Pen IMU proxy)", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                MetricRow("ωX (Roll)",  "%.4f rad/s".format(state.gyroX), "")
                MetricRow("ωY (Pitch)", "%.4f rad/s".format(state.gyroY), "")
                MetricRow("ωZ (Yaw)",  "%.4f rad/s".format(state.gyroZ), "")
                MetricRow("|ω|", "%.4f rad/s".format(state.gyroMag), "")
            }
        }

        // Air write
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("🎯 Air-Writing Unlock", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                Text(
                    "Record a 3D air-gesture as your personal signature. " +
                    "Same gesture → same hash → can be used as an unlock credential.",
                    style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim,
                )
                Spacer(Modifier.height(8.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    if (!state.airWriteActive) {
                        Button(onClick = vm::startAirWrite, modifier = Modifier.weight(1f)) {
                            Text("▶ Start Recording")
                        }
                    } else {
                        Button(
                            onClick = vm::finishAirWrite,
                            colors  = ButtonDefaults.buttonColors(containerColor = GibberRed),
                            modifier = Modifier.weight(1f),
                        ) {
                            Text("⏹ Finish & Hash")
                        }
                    }
                }
                state.lastAirSignature?.let { sig ->
                    Spacer(Modifier.height(8.dp))
                    Text("Signature:", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                    Text(sig.hash, style = MaterialTheme.typography.bodyMedium,
                        fontFamily = FontFamily.Monospace, color = GibberAmber, fontWeight = FontWeight.Bold)
                    Text("Confidence: %.0f%%".format(sig.confidence * 100f),
                        style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                }
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Shared helpers
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun Chip(text: String, color: Color) {
    Surface(
        shape = MaterialTheme.shapes.small,
        color = color.copy(alpha = 0.15f),
        modifier = Modifier.padding(end = 4.dp),
    ) {
        Text(text, style = MaterialTheme.typography.labelMedium, color = color,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp))
    }
}

@Composable
private fun MetricRow(label: String, value: String, note: String) {
    Row(modifier = Modifier.fillMaxWidth().padding(vertical = 2.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(label, style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim, modifier = Modifier.weight(1.2f))
        Text(value, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurface,
            fontFamily = FontFamily.Monospace, modifier = Modifier.weight(1.5f))
        if (note.isNotEmpty())
            Text(note, style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim, modifier = Modifier.weight(1f))
    }
}
