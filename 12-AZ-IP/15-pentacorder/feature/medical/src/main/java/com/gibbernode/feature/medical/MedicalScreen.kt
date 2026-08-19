package com.gibbernode.feature.medical

import androidx.compose.animation.animateColorAsState
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
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Sensors
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Emergency
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.LocalHospital
import androidx.compose.material.icons.filled.Phone
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Divider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.ScrollableTabRow
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.gibbernode.gibberwave.CardSeverity
import com.gibbernode.gibberwave.InjectedCard
import com.gibbernode.ui.GibberAmber
import com.gibbernode.ui.GibberBlue
import com.gibbernode.ui.GibberGreen
import com.gibbernode.ui.GibberRed
import com.gibbernode.ui.OnSurfaceDim
import com.gibbernode.ui.SurfaceDark

/**
 * MedicalScreen — Medical / Health / First Aid / First Responder tab
 *
 * Six sub-tabs:
 *  0 — Vitals     : manual vital entry, NEWS2 score, φ-homeostasis, acoustic broadcast
 *  1 — First Aid  : quick-access emergency protocol cards (CPR, choking, bleeding, etc.)
 *  2 — Responder  : first-responder mode (RED mode + GPS + emergency call)
 *  3 — 🧠 Neuro   : tremor score, dominant frequency, session trend (TremorAdvisor)
 *  4 — 🩸 Skin    : pallor + jaundice screen with medical disclaimer (SkinColorAdvisor)
 *  5 — 💓 rPPG    : contact-free HR + HRV from camera green channel (PPGAdvisor)
 */
