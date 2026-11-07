package com.axiomzero.androidsuite

import org.json.JSONArray
import org.json.JSONObject
import java.time.Instant

data class ResearchNote(
    val createdAt: String,
    val question: String,
    val answer: String
)

class ResearchNotebook(private val file: java.io.File) {
    companion object {
        const val MAX_NOTES = 100
    }

    fun add(question: String, matches: List<EvidenceMatch>): ResearchNote {
        require(question.isNotBlank()) { "A research question is required." }
        val note = ResearchNote(
            createdAt = Instant.now().toString(),
            question = question.trim().take(2_000),
            answer = if (matches.isEmpty()) {
                "UNVERIFIED — no matching local evidence was found."
            } else {
                buildString {
                    appendLine("UNVERIFIED — local keyword matches only; verify the source and interpretation.")
                    matches.forEach { match ->
                        appendLine()
                        appendLine("[${match.name}:${match.line}] SHA-256 ${match.sha256}")
                        appendLine(match.excerpt)
                    }
                }.trim()
            }
        )
        val notes = load().toMutableList()
        require(notes.size < MAX_NOTES) { "The research notebook is limited to $MAX_NOTES notes." }
        notes += note
        val rows = JSONArray()
        notes.forEach {
            rows.put(
                JSONObject()
                    .put("createdAt", it.createdAt)
                    .put("question", it.question)
                    .put("answer", it.answer)
            )
        }
        val temporary = java.io.File(file.parentFile, "${file.name}.tmp")
        temporary.writeText(rows.toString())
        if (!temporary.renameTo(file)) {
            temporary.delete()
            throw IllegalStateException("The private research notebook could not be saved.")
        }
        return note
    }

    fun load(): List<ResearchNote> {
        if (!file.exists()) return emptyList()
        val rows = JSONArray(file.readText())
        return buildList(rows.length()) {
            for (index in 0 until rows.length()) {
                val row = rows.getJSONObject(index)
                add(ResearchNote(row.getString("createdAt"), row.getString("question"), row.getString("answer")))
            }
        }
    }

    fun exportMarkdown(): String = buildString {
        appendLine("# AxiomZero Android Suite — Research notebook")
        appendLine()
        appendLine("Local retrieval notes are UNVERIFIED. Imported evidence is private app data and is not encrypted.")
        appendLine()
        load().forEach { note ->
            appendLine("## ${note.question}")
            appendLine()
            appendLine("Created: ${note.createdAt}")
            appendLine()
            appendLine(note.answer)
            appendLine()
        }
    }

    fun clear(): Boolean = !file.exists() || file.delete()
}
