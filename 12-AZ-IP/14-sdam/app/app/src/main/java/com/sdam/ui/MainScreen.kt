package com.sdam.ui

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
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
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
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
import androidx.compose.material3.OutlinedCard
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.ScrollableTabRow
import androidx.compose.material3.Slider
import androidx.compose.material3.Switch
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
import com.sdam.audio.TxProtocol
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

private val SdamGreen  = Color(0xFF00C853)
private val SdamRed    = Color(0xFFFF1744)
private val SdamBlue   = Color(0xFF2979FF)
private val SdamDiode  = Color(0xFF607D8B)
private val OnSurfaceDim = Color(0xFF8B949E)

/**
 * MainScreen — SDAM 4-tab interface (S5 + S6)
 *
 * Tab 0 📤 Transmit  — mode selector (STANDARD/SECURE/DIODE) + message input + send
 * Tab 1 📥 Receive   — live decode feed with HMAC status
 * Tab 2 🎙️ Calibrate — noise floor measurement + loopback test + protocol/volume picker
 * Tab 3 ⚙️ Settings  — key status + debug mode + about
 */
@Composable
fun MainScreen(viewModel: MainViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    Column(modifier = Modifier.fillMaxSize()) {

        ScrollableTabRow(
            selectedTabIndex = state.activeTab,
            edgePadding      = 16.dp,
            containerColor   = MaterialTheme.colorScheme.surface,
        ) {
            Tab(
                selected = state.activeTab == MainUiState.TAB_TRANSMIT,
                onClick  = { viewModel.selectTab(MainUiState.TAB_TRANSMIT) },
                text     = { Text("📤 Transmit") },
            )
            Tab(
                selected = state.activeTab == MainUiState.TAB_RECEIVE,
                onClick  = { viewModel.selectTab(MainUiState.TAB_RECEIVE) },
                text     = { Text("📥 Receive (${state.decodeLog.size})") },
            )
            Tab(
                selected = state.activeTab == MainUiState.TAB_CALIBRATE,
                onClick  = { viewModel.selectTab(MainUiState.TAB_CALIBRATE) },
                icon     = { Icon(Icons.Default.Tune, contentDescription = null, modifier = Modifier.size(18.dp)) },
                text     = { Text("Calibrate") },
            )
            Tab(
                selected = state.activeTab == MainUiState.TAB_SETTINGS,
                onClick  = { viewModel.selectTab(MainUiState.TAB_SETTINGS) },
                icon     = { Icon(Icons.Default.Settings, contentDescription = null, modifier = Modifier.size(18.dp)) },
                text     = { Text("Settings") },
            )
        }

        HorizontalDivider()

        when (state.activeTab) {
            MainUiState.TAB_TRANSMIT  -> TransmitTab(state, viewModel)
            MainUiState.TAB_RECEIVE   -> ReceiveTab(state)
            MainUiState.TAB_CALIBRATE -> CalibrateTab(state, viewModel)
            MainUiState.TAB_SETTINGS  -> SettingsTab(state, viewModel)
        }
    }
}

// ── Tab 0: Transmit ───────────────────────────────────────────────────────────

