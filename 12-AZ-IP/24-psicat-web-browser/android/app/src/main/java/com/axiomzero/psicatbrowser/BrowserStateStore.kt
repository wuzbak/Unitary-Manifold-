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

    fun loadSession(): BrowserSessionSnapshot {
        val payload = JSONObject(preferences.getString("session", "{}") ?: "{}")
        val tabs = payload.optJSONArray("tabs").toTabs()
        val bookmarks = payload.optJSONArray("bookmarks").toBookmarks()
        val history = payload.optJSONArray("history").toHistory()
        return BrowserSessionSnapshot(
            tabs = tabs,
            activeTabId = payload.optString("activeTabId").ifBlank { tabs.firstOrNull()?.id },
            bookmarks = bookmarks,
            history = history,
            syncAccountEmail = payload.optString("syncAccountEmail"),
            syncMode = payload.optString("syncMode").ifBlank { "local+account" },
        )
    }

    fun saveSession(snapshot: BrowserSessionSnapshot) {
        val persistedTabs = snapshot.tabs.filterNot { it.isPrivate }
        val persistedActiveTabId = snapshot.activeTabId?.takeIf { tabId -> persistedTabs.any { it.id == tabId } }
        val payload = JSONObject().apply {
            put("activeTabId", persistedActiveTabId)
            put("syncAccountEmail", snapshot.syncAccountEmail)
            put("syncMode", snapshot.syncMode)
            put("tabs", JSONArray().apply {
                persistedTabs.forEach { tab ->
                    put(JSONObject().apply {
                        put("id", tab.id)
                        put("title", tab.title)
                        put("url", tab.url)
                        put("isPrivate", tab.isPrivate)
                        put("lastSnapshot", tab.lastSnapshot?.toJson())
                    })
                }
            })
            put("bookmarks", JSONArray().apply {
                snapshot.bookmarks.forEach { bookmark ->
                    put(JSONObject().apply {
                        put("title", bookmark.title)
                        put("url", bookmark.url)
                        put("createdAt", bookmark.createdAt)
                    })
                }
            })
            put("history", JSONArray().apply {
                snapshot.history.forEach { entry ->
                    put(JSONObject().apply {
                        put("title", entry.title)
                        put("url", entry.url)
                        put("visitedAt", entry.visitedAt)
                    })
                }
            })
        }
        preferences.edit().putString("session", payload.toString()).apply()
    }

    private fun JSONArray?.toTabs(): List<BrowserTab> {
        if (this == null) return emptyList()
        val items = mutableListOf<BrowserTab>()
        for (index in 0 until length()) {
            val item = getJSONObject(index)
            items += BrowserTab(
                id = item.optString("id"),
                title = item.optString("title"),
                url = item.optString("url"),
                isPrivate = item.optBoolean("isPrivate", false),
                lastSnapshot = item.optJSONObject("lastSnapshot")?.toPageSnapshot(),
            )
        }
        return items
    }

    private fun JSONArray?.toBookmarks(): List<BookmarkEntry> {
        if (this == null) return emptyList()
        val items = mutableListOf<BookmarkEntry>()
        for (index in 0 until length()) {
            val item = getJSONObject(index)
            items += BookmarkEntry(
                title = item.optString("title"),
                url = item.optString("url"),
                createdAt = item.optString("createdAt"),
            )
        }
        return items
    }

    private fun JSONArray?.toHistory(): List<HistoryEntry> {
        if (this == null) return emptyList()
        val items = mutableListOf<HistoryEntry>()
        for (index in 0 until length()) {
            val item = getJSONObject(index)
            items += HistoryEntry(
                title = item.optString("title"),
                url = item.optString("url"),
                visitedAt = item.optString("visitedAt"),
            )
        }
        return items
    }

    private fun JSONObject.toPageSnapshot(): PageSnapshot = PageSnapshot(
        title = optString("title"),
        url = optString("url"),
        selection = optString("selection"),
        text = optString("text"),
        capturedAt = optString("capturedAt"),
    )

    private fun PageSnapshot.toJson(): JSONObject = JSONObject().apply {
        put("title", title)
        put("url", url)
        put("selection", selection)
        put("text", text)
        put("capturedAt", capturedAt)
    }
}
