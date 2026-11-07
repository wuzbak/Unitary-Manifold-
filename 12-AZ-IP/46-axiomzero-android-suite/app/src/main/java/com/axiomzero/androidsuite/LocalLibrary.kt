package com.axiomzero.androidsuite

import android.content.ContentResolver
import android.net.Uri
import org.json.JSONArray
import org.json.JSONObject
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicLong

internal object LocalStoreTasks {
    val worker = Executors.newSingleThreadExecutor()
    val evidenceRevision = AtomicLong()
}

data class EvidenceDocument(
    val name: String,
    val text: String,
    val sha256: String
)

data class EvidenceMatch(
    val name: String,
    val line: Int,
    val excerpt: String,
    val sha256: String,
    val score: Int
)

class LocalLibrary(private val file: java.io.File) {
    companion object {
        const val MAX_COLLECTION_BYTES = 8 * 1024 * 1024
        const val MAX_DOCUMENTS = 500

        internal fun searchDocuments(documents: List<EvidenceDocument>, query: String, limit: Int): List<EvidenceMatch> {
            require(limit >= 0) { "The search result limit cannot be negative." }
            val terms = query.lowercase().split(Regex("[^\\p{L}\\p{N}_]+")).filter { it.length > 1 }.distinct()
            if (terms.isEmpty() || limit == 0) return emptyList()
            val order = compareByDescending<EvidenceMatch> { it.score }.thenBy { it.name }.thenBy { it.line }
            val best = mutableListOf<EvidenceMatch>()
            for (document in documents) {
                document.text.lineSequence().forEachIndexed { index, line ->
                    val lowered = line.lowercase()
                    val score = terms.count(lowered::contains)
                    if (score > 0) {
                        val firstMatch = terms.map { line.indexOf(it, ignoreCase = true) }
                            .filter { it >= 0 }.minOrNull() ?: 0
                        val start = (firstMatch - 100).coerceAtLeast(0)
                        val match = EvidenceMatch(
                            document.name, index + 1,
                            line.substring(start, minOf(line.length, start + 500)).trim(),
                            document.sha256, score
                        )
                        val position = best.indexOfFirst { order.compare(match, it) < 0 }
                            .let { if (it < 0) best.size else it }
                        if (position < limit) {
                            best.add(position, match)
                            if (best.size > limit) best.removeAt(best.lastIndex)
                        }
                    }
                }
            }
            return best
        }
    }

    fun documents(): List<EvidenceDocument> {
        if (!file.exists()) return emptyList()
        val rows = JSONArray(file.readText())
        return buildList(rows.length()) {
            for (index in 0 until rows.length()) {
                val row = rows.getJSONObject(index)
                add(EvidenceDocument(row.getString("name"), row.getString("text"), row.getString("sha256")))
            }
        }
    }

    fun import(resolver: ContentResolver, uri: Uri, displayName: String): Int {
        val current = documents().toMutableList()
        val additions = resolver.openInputStream(uri)?.use { input ->
            if (displayName.substringAfterLast('.', "").lowercase() == "zip") {
                SafeTextArchive.readArchive(input, displayName)
            } else {
                listOf(SafeTextArchive.readText(displayName, input))
            }
        } ?: throw IllegalStateException("Android could not open the selected document.")
        val combined = (current + additions).distinctBy { "${it.name}:${it.sha256}" }
        require(combined.size <= MAX_DOCUMENTS) { "The local library is limited to $MAX_DOCUMENTS files." }
        require(combined.sumOf { it.text.toByteArray(Charsets.UTF_8).size } <= MAX_COLLECTION_BYTES) {
            "The local library is limited to 8 MiB of indexed text."
        }
        save(combined)
        return combined.size - current.size
    }

    fun search(query: String, limit: Int = 5): List<EvidenceMatch> = searchDocuments(documents(), query, limit)

    fun clear(): Boolean = !file.exists() || file.delete()

    private fun save(documents: List<EvidenceDocument>) {
        val rows = JSONArray()
        documents.forEach { document ->
            rows.put(JSONObject().put("name", document.name).put("text", document.text).put("sha256", document.sha256))
        }
        val temporary = java.io.File(file.parentFile, "${file.name}.tmp")
        temporary.writeText(rows.toString())
        if (!temporary.renameTo(file)) {
            temporary.delete()
            throw IllegalStateException("The local evidence index could not be saved.")
        }
    }
}