@Composable
fun MedicalScreen(
    onActivateRedMode: () -> Unit = {},
    viewModel: MedicalViewModel = hiltViewModel(),
) {
    val state         by viewModel.state.collectAsStateWithLifecycle()
    val adaptiveState by viewModel.adaptiveState.collectAsStateWithLifecycle()
    var tab by remember { mutableIntStateOf(0) }

    Column(modifier = Modifier.fillMaxSize()) {
        ScrollableTabRow(
            selectedTabIndex = tab,
            edgePadding      = 0.dp,
        ) {
            Tab(selected = tab == 0, onClick = { tab = 0 }, text = {
                Text("❤️ Vitals", fontSize = 13.sp)
            })
            Tab(selected = tab == 1, onClick = { tab = 1 }, text = {
                Text("🩺 First Aid", fontSize = 13.sp)
            })
            Tab(selected = tab == 2, onClick = { tab = 2 }, text = {
                Text("🚨 Responder", fontSize = 13.sp)
            })
            Tab(selected = tab == 3, onClick = { tab = 3 }, text = {
                Text("🧠 Neuro", fontSize = 13.sp)
            })
            Tab(selected = tab == 4, onClick = { tab = 4 }, text = {
                Text("🩸 Skin", fontSize = 13.sp)
            })
            Tab(selected = tab == 5, onClick = { tab = 5 }, text = {
                Text("💓 rPPG", fontSize = 13.sp)
            })
        }

        // ── Assistant hint + adaptive cards ───────────────────────────────────
        adaptiveState.screenHints["medical"]?.let { hint ->
            AssistantHintBanner(hint = hint, onDismiss = viewModel::clearMedicalHint)
        }
        adaptiveState.dashboardCards.forEach { card ->
            AdaptiveInjectedCard(card = card, onDismiss = { viewModel.removeAdaptiveCard(card.id) })
        }

        when (tab) {
            0 -> VitalsTab(state = state, vm = viewModel)
            1 -> FirstAidTab()
            2 -> ResponderTab(state = state, onActivateRedMode = onActivateRedMode)
            3 -> NeuroTab(state = state, vm = viewModel)
            4 -> SkinTab(state = state, vm = viewModel)
            5 -> RppgTab(state = state, vm = viewModel)
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 0 — Vitals
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun VitalsTab(state: MedicalUiState, vm: MedicalViewModel) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        // Disclaimer
        Text(
            text  = "⚠ Reference tool only — not a certified medical device. Call 999/911/112 for emergencies.",
            style = MaterialTheme.typography.labelSmall,
            color = OnSurfaceDim,
        )

        // ── Vital inputs ──────────────────────────────────────────────────────
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
        ) {
            Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("Enter Vitals", style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface)

                VitalField("Heart Rate (bpm)",         state.hrInput,   "e.g. 72",  KeyboardType.Number,   vm::onHrChanged)
                VitalField("SpO₂ (%)",                 state.spo2Input, "e.g. 98",  KeyboardType.Number,   vm::onSpo2Changed)
                VitalField("Temperature (°C)",         state.tempInput, "e.g. 37.0",KeyboardType.Decimal,  vm::onTempChanged)
                VitalField("Resp Rate (breaths/min)",  state.respInput, "e.g. 16",  KeyboardType.Number,   vm::onRespChanged)

                // Consciousness switch
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text("Consciousness", style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text(
                            text  = if (state.isAlert) "Alert" else "CVPU",
                            color = if (state.isAlert) GibberGreen else GibberRed,
                            style = MaterialTheme.typography.bodySmall,
                            fontWeight = FontWeight.Bold,
                        )
                        Switch(
                            checked  = state.isAlert,
                            onCheckedChange = vm::onConsciousnessChanged,
                            colors   = SwitchDefaults.colors(checkedThumbColor = GibberGreen),
                        )
                    }
                }

                // Sensor HR note
                state.sensorHrBpm?.let { bpm ->
                    Text(
                        text  = "📡 Sensor HR: $bpm bpm (Samsung Health / TYPE_HEART_RATE)",
                        style = MaterialTheme.typography.labelSmall,
                        color = GibberBlue,
                    )
                }

                // Action buttons
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(
                        onClick = vm::broadcastVitals,
                        colors  = ButtonDefaults.buttonColors(containerColor = GibberBlue),
                        modifier = Modifier.weight(1f),
                    ) {
                        Icon(Icons.Filled.Sensors, contentDescription = null, modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(4.dp))
                        Text("Broadcast BLUE", fontSize = 13.sp)
                    }
                    Button(
                        onClick = vm::clearVitals,
                        colors  = ButtonDefaults.buttonColors(containerColor = SurfaceDark),
                        modifier = Modifier.weight(1f),
                    ) {
                        Icon(Icons.Filled.Clear, contentDescription = null, modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(4.dp))
                        Text("Clear", fontSize = 13.sp)
                    }
                }

                state.lastBroadcastPayload?.let { p ->
                    Text(
                        text  = "✓ Sent: $p",
                        style = MaterialTheme.typography.labelSmall,
                        color = GibberGreen,
                    )
                }
            }
        }

        // ── NEWS2 Score ───────────────────────────────────────────────────────
        state.news2Score?.let { result ->
            News2Card(result)
        }

        // ── φ-homeostasis ─────────────────────────────────────────────────────
        state.phiBio?.let { phi ->
            PhiCard(phi)
        }

        Spacer(Modifier.height(24.dp))
    }
}

@Composable
private fun VitalField(
    label: String,
    value: String,
    placeholder: String,
    keyboardType: KeyboardType,
    onValueChange: (String) -> Unit,
) {
    OutlinedTextField(
        value         = value,
        onValueChange = onValueChange,
        label         = { Text(label, fontSize = 12.sp) },
        placeholder   = { Text(placeholder, fontSize = 12.sp) },
        singleLine    = true,
        modifier      = Modifier.fillMaxWidth(),
        keyboardOptions = KeyboardOptions(keyboardType = keyboardType),
    )
}

