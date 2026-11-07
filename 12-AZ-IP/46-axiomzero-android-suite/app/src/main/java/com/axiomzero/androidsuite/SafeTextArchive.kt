package com.axiomzero.androidsuite

import java.io.ByteArrayOutputStream
import java.io.InputStream
import java.security.MessageDigest
import java.util.zip.ZipInputStream

object SafeTextArchive {
    const val MAX_ARCHIVE_BYTES = 16 * 1024 * 1024
    const val MAX_ARCHIVE_ENTRIES = 1_000
    const val MAX_DOCUMENT_BYTES = 2 * 1024 * 1024

    private val supportedExtensions = setOf(
        "txt", "md", "markdown", "json", "csv", "py", "kt", "java", "html", "xml",
        "yaml", "yml", "toml", "rst", "log"
    )

    fun readArchive(input: InputStream, archiveName: String): List<EvidenceDocument> {
        val documents = mutableListOf<EvidenceDocument>()
        var totalBytes = 0
        var archiveEntries = 0
        ZipInputStream(input).use { zip ->
            while (true) {
                val entry = zip.nextEntry ?: break
                archiveEntries += 1
                require(archiveEntries <= MAX_ARCHIVE_ENTRIES) {
                    "The selected ZIP exceeds the $MAX_ARCHIVE_ENTRIES-entry limit."
                }
                val normalized = entry.name.replace('\\', '/')
                val safeText = !entry.isDirectory && isSafeEntry(normalized) && isSupported(normalized)
                if (safeText) {
                    require(documents.size < LocalLibrary.MAX_DOCUMENTS) {
                        "The selected ZIP exceeds the ${LocalLibrary.MAX_DOCUMENTS}-file limit."
                    }
                }
                val bytes = readBounded(zip)
                totalBytes += bytes.size
                require(totalBytes <= MAX_ARCHIVE_BYTES) {
                    "The selected ZIP exceeds 16 MiB of expanded content."
                }
                if (safeText) documents += document("$archiveName!/$normalized", bytes)
                zip.closeEntry()
            }
        }
        require(documents.isNotEmpty()) { "The selected ZIP contains no supported text documents." }
        return documents
    }

    fun readText(name: String, input: InputStream): EvidenceDocument {
        require(isSupported(name)) { "Choose a supported text document or a ZIP archive." }
        return document(name, readBounded(input))
    }

    private fun document(name: String, bytes: ByteArray): EvidenceDocument {
        val text = bytes.toString(Charsets.UTF_8).removePrefix("\uFEFF")
        require('\u0000' !in text) { "Binary files are not indexed." }
        val digest = MessageDigest.getInstance("SHA-256")
            .digest(bytes)
            .joinToString("") { "%02x".format(it) }
        return EvidenceDocument(name.take(500), text, digest)
    }

    private fun readBounded(input: InputStream): ByteArray {
        val output = ByteArrayOutputStream()
        val buffer = ByteArray(8192)
        while (true) {
            val read = input.read(buffer)
            if (read < 0) break
            require(output.size() + read <= MAX_DOCUMENT_BYTES) {
                "A selected text file exceeds the 2 MiB limit."
            }
            output.write(buffer, 0, read)
        }
        return output.toByteArray()
    }

    private fun isSupported(name: String): Boolean =
        name.substringAfterLast('.', "").lowercase() in supportedExtensions

    private fun isSafeEntry(name: String): Boolean =
        name.isNotBlank() && !name.startsWith("/") && name.split("/").none { it == ".." || it.isBlank() }
}
