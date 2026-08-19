package com.gibbernode.feature.registry

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Divider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontFamily
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
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import kotlin.math.abs
import kotlin.math.sqrt

/**
 * RegistryScreen — Tab 3
 *
 * Shows:
 *  - Live sensor gauges (GPS, accelerometer, barometer, HR, SpO2)
 *  - Energy panel (battery %, battery temp)
 *  - Accessory registry (MNFT devices)
 */
@Composable
fun RegistryScreen(viewModel: RegistryViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {

        // ── GPS ────────────────────────────────────────────────────────────
        SectionCard(title = "📍 GPS Location") {
            GaugeRow("Latitude",   formatCoord(state.latitude),  GibberBlue)
            GaugeRow("Longitude",  formatCoord(state.longitude), GibberBlue)
            GaugeRow("Altitude",   "%.1f m".format(state.altitude), GibberBlue)
            GaugeRow("Accuracy",   "±%.1f m".format(state.gpsAccM), GibberBlue)
        }

        // ── Accelerometer ─────────────────────────────────────────────────
        SectionCard(title = "📐 Accelerometer") {
            val magnitude = sqrt(
                state.accelX * state.accelX +
                state.accelY * state.accelY +
                state.accelZ * state.accelZ
            )
            GaugeRow("X", "%.2f m/s²".format(state.accelX), GibberGreen)
            GaugeRow("Y", "%.2f m/s²".format(state.accelY), GibberGreen)
            GaugeRow("Z", "%.2f m/s²".format(state.accelZ), GibberGreen)
            GaugeRow("|a|", "%.2f m/s²".format(magnitude),
                if (abs(magnitude - 9.8f) > 2f) GibberAmber else GibberGreen)
        }

        // ── Environment ───────────────────────────────────────────────────
        SectionCard(title = "🌡 Environment") {
            GaugeRow("Pressure",   if (state.pressureHpa > 0) "%.1f hPa".format(state.pressureHpa) else "—", GibberBlue)
            GaugeRow("Temp",       if (state.ambientTempC != 0f) "%.1f °C".format(state.ambientTempC) else "—", GibberBlue)
            GaugeRow("Humidity",   if (state.humidityPct > 0) "%.0f%%".format(state.humidityPct) else "—", GibberBlue)
        }

        // ── Biometrics ────────────────────────────────────────────────────
        SectionCard(title = "❤️ Biometrics") {
            GaugeRow("Heart Rate", if (state.heartRateBpm > 0) "${state.heartRateBpm} bpm" else "—",
                when {
                    state.heartRateBpm > 100 -> GibberRed
                    state.heartRateBpm > 0   -> GibberGreen
                    else                     -> OnSurfaceDim
                })
        }

        // ── Energy ────────────────────────────────────────────────────────
        SectionCard(title = "🔋 Energy") {
            GaugeRow("Battery",    if (state.batteryPct >= 0) "${state.batteryPct}%" else "—",
                when {
                    state.batteryPct in 0..15  -> GibberRed
                    state.batteryPct in 16..30 -> GibberAmber
                    else                        -> GibberGreen
                })
            GaugeRow("Bat. Temp",  if (state.batteryTempC > 0) "%.1f °C".format(state.batteryTempC) else "—",
                when {
                    state.batteryTempC > 40 -> GibberRed
                    state.batteryTempC > 35 -> GibberAmber
                    else                    -> GibberGreen
                })
        }

        // ── Accessory Registry ────────────────────────────────────────────
        SectionCard(title = "🔌 Accessory Registry (${state.accessories.size})") {
            if (state.accessories.isEmpty()) {
                Text(
                    text  = "No MNFT accessories discovered yet.\nConnect a USB-OTG sensor or run the Pylon ping.",
                    style = MaterialTheme.typography.bodySmall,
                    color = OnSurfaceDim,
                )
            } else {
                state.accessories.forEach { acc ->
                    Divider(color = MaterialTheme.colorScheme.outline, thickness = 0.5.dp)
                    Spacer(Modifier.height(6.dp))
                    Row(
                        modifier              = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment     = Alignment.CenterVertically,
                    ) {
                        Column {
                            Text(
                                text  = acc.deviceId,
                                style = MaterialTheme.typography.bodyMedium,
                                color = GibberGreen,
                                fontWeight = FontWeight.Bold,
                            )
                            Text(
                                text  = acc.rawManifest.take(60),
                                style = MaterialTheme.typography.labelSmall,
                                fontFamily = FontFamily.Monospace,
                                color = OnSurfaceDim,
                            )
                        }
                        Text(
                            text  = SimpleDateFormat("HH:mm:ss", Locale.US)
                                        .format(Date(acc.lastSeenMs)),
                            style = MaterialTheme.typography.labelSmall,
                            color = OnSurfaceDim,
                        )
                    }
                    Spacer(Modifier.height(6.dp))
                }
            }
        }

        Spacer(Modifier.height(24.dp))
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Shared sub-composables
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun SectionCard(title: String, content: @Composable () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text  = title,
                style = MaterialTheme.typography.titleSmall,
                color = MaterialTheme.colorScheme.onSurface,
                fontWeight = FontWeight.Bold,
            )
            Spacer(Modifier.height(10.dp))
            content()
        }
    }
}

@Composable
private fun GaugeRow(label: String, value: String, valueColor: androidx.compose.ui.graphics.Color) {
    Row(
        modifier              = Modifier.fillMaxWidth().padding(vertical = 2.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment     = Alignment.CenterVertically,
    ) {
        Text(
            text  = label,
            style = MaterialTheme.typography.bodySmall,
            color = OnSurfaceDim,
        )
        Text(
            text       = value,
            style      = MaterialTheme.typography.bodySmall,
            fontFamily = FontFamily.Monospace,
            color      = valueColor,
            fontWeight = FontWeight.Medium,
        )
    }
}

private fun formatCoord(d: Double): String =
    if (d == 0.0) "—" else "%.6f".format(d)
