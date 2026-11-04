const { pathToFileURL } = require('node:url');

function isTrustedSender(event, window, uiEntry) {
  return Boolean(window && !window.isDestroyed()
    && event.sender === window.webContents
    && event.senderFrame === window.webContents.mainFrame
    && event.senderFrame.url === pathToFileURL(uiEntry).href);
}

function isWebUrl(value) {
  try {
    return ['http:', 'https:'].includes(new URL(value).protocol);
  } catch (_error) {
    return false;
  }
}

module.exports = { isTrustedSender, isWebUrl };
