package com.gibbernode.feature.science

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
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.gibbernode.ui.GibberAmber
import com.gibbernode.ui.GibberBlue
import com.gibbernode.ui.GibberGreen
import com.gibbernode.ui.GibberRed
import com.gibbernode.ui.OnSurfaceDim
import com.gibbernode.ui.SurfaceDark

/**
 * ScienceScreen — 🔭 Citizen Science Hub
 *
 * Sub-tabs:
 *  0 — ☄️ Radiation   : camera dark-frame cosmic-ray detector
 *  1 — 🌍 Crowd Pressure : crowdsourced barometric mesh + tornado alert
 *  2 — 🧲 Magneto-Nav  : haptic "warmer/colder" magnetic waypoint nav
 */
@Composable
fun ScienceScreen(viewModel: ScienceViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    var tab   by remember { mutableIntStateOf(0) }

    Column(modifier = Modifier.fillMaxSize()) {
        ScrollableTabRow(selectedTabIndex = tab, edgePadding = 0.dp) {
            Tab(selected = tab == 0, onClick = { tab = 0 }, text = { Text("☄️ Radiation", fontSize = 13.sp) })
            Tab(selected = tab == 1, onClick = { tab = 1 }, text = { Text("🌍 Crowd Pressure", fontSize = 13.sp) })
            Tab(selected = tab == 2, onClick = { tab = 2 }, text = { Text("🧲 Magneto-Nav", fontSize = 13.sp) })
            Tab(selected = tab == 3, onClick = { tab = 3 }, text = { Text("⚡ G-Force", fontSize = 13.sp) })
            Tab(selected = tab == 4, onClick = { tab = 4 }, text = { Text("🔬 Oscillation", fontSize = 13.sp) })
        }
        when (tab) {
            0 -> RadiationTab(state, viewModel)
            1 -> CrowdPressureTab(state, viewModel)
            2 -> MagnetoNavTab(state, viewModel)
            3 -> GForceTab(state, viewModel)
            4 -> OscillationTab(state, viewModel)
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 0 — Radiation
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun RadiationTab(state: ScienceUiState, vm: ScienceViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("☄️ Cosmic Ray Detector", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                Text(
                    "Cover the camera lens completely with opaque tape before starting. " +
                    "Cosmic muons and background radiation occasionally ionise camera pixels, " +
                    "creating hot-pixel streaks detectable in long-exposure dark frames.",
                    style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim,
                )
                Spacer(Modifier.height(8.dp))
                Text(
                    "⚠️ Educational / citizen-science only. Cannot measure radiation dose. " +
                    "Not a certified dosimeter. See DisclaimerRegistry.FEATURE_COSMIC_RAY.",
                    style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim,
                )
            }
        }

        // Stats
        if (state.radiationCapturing || state.radiationEvents > 0) {
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Column {
                            Text("Events Detected", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                            Text("${state.radiationEvents}", style = MaterialTheme.typography.headlineMedium,
                                fontWeight = FontWeight.Bold, color = GibberBlue)
                            Text("Session: ${state.radiationSessionSec / 60} min",
                                style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        }
                        val rate = if (state.radiationSessionSec > 0)
                            state.radiationEvents.toFloat() / (state.radiationSessionSec / 60f) else 0f
                        Column(horizontalAlignment = Alignment.End) {
                            Text("Rate", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                            Text("%.1f / min".format(rate), style = MaterialTheme.typography.headlineSmall,
                                fontWeight = FontWeight.Bold, color = GibberAmber)
                            Text("Background: 1–4/min at sea level",
                                style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        }
                    }
                    if (state.radiationCapturing) {
                        Spacer(Modifier.height(8.dp))
                        LinearProgressIndicator(modifier = Modifier.fillMaxWidth())
                    }
                }
            }
        }

        Button(
            onClick = if (!state.radiationCapturing) vm::startRadiationCapture else vm::stopRadiationCapture,
            modifier = Modifier.fillMaxWidth(),
            colors = if (state.radiationCapturing) ButtonDefaults.buttonColors(containerColor = GibberRed)
                     else ButtonDefaults.buttonColors(),
        ) {
            Text(if (state.radiationCapturing) "⏹ Stop Capture" else "▶ Start Capture")
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 1 — Crowd Pressure
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun CrowdPressureTab(state: ScienceUiState, vm: ScienceViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        if (state.tornadoAlert) {
            Card(colors = CardDefaults.cardColors(containerColor = GibberRed.copy(alpha = 0.15f)), modifier = Modifier.fillMaxWidth()) {
                Text(
                    "⚠️ TORNADO INFLOW ALERT\nPressure dropped > 4 hPa in 10 minutes. Seek shelter immediately.",
                    style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold,
                    color = GibberRed, modifier = Modifier.padding(16.dp),
                )
            }
        }

        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Local Pressure", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Text("%.1f hPa".format(state.pressureHpa), style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold, color = GibberBlue)
            }
        }

        if (state.pressureHistory.size >= 2) {
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Pressure History", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                    Spacer(Modifier.height(8.dp))
                    Canvas(modifier = Modifier.fillMaxWidth().height(80.dp)) {
                        val w = size.width; val h = size.height
                        val values = state.pressureHistory.map { it.second }
                        val minV = values.min(); val maxV = values.max()
                        val range = (maxV - minV).coerceAtLeast(0.1f)
                        val step  = w / (values.size - 1)
                        for (i in 1 until values.size) {
                            val x0 = (i - 1) * step; val x1 = i * step
                            val y0 = h * (1f - (values[i - 1] - minV) / range)
                            val y1 = h * (1f - (values[i] - minV) / range)
                            drawLine(color = Color(0xFF64B5F6), start = Offset(x0, y0), end = Offset(x1, y1), strokeWidth = 2f)
                        }
                    }
                }
            }
        }

        OutlinedButton(
            onClick  = { /* Export to clipboard — handled in Composable launch scope */
                       vm.exportPressureCsv() },
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text("📤 Export CSV")
        }

        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Crowd Mesh (Coming Soon)", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Text("Participates in crowdsourced barometric mesh. Local readings will be " +
                    "logged to SQLite and optionally uploaded to a community endpoint. " +
                    "Upload endpoint not yet active.", style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 2 — Magneto-Nav
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun MagnetoNavTab(state: ScienceUiState, vm: ScienceViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text("Train a magnetic waypoint at a known location, then navigate back using the field fingerprint.",
            style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)

        // Current mag
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Current |B|", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Text("%.2f µT".format(state.magMag), style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold, color = GibberAmber)
                state.magnetoNavWaypointMag?.let { wm ->
                    Text("Waypoint: %.2f µT  Δ = %.2f µT".format(wm, kotlin.math.abs(state.magMag - wm)),
                        style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                }
            }
        }

        // Navigation hint
        state.magnetoNavHint?.let { hint ->
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                Text(hint, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(16.dp))
            }
        }

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = vm::saveWaypoint, modifier = Modifier.weight(1f)) {
                Text("📍 Save Waypoint Here")
            }
            OutlinedButton(onClick = vm::clearWaypoint, enabled = state.magnetoNavWaypointMag != null,
                modifier = Modifier.weight(1f)) {
                Text("↺ Clear")
            }
        }

        if (state.magnetoNavWaypointMag == null) {
            Text("No waypoint saved. Move to your target location and tap 'Save Waypoint Here'.",
                style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 3 — G-Force
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun GForceTab(state: ScienceUiState, vm: ScienceViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        // Free-fall alert
        if (state.freeFallDetected) {
            Card(colors = CardDefaults.cardColors(containerColor = GibberAmber.copy(alpha = 0.15f)), modifier = Modifier.fillMaxWidth()) {
                Text("🪂 FREE FALL DETECTED  (|g| < 0.1 g)",
                    style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold,
                    color = GibberAmber, modifier = Modifier.padding(16.dp))
            }
        }

        // Large g readout
        val gColor = when {
            state.gForce < 1.1f -> GibberGreen
            state.gForce < 2f   -> GibberBlue
            state.gForce < 4f   -> GibberAmber
            state.gForce < 8f   -> Color(0xFFFF6D00)
            else                -> GibberRed
        }
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Text("%.3f g".format(state.gForce),
                    style = MaterialTheme.typography.displayMedium, fontWeight = FontWeight.Bold,
                    color = gColor, fontFamily = FontFamily.Monospace)
                Spacer(Modifier.height(4.dp))
                LinearProgressIndicator(
                    progress = { (state.gForce / 10f).coerceIn(0f, 1f) },
                    modifier = Modifier.fillMaxWidth(),
                    color    = gColor,
                )
                Spacer(Modifier.height(8.dp))
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceAround) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("X", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        Text("%.2f".format(state.gX / 9.806f), style = MaterialTheme.typography.bodyMedium, fontFamily = FontFamily.Monospace)
                    }
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("Y", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        Text("%.2f".format(state.gY / 9.806f), style = MaterialTheme.typography.bodyMedium, fontFamily = FontFamily.Monospace)
                    }
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("Z", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        Text("%.2f".format(state.gZ / 9.806f), style = MaterialTheme.typography.bodyMedium, fontFamily = FontFamily.Monospace)
                    }
                }
            }
        }

        // Peak capture
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Row(modifier = Modifier.padding(16.dp).fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Column {
                    Text("Peak G", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                    Text("%.3f g".format(state.gPeakG), style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold, color = GibberRed, fontFamily = FontFamily.Monospace)
                }
                OutlinedButton(onClick = vm::resetGPeak) { Text("↺ Reset") }
            }
        }

        // Waveform
        if (state.accelWaveformG.size >= 2) {
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Acceleration history (last ${state.accelWaveformG.size} samples)",
                        style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                    Spacer(Modifier.height(8.dp))
                    Canvas(modifier = Modifier.fillMaxWidth().height(80.dp)) {
                        val w = size.width; val h = size.height
                        val vals = state.accelWaveformG
                        val minV = vals.min().coerceAtLeast(0f)
                        val maxV = vals.max().coerceAtLeast(minV + 0.1f)
                        val range = maxV - minV
                        val step  = w / (vals.size - 1)
                        for (i in 1 until vals.size) {
                            val x0 = (i - 1) * step; val x1 = i * step
                            val y0 = h * (1f - (vals[i - 1] - minV) / range)
                            val y1 = h * (1f - (vals[i]     - minV) / range)
                            drawLine(color = Color(0xFF4CAF50), start = Offset(x0, y0), end = Offset(x1, y1), strokeWidth = 2f)
                        }
                    }
                }
            }
        }

        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Reference values", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(4.dp))
                listOf("0.0 g" to "Free fall", "1.0 g" to "Resting (Earth gravity)", "2–3 g" to "Hard braking / sprint start",
                    "4–6 g" to "Roller coaster peak", "9+ g" to "Fighter jet manoeuvre").forEach { (g, d) ->
                    Row(modifier = Modifier.fillMaxWidth().padding(vertical = 1.dp)) {
                        Text(g, style = MaterialTheme.typography.labelSmall, fontFamily = FontFamily.Monospace, modifier = Modifier.width(52.dp))
                        Text(d, style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                    }
                }
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 4 — Oscillation Experiment
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun OscillationTab(state: ScienceUiState, vm: ScienceViewModel) {
    val clipboard = LocalClipboardManager.current
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("🔬 Pendulum / Oscillation Experiment", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                Text(
                    "Attach the phone to a swinging pendulum or oscillating platform. " +
                    "Arm the experiment, let it swing for a few periods, then read the " +
                    "frequency. Zero-crossing detection on the net acceleration magnitude.",
                    style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim,
                )
            }
        }

        // Arm/disarm
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            if (!state.oscillationArmed) {
                Button(onClick = vm::armOscillation, modifier = Modifier.weight(1f)) { Text("▶ Arm Experiment") }
            } else {
                Button(onClick = vm::disarmOscillation,
                    colors = ButtonDefaults.buttonColors(containerColor = GibberRed),
                    modifier = Modifier.weight(1f)) { Text("⏹ Disarm") }
            }
        }

        // Results
        if (state.oscillationArmed || state.oscillationHz != null) {
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    if (state.oscillationHz != null) {
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Column {
                                Text("Frequency", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                                Text("%.3f Hz".format(state.oscillationHz),
                                    style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold,
                                    color = GibberBlue, fontFamily = FontFamily.Monospace)
                            }
                            Column(horizontalAlignment = Alignment.End) {
                                Text("Period", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                                Text("%.1f ms".format(state.oscillationPeriodMs ?: 0f),
                                    style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold,
                                    color = GibberAmber, fontFamily = FontFamily.Monospace)
                            }
                        }
                        Spacer(Modifier.height(8.dp))
                        Text("Zero-crossings detected: ${state.oscillationPeakCount}",
                            style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        // Derived pendulum length L = g / (2π f)²
                        state.oscillationHz?.takeIf { it > 0.01f }?.let { f ->
                            val lengthM = 9.806f / (4f * Math.PI.toFloat() * Math.PI.toFloat() * f * f)
                            Spacer(Modifier.height(4.dp))
                            Text("Pendulum length estimate: %.2f m  (if simple pendulum)".format(lengthM),
                                style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        }
                    } else {
                        if (state.oscillationArmed) {
                            Text("⏳ Waiting for oscillation…", style = MaterialTheme.typography.bodyMedium)
                            LinearProgressIndicator(modifier = Modifier.fillMaxWidth().padding(top = 8.dp))
                        }
                    }
                }
            }
        }

        // Acceleration waveform
        if (state.accelWaveformG.size >= 2) {
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Acceleration waveform", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                    Spacer(Modifier.height(8.dp))
                    Canvas(modifier = Modifier.fillMaxWidth().height(100.dp)) {
                        val w = size.width; val h = size.height
                        val vals = state.accelWaveformG
                        val meanV = vals.average().toFloat()
                        val minV  = vals.min(); val maxV = vals.max()
                        val range = (maxV - minV).coerceAtLeast(0.05f)
                        val step  = w / (vals.size - 1)
                        // Mean line
                        val meanY = h * (1f - (meanV - minV) / range)
                        drawLine(color = Color.Gray.copy(alpha = 0.4f), start = Offset(0f, meanY), end = Offset(w, meanY), strokeWidth = 1f)
                        for (i in 1 until vals.size) {
                            val x0 = (i - 1) * step; val x1 = i * step
                            val y0 = h * (1f - (vals[i - 1] - minV) / range)
                            val y1 = h * (1f - (vals[i]     - minV) / range)
                            drawLine(color = Color(0xFF64B5F6), start = Offset(x0, y0), end = Offset(x1, y1), strokeWidth = 2f)
                        }
                    }
                }
            }
        }

        OutlinedButton(
            onClick = { clipboard.setText(AnnotatedString(vm.exportOscillationCsv())) },
            modifier = Modifier.fillMaxWidth(),
            enabled  = state.accelWaveformG.isNotEmpty(),
        ) { Text("📤 Copy CSV to clipboard") }
    }
}