@Composable
private fun TransmitTab(state: MainUiState, viewModel: MainViewModel) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState()),
    ) {
        Spacer(Modifier.height(12.dp))

        Text(
            "Transmit Mode",
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.onSurface,
        )
        Spacer(Modifier.height(8.dp))

        // Mode selector row
        Row(
            modifier              = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            TransmitMode.entries.forEach { mode ->
                ModeCard(
                    mode     = mode,
                    selected = state.selectedMode == mode,
                    onClick  = { viewModel.selectMode(mode) },
                    modifier = Modifier.weight(1f),
                )
            }
        }

        Spacer(Modifier.height(12.dp))

        // DIODE active badge
        if (state.selectedMode == TransmitMode.DIODE) {
            DiodeBadge(chunkCount = state.diodeTxChunkCount)
            Spacer(Modifier.height(8.dp))
        }

        // SECURE mode indicator
        if (state.selectedMode == TransmitMode.SECURE) {
            Card(
                colors   = CardDefaults.cardColors(containerColor = SdamBlue.copy(alpha = 0.12f)),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Row(
                    modifier          = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Icon(
                        Icons.Default.Lock,
                        contentDescription = null,
                        tint               = SdamBlue,
                        modifier           = Modifier.size(16.dp),
                    )
                    Spacer(Modifier.width(6.dp))
                    Text(
                        "AES-256-GCM + HMAC-SHA256 active",
                        style = MaterialTheme.typography.labelSmall,
                        color = SdamBlue,
                    )
                }
            }
            Spacer(Modifier.height(8.dp))
        }

        Text(
            "Encode & Broadcast",
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.onSurface,
        )
        Spacer(Modifier.height(8.dp))

        OutlinedTextField(
            value         = state.broadcastInput,
            onValueChange = viewModel::onMessageInput,
            placeholder   = {
                Text(
                    if (state.selectedMode == TransmitMode.DIODE)
                        "Enter payload to encrypt and transmit…"
                    else
                        "Type a message to transmit…"
                )
            },
            singleLine    = true,
            modifier      = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
            keyboardActions = KeyboardActions(onSend = { viewModel.broadcast() }),
            trailingIcon  = {
                if (state.isBroadcasting) {
                    BroadcastingIndicator(modeColor(state.selectedMode))
                } else {
                    IconButton(onClick = viewModel::broadcast) {
                        Icon(
                            Icons.Filled.Send,
                            contentDescription = "Send",
                            tint               = modeColor(state.selectedMode),
                        )
                    }
                }
            },
        )
        Spacer(Modifier.height(16.dp))
    }
}

@Composable
private fun ModeCard(
    mode:     TransmitMode,
    selected: Boolean,
    onClick:  () -> Unit,
    modifier: Modifier = Modifier,
) {
    val color = modeColor(mode)
    OutlinedCard(
        onClick  = onClick,
        modifier = modifier,
        border   = BorderStroke(
            width = if (selected) 2.dp else 1.dp,
            color = if (selected) color else OnSurfaceDim.copy(alpha = 0.4f),
        ),
        colors   = CardDefaults.outlinedCardColors(
            containerColor = if (selected) color.copy(alpha = 0.10f) else Color.Transparent,
        ),
    ) {
        Column(
            modifier              = Modifier.padding(vertical = 10.dp, horizontal = 6.dp),
            horizontalAlignment   = Alignment.CenterHorizontally,
        ) {
            Text(
                modeEmoji(mode),
                fontSize = 20.sp,
            )
            Spacer(Modifier.height(2.dp))
            Text(
                mode.displayName,
                style     = MaterialTheme.typography.labelSmall,
                color     = if (selected) color else OnSurfaceDim,
                fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal,
            )
        }
    }
}

