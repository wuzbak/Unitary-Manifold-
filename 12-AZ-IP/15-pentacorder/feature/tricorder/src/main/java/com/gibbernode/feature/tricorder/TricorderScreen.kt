package com.gibbernode.feature.tricorder

import android.content.Intent
import android.net.Uri
import android.provider.MediaStore
import androidx.compose.foundation.Canvas
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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Battery5Bar
import androidx.compose.material.icons.filled.BatteryChargingFull
import androidx.compose.material.icons.filled.Bluetooth
import androidx.compose.material.icons.filled.Camera
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.CellTower
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.GpsFixed
import androidx.compose.material.icons.filled.GraphicEq
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.SyncDisabled
import androidx.compose.material.icons.filled.Share
import androidx.compose.material.icons.filled.Videocam
import androidx.compose.material.icons.filled.Wifi
import androidx.compose.material.icons.filled.WifiTethering
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Divider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.ScrollableTabRow
import androidx.compose.material3.Slider
import androidx.compose.material3.Tab
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.gibbernode.connectivity.ConnectivityAdvisor
import com.gibbernode.energy.EnergyAdvisor
import com.gibbernode.gibberwave.AdaptiveState
import com.gibbernode.gibberwave.CardSeverity
import com.gibbernode.gibberwave.InjectedCard
import com.gibbernode.interpret.SensorInterpreter
import com.gibbernode.interpret.SensorSnapshot
import com.gibbernode.interpret.Severity
import com.gibbernode.interpret.UserRole
import com.gibbernode.ui.GibberAmber
import com.gibbernode.ui.GibberBlue
import com.gibbernode.ui.GibberGreen
import com.gibbernode.ui.GibberRed
import com.gibbernode.ui.OnSurfaceDim
import com.gibbernode.ui.SurfaceDark
import kotlin.math.abs
import kotlin.math.roundToInt

/**
 * TricorderScreen — Sensor / Tricorder tab
 *
 * Three sub-tabs:
 *  0 — Sensors : live readings for all S24 Ultra hardware sensors,
 *                each labelled with its Unitary-Manifold field symbol,
 *                plus the 5D state vector Ψ(t) summary and inline
 *                DEFAULT-role interpretation context.
 *  1 — Cameras : launcher buttons for each camera system (200 MP RAW,
 *                periscope 5×, ultrawide, front, video, slow-motion).
 *  2 — Pentad  : live 5-body Pentad state snapshot driven by current
 *                sensor readings — situation coherence + gap analysis.
 *
 * This screen is the Android port of S24Ultra/scripts/sensor_daemon.py
 * and S24Ultra/docs/SENSOR_MAP.md — every sensor is mapped to a manifold
 * field and shown alongside its field symbol.
 */
