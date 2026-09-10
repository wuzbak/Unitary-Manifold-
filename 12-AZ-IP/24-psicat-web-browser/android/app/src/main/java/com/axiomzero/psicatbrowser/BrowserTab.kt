package com.axiomzero.psicatbrowser

data class BrowserTab(
    val id: String,
    var title: String,
    var url: String,
    val isPrivate: Boolean = false,
    var lastSnapshot: PageSnapshot? = null,
)

data class PageSnapshot(
    val title: String,
    val url: String,
    val selection: String,
    val text: String,
    val capturedAt: String,
)

data class NotebookEntry(
    val title: String,
    val text: String,
    val createdAt: String,
)
