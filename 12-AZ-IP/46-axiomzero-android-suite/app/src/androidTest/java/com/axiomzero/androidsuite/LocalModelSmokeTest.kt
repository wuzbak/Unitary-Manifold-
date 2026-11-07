package com.axiomzero.androidsuite

import android.util.Log
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.json.JSONObject
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File
import java.util.concurrent.atomic.AtomicBoolean

@RunWith(AndroidJUnit4::class)
class LocalModelSmokeTest {
    @Test
    fun nativeLinkageWritesSyntheticReceipt() {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        val context = instrumentation.targetContext
        var runtime: LocalModelRuntime? = null
        try {
            val activeRuntime = LocalModelRuntime()
            runtime = activeRuntime
            val version = activeRuntime.engineVersion()
            assertFalse("llama.cpp must be linked into the installed APK", version.isBlank())
            val receipt = JSONObject()
                .put("test", "Product 46 Android native linkage smoke")
                .put("engine", "llama.cpp $version")
                .put("abi", android.os.Build.SUPPORTED_ABIS.firstOrNull().orEmpty())
                .put("mode", "synthetic-linkage")
                .put("synthetic", true)
                .put("inference_executed", false)
            File(context.filesDir, "native-linkage-smoke-receipt.json").writeText(receipt.toString(2))
            Log.i("P46ModelSmoke", "mode=synthetic-linkage engine=$version")
        } finally {
            runtime.close()
        }
    }

    @Test
    fun optionalRealPinnedModelLoadAndBoundedInference() {
        val arguments = InstrumentationRegistry.getArguments()
        val requestedPath = arguments.getString("modelPath")
        val source = arguments.getString("modelSource") ?: "private-file"
        val required = arguments.getString("requireRealModel").equals("true", ignoreCase = true)
        assertTrue("modelSource must be private-file or app-download", source == "private-file" || source == "app-download")
        if (required && requestedPath == null && source != "app-download") {
            assertTrue("Supply modelPath or set modelSource=app-download for the required real-model lane", false)
        }
        assumeTrue(
            "Pass modelPath or set modelSource=app-download to opt into real-model inference",
            requestedPath != null || source == "app-download"
        )

        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val downloadedSource = if (source == "app-download") {
            val directory = File(context.noBackupFilesDir, "models").apply { check(mkdirs() || isDirectory) }
            MobileModel.download(directory, AtomicBoolean())
            MobileModel.installedFile(directory)
        } else {
            File(checkNotNull(requestedPath))
        }
        assertTrue("The supplied private model file must exist", downloadedSource.isFile)
        assertTrue(
            "The smoke test accepts only the pinned model's exact size and SHA-256",
            MobileModel.verifyInstalled(downloadedSource, AtomicBoolean())
        )
        var importDirectory: File? = null
        val model = if (source == "app-download") {
            importDirectory = File(context.cacheDir, "p46-model-import-smoke").apply {
                check(!exists() || deleteRecursively())
                check(mkdirs())
            }
            try {
                check(importDirectory!!.usableSpace >= MobileModel.SIZE_BYTES) {
                    "Insufficient private cache space to exercise the separate verified import copy."
                }
                downloadedSource.inputStream().buffered().use { input ->
                    MobileModel.importStream(input, importDirectory!!, AtomicBoolean())
                }
                val imported = MobileModel.installedFile(importDirectory!!)
                assertTrue("The private import stream must install the model", imported.isFile)
                assertTrue(
                    "The private imported model must pass exact size and SHA-256 verification",
                    MobileModel.verifyInstalled(imported, AtomicBoolean())
                )
                imported
            } catch (error: Exception) {
                importDirectory?.deleteRecursively()
                throw error
            }
        } else {
            downloadedSource
        }
        var runtime: LocalModelRuntime? = null
        try {
            val activeRuntime = LocalModelRuntime()
            runtime = activeRuntime
            val version = activeRuntime.engineVersion()
            assertTrue("The pinned GGUF must load on this device", activeRuntime.load(model.absolutePath, 512))
            val output = activeRuntime.generate(
                "<|im_start|>system\nReply with a short greeting.\n<|im_end|>\n" +
                    "<|im_start|>user\nHello.\n<|im_end|>\n<|im_start|>assistant\n",
                maxTokens = 16
            )
            assertTrue("Real model inference should produce bounded output", output.isNotBlank())
            assertTrue("Real model inference must not be cancelled", output != "Generation cancelled.")
            val receipt = JSONObject()
                .put("test", "Product 46 Android native real-model smoke")
                .put("engine", "llama.cpp $version")
                .put("abi", android.os.Build.SUPPORTED_ABIS.firstOrNull().orEmpty())
                .put("mode", if (source == "app-download") "real-pinned-model-app-download" else "real-pinned-model-private-file")
                .put("synthetic", false)
                .put("inference_executed", true)
                .put("source", source)
                .put("model_file", model.name)
                .put("model_bytes", model.length())
                .put("model_sha256", MobileModel.SHA256)
                .put("import_verified", source == "app-download")
                .put("context_tokens", 512)
                .put("generation_max_tokens", 16)
                .put("output", output.take(2000))
            val receiptFile = File(
                context.filesDir,
                "local-model-smoke-receipt.json"
            )
            receiptFile.writeText(receipt.toString(2))
            Log.i("P46ModelSmoke", "receipt=${receiptFile.absolutePath} mode=real-pinned-model")
        } finally {
            runtime?.close()
            importDirectory?.deleteRecursively()
        }
    }
}
