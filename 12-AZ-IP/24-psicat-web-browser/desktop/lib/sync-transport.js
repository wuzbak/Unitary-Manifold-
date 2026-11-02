async function pushSyncToBackend({ state, endpoint, core, fetchImpl = fetch }) {
  if (!state.sync.accountEmail) throw new Error('Sync account email is required before backend sync.');
  if (!state.settings.syncAccessToken) throw new Error('Sync access token is required before backend sync.');
  const packet = core.createSyncPacket(state);
  const response = await fetchImpl(`${endpoint}/api/sync/push`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Sync-Token': state.settings.syncAccessToken,
    },
    body: JSON.stringify({
      account_email: state.sync.accountEmail,
      packet,
    }),
  });
  if (!response.ok) throw new Error(`Sync push failed with status ${response.status}`);
  const payload = await response.json();
  const nextState = core.normalizeState({
    ...state,
    sync: {
      ...state.sync,
      lastSyncAt: payload.updated_at || packet.exportedAt,
      lastSyncSource: 'backend-push',
    },
  });
  return { payload, state: nextState };
}

async function pullSyncFromBackend({ state, endpoint, core, fetchImpl = fetch }) {
  if (!state.sync.accountEmail) throw new Error('Sync account email is required before backend sync.');
  if (!state.settings.syncAccessToken) throw new Error('Sync access token is required before backend sync.');
  const response = await fetchImpl(`${endpoint}/api/sync/pull?account_email=${encodeURIComponent(state.sync.accountEmail)}`, {
    headers: {
      'X-Sync-Token': state.settings.syncAccessToken,
    },
  });
  if (response.status === 404) throw new Error('No backend sync packet found for this account.');
  if (!response.ok) throw new Error(`Sync pull failed with status ${response.status}`);
  const payload = await response.json();
  const nextState = core.mergeSyncPacket(state, payload.packet || {});
  return {
    payload,
    state: core.normalizeState({
      ...nextState,
      sync: {
        ...nextState.sync,
        lastSyncAt: payload.updated_at || new Date().toISOString(),
        lastSyncSource: 'backend-pull',
      },
    }),
  };
}

module.exports = { pushSyncToBackend, pullSyncFromBackend };
