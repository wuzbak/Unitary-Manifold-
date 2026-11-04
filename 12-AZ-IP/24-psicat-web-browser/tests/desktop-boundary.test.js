const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { isTrustedSender, isWebUrl } = require('../desktop/lib/desktop-boundary');

test('only the local desktop main frame can call privileged browser IPC', () => {
  const ui = path.resolve(__dirname, '../desktop/ui/index.html');
  const frame = { url: pathToFileURL(ui).href };
  const webContents = { mainFrame: frame };
  const window = { webContents, isDestroyed: () => false };
  const event = { sender: webContents, senderFrame: frame };
  assert.equal(isTrustedSender(event, window, ui), true);
  assert.equal(isTrustedSender({ ...event, sender: {} }, window, ui), false);
  assert.equal(isTrustedSender({ ...event, senderFrame: { url: frame.url } }, window, ui), false);
  frame.url = 'https://remote.example/';
  assert.equal(isTrustedSender(event, window, ui), false);
  frame.url = pathToFileURL(ui).href;
  assert.equal(isTrustedSender(event, null, ui), false);
  assert.equal(isTrustedSender(event, { ...window, isDestroyed: () => true }, ui), false);
});

test('external and popup URLs cannot invoke native protocols or local files', () => {
  for (const url of ['https://example.com', 'http://127.0.0.1:8327']) assert.equal(isWebUrl(url), true);
  for (const url of ['file:///C:/Suite/python.exe', 'javascript:alert(1)', 'ms-settings:privacy', 'shell:AppsFolder', 'not a URL']) {
    assert.equal(isWebUrl(url), false);
  }
});
