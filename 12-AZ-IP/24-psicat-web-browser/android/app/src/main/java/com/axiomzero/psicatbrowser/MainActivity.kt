package com.axiomzero.psicatbrowser

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.OpenableColumns
import android.text.InputType
import android.view.Menu
import android.view.MenuItem
import android.view.inputmethod.EditorInfo
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.drawerlayout.widget.DrawerLayout
import androidx.lifecycle.lifecycleScope
import androidx.preference.PreferenceManager
import com.google.android.material.appbar.MaterialToolbar
import java.io.BufferedReader
import java.net.HttpURLConnection
import java.net.URL
import java.util.UUID
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import org.json.JSONArray
import org.json.JSONTokener
import java.time.Instant

class MainActivity : AppCompatActivity() {
    private lateinit var drawerLayout: DrawerLayout
    private lateinit var toolbar: MaterialToolbar
    private lateinit var tabStrip: LinearLayout
    private lateinit var webContainer: FrameLayout
    private lateinit var addressBar: EditText
    private lateinit var contextSummary: TextView
    private lateinit var notebookList: TextView
    private lateinit var questionBox: EditText
    private lateinit var noteTitle: EditText
    private lateinit var noteBody: EditText
    private val stateStore by lazy { BrowserStateStore(this) }
    private val tabs = mutableListOf<BrowserTab>()
    private val webViews = linkedMapOf<String, WebView>()
    private val bookmarks = mutableListOf<BookmarkEntry>()
    private val history = mutableListOf<HistoryEntry>()
    private var activeTabId: String? = null
    private var notebook = mutableListOf<NotebookEntry>()