@Composable
private fun DiodeBadge(chunkCount: Int) {
    val pulse = rememberInfiniteTransition(label = "diode_pulse")
    val alpha by pulse.animateFloat(
        initialValue   = 0.5f,
        targetValue    = 1.0f,
        animationSpec  = infiniteRepeatable(
            animation  = tween(800, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse,
        ),
        label          = "pulse_alpha",
    )
    Card(
        colors   = CardDefaults.cardColors(containerColor = SdamDiode.copy(alpha = 0.15f)),
        modifier = Modifier.fillMaxWidth().alpha(alpha),
    ) {
        Row(
            modifier          = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text("🔒", fontSize = 14.sp)
            Spacer(Modifier.width(6.dp))
            Text(
                if (chunkCount > 0)
                    "DIODE mode — last TX: $chunkCount chunk${if (chunkCount != 1) "s" else ""}"
                else
                    "DIODE mode — Air-Gap Encrypted Acoustic Data Diode",
                style = MaterialTheme.typography.labelSmall,
                color = SdamDiode,
            )
        }
    }
}

@Composable
private fun BroadcastingIndicator(color: Color) {
    val pulse = rememberInfiniteTransition(label = "tx_pulse")
    val alpha by pulse.animateFloat(
        initialValue  = 0.3f,
        targetValue   = 1.0f,
        animationSpec = infiniteRepeatable(
            animation  = tween(500, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse,
        ),
        label         = "tx_alpha",
    )
    CircularProgressIndicator(
        modifier   = Modifier.size(24.dp).alpha(alpha),
        strokeWidth = 2.dp,
        color       = color,
    )
}

// ── Tab 1: Receive ────────────────────────────────────────────────────────────

@Composable
private fun ReceiveTab(state: MainUiState) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp),
    ) {
        Spacer(Modifier.height(12.dp))
        Text(
            "Live Decode Feed (${state.decodeLog.size})",
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.onSurface,
        )
        Spacer(Modifier.height(8.dp))

        if (state.decodeLog.isEmpty()) {
            Text(
                "Listening… (start AcousticModemService to decode)",
                style = MaterialTheme.typography.bodySmall,
                color = OnSurfaceDim,
            )
        } else {
            LazyColumn(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                items(state.decodeLog) { entry ->
                    DecodeLogCard(entry)
                }
            }
        }
    }
}

@Composable
private fun DecodeLogCard(entry: DecodeEntry) {
    val fmt = SimpleDateFormat("HH:mm:ss", Locale.getDefault())
    val timeStr = fmt.format(Date(entry.timestamp))
    val hmacColor = if (entry.hmacOk) SdamGreen else SdamRed
    val hmacLabel = if (entry.hmacOk) "✓" else "✗"

    Card(
        colors   = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(modifier = Modifier.padding(10.dp)) {
            Row(
                modifier              = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment     = Alignment.CenterVertically,
            ) {
                Text(
                    "$timeStr  ${entry.source}",
                    style  = MaterialTheme.typography.labelSmall,
                    color  = OnSurfaceDim,
                    fontFamily = FontFamily.Monospace,
                )
                Text(
                    hmacLabel,
                    style = MaterialTheme.typography.labelSmall,
                    color = hmacColor,
                    fontWeight = FontWeight.Bold,
                )
            }
            Spacer(Modifier.height(4.dp))
            Text(
                entry.payload,
                style      = MaterialTheme.typography.bodySmall,
                color      = MaterialTheme.colorScheme.onSurface,
                fontFamily = FontFamily.Monospace,
            )
        }
    }
}

// ── Tab 2: Calibrate ──────────────────────────────────────────────────────────

