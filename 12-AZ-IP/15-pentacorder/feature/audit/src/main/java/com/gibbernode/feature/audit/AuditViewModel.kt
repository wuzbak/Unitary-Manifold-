package com.gibbernode.feature.audit

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gibbernode.gibberwave.AuditLogDao
import com.gibbernode.gibberwave.AuditLogEntity
import com.gibbernode.gibberwave.IntentEngine
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.FlowPreview
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.debounce
import kotlinx.coroutines.flow.flatMapLatest
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

@OptIn(FlowPreview::class, ExperimentalCoroutinesApi::class)
@HiltViewModel
class AuditViewModel @Inject constructor(
    private val dao: AuditLogDao,
    private val intentEngine: IntentEngine,
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    /** Live list of log entries — reactive to search query changes. */
    val entries: StateFlow<List<AuditLogEntity>> = _searchQuery
        .debounce(300)
        .flatMapLatest { query ->
            if (query.isBlank()) dao.allEntries() else dao.search(query)
        }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    val entryCount: StateFlow<Int> = dao.count()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), 0)

    private val _ragAnswer = MutableStateFlow<String?>(null)
    val ragAnswer: StateFlow<String?> = _ragAnswer.asStateFlow()

    private val _isQuerying = MutableStateFlow(false)
    val isQuerying: StateFlow<Boolean> = _isQuerying.asStateFlow()

    fun onSearchChanged(query: String) {
        _searchQuery.update { query }
    }

    fun clearLog() {
        viewModelScope.launch { dao.clear() }
    }

    /**
     * Send [question] to the local Ollama RAG endpoint.
     * Emits the response to [ragAnswer].
     */
    fun askRag(question: String) {
        if (question.isBlank()) return
        viewModelScope.launch {
            _isQuerying.value = true
            _ragAnswer.value  = null
            _ragAnswer.value  = intentEngine.ask(question)
            _isQuerying.value = false
        }
    }

    fun dismissRagAnswer() {
        _ragAnswer.value = null
    }

    /**
     * Export audit log as a JSONL string (caller handles share intent / file write).
     */
    suspend fun exportAsJsonl(): String =
        entries.value.joinToString("\n") { entry ->
            """{"id":"${entry.id}","ts":${entry.timestamp},"source":"${entry.source}","intent":"${entry.intent}","payload":${escapeJson(entry.payload)},"confidence":${entry.confidence}}"""
        }

    private fun escapeJson(s: String): String = "\"${s.replace("\\", "\\\\").replace("\"", "\\\"")}\""
}
