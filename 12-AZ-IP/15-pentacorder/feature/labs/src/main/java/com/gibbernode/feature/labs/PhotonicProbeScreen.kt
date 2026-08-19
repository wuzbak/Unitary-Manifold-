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
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.gibbernode.ui.GibberAmber
import com.gibbernode.ui.GibberBlue
import com.gibbernode.ui.GibberGreen
import com.gibbernode.ui.GibberRed
import com.gibbernode.ui.OnSurfaceDim
import com.gibbernode.ui.SurfaceDark

/**
 * PhotonicProbeScreen
 *
 * Compose wrapper for S24Ultra/scripts/photonic_probe.py.
 * Three sub-tabs:
 *
 *  0 — 🎲 TRNG       : Camera pixel noise → Von Neumann de-bias → SHA-256 → random hex
 *  1 — 💡 Flicker    : Dual-frame luminance variance → flicker detection
 *  2 — 🔭 Dark Scan  : Single dark frame → hot-pixel / anomalous-event detection
 */
@Composable
fun PhotonicProbeScreen(viewModel: PhotonicProbeViewModel = hiltViewModel()) {
    val state         by viewModel.state.collectAsStateWithLifecycle()
    val lifecycleOwner = LocalLifecycleOwner.current
    var tab by remember { mutableIntStateOf(0) }

    Column(modifier = Modifier.fillMaxSize()) {
        // Header
        Column(modifier = Modifier.padding(horizontal = 16.dp, vertical = 10.dp)) {
            Text("🔬 Photonic Probe", style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold)
            Text("Camera as a quantum sensing instrument (photonic_probe.py port)",
                style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
        }

        ScrollableTabRow(selectedTabIndex = tab, edgePadding = 0.dp) {
            Tab(selected = tab == 0, onClick = { tab = 0 }, text = { Text("🎲 TRNG", fontSize = 13.sp) })
            Tab(selected = tab == 1, onClick = { tab = 1 }, text = { Text("💡 Flicker", fontSize = 13.sp) })
            Tab(selected = tab == 2, onClick = { tab = 2 }, text = { Text("🔭 Dark Scan", fontSize = 13.sp) })
        }

        when (tab) {
            0 -> TrngTab(state = state, running = state.running && state.mode == PhotonicMode.TRNG,
                onStart = { viewModel.startTrng(lifecycleOwner) })
            1 -> FlickerTab(state = state, running = state.running && state.mode == PhotonicMode.FLICKER,
                onStart = { viewModel.startFlicker(lifecycleOwner) })
            2 -> DarkScanTab(state = state, running = state.running && state.mode == PhotonicMode.DARK_SCAN,
                onStart = { viewModel.startDarkScan(lifecycleOwner) })
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 0 — TRNG
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun TrngTab(state: PhotonicProbeUiState, running: Boolean, onStart: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Card(colors = CardDefaults.cardColors(containerColor = GibberAmber.copy(alpha = 0.08f)),
            modifier = Modifier.fillMaxWidth()) {
            Text(
                "Extracts entropy from camera photon shot noise (JPEG pixel LSBs). " +
                "Output is de-biased via Von Neumann extraction and whitened with SHA-256. " +
                "⚠️ ISP processing reduces raw entropy — for maximum quality, use RAW (DNG) mode. " +
                "Cover the lens completely for TRNG; point at a bright, steady light source for best SNR.",
                style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim,
                modifier = Modifier.padding(12.dp))
        }

        val result = state.result as? PhotonicResult.TrngResult
        result?.let { r ->
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("🎲 ${r.byteCount} Random Bytes", style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold)
                    Text(r.hexBytes, style = MaterialTheme.typography.bodySmall,
                        fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
                        color = GibberGreen)
                    Row(modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween) {
                        Column {
                            Text("%.4f bits/bit".format(r.entropyEst), fontWeight = FontWeight.Bold,
                                style = MaterialTheme.typography.bodySmall)
                            Text("Entropy estimate (max 1.0)", style = MaterialTheme.typography.labelSmall,
                                color = OnSurfaceDim)
                        }
                        Column(horizontalAlignment = Alignment.End) {
                            Text("${r.rawBitCount} bits",
                                style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.Bold)
                            Text("Raw bits sampled", style = MaterialTheme.typography.labelSmall,
                                color = OnSurfaceDim)
                        }
                    }
                }
            }
        }

        state.error?.let { err ->
            Text("⚠️ $err", style = MaterialTheme.typography.bodySmall, color = GibberRed)
        }

        Button(onClick = onStart, enabled = !running,
            colors = ButtonDefaults.buttonColors(containerColor = GibberBlue),
            modifier = Modifier.fillMaxWidth()) {
            if (running) {
                CircularProgressIndicator(modifier = Modifier.size(18.dp), strokeWidth = 2.dp, color = Color.White)
                Spacer(Modifier.width(6.dp))
                Text("Capturing…")
            } else {
                Text("📸 Capture Frame & Extract Random Bytes")
            }
        }
        Text("Cover the camera lens before tapping. Dark frame gives highest entropy.",
            style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 1 — Flicker
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun FlickerTab(state: PhotonicProbeUiState, running: Boolean, onStart: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Card(colors = CardDefaults.cardColors(containerColor = GibberAmber.copy(alpha = 0.08f)),
            modifier = Modifier.fillMaxWidth()) {
            Text(
                "Captures two frames and measures inter-frame luminance change. " +
                "A flickering light source (mains-frequency LED, hidden IR camera) produces " +
                "significant frame-to-frame luma variance. Threshold: > 3% luma difference = flicker detected.",
                style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim,
                modifier = Modifier.padding(12.dp))
        }

        val result = state.result as? PhotonicResult.FlickerResult
        result?.let { r ->
            val color = if (r.flickerDetected) GibberRed else GibberGreen
            Card(colors = CardDefaults.cardColors(containerColor = color.copy(alpha = 0.08f)),
                modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(if (r.flickerDetected) "💡 FLICKER DETECTED" else "✅ No Flicker Detected",
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold, color = color)
                    Row(modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween) {
                        Column {
                            Text("%.1f".format(r.lumaFrameA), fontWeight = FontWeight.Bold,
                                style = MaterialTheme.typography.bodySmall)
                            Text("Frame A luma", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        }
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("Δ %.2f (%.1f%%)".format(r.lumaDiff, r.flickerPct),
                                fontWeight = FontWeight.Bold, style = MaterialTheme.typography.bodySmall)
                            Text("Luma diff", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        }
                        Column(horizontalAlignment = Alignment.End) {
                            Text("%.1f".format(r.lumaFrameB), fontWeight = FontWeight.Bold,
                                style = MaterialTheme.typography.bodySmall)
                            Text("Frame B luma", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        }
                    }
                }
            }
        }

        state.error?.let { err ->
            Text("⚠️ $err", style = MaterialTheme.typography.bodySmall, color = GibberRed)
        }

        Button(onClick = onStart, enabled = !running,
            colors = ButtonDefaults.buttonColors(containerColor = GibberAmber),
            modifier = Modifier.fillMaxWidth()) {
            if (running) {
                CircularProgressIndicator(modifier = Modifier.size(18.dp), strokeWidth = 2.dp, color = Color.Black)
                Spacer(Modifier.width(6.dp))
                Text("Capturing…", color = Color.Black)
            } else {
                Text("📸 Capture Two Frames & Detect Flicker", color = Color.Black)
            }
        }
        Text("Point the rear camera at any light source. Works on ceiling lights, monitors, LEDs.",
            style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 2 — Dark Scan
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun DarkScanTab(state: PhotonicProbeUiState, running: Boolean, onStart: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Card(colors = CardDefaults.cardColors(containerColor = GibberAmber.copy(alpha = 0.08f)),
            modifier = Modifier.fillMaxWidth()) {
            Text(
                "Captures a dark frame and identifies 'hot pixels' — pixels whose green-channel " +
                "intensity exceeds mean + 3σ of the dark-frame distribution. Hot pixels can " +
                "result from: sensor defects, cosmic-ray hits, IR contamination, or thermal noise. " +
                "⚠️ JPEG ISP may suppress single-pixel spikes — for true cosmic-ray detection use RAW DNG.",
                style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim,
                modifier = Modifier.padding(12.dp))
        }

        val result = state.result as? PhotonicResult.DarkScanResult
        result?.let { r ->
            val ppm = (r.hotFraction * 1_000_000f).toInt()
            val hotColor = when {
                ppm > 1000 -> GibberRed
                ppm > 100  -> GibberAmber
                else       -> GibberGreen
            }
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("🔭 Dark Scan Result", style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold)
                    Row(modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween) {
                        Column {
                            Text("${r.hotPixelCount}", fontWeight = FontWeight.Bold,
                                style = MaterialTheme.typography.headlineMedium, color = hotColor)
                            Text("Hot pixels / ${r.totalPixels} total",
                                style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        }
                        Column(horizontalAlignment = Alignment.End) {
                            Text("$ppm ppm", fontWeight = FontWeight.Bold,
                                style = MaterialTheme.typography.titleSmall, color = hotColor)
                            Text("Hot pixel rate", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        }
                    }
                    Row(modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween) {
                        Column {
                            Text("%.1f ± %.1f".format(r.meanGreen, r.stddevGreen),
                                style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.Bold)
                            Text("Green channel mean ± σ",
                                style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        }
                        Column(horizontalAlignment = Alignment.End) {
                            Text("%.1f".format(r.threshold),
                                style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.Bold)
                            Text("Hot-pixel threshold (μ+3σ)",
                                style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        }
                    }
                }
            }
        }

        state.error?.let { err ->
            Text("⚠️ $err", style = MaterialTheme.typography.bodySmall, color = GibberRed)
        }

        Button(onClick = onStart, enabled = !running,
            colors = ButtonDefaults.buttonColors(containerColor = GibberGreen),
            modifier = Modifier.fillMaxWidth()) {
            if (running) {
                CircularProgressIndicator(modifier = Modifier.size(18.dp), strokeWidth = 2.dp, color = Color.Black)
                Spacer(Modifier.width(6.dp))
                Text("Scanning…", color = Color.Black)
            } else {
                Text("🔭 Capture Dark Frame & Scan", color = Color.Black)
            }
        }
        Text("Cover the camera lens completely. Longer exposure = better dark-frame quality.",
            style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
    }
}
