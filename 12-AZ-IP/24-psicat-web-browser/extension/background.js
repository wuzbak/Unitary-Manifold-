async function getActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

async function captureActivePage() {
  const tab = await getActiveTab();
  if (!tab || !tab.id) return null;
  try {
    return await chrome.tabs.sendMessage(tab.id, { type: 'PSICAT_CAPTURE_PAGE' });
  } catch (_error) {
    return null;
  }
}

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'psicat-save-page',
    title: 'Save page to PsiCat Notebook',
    contexts: ['page'],
  });
});

chrome.contextMenus.onClicked.addListener(async (info) => {
  if (info.menuItemId !== 'psicat-save-page') return;
  const page = await captureActivePage();
  if (!page) return;
  const { notebook = [] } = await chrome.storage.local.get(['notebook']);
  notebook.unshift({
    id: crypto.randomUUID(),
    title: page.title,
    text: page.selection || page.text.slice(0, 2000),
    url: page.url,
    createdAt: new Date().toISOString(),
  });
  await chrome.storage.local.set({ notebook: notebook.slice(0, 100) });
});

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message && message.type === 'PSICAT_GET_ACTIVE_PAGE') {
    captureActivePage().then((page) => sendResponse(page || { title: 'Unavailable', url: '', text: '' }));
    return true;
  }
});
