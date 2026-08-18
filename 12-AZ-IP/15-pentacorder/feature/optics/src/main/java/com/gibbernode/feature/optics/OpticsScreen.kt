package com.gibbernode.feature.optics

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
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
import com.gibbernode.ui.GibberBlue
import com.gibbernode.ui.GibberGreen
import com.gibbernode.ui.GibberRed
import com.gibbernode.ui.OnSurfaceDim
import com.gibbernode.ui.SurfaceDark

/**
 * OpticsScreen — 🔬 Optical Physics Suite
 *
 * Seven sub-tabs exposing the S24 Ultra "just past the limit" camera capabilities:
 *   0 — 👁️ NLOS           Non-Line-of-Sight scatter reconstruction
 *   1 — 🌈 Hyperspectral  NIR / dark-frame / red-edge chlorophyll index
 *   2 — 💓 Motion Mag     Eulerian pulse + breathing detection
 *   3 — 🎙️ Visual Mic    Micro-vibration → acoustic reconstruction
 *   4 — 📸 Synth Aperture Gyro-aligned burst → virtual aperture + bokeh
 *   5 — 🌑 Night Mode     16-in-1 binning + AI multi-frame fusion
 *   6 — 🔦 Active NIR     850/940nm illumination + CLAHE + thermal safety
 */