@Composable
fun TricorderScreen(viewModel: TricorderViewModel = hiltViewModel()) {
    val state         by viewModel.state.collectAsStateWithLifecycle()
    val adaptiveState by viewModel.adaptiveState.collectAsStateWithLifecycle()
    var tab by remember { mutableIntStateOf(0) }

    Column(modifier = Modifier.fillMaxSize()) {
        ScrollableTabRow(
            selectedTabIndex = tab,
            edgePadding      = 0.dp,
        ) {
            Tab(selected = tab == 0, onClick = { tab = 0 }, text = {
                Text("📡 Sensors", fontSize = 13.sp)
            })
            Tab(selected = tab == 1, onClick = { tab = 1 }, text = {
                Text("📷 Cameras", fontSize = 13.sp)
            })
            Tab(selected = tab == 2, onClick = { tab = 2 }, text = {
                Text("🔮 Pentad", fontSize = 13.sp)
            })
            Tab(selected = tab == 3, onClick = { tab = 3 }, text = {
                Text("⚡ Energy", fontSize = 13.sp)
            })
            Tab(selected = tab == 4, onClick = { tab = 4 }, text = {
                Text("📶 Connect", fontSize = 13.sp)
            })
            Tab(selected = tab == 5, onClick = { tab = 5 }, text = {
                Text("🗺️ GPS Logger", fontSize = 13.sp)
            })
        }

        // ── Assistant hint + adaptive cards (all tabs share these) ────────────
        adaptiveState.screenHints["tricorder"]?.let { hint ->
            AssistantHintBanner(hint = hint, onDismiss = viewModel::clearTricorderHint)
        }
        adaptiveState.dashboardCards.forEach { card ->
            AdaptiveInjectedCard(card = card, onDismiss = { viewModel.removeAdaptiveCard(card.id) })
        }

        when (tab) {
            0 -> SensorsTab(state, pinnedMetrics = adaptiveState.pinnedMetrics)
            1 -> CamerasTab()
            2 -> PentadTab(state)
            3 -> EnergyTab(state, onScanWifi = viewModel::scanWifi, onSetAccessoryPct = viewModel::setAccessoryBattPct)
            4 -> ConnectTab(state, onDiscoverPeers = viewModel::discoverWifiDirect)
            5 -> GpsLoggerTab(state, onStart = viewModel::startGpsTrack, onStop = viewModel::stopGpsTrack, onExport = viewModel::exportGpsTrackCsv)
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 0 — Live Sensors
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun SensorsTab(state: TricorderUiState, pinnedMetrics: List<String> = emptyList()) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        // ── 📌 Pinned metrics (assistant-selected — shown first) ──────────────
        if (pinnedMetrics.isNotEmpty()) {
            PinnedMetricsCard(state = state, pinned = pinnedMetrics)
        }

        // ── Ψ(t) state vector summary ─────────────────────────────────────────
        PsiCard(state)

        // ── Accelerometer — δg_μν ─────────────────────────────────────────────
        SensorCard(
            title  = "📐 Accelerometer  δg_μν",
            field  = "g_μν metric perturbation",
            color  = GibberGreen,
        ) {
            TRow("X",    "%.3f m/s²".format(state.accelX), xyzColor(state.accelX))
            TRow("Y",    "%.3f m/s²".format(state.accelY), xyzColor(state.accelY))
            TRow("Z",    "%.3f m/s²".format(state.accelZ), xyzColor(state.accelZ))
            TRow("|a|",  "%.3f m/s²".format(state.accelMag),
                if (abs(state.accelMag - 9.8f) > 2f) GibberAmber else GibberGreen)
        }

        // ── Gyroscope — Γ^σ_μν ───────────────────────────────────────────────
        SensorCard(
            title  = "🌀 Gyroscope  Γ^σ_μν",
            field  = "Levi-Civita connection",
            color  = GibberBlue,
        ) {
            TRow("ωX", "%.4f rad/s".format(state.gyroX), GibberBlue)
            TRow("ωY", "%.4f rad/s".format(state.gyroY), GibberBlue)
            TRow("ωZ", "%.4f rad/s".format(state.gyroZ), GibberBlue)
            TRow("|ω|","%.4f rad/s".format(state.gyroMag), GibberBlue)
        }

        // ── Magnetometer — H_μν ───────────────────────────────────────────────
        SensorCard(
            title  = "🧲 Magnetometer  H_μν",
            field  = "Kaluza-Klein gauge field",
            color  = GibberAmber,
        ) {
            TRow("BX", "%.2f µT".format(state.magX), GibberAmber)
            TRow("BY", "%.2f µT".format(state.magY), GibberAmber)
            TRow("BZ", "%.2f µT".format(state.magZ), GibberAmber)
            TRow("|B|","%.2f µT".format(state.magMag), GibberAmber)
        }

        // ── Barometer / Environment — B_4 ────────────────────────────────────
        SensorCard(
            title  = "🌡 Environment  B_4 / φ",
            field  = "compact-dimension pressure / energy scalar",
            color  = GibberBlue,
        ) {
            TRow("Pressure",  if (state.pressureHpa  > 0) "%.1f hPa".format(state.pressureHpa)   else "—", GibberBlue)
            TRow("Temp",      if (state.ambientTempC != 0f) "%.1f °C".format(state.ambientTempC)  else "—", GibberBlue)
            TRow("Humidity",  if (state.humidityPct  > 0) "%.0f%%".format(state.humidityPct)      else "—", GibberBlue)
            if (state.pressureHpa > 0) {
                val weatherHint = when {
                    state.pressureHpa >= 1020f -> "✅ High — stable, clear"
                    state.pressureHpa >= 1005f -> "✅ Normal conditions"
                    state.pressureHpa >= 980f  -> "⚠ Low — deteriorating weather"
                    else                       -> "🚨 Very low — storm / underground?"
                }
                InterpretRow(weatherHint)
            }
        }

        // ── Ambient light — photon flux ───────────────────────────────────────
        SensorCard(
            title  = "☀️ Ambient Light  (photon flux)",
            field  = "CMB proxy / inflation probe",
            color  = GibberAmber,
        ) {
            TRow("Illuminance", if (state.lightLux > 0) "%.1f lux".format(state.lightLux) else "—", GibberAmber)
            if (state.lightLux > 0) {
                val lightHint = when {
                    state.lightLux < 1f     -> "🌑 Darkness — torch required"
                    state.lightLux < 50f    -> "🌒 Dim — reduced visibility"
                    state.lightLux < 500f   -> "✅ Normal indoor lighting"
                    state.lightLux < 2000f  -> "🌤 Bright indoor / overcast"
                    state.lightLux < 10000f -> "☀ Full daylight"
                    else                    -> "☀ Direct sun — UV HIGH"
                }
                InterpretRow(lightHint)
            }
        }

        // ── Proximity — boundary condition ────────────────────────────────────
        SensorCard(
            title  = "📏 Proximity  (boundary flag)",
            field  = "field boundary condition",
            color  = OnSurfaceDim,
        ) {
            val prox = if (state.proximityM >= 0) "%.1f cm".format(state.proximityM) else "—"
            TRow("Distance", prox, if (state.proximityM in 0f..5f) GibberRed else GibberGreen)
        }

        // ── Virtual sensors ────────────────────────────────────────────────────
        SensorCard(
            title  = "⚖ Gravity  g_μν local frame",
            field  = "virtual sensor",
            color  = GibberGreen,
        ) {
            TRow("GX", "%.3f m/s²".format(state.gravX), GibberGreen)
            TRow("GY", "%.3f m/s²".format(state.gravY), GibberGreen)
            TRow("GZ", "%.3f m/s²".format(state.gravZ), GibberGreen)
        }

        SensorCard(
            title  = "🧭 Rotation Vector  SO(3)",
            field  = "frame orientation",
            color  = GibberBlue,
        ) {
            TRow("RX", "%.4f".format(state.rotX), GibberBlue)
            TRow("RY", "%.4f".format(state.rotY), GibberBlue)
            TRow("RZ", "%.4f".format(state.rotZ), GibberBlue)
        }

        SensorCard(
            title  = "➡ Linear Acceleration  (inertial)",
            field  = "inertial 3-vector (gravity removed)",
            color  = GibberGreen,
        ) {
            TRow("laX", "%.3f m/s²".format(state.linAccX), GibberGreen)
            TRow("laY", "%.3f m/s²".format(state.linAccY), GibberGreen)
            TRow("laZ", "%.3f m/s²".format(state.linAccZ), GibberGreen)
        }

        SensorCard(
            title  = "👣 Step Counter  (path integral)",
            field  = "phase-space path integral",
            color  = GibberAmber,
        ) {
            TRow("Steps", "${state.stepCount}", GibberAmber)
        }

        // ── Heart rate — φ-homeostasis ─────────────────────────────────────────
        SensorCard(
            title  = "❤️ Heart Rate  J^μ_inf",
            field  = "φ-homeostasis frequency",
            color  = GibberRed,
        ) {
            TRow("HR", if (state.heartRateBpm > 0) "${state.heartRateBpm} bpm" else "—",
                when {
                    state.heartRateBpm > 100 -> GibberRed
                    state.heartRateBpm > 0   -> GibberGreen
                    else                     -> OnSurfaceDim
                })
            if (state.heartRateBpm > 0) {
                val hrHint = when {
                    state.heartRateBpm < 40  -> "🚨 Severe bradycardia — urgent"
                    state.heartRateBpm < 60  -> "⚠ Bradycardia"
                    state.heartRateBpm <= 100 -> "✅ Normal range"
                    state.heartRateBpm <= 110 -> "⚠ Mild tachycardia"
                    state.heartRateBpm <= 130 -> "⚠ Tachycardia"
                    else -> "🚨 Severe tachycardia"
                }
                InterpretRow(hrHint)
            }
        }

        // ── GPS — geodesic / λ ────────────────────────────────────────────────
        SensorCard(
            title  = "📍 GPS  λ geodesic",
            field  = "geodesic path on curved 5-manifold",
            color  = GibberBlue,
        ) {
            TRow("Latitude",  if (state.latitude  != 0.0) "%.6f°".format(state.latitude)  else "—", GibberBlue)
            TRow("Longitude", if (state.longitude != 0.0) "%.6f°".format(state.longitude) else "—", GibberBlue)
            TRow("Altitude",  "%.1f m".format(state.altitude),  GibberBlue)
            TRow("Accuracy",  "±%.1f m".format(state.gpsAccM),  GibberBlue)
            TRow("Speed",     "%.2f m/s".format(state.gpsSpeedMs), GibberBlue)
            TRow("Bearing",   "%.1f°".format(state.gpsBearing), GibberBlue)
        }

        // ── Battery / thermal — φ scalar ──────────────────────────────────────
        SensorCard(
            title  = "🔋 Battery  φ energy scalar",
            field  = "energy state / thermal field",
            color  = GibberGreen,
        ) {
            TRow("Level", if (state.batteryPct >= 0) "${state.batteryPct}%" else "—",
                battColor(state.batteryPct))
            TRow("Temp",  if (state.batteryTempC > 0) "%.1f°C".format(state.batteryTempC) else "—",
                tempColor(state.batteryTempC))
            if (state.batteryTempC > 40f)
                InterpretRow("⚠ Thermal throttle zone — sensor accuracy may degrade")
            if (state.batteryPct in 0..15)
                InterpretRow("🚨 Low battery — transmit GPS now if in field")
        }

        // ── Sensor inventory ──────────────────────────────────────────────────
        if (state.availableSensors.isNotEmpty()) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
            ) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text(
                        text  = "Available sensors: ${state.availableSensors.size}",
                        style = MaterialTheme.typography.labelSmall,
                        color = GibberGreen,
                    )
                    if (state.missingSensors.isNotEmpty()) {
                        Text(
                            text  = "Not present: ${state.missingSensors.joinToString()}",
                            style = MaterialTheme.typography.labelSmall,
                            color = OnSurfaceDim,
                        )
                    }
                }
            }
        }

        Spacer(Modifier.height(24.dp))
    }
}