@Composable
private fun News2Card(result: News2Result) {
    val riskColor = Color(result.risk.colorHex)
    val animColor by animateColorAsState(
        targetValue = riskColor,
        animationSpec = tween(500),
        label = "news2_color",
    )

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text  = "NEWS2 Score",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface,
                )
                Box(
                    contentAlignment = Alignment.Center,
                    modifier         = Modifier.size(52.dp).clip(CircleShape).background(animColor),
                ) {
                    Text(
                        text  = "${result.score}",
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold,
                        color = Color.Black,
                    )
                }
            }
            Spacer(Modifier.height(8.dp))
            Text(
                text  = "Risk: ${result.risk.label}",
                style = MaterialTheme.typography.bodyMedium,
                color = animColor,
                fontWeight = FontWeight.Bold,
            )
            Text(
                text  = result.risk.action,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurface,
            )

            // NEWS2 table legend
            Spacer(Modifier.height(12.dp))
            Divider(color = MaterialTheme.colorScheme.outline, thickness = 0.5.dp)
            Spacer(Modifier.height(8.dp))
            Text("Score guide", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
            Spacer(Modifier.height(4.dp))
            News2Row("0",   "Minimum",  "Normal monitoring",             Color(0xFF00C853))
            News2Row("1–4", "Low",      "Increase monitoring frequency", Color(0xFFFFAB00))
            News2Row("5–6", "Medium",   "Urgent clinical review",        Color(0xFFFF6D00))
            News2Row("≥7",  "HIGH",     "EMERGENCY — call 999/911/112",  Color(0xFFFF1744))
        }
    }
}

@Composable
private fun News2Row(score: String, risk: String, action: String, color: Color) {
    Row(
        modifier              = Modifier.fillMaxWidth().padding(vertical = 2.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalAlignment     = Alignment.CenterVertically,
    ) {
        Text(score,  style = MaterialTheme.typography.labelSmall, color = color,
            fontWeight = FontWeight.Bold, modifier = Modifier.width(28.dp))
        Text(risk,   style = MaterialTheme.typography.labelSmall, color = color, modifier = Modifier.width(60.dp))
        Text(action, style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
    }
}

@Composable
private fun PhiCard(phi: PhiResult) {
    val statusColor = when (phi.status) {
        PhiStatus.AT_FIXED_POINT -> GibberGreen
        PhiStatus.MILD_DEVIATION -> GibberAmber
        PhiStatus.OUTSIDE_BASIN  -> GibberRed
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors   = CardDefaults.cardColors(
            containerColor = statusColor.copy(alpha = 0.08f)
        ),
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text  = "φ-Homeostasis  (Unitary-Manifold)",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold,
                color = statusColor,
            )
            Spacer(Modifier.height(8.dp))
            Text(
                text  = phi.status.label,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Bold,
                color = statusColor,
            )
            Text(
                text  = phi.status.description,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurface,
            )
            Spacer(Modifier.height(8.dp))
            PhiRow("φ_hr",   phi.phiHr,   "HR / 70 bpm")
            PhiRow("φ_spo2", phi.phiSpo2, "SpO₂ / 98%")
            PhiRow("φ_temp", phi.phiTemp, "Temp / 37°C")
            PhiRow("φ_bio",  phi.phiBio,  "composite mean")
            Text(
                text  = "δφ = %.4f".format(phi.delta),
                style = MaterialTheme.typography.labelSmall,
                color = if (phi.delta < 0) GibberRed else statusColor,
                fontWeight = FontWeight.Bold,
            )
        }
    }
}

