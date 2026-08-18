package com.gibbernode.feature.translate

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
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowForward
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.RecordVoiceOver
import androidx.compose.material.icons.filled.SwapHoriz
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Divider
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.ScrollableTabRow
import androidx.compose.material3.Tab
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
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
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.gibbernode.gibberwave.CardSeverity
import com.gibbernode.gibberwave.InjectedCard
import com.gibbernode.interpret.PentadState
import com.gibbernode.interpret.Severity
import com.gibbernode.interpret.SituationReport
import com.gibbernode.interpret.UserRole
import com.gibbernode.ui.GibberAmber
import com.gibbernode.ui.GibberBlue
import com.gibbernode.ui.GibberGreen
import com.gibbernode.ui.GibberRed
import com.gibbernode.ui.OnSurfaceDim
import com.gibbernode.ui.SurfaceDark
import kotlin.math.roundToInt

/**
 * TranslateScreen — the Pentacorder Translator tab.
 *
 * Three sub-tabs implement the full translation stack:
 *
 *  0 — Human↔Human  : ML Kit on-device translation (59 languages), voice
 *                      in/out, role-aware quick-phrase cards.
 *
 *  1 — Field Intel   : SensorInterpreter renders live sensor readings as a
 *                      role-aware situation report — the "pentacorder" core.
 *
 *  2 — Protocol      : Bidirectional Gibberlink ↔ natural language bridge +
 *                      Pentad coherence panel.
 */
