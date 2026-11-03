const state = {
  campaignId: '',
  playerId: '',
  inviteCode: '',
};

const SESSION_KEY = 'psicat-dm-assistant.session';

function saveSession() {
  localStorage.setItem(SESSION_KEY, JSON.stringify(state));
}

function restoreSession() {
  try {
    const saved = JSON.parse(localStorage.getItem(SESSION_KEY) || '{}');
    state.campaignId = typeof saved.campaignId === 'string' ? saved.campaignId : '';
    state.playerId = typeof saved.playerId === 'string' ? saved.playerId : '';
    state.inviteCode = typeof saved.inviteCode === 'string' ? saved.inviteCode : '';
  } catch {
    localStorage.removeItem(SESSION_KEY);
  }
  if (state.inviteCode) document.getElementById('player-invite-code').value = state.inviteCode;
  if (state.campaignId) {
    document.getElementById('dm-state').textContent = 'Saved campaign session restored. Load its dashboard or choose another campaign.';
  }
  if (state.playerId) {
    document.getElementById('player-state').textContent = 'Saved player session restored. Load your campaign dashboard.';
  }
}

function setView(viewId) {
  for (const node of document.querySelectorAll('.view')) {
    node.classList.toggle('active', node.id === viewId);
  }
}

function output(payload) {
  document.getElementById('output').textContent = JSON.stringify(payload, null, 2);
}

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || `HTTP ${response.status}`);
  }
  return payload;
}

function characterPayloadFromForm(prefix) {
  const nameField = document.getElementById(`${prefix}-name`);
  const fallbackNameField = document.getElementById(`${prefix}-character-name`);
  return {
    name: (nameField && nameField.value) || (fallbackNameField && fallbackNameField.value) || 'Explorer',
    species: prefix === 'player' ? 'human' : 'elf',
    klass: document.getElementById(`${prefix}-class`).value,
    level: Number(document.getElementById(`${prefix}-level`).value || 1),
    background: 'adventurer',
    ability_scores: {
      strength: 10,
      dexterity: 14,
      constitution: 12,
      intelligence: 16,
      wisdom: 12,
      charisma: 10,
    },
    abilities: ['perception', 'initiative'],
  };
}

async function loadHealth() {
  output(await request('/api/health'));
}

async function createCampaign() {
  const payload = await request('/api/campaigns', {
    method: 'POST',
    body: JSON.stringify({
      name: document.getElementById('dm-campaign-name').value,
      setting: document.getElementById('dm-campaign-setting').value,
      dm_name: document.getElementById('dm-name').value,
      rules_edition: '5e-2024',
      tone: 'epic fantasy',
      summary: 'Shared table campaign controlled by Merlin.',
    }),
  });
  state.campaignId = payload.campaign.id;
  state.playerId = '';
  saveSession();
  await refreshCampaigns();
  document.getElementById('dm-campaign-select').value = state.campaignId;
  document.getElementById('dm-state').textContent = `Campaign ${payload.campaign.name} created.`;
  output(payload);
}

async function refreshCampaigns() {
  const { items } = await request('/api/campaigns');
  const select = document.getElementById('dm-campaign-select');
  const selectedId = state.campaignId || select.value;
  select.replaceChildren(new Option('Select a saved campaign', ''));
  for (const campaign of items) {
    select.add(new Option(`${campaign.name} — ${campaign.setting}`, campaign.id));
  }
  if (items.some((campaign) => campaign.id === selectedId)) select.value = selectedId;
  return items;
}

async function resumeCampaign() {
  const campaignId = document.getElementById('dm-campaign-select').value;
  if (!campaignId) throw new Error('Choose a saved campaign first.');
  state.campaignId = campaignId;
  state.playerId = '';
  saveSession();
  const dashboard = await request(`/api/campaigns/${campaignId}/dm-dashboard`);
  document.getElementById('dm-state').textContent = `Resumed campaign ${dashboard.campaign.name}.`;
  output(dashboard);
}