@Composable
private fun CalibrateTab(state: MainUiState, viewModel: MainViewModel) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState()),
    ) {
        Spacer(Modifier.height(12.dp))

        Text(
            "Noise Floor Measurement",
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.onSurface,
        )
        Spacer(Modifier.height(8.dp))

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(
                onClick  = viewModel::measureNoiseFloor,
                enabled  = state.calibrateStatus == CalibrateStatus.IDLE ||
                           state.calibrateStatus == CalibrateStatus.PASSED ||
                           state.calibrateStatus == CalibrateStatus.FAILED,
                colors   = ButtonDefaults.buttonColors(containerColor = SdamGreen),
                modifier = Modifier.weight(1f),
            ) {
                Text("Measure (~1s)")
            }
            OutlinedButton(
                onClick  = viewModel::runLoopback,
                enabled  = state.calibrateStatus == CalibrateStatus.IDLE ||
                           state.calibrateStatus == CalibrateStatus.PASSED ||
                           state.calibrateStatus == CalibrateStatus.FAILED,
                modifier = Modifier.weight(1f),
            ) {
                Icon(Icons.Default.PlayArrow, contentDescription = null, modifier = Modifier.size(16.dp))
                Spacer(Modifier.width(4.dp))
                Text("Loopback Test")
            }
        }

        if (state.calibrateStatus == CalibrateStatus.MEASURING ||
            state.calibrateStatus == CalibrateStatus.TESTING) {
            Spacer(Modifier.height(8.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                CircularProgressIndicator(modifier = Modifier.size(18.dp), strokeWidth = 2.dp)
                Spacer(Modifier.width(8.dp))
                Text(state.calibrateMessage, style = MaterialTheme.typography.bodySmall)
            }
            Spacer(Modifier.height(4.dp))
            OutlinedButton(onClick = viewModel::cancelLoopback) { Text("Cancel") }
        }

        if (state.calibrateMessage.isNotEmpty() &&
            state.calibrateStatus != CalibrateStatus.MEASURING &&
            state.calibrateStatus != CalibrateStatus.TESTING) {
            Spacer(Modifier.height(8.dp))
            val msgColor = when (state.calibrateStatus) {
                CalibrateStatus.PASSED -> SdamGreen
                CalibrateStatus.FAILED -> SdamRed
                else                   -> MaterialTheme.colorScheme.onSurface
            }
            Text(state.calibrateMessage, style = MaterialTheme.typography.bodySmall, color = msgColor)
        }

        Spacer(Modifier.height(16.dp))
        HorizontalDivider()
        Spacer(Modifier.height(12.dp))

        Text(
            "Protocol & Volume",
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.onSurface,
        )
        Spacer(Modifier.height(8.dp))

        // Protocol picker
        Text(
            "Protocol: ${state.calibratedProtocol.name}  (band: ${state.calibratedBand.label})",
            style = MaterialTheme.typography.bodySmall,
            color = OnSurfaceDim,
        )
        Spacer(Modifier.height(6.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            listOf(
                TxProtocol.AUDIBLE_NORMAL,
                TxProtocol.AUDIBLE_FAST,
                TxProtocol.ULTRASOUND_FAST,
            ).forEach { proto ->
                val selected = state.calibratedProtocol == proto
                OutlinedButton(
                    onClick = { viewModel.selectCalibrateProtocol(proto) },
                    border  = BorderStroke(
                        if (selected) 2.dp else 1.dp,
                        if (selected) SdamGreen else OnSurfaceDim.copy(alpha = 0.4f),
                    ),
                    modifier = Modifier.weight(1f),
                ) {
                    Text(
                        proto.name.replace("AUDIBLE_", "AUD-").replace("ULTRASOUND_", "US-"),
                        style = MaterialTheme.typography.labelSmall,
                        color = if (selected) SdamGreen else OnSurfaceDim,
                    )
                }
            }
        }

        Spacer(Modifier.height(12.dp))

        // Volume slider
        Text(
            "Volume: ${state.calibratedVolume}%",
            style = MaterialTheme.typography.bodySmall,
            color = OnSurfaceDim,
        )
        Slider(
            value         = state.calibratedVolume.toFloat(),
            onValueChange = { viewModel.selectCalibrateVolume(it.toInt()) },
            valueRange    = 10f..100f,
            steps         = 8,
            modifier      = Modifier.fillMaxWidth(),
        )

        Spacer(Modifier.height(12.dp))

        Button(
            onClick  = viewModel::saveCalibrateSettings,
            colors   = ButtonDefaults.buttonColors(containerColor = SdamBlue),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Icon(Icons.Default.Check, contentDescription = null, modifier = Modifier.size(16.dp))
            Spacer(Modifier.width(6.dp))
            Text("Save Calibration")
        }

        Spacer(Modifier.height(16.dp))
    }
}

// ── Tab 3: Settings ───────────────────────────────────────────────────────────

