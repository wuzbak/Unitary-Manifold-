package com.gibbernode.feature.enviro

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
import com.gibbernode.enviro.WeatherAdvisor
import com.gibbernode.ui.GibberAmber
import com.gibbernode.ui.GibberBlue
import com.gibbernode.ui.GibberGreen
import com.gibbernode.ui.GibberRed
import com.gibbernode.ui.OnSurfaceDim
import com.gibbernode.ui.SurfaceDark

/**
 * EnviroScreen — 🌡️ Environmental Science Hub
 *
 * Sub-tabs:
 *  0 — 🌩️ Weather   : pressure trend, storm approach, tornado alert
 *  1 — 🏢 Indoor Nav: floor estimate, door-open alert, elevator monitor
 *  2 — 💡 Light Lab  : lux, circadian, plant advice, security tripwire
 */
@Composable
fun EnviroScreen(viewModel: EnviroViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    var tab   by remember { mutableIntStateOf(0) }

    Column(modifier = Modifier.fillMaxSize()) {
        ScrollableTabRow(selectedTabIndex = tab, edgePadding = 0.dp) {
            Tab(selected = tab == 0, onClick = { tab = 0 }, text = { Text("🌩️ Weather", fontSize = 13.sp) })
            Tab(selected = tab == 1, onClick = { tab = 1 }, text = { Text("🏢 Indoor Nav", fontSize = 13.sp) })
            Tab(selected = tab == 2, onClick = { tab = 2 }, text = { Text("💡 Light Lab", fontSize = 13.sp) })
        }
        when (tab) {
            0 -> WeatherTab(state, viewModel)
            1 -> IndoorNavTab(state, viewModel)
            2 -> LightLabTab(state, viewModel)
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 0 — Weather
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun WeatherTab(state: EnviroUiState, vm: EnviroViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        if (state.tornadoAlert) {
            Card(colors = CardDefaults.cardColors(containerColor = GibberRed.copy(alpha = 0.15f)), modifier = Modifier.fillMaxWidth()) {
                Text("⚠️ RAPID PRESSURE DROP — Tornado / severe inflow possible. Seek shelter.",
                    style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold,
                    color = GibberRed, modifier = Modifier.padding(16.dp))
            }
        }

        // Current pressure
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Barometric Pressure", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(4.dp))
                Text("%.1f hPa".format(state.pressureHpa), style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold, color = GibberBlue)
                state.weatherReport?.let { r ->
                    Spacer(Modifier.height(8.dp))
                    val approachColor = when (r.stormApproach) {
                        WeatherAdvisor.StormApproach.CLEAR    -> GibberGreen
                        WeatherAdvisor.StormApproach.WATCH    -> GibberAmber
                        WeatherAdvisor.StormApproach.WARNING  -> Color(0xFFFF6D00)
                        WeatherAdvisor.StormApproach.IMMINENT -> GibberRed
                    }
                    Text("${r.stormApproach.emoji} ${r.stormApproach.label}",
                        style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold, color = approachColor)
                    Text(r.summary, style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
                    r.minutesToArrival?.let { m ->
                        Spacer(Modifier.height(4.dp))
                        Text("Estimated front arrival: ~${m} min", style = MaterialTheme.typography.labelMedium, color = approachColor)
                    }
                    Spacer(Modifier.height(8.dp))
                    val trendColor = if (r.trendHpaPerHr < 0) GibberRed else GibberGreen
                    Text(
                        "Trend: %+.2f hPa/hr".format(r.trendHpaPerHr),
                        style = MaterialTheme.typography.labelMedium, color = trendColor,
                    )
                }
            }
        }

        // Pressure sparkline
        if (state.pressureHistory.size >= 2) {
            PressureSparkline(state.pressureHistory)
        }
    }
}

@Composable
private fun PressureSparkline(history: List<Pair<Long, Float>>) {
    Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Pressure trend (last ${history.size} samples)", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
            Spacer(Modifier.height(8.dp))
            Canvas(modifier = Modifier.fillMaxWidth().height(80.dp)) {
                val w = size.width; val h = size.height
                val values = history.map { it.second }
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

// ─────────────────────────────────────────────────────────────────────────────
// Tab 1 — Indoor Nav
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun IndoorNavTab(state: EnviroUiState, vm: EnviroViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        // Floor estimate
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Floor Estimate", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                state.floorEstimate?.let { fe ->
                    Text("Floor ${if (fe.floor >= 0) "+${fe.floor}" else "${fe.floor}"}",
                        style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold, color = GibberBlue)
                    Text("Δalt = %.1f m  |  conf %.0f%%".format(fe.altitudeM, fe.confidence * 100f),
                        style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                } ?: Text("Set ground-floor reference first", style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
                Spacer(Modifier.height(8.dp))
                Button(onClick = vm::setFloorReference, modifier = Modifier.fillMaxWidth()) {
                    Text("📌 Set Ground-Floor Reference")
                }
                state.pressureReferenceHpa?.let { ref ->
                    Text("Reference: %.1f hPa".format(ref), style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                }
            }
        }

        // Door / window alert
        Card(colors = CardDefaults.cardColors(
            containerColor = if (state.doorAlertTriggered) GibberRed.copy(alpha = 0.12f) else SurfaceDark
        ), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Door / Window Pressure Alert", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(4.dp))
                if (state.doorAlertTriggered) {
                    Text("🚪 Pressure spike detected — door or window opened!", style = MaterialTheme.typography.bodyMedium,
                        color = GibberRed, fontWeight = FontWeight.Bold)
                    Button(onClick = vm::clearDoorAlert, modifier = Modifier.fillMaxWidth()) { Text("Acknowledge") }
                } else {
                    Text(if (state.doorAlertArmed) "✅ Armed — listening" else "Disarmed",
                        style = MaterialTheme.typography.bodySmall, color = if (state.doorAlertArmed) GibberGreen else OnSurfaceDim)
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        if (!state.doorAlertArmed)
                            Button(onClick = vm::armDoorAlert, modifier = Modifier.weight(1f)) { Text("🔔 Arm Alert") }
                        else
                            OutlinedButton(onClick = vm::disarmDoorAlert, modifier = Modifier.weight(1f)) { Text("Disarm") }
                    }
                }
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 2 — Light Lab
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun LightLabTab(state: EnviroUiState, vm: EnviroViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        // Live lux
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Ambient Light", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(4.dp))
                Text("%.1f lux".format(state.lightLux), style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold, color = GibberAmber)
                state.circadianReport?.let { r ->
                    Spacer(Modifier.height(8.dp))
                    LightRow("Colour Temp",    "%.0f K".format(r.colorTempK))
                    LightRow("Melanopic EDI",  "%.1f lux-eq".format(r.melanopicEdi))
                    LightRow("Blue Exposure",  "%.3f µmol/m²".format(r.blueExposureUmolM2))
                    Spacer(Modifier.height(4.dp))
                    Text(r.advice, style = MaterialTheme.typography.bodySmall,
                        color = if (r.colorTempK > 5500f && state.lightLux > 50f) GibberAmber else GibberGreen)
                    Spacer(Modifier.height(4.dp))
                    TextButton(onClick = vm::resetCircadian) { Text("↺ Reset accumulator") }
                }
            }
        }

        // Plant advice
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("🌿 Plant Light Advisor", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                val pl = state.plantLightAdvice
                Text("${pl.emoji} ${pl.label}", style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold)
                Text("Examples: ${pl.examples}", style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
                Text("Range: ${pl.minLux.toInt()}–${if (pl.maxLux > 10000) "∞" else pl.maxLux.toInt()} lux",
                    style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
            }
        }

        // Security tripwire
        Card(colors = CardDefaults.cardColors(
            containerColor = if (state.tripwireTriggered) GibberRed.copy(alpha = 0.12f) else SurfaceDark
        ), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("🔦 Security Tripwire", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(4.dp))
                if (state.tripwireTriggered) {
                    Text("🚨 LIGHT CHANGE DETECTED — tripwire triggered!", style = MaterialTheme.typography.bodyMedium,
                        color = GibberRed, fontWeight = FontWeight.Bold)
                }
                Text(if (state.tripwireArmed) "✅ Armed  (sensitivity: ±${state.tripwireSensitivityLux.toInt()} lux)" else "Disarmed",
                    style = MaterialTheme.typography.bodySmall, color = if (state.tripwireArmed) GibberGreen else OnSurfaceDim)
                Spacer(Modifier.height(8.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    if (!state.tripwireArmed) {
                        Button(onClick = vm::armTripwire, modifier = Modifier.weight(1f)) { Text("🔒 Arm Tripwire") }
                    } else {
                        OutlinedButton(onClick = vm::disarmTripwire, modifier = Modifier.weight(1f)) { Text("Disarm") }
                    }
                }
            }
        }
    }
}

@Composable
private fun LightRow(label: String, value: String) {
    Row(modifier = Modifier.fillMaxWidth().padding(vertical = 2.dp)) {
        Text(label, style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim, modifier = Modifier.weight(1.2f))
        Text(value, style = MaterialTheme.typography.bodySmall, fontFamily = FontFamily.Monospace)
    }
}
