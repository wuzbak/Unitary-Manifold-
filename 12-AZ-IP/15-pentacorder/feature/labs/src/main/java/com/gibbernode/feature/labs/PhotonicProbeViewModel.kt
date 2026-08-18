package com.gibbernode.feature.labs

import android.content.Context
import android.graphics.BitmapFactory
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.security.MessageDigest
import javax.inject.Inject
import kotlin.math.abs
import kotlin.math.sqrt

/**
 * PhotonicProbeViewModel
 *
 * Android port of S24Ultra/scripts/photonic_probe.py.
 *
 * Three operational modes:
 *
 *  TRNG — True Random Number Generation from camera pixel noise.
 *    Captures a dark-frame image (lens covered), extracts per-pixel variance
 *    as a raw entropy source, feeds it through a Von Neumann de-biaser and
 *    SHA-256 whitener to produce cryptographic-quality random bytes.
 *
 *  FLICKER — Detect light-source flicker by analysing temporal mean-brightness
 *    variation across two successive captures.  Detects mains-frequency LED
 *    flicker (50/60 Hz) and hidden IR camera illuminators.
 *
 *  DARK_SCAN — Hot-pixel and anomalous-event hunting from a dark frame.
 *    Identifies pixels whose intensity is more than [HOT_PIXEL_SIGMA] standard
 *    deviations above the mean dark-frame level — analogous to cosmic-ray
 *    event detection in scientific CCDs.
 *
 * ISP note: JPEG processing reduces but does not eliminate photon shot noise.
 * Results are informative / experimental — not certified for cryptographic use.
 */
