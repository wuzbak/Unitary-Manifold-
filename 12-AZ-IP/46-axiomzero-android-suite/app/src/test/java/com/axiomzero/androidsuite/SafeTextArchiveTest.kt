package com.axiomzero.androidsuite

import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.Assert.assertThrows
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

class SafeTextArchiveTest {
    @Test
    fun readsSupportedTextAndSkipsUnsafeOrUnsupportedEntries() {
        val archive = zip(
            "../escape.txt" to "unsafe",
            "folder/notes.md" to "Local evidence",
            "image.png" to "not indexed"
        )

        val documents = SafeTextArchive.readArchive(ByteArrayInputStream(archive), "picked.zip")

        assertEquals(1, documents.size)
        assertEquals("picked.zip!/folder/notes.md", documents.single().name)
        assertEquals("Local evidence", documents.single().text)
        assertEquals(64, documents.single().sha256.length)
    }

    @Test
    fun rejectsOversizedExpandedEntries() {
        val archive = zip("large.txt" to "x".repeat(SafeTextArchive.MAX_DOCUMENT_BYTES + 1))

        assertThrows(IllegalArgumentException::class.java) {
            SafeTextArchive.readArchive(ByteArrayInputStream(archive), "large.zip")
        }
    }

    @Test
    fun rejectsUnsupportedStandaloneFilesAndBinaryText() {
        assertThrows(IllegalArgumentException::class.java) {
            SafeTextArchive.readText("private.pdf", ByteArrayInputStream(byteArrayOf(1, 2, 3)))
        }
        assertThrows(IllegalArgumentException::class.java) {
            SafeTextArchive.readText("data.txt", ByteArrayInputStream(byteArrayOf(0)))
        }
    }

    private fun zip(vararg entries: Pair<String, String>): ByteArray {
        val output = ByteArrayOutputStream()
        ZipOutputStream(output).use { zip ->
            entries.forEach { (name, text) ->
                zip.putNextEntry(ZipEntry(name))
                zip.write(text.toByteArray())
                zip.closeEntry()
            }
        }
        return output.toByteArray()
    }
}
