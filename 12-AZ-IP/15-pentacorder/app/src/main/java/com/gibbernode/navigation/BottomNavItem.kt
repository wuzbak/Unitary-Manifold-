package com.gibbernode.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.BioTech
import androidx.compose.material.icons.filled.Dashboard
import androidx.compose.material.icons.filled.LocalHospital
import androidx.compose.material.icons.filled.Radio
import androidx.compose.material.icons.filled.Science
import androidx.compose.material.icons.filled.Translate
import androidx.compose.ui.graphics.vector.ImageVector

/**
 * BottomNavItem
 *
 * Defines the five tabs of the GibberNode bottom navigation bar.
 * Each item carries a route string used by the NavHost, a display label,
 * and a Material icon.
 */
sealed class BottomNavItem(
    val route: String,
    val label: String,
    val icon: ImageVector,
) {
    /** Tab 1 — real-time health dashboard, SOS button, Sentinel mood. */
    object Dashboard : BottomNavItem(
        route = "dashboard",
        label = "Dashboard",
        icon  = Icons.Filled.Dashboard,
    )

    /** Tab 2 — Medical: vital signs, NEWS2, φ-homeostasis, first-aid protocols, first-responder. */
    object Medical : BottomNavItem(
        route = "medical",
        label = "Medical",
        icon  = Icons.Filled.LocalHospital,
    )

    /** Tab 3 — Transmit: mode selector (GREEN/RED/BLUE/AMBER), encode & broadcast, translator. */
    object Mode : BottomNavItem(
        route = "mode",
        label = "Transmit",
        icon  = Icons.Filled.Radio,
    )

    /** Tab 4 — Pentacorder: all S24 Ultra sensors mapped to manifold fields, camera launchers. */
    object Tricorder : BottomNavItem(
        route = "tricorder",
        label = "Pentacorder",
        icon  = Icons.Filled.Science,
    )

    /** Tab 5 — Pentacorder translator: language bridge, sensor intel, protocol bridge, Pentad state. */
    object Translate : BottomNavItem(
        route = "translate",
        label = "Translate",
        icon  = Icons.Filled.Translate,
    )

    /** Tab 6 — Sensor Labs: 8-suite launcher grid + audit log. */
    object Labs : BottomNavItem(
        route = "labs",
        label = "Labs",
        icon  = Icons.Filled.BioTech,
    )

    companion object {
        /**
         * Ordered list of all bottom-navigation tabs.
         * The order here determines the left-to-right layout in the bottom bar:
         *   0 Dashboard  |  1 Medical  |  2 Transmit  |  3 Tricorder  |  4 Translate  |  5 Labs
         */
        val all: List<BottomNavItem> = listOf(Dashboard, Medical, Mode, Tricorder, Translate, Labs)
    }
}
