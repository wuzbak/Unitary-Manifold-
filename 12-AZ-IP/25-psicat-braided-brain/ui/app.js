const core = window.PsiCatBraidedBrainCore;
const STORAGE_KEY = 'psicat-braided-brain-state-v1';
const DEFAULT_COACH_ENDPOINT = 'http://127.0.0.1:8020/api/psicat';

let campaign = loadCampaign();
let touchStart = null;

function byId(id) {
  return document.getElementById(id);
}

function loadCampaign() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return core.createCampaignState();
    const parsed = JSON.parse(raw);
    if (!parsed || !parsed.current || !parsed.version) return core.createCampaignState();
    return parsed;
  } catch (_error) {
    return core.createCampaignState();
  }
}

function saveCampaign() {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(campaign));
}

function statusTone(value) {
  if (value >= 75) return 'stable';
  if (value >= 45) return 'tense';
  return 'critical';
}

function renderBoard() {
  const board = byId('board');
  const state = campaign.current;
  board.innerHTML = '';
  board.style.setProperty('--cols', state.width);
  for (let y = 0; y < state.height; y += 1) {
    for (let x = 0; x < state.width; x += 1) {
      const button = document.createElement('button');
      const role = core.getCellRole(state, x, y);
      button.className = `cell ${role}`;
      button.dataset.x = String(x);
      button.dataset.y = String(y);
      button.type = 'button';
      button.setAttribute('aria-label', `Cell ${x + 1}, ${y + 1}, ${role}`);
      button.textContent = role === 'player' ? '🐈' : role === 'signal' ? '✦' : role === 'target' ? '◎' : role === 'target-complete' ? '◉' : role === 'hazard' ? '≈' : '·';
      board.appendChild(button);
    }
  }
}

function renderLevelSelector() {
  const wrap = byId('level-selector');
  wrap.innerHTML = '';
  core.getLevelDeck().forEach((level, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `level-pill ${campaign.currentLevelIndex === index ? 'active' : ''}`;
    if (index > campaign.unlockedLevelIndex) button.disabled = true;
    button.textContent = `${index + 1}. ${level.shortLabel}`;
    button.addEventListener('click', () => {
      campaign = core.jumpToLevel(campaign, index);
      persistAndRender();
    });
    wrap.appendChild(button);
  });
}

function renderTargets() {
  const wrap = byId('target-list');
  wrap.innerHTML = '';
  campaign.current.targets.forEach((target) => {
    const item = document.createElement('div');
    item.className = 'mini-card';
    item.innerHTML = `<strong>${target.label}</strong><span>${target.delivered ? 'Delivered' : 'Awaiting ' + target.kind}</span><small>${target.scientificNote}</small>`;
    wrap.appendChild(item);
  });
}

function renderSignals() {
  const wrap = byId('signal-list');
  wrap.innerHTML = '';
  const carried = document.createElement('div');
  carried.className = 'mini-card carried';
  carried.innerHTML = `<strong>Carried signal</strong><span>${campaign.current.carriedSignal ? campaign.current.carriedSignal.label : 'None'}</span>`;
  wrap.appendChild(carried);
  campaign.current.signals.forEach((signal) => {
    const item = document.createElement('div');
    item.className = 'mini-card';
    item.innerHTML = `<strong>${signal.label}</strong><span>${signal.kind}</span>`;
    wrap.appendChild(item);
  });
}

function renderChallenge() {
  const wrap = byId('challenge-panel');
  wrap.innerHTML = '';
  const active = campaign.current.activeChallenge;
  if (!active) {
    wrap.innerHTML = '<p class="muted">Deliver a signal to unlock a science check.</p>';
    return;
  }
  const title = document.createElement('h3');
  title.textContent = active.label;
  const prompt = document.createElement('p');
  prompt.textContent = active.prompt;
  const source = document.createElement('p');
  source.className = 'muted';
  source.textContent = `Source: ${active.source}`;
  wrap.append(title, prompt, source);
  active.choices.forEach((choice) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'choice';
    button.textContent = choice.label;
    button.addEventListener('click', () => {
      campaign = core.answerChallenge(campaign, choice.id);
      persistAndRender();
    });
    wrap.appendChild(button);
  });
}

function renderLogs() {
  byId('mission-log').innerHTML = campaign.current.missionLog.map((item) => `<li>${item}</li>`).join('');
  byId('science-log').innerHTML = campaign.current.scienceLog.map((item) => `<li>${item}</li>`).join('');
}

function renderTrainingPacket() {
  byId('training-packet').textContent = JSON.stringify(core.createTrainingPacket(campaign), null, 2);
}

function renderCoachStatus(text) {
  byId('coach-output').textContent = text;
}

