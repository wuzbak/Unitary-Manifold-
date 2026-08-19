package com.gibbernode.feature.dashboard

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
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
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Emergency
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.gibbernode.gibberwave.AdaptiveStateHolder
import com.gibbernode.gibberwave.CardSeverity
import com.gibbernode.gibberwave.InjectedCard
import com.gibbernode.gibberwave.OperationalMode
import com.gibbernode.gibberwave.SentinelMood
import com.gibbernode.ui.GibberAmber
import com.gibbernode.ui.GibberBlue
import com.gibbernode.ui.GibberGreen
import com.gibbernode.ui.GibberRed
import com.gibbernode.ui.OnSurfaceDim
import com.gibbernode.ui.SurfaceDark

/**
 * DashboardScreen — Tab 1
 *
 * Shows:
 *  - Large colour-coded operational mode ring with heartbeat pulse
 *  - Sentinel health summary (mood, battery, CPU temp, anomaly count)
 *  - Ollama AI analysis card (dismissible)
 *  - SOS FAB (one-tap RED mode broadcast)
 */
@Composable
fun DashboardScreen(
    onNavigateToMode: () -> Unit = {},
    viewModel: DashboardViewModel = hiltViewModel(),
) {
    val state         by viewModel.state.collectAsStateWithLifecycle()
    val adaptiveState by viewModel.adaptiveState.collectAsStateWithLifecycle()

    Scaffold(
        floatingActionButton = {
            FloatingActionButton(
                onClick            = {
                    viewModel.setMode(OperationalMode.RED)
                    onNavigateToMode()
                },
                containerColor     = GibberRed,
                contentColor       = Color.White,
            ) {
                Icon(Icons.Filled.Emergency, contentDescription = "Broadcast SOS")
            }
        },
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 16.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            // ── Mode ring ──────────────────────────────────────────────────
            ModeRing(
                mode           = state.activeMode,
                heartbeatCount = state.heartbeatCount,
            )

            // ── Sentinel health card ───────────────────────────────────────
            SentinelHealthCard(state = state)

            // ── Ollama analysis card (shown only when present) ─────────────
            state.ollamaAnalysis?.let { analysis ->
                OllamaCard(
                    text      = analysis,
                    onDismiss = viewModel::dismissAnalysis,
                )
            }

            // ── Last token card ────────────────────────────────────────────
            state.lastToken?.let { token ->
                LastTokenCard(payload = token.payload)
            }

            // ── Assistant hint banner ──────────────────────────────────────
            adaptiveState.screenHints["dashboard"]?.let { hint ->
                AssistantHintBanner(hint = hint, onDismiss = viewModel::clearDashboardHint)
            }

            // ── Assistant-injected adaptive cards ──────────────────────────
            adaptiveState.dashboardCards.forEach { card ->
                AdaptiveInjectedCard(card = card, onDismiss = { viewModel.removeDashboardCard(card.id) })
            }

            Spacer(Modifier.height(80.dp))  // above FAB
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Sub-composables
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun ModeRing(
    mode: OperationalMode,
    heartbeatCount: Long,
) {
    val ringColor by animateColorAsState(
        targetValue = when (mode) {
            OperationalMode.GREEN -> GibberGreen
            OperationalMode.RED   -> GibberRed
            OperationalMode.BLUE  -> GibberBlue
            OperationalMode.AMBER -> GibberAmber
        },
        animationSpec = tween(500),
        label         = "ring_color",
    )

    // Heartbeat pulse: alpha flashes 1 → 0.3 → 1 each time a new token arrives
    val infiniteTransition = rememberInfiniteTransition(label = "heartbeat")
    val pulseAlpha by infiniteTransition.animateFloat(
        initialValue   = 1f,
        targetValue    = 0.3f,
        animationSpec  = infiniteRepeatable(
            animation  = tween(800),
            repeatMode = RepeatMode.Reverse,
        ),
        label          = "pulse_alpha",
    )

    // Force a re-composition each new heartbeat (key block restarts the animation)
    key(heartbeatCount) {
        Box(
            contentAlignment = Alignment.Center,
            modifier         = Modifier
                .fillMaxWidth()
                .height(200.dp),
        ) {
            // Outer glow ring
            Box(
                modifier = Modifier
                    .size(180.dp)
                    .alpha(pulseAlpha * 0.3f)
                    .clip(CircleShape)
                    .background(ringColor),
            )
            // Inner solid ring
            Box(
                contentAlignment = Alignment.Center,
                modifier         = Modifier
                    .size(140.dp)
                    .clip(CircleShape)
                    .background(ringColor.copy(alpha = 0.9f)),
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text  = mode.name,
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold,
                        color = Color.Black,
                    )
                    if (heartbeatCount > 0) {
                        Text(
                            text  = "♥ $heartbeatCount",
                            style = MaterialTheme.typography.labelSmall,
                            color = Color.Black.copy(alpha = 0.7f),
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun SentinelHealthCard(state: DashboardUiState) {
    val moodColor = when (state.sentinelMood) {
        SentinelMood.CALM      -> GibberGreen
        SentinelMood.STRESSED  -> GibberAmber
        SentinelMood.EXHAUSTED -> Color(0xFFFF6D00)  // deep orange
        SentinelMood.CRITICAL  -> GibberRed
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier            = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment   = Alignment.CenterVertically,
            ) {
                Text(
                    text  = "${state.sentinelMood.emoji} ${state.sentinelMood.label}",
                    style = MaterialTheme.typography.titleMedium,
                    color = moodColor,
                    fontWeight = FontWeight.Bold,
                )
                if (state.anomalyCount > 0) {
                    Text(
                        text  = "⚠ ${state.anomalyCount} anomal${if (state.anomalyCount == 1) "y" else "ies"}",
                        style = MaterialTheme.typography.labelMedium,
                        color = GibberRed,
                    )
                }
            }

            Spacer(Modifier.height(12.dp))

            Row(
                modifier              = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(24.dp),
            ) {
                MetricItem(
                    label = "Battery",
                    value = if (state.batteryPct >= 0) "${state.batteryPct}%" else "—",
                    color = when {
                        state.batteryPct in 0..15 -> GibberRed
                        state.batteryPct in 16..30 -> GibberAmber
                        else -> GibberGreen
                    },
                )
                MetricItem(
                    label = "CPU",
                    value = if (state.cpuTempC > 0) "${state.cpuTempC.toInt()}°C" else "—",
                    color = when {
                        state.cpuTempC > 50 -> GibberRed
                        state.cpuTempC > 45 -> GibberAmber
                        else -> GibberGreen
                    },
                )
                MetricItem(
                    label = "Bat. Temp",
                    value = if (state.batteryTempC > 0) "${state.batteryTempC.toInt()}°C" else "—",
                    color = when {
                        state.batteryTempC > 40 -> GibberRed
                        state.batteryTempC > 35 -> GibberAmber
                        else -> GibberGreen
                    },
                )
            }
        }
    }
}

@Composable
private fun MetricItem(label: String, value: String, color: Color) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text  = value,
            style = MaterialTheme.typography.titleLarge,
            color = color,
            fontWeight = FontWeight.Bold,
        )
        Text(
            text  = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun OllamaCard(text: String, onDismiss: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors   = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f)
        ),
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier              = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment     = Alignment.CenterVertically,
            ) {
                Text(
                    text  = "🤖 AI Analysis",
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.primary,
                )
                Button(
                    onClick  = onDismiss,
                    colors   = ButtonDefaults.textButtonColors(),
                    modifier = Modifier.height(28.dp),
                ) {
                    Text("×", fontSize = 18.sp)
                }
            }
            Spacer(Modifier.height(8.dp))
            Text(
                text  = text,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface,
            )
        }
    }
}