// ── Ψ(t) state vector card ────────────────────────────────────────────────────

@Composable
private fun PsiCard(state: TricorderUiState) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors   = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.15f)
        ),
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Text(
                text  = "Ψ(t)  — Manifold State Vector",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold,
                color = GibberGreen,
            )
            Spacer(Modifier.height(6.dp))
            Text(
                text = buildString {
                    appendLine("g_μν  : [%.2f, %.2f, %.2f]".format(state.accelX, state.accelY, state.accelZ))
                    appendLine("Γ^σ   : [%.3f, %.3f, %.3f]".format(state.gyroX,  state.gyroY,  state.gyroZ))
                    appendLine("H_μν  : [%.1f, %.1f, %.1f] µT".format(state.magX,   state.magY,   state.magZ))
                    appendLine("B_4   : %.1f hPa".format(state.pressureHpa))
                    appendLine("φ     : bat=${state.batteryPct}%  T=${state.batteryTempC}°C")
                    if (state.heartRateBpm > 0)
                        appendLine("J^μ   : ${state.heartRateBpm} bpm")
                    if (state.latitude != 0.0)
                        append("λ     : %.4f, %.4f".format(state.latitude, state.longitude))
                },
                style  = MaterialTheme.typography.bodySmall,
                fontFamily = FontFamily.Monospace,
                color  = MaterialTheme.colorScheme.onSurface,
            )
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 1 — Camera Launchers
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun CamerasTab() {
    val context = LocalContext.current

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(
            text  = "S24 Ultra — 200 MP Camera Array",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onSurface,
        )
        Text(
            text  = "All cameras are scientific instruments. Launch via intent; save RAW DNG for manifold analysis.",
            style = MaterialTheme.typography.bodySmall,
            color = OnSurfaceDim,
        )

        Divider(color = MaterialTheme.colorScheme.outline)

        // Photo launchers
        CameraSection(title = "📸 Photo Capture") {
            CameraButton(
                label    = "200 MP Wide — Main sensor (f/1.7)",
                subLabel = "1/1.3″  •  RAW DNG  •  ~23 mm equiv.",
                icon     = Icons.Filled.CameraAlt,
                color    = GibberGreen,
                onClick  = {
                    context.startActivity(Intent(MediaStore.ACTION_IMAGE_CAPTURE).apply {
                        putExtra("android.intent.extras.LENS_FACING_FRONT", 0)
                    })
                },
            )
            CameraButton(
                label    = "50 MP Periscope 5× Telephoto (f/3.4)",
                subLabel = "5× optical  •  100× Space Zoom  •  111 mm equiv.",
                icon     = Icons.Filled.Camera,
                color    = GibberBlue,
                onClick  = { context.startActivity(Intent(MediaStore.ACTION_IMAGE_CAPTURE)) },
            )
            CameraButton(
                label    = "12 MP Ultrawide (f/2.2)",
                subLabel = "Dual-pixel PDAF  •  macro  •  13 mm equiv.",
                icon     = Icons.Filled.Camera,
                color    = GibberAmber,
                onClick  = { context.startActivity(Intent(MediaStore.ACTION_IMAGE_CAPTURE)) },
            )
            CameraButton(
                label    = "10 MP Short Telephoto 3× (f/2.4)",
                subLabel = "3× optical  •  portrait  •  70 mm equiv.",
                icon     = Icons.Filled.Camera,
                color    = GibberAmber,
                onClick  = { context.startActivity(Intent(MediaStore.ACTION_IMAGE_CAPTURE)) },
            )
            CameraButton(
                label    = "12 MP Front (f/2.2)",
                subLabel = "4K video  •  face unlock  •  26 mm equiv.",
                icon     = Icons.Filled.Camera,
                color    = GibberBlue,
                onClick  = {
                    context.startActivity(Intent(MediaStore.ACTION_IMAGE_CAPTURE).apply {
                        putExtra("android.intent.extras.LENS_FACING_FRONT", 1)
                    })
                },
            )
        }

        // Video launchers
        CameraSection(title = "🎬 Video Capture") {
            CameraButton(
                label    = "4K Video (main sensor)",
                subLabel = "60 fps  •  OIS  •  HDR10+",
                icon     = Icons.Filled.Videocam,
                color    = GibberRed,
                onClick  = { context.startActivity(Intent(MediaStore.ACTION_VIDEO_CAPTURE)) },
            )
            CameraButton(
                label    = "Slow Motion",
                subLabel = "240 fps / 480 fps — temporal field sampling",
                icon     = Icons.Filled.Videocam,
                color    = GibberRed,
                onClick  = {
                    context.startActivity(Intent("com.sec.android.app.camera").apply {
                        putExtra("mode", "slowmotion")
                        addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    }.takeIf {
                        context.packageManager.resolveActivity(it, 0) != null
                    } ?: Intent(MediaStore.ACTION_VIDEO_CAPTURE))
                },
            )
        }

        // Science notes
        CameraSection(title = "🔬 Science Notes") {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
            ) {
                Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text("Shot noise protocol (from CAMERA_PLATFORM.md):",
                        style = MaterialTheme.typography.labelSmall, color = GibberGreen)
                    Text("1. Samsung Camera → Settings → Pictures → RAW copies (DNG + JPEG)",
                        style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurface)
                    Text("2. Copy .dng to Termux: cp ~/storage/dcim/Camera/*.dng ~/S24Ultra/data/",
                        style = MaterialTheme.typography.bodySmall, fontFamily = FontFamily.Monospace,
                        color = MaterialTheme.colorScheme.onSurface)
                    Text("3. Run: python scripts/camera_shot_noise.py --input data/ --output logs/",
                        style = MaterialTheme.typography.bodySmall, fontFamily = FontFamily.Monospace,
                        color = MaterialTheme.colorScheme.onSurface)
                    Spacer(Modifier.height(6.dp))
                    Text("Manifold field map: luminance I(x,y) → φ-field proxy → |∇φ| gradient map",
                        style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
                    Text("Feed output to: Unitary-Manifold/tests/test_quantum_unification.py",
                        style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                }
            }
        }

        // Ultra Low Light / Zero-Lux modes
        CameraSection(title = "🌑 Ultra Low Light / Zero-Lux") {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
            ) {
                Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text("Pro Mode — Total Darkness Protocol",
                        style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold, color = GibberBlue)
                    Spacer(Modifier.height(2.dp))
                    listOf(
                        "Mode"     to "Pro  (Samsung Camera → Pro)",
                        "ISO"      to "12800  (maximum sensitivity)",
                        "Shutter"  to "30 s  (maximum handheld with OIS: 4 s)",
                        "White Bal" to "Auto or 3200 K",
                        "Format"   to "RAW + JPEG  (Settings → Pictures → RAW copies)",
                        "Stabilise" to "Phone on tripod or braced surface",
                        "Flash"    to "OFF — flash kills long-exposure",
                    ).forEach { (k, v) ->
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            Text(k, style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim,
                                modifier = Modifier.width(72.dp))
                            Text(v, style = MaterialTheme.typography.bodySmall, fontFamily = FontFamily.Monospace)
                        }
                    }
                    Spacer(Modifier.height(4.dp))
                    Text("For pixel-binned night mode: use Samsung Night Mode instead (automatic 16-in-1 + AI fusion).",
                        style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                    Text("For IR darkness: use 🔬 Optical Physics → 🔦 Active NIR with external 850 nm illuminator.",
                        style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                }
            }
            CameraButton(
                label    = "🌑 Open Night Mode (16-in-1 binning + AI)",
                subLabel = "Samsung Camera → Night — best for < 5 lux scenes",
                icon     = Icons.Filled.CameraAlt,
                color    = GibberBlue,
                onClick  = {
                    context.startActivity(
                        Intent("com.sec.android.app.camera").apply {
                            putExtra("mode", "night")
                            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                        }.takeIf { context.packageManager.resolveActivity(it, 0) != null }
                        ?: Intent(MediaStore.ACTION_IMAGE_CAPTURE)
                    )
                },
            )
            CameraButton(
                label    = "⚙️ Open Pro Mode (manual ISO/shutter control)",
                subLabel = "For zero-lux RAW capture — ISO 12800 · 30 s shutter",
                icon     = Icons.Filled.CameraAlt,
                color    = GibberAmber,
                onClick  = {
                    context.startActivity(
                        Intent("com.sec.android.app.camera").apply {
                            putExtra("mode", "pro")
                            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                        }.takeIf { context.packageManager.resolveActivity(it, 0) != null }
                        ?: Intent(MediaStore.ACTION_IMAGE_CAPTURE)
                    )
                },
            )
        }

        Spacer(Modifier.height(24.dp))
    }
}