@Composable
private fun SettingsTab(state: MainUiState, viewModel: MainViewModel) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp)
            .verticalScroll(rememberScrollState()),
    ) {
        Spacer(Modifier.height(12.dp))

        Text(
            "Keystore Status",
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.onSurface,
        )
        Spacer(Modifier.height(8.dp))
        Card(
            colors   = CardDefaults.cardColors(
                containerColor = if (state.keyProvisioned)
                    SdamGreen.copy(alpha = 0.10f) else SdamRed.copy(alpha = 0.10f)
            ),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Row(
                modifier          = Modifier.padding(12.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Icon(
                    Icons.Default.Lock,
                    contentDescription = null,
                    tint               = if (state.keyProvisioned) SdamGreen else SdamRed,
                    modifier           = Modifier.size(20.dp),
                )
                Spacer(Modifier.width(8.dp))
                Column {
                    Text(
                        if (state.keyProvisioned) "AES-256-GCM key provisioned" else "Key NOT provisioned",
                        style      = MaterialTheme.typography.bodySmall,
                        color      = if (state.keyProvisioned) SdamGreen else SdamRed,
                        fontWeight = FontWeight.Bold,
                    )
                    Text(
                        if (state.keyProvisioned)
                            "Hardware-backed Android Keystore key ready.\nHMAC-SHA256 session auth active."
                        else
                            "Keys will be generated on next launch.",
                        style = MaterialTheme.typography.labelSmall,
                        color = OnSurfaceDim,
                    )
                }
            }
        }

        Spacer(Modifier.height(16.dp))
        HorizontalDivider()
        Spacer(Modifier.height(12.dp))

        Text(
            "DIODE Mode (Air-Gap Bridge)",
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.onSurface,
        )
        Spacer(Modifier.height(8.dp))
        Text(
            "Select DIODE in the Transmit tab to activate the S6 Encrypted Acoustic " +
            "Data Diode mode.\n\n" +
            "Payloads are split into AES-256-GCM encrypted 32-char chunks. Each chunk " +
            "is independently encrypted with a random IV — a tampered chunk cannot " +
            "reveal adjacent plaintext.\n\n" +
            "Use for: SCIFs, air-gapped industrial control systems, RF-denied environments.",
            style = MaterialTheme.typography.bodySmall,
            color = OnSurfaceDim,
        )

        Spacer(Modifier.height(16.dp))
        HorizontalDivider()
        Spacer(Modifier.height(12.dp))

        Text(
            "Debug",
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.onSurface,
        )
        Spacer(Modifier.height(8.dp))
        Row(
            modifier              = Modifier.fillMaxWidth(),
            verticalAlignment     = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    "Debug mode (plaintext acoustic)",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurface,
                )
                Text(
                    "Disables AES-256-GCM for SECURE mode. Never use in production.",
                    style = MaterialTheme.typography.labelSmall,
                    color = SdamRed.copy(alpha = 0.8f),
                )
            }
            Switch(
                checked         = state.debugMode,
                onCheckedChange = { viewModel.toggleDebugMode() },
            )
        }

        Spacer(Modifier.height(16.dp))
        HorizontalDivider()
        Spacer(Modifier.height(12.dp))

        Text(
            "About",
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.onSurface,
        )
        Spacer(Modifier.height(6.dp))
        Text(
            "SDAM — Software-Defined Acoustic Modem\n" +
            "Version 1.0.0  •  MIT Licence\n\n" +
            "Acoustic protocol: ggwave v0.4.2 (FSK)\n" +
            "Crypto: AES-256-GCM + HMAC-SHA256 (Android Keystore)\n" +
            "Default band: 17–22 kHz near-ultrasonic\n\n" +
            "∇_μ J^μ_inf = 0",
            style      = MaterialTheme.typography.bodySmall,
            color      = OnSurfaceDim,
            fontFamily = FontFamily.Monospace,
        )
        Spacer(Modifier.height(16.dp))
    }
}

// ── Helpers ───────────────────────────────────────────────────────────────────

private fun modeColor(mode: TransmitMode): Color = when (mode) {
    TransmitMode.STANDARD -> SdamGreen
    TransmitMode.SECURE   -> SdamBlue
    TransmitMode.DIODE    -> SdamDiode
}

private fun modeEmoji(mode: TransmitMode): String = when (mode) {
    TransmitMode.STANDARD -> "📡"
    TransmitMode.SECURE   -> "🔐"
    TransmitMode.DIODE    -> "🔒"
}
