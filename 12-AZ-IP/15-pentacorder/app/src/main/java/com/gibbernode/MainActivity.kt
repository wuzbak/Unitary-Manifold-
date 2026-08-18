package com.gibbernode

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.core.content.ContextCompat
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.gibbernode.audio.AudioLoopService
import com.gibbernode.gibberwave.CalibrationStore
import com.gibbernode.gibberwave.SentinelWorker
import com.gibbernode.navigation.AppNavigation
import com.gibbernode.navigation.BottomNavItem
import com.gibbernode.ui.GibberAmber
import com.gibbernode.ui.gibberColorScheme
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * MainActivity
 *
 * Single-Activity host for the entire Unitary Pentacorder Compose UI.
 * Responsibilities:
 *  1. Request runtime permissions (RECORD_AUDIO, ACCESS_FINE_LOCATION, etc.).
 *  2. Start the AudioLoopService foreground service.
 *  3. Schedule the SentinelWorker periodic WorkManager job.
 *  4. Host the NavController and bottom navigation bar.
 *  5. On first launch (CalibrationStore.isCalibrated == false), navigate
 *     automatically to the CalibrationWizard before showing the dashboard.
 *  6. Host the persistent Pentacorder Assistant FAB + ModalBottomSheet.
 */
@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    @Inject
    lateinit var calibrationStore: CalibrationStore

    // ── Permission request ─────────────────────────────────────────────────

    private val permissionsToRequest = buildList {
        add(Manifest.permission.RECORD_AUDIO)
        add(Manifest.permission.ACCESS_FINE_LOCATION)
        add(Manifest.permission.CAMERA)
        add(Manifest.permission.BODY_SENSORS)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            add(Manifest.permission.ACTIVITY_RECOGNITION)
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            add(Manifest.permission.READ_MEDIA_AUDIO)
            add(Manifest.permission.NEARBY_WIFI_DEVICES)
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            add(Manifest.permission.POST_NOTIFICATIONS)
        }
    }.toTypedArray()

    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { results ->
        if (results[Manifest.permission.RECORD_AUDIO] == true) {
            startAudioService()
        }
    }

    // ── Lifecycle ──────────────────────────────────────────────────────────

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        SentinelWorker.schedule(this)

        if (hasRequiredPermissions()) {
            startAudioService()
        } else {
            permissionLauncher.launch(permissionsToRequest)
        }

        setContent {
            PentacorderTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color    = MaterialTheme.colorScheme.background,
                ) {
                    PentacorderApp()
                }
            }
        }
    }

    // ── Root composable ────────────────────────────────────────────────────

    @OptIn(androidx.compose.material3.ExperimentalMaterial3Api::class)
    @Composable
    private fun PentacorderApp() {
        val navController: NavHostController = rememberNavController()
        val assistantVm: AssistantViewModel  = hiltViewModel()
        val assistantState by assistantVm.uiState.collectAsState()

        var showAssistant by remember { mutableStateOf(false) }
        val sheetState    = rememberModalBottomSheetState(skipPartiallyExpanded = true)
        val scope         = rememberCoroutineScope()

        // Wire navigation callback so the assistant can drive tab switches
        assistantVm.onNavigate = { tab ->
            val route = BottomNavItem.all.firstOrNull { it.route == tab }?.route ?: tab
            navController.navigate(route) {
                popUpTo(navController.graph.startDestinationId) { saveState = true }
                launchSingleTop = true
                restoreState    = true
            }
        }

        // On first launch navigate to calibration wizard
        LaunchedEffect(Unit) {
            val calibrated = calibrationStore.isCalibrated.first()
            if (!calibrated) navController.navigate("calibration") { launchSingleTop = true }
        }

        Scaffold(
            bottomBar = { BottomNavBar(navController) },
            floatingActionButton = {
                // Persistent assistant FAB — always visible across all tabs
                FloatingActionButton(
                    onClick           = { showAssistant = true },
                    containerColor    = GibberAmber,
                    contentColor      = androidx.compose.ui.graphics.Color.Black,
                ) {
                    Icon(Icons.Filled.AutoAwesome, contentDescription = "Pentacorder Assistant")
                }
            },
        ) { innerPadding ->
            AppNavigation(
                navController = navController,
                modifier      = Modifier.padding(innerPadding),
            )
        }

        // Assistant bottom sheet
        if (showAssistant) {
            AssistantSheet(
                vm         = assistantVm,
                state      = assistantState,
                sheetState = sheetState,
                onDismiss  = {
                    scope.launch { sheetState.hide() }.invokeOnCompletion { showAssistant = false }
                },
            )
        }
    }

    // ── Bottom Navigation Bar ──────────────────────────────────────────────

    @Composable
    private fun BottomNavBar(navController: NavHostController) {
        val backStackEntry by navController.currentBackStackEntryAsState()
        val currentRoute = backStackEntry?.destination?.route

        NavigationBar {
            BottomNavItem.all.forEach { item ->
                NavigationBarItem(
                    selected = currentRoute == item.route,
                    onClick  = {
                        if (currentRoute != item.route) {
                            navController.navigate(item.route) {
                                popUpTo(navController.graph.startDestinationId) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState    = true
                            }
                        }
                    },
                    icon  = { Icon(imageVector = item.icon, contentDescription = item.label) },
                    label = { Text(item.label) },
                )
            }
        }
    }

    // ── Service management ─────────────────────────────────────────────────

    private fun startAudioService() {
        val intent = Intent(this, AudioLoopService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
    }

    private fun hasRequiredPermissions(): Boolean =
        permissionsToRequest.all { perm ->
            ContextCompat.checkSelfPermission(this, perm) == PackageManager.PERMISSION_GRANTED
        }
}

// ── Theme wrapper ──────────────────────────────────────────────────────────────

/**
 * PentacorderTheme — Material 3 theme with Pentacorder brand palette.
 * Dynamic color disabled — Pentacorder uses its own high-contrast green/red/blue palette.
 */
@Composable
private fun PentacorderTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = gibberColorScheme(),
        typography  = MaterialTheme.typography,
        content     = content,
    )
}