@Composable
private fun CameraSection(title: String, content: @Composable () -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(
            text  = title,
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onSurface,
        )
        content()
    }
}

@Composable
private fun CameraButton(
    label: String,
    subLabel: String,
    icon: ImageVector,
    color: Color,
    onClick: () -> Unit,
) {
    Button(
        onClick = onClick,
        colors  = ButtonDefaults.buttonColors(containerColor = color.copy(alpha = 0.15f)),
        shape   = RoundedCornerShape(12.dp),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(icon, contentDescription = null, tint = color, modifier = Modifier.size(22.dp))
            Column {
                Text(label,    style = MaterialTheme.typography.bodySmall,
                    fontWeight = FontWeight.Bold, color = color)
                Text(subLabel, style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 2 — Pentad State
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun PentadTab(state: TricorderUiState) {
    // Build a SensorSnapshot from the live TricorderUiState and run interpretation
    val snap = SensorSnapshot(
        accelX       = state.accelX,
        accelY       = state.accelY,
        accelZ       = state.accelZ,
        accelMag     = state.accelMag,
        linAccX      = state.linAccX,
        linAccY      = state.linAccY,
        linAccZ      = state.linAccZ,
        magMag       = state.magMag,
        pressureHpa  = state.pressureHpa,
        ambientTempC = state.ambientTempC,
        humidityPct  = state.humidityPct,
        lightLux     = state.lightLux,
        latitude     = state.latitude,
        longitude    = state.longitude,
        altitude     = state.altitude,
        gpsAccM      = state.gpsAccM,
        gpsSpeedMs   = state.gpsSpeedMs,
        batteryPct   = state.batteryPct,
        batteryTempC = state.batteryTempC,
        heartRateBpm = state.heartRateBpm,
    )
    val report = SensorInterpreter.interpret(snap, UserRole.DEFAULT)
    val pentad = report.pentad

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        Text(
            text       = "🔮 Unitary Pentad — Live State",
            style      = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color      = GibberGreen,
        )
        Text(
            text  = "U·Ψ_n = Ψ_{n+1}  •  (5,7) braid  •  c_s = 12/37 ≈ 0.324",
            style = MaterialTheme.typography.labelSmall,
            color = OnSurfaceDim,
            fontFamily = FontFamily.Monospace,
        )

        // Coherence summary card
        val cohPct = (pentad.situationCoherence * 100).toInt()
        val cohColor = when {
            cohPct >= 80 -> GibberGreen
            cohPct >= 50 -> GibberAmber
            else -> GibberRed
        }
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors   = CardDefaults.cardColors(containerColor = cohColor.copy(alpha = 0.10f)),
        ) {
            Row(
                modifier = Modifier.padding(16.dp).fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Column {
                    Text("Situation Coherence", style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold, color = cohColor)
                    Text("Mean ΔI = %.3f".format(pentad.meanInfoGap),
                        style = MaterialTheme.typography.labelSmall,
                        color = OnSurfaceDim, fontFamily = FontFamily.Monospace)
                }
                Text("$cohPct%", style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold, color = cohColor)
            }
        }

        // 5-body φ values
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
        ) {
            Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text("Body φ Values", style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Bold, color = GibberGreen)
                PentadBodyBarRow("Ψ_univ  (sensors)",  pentad.phiUniv,  GibberBlue)
                PentadBodyBarRow("Ψ_brain (biology)",  pentad.phiBrain, GibberRed)
                PentadBodyBarRow("Ψ_human (intent)",   pentad.phiHuman, GibberAmber)
                PentadBodyBarRow("Ψ_AI    (precision)",pentad.phiAI,    GibberGreen)
                PentadBodyBarRow("β·C     (trust)",     pentad.phiTrust, GibberBlue)

                if (!pentad.isBraidStable) {
                    Text(
                        text  = "⚠ BRAID UNSTABLE — φ_trust < 10%. Coherence not guaranteed.",
                        style = MaterialTheme.typography.labelSmall,
                        color = GibberRed, fontWeight = FontWeight.Bold,
                    )
                }
            }
        }

        // 10 pairwise ΔI gaps
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
        ) {
            Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text("All 10 Pairwise ΔI Gaps", style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Bold, color = GibberGreen)
                Text("Harmonic State = all gaps → 0",
                    style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                pentad.pairwiseGaps
                    .sortedByDescending { it.second }
                    .forEach { (label, gap) ->
                        val gapColor = when {
                            gap > 0.4f -> GibberRed
                            gap > 0.2f -> GibberAmber
                            else -> GibberGreen
                        }
                        TRow(label, "ΔI = %.3f".format(gap), gapColor)
                    }
            }
        }

        // Situation report summary
        if (report.findings.isNotEmpty()) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors   = CardDefaults.cardColors(
                    containerColor = severityCardColor(report.severity).copy(alpha = 0.08f)
                ),
            ) {
                Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text("Field Status — DEFAULT role", style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Bold, color = severityCardColor(report.severity))
                    Text(report.narrative, style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurface)
                    if (report.actions.isNotEmpty()) {
                        Divider(color = MaterialTheme.colorScheme.outline)
                        report.actions.forEach { action ->
                            Text("▶ $action", style = MaterialTheme.typography.labelSmall,
                                color = severityCardColor(report.severity))
                        }
                    }
                }
            }
        }

        Text(
            text  = "Open the Translate tab for role-specific interpretation (NURSE / RESPONDER / ENGINEER).",
            style = MaterialTheme.typography.labelSmall,
            color = OnSurfaceDim,
        )

        Spacer(Modifier.height(24.dp))
    }
}

