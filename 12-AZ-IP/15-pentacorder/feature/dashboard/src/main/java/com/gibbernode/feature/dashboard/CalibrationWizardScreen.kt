package com.gibbernode.feature.dashboard

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.GraphicEq
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Tune
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Slider
import androidx.compose.material3.SliderDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.gibbernode.audio.TxProtocol
import com.gibbernode.ui.GibberAmber
import com.gibbernode.ui.GibberGreen
import com.gibbernode.ui.GibberRed
import com.gibbernode.ui.SurfaceDark

/**
 * CalibrationWizardScreen
 *
 * A 4-step wizard that ensures the Pentacorder's ggwave audio channel is working
 * correctly on this device before first use.
 *
 * Step 0 — Welcome  : explain purpose, S24 Ultra Dolby Atmos note
 * Step 1 — Test     : play a test tone, listen for loopback, show pass/fail
 * Step 2 — Protocol : pick TX protocol (auto-recommended or manual override) + volume
 * Step 3 — Done     : confirm saved, navigate back
 *
 * The result (protocolId + volume) is saved to CalibrationStore (DataStore) and
 * used by ModeViewModel for all subsequent broadcasts.
 */
@Composable
fun CalibrationWizardScreen(
    onComplete: () -> Unit,
    viewModel: CalibrationViewModel = hiltViewModel(),
) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    // Navigate back as soon as isDone flips to true
    LaunchedEffect(state.isDone) {
        if (state.isDone) onComplete()
    }

    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = 24.dp)
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Spacer(Modifier.height(24.dp))

            // ── Step indicator ────────────────────────────────────────────────
            StepIndicator(current = state.currentStep, total = 4)

            Spacer(Modifier.height(32.dp))

            // ── Step content ──────────────────────────────────────────────────
            AnimatedContent(
                targetState = state.currentStep,
                transitionSpec = {
                    fadeIn(tween(220)) togetherWith fadeOut(tween(180))
                },
                label = "calibration-step",
            ) { step ->
                when (step) {
                    CalibrationViewModel.STEP_WELCOME  -> WelcomeStep(onNext = viewModel::nextStep, onSkip = viewModel::skip)
                    CalibrationViewModel.STEP_TEST     -> TestStep(state = state, viewModel = viewModel)
                    CalibrationViewModel.STEP_PROTOCOL -> ProtocolStep(state = state, viewModel = viewModel)
                    CalibrationViewModel.STEP_DONE     -> DoneStep(state = state, onSave = viewModel::saveAndComplete)
                    else                               -> Unit
                }
            }
        }
    }
}

// ── Step 0 — Welcome ──────────────────────────────────────────────────────────

