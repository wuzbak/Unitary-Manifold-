package com.axiomzero.psicatbrowser

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject

class BrowserStateStore(context: Context) {
    private val preferences = context.getSharedPreferences("psicat_browser_state", Context.MODE_PRIVATE)

    fun loadNotebook(): MutableList<NotebookEntry> {
        val raw = preferences.getString("notebook", "[]") ?: "[]"
        val array = JSONArray(raw)
        val entries = mutableListOf<NotebookEntry>()
        for (index in 0 until array.length()) {
            val item = array.getJSONObject(index)
            entries += NotebookEntry(
                title = item.optString("title"),
                text = item.optString("text"),
                createdAt = item.optString("createdAt"),
            )
        }
        return entries
    }

    fun saveNotebook(entries: List<NotebookEntry>) {
        val array = JSONArray()
        entries.forEach { entry ->
            array.put(JSONObject().apply {
                put("title", entry.title)
                put("text", entry.text)
                put("createdAt", entry.createdAt)
            })
        }
        preferences.edit().putString("notebook", array.toString()).apply()
    }
}