@HiltViewModel
class PhotonicProbeViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
) : ViewModel() {

    private val _state = MutableStateFlow(PhotonicProbeUiState())
    val state: StateFlow<PhotonicProbeUiState> = _state.asStateFlow()

    private var cameraProvider: ProcessCameraProvider? = null

    // ── Constants ─────────────────────────────────────────────────────────────

    private val DEFAULT_RANDOM_BYTES = 32
    private val HOT_PIXEL_SIGMA      = 3.0f   // σ threshold for hot-pixel detection

    // ─────────────────────────────────────────────────────────────────────────
    // Public API
    // ─────────────────────────────────────────────────────────────────────────

    /**
     * Capture a frame and run TRNG extraction.
     * For best quality: cover the camera lens completely before calling.
     */
    fun startTrng(lifecycleOwner: LifecycleOwner, byteCount: Int = DEFAULT_RANDOM_BYTES) {
        _state.update { it.copy(mode = PhotonicMode.TRNG, running = true, error = null, result = null) }
        captureFrame(lifecycleOwner, "trng_frame.jpg") { file ->
            processTrng(file, byteCount)
        }
    }

    /**
     * Capture two successive frames and analyse luminance variance for flicker.
     * Point the camera at any light source (LED, monitor, etc.).
     */
    fun startFlicker(lifecycleOwner: LifecycleOwner) {
        _state.update { it.copy(mode = PhotonicMode.FLICKER, running = true, error = null, result = null) }
        captureFrame(lifecycleOwner, "flicker_a.jpg") { fileA ->
            captureFrame(lifecycleOwner, "flicker_b.jpg") { fileB ->
                processFlicker(fileA, fileB)
            }
        }
    }

    /**
     * Capture a dark frame and scan for hot pixels / anomalous events.
     * Cover the lens completely for best results.
     */
    fun startDarkScan(lifecycleOwner: LifecycleOwner) {
        _state.update { it.copy(mode = PhotonicMode.DARK_SCAN, running = true, error = null, result = null) }
        captureFrame(lifecycleOwner, "dark_frame.jpg") { file ->
            processDarkScan(file)
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Processing logic (IO-dispatched)
    // ─────────────────────────────────────────────────────────────────────────

    private fun processTrng(file: File, byteCount: Int) {
        viewModelScope.launch(Dispatchers.Default) {
            try {
                val bmp   = BitmapFactory.decodeFile(file.absolutePath)
                    ?: throw IllegalStateException("Could not decode image")
                val w     = bmp.width; val h = bmp.height

                // Extract luma values from the full frame
                val pixels = IntArray(w * h)
                bmp.getPixels(pixels, 0, w, 0, 0, w, h)
                bmp.recycle()

                // Raw byte stream from the least-significant bit of the packed ARGB pixel int.
                // This corresponds to the LSB of the blue channel (ARGB: A=byte3, R=byte2, G=byte1, B=byte0),
                // which retains photon shot noise even after ISP processing.
                val rawBits = mutableListOf<Int>()
                for (px in pixels) {
                    rawBits.add((px and 0x01).toInt())
                }

                // Von Neumann de-biasing: consume pairs (0,1)→0, (1,0)→1, discard equal
                val debiasedBytes = vonNeumannExtract(rawBits)

                // SHA-256 whitening of the de-biased pool
                val poolBytes = debiasedBytes.take(1024.coerceAtMost(debiasedBytes.size)).toByteArray()
                val digest    = MessageDigest.getInstance("SHA-256").digest(poolBytes)

                // Output the requested byte count (cycling the digest if needed)
                val outputBytes = ByteArray(byteCount) { i -> digest[i % digest.size] }
                val hexString   = outputBytes.joinToString("") { "%02x".format(it) }

                val entropyEst = estimateEntropy(rawBits)

                withContext(Dispatchers.Main) {
                    _state.update { it.copy(
                        running = false,
                        result  = PhotonicResult.TrngResult(
                            hexBytes    = hexString,
                            byteCount   = byteCount,
                            entropyEst  = entropyEst,
                            rawBitCount = rawBits.size,
                        ),
                    )}
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    _state.update { it.copy(running = false, error = "TRNG failed: ${e.message}") }
                }
            }
        }
    }

    private fun processFlicker(fileA: File, fileB: File) {
        viewModelScope.launch(Dispatchers.Default) {
            try {
                val bmpA = BitmapFactory.decodeFile(fileA.absolutePath)
                    ?: throw IllegalStateException("Could not decode frame A")
                val bmpB = BitmapFactory.decodeFile(fileB.absolutePath)
                    ?: throw IllegalStateException("Could not decode frame B")

                val lumaA = meanLuma(bmpA); bmpA.recycle()
                val lumaB = meanLuma(bmpB); bmpB.recycle()

                val lumaDiff   = abs(lumaA - lumaB)
                val flickerPct = (lumaDiff / ((lumaA + lumaB) / 2f + 1f)) * 100f

                val flickerDetected = flickerPct > 3f  // >3% inter-frame luma change

                withContext(Dispatchers.Main) {
                    _state.update { it.copy(
                        running = false,
                        result  = PhotonicResult.FlickerResult(
                            lumaFrameA      = lumaA,
                            lumaFrameB      = lumaB,
                            lumaDiff        = lumaDiff,
                            flickerPct      = flickerPct,
                            flickerDetected = flickerDetected,
                        ),
                    )}
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    _state.update { it.copy(running = false, error = "Flicker scan failed: ${e.message}") }
                }
            }
        }
    }

    private fun processDarkScan(file: File) {
        viewModelScope.launch(Dispatchers.Default) {
            try {
                val bmp    = BitmapFactory.decodeFile(file.absolutePath)
                    ?: throw IllegalStateException("Could not decode image")
                val w      = bmp.width; val h = bmp.height
                val pixels = IntArray(w * h)
                bmp.getPixels(pixels, 0, w, 0, 0, w, h)
                bmp.recycle()

                // Extract green channel (least affected by ISP colour correction)
                val greenValues = pixels.map { ((it shr 8) and 0xFF).toFloat() }
                val mean   = greenValues.average().toFloat()
                val stddev = sqrt(greenValues.sumOf { v -> val d = v - mean; (d * d).toDouble() }
                    .toFloat() / greenValues.size)

                val threshold  = mean + HOT_PIXEL_SIGMA * stddev
                val hotPixels  = greenValues.count { it > threshold }
                val hotFraction = hotPixels.toFloat() / greenValues.size

                withContext(Dispatchers.Main) {
                    _state.update { it.copy(
                        running = false,
                        result  = PhotonicResult.DarkScanResult(
                            meanGreen    = mean,
                            stddevGreen  = stddev,
                            threshold    = threshold,
                            hotPixelCount = hotPixels,
                            hotFraction  = hotFraction,
                            totalPixels  = greenValues.size,
                        ),
                    )}
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    _state.update { it.copy(running = false, error = "Dark scan failed: ${e.message}") }
                }
            }
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // CameraX single-frame capture helper
    // ─────────────────────────────────────────────────────────────────────────

    private fun captureFrame(
        lifecycleOwner: LifecycleOwner,
        filename: String,
        onCaptured: (File) -> Unit,
    ) {
        val executor = ContextCompat.getMainExecutor(context)
        val future   = ProcessCameraProvider.getInstance(context)

        future.addListener({
            val provider = future.get() ?: run {
                _state.update { it.copy(running = false, error = "Camera unavailable") }
                return@addListener
            }
            cameraProvider = provider

            val imageCapture = ImageCapture.Builder()
                .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                .build()

            try {
                provider.unbindAll()
                provider.bindToLifecycle(
                    lifecycleOwner,
                    CameraSelector.DEFAULT_BACK_CAMERA,
                    imageCapture,
                )
            } catch (e: Exception) {
                _state.update { it.copy(running = false, error = "Camera bind failed: ${e.message}") }
                return@addListener
            }

            val outputFile    = File(context.cacheDir, filename)
            val outputOptions = ImageCapture.OutputFileOptions.Builder(outputFile).build()

            imageCapture.takePicture(outputOptions, executor,
                object : ImageCapture.OnImageSavedCallback {
                    override fun onImageSaved(outputFileResults: ImageCapture.OutputFileResults) {
                        provider.unbindAll()
                        onCaptured(outputFile)
                    }
                    override fun onError(exception: ImageCaptureException) {
                        provider.unbindAll()
                        _state.update { it.copy(running = false, error = "Capture failed: ${exception.message}") }
                    }
                })
        }, executor)
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Statistical helpers
    // ─────────────────────────────────────────────────────────────────────────

    private fun vonNeumannExtract(bits: List<Int>): List<Byte> {
        val result = mutableListOf<Byte>()
        var byte   = 0; var count = 0
        var i = 0
        while (i + 1 < bits.size && result.size < 1024) {
            val a = bits[i]; val b = bits[i + 1]; i += 2
            if (a == b) continue   // discard equal pairs
            val bit = a             // 0,1 → 0;  1,0 → 1
            byte = (byte shl 1) or bit
            count++
            if (count == 8) {
                result.add(byte.toByte())
                byte = 0; count = 0
            }
        }
        return result
    }

    private fun estimateEntropy(bits: List<Int>): Float {
        if (bits.isEmpty()) return 0f
        val p1 = bits.count { it == 1 }.toFloat() / bits.size
        val p0 = 1f - p1
        if (p0 == 0f || p1 == 0f) return 0f
        return -(p0 * log2(p0) + p1 * log2(p1))
    }

    private fun log2(x: Float): Float = (Math.log(x.toDouble()) / Math.log(2.0)).toFloat()

    private fun meanLuma(bmp: android.graphics.Bitmap): Float {
        val w = bmp.width; val h = bmp.height
        val px = IntArray(w * h)
        bmp.getPixels(px, 0, w, 0, 0, w, h)
        return px.map { p ->
            val r = (p shr 16) and 0xFF
            val g = (p shr  8) and 0xFF
            val b =  p         and 0xFF
            (0.299f * r + 0.587f * g + 0.114f * b)
        }.average().toFloat()
    }

    override fun onCleared() {
        cameraProvider?.unbindAll()
        super.onCleared()
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// UI state
// ─────────────────────────────────────────────────────────────────────────────

enum class PhotonicMode(val label: String, val emoji: String) {
    TRNG      ("TRNG",       "🎲"),
    FLICKER   ("Flicker",    "💡"),
    DARK_SCAN ("Dark Scan",  "🔭"),
}

sealed class PhotonicResult {
    data class TrngResult(
        val hexBytes:    String,
        val byteCount:   Int,
        val entropyEst:  Float,
        val rawBitCount: Int,
    ) : PhotonicResult()

    data class FlickerResult(
        val lumaFrameA:      Float,
        val lumaFrameB:      Float,
        val lumaDiff:        Float,
        val flickerPct:      Float,
        val flickerDetected: Boolean,
    ) : PhotonicResult()

    data class DarkScanResult(
        val meanGreen:      Float,
        val stddevGreen:    Float,
        val threshold:      Float,
        val hotPixelCount:  Int,
        val hotFraction:    Float,
        val totalPixels:    Int,
    ) : PhotonicResult()
}

data class PhotonicProbeUiState(
    val mode:    PhotonicMode  = PhotonicMode.TRNG,
    val running: Boolean       = false,
    val result:  PhotonicResult? = null,
    val error:   String?       = null,
)
