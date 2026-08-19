package com.gibbernode.gibberwave

import android.util.Log
import com.google.gson.Gson
import com.google.gson.JsonSyntaxException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton

private const val TAG = "Pentacorder/IntentEngine"

/**
 * IntentEngine
 *
 * Sends [CommonToken] intents to a local Ollama LLM instance and returns
 * the model's response as a plain string.
 *
 * Default endpoint: http://localhost:11434 (Ollama default in Termux).
 * Configurable via [OllamaConfig].
 *
 * Offline behaviour: if Ollama is unreachable (connection refused, timeout),
 * [query] returns a fallback string so the UI doesn't hang.
 */
@Singleton
class IntentEngine @Inject constructor(
    private val config: OllamaConfig,
) {
    private val gson = Gson()
    private val http = OkHttpClient.Builder()
        .connectTimeout(5, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    /**
     * Query the Ollama model with a [CommonToken] as context.
     *
     * The prompt follows the sentinel_commentary.py humanize format:
     *   system prompt sets the role, user message is the token JSON.
     *
     * @param token   Token to analyse.
     * @param prompt  Override the user prompt (defaults to humanized analysis request).
     * @return        Model response string, or a fallback offline message.
     */
    suspend fun query(
        token: CommonToken,
        prompt: String = defaultPrompt(token),
    ): String = withContext(Dispatchers.IO) {
        try {
            val body = buildRequestBody(prompt)
            val request = Request.Builder()
                .url("${config.baseUrl}/api/generate")
                .post(body.toRequestBody("application/json".toMediaType()))
                .build()

            http.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    Log.w(TAG, "Ollama returned HTTP ${response.code}")
                    return@withContext offlineFallback(token)
                }
                val responseJson = response.body?.string() ?: return@withContext offlineFallback(token)
                parseOllamaResponse(responseJson)
            }
        } catch (e: IOException) {
            Log.d(TAG, "Ollama offline or unreachable: ${e.message}")
            offlineFallback(token)
        } catch (e: Exception) {
            Log.e(TAG, "IntentEngine.query failed", e)
            offlineFallback(token)
        }
    }

    /**
     * Free-form RAG query — send any question and receive an answer.
     * Used by the Audit screen's "Ask the RAG bot" input.
     */
    suspend fun ask(question: String): String = withContext(Dispatchers.IO) {
        try {
            val body = buildRequestBody(question)
            val request = Request.Builder()
                .url("${config.baseUrl}/api/generate")
                .post(body.toRequestBody("application/json".toMediaType()))
                .build()

            http.newCall(request).execute().use { response ->
                if (!response.isSuccessful) return@withContext "Ollama returned HTTP ${response.code}"
                val responseJson = response.body?.string() ?: return@withContext "Empty response"
                parseOllamaResponse(responseJson)
            }
        } catch (e: IOException) {
            "Ollama is offline. Start it with: ollama run ${config.model}"
        } catch (e: Exception) {
            Log.e(TAG, "IntentEngine.ask failed", e)
            "Error: ${e.message}"
        }
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private fun buildRequestBody(prompt: String): String {
        return gson.toJson(mapOf(
            "model"  to config.model,
            "prompt" to prompt,
            "stream" to false,
            "system" to SYSTEM_PROMPT,
        ))
    }

    private fun parseOllamaResponse(json: String): String {
        return try {
            val obj = gson.fromJson(json, Map::class.java)
            (obj["response"] as? String)?.trim() ?: json
        } catch (e: JsonSyntaxException) {
            json.take(500)
        }
    }

    private fun offlineFallback(token: CommonToken): String {
        val mood = when {
            token.intent == IntentTag.ALERT -> "⚠️ Alert detected — start Ollama for AI analysis."
            token.payload.startsWith("SYS") -> "📊 System telemetry received — Ollama offline."
            token.payload.startsWith("VITALS") -> "❤️ Vitals received — Ollama offline."
            else -> "📡 Token received — Ollama offline. Run: ollama run ${config.model}"
        }
        return mood
    }

    private fun defaultPrompt(token: CommonToken): String = buildString {
        append("Analyse this Gibbernode sensor token and give a brief, plain-language ")
        append("assessment in 1–2 sentences. No jargon. Use the manifold mood: ")
        append("CALM / STRESSED / EXHAUSTED / CRITICAL.\n\n")
        append("Token: ${token.payload}\n")
        append("Source: ${token.source.name}\n")
        append("Intent: ${token.intent.name}\n")
        append("Timestamp: ${token.timestamp}\n")
    }

    companion object {
        private const val SYSTEM_PROMPT =
            "You are the Pentacorder Sentinel AI. You analyse hardware telemetry and " +
            "physical-world sensor data from a Blackview BV9900 Pro running the " +
            "Unitary-Manifold framework. Translate cold sensor numbers into plain " +
            "human language. Be concise, calm, and honest. Never use jargon."
    }
}

// ─────────────────────────────────────────────────────────────────────────────

/**
 * OllamaConfig — injectable configuration for the local LLM endpoint.
 */
data class OllamaConfig(
    val baseUrl: String = "http://localhost:11434",
    val model: String   = "llama3.2:3b",
)
