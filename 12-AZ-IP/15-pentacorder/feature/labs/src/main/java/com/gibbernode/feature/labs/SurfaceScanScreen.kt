package com.gibbernode.feature.labs

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ScrollableTabRow
import androidx.compose.material3.Tab
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
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
 * SurfaceScanScreen
 *
 * Compose wrapper for S24Ultra/scripts/surface_scan.py.
 * Two sub-tabs:
 *
 *  0 — 🏗️ Surface Classify : Tap → accelerometer decay → material classification
 *  1 — 🫀 Life Sign          : Hold still 10 s → FFT breathing + heartbeat detection
 */
@Composable
fun SurfaceScanScreen(viewModel: SurfaceScanViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    var tab by remember { mutableIntStateOf(0) }

    Column(modifier = Modifier.fillMaxSize()) {
        // Header
        Column(modifier = Modifier.padding(horizontal = 16.dp, vertical = 10.dp)) {
            Text("🏗️ Surface Scan", style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold)
            Text("Tap-test material classifier + life-sign detector (surface_scan.py port)",
                style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
        }

        ScrollableTabRow(selectedTabIndex = tab, edgePadding = 0.dp) {
            Tab(selected = tab == 0, onClick = { tab = 0 },
                text = { Text("🏗️ Surface", fontSize = 13.sp) })
            Tab(selected = tab == 1, onClick = { tab = 1 },
                text = { Text("🫀 Life Sign", fontSize = 13.sp) })
        }

        when (tab) {
            0 -> SurfaceTab(state = state, vm = viewModel)
            1 -> LifeSignTab(state = state, vm = viewModel)
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 0 — Surface Classify
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun SurfaceTab(state: SurfaceScanUiState, vm: SurfaceScanViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Card(colors = CardDefaults.cardColors(containerColor = GibberAmber.copy(alpha = 0.08f)),
            modifier = Modifier.fillMaxWidth()) {
            Text(
                "After tapping 'Start', tap the target surface firmly once with your finger or the S Pen. " +
                "The accelerometer records the vibration ringdown (~2 s). " +
                "The exponential decay constant λ determines the material classification.",
                style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim,
                modifier = Modifier.padding(12.dp))
        }

        // Progress bar while scanning
        if (state.scanning && state.mode == ScanMode.SURFACE) {
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("🏗️ Recording tap vibration…", style = MaterialTheme.typography.bodyMedium)
                    Spacer(Modifier.height(8.dp))
                    LinearProgressIndicator(
                        progress = state.progress,
                        modifier = Modifier.fillMaxWidth(),
                        color    = GibberAmber,
                    )
                    Spacer(Modifier.height(4.dp))
                    Text("${(state.progress * 100).toInt()}% — tap the surface now",
                        style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                }
            }
        }

        // Result
        state.surfaceResult?.let { r ->
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Row(modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically) {
                        Column {
                            Text("${r.emoji} ${r.material}", style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold, color = GibberAmber)
                            Text("Confidence: ${"%.0f".format(r.confidence * 100)}%",
                                style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        }
                        Column(horizontalAlignment = Alignment.End) {
                            Text("φ = %.3f".format(r.phiSurface), fontWeight = FontWeight.Bold,
                                style = MaterialTheme.typography.titleSmall, color = GibberBlue)
                            Text("Manifold field", style = MaterialTheme.typography.labelSmall,
                                color = OnSurfaceDim)
                        }
                    }
                    Row(modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween) {
                        Column {
                            Text("λ = %.1f /s".format(r.decayConst), fontWeight = FontWeight.Bold,
                                style = MaterialTheme.typography.bodySmall)
                            Text("Decay constant", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        }
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("%.2f g".format(r.peakAccelG), fontWeight = FontWeight.Bold,
                                style = MaterialTheme.typography.bodySmall)
                            Text("Peak accel", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        }
                        Column(horizontalAlignment = Alignment.End) {
                            Text("%.0f/100".format(r.hardness), fontWeight = FontWeight.Bold,
                                style = MaterialTheme.typography.bodySmall)
                            Text("Hardness", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        }
                    }
                    Text(r.advice, style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
                    Text("${r.sampleCount} accelerometer samples", style = MaterialTheme.typography.labelSmall,
                        color = OnSurfaceDim)
                }
            }
        }

        state.error?.let { err ->
            Text("⚠️ $err", style = MaterialTheme.typography.bodySmall, color = GibberRed)
        }

        if (state.scanning && state.mode == ScanMode.SURFACE) {
            Button(onClick = vm::cancelScan,
                colors = ButtonDefaults.buttonColors(containerColor = GibberRed),
                modifier = Modifier.fillMaxWidth()) {
                Text("⏹ Cancel")
            }
        } else {
            Button(onClick = vm::startSurfaceScan,
                enabled = !state.scanning,
                colors = ButtonDefaults.buttonColors(containerColor = GibberAmber),
                modifier = Modifier.fillMaxWidth()) {
                Text("🏗️ Start Surface Scan", color = Color.Black)
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 1 — Life Sign
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun LifeSignTab(state: SurfaceScanUiState, vm: SurfaceScanViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Card(colors = CardDefaults.cardColors(containerColor = GibberAmber.copy(alpha = 0.08f)),
            modifier = Modifier.fillMaxWidth()) {
            Text(
                "Rest the phone on a surface (table, bed, or flat on the chest). " +
                "Hold very still for ~10 seconds. FFT analysis detects: " +
                "Breathing (0.15–0.5 Hz) and Heartbeat (0.8–2.5 Hz) from sub-visual vibration. " +
                "⚠️ NOT a medical device. Results depend on surface coupling quality.",
                style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim,
                modifier = Modifier.padding(12.dp))
        }

        // Progress bar
        if (state.scanning && state.mode == ScanMode.LIFE_SIGN) {
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("🫀 Recording… hold completely still", style = MaterialTheme.typography.bodyMedium)
                    Spacer(Modifier.height(8.dp))
                    LinearProgressIndicator(
                        progress = state.progress,
                        modifier = Modifier.fillMaxWidth(),
                        color    = GibberBlue,
                    )
                    Spacer(Modifier.height(4.dp))
                    Text("${(state.progress * 100).toInt()}% — ${10 - (state.progress * 10).toInt()} s remaining",
                        style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                }
            }
        }

        // Result
        state.lifeSignResult?.let { r ->
            val signalColor = if (r.lifeSignDetected) GibberGreen else GibberRed
            Card(colors = CardDefaults.cardColors(containerColor = signalColor.copy(alpha = 0.08f)),
                modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(if (r.lifeSignDetected) "🫀 Life Signs Detected" else "❓ No Life Sign Signal",
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold, color = signalColor)

                    // Breathing
                    Row(modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween) {
                        Column {
                            Text(r.breathingRpm?.let { "%.1f rpm".format(it) } ?: "—",
                                fontWeight = FontWeight.Bold, style = MaterialTheme.typography.headlineMedium,
                                color = if (r.breathSnrPct > 0.5f) GibberBlue else OnSurfaceDim)
                            Text("Breathing", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                            Text("SNR: %.2f%%".format(r.breathSnrPct),
                                style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        }
                        Column(horizontalAlignment = Alignment.End) {
                            Text(r.heartBpm?.let { "%.0f bpm".format(it) } ?: "—",
                                fontWeight = FontWeight.Bold, style = MaterialTheme.typography.headlineMedium,
                                color = if (r.heartSnrPct > 0.5f) GibberRed else OnSurfaceDim)
                            Text("Heartbeat", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                            Text("SNR: %.2f%%".format(r.heartSnrPct),
                                style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        }
                    }
                    Text("${r.sampleCount} samples analysed (${r.sampleCount / 100} s at 100 Hz)",
                        style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                }
            }
        }

        state.error?.let { err ->
            Text("⚠️ $err", style = MaterialTheme.typography.bodySmall, color = GibberRed)
        }

        if (state.scanning && state.mode == ScanMode.LIFE_SIGN) {
            Button(onClick = vm::cancelScan,
                colors = ButtonDefaults.buttonColors(containerColor = GibberRed),
                modifier = Modifier.fillMaxWidth()) {
                Text("⏹ Cancel")
            }
        } else {
            Button(onClick = vm::startLifeSignScan,
                enabled = !state.scanning,
                colors = ButtonDefaults.buttonColors(containerColor = GibberBlue),
                modifier = Modifier.fillMaxWidth()) {
                Text("🫀 Start Life Sign Scan (~10 s)")
            }
        }

        Text(
            "For best results: place phone flat on a firm surface, no movement, good contact. " +
            "Hold arms still and breathe normally.",
            style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim,
        )
    }
}
