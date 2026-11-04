const search = document.querySelector("#search");
const list = document.querySelector("#product-list");
const message = document.querySelector("#message");
const status = document.querySelector("#repository-status");
const disconnect = document.querySelector("#disconnect-repository");
const knowledgeCollections = document.querySelector("#knowledge-collections");
const knowledgeResults = document.querySelector("#knowledge-results");
const knowledgeQuery = document.querySelector("#knowledge-query");
const knowledgeMessage = document.querySelector("#knowledge-message");
let products = [];
let repositoryConnected = false;
let knowledgeBusy = false;
let knowledgeCollectionTotal = 0;

function showMessage(text) {
  message.textContent = text;
}

function showKnowledgeMessage(text) {
  knowledgeMessage.textContent = text;
}

function escapeText(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[character]);
}

function canOpenSurface(endpoint) {
  return /^https?:\/\/(?:localhost|127\.0\.0\.1)(?::\d{1,5})?(?:\/[^\s]*)?$/i.test(endpoint);
}

function render() {
  const query = search.value.trim().toLocaleLowerCase();
  const matches = products.filter((product) =>
    `${product.id} ${product.name} ${product.version} ${product.trl} ${product.endpoint} ${product.description}`
      .toLocaleLowerCase()
      .includes(query)
  );
  document.querySelector("#product-count").textContent = String(products.length);
  list.replaceChildren();
  if (matches.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "No products match this search.";
    list.append(empty);
    return;
  }
  for (const product of matches) {
    const card = document.createElement("article");
    card.className = "product-card";
    card.innerHTML = `
      <div class="product-title">
        <span class="product-number">#${escapeText(product.id)}</span>
        <h3>${escapeText(product.name)}</h3>
      </div>
      <p class="meta">${escapeText(product.version)} · ${escapeText(product.trl)} · ${escapeText(product.endpoint)}</p>
      <p class="product-description">${escapeText(product.description)}</p>
      <div class="product-actions">
        <button data-action="folder" data-id="${escapeText(product.id)}" ${repositoryConnected ? "" : "disabled"}>Open folder</button>
        <button data-action="readme" data-id="${escapeText(product.id)}" ${repositoryConnected ? "" : "disabled"}>Read guide</button>
        ${canOpenSurface(product.endpoint) ? `<button data-action="surface" data-id="${escapeText(product.id)}">Open local service</button>` : ""}
      </div>`;
    list.append(card);
  }
}

