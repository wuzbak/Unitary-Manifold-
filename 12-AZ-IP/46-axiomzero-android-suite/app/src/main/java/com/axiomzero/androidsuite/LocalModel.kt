package com.axiomzero.androidsuite

import android.app.ActivityManager
import android.content.ContentResolver
import android.net.Uri
import java.io.File
import java.io.FileInputStream
import java.io.InputStream
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest
import java.util.Locale
import java.util.concurrent.atomic.AtomicBoolean

object MobileModel {
    const val FILE_NAME = "Qwen3.5-2B-Q4_K_M.gguf"
    const val SIZE_BYTES = 1_280_835_840L
    const val SHA256 = "aaf42c8b7c3cab2bf3d69c355048d4a0ee9973d48f16c731c0520ee914699223"
    const val MIN_FREE_BYTES = 1792L * 1024 * 1024
    const val MIN_RAM_BYTES = 4L * 1024 * 1024 * 1024
    const val REVISION = "802854bfd388ed92748de119df31327962811548"
    const val REPOSITORY = "Unsloth/Qwen3.5-2B-GGUF"
    const val MODEL_CARD = "https://huggingface.co/Unsloth/Qwen3.5-2B-GGUF"
    const val BASE_MODEL_CARD = "https://huggingface.co/Qwen/Qwen3.5-2B"
    const val ASSISTANT_PREFIX = "<|im_start|>assistant\n<think>\n\n</think>\n\n"

    fun downloadUrl(): String =
        "https://huggingface.co/$REPOSITORY/resolve/$REVISION/$FILE_NAME?download=true"

    fun installedFile(directory: File): File = File(directory, FILE_NAME)

    fun screenStorage(directory: File): Boolean =
        directory.usableSpace >= MIN_FREE_BYTES

    fun screenMemory(activityManager: ActivityManager): Boolean =
        activityManager.totalMemoryBytes() >= MIN_RAM_BYTES

    fun verifyInstalled(file: File, cancelled: AtomicBoolean): Boolean {
        if (!file.isFile || file.length() != SIZE_BYTES) return false
        val digest = MessageDigest.getInstance("SHA-256")
        var total = 0L
        FileInputStream(file).buffered().use { input ->
            val buffer = ByteArray(1024 * 1024)
            while (true) {
                if (cancelled.get() || Thread.currentThread().isInterrupted) {
                    throw InterruptedException("Model verification cancelled.")
                }
                val count = input.read(buffer)
                if (count < 0) break
                total += count
                if (total > SIZE_BYTES) return false
                digest.update(buffer, 0, count)
            }
        }
        return total == SIZE_BYTES &&
            digest.digest().joinToString("") { "%02x".format(Locale.ROOT, it) } == SHA256
    }

    internal fun InputStream.copyVerified(
        destination: File,
        cancelled: AtomicBoolean,
        expectedSize: Long = MobileModel.SIZE_BYTES,
        expectedHash: String = MobileModel.SHA256,
        progress: (Long) -> Unit = {}
    ) {
        val temporary = File(destination.parentFile, "${destination.name}.partial")
        temporary.delete()
        val digest = MessageDigest.getInstance("SHA-256")
        var total = 0L
        try {
            temporary.outputStream().use { rawOutput ->
                rawOutput.buffered().use { output ->
                    val buffer = ByteArray(1024 * 1024)
                    while (true) {
                        if (cancelled.get() || Thread.currentThread().isInterrupted) {
                            throw InterruptedException("Model transfer cancelled.")
                        }
                        val count = read(buffer)
                        if (count < 0) break
                        total += count
                        require(total <= expectedSize) { "Selected model exceeds the pinned $expectedSize-byte size." }
                        digest.update(buffer, 0, count)
                        output.write(buffer, 0, count)
                        progress(total)
                    }
                    output.flush()
                    rawOutput.fd.sync()
                }
            }
            require(total == expectedSize) {
                "Model size mismatch: received $total bytes; expected $expectedSize."
            }
            val actualHash = digest.digest().joinToString("") { "%02x".format(Locale.ROOT, it) }
            require(actualHash == expectedHash) {
                "Model SHA-256 verification failed. The existing installed model was left unchanged."
            }
            java.nio.file.Files.move(
                temporary.toPath(), destination.toPath(),
                java.nio.file.StandardCopyOption.ATOMIC_MOVE,
                java.nio.file.StandardCopyOption.REPLACE_EXISTING
            )
        } catch (error: Exception) {
            temporary.delete()
            throw error
        }
    }

    fun importFrom(
        resolver: ContentResolver,
        uri: Uri,
        directory: File,
        cancelled: AtomicBoolean,
        progress: (Long) -> Unit = {}
    ) {
        require(screenStorage(directory)) {
            "Not enough private storage: keep at least ${MIN_FREE_BYTES / (1024 * 1024)} MiB free for verification."
        }
        resolver.openInputStream(uri)?.use { input ->
            importStream(input, directory, cancelled, progress)
        } ?: throw IllegalStateException("Android could not read the selected model file.")
    }