@Composable
private fun PhiRow(symbol: String, value: Float, note: String) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 1.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text(symbol, style = MaterialTheme.typography.labelSmall, color = GibberAmber,
            fontWeight = FontWeight.Bold, modifier = Modifier.width(52.dp))
        Text("%.4f".format(value), style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurface, modifier = Modifier.width(64.dp))
        Text(note, style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 1 — First Aid Protocols
// ─────────────────────────────────────────────────────────────────────────────

private data class Protocol(val emoji: String, val title: String, val steps: List<String>)

private val PROTOCOLS = listOf(
    Protocol("❤️‍🔥", "CPR — Adult", listOf(
        "1. Check for danger. Make area safe.",
        "2. Check responsiveness — tap shoulders, shout.",
        "3. Call 999/911/112 or send someone.",
        "4. 30 chest compressions: heel of hand, centre of chest, 5–6 cm deep, 100–120/min.",
        "5. 2 rescue breaths: tilt head, lift chin, seal lips, blow 1 sec.",
        "6. Repeat 30:2 until AED arrives or patient recovers.",
        "⚡ AED: turn on, follow voice prompts. Shock if advised.",
    )),
    Protocol("🍬", "Choking — Adult", listOf(
        "1. Encourage coughing if able.",
        "2. 5 firm back blows between shoulder blades.",
        "3. 5 abdominal thrusts: stand behind, fist above navel, pull sharply in and up.",
        "4. Alternate 5 back blows + 5 abdominal thrusts.",
        "5. If unconscious → CPR. Check mouth before breaths.",
        "⚠ Infant choking: face-down on your forearm, 5 back blows, 5 chest thrusts (NOT abdominal).",
    )),
    Protocol("🩸", "Severe Bleeding", listOf(
        "1. Call 999/911/112.",
        "2. Apply direct pressure with clean cloth or dressing.",
        "3. Press hard and continuously — do NOT lift dressing.",
        "4. Elevate limb if possible.",
        "5. Tourniquet if limb amputation or pressure fails — note time applied.",
        "6. Lay patient down, keep warm, monitor for shock.",
        "⚠ Do NOT remove embedded objects — pad around them.",
    )),
    Protocol("🔥", "Burns", listOf(
        "1. Cool burn under cool running water for 20 minutes.",
        "2. Remove clothing/jewellery near burn (NOT if stuck to skin).",
        "3. Cover with clean non-fluffy material (cling film ideal).",
        "4. Do NOT burst blisters, apply butter/toothpaste.",
        "5. For facial burns — call 999/911/112.",
        "⚠ Chemical burns: remove contaminated clothing (with gloves), wash for 20 min.",
    )),
    Protocol("😰", "Shock", listOf(
        "1. Call 999/911/112.",
        "2. Lay patient flat; raise legs ~30 cm (not if head/spine/leg injury).",
        "3. Keep warm — blanket over, NOT under.",
        "4. Do NOT give food or drink.",
        "5. Reassure, monitor breathing and pulse every 5 min.",
        "6. If unconscious and breathing — recovery position.",
    )),
    Protocol("🐝", "Anaphylaxis", listOf(
        "1. Call 999/911/112 immediately.",
        "2. Administer adrenaline auto-injector (EpiPen) — outer thigh, through clothing.",
        "3. Lay patient flat; raise legs (or sit up if breathing difficulty).",
        "4. Second auto-injector after 5–15 min if no improvement.",
        "5. If unconscious and breathing → recovery position.",
        "6. CPR if cardiac arrest.",
    )),
    Protocol("🧠", "Stroke — FAST", listOf(
        "FAST assessment:",
        "F — Face drooping on one side?",
        "A — Arms: can they raise both?",
        "S — Speech slurred or confused?",
        "T — Time: call 999/911/112 NOW.",
        "• Do NOT give food or drink.",
        "• Note exact time symptoms started.",
        "• If unconscious and breathing → recovery position.",
    )),
    Protocol("⚡", "Seizure", listOf(
        "1. Protect from injury — clear the area, cushion head.",
        "2. Do NOT restrain. Do NOT put anything in mouth.",
        "3. Note time seizure started.",
        "4. Call 999 if: first seizure, > 5 min, no recovery after 5 min, another seizure, pregnant, injured.",
        "5. After seizure → recovery position. Stay with patient.",
    )),
)

@Composable
private fun FirstAidTab() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        Text(
            text  = "⚠ Reference only. Always call 999/911/112 for life-threatening emergencies.",
            style = MaterialTheme.typography.labelSmall,
            color = OnSurfaceDim,
        )
        PROTOCOLS.forEach { proto ->
            ProtocolCard(proto)
        }
        Spacer(Modifier.height(24.dp))
    }
}