    private val importLauncher = registerForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        uri?.let { importDocument(it) }
    }

    private val exportLauncher = registerForActivityResult(ActivityResultContracts.CreateDocument("application/json")) { uri ->
        uri?.let { exportNotebook(it) }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        drawerLayout = findViewById(R.id.drawerLayout)
        toolbar = findViewById(R.id.toolbar)
        tabStrip = findViewById(R.id.tabStrip)
        webContainer = findViewById(R.id.webContainer)
        addressBar = findViewById(R.id.addressBar)
        contextSummary = findViewById(R.id.contextSummary)
        notebookList = findViewById(R.id.notebookList)
        questionBox = findViewById(R.id.questionBox)
        noteTitle = findViewById(R.id.noteTitle)
        noteBody = findViewById(R.id.noteBody)

        setSupportActionBar(toolbar)
        notebook = stateStore.loadNotebook()
        val savedSession = stateStore.loadSession()
        bookmarks += savedSession.bookmarks
        history += savedSession.history
        renderNotebook()

        findViewById<android.view.View>(R.id.backButton).setOnClickListener { activeWebView()?.goBack() }
        findViewById<android.view.View>(R.id.forwardButton).setOnClickListener { activeWebView()?.goForward() }
        findViewById<android.view.View>(R.id.reloadButton).setOnClickListener { activeWebView()?.reload() }
        findViewById<android.view.View>(R.id.goButton).setOnClickListener { navigate(addressBar.text.toString()) }
        findViewById<android.view.View>(R.id.saveNoteButton).setOnClickListener { saveNotebookEntry() }
        findViewById<android.view.View>(R.id.importButton).setOnClickListener { importLauncher.launch(arrayOf("text/*", "application/json")) }
        findViewById<android.view.View>(R.id.exportButton).setOnClickListener { exportLauncher.launch("psicat-browser-notebook.json") }
        findViewById<android.view.View>(R.id.askButton).setOnClickListener { interrogate() }
        findViewById<android.view.View>(R.id.pushSyncButton).setOnClickListener { pushSyncToBackend() }
        findViewById<android.view.View>(R.id.pullSyncButton).setOnClickListener { pullSyncFromBackend() }

        addressBar.imeOptions = EditorInfo.IME_ACTION_GO
        addressBar.setRawInputType(InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_URI)
        addressBar.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_GO) {
                navigate(addressBar.text.toString())
                true
            } else false
        }

        restoreSession(savedSession)
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.browser_menu, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.action_new_tab -> addTab()
            R.id.action_bookmark -> saveBookmarkForCurrentTab()
            R.id.action_sidebar -> drawerLayout.openDrawer(findViewById(R.id.sidebar))
            R.id.action_settings -> startActivity(Intent(this, SettingsActivity::class.java))
        }
        return super.onOptionsItemSelected(item)
    }

    private fun addTab() {
        val homePage = prefs().getString("home_page", "https://example.com") ?: "https://example.com"
        addTab(BrowserTab(UUID.randomUUID().toString(), "New Tab", homePage, false))
    }

    private fun addTab(tab: BrowserTab) {
        tabs += tab
        val webView = WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.loadsImagesAutomatically = true
            webViewClient = object : WebViewClient() {
                override fun onPageFinished(view: WebView?, url: String?) {
                    super.onPageFinished(view, url)
                    tab.url = url ?: tab.url
                    tab.title = view?.title ?: tab.title
                    addressBar.setText(tab.url)
                    pushHistory(tab)
                    capturePageContext(tab)
                    persistSessionState()
                    renderTabs()
                }
            }
            webChromeClient = WebChromeClient()
            loadUrl(tab.url)
        }
        webViews[tab.id] = webView
        activeTabId = tab.id
        switchTo(tab.id)
        renderTabs()
    }

    private fun switchTo(tabId: String) {
        activeTabId = tabId
        webContainer.removeAllViews()
        val active = webViews[tabId] ?: return
        webContainer.addView(active, FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT))
        addressBar.setText(tabs.firstOrNull { it.id == tabId }?.url.orEmpty())
        persistSessionState()
        renderNotebook()
    }

    private fun renderTabs() {
        tabStrip.removeAllViews()
        tabs.forEach { tab ->
            val chip = com.google.android.material.button.MaterialButton(this).apply {
                text = tab.title
                setOnClickListener { switchTo(tab.id) }
            }
            tabStrip.addView(chip)
        }
    }

    private fun activeWebView(): WebView? = activeTabId?.let { webViews[it] }

    private fun navigate(raw: String) {
        val url = if (raw.contains("://")) raw else if (raw.contains('.')) "https://$raw" else "https://duckduckgo.com/?q=${Uri.encode(raw)}"
        activeWebView()?.loadUrl(url)
    }

    private fun capturePageContext(tab: BrowserTab) {
        if (!prefs().getBoolean("live_capture", true)) return
        webViews[tab.id]?.evaluateJavascript(
            "(() => JSON.stringify({ title: document.title, url: location.href, selection: String(window.getSelection ? window.getSelection() : ''), text: document.body ? document.body.innerText.slice(0, 8000) : '' }))()"
        ) { raw ->
            val cleaned = JSONTokener(raw).nextValue() as? String ?: return@evaluateJavascript
            runCatching {
                val payload = JSONObject(cleaned)
                val snapshot = PageSnapshot(
                    title = payload.optString("title"),
                    url = payload.optString("url"),
                    selection = payload.optString("selection"),
                    text = payload.optString("text"),
                    capturedAt = timestamp(),
                )
                tab.lastSnapshot = snapshot
                contextSummary.text = buildContextSummary(snapshot)
            }
        }
    }

    private fun buildContextSummary(snapshot: PageSnapshot): String {
        val excerpt = (snapshot.selection.ifBlank { snapshot.text }).replace("\\s+".toRegex(), " ").take(480)
        return "${snapshot.title}\n${snapshot.url}\n\n$excerpt"
    }

    private fun saveNotebookEntry(prefixWithPage: Boolean = false) {
        val title = noteTitle.text.toString().ifBlank { currentTab()?.title ?: "Notebook note" }
        val pagePrefix = if (prefixWithPage) buildContextSummary(currentTab()?.lastSnapshot ?: return) + "\n\n" else ""
        val body = pagePrefix + noteBody.text.toString().ifBlank { currentTab()?.lastSnapshot?.text?.take(1200).orEmpty() }
        if (body.isBlank()) return
        notebook.add(0, NotebookEntry(title, body, timestamp()))
        notebook = notebook.take(100).toMutableList()
        stateStore.saveNotebook(notebook)
        persistSessionState()
        renderNotebook()
    }

    private fun renderNotebook() {
        val bookmarkSummary = if (bookmarks.isEmpty()) "No bookmarks." else bookmarks.take(5).joinToString("\n") { "★ ${it.title} — ${it.url}" }
        val historySummary = if (history.isEmpty()) "No history." else history.take(5).joinToString("\n") { "• ${it.title} — ${it.url}" }
        val notes = if (notebook.isEmpty()) "No notebook entries yet." else notebook.joinToString("\n\n") { "• ${it.title}\n${it.text.take(240)}\n${it.createdAt}" }
        notebookList.text = buildString {
            appendLine("Sync account: ${prefs().getString("sync_account_email", "").orEmpty().ifBlank { "Local-only" }}")
            appendLine("Sync mode: ${prefs().getString("sync_mode", "local+account")}")
            appendLine()
            appendLine("Bookmarks")
            appendLine(bookmarkSummary)
            appendLine()
            appendLine("Recent history")
            appendLine(historySummary)
            appendLine()
            appendLine("Notebook")
            append(notes)
        }
    }

    private fun interrogate() {
        val question = questionBox.text.toString().trim()
        if (question.isBlank()) return
        val snapshot = currentTab()?.lastSnapshot
        contextSummary.text = "Thinking…"
        lifecycleScope.launch(Dispatchers.IO) {
            val local = buildString {
                appendLine("[Local Android PsiCat mode]")
                appendLine("Question: $question")
                snapshot?.let { appendLine(buildContextSummary(it)) }
                if (notebook.isNotEmpty()) appendLine("Notebook topics: ${notebook.take(5).joinToString { it.title }}")
            }
            val answer = runCatching { remotePsiCat(question, snapshot) }.getOrElse { local }
            withContext(Dispatchers.Main) { contextSummary.text = answer }
        }
    }

    private fun remotePsiCat(question: String, snapshot: PageSnapshot?): String {
        val endpoint = prefs().getString("psicat_endpoint", "http://127.0.0.1:8020") ?: "http://127.0.0.1:8020"
        val statusConnection = URL("$endpoint/api/psicat/status").openConnection() as HttpURLConnection
        val statusBody = statusConnection.inputStream.bufferedReader().use(BufferedReader::readText)
        val statusJson = JSONObject(statusBody)
        val handshake = statusJson.optJSONObject("session_contract")?.optJSONObject("handshake")
        val challenge = statusConnection.getHeaderField("X-PsiCat-Handshake-Challenge")
            ?: handshake?.optString("challenge")
            ?: throw IllegalStateException("Missing challenge")
        val receipt = statusConnection.getHeaderField("X-PsiCat-Handshake-Receipt")
            ?: handshake?.optString("receipt")
            ?: throw IllegalStateException("Missing receipt")
        val token = statusJson.optString("memory_profile_token")
        val proof = sha256("$challenge:$token")
        val connection = URL("$endpoint/api/psicat").openConnection() as HttpURLConnection
        connection.requestMethod = "POST"
        connection.doOutput = true
        connection.setRequestProperty("Content-Type", "application/json")
        val payload = JSONObject().apply {
            put("query", question)
            put("page_context", snapshot?.text ?: "")
            put("memory_profile_token", token)
            put("psicat_handshake_challenge", challenge)
            put("psicat_handshake_receipt", receipt)
            put("psicat_handshake_proof", proof)
        }
        connection.outputStream.use { it.write(payload.toString().toByteArray()) }
        val body = connection.inputStream.bufferedReader().use(BufferedReader::readText)
        val json = JSONObject(body)
        return json.optString("answer", body)
    }

    private fun importDocument(uri: Uri) {
        val text = contentResolver.openInputStream(uri)?.bufferedReader()?.use(BufferedReader::readText).orEmpty()
        val title = queryName(uri)
        val restored = runCatching { JSONObject(text) }.getOrNull()
        if (restored != null && (restored.has("notebook") || restored.has("tabs") || restored.has("history"))) {
            restoreFromSyncPacket(restored)
        } else {
            notebook.add(0, NotebookEntry(title, text, timestamp()))
            notebook = notebook.take(100).toMutableList()
            stateStore.saveNotebook(notebook)
            persistSessionState()
            renderNotebook()
        }
    }

    private fun exportNotebook(uri: Uri) {
        val payload = buildSyncPacket()
        contentResolver.openOutputStream(uri)?.bufferedWriter()?.use { it.write(payload.toString(2)) }
        prefs().edit().putString("last_sync_at", timestamp()).apply()
        renderNotebook()
    }

    private fun queryName(uri: Uri): String {
        contentResolver.query(uri, null, null, null, null)?.use { cursor ->
            val index = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
            if (cursor.moveToFirst() && index >= 0) return cursor.getString(index)
        }
        return "Imported document"
    }

    private fun currentTab(): BrowserTab? = tabs.firstOrNull { it.id == activeTabId }

    private fun prefs() = PreferenceManager.getDefaultSharedPreferences(this)

    private fun timestamp(): String = Instant.now().toString()

    private fun sha256(text: String): String = java.security.MessageDigest.getInstance("SHA-256")
        .digest(text.toByteArray())
        .joinToString("") { "%02x".format(it) }

    private fun pushHistory(tab: BrowserTab) {
        history.removeAll { it.url == tab.url }
        history.add(0, HistoryEntry(tab.title, tab.url, timestamp()))
        while (history.size > 100) history.removeLast()
    }

    private fun saveBookmarkForCurrentTab() {
        val tab = currentTab() ?: return
        bookmarks.removeAll { it.url == tab.url }
        bookmarks.add(0, BookmarkEntry(tab.title, tab.url, timestamp()))
        while (bookmarks.size > 100) bookmarks.removeLast()
        persistSessionState()
        renderNotebook()
    }

    private fun persistSessionState() {
        stateStore.saveSession(
            BrowserSessionSnapshot(
                tabs = tabs,
                activeTabId = activeTabId,
                bookmarks = bookmarks,
                history = history,
                syncAccountEmail = prefs().getString("sync_account_email", "").orEmpty(),
                syncMode = prefs().getString("sync_mode", "local+account").orEmpty(),
            )
        )
    }

    private fun restoreSession(snapshot: BrowserSessionSnapshot) {
        if (snapshot.syncAccountEmail.isNotBlank()) {
            prefs().edit()
                .putString("sync_account_email", snapshot.syncAccountEmail)
                .putString("sync_mode", snapshot.syncMode)
                .apply()
        }
        if (snapshot.tabs.isEmpty()) {
            addTab()
            return
        }
        snapshot.tabs.forEach { tab -> addTab(tab.copy(isPrivate = false)) }
        snapshot.activeTabId?.let { switchTo(it) }
        renderNotebook()
    }

    private fun restoreFromSyncPacket(packet: JSONObject) {
        val importedNotebook = mutableListOf<NotebookEntry>()
        (packet.optJSONArray("notebook") ?: packet.optJSONArray("notebookEntries"))?.let { array ->
            for (index in 0 until array.length()) {
                val item = array.getJSONObject(index)
                importedNotebook += NotebookEntry(item.optString("title"), item.optString("text"), item.optString("createdAt"))
            }
        }
        if (importedNotebook.isNotEmpty()) {
            notebook = (importedNotebook + notebook).distinctBy { "${it.title}:${it.createdAt}" }.take(100).toMutableList()
            stateStore.saveNotebook(notebook)
        }
        bookmarks.clear()
        packet.optJSONArray("bookmarks")?.let { array ->
            for (index in 0 until array.length()) {
                val item = array.getJSONObject(index)
                bookmarks += BookmarkEntry(item.optString("title"), item.optString("url"), item.optString("createdAt"))
            }
        }
        history.clear()
        packet.optJSONArray("history")?.let { array ->
            for (index in 0 until array.length()) {
                val item = array.getJSONObject(index)
                history += HistoryEntry(item.optString("title"), item.optString("url"), item.optString("visitedAt"))
            }
        }
        val packetTabs = mutableListOf<BrowserTab>()
        packet.optJSONArray("tabs")?.let { array ->
            for (index in 0 until array.length()) {
                val item = array.getJSONObject(index)
                packetTabs += BrowserTab(
                    id = item.optString("id").ifBlank { UUID.randomUUID().toString() },
                    title = item.optString("title").ifBlank { "Imported Tab" },
                    url = item.optString("url").ifBlank { "https://example.com" },
                    isPrivate = false,
                )
            }
        }
        if (packetTabs.isNotEmpty()) {
            tabs.clear()
            webViews.values.forEach { it.destroy() }
            webViews.clear()
            webContainer.removeAllViews()
            packetTabs.forEach { addTab(it) }
            packet.optString("activeTabId").takeIf { it.isNotBlank() }?.let { switchTo(it) }
                ?: packet.optString("activeTabUrl").takeIf { it.isNotBlank() }?.let { activeUrl ->
                    tabs.firstOrNull { it.url == activeUrl }?.let { switchTo(it.id) }
                }
        }
        val syncObject = packet.optJSONObject("sync")
        val syncAccountEmail = packet.optString("syncAccountEmail")
            .ifBlank { syncObject?.optString("accountEmail").orEmpty() }
        val syncMode = packet.optString("syncMode")
            .ifBlank { syncObject?.optString("mode").orEmpty() }
            .ifBlank { "local+account" }
        prefs().edit()
            .putString("sync_account_email", syncAccountEmail)
            .putString("sync_mode", syncMode)
            .putString("last_sync_at", timestamp())
            .apply()
        persistSessionState()
        renderNotebook()
    }

    private fun buildSyncPacket(): JSONObject = JSONObject().apply {
        put("product", 24)
        put("exportedAt", timestamp())
        put("sync", JSONObject().apply {
            put("accountEmail", prefs().getString("sync_account_email", ""))
            put("mode", prefs().getString("sync_mode", "local+account"))
            put("lastSyncAt", prefs().getString("last_sync_at", ""))
            put("lastSyncSource", prefs().getString("last_sync_source", "android-export"))
        })
        put("syncAccountEmail", prefs().getString("sync_account_email", ""))
        put("syncMode", prefs().getString("sync_mode", "local+account"))
        put("tabs", JSONArray().apply {
            tabs.forEach { tab ->
                put(JSONObject().apply {
                    put("id", tab.id)
                    put("title", tab.title)
                    put("url", tab.url)
                    put("private", false)
                    tab.lastSnapshot?.let { snapshot ->
                        put("lastSnapshot", JSONObject().apply {
                            put("title", snapshot.title)
                            put("url", snapshot.url)
                            put("selection", snapshot.selection)
                            put("text", snapshot.text)
                            put("capturedAt", snapshot.capturedAt)
                        })
                    }
                })
            }
        })
        put("activeTabId", activeTabId)
        put("bookmarks", JSONArray().apply {
            bookmarks.forEach { bookmark ->
                put(JSONObject().apply {
                    put("title", bookmark.title)
                    put("url", bookmark.url)
                    put("createdAt", bookmark.createdAt)
                })
            }
        })
        put("history", JSONArray().apply {
            history.forEach { entry ->
                put(JSONObject().apply {
                    put("title", entry.title)
                    put("url", entry.url)
                    put("visitedAt", entry.visitedAt)
                })
            }
        })
        put("notebook", JSONArray().apply {
            notebook.forEach {
                put(JSONObject().apply {
                    put("title", it.title)
                    put("text", it.text)
                    put("createdAt", it.createdAt)
                })
            }
        })
        put("notebookEntries", getJSONArray("notebook"))
        put("settings", JSONObject().apply {
            put("homePage", prefs().getString("home_page", "https://example.com"))
            put("searchEngine", prefs().getString("search_engine", "https://duckduckgo.com/?q=%s"))
            put("psicatEndpoint", prefs().getString("psicat_endpoint", "http://127.0.0.1:8020"))
            put("syncBackendEndpoint", prefs().getString("sync_backend_endpoint", "http://127.0.0.1:8787"))
            put("livePageCapture", prefs().getBoolean("live_capture", true))
        })
    }

    private fun pushSyncToBackend() {
        val accountEmail = prefs().getString("sync_account_email", "").orEmpty().trim()
        val accessToken = prefs().getString("sync_access_token", "").orEmpty().trim()
        if (accountEmail.isBlank()) {
            contextSummary.text = "Set Sync account email before backend sync."
            return
        }
        if (accessToken.isBlank()) {
            contextSummary.text = "Set Sync access token before backend sync."
            return
        }
        contextSummary.text = "Pushing sync packet…"
        lifecycleScope.launch(Dispatchers.IO) {
            val endpoint = prefs().getString("sync_backend_endpoint", "http://127.0.0.1:8787") ?: "http://127.0.0.1:8787"
            val connection = URL("$endpoint/api/sync/push").openConnection() as HttpURLConnection
            connection.requestMethod = "POST"
            connection.doOutput = true
            connection.setRequestProperty("Content-Type", "application/json")
            connection.setRequestProperty("X-Sync-Token", accessToken)
            val payload = JSONObject().apply {
                put("account_email", accountEmail)
                put("packet", buildSyncPacket())
            }
            connection.outputStream.bufferedWriter().use { it.write(payload.toString()) }
            val body = (if (connection.responseCode in 200..299) connection.inputStream else connection.errorStream)
                ?.bufferedReader()?.use(BufferedReader::readText).orEmpty()
            if (connection.responseCode !in 200..299) throw IllegalStateException(body.ifBlank { "Sync push failed" })
            prefs().edit()
                .putString("last_sync_at", timestamp())
                .putString("last_sync_source", "backend-push")
                .apply()
            withContext(Dispatchers.Main) {
                contextSummary.text = "Sync push complete.\n$body"
                renderNotebook()
            }
        }.invokeOnCompletion { error ->
            if (error != null) runOnUiThread { contextSummary.text = "Sync push failed: ${error.message}" }
        }
    }

    private fun pullSyncFromBackend() {
        val accountEmail = prefs().getString("sync_account_email", "").orEmpty().trim()
        val accessToken = prefs().getString("sync_access_token", "").orEmpty().trim()
        if (accountEmail.isBlank()) {
            contextSummary.text = "Set Sync account email before backend sync."
            return
        }
        if (accessToken.isBlank()) {
            contextSummary.text = "Set Sync access token before backend sync."
            return
        }
        contextSummary.text = "Pulling sync packet…"
        lifecycleScope.launch(Dispatchers.IO) {
            val endpoint = prefs().getString("sync_backend_endpoint", "http://127.0.0.1:8787") ?: "http://127.0.0.1:8787"
            val connection = URL("$endpoint/api/sync/pull?account_email=${Uri.encode(accountEmail)}").openConnection() as HttpURLConnection
            connection.setRequestProperty("X-Sync-Token", accessToken)
            val body = (if (connection.responseCode in 200..299) connection.inputStream else connection.errorStream)
                ?.bufferedReader()?.use(BufferedReader::readText).orEmpty()
            if (connection.responseCode !in 200..299) throw IllegalStateException(body.ifBlank { "Sync pull failed" })
            val packet = JSONObject(body).optJSONObject("packet") ?: throw IllegalStateException("Missing packet")
            withContext(Dispatchers.Main) {
                restoreFromSyncPacket(packet)
                prefs().edit()
                    .putString("last_sync_at", timestamp())
                    .putString("last_sync_source", "backend-pull")
                    .apply()
                contextSummary.text = "Sync pull complete."
                renderNotebook()
            }
        }.invokeOnCompletion { error ->
            if (error != null) runOnUiThread { contextSummary.text = "Sync pull failed: ${error.message}" }
        }
    }
}
