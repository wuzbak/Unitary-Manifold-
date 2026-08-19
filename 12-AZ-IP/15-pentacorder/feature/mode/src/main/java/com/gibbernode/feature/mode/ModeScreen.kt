package com.gibbernode.feature.mode

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.GraphicEq
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Send
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Tune
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.ScrollableTabRow
import androidx.compose.material3.Slider
import androidx.compose.material3.SliderDefaults
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Tab
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.gibbernode.gibberwave.OperationalMode
import com.gibbernode.gibberwave.ParsedPayload
import com.gibbernode.gibberwave.PayloadParser
import com.gibbernode.ui.GibberAmber
import com.gibbernode.ui.GibberBlue
import com.gibbernode.ui.GibberGreen
import com.gibbernode.ui.GibberRed
import com.gibbernode.ui.OnSurfaceDim
import com.gibbernode.ui.SurfaceDark
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

// Charcoal colour for DIODE mode (dark, stealthy)
private val GibberDiode = Color(0xFF607D8B)

/**
 * ModeScreen — Transmit tab (S5 + S6)
 *
 * Material 3 ScrollableTabRow with four sub-tabs:
 *   📤 Transmit  — mode selector + broadcast input (S5 layout, S6 DIODE card)
 *   📥 Receive   — live decode feed + translator toggle
 *   🎙️ Calibrate — inline noise floor + loopback test + protocol/volume picker
 *   ⚙️ Settings  — AES-GCM BLUE encrypt toggle + key status + DIODE description
 */
@Composable
fun ModeScreen(viewModel: ModeViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    Column(modifier = Modifier.fillMaxSize()) {

        // ── Tab row ────────────────────────────────────────────────────────────
        ScrollableTabRow(
            selectedTabIndex = state.activeTab,
            edgePadding      = 16.dp,
            containerColor   = MaterialTheme.colorScheme.surface,
        ) {
            Tab(
                selected = state.activeTab == ModeUiState.TAB_TRANSMIT,
                onClick  = { viewModel.selectTab(ModeUiState.TAB_TRANSMIT) },
                text     = { Text("📤 Transmit") },
            )
            Tab(
                selected = state.activeTab == ModeUiState.TAB_RECEIVE,
                onClick  = { viewModel.selectTab(ModeUiState.TAB_RECEIVE) },
                text     = { Text("📥 Receive  (${state.decodeLog.size})") },
            )
            Tab(
                selected = state.activeTab == ModeUiState.TAB_CALIBRATE,
                onClick  = { viewModel.selectTab(ModeUiState.TAB_CALIBRATE) },
                text     = { Text("🎙️ Calibrate") },
            )
            Tab(
                selected = state.activeTab == ModeUiState.TAB_SETTINGS,
                onClick  = { viewModel.selectTab(ModeUiState.TAB_SETTINGS) },
                text     = { Text("⚙️ Settings") },
            )
        }

        HorizontalDivider()

        // ── Tab content ────────────────────────────────────────────────────────
        when (state.activeTab) {
            ModeUiState.TAB_TRANSMIT  -> TransmitTab(state, viewModel)
            ModeUiState.TAB_RECEIVE   -> ReceiveTab(state, viewModel)
            ModeUiState.TAB_CALIBRATE -> CalibrateTab(state, viewModel)
            ModeUiState.TAB_SETTINGS  -> SettingsTab(state, viewModel)
        }
    }
}

// ── Tab 0: Transmit ───────────────────────────────────────────────────────────

