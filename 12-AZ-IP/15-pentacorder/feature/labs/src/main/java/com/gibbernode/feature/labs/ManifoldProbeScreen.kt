package com.gibbernode.feature.labs

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.gibbernode.ui.GibberAmber
import com.gibbernode.ui.GibberBlue
import com.gibbernode.ui.GibberGreen
import com.gibbernode.ui.GibberRed
import com.gibbernode.ui.OnSurfaceDim
import com.gibbernode.ui.SurfaceDark

/**
 * ManifoldProbeScreen
 *
 * Compose wrapper for the manifold_probe.py Unitary-Manifold field calculator.
 *
 * Reads live sensor data from SensorBridge (written by TricorderViewModel) and
 * runs the 5D Kaluza-Klein RK4 field evolution in [ManifoldProbeViewModel].
 *
 * Displays:
 *   - Live manifold state: φ (radion), B_norm (gauge field), R (Ricci scalar)
 *   - det(g) metric determinant proxy
 *   - Information current J^μ_inf and sparkline history
 *   - Constraint monitor (flags when fields exceed stability bounds)
 *   - Plain-language status line
 *   - Raw sensor inputs panel
 *   - Demo mode button (no TricorderViewModel sensors needed)
 */
@Composable
fun ManifoldProbeScreen(viewModel: ManifoldProbeViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        // Header
        Text(
            "🌌 Manifold Probe",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
        )
        Text(
            "Live sensor data → 5D Kaluza-Klein field evolution (manifold_probe.py port).",
            style = MaterialTheme.typography.bodySmall,
            color = OnSurfaceDim,
        )

        // ── Status line ───────────────────────────────────────────────────────
        val statusColor = when {
            state.ricciFlag || state.bFlag || state.phiFlag -> GibberRed
            state.jInf < 0.05f                              -> GibberGreen
            state.jInf < 0.15f                              -> GibberAmber
            else                                            -> GibberRed
        }
        Card(
            colors   = CardDefaults.cardColors(containerColor = statusColor.copy(alpha = 0.10f)),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(
                text     = state.statusLine,
                style    = MaterialTheme.typography.bodyMedium,
                color    = statusColor,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(12.dp),
            )
        }

        // ── Manifold state vector ─────────────────────────────────────────────
        Card(
            colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text("Manifold State Ψ(t)", style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold)

                ManifoldFieldRow("φ  (radion)", state.phi,
                    flagged = state.phiFlag, baseline = 1f, unit = "× ISA")
                ManifoldFieldRow("B  (gauge field)", state.bNorm,
                    flagged = state.bFlag, baseline = 1f, unit = "× Earth")
                ManifoldFieldRow("R  (Ricci)", state.ricciScalar,
                    flagged = state.ricciFlag, baseline = 0f, unit = "")
                ManifoldFieldRow("det(g)", state.detG,
                    flagged = false, baseline = 1f, unit = "")
            }
        }

        // ── Information current ───────────────────────────────────────────────
        Card(
            colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically) {
                    Text("J^μ_inf (information current)", style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold)
                    val jColor = if (state.jInf < 0.05f) GibberGreen else if (state.jInf < 0.15f) GibberAmber else GibberRed
                    Text("%.4f".format(state.jInf),
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = jColor)
                }
                Text("∇_μ J^μ_inf = 0 at Harmonic State (full coherence)",
                    style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)

                // Sparkline
                if (state.jInfHistory.size >= 2) {
                    Spacer(Modifier.height(8.dp))
                    Canvas(modifier = Modifier.fillMaxWidth().height(50.dp)) {
                        val w    = size.width; val h = size.height
                        val hist = state.jInfHistory
                        val maxV = hist.max().coerceAtLeast(0.01f)
                        val step = w / (hist.size - 1)
                        for (i in 1 until hist.size) {
                            val x0 = (i - 1) * step; val x1 = i * step
                            val y0 = h * (1f - hist[i - 1] / maxV)
                            val y1 = h * (1f - hist[i]     / maxV)
                            drawLine(
                                color = GibberBlue,
                                start = Offset(x0, y0),
                                end   = Offset(x1, y1),
                                strokeWidth = 2f,
                            )
                        }
                    }
                    Text("J^μ_inf history (${state.jInfHistory.size} steps)",
                        style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                }
            }
        }

        // ── Constraint monitor ────────────────────────────────────────────────
        Card(
            colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text("Constraint Monitor", style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold)
                ConstraintRow("Ricci |R| ≤ 1.5",   !state.ricciFlag)
                ConstraintRow("Gauge B_norm ≤ 3.0", !state.bFlag)
                ConstraintRow("Radion φ ≤ 1.5",     !state.phiFlag)
            }
        }

        // ── Raw sensor inputs ─────────────────────────────────────────────────
        Card(
            colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text("Sensor Inputs", style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold)
                SensorInputRow("Accel |g|",    "%.3f m/s²".format(state.accelMag))
                SensorInputRow("Mag |B|",      "%.1f µT".format(state.magMag))
                SensorInputRow("Pressure",     "%.1f hPa".format(state.pressureHpa))
                SensorInputRow("Battery",      if (state.batteryPct >= 0) "${state.batteryPct}%" else "—")
                SensorInputRow("Light",        "%.0f lux".format(state.lightLux))
            }
        }

        // ── Demo mode ─────────────────────────────────────────────────────────
        Button(
            onClick  = viewModel::runDemoStep,
            colors   = ButtonDefaults.buttonColors(containerColor = GibberBlue),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text("▶ Demo Step (synthetic sensor data)")
        }

        Text(
            "For live data: open Tricorder tab first to activate all sensors. " +
            "ManifoldProbe reads the shared SensorBridge flow.",
            style = MaterialTheme.typography.bodySmall,
            color = OnSurfaceDim,
        )
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Helper composables
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun ManifoldFieldRow(label: String, value: Float, flagged: Boolean, baseline: Float, unit: String) {
    val color = if (flagged) GibberRed else if (kotlin.math.abs(value - baseline) < 0.05f) GibberGreen else GibberAmber
    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        Text(label, style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
        Text("%.4f %s %s".format(value, unit, if (flagged) "⚠️" else ""),
            style = MaterialTheme.typography.bodySmall,
            fontWeight = FontWeight.Bold,
            color = color)
    }
}

@Composable
private fun ConstraintRow(label: String, ok: Boolean) {
    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        Text(label, style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
        Text(if (ok) "✅ OK" else "❌ VIOLATED",
            style = MaterialTheme.typography.bodySmall,
            fontWeight = FontWeight.Bold,
            color = if (ok) GibberGreen else GibberRed)
    }
}

@Composable
private fun SensorInputRow(label: String, value: String) {
    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        Text(label, style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
        Text(value, style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.Medium)
    }
}
