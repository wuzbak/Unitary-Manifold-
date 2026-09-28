const core = window.PsiCatBraidedBrainCore;
const STORAGE_KEY = 'psicat-braided-brain-state-v2';
const DEFAULT_COACH_ENDPOINT = 'http://127.0.0.1:8020/api/psicat';
const OFFLINE_CACHE_SIGNAL = 'psicat-braided-brain-offline-ready';

let campaign = loadCampaign();
let touchStart = null;
let deferredInstallPrompt = null;
let animationFrame = null;

function byId(id) {
  return document.getElementById(id);
}

function loadCampaign() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return core.createCampaignState();
    return core.normalizeCampaign(JSON.parse(raw));
  } catch (_error) {
    return core.createCampaignState();
  }
}

function saveCampaign() {
  campaign.updatedAt = new Date().toISOString();
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(campaign));
}

function isTrustedLocalEndpoint(endpoint) {
  try {
    const parsed = new URL(endpoint, window.location.href);
    return ['127.0.0.1', 'localhost', '::1', '[::1]', '0.0.0.0'].includes(parsed.hostname);
  } catch (_error) {
    return false;
  }
}

function statusTone(value) {
  if (value >= 75) return 'stable';
  if (value >= 45) return 'tense';
  return 'critical';
}

function createMiniCard(lines, className = 'mini-card') {
  const item = document.createElement('div');
  item.className = className;
  lines.forEach(({ tag, text }) => {
    const node = document.createElement(tag);
    node.textContent = text;
    item.appendChild(node);
  });
  return item;
}

function renderTextList(id, entries) {
  const list = byId(id);
  list.innerHTML = '';
  entries.forEach((entry) => {
    const item = document.createElement('li');
    item.textContent = entry;
    list.appendChild(item);
  });
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
      button.setAttribute('role', 'gridcell');
      button.setAttribute('aria-label', `Cell ${x + 1}, ${y + 1}, ${role}`);
      button.textContent = role === 'player'
        ? '🐈'
        : role === 'signal'
          ? '✦'
          : role === 'target'
            ? '◎'
            : role === 'target-complete'
              ? '◉'
              : role === 'hazard'
                ? '≈'
                : '·';
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
    button.setAttribute('role', 'tab');
    button.setAttribute('aria-selected', String(campaign.currentLevelIndex === index));
    if (index > campaign.unlockedLevelIndex) button.disabled = true;
    button.textContent = `${index + 1}. ${level.shortLabel}`;
    const detail = document.createElement('small');
    detail.textContent = level.difficulty;
    button.appendChild(detail);
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
    const status = target.challengeResolved ? 'Mastered' : target.delivered ? 'Awaiting correct answer' : `Awaiting ${target.kind}`;
    wrap.appendChild(createMiniCard([
      { tag: 'strong', text: target.label },
      { tag: 'span', text: status },
      { tag: 'small', text: target.scientificNote },
    ]));
  });
}

function renderSignals() {
  const wrap = byId('signal-list');
  wrap.innerHTML = '';
  wrap.appendChild(createMiniCard([
    { tag: 'strong', text: 'Carried signal' },
    { tag: 'span', text: campaign.current.carriedSignal ? campaign.current.carriedSignal.label : 'None' },
  ], 'mini-card carried'));
  campaign.current.signals.forEach((signal) => {
    wrap.appendChild(createMiniCard([
      { tag: 'strong', text: signal.label },
      { tag: 'span', text: signal.kind },
    ]));
  });
}

