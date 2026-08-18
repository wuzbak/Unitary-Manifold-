package com.gibbernode.feature.audit

import android.content.Intent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Share
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.gibbernode.gibberwave.AuditLogEntity
import com.gibbernode.ui.GibberAmber
import com.gibbernode.ui.GibberBlue
import com.gibbernode.ui.GibberGreen
import com.gibbernode.ui.GibberRed
import com.gibbernode.ui.OnSurfaceDim
import com.gibbernode.ui.SurfaceDark
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * AuditScreen — Tab 4
 *
 * Shows:
 *  - Searchable, scrollable audit log backed by Room DB
 *  - RAG query input → Ollama answer card
 *  - Export (share) and Clear buttons
 */
@Composable
fun AuditScreen(viewModel: AuditViewModel = hiltViewModel()) {
    val entries      by viewModel.entries.collectAsStateWithLifecycle()
    val count        by viewModel.entryCount.collectAsStateWithLifecycle()
    val searchQuery  by viewModel.searchQuery.collectAsStateWithLifecycle()
    val ragAnswer    by viewModel.ragAnswer.collectAsStateWithLifecycle()
    val isQuerying   by viewModel.isQuerying.collectAsStateWithLifecycle()

    var ragInput      by remember { mutableStateOf("") }
    var showClearDialog by remember { mutableStateOf(false) }

    val context   = LocalContext.current
    val scope     = rememberCoroutineScope()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {

        // ── Header row ─────────────────────────────────────────────────────
        Row(
            modifier              = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment     = Alignment.CenterVertically,
        ) {
            Text(
                text  = "Audit Log ($count)",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurface,
                fontWeight = FontWeight.Bold,
            )
            Row {
                IconButton(onClick = {
                    scope.launch {
                        val jsonl = viewModel.exportAsJsonl()
                        val intent = Intent(Intent.ACTION_SEND).apply {
                            type     = "text/plain"
                            putExtra(Intent.EXTRA_TEXT, jsonl)
                            putExtra(Intent.EXTRA_SUBJECT, "Pentacorder audit log")
                        }
                        context.startActivity(Intent.createChooser(intent, "Export log"))
                    }
                }) {
                    Icon(Icons.Filled.Share, contentDescription = "Export", tint = GibberBlue)
                }
                IconButton(onClick = { showClearDialog = true }) {
                    Icon(Icons.Filled.Delete, contentDescription = "Clear", tint = GibberRed)
                }
            }
        }

        // ── Search field ───────────────────────────────────────────────────
        OutlinedTextField(
            value         = searchQuery,
            onValueChange = viewModel::onSearchChanged,
            placeholder   = { Text("Search payloads…") },
            leadingIcon   = { Icon(Icons.Filled.Search, contentDescription = null) },
            singleLine    = true,
            modifier      = Modifier.fillMaxWidth(),
        )

        // ── RAG query ──────────────────────────────────────────────────────
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier          = Modifier.fillMaxWidth(),
        ) {
            OutlinedTextField(
                value         = ragInput,
                onValueChange = { ragInput = it },
                placeholder   = { Text("Ask the AI about your logs…") },
                singleLine    = true,
                modifier      = Modifier.weight(1f),
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
                keyboardActions = KeyboardActions(onSend = {
                    viewModel.askRag(ragInput)
                    ragInput = ""
                }),
            )
            if (isQuerying) {
                CircularProgressIndicator(
                    modifier    = Modifier.padding(start = 8.dp).size(24.dp),
                    strokeWidth = 2.dp,
                )
            }
        }

        // ── RAG answer card ────────────────────────────────────────────────
        ragAnswer?.let { answer ->
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors   = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.tertiaryContainer.copy(alpha = 0.25f)
                ),
            ) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Row(
                        modifier              = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                    ) {
                        Text(
                            text  = "🤖 AI Answer",
                            style = MaterialTheme.typography.labelLarge,
                            color = GibberAmber,
                        )
                        TextButton(onClick = viewModel::dismissRagAnswer) {
                            Text("✕")
                        }
                    }
                    Text(
                        text  = answer,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurface,
                    )
                }
            }
        }

        // ── Log entries ────────────────────────────────────────────────────
        if (entries.isEmpty()) {
            Box(
                modifier         = Modifier.fillMaxSize().padding(top = 16.dp),
                contentAlignment = Alignment.TopCenter,
            ) {
                Text(
                    text  = if (searchQuery.isBlank()) "No audit entries yet."
                            else "No results for \"$searchQuery\".",
                    style = MaterialTheme.typography.bodySmall,
                    color = OnSurfaceDim,
                )
            }
        } else {
            LazyColumn(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                items(entries, key = { it.id }) { entry ->
                    AuditEntryRow(entry)
                }
            }
        }
    }

    // ── Clear confirmation dialog ──────────────────────────────────────────
    if (showClearDialog) {
        AlertDialog(
            onDismissRequest = { showClearDialog = false },
            title = { Text("Clear audit log?") },
            text  = { Text("This cannot be undone. All ${count} entries will be deleted.") },
            confirmButton = {
                TextButton(onClick = {
                    viewModel.clearLog()
                    showClearDialog = false
                }) { Text("Clear", color = GibberRed) }
            },
            dismissButton = {
                TextButton(onClick = { showClearDialog = false }) { Text("Cancel") }
            },
        )
    }
}

// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun AuditEntryRow(entry: AuditLogEntity) {
    val intentColor = when (entry.intent) {
        "ALERT"      -> GibberRed
        "RELAY"      -> GibberAmber
        "TELEMETRY"  -> GibberGreen
        "HANDSHAKE"  -> GibberBlue
        else         -> MaterialTheme.colorScheme.onSurface
    }
    val timeStr = SimpleDateFormat("MM-dd HH:mm:ss", Locale.US).format(Date(entry.timestamp))

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors   = CardDefaults.cardColors(containerColor = SurfaceDark),
    ) {
        Row(
            modifier          = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.Top,
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text  = entry.payload,
                    style = MaterialTheme.typography.bodySmall,
                    fontFamily = FontFamily.Monospace,
                    color = MaterialTheme.colorScheme.onSurface,
                    maxLines = 2,
                )
                Row(
                    modifier              = Modifier.fillMaxWidth().padding(top = 4.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    Text(
                        text  = entry.source,
                        style = MaterialTheme.typography.labelSmall,
                        color = OnSurfaceDim,
                    )
                    Text(
                        text  = entry.intent,
                        style = MaterialTheme.typography.labelSmall,
                        color = intentColor,
                        fontWeight = FontWeight.Bold,
                    )
                    Text(
                        text  = timeStr,
                        style = MaterialTheme.typography.labelSmall,
                        color = OnSurfaceDim,
                    )
                }
            }
            Text(
                text  = "%.0f%%".format(entry.confidence * 100),
                style = MaterialTheme.typography.labelSmall,
                color = OnSurfaceDim,
            )
        }
    }
}
