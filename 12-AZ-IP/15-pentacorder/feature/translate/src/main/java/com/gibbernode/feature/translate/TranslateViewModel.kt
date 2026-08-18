package com.gibbernode.feature.translate

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.speech.tts.TextToSpeech
import android.util.Log
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gibbernode.gibberwave.AdaptiveState
import com.gibbernode.gibberwave.AdaptiveStateHolder
import com.gibbernode.gibberwave.ParsedPayload
import com.gibbernode.gibberwave.PayloadBuilder
import com.gibbernode.gibberwave.PayloadParser
import com.gibbernode.gibberwave.PentadSnapshot
import com.gibbernode.gibberwave.SensorBridge
import com.gibbernode.interpret.PentadState
import com.gibbernode.interpret.SensorSnapshot
import com.gibbernode.interpret.SensorInterpreter
import com.gibbernode.interpret.SituationReport
import com.gibbernode.interpret.Severity
import com.gibbernode.interpret.UserRole
import kotlinx.coroutines.flow.collectLatest
import com.google.mlkit.nl.languageid.LanguageIdentification
import com.google.mlkit.nl.translate.TranslateLanguage
import com.google.mlkit.nl.translate.Translation
import com.google.mlkit.nl.translate.TranslatorOptions
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.objects.ObjectDetection
import com.google.mlkit.vision.objects.defaults.ObjectDetectorOptions
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.tasks.await
import java.io.File
import java.util.Locale
import javax.inject.Inject

private const val TAG = "Pentacorder/TranslateVM"

/**
 * TranslateViewModel — powers the three-tab Pentacorder translator:
 *
 *   Tab 0 — Human↔Human Language Bridge
 *     ML Kit on-device translation (59 languages, no network).
 *     Language auto-detect → translate → optional TTS output.
 *     Quick-phrase cards for NURSE / RESPONDER / ENGINEER roles.
 *
 *   Tab 1 — Sensor → Situation Field Interpreter
 *     SensorInterpreter produces a role-aware SituationReport from live
 *     TricorderUiState values.  Reads are injected via [updateSensors].
 *
 *   Tab 2 — Protocol ↔ Natural Language Machine Bridge
 *     Bidirectional: Gibberlink payload → rich human narrative, AND
 *     natural-language text → structured Gibberlink payload.
 *
 * Pentad bodies driven here:
 *   Ψ_human (φ3) — user role selection
 *   Ψ_AI    (φ4) — translation confidence
 *   β·C     (φ5) — trust from calibration quality + sensor count
 */