@Composable
fun TranslateScreen(viewModel: TranslateViewModel = hiltViewModel()) {
    val state         by viewModel.state.collectAsStateWithLifecycle()
    val adaptiveState by viewModel.adaptiveState.collectAsStateWithLifecycle()
    var tab   by remember { mutableIntStateOf(0) }

    Column(modifier = Modifier.fillMaxSize()) {
        ScrollableTabRow(selectedTabIndex = tab, edgePadding = 0.dp) {
            Tab(selected = tab == 0, onClick = { tab = 0 }) {
                Text("🗣 Language",  fontSize = 13.sp, modifier = Modifier.padding(vertical = 12.dp))
            }
            Tab(selected = tab == 1, onClick = { tab = 1 }) {
                Text("🌍 Field Intel", fontSize = 13.sp, modifier = Modifier.padding(vertical = 12.dp))
            }
            Tab(selected = tab == 2, onClick = { tab = 2 }) {
                Text("🔗 Protocol",  fontSize = 13.sp, modifier = Modifier.padding(vertical = 12.dp))
            }
        }

        // ── Assistant hint + adaptive cards ───────────────────────────────────
        adaptiveState.screenHints["translate"]?.let { hint ->
            AssistantHintBanner(hint = hint, onDismiss = viewModel::clearTranslateHint)
        }
        adaptiveState.dashboardCards.forEach { card ->
            AdaptiveInjectedCard(card = card, onDismiss = { viewModel.removeAdaptiveCard(card.id) })
        }

        when (tab) {
            0 -> HumanHumanTab(state = state, vm = viewModel)
            1 -> FieldIntelTab(state = state, vm = viewModel)
            2 -> ProtocolTab(state = state, vm = viewModel)
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 0 — Human ↔ Human Language Bridge
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun HumanHumanTab(state: TranslateUiState, vm: TranslateViewModel) {
    val lifecycleOwner = LocalLifecycleOwner.current
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        // ── Role selector ─────────────────────────────────────────────────────
        RoleSelector(selected = state.role, onSelect = vm::selectRole)

        // ── Language picker ───────────────────────────────────────────────────
        LanguagePicker(
            languages  = vm.getSupportedLanguages(),
            selected   = state.targetLanguage,
            onSelected = vm::onTargetLanguageChanged,
        )

        // ── Input text ────────────────────────────────────────────────────────
        OutlinedTextField(
            value         = state.humanSourceText,
            onValueChange = vm::onSourceTextChanged,
            placeholder   = {
                Text(
                    "Type or paste text to translate…\n(Auto-detects language)",
                    style = MaterialTheme.typography.bodySmall,
                )
            },
            modifier  = Modifier.fillMaxWidth().height(100.dp),
            maxLines  = 4,
        )

        // ── Action row ────────────────────────────────────────────────────────
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(
                onClick  = vm::translateHumanText,
                enabled  = state.humanSourceText.isNotEmpty() && !state.isTranslating,
                colors   = ButtonDefaults.buttonColors(containerColor = GibberAmber),
                modifier = Modifier.weight(1f),
            ) {
                if (state.isTranslating) {
                    CircularProgressIndicator(modifier = Modifier.size(18.dp), strokeWidth = 2.dp, color = Color.Black)
                } else {
                    Icon(Icons.Filled.ArrowForward, contentDescription = null, tint = Color.Black)
                    Spacer(Modifier.width(6.dp))
                    Text("Translate", color = Color.Black, fontWeight = FontWeight.Bold)
                }
            }
            if (state.ttsReady && state.humanTranslated != null) {
                IconButton(
                    onClick  = vm::speakTranslation,
                    modifier = Modifier
                        .clip(CircleShape)
                        .background(GibberBlue.copy(alpha = 0.15f)),
                ) {
                    Icon(Icons.Filled.RecordVoiceOver, contentDescription = "Speak", tint = GibberBlue)
                }
            }
        }

        // ── OCR Camera Scan ───────────────────────────────────────────────────
        Button(
            onClick  = { vm.captureForOcr(lifecycleOwner) },
            enabled  = !state.ocrRunning && !state.isTranslating,
            colors   = ButtonDefaults.buttonColors(containerColor = GibberBlue),
            modifier = Modifier.fillMaxWidth(),
        ) {
            if (state.ocrRunning) {
                CircularProgressIndicator(modifier = Modifier.size(18.dp), strokeWidth = 2.dp, color = Color.White)
                Spacer(Modifier.width(6.dp))
                Text("📷 Scanning text…")
            } else {
                Text("📷 Scan Text with Camera (OCR → Translate)")
            }
        }
        state.ocrError?.let { err ->
            Text("⚠️ $err", style = MaterialTheme.typography.labelSmall, color = GibberRed)
        }
        state.ocrText?.let { scanned ->
            if (scanned.isNotEmpty()) {
                Card(colors = CardDefaults.cardColors(containerColor = GibberBlue.copy(alpha = 0.08f)),
                    modifier = Modifier.fillMaxWidth()) {
                    Text("📷 Scanned: $scanned",
                        style = MaterialTheme.typography.labelSmall,
                        color = GibberBlue,
                        modifier = Modifier.padding(10.dp))
                }
            }
        }

        // ── Result ────────────────────────────────────────────────────────────
        if (state.translateError != null) {
            Card(colors = CardDefaults.cardColors(containerColor = GibberRed.copy(alpha = 0.12f))) {
                Text(
                    text     = state.translateError,
                    style    = MaterialTheme.typography.bodySmall,
                    color    = GibberRed,
                    modifier = Modifier.padding(12.dp),
                )
            }
        }
        if (state.humanTranslated != null) {
            Card(
                colors   = CardDefaults.cardColors(containerColor = GibberAmber.copy(alpha = 0.10f)),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    if (state.detectedSourceLang.isNotEmpty()) {
                        Text(
                            text  = "Detected: ${state.detectedSourceLang.uppercase()} → ${state.targetLanguage.uppercase()}",
                            style = MaterialTheme.typography.labelSmall,
                            color = OnSurfaceDim,
                        )
                    }
                    Text(
                        text       = state.humanTranslated,
                        style      = MaterialTheme.typography.bodyMedium,
                        color      = GibberAmber,
                        fontWeight = FontWeight.Medium,
                    )
                }
            }
        }

        Divider(color = MaterialTheme.colorScheme.outline)

        // ── Quick phrase cards ────────────────────────────────────────────────
        if (state.quickPhrases.isNotEmpty()) {
            Text(
                text  = "${state.role.emoji} Quick Phrases — ${state.role.displayName}",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface,
            )
            Text(
                text  = "Tap to speak in target language. Long-press to queue translation.",
                style = MaterialTheme.typography.labelSmall,
                color = OnSurfaceDim,
            )

            val byCategory = state.quickPhrases.groupBy { it.category }
            byCategory.forEach { (category, phrases) ->
                Text(
                    text  = category.replaceFirstChar { it.uppercase() },
                    style = MaterialTheme.typography.labelMedium,
                    color = roleColor(state.role),
                    fontWeight = FontWeight.SemiBold,
                )
                phrases.forEach { phrase ->
                    QuickPhraseCard(
                        phrase   = phrase,
                        color    = roleColor(state.role),
                        ttsReady = state.ttsReady,
                        onTap    = { vm.speakPhrase(phrase) },
                        onQueue  = {
                            vm.onSourceTextChanged(phrase.english)
                            vm.translateHumanText()
                        },
                    )
                }
            }
        }

        Spacer(Modifier.height(24.dp))
    }
}