    internal fun importStream(
        input: InputStream,
        directory: File,
        cancelled: AtomicBoolean,
        progress: (Long) -> Unit = {}
    ) {
        require(screenStorage(directory)) {
            "Not enough private storage: keep at least ${MIN_FREE_BYTES / (1024 * 1024)} MiB free for verification."
        }
        input.copyVerified(installedFile(directory), cancelled, progress = progress)
    }

    fun download(
        directory: File,
        cancelled: AtomicBoolean,
        progress: (Long) -> Unit = {}
    ) {
        require(screenStorage(directory)) {
            "Not enough private storage: keep at least ${MIN_FREE_BYTES / (1024 * 1024)} MiB free for download and atomic installation."
        }
        val connection = URL(downloadUrl()).openConnection() as HttpURLConnection
        try {
            connection.instanceFollowRedirects = true
            connection.connectTimeout = 15_000
            connection.readTimeout = 30_000
            connection.setRequestProperty("User-Agent", "AxiomZero-Android-Suite/0.1.0")
            connection.connect()
            require(connection.responseCode in 200..299) {
                "Model download failed with HTTP ${connection.responseCode}."
            }
            require(connection.url.protocol == "https") { "The model download redirected to a non-HTTPS URL." }
            val host = connection.url.host.lowercase(Locale.ROOT)
            require(host == "huggingface.co" || host.endsWith(".huggingface.co") || host.endsWith(".hf.co")) {
                "The model download redirected outside Hugging Face's HTTPS domains."
            }
            require(connection.contentLengthLong == -1L || connection.contentLengthLong == SIZE_BYTES) {
                "The model server reported an unexpected content size."
            }
            connection.inputStream.use { input -> input.copyVerified(installedFile(directory), cancelled, progress = progress) }
        } finally {
            connection.disconnect()
        }
    }

    private fun ActivityManager.totalMemoryBytes(): Long {
        val info = ActivityManager.MemoryInfo()
        getMemoryInfo(info)
        return info.totalMem
    }
}

class LocalModelRuntime {
    private val handleOwnershipLock = java.lang.Object()
    private var handle: Long = 0
    private var activeNativeCancels = 0

    val isLoaded: Boolean
        get() = synchronized(handleOwnershipLock) { handle != 0L }

    companion object {
        init {
            System.loadLibrary("axiomzero_llama")
        }
    }

    fun engineVersion(): String = nativeVersion()

    fun load(path: String, contextTokens: Int = 2048): Boolean {
        synchronized(handleOwnershipLock) {
            if (handle != 0L) return true
        }
        val loaded = nativeLoad(path, contextTokens)
        if (loaded == 0L) return false
        synchronized(handleOwnershipLock) {
            if (handle == 0L) {
                handle = loaded
                return true
            }
        }
        nativeFree(loaded)
        return isLoaded
    }

    fun cancelLoad() = nativeCancelLoad()

    fun cancelGeneration() {
        val current = synchronized(handleOwnershipLock) {
            if (handle == 0L) return
            activeNativeCancels += 1
            handle
        }
        try {
            nativeCancel(current)
        } finally {
            synchronized(handleOwnershipLock) {
                activeNativeCancels -= 1
                if (activeNativeCancels == 0) handleOwnershipLock.notifyAll()
            }
        }
    }

    fun generate(prompt: String, maxTokens: Int = 192): String {
        val current = handle
        check(current != 0L) { "The local model is not loaded." }
        return nativeGenerate(current, prompt, maxTokens)
    }

    fun close() {
        var interrupted = false
        val current = synchronized(handleOwnershipLock) {
            val current = handle
            handle = 0L
            while (activeNativeCancels > 0) {
                try {
                    handleOwnershipLock.wait()
                } catch (_: InterruptedException) {
                    interrupted = true
                }
            }
            current
        }
        if (current != 0L) nativeFree(current)
        if (interrupted) Thread.currentThread().interrupt()
    }

    internal fun installCancellationProbeForTest() {
        synchronized(handleOwnershipLock) {
            check(handle == 0L) { "A model is already loaded." }
            handle = nativeCreateCancellationProbe()
            check(handle != 0L) { "Could not create native cancellation probe." }
        }
    }

    private external fun nativeVersion(): String
    private external fun nativeLoad(path: String, contextTokens: Int): Long
    private external fun nativeCancelLoad()
    private external fun nativeCreateCancellationProbe(): Long
    private external fun nativeCancel(handle: Long)
    private external fun nativeGenerate(handle: Long, prompt: String, maxTokens: Int): String
    private external fun nativeFree(handle: Long)
}
