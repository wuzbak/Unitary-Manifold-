package com.gibbernode.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.gibbernode.feature.acoustic.AcousticScreen
import com.gibbernode.feature.audit.AuditScreen
import com.gibbernode.feature.contractor.ContractorScreen
import com.gibbernode.feature.dashboard.CalibrationWizardScreen
import com.gibbernode.feature.dashboard.DashboardScreen
import com.gibbernode.feature.emf.EMFScreen
import com.gibbernode.feature.enviro.EnviroScreen
import com.gibbernode.feature.labs.DataLoggerScreen
import com.gibbernode.feature.labs.LabsScreen
import com.gibbernode.feature.labs.ManifoldProbeScreen
import com.gibbernode.feature.labs.PhotonicProbeScreen
import com.gibbernode.feature.labs.SensorStatusScreen
import com.gibbernode.feature.labs.SurfaceScanScreen
import com.gibbernode.feature.medical.MedicalScreen
import com.gibbernode.feature.mode.ModeScreen
import com.gibbernode.feature.optics.OpticsScreen
import com.gibbernode.feature.registry.RegistryScreen
import com.gibbernode.feature.science.ScienceScreen
import com.gibbernode.feature.spen.SPenScreen
import com.gibbernode.feature.translate.TranslateScreen
import com.gibbernode.feature.tricorder.TricorderScreen
import com.gibbernode.feature.uwb.UWBScreen

/**
 * AppNavigation
 *
 * Declares the NavHost with destinations for all six bottom-nav tabs and
 * all fifteen Pentacorder sensor-suite routes (reachable via the Labs tab).
 *
 * Bottom-nav tabs (6):
 *  1. Dashboard  — sentinel mood, mode ring, SOS, Ollama analysis
 *  2. Medical    — NEWS2, φ-homeostasis, first-aid protocols, first-responder
 *  3. Transmit   — GREEN/RED/BLUE/AMBER mode, encode/broadcast, translator
 *  4. Tricorder  — all S24 Ultra sensors + manifold fields + camera launchers
 *  5. Translate  — language bridge, field intel, protocol bridge, Pentad
 *  6. Labs       — 15-suite launcher grid
 *
 * Suite routes (pushed from Labs grid):
 *  suite/spen        — S Pen Command Center
 *  suite/emf         — EMF & Structural Lab
 *  suite/enviro      — Environmental Science Hub
 *  suite/contractor  — Precision Contractor Suite
 *  suite/uwb         — UWB Spatial Lab
 *  suite/acoustic    — Acoustic Intelligence
 *  suite/science     — Citizen Science Hub
 *  suite/optics      — Optical Physics Suite (7-tab: NLOS/Hyper/MotionMag/VisMic/SynthApt/Night/NIR)
 *  suite/medical_ext — Medical extended (Neuro + Skin sub-tabs; opens MedicalScreen)
 *  audit             — Audit log (still accessible from Labs grid)
 */
@Composable
fun AppNavigation(
    navController: NavHostController,
    startDestination: String = BottomNavItem.Dashboard.route,
    modifier: androidx.compose.ui.Modifier = androidx.compose.ui.Modifier,
) {
    NavHost(
        navController    = navController,
        startDestination = startDestination,
        modifier         = modifier,
    ) {
        // ── Bottom-nav tabs ───────────────────────────────────────────────────

        composable(BottomNavItem.Dashboard.route) {
            DashboardScreen(
                onNavigateToMode = { navController.navigate(BottomNavItem.Mode.route) },
            )
        }

        composable(BottomNavItem.Medical.route) {
            MedicalScreen(
                onActivateRedMode = { navController.navigate(BottomNavItem.Mode.route) },
            )
        }

        composable(BottomNavItem.Mode.route) {
            ModeScreen()
        }

        composable(BottomNavItem.Tricorder.route) {
            TricorderScreen()
        }

        composable(BottomNavItem.Translate.route) {
            TranslateScreen()
        }

        composable(BottomNavItem.Labs.route) {
            LabsScreen(onNavigate = { route -> navController.navigate(route) })
        }

        // ── Suite routes (pushed from Labs grid) ──────────────────────────────

        composable("suite/spen") {
            SPenScreen()
        }

        composable("suite/emf") {
            EMFScreen()
        }

        composable("suite/enviro") {
            EnviroScreen()
        }

        composable("suite/contractor") {
            ContractorScreen()
        }

        composable("suite/uwb") {
            UWBScreen()
        }

        composable("suite/acoustic") {
            AcousticScreen()
        }

        composable("suite/science") {
            ScienceScreen()
        }

        composable("suite/optics") {
            OpticsScreen()
        }

        // Medical extended: re-uses MedicalScreen — Labs card opens it directly
        composable("suite/medical_ext") {
            MedicalScreen(
                onActivateRedMode = { navController.navigate(BottomNavItem.Mode.route) },
            )
        }

        // ── Utility routes ─────────────────────────────────────────────────────

        // Audit log: still accessible from Labs grid
        composable("audit") {
            AuditScreen()
        }

        composable("registry") {
            RegistryScreen()
        }

        composable("calibration") {
            CalibrationWizardScreen(
                onComplete = { navController.popBackStack() }
            )
        }

        // ── New Labs routes ─────────────────────────────────────────────────────

        composable("suite/sensors") {
            SensorStatusScreen()
        }

        composable("suite/logger") {
            DataLoggerScreen()
        }

        // ── A12 Science Probe routes ─────────────────────────────────────────

        composable("suite/manifold") {
            ManifoldProbeScreen()
        }

        composable("suite/photonic") {
            PhotonicProbeScreen()
        }

        composable("suite/surface") {
            SurfaceScanScreen()
        }
    }
}