@Composable
private fun WelcomeStep(onNext: () -> Unit, onSkip: () -> Unit) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Icon(
            imageVector = Icons.Default.Tune,
            contentDescription = null,
            tint = GibberGreen,
            modifier = Modifier.size(64.dp),
        )
        Spacer(Modifier.height(16.dp))
        Text(
            text = "Audio Calibration",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onBackground,
        )
        Spacer(Modifier.height(12.dp))
        Text(
            text = "GibberNode uses ggwave FSK acoustic encoding to transmit data " +
                   "through your device's speaker and microphone.\n\n" +
                   "Calibration ensures the best protocol for your device. " +
                   "It takes about 15 seconds.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center,
        )
        Spacer(Modifier.height(16.dp))
        // S24 Ultra-specific note
        InfoCard(
            icon = Icons.Default.GraphicEq,
            title = "S24 Ultra — Dolby Atmos",
            body = "Dolby Atmos post-processing may attenuate certain FSK frequencies. " +
                   "The loopback test will pick the safest protocol automatically.",
            color = GibberAmber,
        )
        Spacer(Modifier.height(32.dp))
        Button(
            onClick = onNext,
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.buttonColors(containerColor = GibberGreen),
        ) {
            Icon(Icons.Default.PlayArrow, contentDescription = null)
            Spacer(Modifier.width(8.dp))
            Text("Start Calibration", fontWeight = FontWeight.Bold)
        }
        Spacer(Modifier.height(12.dp))
        OutlinedButton(
            onClick = onSkip,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text("Skip — use defaults", color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}

// ── Step 1 — Audio Test ───────────────────────────────────────────────────────

@Composable
private fun TestStep(state: CalibrationUiState, viewModel: CalibrationViewModel) {
    val pulseFraction by rememberInfiniteTransition(label = "pulse").animateFloat(
        initialValue = 0.4f,
        targetValue  = 1f,
        animationSpec = infiniteRepeatable(
            animation  = tween(800, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse,
        ),
        label = "pulse-alpha",
    )
    val isActive = state.testStatus == TestStatus.TESTING

    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Icon(
            imageVector = Icons.Default.GraphicEq,
            contentDescription = null,
            tint = when (state.testStatus) {
                TestStatus.PASSED -> GibberGreen
                TestStatus.FAILED -> GibberAmber
                TestStatus.TESTING -> GibberGreen
                TestStatus.IDLE    -> MaterialTheme.colorScheme.onSurfaceVariant
            },
            modifier = Modifier
                .size(72.dp)
                .alpha(if (isActive) pulseFraction else 1f),
        )
        Spacer(Modifier.height(16.dp))
        Text(
            text = "Loopback Test",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onBackground,
        )
        Spacer(Modifier.height(8.dp))
        Text(
            text = "The app will play a short test tone through your speaker, then " +
                   "listen on the microphone to verify it was decoded correctly.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center,
        )
        Spacer(Modifier.height(24.dp))

        when (state.testStatus) {
            TestStatus.IDLE -> {
                Button(
                    onClick = viewModel::startAudioTest,
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(containerColor = GibberGreen),
                ) {
                    Icon(Icons.Default.PlayArrow, contentDescription = null)
                    Spacer(Modifier.width(8.dp))
                    Text("Run Loopback Test", fontWeight = FontWeight.Bold)
                }
            }
            TestStatus.TESTING -> {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    CircularProgressIndicator(
                        color    = GibberGreen,
                        modifier = Modifier.size(20.dp),
                        strokeWidth = 2.dp,
                    )
                    Spacer(Modifier.width(12.dp))
                    Text(
                        text  = state.testMessage,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        fontFamily = FontFamily.Monospace,
                    )
                }
                Spacer(Modifier.height(16.dp))
                OutlinedButton(onClick = viewModel::cancelTest, modifier = Modifier.fillMaxWidth()) {
                    Text("Cancel")
                }
            }
            TestStatus.PASSED -> {
                ResultBadge(passed = true, message = state.testMessage)
                Spacer(Modifier.height(16.dp))
                Button(
                    onClick = viewModel::nextStep,
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(containerColor = GibberGreen),
                ) {
                    Icon(Icons.Default.Check, contentDescription = null)
                    Spacer(Modifier.width(8.dp))
                    Text("Next — Choose Protocol", fontWeight = FontWeight.Bold)
                }
                Spacer(Modifier.height(8.dp))
                OutlinedButton(onClick = viewModel::startAudioTest, modifier = Modifier.fillMaxWidth()) {
                    Text("Run Again")
                }
            }
            TestStatus.FAILED -> {
                ResultBadge(passed = false, message = state.testMessage)
                Spacer(Modifier.height(16.dp))
                Button(
                    onClick = viewModel::startAudioTest,
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(containerColor = GibberAmber),
                ) {
                    Icon(Icons.Default.PlayArrow, contentDescription = null)
                    Spacer(Modifier.width(8.dp))
                    Text("Retry Test", fontWeight = FontWeight.Bold)
                }
                Spacer(Modifier.height(8.dp))
                OutlinedButton(onClick = viewModel::nextStep, modifier = Modifier.fillMaxWidth()) {
                    Text("Continue Anyway")
                }
            }
        }
    }
}

// ── Step 2 — Protocol selection ───────────────────────────────────────────────

