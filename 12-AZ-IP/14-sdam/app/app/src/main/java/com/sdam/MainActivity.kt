package com.sdam

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.core.content.ContextCompat
import com.sdam.audio.AcousticModemService
import com.sdam.ui.MainScreen
import com.sdam.ui.sdamColorScheme
import dagger.hilt.android.AndroidEntryPoint

/**
 * MainActivity
 *
 * Single-Activity host for the SDAM Compose UI.
 *
 * Responsibilities:
 *   1. Request RECORD_AUDIO + POST_NOTIFICATIONS permissions at runtime.
 *   2. Start [AcousticModemService] as a foreground service.
 *   3. Host [MainScreen] — the 4-tab modem interface.
 */
@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    private val permissionsToRequest = buildList {
        add(Manifest.permission.RECORD_AUDIO)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            add(Manifest.permission.POST_NOTIFICATIONS)
        }
    }.toTypedArray()

    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { results ->
        if (results[Manifest.permission.RECORD_AUDIO] == true) {
            startModemService()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        if (hasRecordPermission()) {
            startModemService()
        } else {
            permissionLauncher.launch(permissionsToRequest)
        }

        setContent {
            SdamTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color    = MaterialTheme.colorScheme.background,
                ) {
                    MainScreen()
                }
            }
        }
    }

    private fun startModemService() {
        val intent = Intent(this, AcousticModemService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
    }

    private fun hasRecordPermission(): Boolean =
        ContextCompat.checkSelfPermission(
            this, Manifest.permission.RECORD_AUDIO
        ) == PackageManager.PERMISSION_GRANTED
}

@Composable
private fun SdamTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = sdamColorScheme(),
        typography  = MaterialTheme.typography,
        content     = content,
    )
}
