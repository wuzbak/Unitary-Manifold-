package com.gibbernode

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.selection.SelectionContainer
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.ContentCopy
import androidx.compose.material.icons.filled.Send
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Divider
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.SheetState
import androidx.compose.material3.SuggestionChip
import androidx.compose.material3.SuggestionChipDefaults
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.gibbernode.gibberwave.AssistantAction
import com.gibbernode.gibberwave.MonitoringJob
import com.gibbernode.ui.GibberAmber
import com.gibbernode.ui.GibberBlue
import com.gibbernode.ui.GibberGreen
import com.gibbernode.ui.GibberRed
import com.gibbernode.ui.OnSurfaceDim
import com.gibbernode.ui.SurfaceDark

// ─────────────────────────────────────────────────────────────────────────────
// AssistantSheet — Clippy-style bottom sheet chat
// ─────────────────────────────────────────────────────────────────────────────

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AssistantSheet(
    vm:         AssistantViewModel,
    state:      AssistantUiState,
    sheetState: SheetState,
    onDismiss:  () -> Unit,
) {
    var showSettings by remember { mutableStateOf(false) }

    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState       = sheetState,
        containerColor   = SurfaceDark,
        modifier         = Modifier
            .imePadding()
            .navigationBarsPadding(),
    ) {
        Column(modifier = Modifier.fillMaxWidth()) {

            // ── Header ────────────────────────────────────────────────────────
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 6.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment     = Alignment.CenterVertically,
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(32.dp)
                            .clip(CircleShape)
                            .background(GibberAmber.copy(alpha = 0.15f)),
                        contentAlignment = Alignment.Center,
                    ) {
                        Icon(Icons.Filled.AutoAwesome, contentDescription = null, tint = GibberAmber,
                            modifier = Modifier.size(18.dp))
                    }
                    Spacer(Modifier.width(8.dp))
                    Column {
                        Text(
                            "Pentacorder Assistant",
                            style      = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold,
                            color      = GibberAmber,
                        )
                        Text(
                            "Coherence: ${"%.2f".format(state.pentad.situationCoherence)} — " +
                            "φ₁=${"%.2f".format(state.pentad.phiUniv)} " +
                            "φ₂=${"%.2f".format(state.pentad.phiBrain)} " +
                            "φ₃=${"%.2f".format(state.pentad.phiHuman)}",
                            style = MaterialTheme.typography.labelSmall,
                            color = OnSurfaceDim,
                        )
                    }
                }
                Row {
                    IconButton(onClick = { showSettings = !showSettings }) {
                        Icon(Icons.Filled.Settings, contentDescription = "Settings", tint = OnSurfaceDim,
                            modifier = Modifier.size(20.dp))
                    }
                    IconButton(onClick = onDismiss) {
                        Icon(Icons.Filled.Close, contentDescription = "Close", tint = OnSurfaceDim,
                            modifier = Modifier.size(20.dp))
                    }
                }
            }

            // ── Coherence bar ─────────────────────────────────────────────────
            val coherence = state.pentad.situationCoherence
            LinearProgressIndicator(
                progress         = coherence,
                modifier         = Modifier.fillMaxWidth().height(2.dp),
                color            = when {
                    coherence >= 0.8f -> GibberGreen
                    coherence >= 0.6f -> GibberAmber
                    else              -> GibberRed
                },
                trackColor       = MaterialTheme.colorScheme.surface,
            )

            // ── Settings panel ────────────────────────────────────────────────
            AnimatedVisibility(
                visible = showSettings,
                enter   = slideInVertically() + fadeIn(),
                exit    = slideOutVertically() + fadeOut(),
            ) {
                ApiSettingsPanel(vm = vm, onClose = { showSettings = false })
            }

            Divider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f))

            // ── Message list ──────────────────────────────────────────────────
            val listState = rememberLazyListState()
            LaunchedEffect(state.messages.size) {
                if (state.messages.isNotEmpty()) {
                    listState.animateScrollToItem(state.messages.size - 1)
                }
            }

            LazyColumn(
                state    = listState,
                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(min = 200.dp, max = 440.dp)
                    .padding(horizontal = 12.dp, vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                items(state.messages, key = { it.id }) { msg ->
                    MessageBubble(msg = msg, onAction = vm::executeAction)
                }
                if (state.isLoading) {
                    item {
                        Row(
                            modifier = Modifier.fillMaxWidth().padding(8.dp),
                            horizontalArrangement = Arrangement.Start,
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            CircularProgressIndicator(
                                modifier   = Modifier.size(16.dp),
                                strokeWidth = 2.dp,
                                color       = GibberAmber,
                            )
                            Spacer(Modifier.width(8.dp))
                            Text("Thinking…", style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
                        }
                    }
                }
            }

            Divider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f))

            // ── Quick suggestion chips ────────────────────────────────────────
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState())
                    .padding(horizontal = 12.dp, vertical = 4.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                listOf(
                    "What's my Pentad state?",
                    "Interpret sensors",
                    "Watch battery",
                    "Monitor pressure",
                    "Explain φ_brain",
                    "Help",
                ).forEach { suggestion ->
                    SuggestionChip(
                        onClick = {
                            vm.onInputChanged(suggestion)
                            vm.sendMessage()
                        },
                        label  = { Text(suggestion, style = MaterialTheme.typography.labelSmall) },
                        colors = SuggestionChipDefaults.suggestionChipColors(
                            containerColor = GibberAmber.copy(alpha = 0.08f),
                        ),
                    )
                }
            }

            // ── Active monitoring jobs ────────────────────────────────────────
            if (state.activeJobs.isNotEmpty()) {
                Divider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f))
                ActiveMonitorsSection(jobs = state.activeJobs, onStop = { jobId ->
                    vm.executeAction(AssistantAction.StopMonitoring(jobId))
                })
            }

            // ── Input row ─────────────────────────────────────────────────────
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 12.dp, vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                OutlinedTextField(
                    value         = state.input,
                    onValueChange = vm::onInputChanged,
                    placeholder   = { Text("Ask anything…", style = MaterialTheme.typography.bodySmall) },
                    modifier      = Modifier.weight(1f),
                    maxLines      = 3,
                    singleLine    = false,
                )
                IconButton(
                    onClick  = vm::sendMessage,
                    enabled  = state.input.isNotBlank() && !state.isLoading,
                    modifier = Modifier
                        .clip(CircleShape)
                        .background(
                            if (state.input.isNotBlank()) GibberAmber else GibberAmber.copy(alpha = 0.2f)
                        ),
                ) {
                    Icon(Icons.Filled.Send, contentDescription = "Send", tint = Color.Black,
                        modifier = Modifier.size(20.dp))
                }
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Message bubble
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun MessageBubble(
    msg:      ChatMessage,
    onAction: (AssistantAction) -> Unit,
) {
    val isUser = msg.role == MessageRole.USER
    val bgColor = when (msg.role) {
        MessageRole.USER      -> GibberBlue.copy(alpha = 0.15f)
        MessageRole.ASSISTANT -> if (msg.isProactive) GibberRed.copy(alpha = 0.10f)
                                 else GibberAmber.copy(alpha = 0.08f)
        MessageRole.SYSTEM    -> MaterialTheme.colorScheme.surface.copy(alpha = 0.5f)
    }
    val align = if (isUser) Alignment.End else Alignment.Start

    Column(modifier = Modifier.fillMaxWidth(), horizontalAlignment = align) {
        // Badge row
        if (msg.badge.isNotEmpty()) {
            Text(
                text   = msg.badge + if (msg.isProactive) " proactive" else "",
                style  = MaterialTheme.typography.labelSmall,
                color  = OnSurfaceDim,
                modifier = Modifier.padding(horizontal = 4.dp),
            )
        }

        Card(
            colors   = CardDefaults.cardColors(containerColor = bgColor),
            shape    = RoundedCornerShape(
                topStart     = if (isUser) 12.dp else 4.dp,
                topEnd       = if (isUser) 4.dp  else 12.dp,
                bottomStart  = 12.dp,
                bottomEnd    = 12.dp,
            ),
            modifier = Modifier.fillMaxWidth(if (isUser) 0.88f else 1f),
        ) {
            Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                SelectionContainer {
                    Text(
                        text   = msg.text,
                        style  = MaterialTheme.typography.bodySmall,
                        color  = MaterialTheme.colorScheme.onSurface,
                        lineHeight = 18.sp,
                    )
                }

                // Code blocks from GenerateCode actions
                msg.actions.filterIsInstance<AssistantAction.GenerateCode>().forEach { code ->
                    CodeBlock(action = code, onCopy = { onAction(code) })
                }

                // Tappable action chips (non-code)
                val chips = msg.actions.filterNot { it is AssistantAction.GenerateCode
                    || it is AssistantAction.InjectHint || it is AssistantAction.AddDashboardCard }
                if (chips.isNotEmpty()) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .horizontalScroll(rememberScrollState()),
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                    ) {
                        chips.forEach { action ->
                            ActionChip(action = action, onClick = { onAction(action) })
                        }
                    }
                }
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Code block
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun CodeBlock(action: AssistantAction.GenerateCode, onCopy: () -> Unit) {
    Card(
        colors   = CardDefaults.cardColors(containerColor = Color(0xFF0D1117)),
        shape    = RoundedCornerShape(6.dp),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(modifier = Modifier.padding(horizontal = 10.dp, vertical = 8.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    "${action.language} · ${action.description}",
                    style  = MaterialTheme.typography.labelSmall,
                    color  = GibberGreen,
                    fontWeight = FontWeight.Bold,
                )
                IconButton(onClick = onCopy, modifier = Modifier.size(24.dp)) {
                    Icon(Icons.Filled.ContentCopy, contentDescription = "Copy",
                        tint = OnSurfaceDim, modifier = Modifier.size(14.dp))
                }
            }
            SelectionContainer {
                Text(
                    text       = action.code,
                    fontFamily = FontFamily.Monospace,
                    fontSize   = 11.sp,
                    color      = Color(0xFFE6EDF3),
                    lineHeight = 16.sp,
                )
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Action chip
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun ActionChip(action: AssistantAction, onClick: () -> Unit) {
    val (label, color) = when (action) {
        is AssistantAction.Navigate          -> "→ ${action.tab.replaceFirstChar { it.uppercase() }}" to GibberBlue
        AssistantAction.ScanWifi             -> "📡 Scan WiFi" to GibberGreen
        AssistantAction.DiscoverPeers        -> "🔗 Discover" to GibberGreen
        is AssistantAction.SetMode           -> "🔴 ${action.mode}" to GibberRed
        is AssistantAction.SetRole           -> "👤 ${action.role}" to GibberAmber
        is AssistantAction.PopulateTranslate -> "📝 Fill Translate" to GibberAmber
        is AssistantAction.PinMetric         -> "📌 Pin ${action.fieldName}" to GibberAmber
        is AssistantAction.UnpinMetric       -> "📌 Unpin" to OnSurfaceDim
        is AssistantAction.StartMonitoring   -> "▶ Monitor ${action.label}" to GibberGreen
        is AssistantAction.StopMonitoring    -> "⏹ Stop ${action.id}" to GibberRed
        is AssistantAction.PushNotification  -> "🔔 Notify" to GibberBlue
        is AssistantAction.RemoveDashboardCard -> "🗑 Remove card" to GibberRed
        is AssistantAction.ClearHint         -> "🧹 Clear hint" to OnSurfaceDim
        else -> return  // InjectHint / AddDashboardCard auto-execute silently
    }

    FilledTonalButton(
        onClick = onClick,
        colors  = ButtonDefaults.filledTonalButtonColors(
            containerColor = color.copy(alpha = 0.15f),
            contentColor   = color,
        ),
        modifier = Modifier.height(30.dp),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(horizontal = 10.dp, vertical = 0.dp),
    ) {
        Text(label, style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Bold)
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// API settings panel
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun ApiSettingsPanel(vm: AssistantViewModel, onClose: () -> Unit) {
    var key      by remember { mutableStateOf("") }
    var endpoint by remember { mutableStateOf("https://api.openai.com/v1/chat/completions") }
    var model    by remember { mutableStateOf("gpt-4o-mini") }

    Surface(
        color    = MaterialTheme.colorScheme.surface,
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 12.dp, vertical = 8.dp),
        shape    = RoundedCornerShape(8.dp),
    ) {
        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(
                "⚙️ AI Source Config",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold,
            )
            Text(
                "Leave key blank to use local Ollama (Termux) or static KB.",
                style = MaterialTheme.typography.bodySmall,
                color = OnSurfaceDim,
            )
            OutlinedTextField(
                value         = key,
                onValueChange = { key = it },
                label         = { Text("API Key (optional)", style = MaterialTheme.typography.labelSmall) },
                placeholder   = { Text("sk-…  or  leave blank for Ollama", style = MaterialTheme.typography.bodySmall) },
                modifier      = Modifier.fillMaxWidth(),
                singleLine    = true,
            )
            OutlinedTextField(
                value         = endpoint,
                onValueChange = { endpoint = it },
                label         = { Text("Endpoint", style = MaterialTheme.typography.labelSmall) },
                modifier      = Modifier.fillMaxWidth(),
                singleLine    = true,
            )
            OutlinedTextField(
                value         = model,
                onValueChange = { model = it },
                label         = { Text("Model", style = MaterialTheme.typography.labelSmall) },
                modifier      = Modifier.fillMaxWidth(),
                singleLine    = true,
            )
            Text(
                "Local Ollama: runs at http://127.0.0.1:11434 via Termux.\n" +
                "Compatible with any OpenAI-compatible endpoint.",
                style = MaterialTheme.typography.labelSmall,
                color = OnSurfaceDim,
                fontStyle = FontStyle.Italic,
            )
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilledTonalButton(
                    onClick = {
                        vm.saveApiConfig(key.trim(), endpoint.trim(), model.trim())
                        onClose()
                    },
                    colors = ButtonDefaults.filledTonalButtonColors(containerColor = GibberAmber.copy(alpha = 0.15f)),
                ) {
                    Text("Save", color = GibberAmber, fontWeight = FontWeight.Bold)
                }
                TextButton(onClick = onClose) {
                    Text("Cancel", color = OnSurfaceDim)
                }
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Active monitors section
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun ActiveMonitorsSection(
    jobs:   List<MonitoringJob>,
    onStop: (String) -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 12.dp, vertical = 6.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Text(
            "🔁 Active Monitors",
            style      = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.Bold,
            color      = GibberGreen,
        )
        jobs.forEach { job ->
            Card(
                colors   = CardDefaults.cardColors(containerColor = GibberGreen.copy(alpha = 0.06f)),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 10.dp, vertical = 6.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment     = Alignment.CenterVertically,
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text  = job.label,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurface,
                        )
                        Text(
                            text  = "every ${job.intervalSeconds}s · ${job.sensorKey}",
                            style = MaterialTheme.typography.labelSmall,
                            color = OnSurfaceDim,
                        )
                    }
                    IconButton(
                        onClick  = { onStop(job.id) },
                        modifier = Modifier.size(28.dp),
                    ) {
                        Icon(
                            imageVector        = Icons.Filled.Close,
                            contentDescription = "Stop monitor ${job.label}",
                            tint               = GibberRed,
                            modifier           = Modifier.size(16.dp),
                        )
                    }
                }
            }
        }
    }
}