async function createInvite() {
  if (!state.campaignId) throw new Error('Create a campaign first.');
  const payload = await request(`/api/campaigns/${state.campaignId}/invite-codes`, {
    method: 'POST',
    body: JSON.stringify({ label: document.getElementById('dm-invite-label').value }),
  });
  state.inviteCode = payload.invite.code;
  saveSession();
  document.getElementById('player-invite-code').value = payload.invite.code;
  document.getElementById('dm-state').textContent = `Invite code ${payload.invite.code} ready for players.`;
  output(payload);
}

async function loadDmDashboard() {
  if (!state.campaignId) throw new Error('Create a campaign first.');
  output(await request(`/api/campaigns/${state.campaignId}/dm-dashboard`));
}

async function joinCampaign() {
  const payload = await request('/api/join-campaign', {
    method: 'POST',
    body: JSON.stringify({
      invite_code: document.getElementById('player-invite-code').value,
      display_name: document.getElementById('player-name').value,
      character: characterPayloadFromForm('player'),
    }),
  });
  state.campaignId = payload.campaign.id;
  state.playerId = payload.player.id;
  state.inviteCode = document.getElementById('player-invite-code').value;
  saveSession();
  document.getElementById('player-state').textContent = `Joined ${payload.campaign.name} as ${payload.player.display_name}.`;
  output(payload);
}

async function loadPlayerDashboard() {
  if (!state.campaignId || !state.playerId) throw new Error('Join a campaign first.');
  output(await request(`/api/campaigns/${state.campaignId}/player-dashboard?player_id=${encodeURIComponent(state.playerId)}`));
}

async function pushImage() {
  if (!state.campaignId) throw new Error('Create a campaign first.');
  output(await request(`/api/campaigns/${state.campaignId}/images`, {
    method: 'POST',
    body: JSON.stringify({
      title: document.getElementById('dm-image-title').value,
      image_url: document.getElementById('dm-image-url').value,
      caption: 'DM scene push',
      audience: 'all_players',
      tags: ['scene', 'map'],
    }),
  }));
}

async function addTreasure() {
  if (!state.campaignId) throw new Error('Create a campaign first.');
  output(await request(`/api/campaigns/${state.campaignId}/treasure`, {
    method: 'POST',
    body: JSON.stringify({
      title: document.getElementById('dm-treasure-title').value,
      gold: Number(document.getElementById('dm-treasure-gold').value || 0),
      items: ['ruby seal', 'signed warrant'],
      recipients: ['party'],
    }),
  }));
}

async function addPartyItem() {
  if (!state.campaignId) throw new Error('Create a campaign first.');
  output(await request(`/api/campaigns/${state.campaignId}/inventory`, {
    method: 'POST',
    body: JSON.stringify({
      name: document.getElementById('dm-item-name').value,
      owner_type: 'party',
      owner_id: 'party',
      quantity: 1,
      rarity: 'rare',
      kind: 'quest-item',
    }),
  }));
}

async function loadSoloDashboard() {
  output(await request('/api/player-dashboard/standalone', {
    method: 'POST',
    body: JSON.stringify({
      player_name: document.getElementById('solo-player-name').value,
      character: {
        ...characterPayloadFromForm('solo'),
        name: document.getElementById('solo-character-name').value,
        inventory: [{ name: 'Thieves\' Tools', owner_type: 'character', owner_id: 'solo', quantity: 1, kind: 'tool', rarity: 'common' }],
      },
    }),
  }));
}

for (const [id, handler] of Object.entries({
  'show-dm': () => setView('dm-view'),
  'show-player': () => setView('player-view'),
  'show-solo': () => setView('solo-view'),
  'load-health': loadHealth,
  'create-campaign': createCampaign,
  'create-invite': createInvite,
  'resume-campaign': resumeCampaign,
  'refresh-campaigns': refreshCampaigns,
  'load-dm-dashboard': loadDmDashboard,
  'join-campaign': joinCampaign,
  'load-player-dashboard': loadPlayerDashboard,
  'push-image': pushImage,
  'add-treasure': addTreasure,
  'add-party-item': addPartyItem,
  'load-solo-dashboard': loadSoloDashboard,
})) {
  document.getElementById(id)?.addEventListener('click', async () => {
    try {
      await handler();
    } catch (error) {
      output({ error: String(error.message || error) });
    }
  });
}

restoreSession();
refreshCampaigns().catch((error) => output({ error: String(error.message || error) }));