@HiltViewModel
class TranslateViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
    private val sensorBridge: SensorBridge,
    private val adaptive: AdaptiveStateHolder,
) : ViewModel() {

    private val _state = MutableStateFlow(TranslateUiState())
    val state: StateFlow<TranslateUiState> = _state.asStateFlow()

    /** Live adaptive state (hints + injected cards) for this screen. */
    val adaptiveState: StateFlow<AdaptiveState> = adaptive.liveState

    private var tts: TextToSpeech? = null
    private val langIdClient = LanguageIdentification.getClient()

    // Keep a reference to the active ML Kit translator so it can be closed
    private var currentTranslator: com.google.mlkit.nl.translate.Translator? = null

    init {
        tts = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                Log.d(TAG, "TTS ready")
                _state.update { it.copy(ttsReady = true) }
            }
        }
        observeSensorBridge()
    }

    // ── SensorBridge observer — Ψ_univ + Ψ_brain ─────────────────────────────

    /**
     * Subscribe to the SensorBridge singleton.  Both TricorderViewModel and
     * MedicalViewModel push to this bridge so TranslateViewModel stays current
     * without any cross-module ViewModel references.
     */
    private fun observeSensorBridge() {
        // Ψ_univ — physical sensor coherence
        viewModelScope.launch {
            sensorBridge.sensorSnapshot.collectLatest { bridgeSnap ->
                bridgeSnap ?: return@collectLatest
                val snap = SensorSnapshot(
                    accelX       = bridgeSnap.accelX,
                    accelY       = bridgeSnap.accelY,
                    accelZ       = bridgeSnap.accelZ,
                    accelMag     = bridgeSnap.accelMag,
                    linAccX      = bridgeSnap.linAccX,
                    linAccY      = bridgeSnap.linAccY,
                    linAccZ      = bridgeSnap.linAccZ,
                    magMag       = bridgeSnap.magMag,
                    pressureHpa  = bridgeSnap.pressureHpa,
                    ambientTempC = bridgeSnap.ambientTempC,
                    humidityPct  = bridgeSnap.humidityPct,
                    lightLux     = bridgeSnap.lightLux,
                    latitude     = bridgeSnap.latitude,
                    longitude    = bridgeSnap.longitude,
                    altitude     = bridgeSnap.altitude,
                    gpsAccM      = bridgeSnap.gpsAccM,
                    gpsSpeedMs   = bridgeSnap.gpsSpeedMs,
                    batteryPct   = bridgeSnap.batteryPct,
                    batteryTempC = bridgeSnap.batteryTempC,
                    heartRateBpm = bridgeSnap.heartRateBpm,
                )
                updateSensors(snap)
            }
        }

        // Ψ_brain — biological coherence from HR / SpO₂
        viewModelScope.launch {
            sensorBridge.biometrics.collectLatest { bio ->
                bio ?: return@collectLatest
                updateBiometrics(bio.hrBpm, bio.spo2Pct)
            }
        }
    }

    // ── Role ─────────────────────────────────────────────────────────────────

    fun selectRole(role: UserRole) {
        _state.update { it.copy(role = role, quickPhrases = quickPhrasesFor(role)) }
        // Re-interpret sensors with new role immediately
        val snap = _state.value.sensorSnapshot
        if (snap != null) runInterpretation(snap, role)
    }

    // ── Tab 0: Human ↔ Human ─────────────────────────────────────────────────

    fun onSourceTextChanged(text: String) {
        _state.update { it.copy(humanSourceText = text, humanTranslated = null) }
    }

    fun onTargetLanguageChanged(lang: String) {
        _state.update { it.copy(targetLanguage = lang) }
        currentTranslator?.close()
        currentTranslator = null
    }

    /**
     * Auto-detect source language, build an ML Kit translator, and translate.
     * All ML Kit operations are on-device — no network call.
     */
    fun translateHumanText() {
        val text = _state.value.humanSourceText.trim()
        if (text.isEmpty()) return
        _state.update { it.copy(isTranslating = true, humanTranslated = null, translateError = null) }

        viewModelScope.launch {
            try {
                // Step 1 — identify language
                val detectedTag = langIdClient.identifyLanguage(text).await()
                val sourceLang = if (detectedTag == "und") TranslateLanguage.ENGLISH else detectedTag
                Log.d(TAG, "Detected language: $sourceLang")

                val targetLang = _state.value.targetLanguage

                // Step 2 — build translator
                val options = TranslatorOptions.Builder()
                    .setSourceLanguage(sourceLang)
                    .setTargetLanguage(targetLang)
                    .build()
                val translator = Translation.getClient(options)
                currentTranslator?.close()
                currentTranslator = translator

                // Step 3 — ensure model is downloaded (no-op if already local)
                translator.downloadModelIfNeeded().await()

                // Step 4 — translate
                val result = translator.translate(text).await()

                _state.update { s ->
                    s.copy(
                        isTranslating    = false,
                        humanTranslated  = result,
                        detectedSourceLang = sourceLang,
                        pentad = s.pentad.copy(
                            phiAI    = if (detectedTag != "und") PHI_AI_LANG_IDENTIFIED else PHI_AI_LANG_UNIDENTIFIED,
                            phiHuman = if (s.role != UserRole.DEFAULT) PHI_HUMAN_ROLE_ACTIVE else PHI_HUMAN_ROLE_DEFAULT,
                        ),
                    )
                }
                Log.d(TAG, "Translation: $result")
            } catch (e: Exception) {
                Log.e(TAG, "Translation failed: ${e.message}")
                _state.update { it.copy(
                    isTranslating = false,
                    translateError = "Translation failed: ${e.message}",
                )}
            }
        }
    }

    /**
     * Speak the last translated text using Android TextToSpeech.
     */
    fun speakTranslation() {
        val text = _state.value.humanTranslated ?: return
        val langTag = _state.value.targetLanguage
        val locale  = Locale.forLanguageTag(langTag)
        tts?.language = locale
        tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "translate")
    }

    /**
     * Speak a quick-phrase in the target language (pre-translated server-side
     * or via ML Kit on demand).
     */
    fun speakPhrase(phrase: QuickPhrase) {
        if (phrase.translated != null) {
            val langTag = _state.value.targetLanguage
            val locale  = Locale.forLanguageTag(langTag)
            tts?.language = locale
            tts?.speak(phrase.translated, TextToSpeech.QUEUE_FLUSH, null, "phrase")
        } else {
            // Trigger on-demand translation for the phrase
            _state.update { it.copy(humanSourceText = phrase.english) }
            translateHumanText()
        }
    }

    // ── Tab 1: Sensor → Situation ─────────────────────────────────────────────

    /**
     * Called by TricorderViewModel (via the shared SensorBridge singleton)
     * whenever sensor readings change.
     */
    fun updateSensors(snap: SensorSnapshot) {
        _state.update { it.copy(sensorSnapshot = snap) }
        runInterpretation(snap, _state.value.role)
    }

    /**
     * Update Ψ_brain (biological coherence) from HR and SpO₂.
     * Called via SensorBridge when MedicalViewModel receives new vitals.
     *
     * Normalisation:
     *   φ_hr   = 1 − |HR − 75| / 75   (75 bpm = homeostatic set-point)
     *   φ_spo2 = (SpO₂ − 85) / 15     (85 % → 0, 100 % → 1)
     *   Ψ_brain = mean(φ_hr, φ_spo2) clamped to [TRUST_PHI_MIN, 1.0]
     */
    fun updateBiometrics(hrBpm: Int?, spo2Pct: Int?) {
        val hr   = hrBpm   ?: return
        val spo2 = spo2Pct ?: return
        val phiHr   = (1f - kotlin.math.abs(hr - 75f) / 75f).coerceIn(0f, 1f)
        val phiSpo2 = ((spo2 - 85f) / 15f).coerceIn(0f, 1f)
        val phiBrain = ((phiHr + phiSpo2) / 2f).coerceIn(PentadState.TRUST_PHI_MIN, 1f)
        _state.update { it.copy(pentad = it.pentad.copy(phiBrain = phiBrain)) }
        pushPentadToBridge()
    }

    private fun runInterpretation(snap: SensorSnapshot, role: UserRole) {
        val currentPentad = _state.value.pentad
        val report = SensorInterpreter.interpret(snap, role, currentPentad)
        _state.update { s ->
            s.copy(
                situationReport = report,
                pentad = report.pentad.copy(
                    phiBrain = s.pentad.phiBrain,  // preserve phiBrain across sensor updates
                    phiTrust = (report.confidence * 0.7f + s.pentad.phiTrust * 0.3f).coerceIn(0f, 1f),
                ),
            )
        }
        pushPentadToBridge()
    }

    /**
     * Push the current PentadState to the SensorBridge so AssistantViewModel
     * can reflect the live coherence in the assistant sheet header without
     * a direct cross-module ViewModel reference.
     */
    private fun pushPentadToBridge() {
        val p = _state.value.pentad
        sensorBridge.pushPentad(PentadSnapshot(
            phiUniv            = p.phiUniv,
            phiBrain           = p.phiBrain,
            phiHuman           = p.phiHuman,
            phiAI              = p.phiAI,
            phiTrust           = p.phiTrust,
            situationCoherence = p.situationCoherence,
        ))
    }

    // ── Tab 2: Protocol ↔ Natural Language ────────────────────────────────────

    fun onProtocolInputChanged(text: String) {
        _state.update { it.copy(protocolInput = text, protocolResult = null) }
    }

    /**
     * Bidirectional translator:
     *  - If input looks like a Gibberlink payload (starts with a known token),
     *    parse → produce rich human narrative.
     *  - If input is natural language, attempt to extract structured data and
     *    build a Gibberlink payload.
     */
    fun translateProtocol() {
        val input = _state.value.protocolInput.trim()
        if (input.isEmpty()) return

        val knownTokens = listOf("GPS:", "SYS:", "ENV:", "VITALS:", "ALERT:", "TRANSLATE:",
            "ALLERGY:", "CONSENT:", "INTENT:", "ENERGY:", "SPATIAL:", "MNFT:", "RAW:")

        if (knownTokens.any { input.startsWith(it) }) {
            // Machine → Human
            val parsed = try { PayloadParser.parse(input) } catch (e: Exception) { null }
            val human  = if (parsed != null) richHumanize(parsed, _state.value.role) else "Could not parse payload."
            _state.update { it.copy(
                protocolResult      = human,
                protocolDirection   = TranslateDirection.MACHINE_TO_HUMAN,
                pentad = _state.value.pentad.copy(phiAI = 0.85f),
            )}
        } else {
            // Human → Machine
            val payload = naturalLanguageToPayload(input)
            _state.update { it.copy(
                protocolResult    = payload ?: "Could not parse. Try: 'HR 112 SpO2 88 temp 38.9' or 'GPS 51.5 -0.12'",
                protocolDirection = TranslateDirection.HUMAN_TO_MACHINE,
                pentad = _state.value.pentad.copy(phiAI = if (payload != null) 0.80f else 0.3f),
            )}
        }
    }

    /**
     * Rich Machine → Human translation — deeper context than the simple
     * one-liner in ModeScreen.humanize().
     */
    private fun richHumanize(parsed: ParsedPayload, role: UserRole): String = when (parsed) {
        is ParsedPayload.Gps -> buildString {
            appendLine("📍 GPS Position")
            appendLine("  Coordinates: %.5f°, %.5f°".format(parsed.lat, parsed.lon))
            appendLine("  Altitude: %.0f m  |  Accuracy: ±%.0f m".format(parsed.altM, parsed.accM))
            if (parsed.batPct >= 0) appendLine("  Device battery: ${parsed.batPct}%")
            val altF = parsed.altM.toFloat()
            when {
                role == UserRole.FIRST_RESPONDER -> {
                    if (altF < -5f) appendLine("  ⚠ BELOW GROUND — possible underground structure")
                    if (parsed.accM > 100f) appendLine("  ⚠ Poor GPS fix — verify position by other means")
                }
                role == UserRole.NURSE && altF > 2500f ->
                    appendLine("  ⚠ HIGH ALTITUDE (${altF.toInt()}m) — adjust SpO₂ thresholds")
            }
        }.trim()

        is ParsedPayload.Vitals -> buildString {
            appendLine("❤️ Patient Vitals")
            appendLine("  Heart Rate: ${parsed.hrBpm} bpm — ${classifyHr(parsed.hrBpm)}")
            appendLine("  SpO₂: ${parsed.spo2Pct}% — ${classifySpo2(parsed.spo2Pct)}")
            appendLine("  Temperature: %.1f°C — ${classifyTemp(parsed.tempC)}".format(parsed.tempC))
            if (role == UserRole.NURSE || role == UserRole.FIRST_RESPONDER) {
                val news2 = news2Score(parsed.hrBpm, parsed.spo2Pct, parsed.tempC)
                appendLine("  NEWS2 estimate: $news2/9 — ${news2Class(news2)}")
                if (news2 >= 5) appendLine("  ⚠ HIGH NEWS2 — escalate to senior clinician IMMEDIATELY")
                appendLine("  Possible concerns: ${vitalsNarrative(parsed.hrBpm, parsed.spo2Pct, parsed.tempC)}")
            }
        }.trim()

        is ParsedPayload.Env -> buildString {
            appendLine("🌡 Environment Reading")
            appendLine("  Pressure: %.1f hPa — ${classifyPressure(parsed.pressureHpa)}".format(parsed.pressureHpa))
            appendLine("  Temperature: %.1f°C".format(parsed.tempC))
            appendLine("  Humidity: %.0f%%".format(parsed.humidityPct))
            if (role == UserRole.NURSE && parsed.pressureHpa < 990f)
                appendLine("  Note: Low pressure — SpO₂ may read ~2% low.")
        }.trim()

        is ParsedPayload.Alert -> buildString {
            appendLine("🚨 ALERT [${parsed.code}]")
            appendLine("  ${parsed.message}")
            if (parsed.code.startsWith("SOS") || parsed.code.startsWith("MAYDAY"))
                appendLine("  ⚠ EMERGENCY — activate RED mode response protocol")
        }.trim()

        is ParsedPayload.Sys -> buildString {
            appendLine("🖥️ System Status — Device: ${parsed.deviceId}")
            appendLine("  CPU temp: %.0f°C ${if (parsed.cpuTempC > 85f) "(THROTTLING)" else ""}".format(parsed.cpuTempC))
            appendLine("  Battery: ${parsed.batPct}%")
            appendLine("  Active anomalies: ${parsed.anomalyCount}")
            appendLine("  Intent: ${parsed.intent}")
            if (parsed.anomalyCount > 0)
                appendLine("  ⚠ ${parsed.anomalyCount} anomaly/anomalies active — review Audit log")
        }.trim()

        is ParsedPayload.Allergy -> buildString {
            appendLine("⚕ Patient Allergy Record")
            appendLine("  Patient ID: ${parsed.patientId}")
            appendLine("  Allergens: ${parsed.allergensCsv}")
            appendLine("  Severity: ${parsed.severity}")
            if (parsed.severity == "SEVERE")
                appendLine("  ⚠ SEVERE ALLERGY — ensure adrenaline auto-injector on hand")
        }.trim()

        is ParsedPayload.Consent -> buildString {
            appendLine("✅ Consent Record")
            appendLine("  Patient: ${parsed.patientId}")
            appendLine("  Action: ${parsed.action}")
            appendLine("  Operator: ${parsed.operatorId}")
        }.trim()

        is ParsedPayload.Translate ->
            "🔤 Translation request: ${parsed.sourceProtocol} → ${parsed.targetLang}\n" +
            "  Text: ${parsed.inputText}"

        is ParsedPayload.Intent ->
            "🔗 Intent: ${parsed.intent.name} from ${parsed.source.name}\n  Payload: ${parsed.payload}"

        is ParsedPayload.Energy ->
            "⚡ Energy state: ${parsed.raw}"

        is ParsedPayload.Spatial ->
            "📡 Spatial/RSSI: ${parsed.raw}"

        is ParsedPayload.Mnft ->
            "🔌 Manifest fragment: ${parsed.raw.take(80)}"

        is ParsedPayload.Raw ->
            "📄 Raw data: ${parsed.raw}"
    }

    /**
     * Natural-language → Gibberlink payload.
     *
     * Recognises patterns like:
     *   "HR 112 SpO2 88 temp 38.9"   → VITALS:112:88:38.9000
     *   "GPS 51.5074 -0.1278"         → GPS:51.5074:-0.1278:0.0000:0.0000:-1
     *   "ALERT fire in building B"     → ALERT:FIRE:fire in building B
     *   "allergy penicillin severe"    → ALLERGY:ANON:penicillin:SEVERE
     *   "environment 1013 22 50"       → ENV:1013.0000:22.0000:50.0000
     */
    private fun naturalLanguageToPayload(text: String): String? {
        val lower = text.lowercase()
        val tokens = text.trim().split(Regex("\\s+"))

        // VITALS
        val hrMatch  = Regex("(?i)\\b(?:hr|heart rate|pulse)[:\\s]+([0-9]+)").find(text)
        val spo2Match = Regex("(?i)\\b(?:spo2|spo₂|sat|saturation)[:\\s]+([0-9]+)").find(text)
        val tempMatch = Regex("(?i)\\b(?:temp|temperature)[:\\s]+([0-9]+\\.?[0-9]*)").find(text)
        if (hrMatch != null || spo2Match != null) {
            val hr   = hrMatch?.groupValues?.get(1)?.toIntOrNull() ?: 0
            val spo2 = spo2Match?.groupValues?.get(1)?.toIntOrNull() ?: 0
            val temp = tempMatch?.groupValues?.get(1)?.toFloatOrNull() ?: 36.5f
            return PayloadBuilder.vitals(hr, spo2, temp)
        }

        // GPS — two floats after GPS keyword
        if (lower.startsWith("gps") && tokens.size >= 3) {
            val lat = tokens.getOrNull(1)?.toDoubleOrNull()
            val lon = tokens.getOrNull(2)?.toDoubleOrNull()
            if (lat != null && lon != null) return PayloadBuilder.gps(lat, lon)
        }

        // ENV — three numbers after env/environment
        if (lower.startsWith("env") && tokens.size >= 4) {
            val p = tokens.getOrNull(1)?.toFloatOrNull()
            val t = tokens.getOrNull(2)?.toFloatOrNull()
            val h = tokens.getOrNull(3)?.toFloatOrNull()
            if (p != null && t != null && h != null) return PayloadBuilder.env(p, t, h)
        }

        // ALERT
        if (lower.startsWith("alert") || lower.startsWith("sos") || lower.startsWith("mayday")) {
            val code = tokens.firstOrNull()?.uppercase() ?: "ALERT"
            val msg  = tokens.drop(1).joinToString(" ")
            return PayloadBuilder.alert(code, msg.ifEmpty { "EMERGENCY" })
        }

        // ALLERGY
        val allergyMatch = Regex("(?i)allerg(?:y|ic)\\s+(.+)").find(text)
        if (allergyMatch != null) {
            val rest = allergyMatch.groupValues[1].trim()
            val parts = rest.split(Regex("\\s+"))
            val allergen = parts.firstOrNull() ?: "UNKNOWN"
            val severity = when {
                rest.contains("severe", ignoreCase = true)   -> "SEVERE"
                rest.contains("moderate", ignoreCase = true) -> "MODERATE"
                rest.contains("mild", ignoreCase = true)     -> "MILD"
                else -> "UNKNOWN"
            }
            return PayloadBuilder.allergy("ANON", allergen, severity)
        }

        return null
    }

    // ── Quick phrases ─────────────────────────────────────────────────────────

    private fun quickPhrasesFor(role: UserRole): List<QuickPhrase> = when (role) {
        UserRole.NURSE -> listOf(
            QuickPhrase("Where does it hurt?",            "medical"),
            QuickPhrase("Are you having trouble breathing?", "medical"),
            QuickPhrase("Do you have any allergies?",     "medical"),
            QuickPhrase("Help is coming.",                "reassurance"),
            QuickPhrase("Can you tell me your name?",     "assessment"),
            QuickPhrase("Have you taken any medication?", "medical"),
            QuickPhrase("I need to take your blood pressure.", "medical"),
            QuickPhrase("Please stay calm.",              "reassurance"),
            QuickPhrase("Are you diabetic?",              "medical"),
            QuickPhrase("When did the pain start?",       "assessment"),
        )
        UserRole.FIRST_RESPONDER -> listOf(
            QuickPhrase("Are you injured?",               "triage"),
            QuickPhrase("Can you walk?",                  "triage"),
            QuickPhrase("How many people are with you?",  "triage"),
            QuickPhrase("Do not move — help is coming.",  "safety"),
            QuickPhrase("Is anyone trapped?",             "rescue"),
            QuickPhrase("Do you smell gas?",              "hazmat"),
            QuickPhrase("Move away from the building.",   "evacuation"),
            QuickPhrase("Follow me to safety.",           "evacuation"),
            QuickPhrase("Do not touch any wires.",        "electrical"),
            QuickPhrase("Stay low — there may be smoke.", "fire"),
        )
        UserRole.ENGINEER -> listOf(
            QuickPhrase("Is the equipment switched off?",  "safety"),
            QuickPhrase("What is the last known fault?",   "diagnosis"),
            QuickPhrase("Do not operate this machine.",    "lockout"),
            QuickPhrase("Where is the emergency stop?",    "safety"),
            QuickPhrase("Has this been locked out?",       "lockout"),
            QuickPhrase("What pressure is the system at?", "diagnostic"),
            QuickPhrase("When was the last inspection?",   "maintenance"),
            QuickPhrase("Who is the site safety officer?", "authority"),
        )
        else -> listOf(
            QuickPhrase("I need help.",                   "general"),
            QuickPhrase("Call emergency services.",       "general"),
            QuickPhrase("Where are you?",                 "general"),
            QuickPhrase("Are you okay?",                  "general"),
            QuickPhrase("Follow me.",                     "general"),
            QuickPhrase("Do not panic.",                  "general"),
        )
    }

    // ── Clinical helpers ──────────────────────────────────────────────────────

    private fun classifyHr(hr: Int) = when {
        hr < 40  -> "SEVERE BRADYCARDIA ⚠"
        hr < 60  -> "Bradycardia"
        hr <= 100 -> "Normal"
        hr <= 110 -> "Mild tachycardia"
        hr <= 130 -> "Tachycardia ⚠"
        else -> "SEVERE TACHYCARDIA ⚠"
    }

    private fun classifySpo2(spo2: Int) = when {
        spo2 < 85  -> "CRITICAL hypoxia ⚠ — O₂ NOW"
        spo2 < 90  -> "SEVERE hypoxia ⚠"
        spo2 < 94  -> "Mild hypoxia — supplemental O₂ indicated"
        spo2 < 96  -> "Low-normal — monitor closely"
        spo2 <= 100 -> "Normal"
        else -> "Invalid reading"
    }

    private fun classifyTemp(t: Float) = when {
        t < 35f  -> "HYPOTHERMIA ⚠"
        t < 36f  -> "Low"
        t <= 37.5f -> "Normal"
        t <= 38f   -> "Low-grade fever"
        t <= 39f   -> "Fever"
        t <= 40f   -> "High fever ⚠"
        else -> "HYPERPYREXIA ⚠ — cool immediately"
    }

    private fun classifyPressure(p: Float) = when {
        p < 960f  -> "VERY LOW — storm/underground risk"
        p < 990f  -> "Low — deteriorating weather"
        p < 1013f -> "Below normal"
        p <= 1020f -> "Normal"
        else -> "High — stable conditions"
    }

    private fun news2Score(hr: Int, spo2: Int, tempC: Float): Int {
        val hrS = when {
            hr <= 40         -> 3
            hr <= 50         -> 1
            hr in 51..90     -> 0
            hr in 91..110    -> 1
            hr in 111..130   -> 2
            else             -> 3
        }
        val spS = when {
            spo2 < 92        -> 3
            spo2 <= 93       -> 2
            spo2 <= 95       -> 1
            else             -> 0
        }
        val tS = when {
            tempC < 35f      -> 3
            tempC < 36f      -> 1
            tempC <= 38f     -> 0
            tempC <= 39f     -> 1
            else             -> 2
        }
        return hrS + spS + tS
    }

    private fun news2Class(n: Int) = when {
        n >= 7 -> "HIGH RISK — immediate medical emergency response"
        n >= 5 -> "MEDIUM-HIGH — urgent escalation"
        n >= 3 -> "MEDIUM — close monitoring required"
        else   -> "LOW — routine monitoring"
    }

    private fun vitalsNarrative(hr: Int, spo2: Int, tempC: Float): String {
        val concerns = mutableListOf<String>()
        if (hr > 100 && spo2 < 94) concerns += "Hypoxic tachycardia — ensure O₂, check airway"
        if (hr > 100 && tempC > 38f) concerns += "Febrile tachycardia — consider infection/sepsis"
        if (hr > 100) concerns += "Tachycardia: pain, dehydration, haemorrhage, anxiety"
        if (spo2 < 94) concerns += "Hypoxia: airway obstruction, pneumonia, COPD exacerbation"
        if (tempC > 38.5f) concerns += "Pyrexia: infection, inflammation"
        if (tempC < 36f) concerns += "Hypothermia: exposure, shock"
        return if (concerns.isEmpty()) "No immediate concerns." else concerns.joinToString("; ")
    }

    override fun onCleared() {
        tts?.stop()
        tts?.shutdown()
        currentTranslator?.close()
        langIdClient.close()
        ocrCameraProvider?.unbindAll()
        hazardCameraProvider?.unbindAll()
        textRecognizer.close()
        objectDetector.close()
        super.onCleared()
    }

    private companion object {
        /** φ confidence assigned when ML Kit successfully identifies the source language. */
        const val PHI_AI_LANG_IDENTIFIED   = 0.9f
        /** φ confidence when source language could not be identified ("und"). */
        const val PHI_AI_LANG_UNIDENTIFIED = 0.6f
        /** φ_human when the user has an active (non-DEFAULT) role selected. */
        const val PHI_HUMAN_ROLE_ACTIVE    = 0.9f
        /** φ_human for DEFAULT (no specific role). */
        const val PHI_HUMAN_ROLE_DEFAULT   = 0.5f

        val SUPPORTED_LANGUAGES: List<Pair<String, String>> = listOf(
            "af" to "Afrikaans",      "ar" to "Arabic",         "be" to "Belarusian",
            "bg" to "Bulgarian",      "bn" to "Bengali",        "ca" to "Catalan",
            "cs" to "Czech",          "cy" to "Welsh",          "da" to "Danish",
            "de" to "German",         "el" to "Greek",          "en" to "English",
            "eo" to "Esperanto",      "es" to "Spanish",        "et" to "Estonian",
            "fa" to "Persian",        "fi" to "Finnish",        "fr" to "French",
            "ga" to "Irish",          "gl" to "Galician",       "gu" to "Gujarati",
            "he" to "Hebrew",         "hi" to "Hindi",          "hr" to "Croatian",
            "ht" to "Haitian Creole", "hu" to "Hungarian",      "id" to "Indonesian",
            "is" to "Icelandic",      "it" to "Italian",        "ja" to "Japanese",
            "ka" to "Georgian",       "kn" to "Kannada",        "ko" to "Korean",
            "lt" to "Lithuanian",     "lv" to "Latvian",        "mk" to "Macedonian",
            "mr" to "Marathi",        "ms" to "Malay",          "mt" to "Maltese",
            "nl" to "Dutch",          "no" to "Norwegian",      "pl" to "Polish",
            "pt" to "Portuguese",     "ro" to "Romanian",       "ru" to "Russian",
            "sk" to "Slovak",         "sl" to "Slovenian",      "sq" to "Albanian",
            "sr" to "Serbian",        "sv" to "Swedish",        "sw" to "Swahili",
            "ta" to "Tamil",          "te" to "Telugu",         "th" to "Thai",
            "tl" to "Filipino",       "tr" to "Turkish",        "uk" to "Ukrainian",
            "ur" to "Urdu",           "vi" to "Vietnamese",     "zh" to "Chinese",
        )
    }

    fun getSupportedLanguages() = SUPPORTED_LANGUAGES

    // ── ML Kit OCR — Camera Text Recognition ─────────────────────────────────

    private val textRecognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
    private var ocrCameraProvider: ProcessCameraProvider? = null

    /**
     * Capture a single frame from the rear camera and run ML Kit Text Recognition.
     * Detected text is injected into the translation input field and auto-translated.
     * Requires CAMERA permission.
     */
    fun captureForOcr(lifecycleOwner: LifecycleOwner) {
        _state.update { it.copy(ocrRunning = true, ocrText = null, ocrError = null) }
        val executor = ContextCompat.getMainExecutor(context)
        val future   = ProcessCameraProvider.getInstance(context)

        future.addListener({
            val provider = future.get() ?: run {
                _state.update { it.copy(ocrRunning = false, ocrError = "Camera unavailable") }
                return@addListener
            }
            ocrCameraProvider = provider

            val imageCapture = ImageCapture.Builder()
                .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                .build()

            try {
                provider.unbindAll()
                provider.bindToLifecycle(lifecycleOwner, CameraSelector.DEFAULT_BACK_CAMERA, imageCapture)
            } catch (e: Exception) {
                _state.update { it.copy(ocrRunning = false, ocrError = "Camera bind failed: ${e.message}") }
                return@addListener
            }

            val outputFile = File(context.cacheDir, "ocr_capture.jpg")
            val outputOptions = ImageCapture.OutputFileOptions.Builder(outputFile).build()

            imageCapture.takePicture(outputOptions, executor,
                object : ImageCapture.OnImageSavedCallback {
                    override fun onImageSaved(outputFileResults: ImageCapture.OutputFileResults) {
                        provider.unbindAll()
                        processOcrBitmap(BitmapFactory.decodeFile(outputFile.absolutePath))
                    }
                    override fun onError(exception: ImageCaptureException) {
                        provider.unbindAll()
                        _state.update { it.copy(ocrRunning = false, ocrError = "Capture failed: ${exception.message}") }
                    }
                })
        }, executor)
    }

    /**
     * Process a [Bitmap] with ML Kit Text Recognition.
     * On success, the detected text is injected into the human translation input
     * and auto-translation is triggered.
     */
    fun processOcrBitmap(bitmap: Bitmap) {
        viewModelScope.launch {
            try {
                val image  = InputImage.fromBitmap(bitmap, 0)
                val result = textRecognizer.process(image).await()
                val text   = result.text.trim()
                if (text.isEmpty()) {
                    _state.update { it.copy(ocrRunning = false, ocrText = "", ocrError = "No text detected") }
                } else {
                    _state.update { it.copy(
                        ocrRunning       = false,
                        ocrText          = text,
                        humanSourceText  = text,   // inject into translation input
                        humanTranslated  = null,
                    )}
                    // auto-translate the scanned text
                    translateHumanText()
                }
            } catch (e: Exception) {
                _state.update { it.copy(ocrRunning = false, ocrError = "OCR error: ${e.message}") }
            }
        }
    }

    // ── ML Kit Object Detection — Hazard Scan ─────────────────────────────────

    private val objectDetector = ObjectDetection.getClient(
        ObjectDetectorOptions.Builder()
            .setDetectorMode(ObjectDetectorOptions.SINGLE_IMAGE_MODE)
            .enableMultipleObjects()
            .enableClassification()
            .build()
    )
    private var hazardCameraProvider: ProcessCameraProvider? = null

    /**
     * Capture a single frame and run ML Kit Object Detection.
     * Detected object labels are surfaced as a hazard summary in Field Intel tab.
     * Requires CAMERA permission.
     */
    fun captureForHazardScan(lifecycleOwner: LifecycleOwner) {
        _state.update { it.copy(hazardRunning = true, hazardLabels = emptyList(), hazardError = null) }
        val executor = ContextCompat.getMainExecutor(context)
        val future   = ProcessCameraProvider.getInstance(context)

        future.addListener({
            val provider = future.get() ?: run {
                _state.update { it.copy(hazardRunning = false, hazardError = "Camera unavailable") }
                return@addListener
            }
            hazardCameraProvider = provider

            val imageCapture = ImageCapture.Builder()
                .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                .build()

            try {
                provider.unbindAll()
                provider.bindToLifecycle(lifecycleOwner, CameraSelector.DEFAULT_BACK_CAMERA, imageCapture)
            } catch (e: Exception) {
                _state.update { it.copy(hazardRunning = false, hazardError = "Camera bind failed: ${e.message}") }
                return@addListener
            }

            val outputFile = File(context.cacheDir, "hazard_capture.jpg")
            val outputOptions = ImageCapture.OutputFileOptions.Builder(outputFile).build()

            imageCapture.takePicture(outputOptions, executor,
                object : ImageCapture.OnImageSavedCallback {
                    override fun onImageSaved(outputFileResults: ImageCapture.OutputFileResults) {
                        provider.unbindAll()
                        processHazardBitmap(BitmapFactory.decodeFile(outputFile.absolutePath))
                    }
                    override fun onError(exception: ImageCaptureException) {
                        provider.unbindAll()
                        _state.update { it.copy(hazardRunning = false, hazardError = "Capture failed: ${exception.message}") }
                    }
                })
        }, executor)
    }

    /**
     * Run ML Kit Object Detection on [bitmap].
     * Detected objects and their classification labels are formatted as
     * situation alerts and stored in [TranslateUiState.hazardLabels].
     */
    fun processHazardBitmap(bitmap: Bitmap) {
        viewModelScope.launch {
            try {
                val image   = InputImage.fromBitmap(bitmap, 0)
                val objects = objectDetector.process(image).await()
                val labels  = objects.flatMap { obj ->
                    obj.labels.map { label ->
                        "${label.text} (${(label.confidence * 100).toInt()}%)"
                    }
                }.distinct().take(10)

                _state.update { it.copy(
                    hazardRunning = false,
                    hazardLabels  = labels.ifEmpty { listOf("No objects detected") },
                )}
            } catch (e: Exception) {
                _state.update { it.copy(hazardRunning = false, hazardError = "Detection error: ${e.message}") }
            }
        }
    }

    // ── Adaptive card/hint helpers ─────────────────────────────────────────────

    /** Remove an assistant-injected card from the shared adaptive state. */
    fun removeAdaptiveCard(id: String) {
        adaptive.removeDashboardCard(id)
    }

    /** Clear an assistant-injected hint for the Translate screen. */
    fun clearTranslateHint() {
        adaptive.clearHint("translate")
    }
}

