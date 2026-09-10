function shouldUseBackendSync(state) {
  const sync = state?.sync || {};
  return sync.mode !== 'local-only' && Boolean(sync.accountEmail);
}

module.exports = {
  shouldUseBackendSync,
};