@Composable
fun OpticsScreen(viewModel: OpticsViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    var tab   by remember { mutableIntStateOf(0) }

    Column(modifier = Modifier.fillMaxSize()) {
        ScrollableTabRow(selectedTabIndex = tab, edgePadding = 0.dp) {
            Tab(selected = tab == 0, onClick = { tab = 0 }, text = { Text("👁️ NLOS",        fontSize = 12.sp) })
            Tab(selected = tab == 1, onClick = { tab = 1 }, text = { Text("🌈 Hyper",       fontSize = 12.sp) })
            Tab(selected = tab == 2, onClick = { tab = 2 }, text = { Text("💓 Motion",      fontSize = 12.sp) })
            Tab(selected = tab == 3, onClick = { tab = 3 }, text = { Text("🎙️ Vis.Mic",    fontSize = 12.sp) })
            Tab(selected = tab == 4, onClick = { tab = 4 }, text = { Text("📸 Syn.Apt",     fontSize = 12.sp) })
            Tab(selected = tab == 5, onClick = { tab = 5 }, text = { Text("🌑 Night",       fontSize = 12.sp) })
            Tab(selected = tab == 6, onClick = { tab = 6 }, text = { Text("🔦 NIR",         fontSize = 12.sp) })
            Tab(selected = tab == 7, onClick = { tab = 7 }, text = { Text("🌑 Ultra Dark",  fontSize = 12.sp) })
        }
        when (tab) {
            0 -> NlosTab(state, viewModel)
            1 -> HyperspectralTab(state, viewModel)
            2 -> MotionMagTab(state, viewModel)
            3 -> VisualMicTab(state, viewModel)
            4 -> SynthApertureTab(state, viewModel)
            5 -> NightModeTab(state, viewModel)
            6 -> ActiveNirTab(state, viewModel)
            7 -> UltraDarkTab(state, viewModel)
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 0 — NLOS
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun NlosTab(state: OpticsUiState, vm: OpticsViewModel) {
    TabScaffold(
        title     = "👁️ Non-Line-of-Sight Imaging",
        theory    = "Detects scatter of light bouncing off a relay wall to reconstruct " +
                    "the silhouette of objects hidden around corners. Uses the LaserAF " +
                    "ToF sensor in sync with the 200MP sensor.",
        disclaimer = "Experimental research only. Do not observe persons without consent.",
        running   = state.nlosRunning,
        onRun     = vm::runNlos,
        runLabel  = "▶ Run NLOS Reconstruction",
    ) {
        state.nlosResult?.let { r ->
            MetricCard {
                MetricRow("Echoes detected",   "${r.echos.size}",                         "")
                MetricRow("Silhouette area",   "%.1f%%".format(r.silhouetteArea * 100f),  "of hidden volume")
                MetricRow("Confidence",        "%.0f%%".format(r.confidence * 100f),      "")
                r.echos.take(3).forEachIndexed { i, e ->
                    MetricRow("Echo ${i + 1}",
                        "(%.2f, %.2f)".format(e.echoX, e.echoY),
                        "energy=%.2f  depth=%.1fm".format(e.energy, e.depthMeters))
                }
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 1 — Hyperspectral
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun HyperspectralTab(state: OpticsUiState, vm: OpticsViewModel) {
    TabScaffold(
        title     = "🌈 Hyperspectral / NIR Scan",
        theory    = "Dark-frame subtraction reveals residual NIR signal leaking through " +
                    "the IR-cut filter. Chlorophyll red-edge index (REI) detects plant " +
                    "stress. NIR/green ratio identifies sub-surface bruising.",
        disclaimer = "Indicative only — not calibrated spectroscopy. Not for food safety or clinical use.",
        running   = state.hyperRunning,
        onRun     = vm::runHyperspectral,
        runLabel  = "▶ Run Dark-Frame Analysis",
    ) {
        state.hyperResult?.let { r ->
            MetricCard {
                val stressColor = when (r.plantStressLabel) {
                    com.gibbernode.optics.HyperspectralAdvisor.PlantStressLevel.HEALTHY    -> GibberGreen
                    com.gibbernode.optics.HyperspectralAdvisor.PlantStressLevel.MILD_STRESS -> GibberAmber
                    com.gibbernode.optics.HyperspectralAdvisor.PlantStressLevel.NOT_PLANT  -> OnSurfaceDim
                    else -> GibberRed
                }
                Text(
                    "${r.plantStressLabel.emoji} ${r.plantStressLabel.label}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold, color = stressColor,
                )
                Spacer(Modifier.height(8.dp))
                MetricRow("Red-Edge Index",  "%.3f".format(r.meanRedEdgeIndex), "REI  (healthy > 0.30)")
                MetricRow("NIR proxy mean",  "%.3f".format(r.nirMean),          "")
                MetricRow("Bruised pixels",  "%.1f%%".format(r.bruisedFraction * 100f), "")
                MetricRow("Pixels analysed", "${r.annotations.size}", "")
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 2 — Motion Magnification
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun MotionMagTab(state: OpticsUiState, vm: OpticsViewModel) {
    TabScaffold(
        title     = "💓 Sub-Visual Motion Magnification",
        theory    = "Eulerian video magnification amplifies periodic colour oscillations " +
                    "in the green channel of a forehead ROI. Extracts cardiac (0.7–3 Hz) " +
                    "and respiratory (0.1–0.6 Hz) signals without contact.",
        disclaimer = "Screening reference only. Not a medical device. Not for clinical HR measurement.",
        running   = state.motionRunning,
        onRun     = vm::runMotionMag,
        runLabel  = "▶ Run Motion Magnification",
    ) {
        state.motionCardiac?.let { c ->
            MetricCard {
                Text("Cardiac Channel", style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold, color = GibberRed)
                Spacer(Modifier.height(4.dp))
                MetricRow("Dominant freq",  "%.2f Hz".format(c.dominantFreqHz), "")
                MetricRow("BPM estimate",   "%.0f bpm".format(c.bpmEstimate),   "")
                MetricRow("Signal power",   "%.4f".format(c.signalPower),       "RMS")
                MetricRow("SNR",            "%.1f dB".format(c.snrDb),          "")
            }
        }
        Spacer(Modifier.height(8.dp))
        state.motionBreathing?.let { b ->
            MetricCard {
                Text("Respiratory Channel", style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold, color = GibberBlue)
                Spacer(Modifier.height(4.dp))
                MetricRow("Dominant freq",  "%.2f Hz".format(b.dominantFreqHz), "")
                MetricRow("Breaths/min",    "%.0f".format(b.bpmEstimate),        "")
                MetricRow("Signal power",   "%.4f".format(b.signalPower),        "RMS")
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 3 — Visual Microphone
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun VisualMicTab(state: OpticsUiState, vm: OpticsViewModel) {
    TabScaffold(
        title     = "🎙️ Visual Microphone",
        theory    = "High-speed video (120–960 fps) tracks micro-vibrations of lightweight " +
                    "objects. Sub-pixel optical flow recovers the acoustic pressure waveform. " +
                    "At 960 fps the Nyquist frequency is 480 Hz — intelligible speech fundamentals.",
        disclaimer = "Experimental. Covert audio interception may be illegal. Do not use without consent.",
        running   = state.visualMicRunning,
        onRun     = vm::runVisualMic,
        runLabel  = "▶ Run Visual Microphone",
    ) {
        state.visualMicResult?.let { r ->
            MetricCard {
                val speechColor = if (r.speechLikely) GibberAmber else OnSurfaceDim
                Text(
                    if (r.speechLikely) "🎙️ Speech-frequency content detected"
                    else                "🔇 No speech-band signal",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Bold, color = speechColor,
                )
                Spacer(Modifier.height(8.dp))
                MetricRow("Dominant freq",  "%.1f Hz".format(r.dominantFreqHz),  "")
                MetricRow("RMS amplitude",  "%.5f px".format(r.rmsAmplitude),    "sub-pixel displacement")
                MetricRow("SNR",            "%.1f dB".format(r.snrDb),           "")
                MetricRow("Spectrum bins",  "${r.spectrum.size}",                 "")
                MetricRow("PCM frames",     "${r.reconstructedPcm.size}",         "reconstructed")
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 4 — Synthetic Aperture
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun SynthApertureTab(state: OpticsUiState, vm: OpticsViewModel) {
    TabScaffold(
        title     = "📸 Synthetic Aperture Photogrammetry",
        theory    = "Move the phone deliberately during a burst of 200MP shots. The gyroscope " +
                    "records the sub-pixel translation between frames. Coherent stacking creates " +
                    "a virtual lens the size of the total camera displacement.",
        disclaimer = "SNR and bokeh values are theoretical estimates. Requires careful deliberate panning.",
        running   = state.synthRunning,
        onRun     = vm::runSynthAperture,
        runLabel  = "▶ Compute Virtual Aperture",
    ) {
        state.synthResult?.let { r ->
            MetricCard {
                MetricRow("Physical aperture", "%.2f mm".format(r.physicalApertureMm),  "f/1.7 main lens")
                MetricRow("Virtual aperture",  "%.2f mm".format(r.virtualApertureMm),   "after pan")
                MetricRow("Aperture ratio",    "%.1f×".format(r.apertureRatio),          "virtual / physical")
                MetricRow("SNR improvement",   "+%.1f dB".format(r.snrImprovementDb),    "√N frame stack")
                MetricRow("Bokeh blur radius", "%.1f px".format(r.bokehBlurRadiusPx),    "background")
                MetricRow("Max displacement",  "%.1f px".format(r.maxDisplacementPx),    "sub-pixel total")
                MetricRow("Coherence",         "%.0f%%".format(r.coherenceQuality * 100f), "")
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 5 — Night Mode
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun NightModeTab(state: OpticsUiState, vm: OpticsViewModel) {
    TabScaffold(
        title     = "🌑 Full-Colour Night Mode Engine  (0.1 – 5 lux)",
        theory    = "16-in-1 pixel binning lifts SNR 12 dB. Up to 30-frame AI burst fusion adds " +
                    "another √N gain. OIS + gyroscope compensates hand tremor for up to 4-second " +
                    "handheld exposures. AI ISP reconstructs ambiguous colour from dark Bayer data. " +
                    "Best for dimly-lit rooms and evening scenes (0.1–5 lux). " +
                    "For total/near-total darkness (< 0.1 lux) use the 🌑 Ultra Dark tab instead.",
        disclaimer = "Theoretical SNR values based on published sensor specs. Actual results depend on ISP firmware.",
        running   = state.nightRunning,
        onRun     = vm::runNightMode,
        runLabel  = "▶ Analyse Night Mode Stack",
    ) {
        state.nightResult?.let { r ->
            MetricCard {
                Text("SNR Analysis", style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(4.dp))
                MetricRow("Single-pixel SNR",  "%.1f dB".format(r.singlePixelSnrDb),   "native 0.6 µm pixel")
                MetricRow("After 16-in-1 bin", "%.1f dB".format(r.binnedSnrDb),        "+%.1f dB".format(r.binnedSnrDb - r.singlePixelSnrDb))
                MetricRow("After ${r.frameCount}-frame fusion", "%.1f dB".format(r.fusedSnrDb),
                    "+%.1f dB total".format(r.snrGainOverSingleDb))
                Spacer(Modifier.height(8.dp))
                Text("Exposure", style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(4.dp))
                MetricRow("Recommended ISO",    "${r.recommendedIso}",                       "")
                MetricRow("Recommended exp.",   "%.0f ms".format(r.recommendedExposureMs),   "")
                MetricRow("Max handheld exp.",  "%.0f ms".format(r.maxHandheldExposureMs),   "OIS-limited")
                Spacer(Modifier.height(8.dp))
                Text("Colour Reconstruction", style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(4.dp))
                MetricRow("Fused R/G/B",
                    "%.3f / %.3f / %.3f".format(r.fusedR, r.fusedG, r.fusedB), "")
                MetricRow("Colour temp",
                    "%.0f K".format(r.colourTempK),
                    "WB conf %.0f%%".format(r.whiteBalanceConf * 100f))
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 6 — Active NIR
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun ActiveNirTab(state: OpticsUiState, vm: OpticsViewModel) {
    TabScaffold(
        title     = "🔦 Active NIR / True Night Vision",
        theory    = "An external 850/940 nm IR illuminator floods a pitch-black scene. The " +
                    "200MP sensor's IR-cut filter passes 5–15% at 850 nm — enough with a " +
                    "high-power illuminator. RAW_SENSOR capture + CLAHE reveals every photon. " +
                    "Temporal denoising stacks 5–10 ISO-12800 frames to cut digital snow. " +
                    "LaserAF depth map gives a coarse 240×180 radar silhouette in 100% darkness.",
        disclaimer = "Do not observe persons without consent. High-ISO operation above 45°C risks permanent hot pixels.",
        running   = state.nirRunning,
        onRun     = { vm.runActiveNir(850) },
        runLabel  = "▶ Run Active NIR (850 nm)",
    ) {
        state.nirIrResult?.let { ir ->
            MetricCard {
                Text("IR-Cut Filter @ ${ir.wavelengthNm} nm",
                    style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(4.dp))
                MetricRow("Transmittance",  "%.1f%%".format(ir.transmittance * 100f), "")
                MetricRow("Usable signal",  if (ir.usableSignal) "✅ Yes" else "❌ No", "")
                Spacer(Modifier.height(4.dp))
                Text(ir.recommendation, style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
            }
        }
        Spacer(Modifier.height(8.dp))
        state.nirCamera2?.let { c ->
            MetricCard {
                Text("Camera2 Parameters", style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(4.dp))
                MetricRow("ISO",           "${c.iso}",           "")
                MetricRow("Exposure",      "%.0f ms".format(c.exposureMs), "")
                MetricRow("AWB mode",      c.awbMode,            "")
                MetricRow("Output format", c.outputFormat,       "")
                MetricRow("Noise red.",    c.noiseReduction,     "")
            }
        }
        Spacer(Modifier.height(8.dp))
        if (state.nirClaheGain > 0f) {
            MetricCard {
                Text("CLAHE Processing", style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(4.dp))
                MetricRow("Contrast gain", "%.1f×".format(state.nirClaheGain),
                    "dark-frame brightness lift")
            }
        }
        Spacer(Modifier.height(8.dp))
        state.nirThermal?.let { t ->
            val riskColor = when (t.riskLevel) {
                com.gibbernode.optics.ActiveNIRAdvisor.ThermalRisk.SAFE     -> GibberGreen
                com.gibbernode.optics.ActiveNIRAdvisor.ThermalRisk.WARM     -> GibberAmber
                com.gibbernode.optics.ActiveNIRAdvisor.ThermalRisk.HOT      -> GibberAmber
                com.gibbernode.optics.ActiveNIRAdvisor.ThermalRisk.CRITICAL -> GibberRed
            }
            MetricCard {
                Text("Thermal Safety", style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(4.dp))
                Text(
                    "${t.riskLevel.emoji} ${t.riskLevel.label}  (${t.cameraModuleTempC}°C)",
                    style = MaterialTheme.typography.bodyMedium, color = riskColor,
                    fontWeight = FontWeight.Bold,
                )
                Spacer(Modifier.height(4.dp))
                MetricRow("Duty cycle",  "%.0f%%".format(t.maxDutyCycle * 100f), "")
                Spacer(Modifier.height(4.dp))
                Text(t.recommendedAction, style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
                Spacer(Modifier.height(2.dp))
                Text(t.hotPixelRiskNote, style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Shared composables
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun TabScaffold(
    title:      String,
    theory:     String,
    disclaimer: String,
    running:    Boolean,
    onRun:      () -> Unit,
    runLabel:   String,
    content:    @Composable ColumnScope.() -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        // Theory card
        Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark),
            modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(14.dp)) {
                Text(title, style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(6.dp))
                Text(theory, style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
            }
        }

        // Run button
        Button(
            onClick  = onRun,
            enabled  = !running,
            modifier = Modifier.fillMaxWidth(),
        ) {
            if (running) {
                CircularProgressIndicator(
                    modifier = Modifier.size(16.dp),
                    strokeWidth = 2.dp,
                    color = MaterialTheme.colorScheme.onPrimary,
                )
                Spacer(Modifier.width(8.dp))
                Text("Running…")
            } else {
                Text(runLabel)
            }
        }

        // Results
        content()

        // Disclaimer
        Text(
            "⚠️ $disclaimer",
            style = MaterialTheme.typography.labelSmall,
            color = OnSurfaceDim,
        )
    }
}

@Composable
private fun MetricCard(content: @Composable ColumnScope.() -> Unit) {
    Card(colors = CardDefaults.cardColors(containerColor = SurfaceDark),
        modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(14.dp)) {
            content()
        }
    }
}

@Composable
private fun MetricRow(label: String, value: String, note: String) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 2.dp),
        horizontalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        Text(label, style = MaterialTheme.typography.bodySmall,
            color = OnSurfaceDim, modifier = Modifier.weight(1.4f))
        Text(value, style = MaterialTheme.typography.bodySmall,
            fontFamily = FontFamily.Monospace, modifier = Modifier.weight(1.5f))
        if (note.isNotEmpty())
            Text(note, style = MaterialTheme.typography.labelSmall,
                color = OnSurfaceDim, modifier = Modifier.weight(1.2f))
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 7 — Ultra Dark / Zero-Lux
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun UltraDarkTab(state: OpticsUiState, vm: OpticsViewModel) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        // Theory card
        MetricCard {
            Text("🌑 Ultra Dark / Zero-Lux Imaging",
                style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(6.dp))
            Text(
                "This mode targets scenes with less than 0.01 lux — total or near-total darkness. " +
                "It combines maximum ISO (12800), maximum shutter (4 s OIS-limited), 16-in-1 pixel " +
                "binning, 30-frame AI fusion, and CLAHE post-processing to recover any usable signal. " +
                "The S24 Ultra main sensor's f/1.7 aperture and 1/1.3\" sensor size give it a genuine " +
                "advantage over virtually every other phone in zero-lux conditions.",
                style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim,
            )
        }

        // Protocol steps
        MetricCard {
            Text("🔦 Zero-Lux Protocol", style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold, color = GibberBlue)
            Spacer(Modifier.height(6.dp))
            listOf(
                "1" to "Use Samsung Camera → Night Mode (not Auto).",
                "2" to "Phone on solid surface or tripod — no hand movement.",
                "3" to "Enable RAW copies (Settings → Pictures → RAW copies → RAW + JPEG).",
                "4" to "For full control: switch to Pro Mode → ISO 12800 → Shutter 30 s.",
                "5" to "Flash OFF. Any flash will overexpose the binned sensor.",
                "6" to "Tap to set focus before complete darkness, or use ∞ manual focus.",
                "7" to "Copy RAW DNG to Termux and run the CLAHE pipeline (see Cameras tab).",
                "8" to "For true zero-photon scenes: add 850 nm external illuminator → use 🔦 NIR tab.",
            ).forEach { (n, step) ->
                Row(modifier = Modifier.fillMaxWidth().padding(vertical = 2.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(n, style = MaterialTheme.typography.labelSmall,
                        color = GibberBlue, modifier = Modifier.width(16.dp))
                    Text(step, style = MaterialTheme.typography.bodySmall)
                }
            }
        }

        // Analyse button
        Button(
            onClick  = vm::runUltraDark,
            enabled  = !state.ultraDarkRunning,
            modifier = Modifier.fillMaxWidth(),
        ) {
            if (state.ultraDarkRunning) {
                CircularProgressIndicator(
                    modifier = Modifier.size(16.dp), strokeWidth = 2.dp,
                    color = MaterialTheme.colorScheme.onPrimary,
                )
                Spacer(Modifier.width(8.dp))
                Text("Analysing zero-lux stack…")
            } else {
                Text("▶ Analyse Zero-Lux Stack (Demo)")
            }
        }

        // Results
        state.ultraDarkResult?.let { r ->
            MetricCard {
                Text("SNR Analysis — Zero-Lux Scene (< 0.01 lux)",
                    style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold,
                    color = GibberBlue)
                Spacer(Modifier.height(4.dp))
                MetricRow("Native pixel SNR",     "%.1f dB".format(r.singlePixelSnrDb),  "ISO 12800 noise floor")
                MetricRow("After 16-in-1 bin",    "%.1f dB".format(r.binnedSnrDb),       "+%.1f dB".format(r.binnedSnrDb - r.singlePixelSnrDb))
                MetricRow("After ${r.frameCount}-frame fusion", "%.1f dB".format(r.fusedSnrDb),
                    "+%.1f dB total".format(r.snrGainOverSingleDb))
            }
            MetricCard {
                Text("Capture Parameters", style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(4.dp))
                MetricRow("ISO",             "${r.recommendedIso}",                        "maximum sensitivity")
                MetricRow("Exposure",        "%.0f ms".format(r.recommendedExposureMs),    "target: 4000 ms")
                MetricRow("Max handheld",    "%.0f ms".format(r.maxHandheldExposureMs),    "OIS limit — use tripod")
                MetricRow("Aperture",        "f/1.7",                                       "main sensor")
                MetricRow("Pixel size",      "2.4 µm (binned)",                             "4-in-1 on 0.6 µm native")
            }
            MetricCard {
                Text("Colour Recovery", style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(4.dp))
                MetricRow("Fused R/G/B",
                    "%.4f / %.4f / %.4f".format(r.fusedR, r.fusedG, r.fusedB), "very low signal")
                MetricRow("Colour temp",
                    "%.0f K".format(r.colourTempK), "WB conf %.0f%%".format(r.whiteBalanceConf * 100f))
                Spacer(Modifier.height(4.dp))
                Text(
                    "At true zero-lux the colour reconstruction is unreliable — monochrome RAW " +
                    "processing in CLAHE will yield more detail than the AI colour reconstruction.",
                    style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim,
                )
            }
        }

        // Comparison / mode selector guide
        MetricCard {
            Text("Mode Selector Guide", style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold, color = GibberAmber)
            Spacer(Modifier.height(4.dp))
            listOf(
                ">  5 lux"     to "Auto / Night Mode (Samsung default)",
                "0.1–5 lux"   to "Night Mode — 16-in-1 bin + AI  (🌑 Night tab)",
                "0.01–0.1 lux" to "Ultra Dark (this tab) — max ISO + long exposure",
                "< 0.01 lux"  to "🔦 NIR tab + external 850 nm illuminator",
            ).forEach { (lux, mode) ->
                Row(modifier = Modifier.fillMaxWidth().padding(vertical = 2.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(lux,  style = MaterialTheme.typography.labelSmall, fontFamily = FontFamily.Monospace,
                        modifier = Modifier.width(96.dp), color = OnSurfaceDim)
                    Text(mode, style = MaterialTheme.typography.bodySmall)
                }
            }
        }

        Text(
            "⚠️ Extended ISO 12800 operation above 40°C risks permanent hot-pixel damage. " +
            "Check thermal reading in the 🔦 NIR tab before starting long sessions.",
            style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim,
        )
    }
}
