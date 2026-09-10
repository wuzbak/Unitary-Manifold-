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
import androidx.core.content.edit
import androidx.drawerlayout.widget.DrawerLayout
import androidx.preference.PreferenceManager
import com.google.android.material.appbar.MaterialToolbar
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.UUID
import org.json.JSONObject
import org.json.JSONTokener

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
        renderNotebook()

        findViewById<android.view.View>(R.id.backButton).setOnClickListener { activeWebView()?.goBack() }
        findViewById<android.view.View>(R.id.forwardButton).setOnClickListener { activeWebView()?.goForward() }
        findViewById<android.view.View>(R.id.reloadButton).setOnClickListener { activeWebView()?.reload() }
        findViewById<android.view.View>(R.id.goButton).setOnClickListener { navigate(addressBar.text.toString()) }
        findViewById<android.view.View>(R.id.saveNoteButton).setOnClickListener { saveNotebookEntry() }
        findViewById<android.view.View>(R.id.importButton).setOnClickListener { importLauncher.launch(arrayOf("text/*", "application/json")) }
        findViewById<android.view.View>(R.id.exportButton).setOnClickListener { exportLauncher.launch("psicat-browser-notebook.json") }
        findViewById<android.view.View>(R.id.askButton).setOnClickListener { interrogate() }

        addressBar.imeOptions = EditorInfo.IME_ACTION_GO
        addressBar.setRawInputType(InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_URI)
        addressBar.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_GO) {
                navigate(addressBar.text.toString())
                true
            } else false
        }

        addTab(isPrivate = false)
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.browser_menu, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.action_new_tab -> addTab(false)
            R.id.action_private_tab -> addTab(true)
            R.id.action_bookmark -> saveNotebookEntry(prefixWithPage = true)
            R.id.action_sidebar -> drawerLayout.openDrawer(findViewById(R.id.sidebar))
            R.id.action_settings -> startActivity(Intent(this, SettingsActivity::class.java))
        }
        return super.onOptionsItemSelected(item)
    }

    private fun addTab(isPrivate: Boolean) {
        val homePage = prefs().getString("home_page", "https://example.com") ?: "https://example.com"
        val tab = BrowserTab(UUID.randomUUID().toString(), if (isPrivate) "Private Tab" else "New Tab", homePage, isPrivate)
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
                    capturePageContext(tab)
                    renderTabs()
                }
            }
            webChromeClient = WebChromeClient()
            loadUrl(homePage)
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
    }

    private fun renderTabs() {
        tabStrip.removeAllViews()
        tabs.forEach { tab ->
            val chip = com.google.android.material.button.MaterialButton(this).apply {
                text = if (tab.isPrivate) "🕶 ${tab.title}" else tab.title
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
        renderNotebook()
    }

    private fun renderNotebook() {
        notebookList.text = if (notebook.isEmpty()) {
            "No notebook entries yet."
        } else {
            notebook.joinToString("\n\n") { "• ${it.title}\n${it.text.take(240)}\n${it.createdAt}" }
        }
    }

    private fun interrogate() {
        val question = questionBox.text.toString().trim()
        if (question.isBlank()) return
        val snapshot = currentTab()?.lastSnapshot
        contextSummary.text = "Thinking…"
        Thread {
            val local = buildString {
                appendLine("[Local Android PsiCat mode]")
                appendLine("Question: $question")
                snapshot?.let { appendLine(buildContextSummary(it)) }
                if (notebook.isNotEmpty()) appendLine("Notebook topics: ${notebook.take(5).joinToString { it.title }}")
            }
            val answer = runCatching { remotePsiCat(question, snapshot) }.getOrElse { local }
            runOnUiThread { contextSummary.text = answer }
        }.start()
    }

    private fun remotePsiCat(question: String, snapshot: PageSnapshot?): String {
        val endpoint = prefs().getString("psicat_endpoint", "http://127.0.0.1:8020") ?: "http://127.0.0.1:8020"
        val statusConnection = URL("$endpoint/api/psicat/status").openConnection() as HttpURLConnection
        val statusBody = statusConnection.inputStream.bufferedReader().use(BufferedReader::readText)
        val statusJson = JSONObject(statusBody)
        val challenge = statusConnection.getHeaderField("X-PsiCat-Handshake-Challenge") ?: throw IllegalStateException("Missing challenge")
        val receipt = statusConnection.getHeaderField("X-PsiCat-Handshake-Receipt") ?: throw IllegalStateException("Missing receipt")
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
        notebook.add(0, NotebookEntry(title, text, timestamp()))
        notebook = notebook.take(100).toMutableList()
        stateStore.saveNotebook(notebook)
        renderNotebook()
    }

    private fun exportNotebook(uri: Uri) {
        val payload = JSONObject().apply {
            put("exportedAt", timestamp())
            put("notebook", notebook.map { JSONObject().apply {
                put("title", it.title)
                put("text", it.text)
                put("createdAt", it.createdAt)
            } })
        }
        contentResolver.openOutputStream(uri)?.bufferedWriter()?.use { it.write(payload.toString(2)) }
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

    private fun timestamp(): String = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US).format(Date())

    private fun sha256(text: String): String = java.security.MessageDigest.getInstance("SHA-256")
        .digest(text.toByteArray())
        .joinToString("") { "%02x".format(it) }
}
