const TOPIC_CLASS_MAP = Object.freeze({
  "Foundation & Core Theory": "topic-foundation",
  "Particle Physics & Standard Model": "topic-particle",
  "Cosmology & Observation": "topic-cosmology",
  "Philosophy & Consciousness": "topic-philosophy",
  "AI, Ethics & Collaboration": "topic-ai",
  "Applied Domains": "topic-applied",
  "Mathematics & Formal Methods": "topic-math",
  "Open Science & Community": "topic-open",
  Books: "topic-books",
});

const SERIES_LABELS = Object.freeze({
  general: "General",
  thematic: "Thematic",
  epilog: "Epilog",
  book: "Books",
  s01: "Season 1",
  s02: "Season 2",
  s03: "Season 3",
});

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatWordCount(wordCount) {
  return `${Number(wordCount || 0).toLocaleString()} words`;
}

function prefersUSVoice(voice) {
  return /en-us/i.test(voice.lang || "");
}

function pleasantVoiceScore(voice) {
  const name = `${voice.name || ""} ${voice.voiceURI || ""}`.toLowerCase();
  let score = prefersUSVoice(voice) ? 100 : 0;
  if (/(samantha|ava|alloy|daniel|karen|serena|google us english|microsoft aria|microsoft guy|zira)/.test(name)) score += 20;
  if (voice.default) score += 10;
  return score;
}

export class ReaderIndex {
  constructor(indexUrl) {
    this.indexUrl = indexUrl;
    this.entries = [];
    this.filters = {
      topic: "All",
      series: "All",
      sort: "number",
      search: "",
    };
  }

