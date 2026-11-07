package com.axiomzero.androidsuite

import com.axiomzero.androidsuite.MobileModel.copyVerified

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertThrows
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.ByteArrayInputStream
import java.io.File
import java.security.MessageDigest
import java.util.concurrent.atomic.AtomicBoolean

class MobileModelTest {
    @Test
    fun nativeSourcePinsTheFullFortyCharacterLlamaCommit() {
        val revision = "9f0e5098a5d5d8adb8dd5c59036ae2a38ab07db9"
        assertEquals(40, revision.length)

        val projectRoot = File(System.getProperty("user.dir"))
        val candidates = listOf(
            File(projectRoot, "src/main/cpp/CMakeLists.txt"),
            File(projectRoot, "app/src/main/cpp/CMakeLists.txt"),
            File(projectRoot, "12-AZ-IP/46-axiomzero-android-suite/app/src/main/cpp/CMakeLists.txt")
        )
        val cmake = candidates.firstOrNull { it.isFile }
            ?: error("Could not locate Product 46's llama.cpp CMake configuration.")
        val configuration = cmake.readText()
        assertTrue(configuration.contains("set(LLAMA_CPP_REVISION \"$revision\""))
        assertTrue(configuration.contains("STREQUAL LLAMA_CPP_REVISION"))
    }

    @Test
    fun pinnedArtifactUsesExactImmutableIdentity() {
        assertEquals(1_280_835_840L, MobileModel.SIZE_BYTES)
        assertEquals(
            "https://huggingface.co/Unsloth/Qwen3.5-2B-GGUF/resolve/" +
                "802854bfd388ed92748de119df31327962811548/Qwen3.5-2B-Q4_K_M.gguf?download=true",
            MobileModel.downloadUrl()
        )
        assertEquals(64, MobileModel.SHA256.length)
        assertEquals(1792L * 1024 * 1024, MobileModel.MIN_FREE_BYTES)
        assertEquals(4L * 1024 * 1024 * 1024, MobileModel.MIN_RAM_BYTES)
    }

    @Test
    fun verifiedStreamAtomicallyReplacesDestinationOnlyAfterFullHashMatch() {
        val directory = testDirectory()
        try {
            val destination = File(directory, MobileModel.FILE_NAME)
            destination.writeText("old verified model")
            val bytes = "small test fixture".toByteArray()
            val hash = sha256(bytes)

            ByteArrayInputStream(bytes).copyVerified(
                destination, AtomicBoolean(), bytes.size.toLong(), hash
            )

            assertTrue(destination.readBytes().contentEquals(bytes))
            assertFalse(File(directory, "${MobileModel.FILE_NAME}.partial").exists())
        } finally {
            directory.deleteRecursively()
        }
    }

    @Test
    fun sizeAndHashFailuresPreservePriorInstallAndRemovePartialFile() {
        val directory = testDirectory()
        try {
            val destination = File(directory, MobileModel.FILE_NAME)
            destination.writeText("preserve old install")
            val bytes = "not the expected model".toByteArray()

            assertThrows(IllegalArgumentException::class.java) {
                ByteArrayInputStream(bytes).copyVerified(
                    destination, AtomicBoolean(), bytes.size.toLong() + 1, sha256(bytes)
                )
            }
            assertEquals("preserve old install", destination.readText())
            assertThrows(IllegalArgumentException::class.java) {
                ByteArrayInputStream(bytes).copyVerified(
                    destination, AtomicBoolean(), bytes.size.toLong(), "0".repeat(64)
                )
            }
            assertEquals("preserve old install", destination.readText())
            assertFalse(File(directory, "${MobileModel.FILE_NAME}.partial").exists())
        } finally {
            directory.deleteRecursively()
        }
    }

    @Test
    fun transferCancellationDoesNotInstallPartialModel() {
        val directory = testDirectory()
        try {
            val destination = File(directory, MobileModel.FILE_NAME)
            val cancelled = AtomicBoolean(true)
            assertThrows(InterruptedException::class.java) {
                ByteArrayInputStream(byteArrayOf(1, 2, 3)).copyVerified(
                    destination, cancelled, 3, sha256(byteArrayOf(1, 2, 3))
                )
            }
            assertFalse(destination.exists())
            assertFalse(File(directory, "${MobileModel.FILE_NAME}.partial").exists())
        } finally {
            directory.deleteRecursively()
        }
    }

    private fun sha256(bytes: ByteArray): String =
        MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }

    private fun testDirectory(): File =
        File(System.getProperty("user.dir"), ".model-test-${System.nanoTime()}").apply {
            check(mkdirs())
        }
}