@Composable
private fun PentadBodyBarRow(label: String, phi: Float, color: Color) {
    Row(
        modifier          = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text(label, style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim,
            modifier = Modifier.width(130.dp))
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
            fontFamily = FontFamily.Monospace, color = color,
            modifier = Modifier.width(36.dp))
    }
}

private fun severityCardColor(severity: com.gibbernode.interpret.Severity): Color = when (severity) {
    com.gibbernode.interpret.Severity.OK       -> GibberGreen
    com.gibbernode.interpret.Severity.CAUTION  -> GibberBlue
    com.gibbernode.interpret.Severity.WARNING  -> GibberAmber
    com.gibbernode.interpret.Severity.CRITICAL -> GibberRed
}

// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun SensorCard(
    title: String,
    field: String,
    color: Color,
    content: @Composable () -> Unit,
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Text(title, style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold, color = color)
            Text(field, style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
            Spacer(Modifier.height(8.dp))
            content()
        }
    }
}

@Composable
private fun TRow(label: String, value: String, valueColor: Color) {
    Row(
        modifier              = Modifier.fillMaxWidth().padding(vertical = 1.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment     = Alignment.CenterVertically,
    ) {
        Text(label, style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
        Text(value,
            style = MaterialTheme.typography.bodySmall,
            fontFamily = FontFamily.Monospace,
            color = valueColor,
            fontWeight = FontWeight.Medium,
        )
    }
}

@Composable
private fun InterpretRow(text: String) {
    Text(
        text  = text,
        style = MaterialTheme.typography.labelSmall,
        color = GibberAmber,
        fontWeight = FontWeight.Medium,
        modifier = Modifier.padding(top = 4.dp),
    )
}

// ── Colour helpers ────────────────────────────────────────────────────────────

private fun xyzColor(v: Float): Color = when {
    v >  5f || v < -5f -> GibberRed
    v >  2f || v < -2f -> GibberAmber
    else               -> GibberGreen
}

private fun battColor(pct: Int): Color = when {
    pct in 0..15  -> GibberRed
    pct in 16..30 -> GibberAmber
    else          -> GibberGreen
}

private fun tempColor(t: Float): Color = when {
    t > 40f -> GibberRed
    t > 35f -> GibberAmber
    else    -> GibberGreen
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 3 — Energy Advisory
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun EnergyTab(
    state: TricorderUiState,
    onScanWifi: () -> Unit,
    onSetAccessoryPct: (Int) -> Unit,
) {
    // Local slider state for accessory battery (default: -1 = unknown = slider at 0)
    var accessorySlider by remember {
        mutableFloatStateOf(if (state.accessoryBattPct >= 0) state.accessoryBattPct.toFloat() else 0f)
    }

    val band       = state.energyBand
    val bandColor  = energyBandColor(band)
    val advisory   = state.harvestAdvisory
    val shareDecision = state.powerShareDecision

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {

        // ── Battery Band ───────────────────────────────────────────────────────
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors   = CardDefaults.cardColors(containerColor = bandColor.copy(alpha = 0.12f)),
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Column {
                        Text(
                            text  = "${band.emoji}  ${band.label}",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold, color = bandColor,
                        )
                        Text(
                            text  = "Battery: ${state.batteryPct}%  •  ${state.batteryTempC}°C",
                            style = MaterialTheme.typography.bodySmall,
                            fontFamily = FontFamily.Monospace, color = OnSurfaceDim,
                        )
                    }
                    Icon(
                        imageVector = if (state.batteryPct > 80) Icons.Filled.BatteryChargingFull
                                      else Icons.Filled.Battery5Bar,
                        contentDescription = null,
                        tint = bandColor,
                        modifier = Modifier.size(40.dp),
                    )
                }
                if (state.batteryPct >= 0) {
                    Spacer(Modifier.height(10.dp))
                    LinearProgressIndicator(
                        progress   = (state.batteryPct / 100f).coerceIn(0f, 1f),
                        modifier   = Modifier.fillMaxWidth().height(8.dp).clip(RoundedCornerShape(4.dp)),
                        color      = bandColor,
                        trackColor = bandColor.copy(alpha = 0.2f),
                    )
                }
                Spacer(Modifier.height(8.dp))
                val tip = when (band) {
                    EnergyAdvisor.EnergyBand.CRITICAL ->
                        "🚨 Lockdown — transmit GPS / SOS only. Harvest mode active."
                    EnergyAdvisor.EnergyBand.FLOOR ->
                        "🟠 Read-only sensors. No sharing. Move to harvest position."
                    EnergyAdvisor.EnergyBand.BALANCED ->
                        "🟡 Normal operation. Harvest advisory active. No sharing."
                    EnergyAdvisor.EnergyBand.SHARE_ELIGIBLE ->
                        "🟢 Sharing allowed. Connect accessory to activate PowerShare."
                    EnergyAdvisor.EnergyBand.SURPLUS ->
                        "💚 Surplus. Actively offer PowerShare to mission-critical accessories."
                }
                Text(tip, style = MaterialTheme.typography.bodySmall, color = bandColor)
            }
        }

        // ── RF Harvest Advisory ────────────────────────────────────────────────
        SensorCard(
            title = "📡 RF Harvest Advisory",
            field = "Ambient WiFi → rectenna → trickle DC (advisory only)",
            color = GibberBlue,
        ) {
            if (advisory.totalAps > 0) {
                TRow("Est. harvest",  "%.1f µW".format(advisory.rfEstimateUw), GibberBlue)
                TRow("Best AP",       advisory.bestSsid, GibberBlue)
                TRow("Best RSSI",     "${advisory.bestRssiDbm} dBm", rssiColor(advisory.bestRssiDbm))
                TRow("APs detected",  "${advisory.totalAps}", GibberGreen)
                Spacer(Modifier.height(6.dp))
                // Harvest gauge: scale 0–500 µW as 100%
                val gaugeProgress = (advisory.rfEstimateUw / 500.0).coerceIn(0.0, 1.0).toFloat()
                LinearProgressIndicator(
                    progress   = gaugeProgress,
                    modifier   = Modifier.fillMaxWidth().height(6.dp).clip(RoundedCornerShape(3.dp)),
                    color      = if (gaugeProgress > 0.4f) GibberGreen else GibberAmber,
                    trackColor = GibberBlue.copy(alpha = 0.15f),
                )
                Text("0 µW ──────────────── 500 µW (Sentinel heartbeat target)",
                    style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
            }
            Spacer(Modifier.height(6.dp))
            InterpretRow(advisory.hint)
            Spacer(Modifier.height(10.dp))
            Button(
                onClick = onScanWifi,
                colors  = ButtonDefaults.buttonColors(containerColor = GibberBlue.copy(alpha = 0.2f)),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Icon(Icons.Filled.Refresh, contentDescription = null,
                    tint = GibberBlue, modifier = Modifier.size(18.dp))
                Spacer(Modifier.width(8.dp))
                Text("Scan WiFi", color = GibberBlue, fontWeight = FontWeight.Bold)
            }
            Spacer(Modifier.height(4.dp))
            Text(
                "Actual power delivery requires an external rectenna (e.g. Powercast P2110B) " +
                "connected via USB-C.  This advisory shows ambient RF density only.",
                style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim,
            )
        }

        // ── WiFi AP Table ─────────────────────────────────────────────────────
        if (state.wifiScanAps.isNotEmpty()) {
            SensorCard(
                title = "🛜 Detected Access Points",
                field = "RSSI scan results — ${state.wifiScanAps.size} APs",
                color = GibberGreen,
            ) {
                state.wifiScanAps.entries
                    .sortedByDescending { it.value }
                    .take(8)
                    .forEach { (ssid, rssi) ->
                        TRow(ssid.take(22), "$rssi dBm", rssiColor(rssi))
                    }
                if (state.wifiScanAps.size > 8) {
                    Text(
                        text  = "…and ${state.wifiScanAps.size - 8} more",
                        style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim,
                    )
                }
            }
        }

        // ── PowerShare Governance ─────────────────────────────────────────────
        val shareColor = if (shareDecision.canShare) GibberGreen else GibberAmber
        SensorCard(
            title = "🔋 PowerShare Governance",
            field = "Wireless PowerShare — 15W Qi reverse charging",
            color = shareColor,
        ) {
            Text(
                text  = "Accessory battery level:",
                style = MaterialTheme.typography.bodySmall,
                color = OnSurfaceDim,
            )
            Spacer(Modifier.height(4.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Slider(
                    value         = accessorySlider,
                    onValueChange = { accessorySlider = it },
                    onValueChangeFinished = { onSetAccessoryPct(accessorySlider.roundToInt()) },
                    valueRange    = 0f..100f,
                    modifier      = Modifier.weight(1f),
                )
                Text(
                    text  = if (accessorySlider < 1f) "—" else "${accessorySlider.roundToInt()}%",
                    style = MaterialTheme.typography.labelMedium,
                    fontFamily = FontFamily.Monospace,
                    color = battColor(accessorySlider.roundToInt()),
                    modifier = Modifier.width(36.dp),
                )
            }
            Spacer(Modifier.height(8.dp))
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors   = CardDefaults.cardColors(
                    containerColor = shareColor.copy(alpha = 0.10f)
                ),
            ) {
                Row(
                    modifier = Modifier.padding(12.dp).fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(10.dp),
                ) {
                    Icon(
                        imageVector = Icons.Filled.Share,
                        contentDescription = null,
                        tint = shareColor,
                        modifier = Modifier.size(24.dp),
                    )
                    Column {
                        Text(
                            text  = if (shareDecision.canShare) "✅ Share authorized" else "⛔ Share blocked",
                            style = MaterialTheme.typography.labelMedium,
                            fontWeight = FontWeight.Bold, color = shareColor,
                        )
                        Text(
                            text  = shareDecision.reason,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurface,
                        )
                        if (shareDecision.canShare) {
                            Text(
                                text  = "Fill target: ${shareDecision.fillTargetPct}% (survival level)",
                                style = MaterialTheme.typography.labelSmall,
                                color = GibberGreen,
                            )
                        }
                    }
                }
            }
            Spacer(Modifier.height(8.dp))
            Text(
                text  = "Activate via Settings → Battery → Wireless PowerShare " +
                        "when conditions above are met. Auto-stops at 30% sentinel.",
                style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim,
            )
        }

        Spacer(Modifier.height(24.dp))
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Tab 4 — Resilient Connectivity
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun ConnectTab(
    state: TricorderUiState,
    onDiscoverPeers: () -> Unit,
) {
    val tier = state.connectivityTier

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {

        // ── Active tier banner ────────────────────────────────────────────────
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors   = CardDefaults.cardColors(
                containerColor = GibberGreen.copy(alpha = 0.12f)
            ),
        ) {
            Row(
                modifier = Modifier.padding(16.dp).fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(14.dp),
            ) {
                Icon(
                    imageVector = tierIcon(tier),
                    contentDescription = null,
                    tint = GibberGreen,
                    modifier = Modifier.size(36.dp),
                )
                Column {
                    Text("Active Tier", style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                    Text(
                        text  = "${tier.emoji}  ${tier.label}",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold, color = GibberGreen,
                    )
                    Text(
                        text  = "Max throughput: ${formatBps(tier.maxBps)}",
                        style = MaterialTheme.typography.labelSmall,
                        fontFamily = FontFamily.Monospace, color = OnSurfaceDim,
                    )
                }
            }
        }

        // ── Tier stack ────────────────────────────────────────────────────────
        SensorCard(
            title = "📶 Connectivity Tier Stack",
            field = "Graceful degradation — best available channel",
            color = GibberBlue,
        ) {
            ConnectivityAdvisor.ConnectivityTier.entries.forEach { t ->
                val isActive = t == tier
                val rowColor = if (isActive) GibberGreen else OnSurfaceDim
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp)
                        .clip(RoundedCornerShape(6.dp))
                        .background(if (isActive) GibberGreen.copy(alpha = 0.08f) else Color.Transparent)
                        .padding(horizontal = 8.dp, vertical = 3.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween,
                ) {
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(t.emoji, style = MaterialTheme.typography.bodyMedium)
                        Text(
                            t.label,
                            style = MaterialTheme.typography.bodySmall,
                            color = rowColor,
                            fontWeight = if (isActive) FontWeight.Bold else FontWeight.Normal,
                        )
                    }
                    if (isActive) {
                        Text(
                            "◀ ACTIVE",
                            style = MaterialTheme.typography.labelSmall,
                            color = GibberGreen,
                            fontWeight = FontWeight.Bold,
                        )
                    } else {
                        Text(
                            formatBps(t.maxBps),
                            style = MaterialTheme.typography.labelSmall,
                            fontFamily = FontFamily.Monospace,
                            color = OnSurfaceDim,
                        )
                    }
                }
            }
        }

        // ── GPS quality ───────────────────────────────────────────────────────
        SensorCard(
            title = "📍 GPS Quality",
            field = "GNSS / AGPS / dead reckoning status",
            color = GibberBlue,
        ) {
            TRow("Accuracy", if (state.gpsAccM > 0f) "±%.0f m".format(state.gpsAccM) else "No fix", GibberBlue)
            TRow("AGPS",
                if (state.hasCarrier || state.hasWifi) "✅ Available (~5 s fix)" else "⚠ Unavailable (~60 s cold fix)",
                if (state.hasCarrier || state.hasWifi) GibberGreen else GibberAmber,
            )
            TRow("Fix estimate", "${state.gpsFixEstimateSec} s", GibberBlue)
            Spacer(Modifier.height(6.dp))
            InterpretRow(state.gpsQualityHint)
            Spacer(Modifier.height(8.dp))
            val drColor = if (state.deadReckonAvailable) GibberGreen else OnSurfaceDim
            Row(
                modifier = Modifier.fillMaxWidth()
                    .clip(RoundedCornerShape(6.dp))
                    .background(drColor.copy(alpha = 0.08f))
                    .padding(10.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                Icon(Icons.Filled.GpsFixed, contentDescription = null,
                    tint = drColor, modifier = Modifier.size(20.dp))
                Column {
                    Text(
                        text  = if (state.deadReckonAvailable) "✅ Dead reckoning AVAILABLE"
                                else "⚠ Dead reckoning UNAVAILABLE",
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Bold, color = drColor,
                    )
                    Text(
                        text  = "Requires: accel ✓  gyro ✓  mag ✓  (all 3 present = DR-capable)",
                        style = MaterialTheme.typography.labelSmall,
                        color = OnSurfaceDim,
                    )
                    if (state.deadReckonAvailable) {
                        Text(
                            text  = "IMU can bridge GPS gaps via sensor fusion.  Accuracy degrades ~1–5 m/min.",
                            style = MaterialTheme.typography.labelSmall,
                            color = drColor,
                        )
                    }
                }
            }
        }

        // ── WiFi Direct mesh ──────────────────────────────────────────────────
        SensorCard(
            title = "📡 WiFi Direct Mesh",
            field = "Carrier-free P2P — no access point required",
            color = if (state.hasWifiDirect) GibberGreen else GibberAmber,
        ) {
            TRow("Peers found", "${state.wifiDirectPeerCount}",
                if (state.wifiDirectPeerCount > 0) GibberGreen else OnSurfaceDim)
            if (state.wifiDirectPeerNames.isNotEmpty()) {
                Spacer(Modifier.height(4.dp))
                state.wifiDirectPeerNames.forEach { name ->
                    TRow("  •  $name", "Pentacorder peer", GibberGreen)
                }
            }
            Spacer(Modifier.height(10.dp))
            OutlinedButton(
                onClick  = onDiscoverPeers,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Icon(Icons.Filled.WifiTethering, contentDescription = null,
                    modifier = Modifier.size(18.dp))
                Spacer(Modifier.width(8.dp))
                Text("Discover Peers")
            }
            Spacer(Modifier.height(6.dp))
            Text(
                text  = "WiFi Direct forms a mesh between nearby Pentacorder devices " +
                        "with no carrier or AP needed.  Range: ~100 m.  Throughput: ~25 Mbps.",
                style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim,
            )
        }

        // ── Data resilience ───────────────────────────────────────────────────
        SensorCard(
            title = "💾 Data Resilience",
            field = "Offline-first cache-and-forward",
            color = GibberAmber,
        ) {
            val isOffline = tier == ConnectivityAdvisor.ConnectivityTier.OFFLINE
            if (isOffline) {
                InterpretRow("⚠ All links offline — UPBHub queuing tokens locally")
            }
            TRow("Local queue capacity", "256 tokens", GibberAmber)
            TRow("Sync on reconnect",    "✅ Automatic", GibberGreen)
            TRow("Acoustic relay",       "✅ Always on (~5 m)", GibberGreen)
            Spacer(Modifier.height(6.dp))
            Text(
                text  = "All sensor telemetry, GPS tokens, and VITALS payloads are " +
                        "queued in the UPBHub local channel.  When any tier above " +
                        "Acoustic becomes available, queued tokens flush automatically.",
                style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim,
            )
        }

        Spacer(Modifier.height(24.dp))
    }
}

// ── Connectivity helpers ──────────────────────────────────────────────────────

private fun tierIcon(tier: ConnectivityAdvisor.ConnectivityTier): ImageVector = when (tier) {
    ConnectivityAdvisor.ConnectivityTier.CARRIER            -> Icons.Filled.CellTower
    ConnectivityAdvisor.ConnectivityTier.WIFI               -> Icons.Filled.Wifi
    ConnectivityAdvisor.ConnectivityTier.WIFI_DIRECT        -> Icons.Filled.WifiTethering
    ConnectivityAdvisor.ConnectivityTier.BLUETOOTH          -> Icons.Filled.Bluetooth
    ConnectivityAdvisor.ConnectivityTier.GIBBERLINK_ACOUSTIC -> Icons.Filled.GraphicEq
    ConnectivityAdvisor.ConnectivityTier.OFFLINE            -> Icons.Filled.SyncDisabled
}

private fun formatBps(bps: Long): String = when {
    bps >= 1_000_000L -> "${bps / 1_000_000L} Mbps"
    bps >= 1_000L     -> "${bps / 1_000L} kbps"
    bps > 0L          -> "$bps bps"
    else              -> "offline"
}

private fun rssiColor(rssi: Int): Color = when {
    rssi > -50 -> GibberGreen
    rssi > -65 -> GibberAmber
    else       -> GibberRed
}

private fun energyBandColor(band: EnergyAdvisor.EnergyBand): Color = when (band) {
    EnergyAdvisor.EnergyBand.CRITICAL       -> GibberRed
    EnergyAdvisor.EnergyBand.FLOOR          -> GibberAmber
    EnergyAdvisor.EnergyBand.BALANCED       -> GibberAmber
    EnergyAdvisor.EnergyBand.SHARE_ELIGIBLE -> GibberGreen
    EnergyAdvisor.EnergyBand.SURPLUS        -> GibberGreen
}

// ─────────────────────────────────────────────────────────────────────────────
// 📌 Pinned metrics summary card (Item 3)
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun PinnedMetricsCard(state: TricorderUiState, pinned: List<String>) {
    SensorCard(
        title = "📌 Pinned Metrics",
        field = "assistant-pinned sensor fields",
        color = GibberAmber,
    ) {
        pinned.forEach { key ->
            val (label, value) = when (key) {
                "pressure_hpa"   -> "Pressure"   to if (state.pressureHpa  > 0f) "%.1f hPa".format(state.pressureHpa)   else "—"
                "heart_rate_bpm" -> "Heart Rate" to if (state.heartRateBpm > 0)  "${state.heartRateBpm} bpm"              else "—"
                "battery_pct"    -> "Battery"    to if (state.batteryPct  >= 0)  "${state.batteryPct}%"                   else "—"
                "battery_temp_c" -> "Bat Temp"   to if (state.batteryTempC > 0f) "%.1f °C".format(state.batteryTempC)    else "—"
                "accel_mag"      -> "|Accel|"    to if (state.accelMag    > 0f)  "%.3f m/s²".format(state.accelMag)      else "—"
                "mag_ut"         -> "|Mag|"      to if (state.magMag      > 0f)  "%.1f µT".format(state.magMag)          else "—"
                "light_lux"      -> "Light"      to if (state.lightLux   >= 0f)  "%.0f lux".format(state.lightLux)       else "—"
                "humidity_pct"   -> "Humidity"   to if (state.humidityPct > 0f)  "%.0f%%".format(state.humidityPct)      else "—"
                "ambient_temp_c" -> "Ambient T"  to if (state.ambientTempC != 0f) "%.1f °C".format(state.ambientTempC)   else "—"
                "gps_acc_m"      -> "GPS Acc"    to if (state.gpsAccM    > 0f)   "±${state.gpsAccM.toInt()} m"           else "—"
                else             -> key          to "—"
            }
            TRow(label, value, GibberAmber)
        }
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
// Tab 5 — GPS Track Logger
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun GpsLoggerTab(
    state:    TricorderUiState,
    onStart:  () -> Unit,
    onStop:   () -> Unit,
    onExport: () -> String,
) {
    val clipboard = LocalClipboardManager.current
    val elapsedMs = if (state.gpsTrackRecording && state.gpsTrackStartMs > 0L) {
        System.currentTimeMillis() - state.gpsTrackStartMs
    } else 0L

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        // Status / control card
        val recColor = if (state.gpsTrackRecording) GibberRed else GibberGreen
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors   = CardDefaults.cardColors(containerColor = recColor.copy(alpha = 0.08f)),
        ) {
            Column(modifier = Modifier.padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    if (state.gpsTrackRecording) "🔴 RECORDING TRACK" else "⏹ STOPPED",
                    style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = recColor,
                )
                if (state.gpsTrackRecording) {
                    Spacer(Modifier.height(4.dp))
                    Text(
                        "${state.gpsTrackPoints.size} pts  •  %.1f m  •  %d s".format(
                            state.gpsTrackDistanceM, elapsedMs / 1000L),
                        style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim,
                    )
                } else if (state.gpsTrackPoints.isNotEmpty()) {
                    Spacer(Modifier.height(4.dp))
                    Text(
                        "${state.gpsTrackPoints.size} pts recorded  •  %.1f m total".format(state.gpsTrackDistanceM),
                        style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim,
                    )
                }
            }
        }

        // Start / Stop buttons
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            if (!state.gpsTrackRecording) {
                Button(onClick = onStart, modifier = Modifier.weight(1f)) { Text("▶ Start Track") }
            } else {
                Button(
                    onClick = onStop,
                    colors  = ButtonDefaults.buttonColors(containerColor = GibberRed),
                    modifier = Modifier.weight(1f),
                ) { Text("⏹ Stop") }
            }
            OutlinedButton(
                onClick  = { clipboard.setText(AnnotatedString(onExport())) },
                enabled  = state.gpsTrackPoints.isNotEmpty(),
                modifier = Modifier.weight(1f),
            ) { Text("📤 Copy CSV") }
        }

        // Map canvas — normalised lat/lon path
        if (state.gpsTrackPoints.size >= 2) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
            ) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text("Track Map  (${state.gpsTrackPoints.size} pts)",
                        style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim)
                    Spacer(Modifier.height(8.dp))
                    Canvas(
                        modifier = Modifier.fillMaxWidth().height(220.dp),
                    ) {
                        val pts   = state.gpsTrackPoints
                        val lats  = pts.map { it.first.toFloat() }
                        val lons  = pts.map { it.second.toFloat() }
                        val minLat = lats.min(); val maxLat = lats.max()
                        val minLon = lons.min(); val maxLon = lons.max()
                        val latRange = (maxLat - minLat).coerceAtLeast(1e-5f)
                        val lonRange = (maxLon - minLon).coerceAtLeast(1e-5f)
                        val pad = 16f
                        val w = size.width - 2 * pad; val h = size.height - 2 * pad
                        fun toX(lon: Float) = pad + (lon - minLon) / lonRange * w
                        fun toY(lat: Float) = pad + (1f - (lat - minLat) / latRange) * h
                        // Draw path
                        for (i in 1 until pts.size) {
                            val x0 = toX(lons[i - 1]); val y0 = toY(lats[i - 1])
                            val x1 = toX(lons[i]);     val y1 = toY(lats[i])
                            drawLine(color = GibberBlue, start = Offset(x0, y0),
                                end = Offset(x1, y1), strokeWidth = 3f)
                        }
                        // Start marker (green)
                        drawCircle(color = GibberGreen, radius = 7f,
                            center = Offset(toX(lons.first()), toY(lats.first())))
                        // End / current marker (red or amber)
                        val tailColor = if (state.gpsTrackRecording) GibberAmber else GibberRed
                        drawCircle(color = tailColor, radius = 7f,
                            center = Offset(toX(lons.last()), toY(lats.last())))
                    }
                }
            }
        } else if (state.gpsTrackRecording) {
            Card(modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = SurfaceDark)) {
                Column(modifier = Modifier.padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("⏳ Waiting for GPS fix…", style = MaterialTheme.typography.bodyMedium, color = OnSurfaceDim)
                    Spacer(Modifier.height(8.dp))
                    LinearProgressIndicator(modifier = Modifier.fillMaxWidth())
                }
            }
        } else {
            Card(modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = SurfaceDark)) {
                Text(
                    "Tap ▶ Start Track to begin recording.\nMove around to build the path.",
                    style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim,
                    modifier = Modifier.padding(16.dp),
                )
            }
        }

        // Stats card
        if (state.gpsTrackPoints.isNotEmpty()) {
            SensorCard(title = "📊 Track Stats", field = "GPS track metrics", color = GibberBlue) {
                TRow("Points",    "${state.gpsTrackPoints.size}",                              GibberBlue)
                TRow("Distance",  "%.1f m  (%.3f km)".format(state.gpsTrackDistanceM, state.gpsTrackDistanceM / 1000f), GibberBlue)
                TRow("Lat range", "%.6f → %.6f".format(
                    state.gpsTrackPoints.minOf { it.first },
                    state.gpsTrackPoints.maxOf { it.first }), GibberBlue)
                TRow("Lon range", "%.6f → %.6f".format(
                    state.gpsTrackPoints.minOf { it.second },
                    state.gpsTrackPoints.maxOf { it.second }), GibberBlue)
                if (state.gpsTrackStartMs > 0L && !state.gpsTrackRecording && state.gpsTrackEndMs > state.gpsTrackStartMs) {
                    val durSec = (state.gpsTrackEndMs - state.gpsTrackStartMs) / 1000L
                    TRow("Duration", "${durSec / 60} min ${durSec % 60} s", GibberBlue)
                }
            }
        }

        Text(
            "Export: CSV contains lat,lon pairs.  Import into Google Maps, QGIS, or any GPX viewer.",
            style = MaterialTheme.typography.labelSmall, color = OnSurfaceDim,
        )
        Spacer(Modifier.height(24.dp))
    }
}
