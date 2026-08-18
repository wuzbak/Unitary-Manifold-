package com.gibbernode.feature.acoustic

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.lerp
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.gibbernode.acoustic.AcousticAdvisor
import com.gibbernode.ui.GibberAmber
import com.gibbernode.ui.GibberBlue
import com.gibbernode.ui.GibberGreen
import com.gibbernode.ui.GibberRed
import com.gibbernode.ui.OnSurfaceDim
import com.gibbernode.ui.SurfaceDark
import kotlin.math.log10

/**
 * AcousticScreen — 🎵 Acoustic Intelligence
 *
 * Sub-tabs:
 *  0 — 🔔 Alert Monitor : armed/disarmed + real-time spectrum + alert banners
 *  1 — 🔧 Diagnostic     : engine-knock / pipe-leak spectrogram
 *  2 — 🎙️ Gyrophone     : side-channel physics demo (educational)
 */
@Composable
fun AcousticScreen(viewModel: AcousticViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    var tab   by remember { mutableIntStateOf(0) }

    Column(modifier = Modifier.fillMaxSize()) {
        ScrollableTabRow(selectedTabIndex = tab, edgePadding = 0.dp) {
            Tab(selected = tab == 0, onClick = { tab = 0 }, text = { Text("🔔 Alert Monitor", fontSize = 13.sp) })
            Tab(selected = tab == 1, onClick = { tab = 1 }, text = { Text("🔧 Diagnostic", fontSize = 13.sp) })
            Tab(selected = tab == 2, onClick = { tab = 2 }, text = { Text("🎙️ Gyrophone", fontSize = 13.sp) })
            Tab(selected = tab == 3, onClick = { tab = 3 }, text = { Text("🔊 dB Meter", fontSize = 13.sp) })
            Tab(selected = tab == 4, onClick = { tab = 4 }, text = { Text("📈 Oscilloscope", fontSize = 13.sp) })
        }
        when (tab) {
            0 -> AlertMonitorTab(state, viewModel)
            1 -> DiagnosticTab(state, viewModel)
            2 -> GyrophoneTab()
            3 -> DbMeterTab(state, viewModel)
            4 -> OscilloscopeTab(state, viewModel)
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 0 — Alert Monitor
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun AlertMonitorTab(state: AcousticUiState, vm: AcousticViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        // Alert banner
        if (state.primaryAlert != AcousticAdvisor.AlertType.NONE) {
            Card(colors = CardDefaults.cardColors(containerColor = GibberRed.copy(alpha = 0.15f)), modifier = Modifier.fillMaxWidth()) {
                Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text("${state.primaryAlert.emoji} ${state.primaryAlert.label}",
                            style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = GibberRed)
                        state.alerts.forEach { a ->
                            Text(a, style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        }
                    }
                    TextButton(onClick = vm::dismissAlerts) { Text("Dismiss") }
                }
            }
        }

        // Monitor toggle
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            if (!state.monitoring) {
                Button(onClick = vm::startMonitoring, modifier = Modifier.weight(1f)) {
                    Text("🎙️ Start Monitoring")
                }
            } else {
                Button(onClick = vm::stopMonitoring,
                    colors = ButtonDefaults.buttonColors(containerColor = GibberRed),
                    modifier = Modifier.weight(1f)) {
                    Text("⏹ Stop")
                }
            }
        }

        // Sensitivity selector
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Sensitivity", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    AcousticAdvisor.AlertSensitivity.entries.forEach { s ->
                        FilterChip(
                            selected  = state.sensitivity == s,
                            onClick   = { vm.setSensitivity(s) },
                            label     = { Text(s.label, fontSize = 12.sp) },
                        )
                    }
                }
            }
        }

        // Live levels
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Live Signal", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                AcousticRow("Overall Level",  "%.3f".format(state.overallLevel))
                AcousticRow("Peak Frequency", "%.0f Hz".format(state.spectrumPeakHz))

                // Spectrum bar chart (downsampled to 32 bins)
                if (state.lastSpectrum.isNotEmpty()) {
                    Spacer(Modifier.height(8.dp))
                    SpectrumBars(state.lastSpectrum)
                }
            }
        }
    }
}