@Composable
private fun ProtocolCard(proto: Protocol) {
    var expanded by remember { mutableStateOf(false) }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
        onClick  = { expanded = !expanded },
        shape    = RoundedCornerShape(12.dp),
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier              = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment     = Alignment.CenterVertically,
            ) {
                Row(
                    verticalAlignment   = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    Text(proto.emoji, fontSize = 22.sp)
                    Text(proto.title, style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onSurface)
                }
                Text(
                    text  = if (!expanded) "▼" else "▲",
                    style = MaterialTheme.typography.labelSmall,
                    color = OnSurfaceDim,
                )
            }

            if (expanded) {
                Spacer(Modifier.height(10.dp))
                Divider(color = MaterialTheme.colorScheme.outline, thickness = 0.5.dp)
                Spacer(Modifier.height(8.dp))
                proto.steps.forEach { step ->
                    Text(
                        text  = step,
                        style = MaterialTheme.typography.bodySmall,
                        color = if (step.startsWith("⚠") || step.startsWith("⚡"))
                                    GibberAmber
                                else
                                    MaterialTheme.colorScheme.onSurface,
                        modifier = Modifier.padding(vertical = 2.dp),
                    )
                }
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 2 — First Responder
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun ResponderTab(state: MedicalUiState, onActivateRedMode: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(
            text  = "First Responder Mode — S24 Ultra",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = GibberRed,
        )
        Text(
            text  = "Activate RED mode for air-gap GPS broadcast. Works without LTE, WiFi, or Bluetooth.",
            style = MaterialTheme.typography.bodySmall,
            color = OnSurfaceDim,
        )

        // ── SOS / RED mode button ─────────────────────────────────────────────
        Button(
            onClick = onActivateRedMode,
            colors  = ButtonDefaults.buttonColors(containerColor = GibberRed),
            modifier = Modifier.fillMaxWidth().height(56.dp),
            shape   = RoundedCornerShape(14.dp),
        ) {
            Icon(Icons.Filled.Emergency, contentDescription = null)
            Spacer(Modifier.width(8.dp))
            Text("ACTIVATE RED MODE — GPS BROADCAST", fontWeight = FontWeight.Bold)
        }

        // ── Emergency call ────────────────────────────────────────────────────
        Button(
            onClick = { /* handled by MainActivity via Intent */ },
            colors  = ButtonDefaults.buttonColors(containerColor = Color(0xFFFF6D00)),
            modifier = Modifier.fillMaxWidth().height(56.dp),
            shape   = RoundedCornerShape(14.dp),
        ) {
            Icon(Icons.Filled.Phone, contentDescription = null)
            Spacer(Modifier.width(8.dp))
            Text("CALL 999 / 911 / 112", fontWeight = FontWeight.Bold)
        }

        Divider(color = MaterialTheme.colorScheme.outline)

        // ── Scene assessment checklist ────────────────────────────────────────
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Icon(Icons.Filled.Shield, contentDescription = null, tint = GibberAmber, modifier = Modifier.size(20.dp))
                    Text("Scene Assessment (SAFE-DR)", style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface)
                }
                Spacer(Modifier.height(8.dp))
                listOf(
                    "S — Situation: what happened?",
                    "A — Airway: is it open?",
                    "F — Fire / hazards: is the scene safe?",
                    "E — Environment: weather, terrain, crowds",
                    "D — Danger: ongoing threat to you or patient?",
                    "R — Response: is the patient conscious?",
                ).forEach { item ->
                    Text(item, style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurface,
                        modifier = Modifier.padding(vertical = 2.dp))
                }
            }
        }

        // ── Triage card ───────────────────────────────────────────────────────
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Icon(Icons.Filled.LocalHospital, contentDescription = null, tint = GibberBlue, modifier = Modifier.size(20.dp))
                    Text("START Triage Colours", style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface)
                }
                Spacer(Modifier.height(8.dp))
                TriageRow("🟢 Green",  "Minor",       "Walking wounded — treat last")
                TriageRow("🟡 Yellow", "Delayed",     "Serious but stable — can wait")
                TriageRow("🔴 Red",    "Immediate",   "Life-threatening — treat first")
                TriageRow("⬛ Black",  "Expectant",   "Fatal or unsurvivable without resources")
            }
        }

        // ── Acoustic broadcast info ───────────────────────────────────────────
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Icon(Icons.Filled.Favorite, contentDescription = null, tint = GibberGreen, modifier = Modifier.size(20.dp))
                    Text("Pentacorder Broadcast Payloads", style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface)
                }
                Spacer(Modifier.height(6.dp))
                Text(
                    "RED mode broadcasts GPS + battery to nearby devices and overhead drones — no LTE or WiFi required. BLUE mode broadcasts vitals (HR, SpO₂, temp) to bedside receivers within 1 m.",
                    style = MaterialTheme.typography.bodySmall,
                    color = OnSurfaceDim,
                )
                if (state.news2Score != null) {
                    Spacer(Modifier.height(6.dp))
                    Text(
                        text  = "Current NEWS2 = ${state.news2Score.score} (${state.news2Score.risk.label})",
                        style = MaterialTheme.typography.labelSmall,
                        color = Color(state.news2Score.risk.colorHex),
                        fontWeight = FontWeight.Bold,
                    )
                }
            }
        }

        Spacer(Modifier.height(24.dp))
    }
}