  async load() {
    const response = await fetch(this.indexUrl, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Reader index failed to load (${response.status}).`);
    }
    this.entries = await response.json();
    return this.entries;
  }

  setFilter(key, value) {
    this.filters[key] = value;
  }

  getTopics() {
    return ["All", ...new Set(this.entries.map((entry) => entry.topic))];
  }

  getSeries() {
    const knownOrder = ["general", "s01", "s02", "s03", "thematic", "epilog", "book"];
    const present = new Set(this.entries.map((entry) => entry.series));
    return ["All", ...knownOrder.filter((series) => present.has(series))];
  }

  getFilteredEntries() {
    const search = this.filters.search.trim().toLowerCase();
    const filtered = this.entries.filter((entry) => {
      if (this.filters.topic !== "All" && entry.topic !== this.filters.topic) {
        return false;
      }
      if (this.filters.series !== "All" && entry.series !== this.filters.series) {
        return false;
      }
      if (!search) {
        return true;
      }
      const haystack = `${entry.title} ${entry.preview} ${entry.topic}`.toLowerCase();
      return haystack.includes(search);
    });

    filtered.sort((left, right) => {
      if (this.filters.sort === "title") {
        return left.title.localeCompare(right.title);
      }
      if (left.number !== right.number) {
        return left.number - right.number;
      }
      return left.title.localeCompare(right.title);
    });
    return filtered;
  }

  getById(id) {
    return this.entries.find((entry) => entry.id === id) || null;
  }

  getAdjacentEntry(activeId, direction) {
    const entries = this.getFilteredEntries();
    const index = entries.findIndex((entry) => entry.id === activeId);
    if (index < 0) {
      return entries[0] || null;
    }
    return entries[index + direction] || null;
  }

  static seriesLabel(series) {
    return SERIES_LABELS[series] || series;
  }

  static topicClass(topic) {
    return TOPIC_CLASS_MAP[topic] || "topic-foundation";
  }
}

export class MarkdownViewer {
  constructor({
    container,
    metaTitle,
    metaBadge,
    metaWordCount,
    metaSeries,
    openLink,
    loading,
    error,
  }) {
    this.container = container;
    this.metaTitle = metaTitle;
    this.metaBadge = metaBadge;
    this.metaWordCount = metaWordCount;
    this.metaSeries = metaSeries;
    this.openLink = openLink;
    this.loading = loading;
    this.error = error;
    this.currentEntry = null;
  }

  setLoading(isLoading) {
    this.loading.hidden = !isLoading;
  }

  showError(message) {
    this.error.hidden = false;
    this.error.textContent = message;
    this.container.innerHTML = "";
  }

  clearError() {
    this.error.hidden = true;
    this.error.textContent = "";
  }

  async loadEntry(entry) {
    this.currentEntry = entry;
    this.setLoading(true);
    this.clearError();
    this.updateMeta(entry);
    try {
      const response = await fetch(entry.path, { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`Unable to load markdown (${response.status}).`);
      }
      const markdown = await response.text();
      this.render(markdown);
    } catch (error) {
      this.showError(error.message || "Unable to load document.");
    } finally {
      this.setLoading(false);
    }
  }

  updateMeta(entry) {
    this.metaTitle.textContent = entry.title;
    this.metaBadge.textContent = entry.topic;
    this.metaBadge.className = `badge ${ReaderIndex.topicClass(entry.topic)}`;
    this.metaWordCount.textContent = formatWordCount(entry.word_count);
    this.metaSeries.textContent = ReaderIndex.seriesLabel(entry.series);
    this.openLink.href = entry.path;
    this.openLink.setAttribute("aria-label", `Open ${entry.title} in a new tab`);
  }

  render(markdown) {
    const normalized = this.prepareMarkdown(markdown);
    this.container.innerHTML = marked.parse(normalized, {
      breaks: false,
      gfm: true,
      headerIds: true,
      mangle: false,
    });
    this.renderBlockMath();
    this.renderInlineMath();
    this.decorateContent();
  }

  prepareMarkdown(markdown) {
    const placeholders = [];
    let working = markdown.replace(/```[\s\S]*?```/g, (match) => {
      const token = `@@UM_CODE_BLOCK_${placeholders.length}@@`;
      placeholders.push(match);
      return token;
    });

    working = working.replace(/`[^`\n]+`/g, (match) => {
      const token = `@@UM_INLINE_CODE_${placeholders.length}@@`;
      placeholders.push(match);
      return token;
    });

    working = working.replace(/\$\$([\s\S]+?)\$\$/g, (_, expression) => {
      const encoded = encodeURIComponent(expression.trim());
      return `\n<div class="um-reader-math-block" data-expression="${encoded}"></div>\n`;
    });

    working = working.replace(/@@UM_(?:CODE_BLOCK|INLINE_CODE)_(\d+)@@/g, (_, index) => placeholders[Number(index)] || "");
    return working;
  }

  renderBlockMath() {
    this.container.querySelectorAll(".um-reader-math-block").forEach((node) => {
      const expression = decodeURIComponent(node.dataset.expression || "");
      try {
        node.innerHTML = katex.renderToString(expression, {
          throwOnError: false,
          displayMode: true,
        });
      } catch {
        node.textContent = expression;
      }
    });
  }

  renderInlineMath() {
    const walker = document.createTreeWalker(this.container, NodeFilter.SHOW_TEXT, {
      acceptNode: (node) => {
        const parent = node.parentElement;
        if (!parent) return NodeFilter.FILTER_REJECT;
        if (parent.closest("pre, code, .katex, .um-reader-math-block")) return NodeFilter.FILTER_REJECT;
        return node.textContent.includes("$") ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      },
    });

    const textNodes = [];
    while (walker.nextNode()) {
      textNodes.push(walker.currentNode);
    }

    const inlinePattern = /\$([^$\n]+?)\$/g;
    textNodes.forEach((textNode) => {
      const text = textNode.textContent;
      if (!inlinePattern.test(text)) {
        inlinePattern.lastIndex = 0;
        return;
      }
      inlinePattern.lastIndex = 0;
      const fragment = document.createDocumentFragment();
      let cursor = 0;
      let match;
      while ((match = inlinePattern.exec(text)) !== null) {
        const before = text.slice(cursor, match.index);
        if (before) {
          fragment.appendChild(document.createTextNode(before));
        }
        const expression = match[1].trim();
        const span = document.createElement("span");
        span.className = "um-reader-inline-math";
        try {
          span.innerHTML = katex.renderToString(expression, {
            throwOnError: false,
            displayMode: false,
          });
        } catch {
          span.textContent = expression;
        }
        fragment.appendChild(span);
        cursor = match.index + match[0].length;
      }
      const tail = text.slice(cursor);
      if (tail) {
        fragment.appendChild(document.createTextNode(tail));
      }
      textNode.parentNode.replaceChild(fragment, textNode);
    });
  }

  decorateContent() {
    this.container.querySelectorAll("a").forEach((link) => {
      link.target = "_blank";
      link.rel = "noopener noreferrer";
    });
  }

  getSpeechBlocks() {
    const candidates = [...this.container.querySelectorAll("h1, h2, h3, h4, p, li, blockquote")];
    return candidates
      .map((element, index) => {
        element.dataset.ttsIndex = String(index);
        const clone = element.cloneNode(true);
        clone.querySelectorAll(".katex, pre, code, script, style").forEach((node) => node.remove());
        const text = clone.textContent.replace(/\s+/g, " ").trim();
        if (!text) {
          return null;
        }
        return { element, text, index };
      })
      .filter(Boolean);
  }

  setActiveSpeechElement(element) {
    this.clearSpeechHighlights();
    if (!element) {
      return;
    }
    element.classList.add("tts-active");
    element.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  clearSpeechHighlights() {
    this.container.querySelectorAll(".tts-active").forEach((node) => node.classList.remove("tts-active"));
  }
}

export class TTSController {
  constructor({
    playButton,
    pauseButton,
    stopButton,
    speedSlider,
    speedValue,
    voiceSelect,
    viewer,
  }) {
    this.playButton = playButton;
    this.pauseButton = pauseButton;
    this.stopButton = stopButton;
    this.speedSlider = speedSlider;
    this.speedValue = speedValue;
    this.voiceSelect = voiceSelect;
    this.viewer = viewer;
    this.synth = window.speechSynthesis;
    this.blocks = [];
    this.currentIndex = 0;
    this.isStopping = false;
    this.voices = [];
    this.rate = 0.95;
    this.pitch = 1.05;
    this.bindEvents();
    this.populateVoices();
    window.speechSynthesis?.addEventListener?.("voiceschanged", () => this.populateVoices());
  }

  bindEvents() {
    this.playButton.addEventListener("click", () => this.play());
    this.pauseButton.addEventListener("click", () => this.pauseOrResume());
    this.stopButton.addEventListener("click", () => this.stop());
    this.speedSlider.addEventListener("input", () => {
      this.rate = Number(this.speedSlider.value);
      this.speedValue.textContent = `${this.rate.toFixed(2)}×`;
      if (this.synth.speaking && !this.synth.paused) {
        this.restartCurrent();
      }
    });
    this.voiceSelect.addEventListener("change", () => {
      if (this.synth.speaking && !this.synth.paused) {
        this.restartCurrent();
      }
    });
  }

  populateVoices() {
    const voices = (this.synth?.getVoices?.() || []).slice().sort((a, b) => pleasantVoiceScore(b) - pleasantVoiceScore(a));
    this.voices = voices;
    const selectedVoiceName = this.voiceSelect.value;
    this.voiceSelect.innerHTML = voices
      .filter((voice) => prefersUSVoice(voice) || /en/i.test(voice.lang || ""))
      .map((voice) => `<option value="${escapeHtml(voice.name)}">${escapeHtml(voice.name)} (${escapeHtml(voice.lang)})</option>`)
      .join("");
    if (!this.voiceSelect.options.length) {
      this.voiceSelect.innerHTML = '<option value="">System default</option>';
      return;
    }
    const preferred = [...this.voiceSelect.options].find((option) => option.value === selectedVoiceName) || this.voiceSelect.options[0];
    preferred.selected = true;
  }

  getSelectedVoice() {
    const selected = this.voiceSelect.value;
    return this.voices.find((voice) => voice.name === selected) || this.voices[0] || null;
  }

  play() {
    if (!this.synth) {
      return;
    }
    if (this.synth.paused) {
      this.synth.resume();
      return;
    }
    if (this.synth.speaking) {
      return;
    }
    this.blocks = this.viewer.getSpeechBlocks();
    if (!this.blocks.length) {
      return;
    }
    this.currentIndex = 0;
    this.isStopping = false;
    this.speakCurrent();
  }

  pauseOrResume() {
    if (!this.synth?.speaking) {
      return;
    }
    if (this.synth.paused) {
      this.synth.resume();
      return;
    }
    this.synth.pause();
  }

  restartCurrent() {
    if (!this.blocks.length) {
      this.blocks = this.viewer.getSpeechBlocks();
    }
    if (!this.blocks.length) {
      return;
    }
    const wasSpeaking = this.synth.speaking;
    this.synth.cancel();
    if (wasSpeaking) {
      this.speakCurrent();
    }
  }

  speakCurrent() {
    if (!this.blocks[this.currentIndex]) {
      this.finish();
      return;
    }
    const block = this.blocks[this.currentIndex];
    const utterance = new SpeechSynthesisUtterance(block.text);
    utterance.rate = this.rate;
    utterance.pitch = this.pitch;
    utterance.voice = this.getSelectedVoice();
    utterance.onstart = () => {
      this.viewer.setActiveSpeechElement(block.element);
    };
    utterance.onend = () => {
      if (this.isStopping) {
        return;
      }
      this.currentIndex += 1;
      this.speakCurrent();
    };
    utterance.onerror = () => {
      this.currentIndex += 1;
      this.speakCurrent();
    };
    this.synth.speak(utterance);
  }

  stop() {
    if (!this.synth) {
      return;
    }
    this.isStopping = true;
    this.synth.cancel();
    this.finish();
  }

  finish() {
    this.currentIndex = 0;
    this.blocks = [];
    this.isStopping = false;
    this.viewer.clearSpeechHighlights();
  }
}

export class ReaderApp {
  constructor() {
    this.index = new ReaderIndex("../data/reader-index.json");
    this.viewer = new MarkdownViewer({
      container: document.getElementById("readerContent"),
      metaTitle: document.getElementById("readerTitle"),
      metaBadge: document.getElementById("readerTopicBadge"),
      metaWordCount: document.getElementById("readerWordCount"),
      metaSeries: document.getElementById("readerSeries"),
      openLink: document.getElementById("readerOpenLink"),
      loading: document.getElementById("readerLoading"),
      error: document.getElementById("readerError"),
    });
    this.tts = new TTSController({
      playButton: document.getElementById("ttsPlay"),
      pauseButton: document.getElementById("ttsPause"),
      stopButton: document.getElementById("ttsStop"),
      speedSlider: document.getElementById("ttsRate"),
      speedValue: document.getElementById("ttsRateValue"),
      voiceSelect: document.getElementById("ttsVoice"),
      viewer: this.viewer,
    });
    this.activeId = null;
    this.cacheElements();
  }

  cacheElements() {
    this.searchInput = document.getElementById("readerSearch");
    this.topicSelect = document.getElementById("readerTopicFilter");
    this.seriesSelect = document.getElementById("readerSeriesFilter");
    this.sortSelect = document.getElementById("readerSort");
    this.list = document.getElementById("readerList");
    this.count = document.getElementById("readerCount");
    this.sidebar = document.getElementById("readerSidebar");
    this.sidebarToggle = document.getElementById("readerSidebarToggle");
  }

  async init() {
    this.bindEvents();
    await this.index.load();
    this.populateFilters();
    this.renderList();
    const initialEntry = this.resolveInitialEntry();
    if (initialEntry) {
      await this.selectEntry(initialEntry.id, { fromHash: true });
    }
  }

  bindEvents() {
    this.searchInput.addEventListener("input", () => {
      this.index.setFilter("search", this.searchInput.value);
      this.renderList();
      this.syncActiveEntryAfterFilter();
    });
    this.topicSelect.addEventListener("change", () => {
      this.index.setFilter("topic", this.topicSelect.value);
      this.renderList();
      this.syncActiveEntryAfterFilter();
    });
    this.seriesSelect.addEventListener("change", () => {
      this.index.setFilter("series", this.seriesSelect.value);
      this.renderList();
      this.syncActiveEntryAfterFilter();
    });
    this.sortSelect.addEventListener("change", () => {
      this.index.setFilter("sort", this.sortSelect.value);
      this.renderList();
      this.syncActiveEntryAfterFilter();
    });
    this.sidebarToggle.addEventListener("click", () => {
      this.sidebar.classList.toggle("is-open");
    });
    window.addEventListener("hashchange", async () => {
      const hashId = window.location.hash.replace(/^#/, "");
      if (hashId && hashId !== this.activeId && this.index.getById(hashId)) {
        await this.selectEntry(hashId, { fromHash: true });
      }
    });
    document.addEventListener("keydown", async (event) => {
      const targetTag = event.target?.tagName;
      if (["INPUT", "SELECT", "TEXTAREA"].includes(targetTag)) {
        return;
      }
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        await this.moveSelection(-1);
      }
      if (event.key === "ArrowRight") {
        event.preventDefault();
        await this.moveSelection(1);
      }
    });
  }

  populateFilters() {
    this.topicSelect.innerHTML = this.index.getTopics().map((topic) => `<option value="${escapeHtml(topic)}">${escapeHtml(topic)}</option>`).join("");
    this.seriesSelect.innerHTML = this.index.getSeries().map((series) => `<option value="${escapeHtml(series)}">${escapeHtml(ReaderIndex.seriesLabel(series))}</option>`).join("");
  }

  resolveInitialEntry() {
    const hashId = window.location.hash.replace(/^#/, "");
    if (hashId) {
      return this.index.getById(hashId);
    }
    return this.index.getFilteredEntries()[0] || null;
  }

  renderList() {
    const entries = this.index.getFilteredEntries();
    this.count.textContent = `${entries.length} items`;
    if (!entries.length) {
      this.list.innerHTML = '<div class="reader-empty">No entries match your filters yet.</div>';
      return;
    }
    if (!entries.some((entry) => entry.id === this.activeId)) {
      this.activeId = entries[0].id;
    }
    this.list.innerHTML = entries.map((entry) => `
      <button class="reader-entry ${entry.id === this.activeId ? "is-active" : ""}" data-entry-id="${escapeHtml(entry.id)}">
        <div class="reader-entry-topline">
          <span class="reader-entry-title">${escapeHtml(entry.title)}</span>
          <span class="badge ${ReaderIndex.topicClass(entry.topic)}">${escapeHtml(entry.topic)}</span>
        </div>
        <div class="reader-entry-meta">
          <span>${escapeHtml(ReaderIndex.seriesLabel(entry.series))}</span>
          <span>${escapeHtml(formatWordCount(entry.word_count))}</span>
        </div>
        <div class="reader-entry-preview">${escapeHtml(entry.preview)}</div>
      </button>
    `).join("");
    this.list.querySelectorAll("[data-entry-id]").forEach((button) => {
      button.addEventListener("click", async () => this.selectEntry(button.dataset.entryId));
    });
  }

  syncActiveEntryAfterFilter() {
    const visibleEntry = this.index.getFilteredEntries().find((entry) => entry.id === this.activeId);
    if (!visibleEntry) {
      const firstEntry = this.index.getFilteredEntries()[0];
      if (firstEntry) {
        this.selectEntry(firstEntry.id);
      }
    }
  }

  async selectEntry(entryId, { fromHash = false } = {}) {
    const entry = this.index.getById(entryId);
    if (!entry) {
      return;
    }
    this.tts.stop();
    this.activeId = entry.id;
    this.renderList();
    await this.viewer.loadEntry(entry);
    if (!fromHash) {
      history.replaceState(null, "", `#${entry.id}`);
    }
    if (window.innerWidth <= 980) {
      this.sidebar.classList.remove("is-open");
    }
  }

  async moveSelection(direction) {
    const nextEntry = this.index.getAdjacentEntry(this.activeId, direction);
    if (nextEntry) {
      await this.selectEntry(nextEntry.id);
    }
  }
}

window.addEventListener("DOMContentLoaded", async () => {
  const app = new ReaderApp();
  try {
    await app.init();
  } catch (error) {
    const errorNode = document.getElementById("readerError");
    errorNode.hidden = false;
    errorNode.textContent = error.message || "Unable to initialize UM Reader.";
  }
});