@Composable
private fun QuickPhraseCard(
    phrase: QuickPhrase,
    color:  Color,
    ttsReady: Boolean,
    onTap:  () -> Unit,
    onQueue: () -> Unit,
) {
    Card(
        onClick = onTap,
        colors  = CardDefaults.cardColors(containerColor = SurfaceDark),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Row(
            modifier          = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(phrase.english, style = MaterialTheme.typography.bodySmall,
                    fontWeight = FontWeight.Medium, color = MaterialTheme.colorScheme.onSurface)
                if (phrase.translated != null) {
                    Text(phrase.translated, style = MaterialTheme.typography.bodySmall,
                        color = color, fontStyle = FontStyle.Italic)
                }
            }
            Row {
                if (ttsReady) {
                    IconButton(onClick = onTap) {
                        Icon(Icons.Filled.RecordVoiceOver, contentDescription = "Speak",
                            tint = color, modifier = Modifier.size(20.dp))
                    }
                }
                IconButton(onClick = onQueue) {
                    Icon(Icons.Filled.ArrowForward, contentDescription = "Translate",
                        tint = OnSurfaceDim, modifier = Modifier.size(20.dp))
                }
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 1 — Field Intelligence (Sensor → Situation)
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun FieldIntelTab(state: TranslateUiState, vm: TranslateViewModel) {
    val lifecycleOwner = LocalLifecycleOwner.current
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        // ── Role selector ─────────────────────────────────────────────────────
        RoleSelector(selected = state.role, onSelect = vm::selectRole)

        // ── Pentad coherence gauge ─────────────────────────────────────────────
        PentadCoherenceCard(pentad = state.pentad)

        val report = state.situationReport
        if (report == null) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
            ) {
                Text(
                    text     = "No sensor data yet. Open the Tricorder tab to activate sensors, " +
                        "then return here for real-time interpretation.",
                    style    = MaterialTheme.typography.bodySmall,
                    color    = OnSurfaceDim,
                    modifier = Modifier.padding(16.dp),
                )
            }
        } else {
            SituationReportCard(report = report, role = state.role)
        }

        // ── Hazard Object Detection ───────────────────────────────────────────
        Button(
            onClick  = { vm.captureForHazardScan(lifecycleOwner) },
            enabled  = !state.hazardRunning,
            colors   = ButtonDefaults.buttonColors(containerColor = GibberRed),
            modifier = Modifier.fillMaxWidth(),
        ) {
            if (state.hazardRunning) {
                CircularProgressIndicator(modifier = Modifier.size(18.dp), strokeWidth = 2.dp, color = Color.White)
                Spacer(Modifier.width(6.dp))
                Text("🔍 Scanning scene…")
            } else {
                Text("🔍 Hazard Scan (Object Detection)")
            }
        }
        state.hazardError?.let { err ->
            Text("⚠️ $err", style = MaterialTheme.typography.labelSmall, color = GibberRed)
        }
        if (state.hazardLabels.isNotEmpty()) {
            Card(
                colors   = CardDefaults.cardColors(containerColor = GibberRed.copy(alpha = 0.08f)),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text("🔍 Detected Objects", style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold, color = GibberRed)
                    state.hazardLabels.forEach { label ->
                        Text("• $label", style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurface)
                    }
                }
            }
        }

        Spacer(Modifier.height(24.dp))
    }
}

