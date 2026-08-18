package com.gibbernode.audio

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Binder
import android.os.Build
import android.os.IBinder
import android.util.Log
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

private const val TAG              = "GibberNode/AudioLoop"
private const val NOTIFICATION_ID  = 1001
private const val CHANNEL_ID       = "gibbernode_audio_channel"

/**
 * AudioLoopService
 *
 * A Foreground Service that keeps the microphone open for continuous ggwave
 * decoding, even when the GibberNode UI is in the background.
 *
 * Android 12+ requires FOREGROUND_SERVICE_TYPE_MICROPHONE to hold a mic in a
 * foreground service; the manifest already declares this type on this service.
 *
 * The service exposes a [LocalBinder] so the UI can bind and access the
 * decoded payload [SharedFlow] and call [playPayload] directly.
 *
 * Lifecycle:
 *   startForegroundService(intent)        → onCreate → onStartCommand → starts mic
 *   stopService / stopSelf                → onDestroy → releases AudioEngine
 *   bindService(…, LocalBinder)           → UI gets live access to payloads
 */
@AndroidEntryPoint
class AudioLoopService : Service() {

    @Inject lateinit var audioEngine: AudioEngine

    private val serviceScope = CoroutineScope(Dispatchers.Main + SupervisorJob())

    // ── Binder ────────────────────────────────────────────────────────────────

    inner class LocalBinder : Binder() {
        /** Hot flow of decoded Gibberlink payload strings. */
        val decodedPayloads: SharedFlow<String> get() = audioEngine.decodedPayloads

        /** Encode and play a message. */
        suspend fun playPayload(
            payload: String,
            protocol: TxProtocol = TxProtocol.AUDIBLE_NORMAL,
            volume: Int = 50,
        ) = audioEngine.play(payload, protocol, volume)

        /** Whether the capture loop is currently active. */
        val isListening: Boolean get() = audioEngine.isListening
    }

    private val binder = LocalBinder()

    override fun onBind(intent: Intent?): IBinder = binder

    // ── Lifecycle ─────────────────────────────────────────────────────────────

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        Log.i(TAG, "Service created")
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_STOP -> {
                Log.i(TAG, "Stop requested via intent action")
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
                return START_NOT_STICKY
            }
        }

        val notification = buildNotification()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE,
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }

        audioEngine.startListening()
        Log.i(TAG, "Foreground service started — mic open")

        return START_STICKY
    }

    override fun onDestroy() {
        audioEngine.stopListening()
        serviceScope.launch {
            audioEngine.release()
        }
        serviceScope.cancel()
        Log.i(TAG, "Service destroyed")
        super.onDestroy()
    }

    // ── Notification ──────────────────────────────────────────────────────────

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Gibberlink Audio",
                NotificationManager.IMPORTANCE_LOW,  // silent, non-intrusive
            ).apply {
                description = "Keeps the microphone open for Gibberlink acoustic decoding"
                setShowBadge(false)
            }
            getSystemService(NotificationManager::class.java)
                .createNotificationChannel(channel)
        }
    }

    @Suppress("DEPRECATION")
    private fun buildNotification(): Notification {
        // Intent to stop the service from the notification action
        val stopIntent = Intent(this, AudioLoopService::class.java).apply {
            action = ACTION_STOP
        }
        val stopPendingIntent = PendingIntent.getService(
            this, 0, stopIntent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT,
        )

        // Tap the notification to open the app
        val launchIntent = packageManager.getLaunchIntentForPackage(packageName)
        val launchPendingIntent = PendingIntent.getActivity(
            this, 0, launchIntent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT,
        )

        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            Notification.Builder(this, CHANNEL_ID)
                .setContentTitle("GibberNode")
                .setContentText("Listening for Gibberlink transmissions")
                .setSmallIcon(android.R.drawable.ic_btn_speak_now)
                .setContentIntent(launchPendingIntent)
                .setOngoing(true)
                .addAction(
                    Notification.Action.Builder(
                        android.R.drawable.ic_delete,
                        "Stop",
                        stopPendingIntent,
                    ).build()
                )
                .build()
        } else {
            @Suppress("DEPRECATION")
            Notification.Builder(this)
                .setContentTitle("GibberNode")
                .setContentText("Listening for Gibberlink transmissions")
                .setSmallIcon(android.R.drawable.ic_btn_speak_now)
                .setContentIntent(launchPendingIntent)
                .setOngoing(true)
                .build()
        }
    }

    companion object {
        const val ACTION_STOP = "com.gibbernode.audio.ACTION_STOP"
    }
}