@Composable
private fun ProtocolStep(state: CalibrationUiState, viewModel: CalibrationViewModel) {
    val audibleProtocols = listOf(
        TxProtocol.AUDIBLE_NORMAL   to "Normal  — Robust, ~4 s/msg. Best for noisy environments.",
        TxProtocol.AUDIBLE_FAST     to "Fast    — Balanced, ~2 s/msg. Good all-rounder.",
        TxProtocol.AUDIBLE_FASTEST  to "Fastest — ~1 s/msg. Quiet rooms only; higher error rate.",
    )

    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Icon(
            imageVector = Icons.Default.Tune,
            contentDescription = null,
            tint = GibberGreen,
            modifier = Modifier.size(56.dp),
        )
        Spacer(Modifier.height(16.dp))
        Text(
            text = "Choose Protocol",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onBackground,
        )
        Spacer(Modifier.height(8.dp))

        if (state.recommendedProtocol != null) {
            Text(
                text = "Recommended based on test: ${state.recommendedProtocol.name}",
                style = MaterialTheme.typography.bodySmall,
                color = GibberGreen,
                fontFamily = FontFamily.Monospace,
            )
            Spacer(Modifier.height(8.dp))
        }

        audibleProtocols.forEach { (protocol, description) ->
            ProtocolCard(
                protocol    = protocol,
                description = description,
                selected    = state.selectedProtocol == protocol,
                recommended = state.recommendedProtocol == protocol,
                onClick     = { viewModel.selectProtocol(protocol) },
            )
            Spacer(Modifier.height(8.dp))
        }

        Spacer(Modifier.height(16.dp))

        // Volume slider
        Text(
            text = "Volume: ${state.selectedVolume}",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.fillMaxWidth(),
        )
        Slider(
            value          = state.selectedVolume.toFloat(),
            onValueChange  = { viewModel.selectVolume(it.toInt()) },
            valueRange     = 5f..100f,
            steps          = 18,
            colors         = SliderDefaults.colors(thumbColor = GibberGreen, activeTrackColor = GibberGreen),
        )
        Text(
            text  = "Lower = quieter / less distortion   Higher = longer range",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Spacer(Modifier.height(24.dp))
        Button(
            onClick  = viewModel::nextStep,
            modifier = Modifier.fillMaxWidth(),
            colors   = ButtonDefaults.buttonColors(containerColor = GibberGreen),
        ) {
            Icon(Icons.Default.Check, contentDescription = null)
            Spacer(Modifier.width(8.dp))
            Text("Save and Finish", fontWeight = FontWeight.Bold)
        }
        Spacer(Modifier.height(8.dp))
        OutlinedButton(onClick = viewModel::prevStep, modifier = Modifier.fillMaxWidth()) {
            Text("Back")
        }
    }
}

// ── Step 3 — Done ─────────────────────────────────────────────────────────────

@Composable
private fun DoneStep(state: CalibrationUiState, onSave: () -> Unit) {
    // Trigger save immediately on entering this step
    LaunchedEffect(Unit) { onSave() }

    val ceilingKHz = state.safeCeilingHz / 1_000f

    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
        modifier = Modifier.fillMaxSize(),
    ) {
        Box(
            contentAlignment = Alignment.Center,
            modifier = Modifier
                .size(80.dp)
                .clip(CircleShape)
                .background(GibberGreen.copy(alpha = 0.15f)),
        ) {
            Icon(
                imageVector = Icons.Default.Check,
                contentDescription = null,
                tint = GibberGreen,
                modifier = Modifier.size(48.dp),
            )
        }
        Spacer(Modifier.height(24.dp))
        Text(
            text = "Calibration Complete",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            color = GibberGreen,
        )
        Spacer(Modifier.height(12.dp))
        Text(
            text = "Settings saved. Pentacorder is ready to broadcast.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center,
        )
        Spacer(Modifier.height(16.dp))
        // Safe ceiling summary card
        InfoCard(
            icon  = Icons.Default.GraphicEq,
            title = "safe_ceiling_hz = ${state.safeCeilingHz} Hz  (%.1f kHz)".format(ceilingKHz),
            body  = buildString {
                append("Protocol: ${state.selectedProtocol.name}  |  Volume: ${state.selectedVolume}")
                if (state.noiseFloorDb > -99f) {
                    append("\nNoise floor: %.0f dBFS".format(state.noiseFloorDb))
                }
                if (state.safeCeilingHz >= 17_000) {
                    append("\n✓ Near-ultrasonic band verified — Dolby Atmos safe.")
                } else {
                    append("\n⚠ Falling back to audible band (Dolby Atmos may attenuate > ${state.safeCeilingHz} Hz).")
                }
            },
            color = if (state.safeCeilingHz >= 17_000) GibberGreen else GibberAmber,
        )
        Spacer(Modifier.height(8.dp))
        Text(
            text = "Returning to dashboard…",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            fontFamily = FontFamily.Monospace,
        )
    }
}

