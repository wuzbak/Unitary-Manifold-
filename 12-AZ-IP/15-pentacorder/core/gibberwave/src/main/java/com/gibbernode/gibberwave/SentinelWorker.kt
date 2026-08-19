package com.gibbernode.gibberwave

import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.BatteryManager
import android.util.Log
import androidx.hilt.work.HiltWorker
import androidx.work.CoroutineWorker
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.WorkerParameters
import dagger.assisted.Assisted
import dagger.assisted.AssistedInject
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.withContext
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import kotlin.math.abs
import java.util.concurrent.TimeUnit

private const val TAG           = "GibberNode/Sentinel"
private const val WORK_NAME     = "sentinel_watchdog"
private const val POLL_MINUTES  = 5L

// Anomaly thresholds (calibrated from sentinel_watchdog.py defaults)
private const val CPU_HOT_C     = 45f
private const val BAT_HOT_C     = 40f
private const val BAT_LOW_PCT   = 15
private const val PROCESS_SIGMA = 3.0   // k = 3σ for process-bleed detection

/**
 * SentinelWorker
 *
 * WorkManager periodic worker that polls device health metrics and emits
 * [CommonToken]s to [UPBHubService.qSystem] when anomalies are detected.
 *
 * Replaces sentinel_watchdog.py for on-device (non-ADB) operation.
 * Runs every [POLL_MINUTES] minutes.  WorkManager survives Doze mode.
 *
 * Metrics collected via standard Android APIs (no root required):
 *   - Battery % and temperature    → BatteryManager
 *   - CPU temperature              → /sys/class/thermal/thermal_zone* (best-effort)
 *   - Storage free                 → StatFs on /data
 *
 * Anomaly codes (match sentinel_watchdog.py):
 *   THERMAL_THROTTLE  — CPU temp > 45 °C
 *   BATTERY_HOT       — Battery temp > 40 °C
 *   BATTERY_LOW       — Battery % ≤ 15 %
 *   STORAGE_LOW       — Internal free storage < 500 MB
 */