async function runAction(action) {
  showMessage("");
  try {
    const state = await window.axiomSuite.getState();
    if (action.type === "connect") {
      const result = await window.axiomSuite.connectRepository();
      if (!result.canceled) {
        updateState({ ...state, repositoryRoot: result.repositoryRoot });
      }
    } else if (action.type === "disconnect") {
      updateState(await window.axiomSuite.disconnectRepository());
    } else if (action.type === "workspace") {
      await window.axiomSuite.openWorkspace();
    } else if (action.type === "folder") {
      await window.axiomSuite.openProductFolder(action.id);
    } else if (action.type === "readme") {
      await window.axiomSuite.openProductReadme(action.id);
    } else if (action.type === "surface") {
      await window.axiomSuite.openProductSurface(action.id);
    } else if (action.type === "psicat") {
      await window.axiomSuite.openPsiCat();
    } else if (action.type === "legal") {
      await window.axiomSuite.openLegalNotices();
    } else if (action.type === "category") {
      await window.axiomSuite.openIpCategory(action.category);
    }
  } catch (error) {
    showMessage(error.message || "The requested action failed.");
  }
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function renderKnowledgeCollections(collections) {
  knowledgeCollectionTotal = collections.length;
  document.querySelector("#knowledge-count").textContent =
    `${collections.length} collection${collections.length === 1 ? "" : "s"}`;
  knowledgeCollections.replaceChildren();
  for (const collection of collections) {
    const card = document.createElement("article");
    card.className = "knowledge-card";
    const name = document.createElement("h3");
    name.textContent = collection.name;
    const summary = document.createElement("p");
    summary.textContent =
      `${collection.sourceType === "zip" ? "ZIP archive" : "Folder"} · ` +
      `${collection.indexedTextFiles} text files indexed · ${collection.totalFiles} files considered · ` +
      `${formatBytes(collection.textBytes)} searchable text`;
    const skips = document.createElement("p");
    skips.className = "knowledge-skips";
    skips.textContent =
      `${collection.unsupportedFiles} unsupported · ${collection.oversizedFiles} over 8 MiB · ` +
      `${collection.textLimitFiles} over text limit · ${collection.unreadableFiles} unreadable · ` +
      `${collection.symlinksSkipped} links skipped · ` +
      `${collection.excludedDirectories} excluded directories`;
    if (collection.truncated) {
      skips.textContent += " · scan stopped at an entry or depth limit";
    }
    const importDetails = document.createElement("details");
    const detailsSummary = document.createElement("summary");
    detailsSummary.textContent =
      `Skipped-file details (${collection.skippedFiles.length + collection.omittedSkippedFiles} listed)`;
    importDetails.append(detailsSummary);
    if (collection.skippedFiles.length > 0) {
      const skippedList = document.createElement("ul");
      for (const skippedFile of collection.skippedFiles) {
        const item = document.createElement("li");
        const reason = skippedFile.status === "oversized"
          ? "over 8 MiB"
          : skippedFile.status === "text-limit"
            ? "collection text limit reached"
            : skippedFile.status === "unreadable"
              ? "unreadable"
              : skippedFile.status === "symlink"
                ? "link skipped"
                : "unsupported format or encoding";
        item.textContent = `${reason} · ${skippedFile.path} · ${formatBytes(skippedFile.sizeBytes)}`;
        skippedList.append(item);
      }
      importDetails.append(skippedList);
    } else {
      const noSkips = document.createElement("p");
      noSkips.textContent = "No skipped text files.";
      importDetails.append(noSkips);
    }
    if (collection.omittedSkippedFiles > 0) {
      const omitted = document.createElement("p");
      omitted.textContent = `${collection.omittedSkippedFiles} additional skipped files are not shown here.`;
      importDetails.append(omitted);
    }
    const actions = document.createElement("div");
    actions.className = "knowledge-card-actions";
    for (const [action, label] of [["refresh", "Refresh"], ["remove", "Remove index"]]) {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.action = action;
      button.dataset.id = collection.id;
      button.textContent = label;
      button.disabled = knowledgeBusy;
      actions.append(button);
    }
    card.append(name, summary, skips, importDetails, actions);
    knowledgeCollections.append(card);
  }
  const searchButton = document.querySelector("#knowledge-search-form button");
  searchButton.disabled = knowledgeBusy || collections.length === 0;
  if (collections.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "No local sources yet. Import the Webspace seed or PsiCat Mind ZIP to begin.";
    knowledgeCollections.append(empty);
  }
}

function renderKnowledgeResults(result) {
  knowledgeResults.replaceChildren();
  const heading = document.createElement("p");
  heading.className = "knowledge-result-count";
  heading.textContent = result.totalMatches === 0
    ? "No matching evidence found in the indexed text."
    : `Showing ${result.results.length} of ${result.totalMatches} matching files.`;
  knowledgeResults.append(heading);
  for (const match of result.results) {
    const card = document.createElement("article");
    card.className = "evidence-card";
    const citation = document.createElement("p");
    citation.className = "evidence-citation";
    citation.textContent = `${match.collectionName} · ${match.citation}`;
    const excerpt = document.createElement("pre");
    excerpt.textContent = match.excerpt;
    const hash = document.createElement("details");
    const summary = document.createElement("summary");
    summary.textContent = "Source SHA-256";
    const digest = document.createElement("code");
    digest.textContent = match.sha256;
    hash.append(summary, digest);
    card.append(citation, excerpt, hash);
    knowledgeResults.append(card);
  }
}

function updateKnowledgeControls() {
  const panel = document.querySelector(".knowledge");
  panel.setAttribute("aria-busy", String(knowledgeBusy));
  panel.querySelectorAll("button, input").forEach((control) => {
    control.disabled = knowledgeBusy ||
      (control.id === "knowledge-search-button" && knowledgeCollectionTotal === 0);
  });
}

async function runKnowledgeAction(action) {
  if (knowledgeBusy) return;
  knowledgeBusy = true;
  updateKnowledgeControls();
  showKnowledgeMessage("");
  const knowledgePanel = document.querySelector(".knowledge");
  if (action === "import-folder" || action === "import-zip") {
    showKnowledgeMessage("Indexing the selected source locally...");
  } else if (action.startsWith("refresh:")) {
    showKnowledgeMessage("Refreshing the local evidence index...");
  }
  if (action === "import-folder" || action === "import-zip" || action.startsWith("refresh:")) {
    knowledgeResults.replaceChildren();
  }
  try {
    let result;
    if (action === "import-folder") {
      result = await window.axiomSuite.importKnowledgeFolder();
    } else if (action === "import-zip") {
      result = await window.axiomSuite.importKnowledgeZip();
    } else if (action === "search") {
      knowledgeResults.replaceChildren();
      renderKnowledgeResults(await window.axiomSuite.searchKnowledge(knowledgeQuery.value));
      return;
    } else if (action.startsWith("refresh:")) {
      result = { collections: await window.axiomSuite.refreshKnowledge(action.slice(8)) };
    } else if (action.startsWith("remove:")) {
      result = await window.axiomSuite.removeKnowledge(action.slice(7));
    }
    if (result?.canceled) {
      showKnowledgeMessage("");
      return;
    }
    if (result?.collections) renderKnowledgeCollections(result.collections);
    if (action === "import-folder" || action === "import-zip") {
      const added = result.collections.at(-1);
      const skipped =
        added.unsupportedFiles + added.oversizedFiles + added.textLimitFiles +
        added.unreadableFiles + added.symlinksSkipped;
      showKnowledgeMessage(
        `Indexed ${added.indexedTextFiles} text files from ${added.name}. ` +
        `${skipped} files or links were not searched.`
      );
    }
    if (action.startsWith("refresh:")) showKnowledgeMessage("Local evidence index refreshed.");
    if (action.startsWith("remove:")) knowledgeResults.replaceChildren();
  } catch (error) {
    showKnowledgeMessage(error.message || "The local knowledge action failed.");
  } finally {
    knowledgeBusy = false;
    updateKnowledgeControls();
  }
}

function updateState(state) {
  repositoryConnected = Boolean(state.repositoryRoot);
  status.textContent = state.repositoryRoot
    ? state.repositoryRoot
    : "Not connected. Select a repository checkout to open its apps and documentation.";
  disconnect.hidden = !repositoryConnected;
  render();
}

async function loadCatalog() {
  const [catalog, state] = await Promise.all([
    window.axiomSuite.getProducts(),
    window.axiomSuite.getState()
  ]);
  products = catalog;
  if (!Array.isArray(products) || products.length < 1) {
    throw new Error("The product catalog is empty.");
  }
  render();
  updateState(state);
  try {
    renderKnowledgeCollections(await window.axiomSuite.listKnowledge());
  } catch (error) {
    showKnowledgeMessage(`The local evidence library could not be loaded: ${error.message}`);
  }
}

search.addEventListener("input", render);
document.querySelector("#import-knowledge-folder").addEventListener("click", () =>
  runKnowledgeAction("import-folder")
);
document.querySelector("#import-knowledge-zip").addEventListener("click", () =>
  runKnowledgeAction("import-zip")
);
document.querySelector("#knowledge-search-form").addEventListener("submit", (event) => {
  event.preventDefault();
  runKnowledgeAction("search");
});
knowledgeCollections.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  runKnowledgeAction(`${button.dataset.action}:${button.dataset.id}`);
});
document.querySelector("#connect-repository").addEventListener("click", () => runAction({ type: "connect" }));
disconnect.addEventListener("click", () => runAction({ type: "disconnect" }));
document.querySelector("#open-workspace").addEventListener("click", () => runAction({ type: "workspace" }));
document.querySelector("#open-psicat").addEventListener("click", () => runAction({ type: "psicat" }));
document.querySelector("#open-legal").addEventListener("click", () => runAction({ type: "legal" }));
document.querySelectorAll("[data-category]").forEach((button) => {
  button.addEventListener("click", () => runAction({ type: "category", category: button.dataset.category }));
});
list.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (button && !button.disabled) {
    runAction({ type: button.dataset.action, id: button.dataset.id });
  }
});

loadCatalog().catch((error) => showMessage(error.message || "The suite could not start."));