@Composable
private fun PentadCoherenceCard(pentad: PentadState) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors   = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.12f)
        ),
    ) {
        Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text       = "Pentad Situation Coherence",
                    style      = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold,
                    color      = GibberGreen,
                )
                val coherencePct = (pentad.situationCoherence * 100).roundToInt()
                val cohColor = when {
                    coherencePct >= 80 -> GibberGreen
                    coherencePct >= 50 -> GibberAmber
                    else -> GibberRed
                }
                Text(
                    text       = "$coherencePct%",
                    style      = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color      = cohColor,
                )
            }
            Text(
                text  = "U·Ψ_n = Ψ_{n+1}  →  driving all 10 information gaps toward zero",
                style = MaterialTheme.typography.labelSmall,
                color = OnSurfaceDim,
                fontFamily = FontFamily.Monospace,
            )

            // 5 body φ bars
            PentadBodyRow("Ψ_univ  (sensors)",  pentad.phiUniv,  GibberBlue)
            PentadBodyRow("Ψ_brain (biology)",  pentad.phiBrain, GibberRed)
            PentadBodyRow("Ψ_human (intent)",   pentad.phiHuman, GibberAmber)
            PentadBodyRow("Ψ_AI    (precision)",pentad.phiAI,    GibberGreen)
            PentadBodyRow("β·C     (trust)",     pentad.phiTrust, GibberBlue)

            Divider(color = MaterialTheme.colorScheme.outline)

            // Top 3 largest gaps
            val topGaps = pentad.pairwiseGaps.sortedByDescending { it.second }.take(3)
            Text("Largest ΔI gaps:", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
            topGaps.forEach { (label, gap) ->
                val gapColor = when { gap > 0.4f -> GibberRed; gap > 0.2f -> GibberAmber; else -> GibberGreen }
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(label, style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                    Text("ΔI = %.2f".format(gap), style = MaterialTheme.typography.labelSmall,
                        fontFamily = FontFamily.Monospace, color = gapColor)
                }
            }

            if (!pentad.isBraidStable) {
                Text(
                    text  = "⚠ BRAID UNSTABLE: φ_trust < ${(PentadState.TRUST_PHI_MIN * 100).roundToInt()}%. " +
                        "System coherence not guaranteed.",
                    style = MaterialTheme.typography.labelSmall,
                    color = GibberRed,
                    fontWeight = FontWeight.Bold,
                )
            }
        }
    }
}

@Composable
private fun PentadBodyRow(label: String, phi: Float, color: Color) {
    Row(
        modifier          = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text(label, style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim,
            modifier = Modifier.width(150.dp))
        Box(
            modifier = Modifier
                .height(6.dp)
                .weight(1f)
                .clip(RoundedCornerShape(3.dp))
                .background(color.copy(alpha = 0.2f))
        ) {
            Box(
                modifier = Modifier
                    .fillMaxSize(phi.coerceIn(0f, 1f))
                    .clip(RoundedCornerShape(3.dp))
                    .background(color)
            )
        }
        Text("%.0f%%".format(phi * 100), style = MaterialTheme.typography.labelSmall,
            fontFamily = FontFamily.Monospace, color = color, modifier = Modifier.width(36.dp))
    }
}

@Composable
private fun SituationReportCard(report: SituationReport, role: UserRole) {
    val severityColor = severityColor(report.severity)

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors   = CardDefaults.cardColors(containerColor = severityColor.copy(alpha = 0.08f)),
    ) {
        Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text       = "${role.emoji} ${report.severity.name} — ${role.displayName}",
                    style      = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold,
                    color      = severityColor,
                )
                Text(
                    text  = "conf %.0f%%".format(report.confidence * 100),
                    style = MaterialTheme.typography.labelSmall,
                    color = OnSurfaceDim,
                )
            }

            Text(
                text  = report.narrative,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurface,
            )

            if (report.actions.isNotEmpty()) {
                Divider(color = MaterialTheme.colorScheme.outline)
                Text("Recommended Actions:", style = MaterialTheme.typography.labelSmall,
                    color = severityColor, fontWeight = FontWeight.Bold)
                report.actions.forEach { action ->
                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text("▶", style = MaterialTheme.typography.bodySmall, color = severityColor)
                        Text(action, style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurface)
                    }
                }
            }
        }
    }

    // Individual findings
    Divider(color = MaterialTheme.colorScheme.outline)
    Text(
        text  = "Sensor-by-Sensor Breakdown",
        style = MaterialTheme.typography.titleSmall,
        fontWeight = FontWeight.Bold,
        color = MaterialTheme.colorScheme.onSurface,
    )

    report.findings.sortedByDescending { it.severity.ordinal }.forEach { finding ->
        FindingCard(finding)
    }
}