@HiltWorker
class SentinelWorker @AssistedInject constructor(
    @Assisted private val context: Context,
    @Assisted workerParams: WorkerParameters,
) : CoroutineWorker(context, workerParams) {

    // Rolling baseline for anomaly detection (populated across Worker instances via
    // the companion object — Workers are short-lived but the companion survives).
    private val batteryPctHistory = Companion.batteryHistory
    private val cpuTempHistory    = Companion.cpuHistory

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        try {
            val snapshot = collectSnapshot()
            val anomalies = detectAnomalies(snapshot)
            writeLog(snapshot, anomalies)
            emitTokens(snapshot, anomalies)
            Result.success()
        } catch (e: Exception) {
            Log.e(TAG, "SentinelWorker failed", e)
            Result.retry()
        }
    }

    // ── Metric collection ─────────────────────────────────────────────────────

    private fun collectSnapshot(): SentinelSnapshot {
        val bm = context.getSystemService(Context.BATTERY_SERVICE) as BatteryManager

        val batPct  = bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
        val batTempC = (context.registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
            ?.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, 0) ?: 0) / 10f
        val cpuTempC = readCpuTemp()

        val dataDir  = context.filesDir
        val freeBytes = dataDir.freeSpace
        val freeMb    = freeBytes / (1024L * 1024L)

        return SentinelSnapshot(
            timestamp  = System.currentTimeMillis(),
            batPct     = batPct,
            batTempC   = batTempC,
            cpuTempC   = cpuTempC,
            freeStorageMb = freeMb,
        )
    }

    /**
     * Read CPU temperature from sysfs thermal zones.
     * Returns the maximum reading across all zones, or -1f if unavailable.
     * This path exists on BV9900 Pro (MediaTek MT6779 / Helio P90).
     */
    private fun readCpuTemp(): Float {
        return try {
            val thermalDir = File("/sys/class/thermal")
            val zones = thermalDir.listFiles { f -> f.name.startsWith("thermal_zone") }
                ?: return -1f
            var maxTemp = Float.MIN_VALUE
            for (zone in zones) {
                val typeFile = File(zone, "type")
                val tempFile = File(zone, "temp")
                if (!tempFile.canRead()) continue
                val type = typeFile.readText().trim()
                // Focus on CPU/SoC zones; skip battery/charger zones
                if (type.contains("cpu", ignoreCase = true) ||
                    type.contains("soc", ignoreCase = true) ||
                    type.contains("mtk", ignoreCase = true)) {
                    val raw = tempFile.readText().trim().toIntOrNull() ?: continue
                    // Kernel reports millidegrees; divide by 1000
                    val tempC = raw / 1000f
                    if (tempC > maxTemp) maxTemp = tempC
                }
            }
            if (maxTemp == Float.MIN_VALUE) -1f else maxTemp
        } catch (e: Exception) {
            Log.d(TAG, "readCpuTemp: sysfs unavailable (${e.message})")
            -1f
        }
    }

    // ── Anomaly detection ─────────────────────────────────────────────────────

    private fun detectAnomalies(s: SentinelSnapshot): List<String> {
        val anomalies = mutableListOf<String>()

        if (s.cpuTempC  > CPU_HOT_C)  anomalies += "THERMAL_THROTTLE"
        if (s.batTempC  > BAT_HOT_C)  anomalies += "BATTERY_HOT"
        if (s.batPct    <= BAT_LOW_PCT && s.batPct >= 0) anomalies += "BATTERY_LOW"
        if (s.freeStorageMb in 0L..500L)  anomalies += "STORAGE_LOW"

        // Rolling-baseline battery anomaly (k = 3σ deviation from recent mean)
        batteryPctHistory.add(s.batPct.toFloat())
        if (batteryPctHistory.size > BASELINE_WINDOW) batteryPctHistory.removeAt(0)
        if (batteryPctHistory.size >= 3) {
            val mean = batteryPctHistory.average().toFloat()
            val sigma = stddev(batteryPctHistory)
            if (abs(s.batPct - mean) > PROCESS_SIGMA * sigma && sigma > 1.0) {
                anomalies += "BATTERY_SPIKE"
            }
        }

        return anomalies
    }

    private fun stddev(values: List<Float>): Double {
        val mean = values.average()
        return Math.sqrt(values.sumOf { (it - mean) * (it - mean) } / values.size)
    }

    // ── Logging ───────────────────────────────────────────────────────────────

    private fun writeLog(s: SentinelSnapshot, anomalies: List<String>) {
        try {
            val dateStr = SimpleDateFormat("yyyyMMdd", Locale.US).format(Date(s.timestamp))
            val logDir  = File(context.filesDir, "sessions")
            logDir.mkdirs()
            val logFile = File(logDir, "sentinel_$dateStr.jsonl")

            val intentStr = if (anomalies.isEmpty()) "AUTO:POLL"
                            else "AUTO:${anomalies.joinToString("+")}"
            val line = """{"ts":${s.timestamp},"bat_pct":${s.batPct},"bat_temp_c":${s.batTempC},"cpu_temp_c":${s.cpuTempC},"free_storage_mb":${s.freeStorageMb},"anomalies":${anomalies.map { "\"$it\"" }},"intent":"$intentStr"}"""

            logFile.appendText(line + "\n")
        } catch (e: Exception) {
            Log.w(TAG, "writeLog failed", e)
        }
    }

    // ── Token emission ────────────────────────────────────────────────────────

    private fun emitTokens(s: SentinelSnapshot, anomalies: List<String>) {
        // We need the UPBHubService.  Since we're in a Worker, we use the
        // application's Hilt component to get the hub reference.
        // For now we publish via a shared in-memory bus (see SentinelBus).
        val intentStr = if (anomalies.isEmpty()) "AUTO:POLL"
                        else "AUTO:${anomalies.joinToString("+")}"
        val payload = PayloadBuilder.sys(
            deviceId     = "BV9900",
            cpuTempC     = s.cpuTempC,
            batPct       = s.batPct,
            anomalyCount = anomalies.size,
            intent       = intentStr,
        )
        val token = CommonToken(
            source  = SourceProtocol.SYSTEM,
            intent  = if (anomalies.isNotEmpty()) IntentTag.ALERT else IntentTag.TELEMETRY,
            payload = payload,
        )
        SentinelBus.emit(token)
        if (anomalies.isNotEmpty()) {
            Log.w(TAG, "Anomalies detected: ${anomalies.joinToString()} — token emitted")
        }
    }

    // ── Data classes ──────────────────────────────────────────────────────────

    data class SentinelSnapshot(
        val timestamp: Long,
        val batPct: Int,
        val batTempC: Float,
        val cpuTempC: Float,
        val freeStorageMb: Long,
    )

    companion object {
        private const val BASELINE_WINDOW = 12  // ~1 hour at 5-min polling

        // In-process rolling baselines shared across Worker instances
        internal val batteryHistory = mutableListOf<Float>()
        internal val cpuHistory     = mutableListOf<Float>()

        /** Schedule the periodic Sentinel worker via WorkManager. */
        fun schedule(context: Context) {
            val request = PeriodicWorkRequestBuilder<SentinelWorker>(
                POLL_MINUTES, TimeUnit.MINUTES,
            ).build()

            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                WORK_NAME,
                ExistingPeriodicWorkPolicy.KEEP,
                request,
            )
            Log.i(TAG, "SentinelWorker scheduled every ${POLL_MINUTES} min")
        }

        /** Cancel the scheduled Sentinel work (e.g. on user request). */
        fun cancel(context: Context) {
            WorkManager.getInstance(context).cancelUniqueWork(WORK_NAME)
            Log.i(TAG, "SentinelWorker cancelled")
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────

/**
 * SentinelBus
 *
 * Lightweight in-process event bus for Worker → Service token delivery.
 * Workers can't inject Services directly; this shared SharedFlow bridges them.
 * The UPBHubService collects from [tokens] and forwards to its Q_SYSTEM channel.
 */
object SentinelBus {
    private val _tokens = MutableSharedFlow<CommonToken>(
        extraBufferCapacity = 64,
        replay = 0,
    )
    val tokens: SharedFlow<CommonToken> = _tokens.asSharedFlow()

    fun emit(token: CommonToken) { _tokens.tryEmit(token) }
}
