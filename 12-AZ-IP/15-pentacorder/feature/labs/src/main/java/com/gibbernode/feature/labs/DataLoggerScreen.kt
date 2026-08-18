package com.gibbernode.feature.labs

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
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
 * DataLoggerScreen — 📼 Multi-Sensor Data Logger
 *
 * Select channels, optionally set a trigger threshold, start recording, then
 * export each sensor's CSV via the clipboard or Android Share.
 * Sensor Logger / Phyphox parity.
 */
@Composable
fun DataLoggerScreen(viewModel: DataLoggerViewModel = hiltViewModel()) {
    val state     by viewModel.state.collectAsStateWithLifecycle()
    val clipboard  = LocalClipboardManager.current
    var tab       by remember { mutableIntStateOf(0) }

    Column(modifier = Modifier.fillMaxSize()) {
        ScrollableTabRow(selectedTabIndex = tab, edgePadding = 0.dp) {
            Tab(selected = tab == 0, onClick = { tab = 0 }, text = { Text("📼 Record",   fontSize = 13.sp) })
            Tab(selected = tab == 1, onClick = { tab = 1 }, text = { Text("⚙️ Configure", fontSize = 13.sp) })
            Tab(selected = tab == 2, onClick = { tab = 2 }, text = { Text("📤 Export",   fontSize = 13.sp) })
        }
        when (tab) {
            0 -> RecordTab(state, viewModel)
            1 -> ConfigureTab(state, viewModel)
            2 -> ExportTab(state, clipboard)
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 0 — Record
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun RecordTab(state: DataLoggerUiState, vm: DataLoggerViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        // Status card
        val recColor = if (state.recording) GibberRed else GibberGreen
        Card(colors = CardDefaults.cardColors(
            containerColor = recColor.copy(alpha = 0.08f)
        ), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    if (state.recording) {
                        if (state.triggerArmed) "⏳ ARMED — waiting for trigger…" else "🔴 RECORDING"
                    } else "⏹ STOPPED",
                    style     = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color     = recColor,
                )
                if (state.recording) {
                    Spacer(Modifier.height(4.dp))
                    Text("${state.rowCount} rows logged", style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
                    if (state.triggerArmed) LinearProgressIndicator(modifier = Modifier.fillMaxWidth().padding(top = 8.dp))
                }
            }
        }

        // Start / stop button
        if (!state.recording) {
            Button(
                onClick  = vm::startRecording,
                modifier = Modifier.fillMaxWidth(),
                colors   = ButtonDefaults.buttonColors(containerColor = GibberGreen),
            ) { Text("▶ Start Recording") }
        } else {
            Button(
                onClick  = vm::stopRecording,
                modifier = Modifier.fillMaxWidth(),
                colors   = ButtonDefaults.buttonColors(containerColor = GibberRed),
            ) { Text("⏹ Stop Recording") }
        }

        // Session name
        OutlinedTextField(
            value         = state.sessionName,
            onValueChange = vm::setSessionName,
            label         = { Text("Session name") },
            singleLine    = true,
            enabled       = !state.recording,
            modifier      = Modifier.fillMaxWidth(),
        )

        // Active channels summary
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Active channels (${state.enabledChannels.size})",
                    style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                if (state.enabledChannels.isEmpty()) {
                    Text("No channels selected — go to Configure tab.",
                        style = MaterialTheme.typography.bodySmall, color = GibberRed)
                } else {
                    state.enabledChannels.forEach { ch ->
                        Text("${ch.emoji} ${ch.label}", style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        }

        // Trigger summary
        if (state.triggerType != TriggerType.IMMEDIATE) {
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Trigger: ${state.triggerType.label}",
                        style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold, color = GibberAmber)
                    Text("Threshold: %.1f m/s²  (≈ %.1f g)".format(
                        state.triggerThreshold, state.triggerThreshold / 9.806f),
                        style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
                }
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 1 — Configure
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun ConfigureTab(state: DataLoggerUiState, vm: DataLoggerViewModel) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        // Channel toggles
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Channels to record", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                LogChannel.entries.forEach { ch ->
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(vertical = 2.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween,
                    ) {
                        Text("${ch.emoji}  ${ch.label}", style = MaterialTheme.typography.bodyMedium)
                        Switch(
                            checked         = ch in state.enabledChannels,
                            onCheckedChange = { vm.toggleChannel(ch) },
                            enabled         = !state.recording,
                        )
                    }
                }
            }
        }

        // Trigger config
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Experiment trigger", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                TriggerType.entries.forEach { tt ->
                    Row(modifier = Modifier.fillMaxWidth().padding(vertical = 2.dp),
                        verticalAlignment = Alignment.CenterVertically) {
                        RadioButton(
                            selected  = state.triggerType == tt,
                            onClick   = { vm.setTrigger(tt, state.triggerThreshold) },
                            enabled   = !state.recording,
                        )
                        Spacer(Modifier.width(4.dp))
                        Text(tt.label, style = MaterialTheme.typography.bodySmall)
                    }
                }
                if (state.triggerType == TriggerType.ACCEL_THRESHOLD) {
                    Spacer(Modifier.height(8.dp))
                    Text("Accel threshold: %.1f m/s²  (%.1f g)".format(
                        state.triggerThreshold, state.triggerThreshold / 9.806f),
                        style = MaterialTheme.typography.bodySmall, color = GibberAmber)
                    Slider(
                        value         = state.triggerThreshold,
                        onValueChange = { vm.setTrigger(state.triggerType, it) },
                        valueRange    = 2f..50f,
                        steps         = 47,
                        enabled       = !state.recording,
                        modifier      = Modifier.fillMaxWidth(),
                    )
                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text("2 m/s²",  style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                        Text("50 m/s²", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                    }
                }
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 2 — Export
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun ExportTab(
    state: DataLoggerUiState,
    clipboard: androidx.compose.ui.platform.ClipboardManager,
) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        if (state.exportCsvMap.isEmpty()) {
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                Text(
                    if (state.recording) "Recording in progress — stop recording to export."
                    else "No session data yet. Start and stop a recording first.",
                    style = MaterialTheme.typography.bodyMedium, color = OnSurfaceDim,
                    modifier = Modifier.padding(16.dp),
                )
            }
        } else {
            Text("Session: ${state.sessionName}", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            Text("${state.rowCount} total rows", style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
            Spacer(Modifier.height(4.dp))

            state.exportCsvMap.forEach { (channelName, csv) ->
                val lineCount = csv.lines().size - 1  // minus header
                Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark), modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Row(modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically) {
                            Column {
                                Text(channelName, style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.SemiBold)
                                Text("$lineCount rows", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                            }
                            OutlinedButton(
                                onClick = { clipboard.setText(AnnotatedString(csv)) },
                            ) { Text("📋 Copy CSV") }
                        }
                        // Preview first 2 data lines
                        val preview = csv.lines().take(3).joinToString("\n")
                        Spacer(Modifier.height(4.dp))
                        Text(preview, style = MaterialTheme.typography.labelSmall,
                            fontFamily = FontFamily.Monospace, color = OnSurfaceDim, maxLines = 3)
                    }
                }
            }

            // Copy all channels merged
            OutlinedButton(
                onClick = {
                    val all = state.exportCsvMap.entries.joinToString("\n\n") { (name, csv) ->
                        "# $name\n$csv"
                    }
                    clipboard.setText(AnnotatedString(all))
                },
                modifier = Modifier.fillMaxWidth(),
            ) { Text("📤 Copy all channels to clipboard") }
        }
    }
}