@Composable
private fun TransmitTab(state: ModeUiState, viewModel: ModeViewModel) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState()),
    ) {
        Spacer(Modifier.height(12.dp))

        Text("Operational Mode", style = MaterialTheme.typography.titleMedium,
             color = MaterialTheme.colorScheme.onSurface)
        Spacer(Modifier.height(8.dp))

        // Mode cards — 5 total: GREEN, RED, BLUE, AMBER + DIODE (S6)
        val row1 = listOf(OperationalMode.GREEN, OperationalMode.RED, OperationalMode.BLUE)
        val row2 = listOf(OperationalMode.AMBER, OperationalMode.DIODE)

        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            row1.forEach { mode ->
                ModeCard(mode, state.selectedMode == mode, { viewModel.selectMode(mode) }, Modifier.weight(1f))
            }
        }
        Spacer(Modifier.height(8.dp))
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            row2.forEach { mode ->
                ModeCard(mode, state.selectedMode == mode, { viewModel.selectMode(mode) }, Modifier.weight(1f))
            }
            // Spacer to keep row aligned when only 2 items
            Spacer(Modifier.weight(1f))
        }

        Spacer(Modifier.height(12.dp))

        // S6 DIODE active badge
        if (state.selectedMode == OperationalMode.DIODE) {
            DiodeActiveBadge(chunkCount = state.diodeTxChunkCount)
            Spacer(Modifier.height(8.dp))
        }

        // S5: BLUE encrypt indicator
        if (state.selectedMode == OperationalMode.BLUE && state.blueEncryptEnabled) {
            Card(
                colors = CardDefaults.cardColors(containerColor = GibberBlue.copy(alpha = 0.12f)),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Icon(Icons.Default.Lock, contentDescription = null,
                         tint = GibberBlue, modifier = Modifier.size(16.dp))
                    Spacer(Modifier.width(6.dp))
                    Text("AES-256-GCM encryption active (BLUE mode)",
                         style = MaterialTheme.typography.labelSmall, color = GibberBlue)
                }
            }
            Spacer(Modifier.height(8.dp))
        }

        Text("Encode & Broadcast", style = MaterialTheme.typography.titleMedium,
             color = MaterialTheme.colorScheme.onSurface)
        Spacer(Modifier.height(8.dp))
        Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
            OutlinedTextField(
                value         = state.broadcastInput,
                onValueChange = viewModel::onMessageInput,
                placeholder   = {
                    Text(if (state.selectedMode == OperationalMode.DIODE)
                         "Enter payload to encrypt and broadcast…"
                         else "Type a message to transmit…")
                },
                singleLine    = true,
                modifier      = Modifier.weight(1f),
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
                keyboardActions = KeyboardActions(onSend = { viewModel.broadcast() }),
                trailingIcon  = {
                    if (state.isBroadcasting) {
                        CircularProgressIndicator(modifier = Modifier.size(24.dp), strokeWidth = 2.dp)
                    } else {
                        IconButton(onClick = viewModel::broadcast) {
                            Icon(Icons.Filled.Send, contentDescription = "Send",
                                 tint = modeColor(state.selectedMode))
                        }
                    }
                },
            )
        }
        Spacer(Modifier.height(16.dp))
    }
}

// ── Tab 1: Receive ────────────────────────────────────────────────────────────