@Composable
private fun SpectrumBars(spectrum: FloatArray) {
    val bins    = 32
    val step    = (spectrum.size / bins).coerceAtLeast(1)
    val reduced = FloatArray(bins) { i ->
        val from = i * step; val to = ((i + 1) * step).coerceAtMost(spectrum.size)
        spectrum.slice(from until to).average().toFloat()
    }
    val peak = reduced.max().coerceAtLeast(0.001f)
    Canvas(modifier = Modifier.fillMaxWidth().height(80.dp)) {
        val w = size.width; val h = size.height
        val bw = w / bins
        reduced.forEachIndexed { i, v ->
            val barH = (v / peak) * h
            val freq  = i.toFloat() / bins  // 0–1 normalised → colour
            drawRect(
                color = lerp(Color(0xFF1565C0), Color(0xFFFF6D00), freq),
                topLeft = Offset(i * bw, h - barH),
                size    = Size(bw * 0.85f, barH),
            )
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 1 — Diagnostic
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun DiagnosticTab(state: AcousticUiState, vm: AcousticViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text("Extended diagnostic mode for engine knock and pipe leak detection.",
            style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(
                onClick = {
                    vm.startDiagnostic(DiagnosticMode.ENGINE)
                    vm.startMonitoring()
                },
                enabled = !state.monitoring,
                modifier = Modifier.weight(1f),
            ) { Text("🔧 Engine Knock") }
            Button(
                onClick = {
                    vm.startDiagnostic(DiagnosticMode.PIPE)
                    vm.startMonitoring()
                },
                enabled = !state.monitoring,
                modifier = Modifier.weight(1f),
            ) { Text("💧 Pipe Leak") }
            if (state.monitoring) {
                OutlinedButton(onClick = { vm.stopMonitoring(); vm.finishDiagnostic() }, modifier = Modifier.weight(1f)) {
                    Text("Finish")
                }
            }
        }

        state.diagnosticResult?.let { r ->
            val c = when (r.alertType) {
                AcousticAdvisor.AlertType.NONE -> GibberGreen
                else                           -> GibberAmber
            }
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("${r.alertType.emoji} ${r.alertType.label}", style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold, color = c)
                    Spacer(Modifier.height(8.dp))
                    AcousticRow("Confidence",   "%.0f%%".format(r.confidence * 100f))
                    AcousticRow("Peak Freq",    "%.0f Hz".format(r.peakFreqHz))
                    AcousticRow("Periodicity",  "%.2f".format(r.periodicity))
                    Spacer(Modifier.height(8.dp))
                    Text(r.interpretation, style = MaterialTheme.typography.bodySmall)
                }
            }
        }

        // Spectrogram waterfall
        if (state.waterfallFrames.size >= 4) {
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Spectrogram (last ${state.waterfallFrames.size} frames)", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                    Spacer(Modifier.height(8.dp))
                    SpectrogramWaterfall(state.waterfallFrames)
                }
            }
        }
    }
}