function renderChallenge() {
  const wrap = byId('challenge-panel');
  wrap.innerHTML = '';
  const active = campaign.current.activeChallenge;
  if (!active) {
    const hint = document.createElement('p');
    hint.className = 'muted';
    hint.textContent = 'Deliver a signal to unlock a science check.';
    wrap.appendChild(hint);
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
  renderTextList('mission-log', campaign.current.missionLog);
  renderTextList('science-log', campaign.current.scienceLog);
}

function renderTrainingPacket() {
  byId('training-packet').textContent = JSON.stringify(core.createTrainingPacket(campaign), null, 2);
}

function renderCoachStatus(text) {
  byId('coach-output').textContent = text;
}

function renderAtlas() {
  const wrap = byId('atlas-list');
  wrap.innerHTML = '';
  core.getAtlasEntries(campaign).forEach((entry) => {
    const status = entry.unlocked ? 'Unlocked' : 'Locked until mastered';
    wrap.appendChild(createMiniCard([
      { tag: 'strong', text: `${entry.levelName} — ${entry.label}` },
      { tag: 'span', text: status },
      { tag: 'small', text: entry.unlocked ? entry.scientificNote : 'Play the corresponding level to reveal the full note.' },
      { tag: 'small', text: `Source: ${entry.source}` },
    ], entry.unlocked ? 'mini-card atlas-card unlocked' : 'mini-card atlas-card locked'));
  });
}

function renderAchievements() {
  const wrap = byId('achievement-list');
  wrap.innerHTML = '';
  const entries = core.buildAchievementLedger(campaign);
  if (!entries.length) {
    wrap.appendChild(createMiniCard([
      { tag: 'strong', text: 'No badges yet' },
      { tag: 'small', text: 'Finish missions and unlock concepts to fill this board.' },
    ], 'mini-card'));
    return;
  }
  entries.forEach((entry) => {
    wrap.appendChild(createMiniCard([
      { tag: 'strong', text: entry.label },
      { tag: 'small', text: entry.id },
    ], `mini-card badge-card ${entry.tone}`));
  });
}

function renderProgress() {
  const snapshot = core.getCampaignSnapshot(campaign);
  const mastery = core.calculateLevelMastery(campaign.current);
  byId('mastery-badge').textContent = `${mastery.badge} · ${mastery.stars}/3 stars`;
  byId('moves-made').textContent = String(snapshot.telemetry.movesMade);
  byId('wrap-count-total').textContent = String(snapshot.telemetry.wrapsAchieved);
  byId('atlas-count').textContent = String(snapshot.atlasInsights);
  byId('achievement-count').textContent = String(snapshot.achievements);
  byId('save-status').textContent = `Saved locally · updated ${new Date(campaign.updatedAt || Date.now()).toLocaleString()}`;
  byId('player-name').value = campaign.profile.playerName;
}

function renderInstallStatus() {
  const button = byId('install-app');
  button.disabled = !deferredInstallPrompt;
  byId('offline-status').textContent = campaign.installHints.offlineReady
    ? 'Offline cache ready'
    : 'Offline cache pending';
}

function renderState() {
  const state = campaign.current;
  const level = core.LEVELS[campaign.currentLevelIndex];
  const mastery = core.calculateLevelMastery(state);
  byId('title').textContent = 'PsiCat Braided Brain';
  byId('subtitle').textContent = 'A toroidal brain simulator for serious play, local-first saves, and explicit science tethering.';
  byId('level-name').textContent = level.name;
  byId('briefing').textContent = state.briefing;
  byId('source-note').textContent = level.sourceNote;
  byId('narrative-note').textContent = state.narrative;
  byId('score').textContent = String(campaign.totalScore + state.score);
  byId('coherence').textContent = `${state.coherence}%`;
  byId('coherence').dataset.tone = statusTone(state.coherence);
  byId('wraps').textContent = `${state.wraps}/${state.wrapGoal}`;
  byId('moves').textContent = String(state.movesLeft);
  byId('completed-levels').textContent = `${campaign.completedLevelIds.length}/${core.LEVELS.length}`;
  byId('privacy-note').textContent = 'Local progress only unless you explicitly export a save bundle or training packet.';
  byId('difficulty-chip').textContent = state.difficulty;
  byId('mastery-hero').textContent = `${mastery.badge} · ${mastery.stars}/3`;
  renderBoard();
  renderLevelSelector();
  renderTargets();
  renderSignals();
  renderChallenge();
  renderLogs();
  renderTrainingPacket();
  renderAtlas();
  renderAchievements();
  renderProgress();
  renderInstallStatus();

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

function moveTowardCell(x, y) {
  const { player, width, height } = campaign.current;
  const candidates = [
    { dx: 1, dy: 0, nx: (player.x + 1) % width, ny: player.y },
    { dx: -1, dy: 0, nx: (player.x - 1 + width) % width, ny: player.y },
    { dx: 0, dy: 1, nx: player.x, ny: (player.y + 1) % height },
    { dx: 0, dy: -1, nx: player.x, ny: (player.y - 1 + height) % height },
  ];
  const match = candidates.find((item) => item.nx === x && item.ny === y);
  if (match) {
    move(match.dx, match.dy);
  }
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

function buildLocalCoachFallback(reason) {
  const nextTarget = campaign.current.targets.find((target) => !target.challengeResolved);
  const wrapsRemaining = Math.max(0, campaign.current.wrapGoal - campaign.current.wraps);
  const carried = campaign.current.carriedSignal ? campaign.current.carriedSignal.label : 'no signal yet';
  const nextStep = nextTarget
    ? `Next focus: deliver ${nextTarget.kind} to ${nextTarget.label}.`
    : 'Next focus: finish the remaining science checks and prepare to advance.';
  const wrapHint = wrapsRemaining > 0
    ? `You still need ${wrapsRemaining} wrap${wrapsRemaining === 1 ? '' : 's'} for this mission.`
    : 'Wrap goal complete — prioritize clean deliveries.';
  return `Coach offline. Local hint: Carry ${carried}, keep coherence high, and use the torus edges to reposition. ${nextStep} ${wrapHint} (${reason})`;
}

async function askCoach() {
  const endpoint = byId('coach-endpoint').value.trim() || DEFAULT_COACH_ENDPOINT;
  const playerPrompt = byId('coach-input').value.trim();
  const query = playerPrompt || core.suggestCoachQuery(campaign);
  const trustedLocal = isTrustedLocalEndpoint(endpoint);
  if (!trustedLocal) {
    const confirmed = window.confirm('This endpoint is not local. Sending coaching context there may export gameplay data. Continue?');
    if (!confirmed) {
      renderCoachStatus('Coach request cancelled to preserve local-only retention defaults.');
      return;
    }
  }
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
      await response.text();
      throw new Error(`Coach endpoint returned status ${response.status}`);
    }
    const answer = payload.answer || payload.body || payload.message || JSON.stringify(payload, null, 2);
    renderCoachStatus(answer);
  } catch (error) {
    const reason = error && error.message ? error.message : 'coach endpoint unavailable';
    renderCoachStatus(buildLocalCoachFallback(reason));
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

function importSaveBundle(file) {
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const payload = JSON.parse(String(reader.result || '{}'));
      campaign = core.importSaveBundle(payload);
      persistAndRender();
      renderCoachStatus('Save bundle imported.');
    } catch (error) {
      renderCoachStatus(`Import failed: ${error.message}`);
    }
  };
  reader.readAsText(file);
}

function registerServiceWorker() {
  if (!('serviceWorker' in navigator)) return;
  navigator.serviceWorker.register('../sw.js', { scope: '../' })
    .then((registration) => {
      if (navigator.serviceWorker.controller || registration.active) {
        campaign.installHints.offlineReady = true;
        saveCampaign();
        renderInstallStatus();
      }
    })
    .catch(() => {});
}

function bindServiceWorkerEvents() {
  navigator.serviceWorker?.addEventListener?.('message', (event) => {
    if (event.data && event.data.type === OFFLINE_CACHE_SIGNAL) {
      campaign.installHints.offlineReady = true;
      saveCampaign();
      renderInstallStatus();
    }
  });
}

function setupInstallPrompt() {
  window.addEventListener('beforeinstallprompt', (event) => {
    event.preventDefault();
    deferredInstallPrompt = event;
    renderInstallStatus();
  });
}

async function installApp() {
  if (!deferredInstallPrompt) return;
  deferredInstallPrompt.prompt();
  try {
    await deferredInstallPrompt.userChoice;
  } finally {
    deferredInstallPrompt = null;
    renderInstallStatus();
  }
}

function drawBackground() {
  const canvas = byId('braid-canvas');
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  const ratio = window.devicePixelRatio || 1;
  canvas.width = Math.max(1, Math.floor(rect.width * ratio));
  canvas.height = Math.max(1, Math.floor(rect.height * ratio));
  const ctx = canvas.getContext('2d');
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  const { width, height } = rect;
  let phase = 0;
  const loop = () => {
    phase += 0.015;
    ctx.clearRect(0, 0, width, height);
    const gradient = ctx.createRadialGradient(width * 0.2, height * 0.1, 20, width * 0.5, height * 0.5, width * 0.9);
    gradient.addColorStop(0, 'rgba(124,92,255,0.32)');
    gradient.addColorStop(1, 'rgba(7,17,31,0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);

    ctx.lineWidth = 2;
    for (let index = 0; index < 3; index += 1) {
      ctx.beginPath();
      ctx.strokeStyle = index === 1 ? 'rgba(37,208,255,0.65)' : index === 2 ? 'rgba(57,217,138,0.4)' : 'rgba(255,190,85,0.35)';
      for (let x = 0; x <= width; x += 6) {
        const y = height * (0.28 + index * 0.18) + Math.sin((x / width) * Math.PI * 4 + phase + index) * (26 + index * 8);
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
    }

    ctx.beginPath();
    ctx.strokeStyle = 'rgba(255,255,255,0.12)';
    ctx.lineWidth = 1.2;
    ctx.ellipse(width * 0.77, height * 0.48, 84, 48, phase * 0.2, 0, Math.PI * 2);
    ctx.stroke();
    animationFrame = window.requestAnimationFrame(loop);
  };
  if (animationFrame) window.cancelAnimationFrame(animationFrame);
  loop();
}

function bindEvents() {
  const coachEndpoint = byId('coach-endpoint');
  if (!coachEndpoint.value.trim()) {
    coachEndpoint.value = DEFAULT_COACH_ENDPOINT;
  }

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
    campaign.installHints.saveExports += 1;
    persistAndRender();
    downloadText(
      'psicat-braided-brain-training-packet.json',
      JSON.stringify(core.createTrainingPacket(campaign), null, 2),
      'application/json',
    );
  });
  byId('export-jsonl').addEventListener('click', () => {
    campaign.installHints.saveExports += 1;
    persistAndRender();
    downloadText(
      'psicat-braided-brain-training.jsonl',
      core.createJsonlExport(campaign),
      'application/x-ndjson',
    );
  });
  byId('export-save').addEventListener('click', () => {
    campaign.installHints.saveExports += 1;
    persistAndRender();
    downloadText(
      'psicat-braided-brain-save.json',
      JSON.stringify(core.createSaveBundle(campaign), null, 2),
      'application/json',
    );
  });
  byId('import-save-file').addEventListener('change', (event) => {
    const [file] = event.target.files || [];
    if (file) importSaveBundle(file);
    event.target.value = '';
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
  byId('install-app').addEventListener('click', installApp);
  byId('player-name').addEventListener('change', (event) => {
    campaign.profile.playerName = String(event.target.value || 'PsiCat Pilot').trim() || 'PsiCat Pilot';
    persistAndRender();
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
  board.addEventListener('click', (event) => {
    const cell = event.target.closest('[data-x][data-y]');
    if (!cell) return;
    moveTowardCell(Number(cell.dataset.x), Number(cell.dataset.y));
  });
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
    if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 12) {
      move(dx > 0 ? 1 : -1, 0);
    } else if (Math.abs(dy) > 12) {
      move(0, dy > 0 ? 1 : -1);
    }
  }, { passive: true });

  window.addEventListener('resize', drawBackground);
}

bindServiceWorkerEvents();
bindEvents();
setupInstallPrompt();
registerServiceWorker();
drawBackground();
renderState();
renderCoachStatus('Ask PsiCat for coaching, or use the local hint if Product 20 is offline.');