@Composable
private fun TriageRow(color: String, level: String, note: String) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 2.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text(color,  style = MaterialTheme.typography.bodySmall, modifier = Modifier.width(72.dp))
        Text(level,  style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onSurface, modifier = Modifier.width(72.dp))
        Text(note,   style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
    }
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

// ─────────────────────────────────────────────────────────────────────────────
// Tab 3 — Neuro (Tremor Screening)
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun NeuroTab(state: MedicalUiState, vm: MedicalViewModel) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Card(colors = CardDefaults.cardColors(containerColor = GibberAmber.copy(alpha = 0.08f)),
            modifier = Modifier.fillMaxWidth()) {
            Text(
                "⚠️ Screening only — not a medical diagnosis. This tool measures pen stroke " +
                "variability as a tremor proxy. Consult a neurologist for clinical evaluation.",
                style    = MaterialTheme.typography.labelSmall,
                color    = OnSurfaceDim,
                modifier = Modifier.padding(12.dp),
            )
        }

        state.tremorScore?.let { score ->
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Tremor Score", style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(8.dp))
                    Row(modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween) {
                        Column {
                            Text("%.1f / 10".format(score),
                                style = MaterialTheme.typography.headlineMedium,
                                fontWeight = FontWeight.Bold,
                                color = when {
                                    score < 2f -> GibberGreen
                                    score < 5f -> GibberAmber
                                    else       -> GibberRed
                                })
                            state.tremorSeverity?.let { s ->
                                Text(s, style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
                            }
                        }
                        state.tremorFreqHz?.let { hz ->
                            Column(horizontalAlignment = Alignment.End) {
                                Text("%.1f Hz".format(hz), style = MaterialTheme.typography.titleSmall,
                                    fontWeight = FontWeight.Bold)
                                Text("Dominant freq", style = MaterialTheme.typography.labelSmall,
                                    color = OnSurfaceDim)
                            }
                        }
                    }
                }
            }
        }

        if (state.tremorHistory.size >= 2) {
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Session Trend (${state.tremorHistory.size} readings)",
                        style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(8.dp))
                    androidx.compose.foundation.Canvas(
                        modifier = Modifier.fillMaxWidth().height(60.dp)
                    ) {
                        val w    = size.width; val h = size.height
                        val hist = state.tremorHistory
                        val minV = hist.min().coerceAtMost(0f)
                        val maxV = hist.max().coerceAtLeast(0.1f)
                        val rng  = maxV - minV
                        val step = w / (hist.size - 1)
                        for (i in 1 until hist.size) {
                            val x0 = (i - 1) * step; val x1 = i * step
                            val y0 = h * (1f - (hist[i - 1] - minV) / rng)
                            val y1 = h * (1f - (hist[i]     - minV) / rng)
                            drawLine(color = GibberBlue,
                                start = androidx.compose.ui.geometry.Offset(x0, y0),
                                end   = androidx.compose.ui.geometry.Offset(x1, y1),
                                strokeWidth = 2f)
                        }
                    }
                }
            }
        }

        Button(
            onClick  = { vm.startTremorTest() },
            enabled  = !state.tremorRunning,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(if (state.tremorRunning) "⏳ Measuring…" else "▶ Test Again")
        }

        Text("Instructions: grip S Pen normally, write your signature twice on the screen. " +
            "The analyser measures velocity variance across both strokes.",
            style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 4 — Skin (Pallor / Jaundice Screen)
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun SkinTab(state: MedicalUiState, vm: MedicalViewModel) {
    val lifecycleOwner = LocalLifecycleOwner.current
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Card(colors = CardDefaults.cardColors(containerColor = GibberRed.copy(alpha = 0.08f)),
            modifier = Modifier.fillMaxWidth()) {
            Text(
                "⚠️ NOT FOR CLINICAL USE. This feature provides a rough optical estimate only. " +
                "Camera RGB values vary with lighting, skin tone, and camera calibration. " +
                "Do not use for medical diagnosis. Always consult a qualified healthcare professional.",
                style    = MaterialTheme.typography.labelSmall,
                color    = OnSurfaceDim,
                modifier = Modifier.padding(12.dp),
            )
        }

        state.pallorIndex?.let { _ ->
            Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Skin Screen Result", style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(8.dp))
                    Row(modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween) {
                        Column {
                            Text(state.pallorSeverity ?: "—",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold,
                                color = if (state.jaundiceFlagged) GibberAmber else GibberGreen)
                            if (state.jaundiceFlagged) {
                                Text("⚠️ Elevated yellow index",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = GibberAmber, fontWeight = FontWeight.Bold)
                            }
                        }
                        Column(horizontalAlignment = Alignment.End) {
                            Text("Confidence", style = MaterialTheme.typography.labelSmall,
                                color = OnSurfaceDim)
                            Text("%.0f%%".format(state.skinConfidence * 100f),
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.Bold)
                        }
                    }
                    state.skinAdvice?.let { advice ->
                        Spacer(Modifier.height(8.dp))
                        Text(advice, style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        }

        Button(
            onClick  = { vm.bindSkinCamera(lifecycleOwner) },
            enabled  = !state.skinCapturing,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(if (state.skinCapturing) "⏳ Capturing…" else "📸 Capture Fingertip")
        }

        Text("Hold the tip of your index finger over the rear camera lens. " +
            "Ensure even lighting with no shadows. Tap 'Capture' to analyse.",
            style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 5 — rPPG (Contact-Free Heart Rate / HRV)
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun RppgTab(state: MedicalUiState, vm: MedicalViewModel) {
    val lifecycleOwner = LocalLifecycleOwner.current
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        // Disclaimer
        Card(
            colors   = CardDefaults.cardColors(containerColor = GibberRed.copy(alpha = 0.08f)),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(
                "⚠️ rPPG is a research tool only — NOT a certified medical device. " +
                "Green-channel photoplethysmography accuracy varies with skin tone, " +
                "lighting, and motion. Do not use for clinical decisions.",
                style    = MaterialTheme.typography.labelSmall,
                color    = OnSurfaceDim,
                modifier = Modifier.padding(12.dp),
            )
        }

        // Collection progress bar
        if (state.rppgRunning) {
            Card(
                colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier  = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text("📡 Collecting frames…", style = MaterialTheme.typography.bodyMedium)
                        Text("${(state.rppgProgress * 100).toInt()}%",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold,
                            color = GibberBlue)
                    }
                    Spacer(Modifier.height(8.dp))
                    androidx.compose.material3.LinearProgressIndicator(
                        progress = state.rppgProgress,
                        modifier = Modifier.fillMaxWidth(),
                        color    = GibberBlue,
                    )
                    Spacer(Modifier.height(4.dp))
                    Text(
                        "Keep device still, face well-lit. ~10 seconds total.",
                        style = MaterialTheme.typography.labelSmall,
                        color = OnSurfaceDim,
                    )
                }
            }
        }

        // Result card
        if (state.rppgBpm != null) {
            Card(
                colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("💓 rPPG Result", style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(8.dp))
                    Row(modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween) {
                        Column {
                            Text("${state.rppgBpm} bpm",
                                style = MaterialTheme.typography.headlineMedium,
                                fontWeight = FontWeight.Bold,
                                color = when {
                                    state.rppgBpm!! in 50..100 -> GibberGreen
                                    state.rppgBpm!! in 40..130 -> GibberAmber
                                    else                        -> GibberRed
                                })
                            Text("Heart rate estimate", style = MaterialTheme.typography.labelSmall,
                                color = OnSurfaceDim)
                        }
                        Column(horizontalAlignment = Alignment.End) {
                            Text("${state.rppgStressEmoji} ${state.rppgStressLevel ?: "—"}",
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.Bold)
                            Text("Stress level", style = MaterialTheme.typography.labelSmall,
                                color = OnSurfaceDim)
                        }
                    }
                    state.rppgRmssdMs?.let { rmssd ->
                        Spacer(Modifier.height(8.dp))
                        Row(modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween) {
                            Column {
                                Text("%.1f ms".format(rmssd),
                                    style = MaterialTheme.typography.titleSmall,
                                    fontWeight = FontWeight.Bold)
                                Text("HRV (RMSSD)", style = MaterialTheme.typography.labelSmall,
                                    color = OnSurfaceDim)
                            }
                            Column(horizontalAlignment = Alignment.End) {
                                Text("%.0f%%".format(state.rppgConfidence * 100f),
                                    style = MaterialTheme.typography.titleSmall,
                                    fontWeight = FontWeight.Bold)
                                Text("Confidence", style = MaterialTheme.typography.labelSmall,
                                    color = OnSurfaceDim)
                            }
                        }
                    }
                    if (state.rppgRrIntervals.isNotEmpty()) {
                        Spacer(Modifier.height(8.dp))
                        Text("RR intervals (${state.rppgRrIntervals.size}): " +
                            state.rppgRrIntervals.take(6).joinToString { "%.0f".format(it) + "ms" },
                            style = MaterialTheme.typography.labelSmall,
                            color = OnSurfaceDim)
                    }
                }
            }
        }

        // Start / Stop button
        if (state.rppgRunning) {
            Button(
                onClick  = { vm.stopRppgCamera() },
                colors   = ButtonDefaults.buttonColors(containerColor = GibberRed),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text("⏹ Stop")
            }
        } else {
            Button(
                onClick  = { vm.bindRppgCamera(lifecycleOwner) },
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text("💓 Start rPPG Measurement (~10 s)")
            }
        }

        Text(
            "Point the front camera at your face (face forward, even lighting). " +
            "The app collects ~300 frames then runs the PPGAdvisor peak-detection algorithm. " +
            "For fingertip rPPG: cover rear lens completely and hold steady.",
            style = MaterialTheme.typography.bodySmall,
            color = OnSurfaceDim,
        )
    }
}