@Composable
private fun LastTokenCard(payload: String) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Text(
                text  = "Last Token",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Spacer(Modifier.height(4.dp))
            Text(
                text       = payload,
                style      = MaterialTheme.typography.bodySmall,
                fontFamily = FontFamily.Monospace,
                color      = MaterialTheme.colorScheme.onSurface,
                maxLines   = 3,
                overflow   = TextOverflow.Ellipsis,
            )
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Note: CalibrationWizardScreen is in CalibrationWizardScreen.kt (same package)
// ─────────────────────────────────────────────────────────────────────────────

// ─────────────────────────────────────────────────────────────────────────────
// Adaptive / assistant-injected composables
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun AssistantHintBanner(hint: String, onDismiss: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors   = CardDefaults.cardColors(containerColor = GibberAmber.copy(alpha = 0.10f)),
    ) {
        Row(
            modifier  = Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            Text(
                text     = "💡 $hint",
                style    = MaterialTheme.typography.bodySmall,
                color    = GibberAmber,
                modifier = Modifier.weight(1f),
            )
            IconButton(onClick = onDismiss, modifier = Modifier.size(24.dp)) {
                Icon(Icons.Filled.Close, contentDescription = "Dismiss",
                    tint = OnSurfaceDim, modifier = Modifier.size(14.dp))
            }
        }
    }
}

@Composable
private fun AdaptiveInjectedCard(card: InjectedCard, onDismiss: () -> Unit) {
    val accentColor = when (card.severity) {
        CardSeverity.CRITICAL -> GibberRed
        CardSeverity.WARNING  -> GibberAmber
        CardSeverity.CAUTION  -> GibberAmber.copy(alpha = 0.7f)
        CardSeverity.INFO     -> GibberGreen
    }
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors   = CardDefaults.cardColors(containerColor = accentColor.copy(alpha = 0.08f)),
    ) {
        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text       = "${card.icon} ${card.title}",
                    style      = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Bold,
                    color      = accentColor,
                )
                IconButton(onClick = onDismiss, modifier = Modifier.size(24.dp)) {
                    Icon(Icons.Filled.Close, contentDescription = "Dismiss",
                        tint = OnSurfaceDim, modifier = Modifier.size(14.dp))
                }
            }
            Text(
                text  = card.body,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurface,
            )
        }
    }
}