// ── Small reusable composables ────────────────────────────────────────────────

@Composable
private fun StepIndicator(current: Int, total: Int) {
    Row(
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        repeat(total) { idx ->
            val active = idx == current
            val done   = idx < current
            val color  = when {
                active -> GibberGreen
                done   -> GibberGreen.copy(alpha = 0.4f)
                else   -> MaterialTheme.colorScheme.surfaceVariant
            }
            Box(
                modifier = Modifier
                    .size(if (active) 10.dp else 8.dp)
                    .clip(CircleShape)
                    .background(color),
            )
        }
    }
}

@Composable
private fun ResultBadge(passed: Boolean, message: String) {
    val color = if (passed) GibberGreen else GibberAmber
    val icon  = if (passed) Icons.Default.Check else Icons.Default.Close

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(8.dp))
            .background(color.copy(alpha = 0.1f))
            .border(1.dp, color.copy(alpha = 0.4f), RoundedCornerShape(8.dp))
            .padding(12.dp),
        verticalAlignment = Alignment.Top,
    ) {
        Icon(icon, contentDescription = null, tint = color, modifier = Modifier.size(20.dp))
        Spacer(Modifier.width(10.dp))
        Text(
            text = message,
            style = MaterialTheme.typography.bodySmall,
            color = color,
            fontFamily = FontFamily.Monospace,
        )
    }
}

@Composable
private fun ProtocolCard(
    protocol:    TxProtocol,
    description: String,
    selected:    Boolean,
    recommended: Boolean,
    onClick:     () -> Unit,
) {
    val borderColor by animateColorAsState(
        targetValue = if (selected) GibberGreen else MaterialTheme.colorScheme.surfaceVariant,
        label = "protocol-border",
    )

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(8.dp))
            .background(if (selected) GibberGreen.copy(alpha = 0.08f) else SurfaceDark)
            .border(1.5.dp, borderColor, RoundedCornerShape(8.dp))
            .clickable { onClick() }
            .padding(12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            modifier = Modifier
                .size(18.dp)
                .clip(CircleShape)
                .background(if (selected) GibberGreen else Color.Transparent)
                .border(2.dp, if (selected) GibberGreen else MaterialTheme.colorScheme.onSurfaceVariant, CircleShape),
        )
        Spacer(Modifier.width(12.dp))
        Column(Modifier.weight(1f)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = protocol.name,
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = if (selected) GibberGreen else MaterialTheme.colorScheme.onBackground,
                    fontFamily = FontFamily.Monospace,
                    fontSize = 13.sp,
                )
                if (recommended) {
                    Spacer(Modifier.width(6.dp))
                    Text(
                        text = "✓ recommended",
                        style = MaterialTheme.typography.labelSmall,
                        color = GibberGreen,
                    )
                }
            }
            Text(
                text = description,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun InfoCard(
    icon:  androidx.compose.ui.graphics.vector.ImageVector,
    title: String,
    body:  String,
    color: Color,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(8.dp))
            .background(color.copy(alpha = 0.08f))
            .border(1.dp, color.copy(alpha = 0.3f), RoundedCornerShape(8.dp))
            .padding(12.dp),
        verticalAlignment = Alignment.Top,
    ) {
        Icon(icon, contentDescription = null, tint = color, modifier = Modifier.size(20.dp))
        Spacer(Modifier.width(10.dp))
        Column {
            Text(title, style = MaterialTheme.typography.labelMedium, color = color, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(2.dp))
            Text(body, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}
