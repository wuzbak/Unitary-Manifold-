package com.gibbernode.feature.labs

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.gibbernode.ui.GibberAmber
import com.gibbernode.ui.GibberBlue
import com.gibbernode.ui.GibberGreen
import com.gibbernode.ui.GibberRed
import com.gibbernode.ui.OnSurfaceDim
import com.gibbernode.ui.SurfaceDark

/**
 * LabsScreen — 🔬 Sensor Suites Launcher
 *
 * A 2-column grid of feature suite cards.  Each card navigates to its
 * dedicated route.  This screen replaces the "Audit" bottom-nav tab, giving
 * all 15 Pentacorder suites a discoverable home without exceeding 6 top-level
 * tabs.
 *
 * Navigation: caller passes an [onNavigate] lambda keyed by route string.
 */
@Composable
fun LabsScreen(onNavigate: (String) -> Unit) {
    Column(modifier = Modifier.fillMaxSize()) {
        // Header
        Column(modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp)) {
            Text("🔬 Sensor Labs", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
            Text("Tap a suite to open it", style = MaterialTheme.typography.bodySmall, color = OnSurfaceDim)
        }

        LazyVerticalGrid(
            columns             = GridCells.Fixed(2),
            contentPadding      = PaddingValues(horizontal = 12.dp, vertical = 4.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
            modifier            = Modifier.weight(1f),
        ) {
            items(SUITE_CARDS) { card ->
                SuiteCard(card, onClick = { onNavigate(card.route) })
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Suite cards
// ─────────────────────────────────────────────────────────────────────────────

private data class SuiteCardData(
    val emoji:    String,
    val title:    String,
    val subtitle: String,
    val route:    String,
    val priority: Int,   // lower = shown first
    val accentColor: Color = GibberBlue,
)

private val SUITE_CARDS = listOf(
    SuiteCardData("🖊️", "S Pen",        "Gestures · Stroke Lab · Air Control", "suite/spen",        1, GibberAmber),
    SuiteCardData("🩺", "Health Lab",   "rPPG HR · Tremor · Skin Screen",      "suite/medical_ext", 2, GibberRed),
    SuiteCardData("🧲", "EMF Lab",      "Stud Finder · Sleep Check · Dirty ⚡","suite/emf",         3, GibberAmber),
    SuiteCardData("🎵", "Acoustic",     "Alert Monitor · dB Meter · Oscilloscope","suite/acoustic",  4, GibberBlue),
    SuiteCardData("🌡️", "Enviro",      "Weather · Indoor Nav · Light Lab",     "suite/enviro",      5, GibberGreen),
    SuiteCardData("🏗️", "Contractor",  "Wall Scanner · Level · Tap Test",      "suite/contractor",  6, GibberAmber),
    SuiteCardData("📡", "UWB Spatial",  "Ranging · Room Map · Point & Control","suite/uwb",         7, GibberBlue),
    SuiteCardData("🔭", "Citizen Sci.", "Radiation · G-Force · Oscillation",   "suite/science",     8, GibberGreen),
    SuiteCardData("🔬", "Optical Physics","NLOS · NIR · Motion Mag · Night Vision","suite/optics",  9, GibberBlue),
    SuiteCardData("🌐", "Sensor Status","All hardware sensors · live readings", "suite/sensors",    10, GibberGreen),
    SuiteCardData("📼", "Data Logger",  "Record all sensors · CSV export",      "suite/logger",     11, GibberRed),
    SuiteCardData("📋", "Audit Log",    "Event log & broadcast history",        "audit",            12, GibberAmber),
    // ── A12 Science Probe Screens ────────────────────────────────────────────
    SuiteCardData("🌌", "Manifold Probe","Sensor→Ψ(t) KK field evolution · J^μ_inf","suite/manifold", 13, GibberBlue),
    SuiteCardData("🔬", "Photonic Probe","TRNG · Flicker detect · Hot-pixel scan","suite/photonic",  14, GibberGreen),
    SuiteCardData("🏗️", "Surface Scan", "Tap material classify · Life-sign FFT","suite/surface",   15, GibberAmber),
).sortedBy { it.priority }

@Composable
private fun SuiteCard(card: SuiteCardData, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .aspectRatio(1f)
            .clickable(onClick = onClick),
        colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            // Accent colour bar at top
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(4.dp)
                    .background(card.accentColor),
            )
            Column(
                modifier            = Modifier.fillMaxSize().padding(14.dp),
                verticalArrangement = Arrangement.SpaceBetween,
            ) {
                Text(card.emoji, fontSize = 30.sp)
                Column {
                    Text(
                        card.title,
                        style      = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold,
                        color      = card.accentColor,
                        maxLines   = 1,
                    )
                    Spacer(Modifier.height(4.dp))
                    Text(
                        card.subtitle,
                        style    = MaterialTheme.typography.labelSmall,
                        color    = OnSurfaceDim,
                        maxLines = 2,
                        lineHeight = 15.sp,
                    )
                }
            }
        }
    }
}