function renderState() {
  const state = campaign.current;
  const level = core.LEVELS[campaign.currentLevelIndex];
  byId('title').textContent = 'PsiCat Braided Brain';
  byId('subtitle').textContent = 'A toroidal brain simulator game for desktop and mobile.';
  byId('level-name').textContent = level.name;
  byId('briefing').textContent = state.briefing;
  byId('source-note').textContent = level.sourceNote;
  byId('score').textContent = String(campaign.totalScore + state.score);
  byId('coherence').textContent = `${state.coherence}%`;
  byId('coherence').dataset.tone = statusTone(state.coherence);
  byId('wraps').textContent = `${state.wraps}/${state.wrapGoal}`;
  byId('moves').textContent = String(state.movesLeft);
  byId('completed-levels').textContent = `${campaign.completedLevelIds.length}/${core.LEVELS.length}`;
  byId('privacy-note').textContent = 'Local progress only unless you explicitly export a training packet.';
  byId('coach-endpoint').value = byId('coach-endpoint').value || DEFAULT_COACH_ENDPOINT;
  renderBoard();
  renderLevelSelector();
  renderTargets();
  renderSignals();
  renderChallenge();
  renderLogs();
  renderTrainingPacket();

  const summary = [];
  if (state.completed) summary.push('Level complete. Advance when ready.');
  if (state.failed) summary.push('Mission failed. Reset the braid to try again.');
  if (!summary.length) summary.push('Collect signals, wrap the board, and deliver them to matching science targets.');
  byId('status-banner').textContent = summary.join(' ');
  byId('advance-level').disabled = !state.completed || campaign.currentLevelIndex === core.LEVELS.length - 1;
}

function persistAndRender() {
  saveCampaign();
  renderState();
}

function move(dx, dy) {
  campaign = core.movePlayer(campaign, dx, dy);
  persistAndRender();
}

function downloadText(filename, text, contentType = 'application/json') {
  const blob = new Blob([text], { type: contentType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

async function askCoach() {
  const endpoint = byId('coach-endpoint').value.trim() || DEFAULT_COACH_ENDPOINT;
  const playerPrompt = byId('coach-input').value.trim();
  const query = playerPrompt || core.suggestCoachQuery(campaign);
  renderCoachStatus('PsiCat coach is thinking…');
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        page_context: campaign.current.briefing,
        user_context: JSON.stringify(core.createTrainingPacket(campaign)),
      }),
    });
    let payload;
    if (response.ok) {
      payload = await response.json();
    } else {
      const errorText = await response.text();
      throw new Error(errorText || `Coach request failed with status ${response.status}`);
    }
    const answer = payload.answer || payload.body || payload.message || JSON.stringify(payload, null, 2);
    renderCoachStatus(answer);
  } catch (error) {
    renderCoachStatus(`Coach unavailable. Local hint: ${core.suggestCoachQuery(campaign)} (${error.message})`);
  }
}

function resetRun() {
  campaign = core.resetCurrentLevel(campaign);
  persistAndRender();
}

function resetCampaign() {
  campaign = core.createCampaignState();
  persistAndRender();
}

function bindEvents() {
  byId('move-up').addEventListener('click', () => move(0, -1));
  byId('move-down').addEventListener('click', () => move(0, 1));
  byId('move-left').addEventListener('click', () => move(-1, 0));
  byId('move-right').addEventListener('click', () => move(1, 0));
  byId('reset-level').addEventListener('click', resetRun);
  byId('reset-campaign').addEventListener('click', resetCampaign);
  byId('advance-level').addEventListener('click', () => {
    campaign = core.advanceLevel(campaign);
    persistAndRender();
  });
  byId('export-packet').addEventListener('click', () => {
    downloadText(
      'psicat-braided-brain-training-packet.json',
      JSON.stringify(core.createTrainingPacket(campaign), null, 2),
      'application/json',
    );
  });
  byId('export-jsonl').addEventListener('click', () => {
    downloadText(
      'psicat-braided-brain-training.jsonl',
      core.createJsonlExport(campaign),
      'application/x-ndjson',
    );
  });
  byId('ask-psicat').addEventListener('click', askCoach);
  byId('copy-prompt').addEventListener('click', async () => {
    const prompt = core.suggestCoachQuery(campaign);
    try {
      await navigator.clipboard.writeText(prompt);
      renderCoachStatus('Coach prompt copied.');
    } catch (_error) {
      renderCoachStatus(prompt);
    }
  });

  document.addEventListener('keydown', (event) => {
    const targetTag = event.target && event.target.tagName ? event.target.tagName.toLowerCase() : '';
    if (targetTag === 'input' || targetTag === 'textarea') return;
    if (event.key === 'ArrowUp' || event.key.toLowerCase() === 'w') move(0, -1);
    if (event.key === 'ArrowDown' || event.key.toLowerCase() === 's') move(0, 1);
    if (event.key === 'ArrowLeft' || event.key.toLowerCase() === 'a') move(-1, 0);
    if (event.key === 'ArrowRight' || event.key.toLowerCase() === 'd') move(1, 0);
  });

  const board = byId('board');
  board.addEventListener('touchstart', (event) => {
    const touch = event.touches[0];
    touchStart = { x: touch.clientX, y: touch.clientY };
  }, { passive: true });
  board.addEventListener('touchend', (event) => {
    if (!touchStart) return;
    const touch = event.changedTouches[0];
    const dx = touch.clientX - touchStart.x;
    const dy = touch.clientY - touchStart.y;
    touchStart = null;
    if (Math.abs(dx) > Math.abs(dy)) {
      move(dx > 0 ? 1 : -1, 0);
    } else if (Math.abs(dy) > 12) {
      move(0, dy > 0 ? 1 : -1);
    }
  }, { passive: true });
}

bindEvents();
renderState();
renderCoachStatus('Ask PsiCat for coaching, or use the local hint if Product 20 is offline.');