@Composable
private fun SpectrogramWaterfall(frames: List<FloatArray>) {
    Canvas(modifier = Modifier.fillMaxWidth().height(120.dp)) {
        val w = size.width; val h = size.height
        val cols   = frames.size
        val colW   = w / cols
        val binCnt = (frames.firstOrNull()?.size ?: 1).coerceAtLeast(1)

        frames.forEachIndexed { col, spectrum ->
            val peak = spectrum.max().coerceAtLeast(0.001f)
            val binH = h / binCnt
            for (bin in 0 until binCnt) {
                val intensity = (spectrum.getOrElse(bin) { 0f } / peak).coerceIn(0f, 1f)
                // dB approximation
                val db = if (intensity > 0f) (20f * log10(intensity)).coerceIn(-60f, 0f) / 60f + 1f else 0f
                drawRect(
                    color   = lerp(Color.Black, Color(0xFF64B5F6), db),
                    topLeft = Offset(col * colW, h - (bin + 1) * binH),
                    size    = Size(colW, binH),
                )
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 2 — Gyrophone
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun GyrophoneTab() {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("🎙️ Gyrophone — Educational Mode", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                Text(
                    "Smartphones carry MEMS gyroscopes that — like any vibrating rigid body — " +
                    "respond to acoustic vibrations in the environment.\n\n" +
                    "The gyroscope's resonant frequency band (typically 100–3000 Hz) overlaps " +
                    "with human speech, meaning the gyroscope signal contains a faint acoustic " +
                    "side-channel.\n\n" +
                    "This was first demonstrated by Michalevsky et al. (2014) and Marquardt et " +
                    "al. (2011), showing that words could be partially reconstructed from " +
                    "uncalibrated gyro data — without microphone permission.\n\n" +
                    "Key physics:\n" +
                    "  • MEMS gyroscope proof mass oscillates at ~20–40 kHz\n" +
                    "  • External acoustic pressure modulates the oscillation amplitude\n" +
                    "  • Demodulated signal ≈ low-pass filtered version of the sound field\n" +
                    "  • Maximum SNR at frequencies near the gyro resonance (~100–3000 Hz)",
                    style = MaterialTheme.typography.bodySmall,
                )
                Spacer(Modifier.height(8.dp))
                Text(
                    "⚠️ This screen demonstrates the physics only. " +
                    "No audio is recorded or transmitted. " +
                    "Android requires the RECORD_AUDIO permission for microphone access; " +
                    "gyroscope access requires no permission (a known privacy concern " +
                    "documented in CVE-2023-21250).",
                    style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim,
                )
            }
        }

        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Side-Channel Mitigations (Android 13+)", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                listOf(
                    "Android 13: gyro sample rate limited to 200 Hz for unprivileged apps",
                    "Android 12: background sensor access requires BODY_SENSORS_BACKGROUND permission",
                    "Android 11: sensor access throttled when screen is off",
                    "Android 9: VIBRATE permission required for vibration side-channel",
                ).forEach { mitigation ->
                    Text("• $mitigation", style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(vertical = 2.dp))
                }
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun AcousticRow(label: String, value: String) {
    Row(modifier = Modifier.fillMaxWidth().padding(vertical = 2.dp)) {
        Text(label, style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim, modifier = Modifier.weight(1.2f))
        Text(value, style = MaterialTheme.typography.bodySmall, fontFamily = FontFamily.Monospace)
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 3 — dB Meter
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun DbMeterTab(state: AcousticUiState, vm: AcousticViewModel) {
    val clipboard = LocalClipboardManager.current
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        // Start/stop
        if (!state.monitoring) {
            Button(onClick = vm::startMonitoring, modifier = Modifier.fillMaxWidth()) {
                Text("🎙️ Start dB Meter")
            }
        } else {
            Button(onClick = vm::stopMonitoring,
                colors = ButtonDefaults.buttonColors(containerColor = GibberRed),
                modifier = Modifier.fillMaxWidth()) {
                Text("⏹ Stop")
            }
        }

        // Large dB readout
        val db = state.dbSpl.coerceIn(-120f, 140f)
        val dbColor = when {
            db < 50f  -> GibberGreen
            db < 70f  -> GibberBlue
            db < 85f  -> GibberAmber
            db < 100f -> Color(0xFFFF6D00)
            else      -> GibberRed
        }
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    "%.1f".format(db),
                    style = MaterialTheme.typography.displayLarge,
                    fontWeight = FontWeight.Bold,
                    color = dbColor,
                    fontFamily = FontFamily.Monospace,
                )
                Text(
                    if (state.dbAWeighted) "dB(A)" else "dB SPL",
                    style = MaterialTheme.typography.titleMedium,
                    color = OnSurfaceDim,
                )
                Spacer(Modifier.height(8.dp))
                // Level bar
                val progress = ((db + 120f) / 260f).coerceIn(0f, 1f)
                LinearProgressIndicator(progress = { progress }, modifier = Modifier.fillMaxWidth(), color = dbColor)
                Spacer(Modifier.height(4.dp))
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("Min: %.1f dB".format(state.dbMin.coerceIn(-120f, 140f)),
                        style = MaterialTheme.typography.labelSmall, color = GibberGreen)
                    Text("Peak: %.1f dB".format(state.dbPeak.coerceIn(-120f, 140f)),
                        style = MaterialTheme.typography.labelSmall, color = GibberRed)
                }
            }
        }

        // Controls row
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            FilterChip(
                selected = state.dbAWeighted,
                onClick  = vm::toggleAWeighting,
                label    = { Text("A-weighted") },
                modifier = Modifier.weight(1f),
            )
            OutlinedButton(onClick = vm::resetDbPeakMin, modifier = Modifier.weight(1f)) {
                Text("↺ Reset Peak/Min")
            }
        }

        // Calibration offset
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Calibration offset: %+.1f dB".format(state.dbCalibOffset),
                    style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Slider(
                    value         = state.dbCalibOffset,
                    onValueChange = vm::setDbCalibOffset,
                    valueRange    = -20f..20f,
                    steps         = 79,
                    modifier      = Modifier.fillMaxWidth(),
                )
                Text(
                    "Adjust if your device reads high or low vs. a reference meter.",
                    style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim,
                )
            }
        }

        // dB history sparkline
        if (state.dbHistory.size >= 2) {
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("dB history (last ${state.dbHistory.size} samples)",
                        style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                    Spacer(Modifier.height(8.dp))
                    Canvas(modifier = Modifier.fillMaxWidth().height(80.dp)) {
                        val w = size.width; val h = size.height
                        val vals = state.dbHistory.map { it.second }
                        val minV = vals.min().coerceAtLeast(-120f)
                        val maxV = vals.max().coerceAtMost(140f)
                        val range = (maxV - minV).coerceAtLeast(1f)
                        val step  = w / (vals.size - 1)
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
            onClick = { clipboard.setText(AnnotatedString(vm.exportDbCsv())) },
            modifier = Modifier.fillMaxWidth(),
        ) { Text("📤 Copy CSV to clipboard") }

        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Reference levels", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(4.dp))
                listOf(
                    "30 dB" to "Quiet bedroom",
                    "50 dB" to "Normal conversation",
                    "70 dB" to "Busy street",
                    "85 dB" to "Hearing damage threshold (8 h/day)",
                    "100 dB" to "Power tools",
                    "120 dB" to "Jet engine at 30 m",
                ).forEach { (lvl, desc) ->
                    Row(modifier = Modifier.fillMaxWidth().padding(vertical = 1.dp)) {
                        Text(lvl,  style = MaterialTheme.typography.labelSmall, fontFamily = FontFamily.Monospace, modifier = Modifier.width(52.dp))
                        Text(desc, style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                    }
                }
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 4 — Oscilloscope
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun OscilloscopeTab(state: AcousticUiState, vm: AcousticViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        // Start/stop + freeze
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            if (!state.monitoring) {
                Button(onClick = vm::startMonitoring, modifier = Modifier.weight(1f)) { Text("▶ Start") }
            } else {
                Button(onClick = vm::stopMonitoring,
                    colors = ButtonDefaults.buttonColors(containerColor = GibberRed),
                    modifier = Modifier.weight(1f)) { Text("⏹ Stop") }
            }
            Button(
                onClick = vm::freezeOscilloscope,
                colors = if (state.oscFrozen) ButtonDefaults.buttonColors(containerColor = GibberAmber)
                         else ButtonDefaults.outlinedButtonColors(),
                modifier = Modifier.weight(1f),
            ) { Text(if (state.oscFrozen) "❄ Frozen" else "❄ Freeze") }
        }

        // Waveform canvas
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("Waveform  (${state.oscTimeWindowMs} ms window)",
                        style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                    if (state.oscFrozen) Text("FROZEN", style = MaterialTheme.typography.labelSmall, color = GibberAmber, fontWeight = FontWeight.Bold)
                }
                Spacer(Modifier.height(8.dp))
                val waveform = state.oscWaveform
                if (waveform.isEmpty()) {
                    Text("No signal — tap Start", style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
                } else {
                    Canvas(modifier = Modifier.fillMaxWidth().height(150.dp)) {
                        val w = size.width; val h = size.height
                        val midY = h / 2f
                        // Zero line
                        drawLine(color = Color.Gray.copy(alpha = 0.3f), start = Offset(0f, midY), end = Offset(w, midY), strokeWidth = 1f)
                        // Trigger level line
                        if (state.oscTriggerLevel != 0f) {
                            val trigY = midY - state.oscTriggerLevel * midY
                            drawLine(color = GibberAmber.copy(alpha = 0.6f), start = Offset(0f, trigY), end = Offset(w, trigY), strokeWidth = 1f)
                        }
                        val step = w / waveform.size.coerceAtLeast(1)
                        for (i in 1 until waveform.size) {
                            val x0 = (i - 1) * step; val x1 = i * step
                            val y0 = midY - waveform[i - 1] * midY * 0.9f
                            val y1 = midY - waveform[i]     * midY * 0.9f
                            drawLine(color = Color(0xFF64B5F6), start = Offset(x0, y0), end = Offset(x1, y1), strokeWidth = 1.5f)
                        }
                    }
                }
            }
        }

        // Time window selector
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Time window: ${state.oscTimeWindowMs} ms",
                    style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Slider(
                    value         = state.oscTimeWindowMs.toFloat(),
                    onValueChange = { vm.setOscTimeWindow(it.toInt()) },
                    valueRange    = 5f..500f,
                    steps         = 98,
                    modifier      = Modifier.fillMaxWidth(),
                )
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("5 ms",   style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                    Text("500 ms", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                }
            }
        }

        // Trigger level
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Trigger level: %+.2f".format(state.oscTriggerLevel),
                    style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Slider(
                    value         = state.oscTriggerLevel,
                    onValueChange = vm::setOscTriggerLevel,
                    valueRange    = -1f..1f,
                    steps         = 99,
                    modifier      = Modifier.fillMaxWidth(),
                )
                Text("Set to 0 to disable triggering (free-running).",
                    style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
            }
        }
    }
}