@Composable
private fun FindingCard(finding: com.gibbernode.interpret.Finding) {
    val color = severityColor(finding.severity)
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
    ) {
        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Text(finding.sensor, style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Bold, color = color)
                Text(finding.rawValue, style = MaterialTheme.typography.labelSmall,
                    fontFamily = FontFamily.Monospace, color = OnSurfaceDim)
            }
            Text(finding.context, style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurface)
            if (finding.action != null) {
                Text("▶ ${finding.action}", style = MaterialTheme.typography.labelSmall,
                    color = color, fontWeight = FontWeight.SemiBold)
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 2 — Protocol ↔ Natural Language
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun ProtocolTab(state: TranslateUiState, vm: TranslateViewModel) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        // ── Role selector ─────────────────────────────────────────────────────
        RoleSelector(selected = state.role, onSelect = vm::selectRole)

        // ── Description ───────────────────────────────────────────────────────
        Card(
            colors = CardDefaults.cardColors(containerColor = SurfaceDark),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text("Bidirectional Protocol Bridge", style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold, color = GibberAmber)
                Text(
                    "Paste a Gibberlink payload for rich human interpretation, or type plain text " +
                    "(e.g. \"HR 112 SpO2 88 temp 38.9\") to build a protocol payload automatically.",
                    style = MaterialTheme.typography.bodySmall,
                    color = OnSurfaceDim,
                )
            }
        }

        // ── Input ─────────────────────────────────────────────────────────────
        OutlinedTextField(
            value         = state.protocolInput,
            onValueChange = vm::onProtocolInputChanged,
            placeholder   = {
                Text(
                    "VITALS:112:88:38.9\nor: HR 112 SpO2 88 temp 38.9",
                    style = MaterialTheme.typography.bodySmall,
                    fontFamily = FontFamily.Monospace,
                )
            },
            modifier  = Modifier.fillMaxWidth().height(100.dp),
            maxLines  = 5,
        )

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(
                onClick  = vm::translateProtocol,
                enabled  = state.protocolInput.isNotEmpty(),
                colors   = ButtonDefaults.buttonColors(containerColor = GibberAmber),
                modifier = Modifier.weight(1f),
            ) {
                Icon(Icons.Filled.SwapHoriz, contentDescription = null, tint = Color.Black)
                Spacer(Modifier.width(6.dp))
                Text(
                    text  = when (state.protocolDirection) {
                        TranslateDirection.MACHINE_TO_HUMAN -> "Decode → Human"
                        TranslateDirection.HUMAN_TO_MACHINE -> "Encode → Protocol"
                    },
                    color = Color.Black,
                    fontWeight = FontWeight.Bold,
                )
            }
        }

        // ── Result ────────────────────────────────────────────────────────────
        if (state.protocolResult != null) {
            val isEncoded = state.protocolDirection == TranslateDirection.HUMAN_TO_MACHINE
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors   = CardDefaults.cardColors(
                    containerColor = if (isEncoded)
                        GibberGreen.copy(alpha = 0.08f)
                    else
                        GibberAmber.copy(alpha = 0.08f)
                ),
            ) {
                Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text(
                        text  = if (isEncoded) "🔗 Encoded Gibberlink Payload" else "🌐 Human Interpretation",
                        style = MaterialTheme.typography.labelSmall,
                        color = if (isEncoded) GibberGreen else GibberAmber,
                        fontWeight = FontWeight.Bold,
                    )
                    Text(
                        text       = state.protocolResult,
                        style      = if (isEncoded) MaterialTheme.typography.bodySmall else MaterialTheme.typography.bodyMedium,
                        fontFamily = if (isEncoded) FontFamily.Monospace else null,
                        color      = MaterialTheme.colorScheme.onSurface,
                    )
                }
            }
        }

        Divider(color = MaterialTheme.colorScheme.outline)

        // ── Protocol reference card ────────────────────────────────────────────
        ProtocolReferenceCard()

        // ── Pentad coherence ──────────────────────────────────────────────────
        PentadCoherenceCard(pentad = state.pentad)

        Spacer(Modifier.height(24.dp))
    }
}

