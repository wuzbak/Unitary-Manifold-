package com.sdam.audio

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

private const val TAG             = "SDAM/ModemService"
private const val NOTIFICATION_ID = 2001
private const val CHANNEL_ID      = "sdam_audio_channel"

/**
 * AcousticModemService — S3: Foreground Microphone Service
 *
 * Keeps the microphone open for continuous ggwave decoding, even when the SDAM
 * UI is in the background.
 *
 * Android 12+ requires FOREGROUND_SERVICE_TYPE_MICROPHONE to hold a mic in a
 * foreground service; the manifest declares this type on this service.
 *
 * A [LocalBinder] exposes the decoded payload [SharedFlow] and [playPayload]
 * so the UI can bind and interact without restarts.
 */
@AndroidEntryPoint
class AcousticModemService : Service() {

    @Inject lateinit var audioEngine: AudioEngine

    private val serviceScope = CoroutineScope(Dispatchers.Main + SupervisorJob())

    // ── Binder ────────────────────────────────────────────────────────────────

    inner class LocalBinder : Binder() {
        /** Hot flow of decoded acoustic payload strings. */
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
        if (intent?.action == ACTION_STOP) {
            Log.i(TAG, "Stop requested via intent action")
            stopForeground(STOP_FOREGROUND_REMOVE)
            stopSelf()
            return START_NOT_STICKY
        }

        val notification = buildNotification()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }

        audioEngine.startListening()
        Log.i(TAG, "Foreground service started — mic open")
        return START_STICKY
    }

    override fun onDestroy() {
        audioEngine.stopListening()
        serviceScope.launch { audioEngine.release() }
        serviceScope.cancel()
        Log.i(TAG, "Service destroyed")
        super.onDestroy()
    }

    // ── Notification ──────────────────────────────────────────────────────────

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "SDAM Audio",
                NotificationManager.IMPORTANCE_LOW,
            ).apply {
                description = "Keeps the microphone open for SDAM acoustic decoding"
                setShowBadge(false)
            }
            getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
        }
    }

    @Suppress("DEPRECATION")
    private fun buildNotification(): Notification {
        val stopIntent = Intent(this, AcousticModemService::class.java).apply { action = ACTION_STOP }
        val stopPending = PendingIntent.getService(
            this, 0, stopIntent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT,
        )

        val launchIntent = packageManager.getLaunchIntentForPackage(packageName)
        val launchPending = PendingIntent.getActivity(
            this, 0, launchIntent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT,
        )

        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            Notification.Builder(this, CHANNEL_ID)
                .setContentTitle("SDAM Sentinel")
                .setContentText("Listening for acoustic transmissions")
                .setSmallIcon(android.R.drawable.ic_btn_speak_now)
                .setContentIntent(launchPending)
                .setOngoing(true)
                .addAction(
                    Notification.Action.Builder(
                        android.R.drawable.ic_delete, "Stop", stopPending
                    ).build()
                )
                .build()
        } else {
            @Suppress("DEPRECATION")
            Notification.Builder(this)
                .setContentTitle("SDAM Sentinel")
                .setContentText("Listening for acoustic transmissions")
                .setSmallIcon(android.R.drawable.ic_btn_speak_now)
                .setContentIntent(launchPending)
                .setOngoing(true)
                .build()
        }
    }

    companion object {
        const val ACTION_STOP = "com.sdam.audio.ACTION_STOP"
    }
}
