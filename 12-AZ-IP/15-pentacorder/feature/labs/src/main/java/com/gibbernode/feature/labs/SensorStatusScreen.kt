package com.gibbernode.feature.labs

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.gibbernode.ui.GibberAmber
import com.gibbernode.ui.GibberGreen
import com.gibbernode.ui.OnSurfaceDim
import com.gibbernode.ui.SurfaceDark

/**
 * SensorStatusScreen — 🌐 Raw Sensor Dashboard
 *
 * Enumerates every hardware sensor available on the device and shows live
 * readings, range, resolution, and power draw.  Phyphox / Sensor Box parity.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SensorStatusScreen(viewModel: SensorStatusViewModel = hiltViewModel()) {
    val state   by viewModel.state.collectAsStateWithLifecycle()
    val sensors  = state.filteredSensors

    Column(modifier = Modifier.fillMaxSize()) {
        // Header
        Column(modifier = Modifier.padding(horizontal = 16.dp, vertical = 10.dp)) {
            Text("🌐 Sensor Status", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
            Text("${state.sensors.size} sensors on this device",
                style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
        }

        // Search / filter
        TextField(
            value         = state.filterText,
            onValueChange = viewModel::setFilter,
            placeholder   = { Text("Filter sensors…") },
            singleLine    = true,
            modifier      = Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 4.dp),
            colors        = TextFieldDefaults.colors(),
        )

        Spacer(Modifier.height(4.dp))

        if (sensors.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text("No sensors match "${state.filterText}"",
                    style = MaterialTheme.typography.bodyMedium, color = OnSurfaceDim)
            }
        } else {
            LazyColumn(
                contentPadding      = PaddingValues(horizontal = 12.dp, vertical = 4.dp),
                verticalArrangement = Arrangement.spacedBy(6.dp),
                modifier            = Modifier.weight(1f),
            ) {
                items(sensors, key = { it.id }) { entry ->
                    SensorCard(entry)
                }
            }
        }
    }
}

@Composable
private fun SensorCard(entry: SensorEntry) {
    val hasReading = entry.tsMs > 0
    Card(
        colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment     = Alignment.Top) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(entry.name, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.SemiBold, maxLines = 1)
                    Text(entry.typeName, style = MaterialTheme.typography.labelSmall, color = GibberAmber)
                    Text("vendor: ${entry.vendor} · v${entry.version}",
                        style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                }
                // Live indicator
                Surface(
                    shape = MaterialTheme.shapes.small,
                    color = if (hasReading) GibberGreen.copy(alpha = 0.15f) else OnSurfaceDim.copy(alpha = 0.1f),
                ) {
                    Text(
                        if (hasReading) "● LIVE" else "○ —",
                        style    = MaterialTheme.typography.labelSmall,
                        color    = if (hasReading) GibberGreen else OnSurfaceDim,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                    )
                }
            }

            if (hasReading) {
                Spacer(Modifier.height(6.dp))
                Text(
                    entry.valueStr,
                    style      = MaterialTheme.typography.bodySmall,
                    fontFamily = FontFamily.Monospace,
                    maxLines   = 2,
                )
            }

            Spacer(Modifier.height(4.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                InfoChip("Range", entry.rangeStr)
                InfoChip("Res.", entry.resolutionStr)
                InfoChip("Power", entry.powerMaStr)
            }
        }
    }
}

@Composable
private fun InfoChip(label: String, value: String) {
    Column {
        Text(label, style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim, fontSize = 10.sp)
        Text(value, style = MaterialTheme.typography.labelSmall, fontFamily = FontFamily.Monospace, fontSize = 11.sp)
    }
}