@Composable
private fun ReceiveTab(state: ModeUiState, viewModel: ModeViewModel) {
    Column(modifier = Modifier.fillMaxSize().padding(horizontal = 16.dp)) {
        Spacer(Modifier.height(12.dp))
        Row(
            modifier              = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment     = Alignment.CenterVertically,
        ) {
            Text("Live Decode Feed (${state.decodeLog.size})",
                 style = MaterialTheme.typography.titleMedium,
                 color = MaterialTheme.colorScheme.onSurface)
            Row(verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                Text("🔤 Translate", style = MaterialTheme.typography.labelSmall,
                     color = if (state.translatorEnabled) GibberAmber else OnSurfaceDim)
                Switch(
                    checked         = state.translatorEnabled,
                    onCheckedChange = { viewModel.toggleTranslator() },
                    colors          = SwitchDefaults.colors(checkedThumbColor = GibberAmber),
                )
            }
        }
        Spacer(Modifier.height(4.dp))

        if (state.decodeLog.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize().padding(top = 24.dp),
                contentAlignment = Alignment.TopCenter) {
                Text("No transmissions yet.\nPoint two devices at each other and broadcast.",
                     style = MaterialTheme.typography.bodySmall,
                     color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        } else {
            LazyColumn(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                items(state.decodeLog, key = { it.timestamp.toString() + it.payload.take(8) }) { entry ->
                    DecodeLogItem(entry, state.translatorEnabled)
                }
            }
        }
    }
}

// ── Tab 2: Calibrate ──────────────────────────────────────────────────────────

@Composable
private fun CalibrateTab(state: ModeUiState, viewModel: ModeViewModel) {
    val pulseFraction by rememberInfiniteTransition(label = "pulse").animateFloat(
        initialValue  = 0.4f,
        targetValue   = 1f,
        animationSpec = infiniteRepeatable(tween(800, easing = LinearEasing), RepeatMode.Reverse),
        label         = "pulse-alpha",
    )
    val isActive = state.calibrateStatus == CalibrateStatus.MEASURING ||
                   state.calibrateStatus == CalibrateStatus.TESTING

    Column(
        modifier            = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Spacer(Modifier.height(16.dp))

        Icon(
            imageVector = Icons.Default.GraphicEq,
            contentDescription = null,
            tint = when (state.calibrateStatus) {
                CalibrateStatus.PASSED  -> GibberGreen
                CalibrateStatus.FAILED  -> GibberAmber
                CalibrateStatus.TESTING -> GibberGreen
                else -> MaterialTheme.colorScheme.onSurfaceVariant
            },
            modifier = Modifier.size(56.dp).alpha(if (isActive) pulseFraction else 1f),
        )
        Spacer(Modifier.height(8.dp))
        Text("Audio Calibration", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
        Spacer(Modifier.height(4.dp))

        // Noise floor display
        val noiseStr = if (state.noiseFloorDb <= -98f) "Not measured"
                       else "%.0f dBFS".format(state.noiseFloorDb)
        Text("Noise floor: $noiseStr — Band: ${state.calibratedBand.label}",
             style = MaterialTheme.typography.bodySmall,
             color = MaterialTheme.colorScheme.onSurfaceVariant,
             fontFamily = FontFamily.Monospace)

        if (state.calibrateMessage.isNotEmpty()) {
            Spacer(Modifier.height(6.dp))
            Text(state.calibrateMessage,
                 style = MaterialTheme.typography.bodySmall,
                 color = when (state.calibrateStatus) {
                     CalibrateStatus.PASSED -> GibberGreen
                     CalibrateStatus.FAILED -> GibberAmber
                     else -> MaterialTheme.colorScheme.onSurfaceVariant
                 },
                 fontFamily = FontFamily.Monospace)
        }

        Spacer(Modifier.height(16.dp))

        // Action buttons
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedButton(
                onClick  = viewModel::measureNoiseFloor,
                enabled  = !isActive,
                modifier = Modifier.weight(1f),
            ) {
                Text("🎙️ Measure Noise", fontSize = 13.sp)
            }
            Button(
                onClick  = if (state.calibrateStatus == CalibrateStatus.TESTING) viewModel::cancelLoopback
                           else viewModel::runLoopback,
                enabled  = state.calibrateStatus != CalibrateStatus.MEASURING,
                modifier = Modifier.weight(1f),
                colors   = ButtonDefaults.buttonColors(
                    containerColor = if (state.calibrateStatus == CalibrateStatus.TESTING) GibberAmber else GibberGreen
                ),
            ) {
                if (state.calibrateStatus == CalibrateStatus.TESTING) {
                    CircularProgressIndicator(color = Color.White, modifier = Modifier.size(16.dp), strokeWidth = 2.dp)
                    Spacer(Modifier.width(6.dp))
                    Text("Cancel", fontSize = 13.sp)
                } else {
                    Icon(Icons.Default.PlayArrow, null, modifier = Modifier.size(16.dp))
                    Spacer(Modifier.width(4.dp))
                    Text("Loopback", fontSize = 13.sp)
                }
            }
        }

        Spacer(Modifier.height(16.dp))
        HorizontalDivider()
        Spacer(Modifier.height(12.dp))

        // Protocol picker
        Text("TX Protocol", style = MaterialTheme.typography.titleSmall,
             modifier = Modifier.fillMaxWidth())
        Spacer(Modifier.height(8.dp))
        val protocols = listOf(
            com.gibbernode.audio.TxProtocol.AUDIBLE_NORMAL   to "Audible Normal  — Robust, ~4 s/msg",
            com.gibbernode.audio.TxProtocol.AUDIBLE_FAST     to "Audible Fast  — Balanced, ~2 s/msg",
            com.gibbernode.audio.TxProtocol.AUDIBLE_FASTEST  to "Audible Fastest  — ~1 s, quiet rooms",
            com.gibbernode.audio.TxProtocol.ULTRASOUND_FAST  to "Ultrasound Fast  — 17-22 kHz (default)",
        )
        protocols.forEach { (proto, desc) ->
            val selected = state.calibratedProtocol == proto
            Card(
                onClick  = { viewModel.selectCalibrateProtocol(proto) },
                modifier = Modifier.fillMaxWidth().padding(vertical = 3.dp),
                border   = if (selected) BorderStroke(2.dp, GibberGreen)
                           else BorderStroke(1.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.3f)),
                colors   = CardDefaults.cardColors(
                    containerColor = if (selected) GibberGreen.copy(alpha = 0.1f) else SurfaceDark),
            ) {
                Row(modifier = Modifier.padding(10.dp), verticalAlignment = Alignment.CenterVertically) {
                    if (selected) Icon(Icons.Default.Check, null, tint = GibberGreen,
                                       modifier = Modifier.size(16.dp))
                    else Spacer(Modifier.size(16.dp))
                    Spacer(Modifier.width(8.dp))
                    Column {
                        Text(proto.name, style = MaterialTheme.typography.labelMedium,
                             color = if (selected) GibberGreen else MaterialTheme.colorScheme.onSurface,
                             fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal)
                        Text(desc, style = MaterialTheme.typography.labelSmall,
                             color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
            }
        }

        Spacer(Modifier.height(12.dp))
        Text("Volume: ${state.calibratedVolume}", style = MaterialTheme.typography.bodyMedium,
             color = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.fillMaxWidth())
        Slider(
            value          = state.calibratedVolume.toFloat(),
            onValueChange  = { viewModel.selectCalibrateVolume(it.toInt()) },
            valueRange     = 5f..100f,
            steps          = 18,
            colors         = SliderDefaults.colors(thumbColor = GibberGreen, activeTrackColor = GibberGreen),
        )

        Spacer(Modifier.height(12.dp))
        Button(
            onClick  = viewModel::saveCalibrateSettings,
            modifier = Modifier.fillMaxWidth(),
            colors   = ButtonDefaults.buttonColors(containerColor = GibberGreen),
        ) {
            Icon(Icons.Default.Check, null)
            Spacer(Modifier.width(6.dp))
            Text("Save Calibration", fontWeight = FontWeight.Bold)
        }
        Spacer(Modifier.height(24.dp))
    }
}

// ── Tab 3: Settings ───────────────────────────────────────────────────────────

@Composable
private fun SettingsTab(state: ModeUiState, viewModel: ModeViewModel) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState()),
    ) {
        Spacer(Modifier.height(16.dp))

        // ── AES-256-GCM BLUE encrypt toggle ───────────────────────────────────
        Text("Security", style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(8.dp))
        Card(
            colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier              = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment     = Alignment.CenterVertically,
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Lock, null, tint = GibberBlue,
                                 modifier = Modifier.size(18.dp))
                            Spacer(Modifier.width(6.dp))
                            Text("BLUE Mode Encryption", fontWeight = FontWeight.Bold)
                        }
                        Spacer(Modifier.height(4.dp))
                        Text("AES-256-GCM hardware-backed payload encryption.\n" +
                             "Enabled only in BLUE mode. Key lives in Android Keystore.",
                             style = MaterialTheme.typography.bodySmall,
                             color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    Spacer(Modifier.width(8.dp))
                    Switch(
                        checked         = state.blueEncryptEnabled,
                        onCheckedChange = { viewModel.toggleBlueEncrypt() },
                        enabled         = state.keyProvisioned,
                        colors          = SwitchDefaults.colors(checkedThumbColor = GibberBlue),
                    )
                }
                if (!state.keyProvisioned) {
                    Spacer(Modifier.height(6.dp))
                    Text("⚠ AES key not provisioned — restart the app to initialise.",
                         style = MaterialTheme.typography.labelSmall, color = GibberAmber)
                }
            }
        }

        Spacer(Modifier.height(8.dp))

        // Key status card
        Card(
            colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Column(modifier = Modifier.padding(12.dp)) {
                Text("Key Status", style = MaterialTheme.typography.labelLarge,
                     color = MaterialTheme.colorScheme.onSurfaceVariant)
                Spacer(Modifier.height(4.dp))
                KeyStatusRow("HMAC-SHA256 (session auth)", state.keyProvisioned)
                KeyStatusRow("AES-256-GCM (payload encryption)", state.keyProvisioned)
                Spacer(Modifier.height(4.dp))
                Text("Keys are hardware-backed (Android Keystore / StrongBox) and\nnever appear in app memory as raw bytes.",
                     style = MaterialTheme.typography.bodySmall,
                     color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }

        Spacer(Modifier.height(16.dp))
        HorizontalDivider()
        Spacer(Modifier.height(16.dp))

        // ── DIODE Air-Gap Bridge description (S6) ──────────────────────────────
        Text("Air-Gap Bridge (S6)", style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(8.dp))
        Card(
            colors   = CardDefaults.cardColors(containerColor = GibberDiode.copy(alpha = 0.08f)),
            border   = BorderStroke(1.dp, GibberDiode.copy(alpha = 0.4f)),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.Lock, null, tint = GibberDiode, modifier = Modifier.size(18.dp))
                    Spacer(Modifier.width(6.dp))
                    Text("🔒 DIODE Mode", fontWeight = FontWeight.Bold, color = GibberDiode)
                }
                Spacer(Modifier.height(8.dp))
                listOf(
                    "One-way logical air gap — TX only, no acoustic reply.",
                    "Every payload AES-256-GCM encrypted before transmission.",
                    "Large payloads auto-chunked into DIODE:seq:total:enc bursts.",
                    "Near-ultrasonic (17–22 kHz) — inaudible, above ambient speech.",
                    "HMAC-SHA256 wraps each chunk for replay protection.",
                    "RX assembler reassembles + decrypts, never transmits back.",
                ).forEach { line ->
                    Row(verticalAlignment = Alignment.Top, modifier = Modifier.padding(vertical = 2.dp)) {
                        Text("•  ", style = MaterialTheme.typography.bodySmall, color = GibberDiode)
                        Text(line, style = MaterialTheme.typography.bodySmall,
                             color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
            }
        }

        Spacer(Modifier.height(16.dp))
        HorizontalDivider()
        Spacer(Modifier.height(16.dp))

        // ── Calibration summary ────────────────────────────────────────────────
        Text("Current Calibration", style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(8.dp))
        Card(
            colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Column(modifier = Modifier.padding(12.dp)) {
                SettingsRow("Protocol",    state.calibratedProtocol.name)
                SettingsRow("Volume",      "${state.calibratedVolume}")
                SettingsRow("Band",        state.calibratedBand.label)
                SettingsRow("Noise floor",
                    if (state.noiseFloorDb <= -98f) "Not measured"
                    else "%.0f dBFS".format(state.noiseFloorDb))
            }
        }

        Spacer(Modifier.height(8.dp))
        OutlinedButton(
            onClick  = { },  // Recalibrate = navigate to Calibrate tab
            modifier = Modifier.fillMaxWidth(),
        ) {
            Icon(Icons.Default.Tune, null, modifier = Modifier.size(16.dp))
            Spacer(Modifier.width(6.dp))
            Text("Recalibrate → open Calibrate tab")
        }

        Spacer(Modifier.height(32.dp))
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Sub-composables
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun ModeCard(
    mode: OperationalMode,
    isSelected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val color  = modeColor(mode)
    val border = if (isSelected) BorderStroke(2.dp, color) else BorderStroke(1.dp, color.copy(alpha = 0.3f))

    Card(
        onClick  = onClick,
        border   = border,
        modifier = modifier,
        colors   = CardDefaults.cardColors(
            containerColor = if (isSelected) color.copy(alpha = 0.15f) else SurfaceDark,
        ),
        shape = RoundedCornerShape(12.dp),
    ) {
        Column(modifier = Modifier.padding(10.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            // DIODE gets a lock icon
            if (mode == OperationalMode.DIODE) {
                Icon(Icons.Default.Lock, null, tint = if (isSelected) color else color.copy(alpha = 0.5f),
                     modifier = Modifier.size(14.dp))
            }
            Text(
                text       = mode.name,
                style      = MaterialTheme.typography.labelLarge,
                color      = if (isSelected) color else MaterialTheme.colorScheme.onSurfaceVariant,
                fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
            )
            Text("vol ${mode.volume}", style = MaterialTheme.typography.labelSmall,
                 color = MaterialTheme.colorScheme.onSurfaceVariant, fontSize = 10.sp)
            Text("${mode.rangeM.toInt()} m", style = MaterialTheme.typography.labelSmall,
                 color = MaterialTheme.colorScheme.onSurfaceVariant, fontSize = 10.sp)
        }
    }
}

@Composable
private fun DiodeActiveBadge(chunkCount: Int) {
    val pulse by rememberInfiniteTransition(label = "diode-pulse").animateFloat(
        initialValue  = 0.6f,
        targetValue   = 1f,
        animationSpec = infiniteRepeatable(tween(600, easing = LinearEasing), RepeatMode.Reverse),
        label         = "alpha",
    )
    Card(
        colors   = CardDefaults.cardColors(containerColor = GibberDiode.copy(alpha = 0.12f)),
        border   = BorderStroke(1.dp, GibberDiode.copy(alpha = pulse)),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Row(
            modifier          = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(Icons.Default.Lock, null, tint = GibberDiode.copy(alpha = pulse),
                 modifier = Modifier.size(16.dp))
            Spacer(Modifier.width(8.dp))
            Column {
                Text("🔒 Air-Gap TX Active",
                     style = MaterialTheme.typography.labelMedium, color = GibberDiode,
                     fontWeight = FontWeight.Bold)
                Text(
                    text = "Payload will be AES-256-GCM encrypted + chunked over near-ultrasonic.",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                if (chunkCount > 0) {
                    Text(
                        text  = "Last TX: $chunkCount ${if (chunkCount > 1) "chunks" else "chunk"}.",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
        }
    }
}

@Composable
private fun DecodeLogItem(entry: DecodeLogEntry, showTranslation: Boolean) {
    val timeStr = SimpleDateFormat("HH:mm:ss", Locale.US).format(Date(entry.timestamp))
    val isRx    = entry.source.startsWith("RX")
    val isDiode = entry.source == "RX:DIODE" || entry.source == "TX:DIODE"

    Card(
        colors = CardDefaults.cardColors(
            containerColor = when {
                isDiode -> GibberDiode.copy(alpha = 0.08f)
                isRx    -> MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.2f)
                else    -> MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.2f)
            }
        ),
    ) {
        Row(
            modifier          = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    if (isDiode) {
                        Icon(Icons.Default.Lock, null, tint = GibberDiode,
                             modifier = Modifier.size(12.dp).padding(end = 2.dp))
                    }
                    Text(entry.payload, style = MaterialTheme.typography.bodySmall,
                         fontFamily = FontFamily.Monospace,
                         color = MaterialTheme.colorScheme.onSurface, maxLines = 2)
                }
                if (showTranslation) {
                    val human = humanize(entry.payload)
                    if (human != null) {
                        Text(human, style = MaterialTheme.typography.bodySmall, color = GibberAmber)
                    }
                }
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(entry.source, style = MaterialTheme.typography.labelSmall,
                         color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(timeStr, style = MaterialTheme.typography.labelSmall,
                         color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
            Text(
                text       = if (entry.hmacOk) "✓ AUTH" else "✗ AUTH",
                style      = MaterialTheme.typography.labelSmall,
                color      = if (entry.hmacOk) GibberGreen else GibberRed,
                fontWeight = FontWeight.Bold,
            )
        }
    }
}

@Composable
private fun KeyStatusRow(label: String, ok: Boolean) {
    Row(
        modifier              = Modifier.fillMaxWidth().padding(vertical = 2.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
    ) {
        Text(label, style = MaterialTheme.typography.bodySmall,
             color = MaterialTheme.colorScheme.onSurface)
        Text(if (ok) "✓ provisioned" else "✗ missing",
             style = MaterialTheme.typography.bodySmall,
             color = if (ok) GibberGreen else GibberAmber, fontWeight = FontWeight.Bold)
    }
}

@Composable
private fun SettingsRow(label: String, value: String) {
    Row(
        modifier              = Modifier.fillMaxWidth().padding(vertical = 2.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
    ) {
        Text(label, style = MaterialTheme.typography.bodySmall,
             color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(value, style = MaterialTheme.typography.bodySmall,
             color = MaterialTheme.colorScheme.onSurface, fontFamily = FontFamily.Monospace)
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Helpers (humanize + modeColor)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * humanize — converts a Gibberlink payload string to a plain-English description.
 * Returns null when the payload is already human-readable (no prefix).
 */
private fun humanize(payload: String): String? {
    val parsed = try { PayloadParser.parse(payload) } catch (e: Exception) {
        android.util.Log.d("Pentacorder/Translator", "Could not parse: $payload — ${e.message}")
        return null
    }
    return when (parsed) {
        is ParsedPayload.Gps -> {
            val altF = parsed.altM.toFloat()
            val altNote = when {
                altF > 3000f -> " ⚠ HIGH ALT"
                altF < -5f   -> " ⚠ UNDERGROUND"
                else -> ""
            }
            "📍 %.4f°, %.4f°  alt %.0fm  ±%.0fm  bat %d%%%s"
                .format(parsed.lat, parsed.lon, parsed.altM, parsed.accM, parsed.batPct, altNote)
        }
        is ParsedPayload.Sys -> {
            val tempNote = if (parsed.cpuTempC > 85f) " 🔥 THROTTLE" else ""
            val anomNote = if (parsed.anomalyCount > 0) "  ⚠ ${parsed.anomalyCount} anomaly" else ""
            "🖥️ ${parsed.deviceId}  CPU %.0f°C$tempNote  bat ${parsed.batPct}%%%anomNote  ${parsed.intent}"
                .format(parsed.cpuTempC)
        }
        is ParsedPayload.Env -> {
            val pressNote = when {
                parsed.pressureHpa < 980f  -> " ⚠ LOW"
                parsed.pressureHpa > 1025f -> " HIGH"
                else -> " normal"
            }
            val tempNote = when {
                parsed.tempC > 35f -> " HOT"
                parsed.tempC < 5f  -> " COLD"
                else -> ""
            }
            "🌡 %.0f hPa$pressNote  %.1f°C$tempNote  %.0f%% RH"
                .format(parsed.pressureHpa, parsed.tempC, parsed.humidityPct)
        }
        is ParsedPayload.Vitals -> {
            val hrNote = when {
                parsed.hrBpm > 130 -> " 🚨 TACHYCARDIA"
                parsed.hrBpm > 100 -> " ⚠ high"
                parsed.hrBpm in 60..100 -> ""
                parsed.hrBpm > 0 -> " ⚠ low"
                else -> ""
            }
            val spo2Note = when {
                parsed.spo2Pct < 90 -> " 🚨 HYPOXIA"
                parsed.spo2Pct < 94 -> " ⚠ low"
                else -> ""
            }
            val tempNote = when {
                parsed.tempC > 38.5f -> " fever"
                parsed.tempC < 36f   -> " hypothermic"
                else -> ""
            }
            "❤️ HR ${parsed.hrBpm} bpm$hrNote  SpO₂ ${parsed.spo2Pct}%$spo2Note  %.1f°C$tempNote"
                .format(parsed.tempC)
        }
        is ParsedPayload.Mnft    -> "🔌 Manifest: ${parsed.raw.take(60)}"
        is ParsedPayload.Intent  -> "🔗 ${parsed.intent.name} from ${parsed.source.name}: ${parsed.payload.take(60)}"
        is ParsedPayload.Energy  -> "⚡ Energy: ${parsed.raw.take(60)}"
        is ParsedPayload.Spatial -> "📡 Spatial: ${parsed.raw.take(60)}"
        is ParsedPayload.Alert   -> {
            val isSos = parsed.code.startsWith("SOS") || parsed.code.startsWith("MAYDAY")
            "${if (isSos) "🆘" else "🚨"} ALERT [${parsed.code}]: ${parsed.message}"
        }
        is ParsedPayload.Translate -> "🔤 ${parsed.sourceProtocol}→${parsed.targetLang}: ${parsed.inputText.take(60)}"
        is ParsedPayload.Allergy   -> {
            val sevIcon = when (parsed.severity) { "SEVERE" -> "🚨"; "MODERATE" -> "⚠"; else -> "ℹ" }
            "$sevIcon Allergy ${parsed.severity}: ${parsed.allergensCsv}"
        }
        is ParsedPayload.Consent -> "✅ Consent: ${parsed.action} by ${parsed.operatorId}"
        is ParsedPayload.Raw     -> null
    }
}

private fun modeColor(mode: OperationalMode): Color = when (mode) {
    OperationalMode.GREEN -> GibberGreen
    OperationalMode.RED   -> GibberRed
    OperationalMode.BLUE  -> GibberBlue
    OperationalMode.AMBER -> GibberAmber
    OperationalMode.DIODE -> GibberDiode
}