// ─────────────────────────────────────────────────────────────────────────────

data class TranslateUiState(
    val role:               UserRole            = UserRole.DEFAULT,

    // Tab 0 — Human↔Human
    val humanSourceText:    String              = "",
    val humanTranslated:    String?             = null,
    val detectedSourceLang: String              = "",
    val targetLanguage:     String              = TranslateLanguage.ENGLISH,
    val isTranslating:      Boolean             = false,
    val ttsReady:           Boolean             = false,
    val translateError:     String?             = null,
    val quickPhrases:       List<QuickPhrase>   = emptyList(),

    // Tab 0 — OCR Camera Scan
    val ocrRunning:         Boolean             = false,
    val ocrText:            String?             = null,    // raw scanned text
    val ocrError:           String?             = null,

    // Tab 1 — Sensor → Situation
    val sensorSnapshot:     SensorSnapshot?     = null,
    val situationReport:    SituationReport?    = null,

    // Tab 1 — Object Detection / Hazard Scan
    val hazardRunning:      Boolean             = false,
    val hazardLabels:       List<String>        = emptyList(),
    val hazardError:        String?             = null,

    // Tab 2 — Protocol ↔ NL
    val protocolInput:      String              = "",
    val protocolResult:     String?             = null,
    val protocolDirection:  TranslateDirection  = TranslateDirection.MACHINE_TO_HUMAN,

    // Pentad
    val pentad:             PentadState         = PentadState(),
)

data class QuickPhrase(
    val english:    String,
    val category:   String,
    val translated: String? = null,
)

enum class TranslateDirection { MACHINE_TO_HUMAN, HUMAN_TO_MACHINE }
