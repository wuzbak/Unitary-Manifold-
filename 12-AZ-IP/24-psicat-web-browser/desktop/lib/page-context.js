function normalizeText(text) {
  return String(text || '').replace(/\s+/g, ' ').trim();
}

function collectKeySentences(text, limit = 4) {
  const normalized = normalizeText(text);
  if (!normalized) return [];
  return normalized
    .split(/(?<=[.!?])\s+/)
    .map((sentence) => sentence.trim())
    .filter((sentence) => sentence.length > 32)
    .sort((a, b) => b.length - a.length)
    .slice(0, limit);
}

function summarizeSnapshot(snapshot) {
  if (!snapshot) return null;
  const text = normalizeText(snapshot.text || snapshot.selection || '');
  const bullets = collectKeySentences(text, 3);
  return {
    title: snapshot.title || 'Untitled page',
    url: snapshot.url || '',
    bullets,
    excerpt: text.slice(0, 600),
  };
}

function scoreMatch(text, query) {
  const haystack = normalizeText(text).toLowerCase();
  const needles = normalizeText(query).toLowerCase().split(/\s+/).filter(Boolean);
  return needles.reduce((score, needle) => score + (haystack.includes(needle) ? 1 : 0), 0);
}

function searchResearchCorpus(corpus, query) {
  const items = Array.isArray(corpus) ? corpus : [];
  return items
    .map((item) => ({ item, score: scoreMatch(`${item.title || ''} ${item.text || item.excerpt || ''}`, query) }))
    .filter((row) => row.score > 0)
    .sort((a, b) => b.score - a.score)
    .map((row) => row.item);
}

function buildContextEnvelope(state) {
  const tabs = Array.isArray(state.tabs) ? state.tabs : [];
  const activeTab = tabs.find((tab) => tab.id === state.activeTabId) || tabs[0] || null;
  const currentPage = summarizeSnapshot(activeTab && activeTab.lastSnapshot ? activeTab.lastSnapshot : activeTab);
  const rememberedPages = (state.rememberedPages || []).slice(0, 8).map(summarizeSnapshot).filter(Boolean);
  const notebookEntries = (state.notebookEntries || []).slice(0, 12).map((entry) => ({
    title: entry.title,
    text: normalizeText(entry.text).slice(0, 1200),
    tags: entry.tags || [],
  }));
  const importedResearch = (state.importedResearch || []).slice(0, 12).map((entry) => ({
    title: entry.title,
    text: normalizeText(entry.text).slice(0, 1200),
    source: entry.source,
  }));
  return {
    current_page: currentPage,
    remembered_pages: rememberedPages,
    notebook_entries: notebookEntries,
    imported_research: importedResearch,
  };
}

function summarizeResearchBundle({ question = '', state }) {
  const envelope = buildContextEnvelope(state || {});
  const sections = [];
  if (envelope.current_page) {
    sections.push(`Current page: ${envelope.current_page.title} (${envelope.current_page.url})`);
    if (envelope.current_page.bullets.length) sections.push(`Current findings: ${envelope.current_page.bullets.join(' | ')}`);
  }
  if (envelope.remembered_pages.length) {
    sections.push(`Remembered pages: ${envelope.remembered_pages.map((item) => item.title).join('; ')}`);
  }
  if (envelope.notebook_entries.length) {
    sections.push(`Notebook topics: ${envelope.notebook_entries.map((item) => item.title).join('; ')}`);
  }
  if (envelope.imported_research.length) {
    sections.push(`Imported sources: ${envelope.imported_research.map((item) => item.title).join('; ')}`);
  }
  if (question) {
    const corpus = [
      ...(envelope.remembered_pages || []),
      ...(envelope.notebook_entries || []),
      ...(envelope.imported_research || []),
    ];
    const matches = searchResearchCorpus(corpus, question).slice(0, 5);
    if (matches.length) sections.push(`Best local matches: ${matches.map((item) => item.title).join('; ')}`);
  }
  return sections.join('\n');
}

module.exports = {
  normalizeText,
  collectKeySentences,
  summarizeSnapshot,
  searchResearchCorpus,
  buildContextEnvelope,
  summarizeResearchBundle,
};
