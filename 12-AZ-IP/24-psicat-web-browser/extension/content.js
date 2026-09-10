chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message && message.type === 'PSICAT_CAPTURE_PAGE') {
    const text = document.body ? document.body.innerText.slice(0, 12000) : '';
    sendResponse({
      title: document.title,
      url: location.href,
      selection: String(window.getSelection ? window.getSelection() : '').trim(),
      text,
    });
  }
});