@Composable
private fun ProtocolReferenceCard() {
    Card(
        colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text("Natural Language → Payload Examples", style = MaterialTheme.typography.labelMedium,
                fontWeight = FontWeight.Bold, color = GibberGreen)
            val examples = listOf(
                "HR 112 SpO2 88 temp 38.9"    to "VITALS:112:88:38.9000",
                "GPS 51.5074 -0.1278"          to "GPS:51.5074:-0.1278:0.0000:...",
                "allergy penicillin severe"    to "ALLERGY:ANON:penicillin:SEVERE",
                "ALERT fire in building B"     to "ALERT:ALERT:fire in building B",
                "env 1013 22 50"               to "ENV:1013.0000:22.0000:50.0000",
            )
            examples.forEach { (input, output) ->
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text("\"$input\"", style = MaterialTheme.typography.labelSmall,
                        color = OnSurfaceDim, modifier = Modifier.weight(1f))
                    Text("→", style = MaterialTheme.typography.labelSmall, color = GibberAmber)
                    Text(output, style = MaterialTheme.typography.labelSmall,
                        fontFamily = FontFamily.Monospace, color = GibberGreen,
                        modifier = Modifier.weight(1f))
                }
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Shared sub-composables
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun RoleSelector(selected: UserRole, onSelect: (UserRole) -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Text("Active Role  (shapes all interpretation)", style = MaterialTheme.typography.labelSmall,
            color = OnSurfaceDim)
        LazyRow(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            items(UserRole.entries) { role ->
                FilterChip(
                    selected = selected == role,
                    onClick  = { onSelect(role) },
                    label    = { Text("${role.emoji} ${role.displayName}", fontSize = 11.sp) },
                    colors   = FilterChipDefaults.filterChipColors(
                        selectedContainerColor     = roleColor(role).copy(alpha = 0.2f),
                        selectedLabelColor         = roleColor(role),
                    ),
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun LanguagePicker(
    languages: List<Pair<String, String>>,
    selected:  String,
    onSelected: (String) -> Unit,
) {
    var expanded by remember { mutableStateOf(false) }
    val selectedName = languages.firstOrNull { it.first == selected }?.second ?: selected

    ExposedDropdownMenuBox(
        expanded = expanded,
        onExpandedChange = { expanded = !expanded },
        modifier = Modifier.fillMaxWidth(),
    ) {
        OutlinedTextField(
            value         = "Target language: $selectedName",
            onValueChange = {},
            readOnly      = true,
            trailingIcon  = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
            modifier      = Modifier.menuAnchor().fillMaxWidth(),
        )
        ExposedDropdownMenu(
            expanded         = expanded,
            onDismissRequest = { expanded = false },
        ) {
            languages.forEach { (code, name) ->
                DropdownMenuItem(
                    text    = { Text("$name  [$code]") },
                    onClick = {
                        onSelected(code)
                        expanded = false
                    },
                )
            }
        }
    }
}

// ── Colour helpers ────────────────────────────────────────────────────────────

private fun roleColor(role: UserRole): Color = when (role) {
    UserRole.NURSE          -> GibberRed
    UserRole.FIRST_RESPONDER -> GibberAmber
    UserRole.ENGINEER       -> GibberBlue
    UserRole.SCIENTIST      -> GibberGreen
    UserRole.DEFAULT        -> GibberGreen
}

private fun severityColor(severity: Severity): Color = when (severity) {
    Severity.OK       -> GibberGreen
    Severity.CAUTION  -> GibberBlue
    Severity.WARNING  -> GibberAmber
    Severity.CRITICAL -> GibberRed
}

// ─────────────────────────────────────────────────────────────────────────────
// Assistant adaptive card composables (mirrors DashboardScreen pattern)
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
