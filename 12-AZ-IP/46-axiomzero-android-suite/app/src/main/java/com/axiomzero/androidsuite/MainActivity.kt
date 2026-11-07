package com.axiomzero.androidsuite

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.OpenableColumns
import android.view.Gravity
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.documentfile.provider.DocumentFile
import java.io.ByteArrayOutputStream
import java.io.File
import java.util.concurrent.Executors

class MainActivity : AppCompatActivity() {
    private val worker = Executors.newSingleThreadExecutor()
    private lateinit var content: LinearLayout
    private lateinit var catalog: List<Product>
    private lateinit var library: LocalLibrary
    private lateinit var notebook: ResearchNotebook
    private var selectedMatches = emptyList<EvidenceMatch>()
    private var selectedTab = "Portfolio"
    private var filter = ""
    private var question = ""
    private var selectedQuestion = ""
    private var searchResults = ""
    private var repositoryUri: Uri? = null

    private val documentPicker = registerForActivityResult(ActivityResultContracts.OpenMultipleDocuments()) { uris ->
        if (uris.isNotEmpty()) importDocuments(uris)
    }
    private val checkoutPicker = registerForActivityResult(ActivityResultContracts.OpenDocumentTree()) { uri ->
        if (uri != null) {
            try {
                contentResolver.takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION)
                repositoryUri = uri
                getSharedPreferences("suite", MODE_PRIVATE).edit().putString("repositoryUri", uri.toString()).apply()
                toast("Checkout folder selected. Product documentation stays on this device.")
                render()
            } catch (error: SecurityException) {
                toast(error.message ?: "Android did not grant persistent access to that folder.")
            }
        }
    }
    private val exportPicker = registerForActivityResult(ActivityResultContracts.CreateDocument("text/markdown")) { uri ->
        if (uri != null) exportNotebook(uri)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        catalog = PortfolioCatalog.load(this)
        library = LocalLibrary(File(filesDir, "local-evidence.json"))
        notebook = ResearchNotebook(File(filesDir, "research-notebook.json"))
        repositoryUri = getSharedPreferences("suite", MODE_PRIVATE).getString("repositoryUri", null)?.let(Uri::parse)
        render()
    }

    override fun onDestroy() {
        worker.shutdown()
        super.onDestroy()
    }

    private fun render() {
        val page = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(18), dp(12), dp(18), dp(28))
        }
        page.addView(label("AXIOMZERO · PRODUCT 46", 13, "#80B9FF"))
        page.addView(label("Android Suite", 28, "#F1F5FB", bold = true))
        page.addView(label("Offline-first portfolio, local evidence and governed research", 14, "#A9B8CC"))
        page.addView(label("On-device only. No account, analytics, network, or broad storage permission.", 12, "#75D6B0"))

        val tabs = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER
        }
        listOf("Portfolio" to "Portfolio", "Evidence" to "Evidence & Ask", "Research" to "Research")
            .forEach { (tabLabel, tab) ->
            tabs.addView(button(tabLabel) {
                selectedTab = tab
                render()
            }, LinearLayout.LayoutParams(0, dp(48), 1f).apply { setMargins(dp(2), dp(12), dp(2), dp(10)) })
        }
        page.addView(tabs)
        content = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        page.addView(content)
        setContentView(ScrollView(this).apply { addView(page) })

        when (selectedTab) {
            "Portfolio" -> renderPortfolio()
            "Evidence & Ask" -> renderEvidence()
            else -> renderResearch()
        }
    }

    private fun renderPortfolio() {
        content.addView(label("${catalog.size} registered products · offline catalog", 14, "#A9B8CC"))
        content.addView(button(if (repositoryUri == null) "Choose a repository folder" else "Change repository folder") {
            checkoutPicker.launch(null)
        })
        val search = EditText(this).apply {
            hint = "Search portfolio"
            setSingleLine()
            setText(filter)
            setTextColor(android.graphics.Color.WHITE)
            setHintTextColor(android.graphics.Color.GRAY)
        }
        search.addTextChangedListener(SimpleTextWatcher { value ->
            filter = value
            showProducts()
        })
        content.addView(search)
        val list = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        content.addView(list)
        productList = list
        showProducts()
    }

    private var productList: LinearLayout? = null

    private fun showProducts() {
        val list = productList ?: return
        list.removeAllViews()
        PortfolioCatalog.search(catalog, filter).forEach { product ->
            val card = card()
            card.addView(label("${product.id} · ${product.name}", 17, "#EAF1FC", bold = true))
            card.addView(label("${product.version} · ${product.trl} · ${product.endpoint}", 12, "#80B9FF"))
            card.addView(label(product.description, 13, "#B8C6D9"))
            card.addView(button("Read product documentation") { openReadme(product) })
            list.addView(card)
        }
        if (list.childCount == 0) list.addView(label("No products match this search.", 14, "#A9B8CC"))
    }

    private fun renderEvidence() {
        content.addView(label(
            "Import selected text files or ZIP archives into private app storage. Imports are never extracted to shared storage, executed, or uploaded.",
            13, "#A9B8CC"
        ))
        content.addView(button("Choose evidence files or ZIP") {
            documentPicker.launch(arrayOf("*/*"))
        })
        content.addView(label("Supported text: TXT, Markdown, JSON, CSV, Python, Kotlin, Java, HTML, XML, YAML, TOML and logs.", 12, "#8FA2BB"))
        content.addView(label(
            "Limits: 500 files, 2 MiB per file, 8 MiB indexed text, 16 MiB expanded ZIP data. Index is local plaintext, not encrypted.",
            12, "#E4B86E"
        ))
        content.addView(button("Clear imported evidence") {
            AlertDialog.Builder(this)
                .setTitle("Remove local evidence?")
                .setMessage("This deletes Product 46's private evidence index. Original selected files are unchanged.")
                .setNegativeButton("Cancel", null)
                .setPositiveButton("Delete") { _, _ ->
                    if (library.clear()) {
                        selectedMatches = emptyList()
                        selectedQuestion = ""
                        searchResults = ""
                        toast("Local evidence index removed.")
                    } else {
                        toast("The local evidence index could not be removed.")
                    }
                    render()
                }
                .show()
        })
        val query = EditText(this).apply {
            hint = "Ask a question about imported evidence"
            setText(question)
            setTextColor(android.graphics.Color.WHITE)
            setHintTextColor(android.graphics.Color.GRAY)
            minLines = 2
        }
        query.addTextChangedListener(SimpleTextWatcher { question = it })
        content.addView(query)
        content.addView(button("Search local evidence") { searchEvidence() })
        if (searchResults.isNotBlank()) {
            content.addView(label(searchResults, 13, "#D1DCEC"))
            content.addView(button("Save as UNVERIFIED research note") {
                if (selectedQuestion != question) {
                    toast("The question changed. Run local evidence search again before saving.")
                    return@button
                }
                try {
                    notebook.add(question, selectedMatches)
                    toast("Research note saved locally.")
                    selectedTab = "Research"
                    render()
                } catch (error: Exception) {
                    toast(error.message ?: "Research note could not be saved.")
                }
            })
        }
    }

    private fun renderResearch() {
        content.addView(label(
            "Saved notes are device-local and explicitly UNVERIFIED. The app records retrieval evidence; it does not claim model-generated conclusions.",
            13, "#A9B8CC"
        ))
        content.addView(button("Export notebook") { exportPicker.launch("axiomzero-research-notes.md") })
        content.addView(button("Clear research notebook") {
            AlertDialog.Builder(this)
                .setTitle("Remove research notes?")
                .setMessage("This deletes Product 46's private notebook. Any exported copies are unchanged.")
                .setNegativeButton("Cancel", null)
                .setPositiveButton("Delete") { _, _ ->
                    if (notebook.clear()) toast("Research notebook removed.")
                    else toast("The research notebook could not be removed.")
                    render()
                }
                .show()
        })
        val notes = try {
            notebook.load()
        } catch (error: Exception) {
            content.addView(label("Notebook could not be read: ${error.message}", 13, "#FF938B"))
            return
        }
        if (notes.isEmpty()) {
            content.addView(label("No research notes saved yet.", 14, "#A9B8CC"))
        } else {
            notes.asReversed().forEach { note ->
                val card = card()
                card.addView(label(note.question, 16, "#EAF1FC", bold = true))
                card.addView(label(note.createdAt, 11, "#80B9FF"))
                card.addView(label(note.answer, 13, "#B8C6D9"))
                content.addView(card)
            }
        }
    }

    private fun importDocuments(uris: List<Uri>) {
        worker.execute {
            var imported = 0
            try {
                uris.forEach { uri -> imported += library.import(contentResolver, uri, displayName(uri)) }
                runOnUiThread {
                    toast("Indexed $imported new document(s).")
                    searchResults = ""
                    selectedMatches = emptyList()
                    selectedQuestion = ""
                    render()
                }
            } catch (error: Exception) {
                runOnUiThread {
                    val detail = error.message ?: "The selected files could not be indexed."
                    toast(if (imported == 0) detail else "Indexed $imported file(s) before stopping: $detail")
                }
            }
        }
    }

    private fun searchEvidence() {
        if (question.isBlank()) {
            toast("Enter a question or search phrase first.")
            return
        }
        val requestedQuestion = question
        worker.execute {
            try {
                val matches = library.search(requestedQuestion)
                val result = if (matches.isEmpty()) {
                    "UNVERIFIED — no matching local evidence was found."
                } else {
                    buildString {
                        appendLine("UNVERIFIED — ranked local keyword matches, not an AI-generated answer.")
                        matches.forEach { match ->
                            appendLine()
                            appendLine("[${match.name}:${match.line}] · score ${match.score}")
                            appendLine("SHA-256 ${match.sha256}")
                            appendLine(match.excerpt)
                        }
                    }
                }
                runOnUiThread {
                    if (question != requestedQuestion) {
                        toast("The question changed while searching. Search again to refresh results.")
                        return@runOnUiThread
                    }
                    selectedMatches = matches
                    selectedQuestion = requestedQuestion
                    searchResults = result
                    render()
                }
            } catch (error: Exception) {
                runOnUiThread { toast(error.message ?: "The local evidence search failed.") }
            }
        }
    }

    private fun openReadme(product: Product) {
        val rootUri = repositoryUri
        if (rootUri == null) {
            toast("Choose a repository folder first.")
            return
        }
        worker.execute {
            try {
                val root = DocumentFile.fromTreeUri(this, rootUri)
                    ?: throw IllegalStateException("The selected repository folder is unavailable.")
                val segments = product.folder.removeSuffix("/").split("/") + "README.md"
                val document = segments.fold(root) { parent, segment ->
                    parent.findFile(segment) ?: throw IllegalStateException("Could not find ${product.name}/$segment.")
                }
                require(document.isFile) { "Product documentation is not a file." }
                val text = contentResolver.openInputStream(document.uri)?.use { readTextBounded(it, 256 * 1024) }
                    ?: throw IllegalStateException("Android could not read this product's documentation.")
                runOnUiThread { showDocument(product.name, text) }
            } catch (error: Exception) {
                runOnUiThread { toast(error.message ?: "Product documentation could not be opened.") }
            }
        }
    }

    private fun exportNotebook(uri: Uri) {
        worker.execute {
            try {
                contentResolver.openOutputStream(uri, "wt")?.bufferedWriter()?.use {
                    it.write(notebook.exportMarkdown())
                } ?: throw IllegalStateException("Android could not create the selected export.")
                runOnUiThread { toast("Notebook exported to the selected destination.") }
            } catch (error: Exception) {
                runOnUiThread { toast(error.message ?: "Notebook export failed.") }
            }
        }
    }

    private fun displayName(uri: Uri): String {
        contentResolver.query(uri, arrayOf(OpenableColumns.DISPLAY_NAME), null, null, null)?.use { cursor ->
            if (cursor.moveToFirst()) {
                val index = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                if (index >= 0) return cursor.getString(index)
            }
        }
        return uri.lastPathSegment?.substringAfterLast('/') ?: "selected-document"
    }

    private fun readTextBounded(input: java.io.InputStream, maxBytes: Int): String {
        val output = ByteArrayOutputStream()
        val buffer = ByteArray(8192)
        while (true) {
            val count = input.read(buffer)
            if (count < 0) break
            require(output.size() + count <= maxBytes) { "Product README exceeds the 256 KiB display limit." }
            output.write(buffer, 0, count)
        }
        return output.toString(Charsets.UTF_8.name())
    }

    private fun showDocument(title: String, text: String) {
        val body = TextView(this).apply {
            this.text = text
            textSize = 14f
            setTextColor(android.graphics.Color.rgb(220, 228, 239))
            setPadding(dp(18), dp(12), dp(18), dp(12))
        }
        AlertDialog.Builder(this)
            .setTitle(title)
            .setView(ScrollView(this).apply { addView(body) })
            .setPositiveButton("Close", null)
            .show()
    }

    private fun card(): LinearLayout = LinearLayout(this).apply {
        orientation = LinearLayout.VERTICAL
        setPadding(dp(14), dp(12), dp(14), dp(14))
        setBackgroundColor(android.graphics.Color.rgb(18, 30, 48))
        val params = LinearLayout.LayoutParams(-1, -2).apply { setMargins(0, dp(8), 0, dp(4)) }
        layoutParams = params
    }

    private fun label(text: String, size: Int, color: String, bold: Boolean = false) =
        TextView(this).apply {
            this.text = text
            textSize = size.toFloat()
            setTextColor(android.graphics.Color.parseColor(color))
            if (bold) setTypeface(typeface, android.graphics.Typeface.BOLD)
            setPadding(0, dp(4), 0, dp(4))
            setTextIsSelectable(true)
        }

    private fun button(text: String, action: () -> Unit) = Button(this).apply {
        this.text = text
        isAllCaps = false
        setOnClickListener { action() }
    }

    private fun toast(text: String) = Toast.makeText(this, text, Toast.LENGTH_LONG).show()
    private fun dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()

    private class SimpleTextWatcher(private val changed: (String) -> Unit) :
        android.text.TextWatcher {
        override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) = Unit
        override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
            changed(s?.toString().orEmpty())
        }
        override fun afterTextChanged(s: android.text.Editable?) = Unit
    }
}
