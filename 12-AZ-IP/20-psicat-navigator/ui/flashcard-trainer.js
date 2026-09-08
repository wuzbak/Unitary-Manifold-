// SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
// Copyright (C) 2026  ThomasCory Walker-Pearson
//
// 19-flashcard-trainer.js
// UM Physics Flashcard Trainer — client-side logic
// Zero dependencies. Works fully offline.

(function () {
  'use strict';

  // ── State ──────────────────────────────────────────────────────────────────
  let allCards = [];
  let deck = [];
  let idx = 0;
  let flipped = false;
  let rightCount = 0;
  let wrongCount = 0;
  let againQueue = [];
  let activeCats = new Set();
  let mode = 'all';

  const CATEGORIES = ['constants', 'predictions', 'gates', 'geometry', 'experiments', 'lean4', 'architecture_limits'];

  // ── DOM refs ───────────────────────────────────────────────────────────────
  const cardEl      = document.getElementById('card');
  const cardQ       = document.getElementById('card-q');
  const cardA       = document.getElementById('card-a');
  const frontMeta   = document.getElementById('front-meta');
  const backMeta    = document.getElementById('back-meta');
  const answerBtns  = document.getElementById('answer-btns');
  const btnWrong    = document.getElementById('btn-wrong');
  const btnAgain    = document.getElementById('btn-again');
  const btnRight    = document.getElementById('btn-right');
  const btnStart    = document.getElementById('btn-start');
  const btnShuffle  = document.getElementById('btn-shuffle');
  const btnAgainAll = document.getElementById('btn-again-all');
  const modeSelect  = document.getElementById('mode-select');
  const catGrid     = document.getElementById('cat-grid');
  const doneScreen  = document.getElementById('done-screen');
  const progFill    = document.getElementById('prog-fill');
  const progLabel   = document.getElementById('prog-label');
  const accLabel    = document.getElementById('acc-label');
  const statRight   = document.getElementById('stat-right');
  const statWrong   = document.getElementById('stat-wrong');
  const statRem     = document.getElementById('stat-rem');
  const donePct     = document.getElementById('done-pct');
  const doneDetail  = document.getElementById('done-detail');

  // ── Bootstrap ──────────────────────────────────────────────────────────────
  buildCatGrid();
  loadDeck();

  function buildCatGrid() {
    CATEGORIES.forEach(cat => {
      activeCats.add(cat);
      const btn = document.createElement('button');
      btn.className = 'cat-btn active';
      btn.textContent = cat.replace('_', ' ');
      btn.dataset.cat = cat;
      btn.addEventListener('click', () => {
        if (activeCats.has(cat)) {
          if (activeCats.size === 1) return; // keep at least one
          activeCats.delete(cat);
          btn.classList.remove('active');
        } else {
          activeCats.add(cat);
          btn.classList.add('active');
        }
      });
      catGrid.appendChild(btn);
    });
  }

  function loadDeck() {
    fetch('./flashcard-deck.json')
      .then(r => r.json())
      .then(data => {
        allCards = data.cards;
        renderCard({ q: 'Press Start to begin', a: '', cat: '', gate: '', pillar: null });
      })
      .catch(() => {
        // fallback — inline a minimal set if fetch fails (offline)
        allCards = [
          { id: 1, cat: 'constants', q: 'What is n_w?', a: 'n_w = 5 (braided winding number, proved unique)', gate: 'WINDING_RESONANCE_STABILITY_BASIN', pillar: 789 },
          { id: 2, cat: 'constants', q: 'What is K_CS?', a: 'K_CS = 74 = 5² + 7²', gate: 'HARDGATE', pillar: 2 },
          { id: 3, cat: 'predictions', q: 'What is n_s?', a: 'n_s = 0.9635, within 0.33σ of Planck', gate: 'HARDGATE', pillar: 3 },
        ];
        renderCard({ q: 'Offline mode — limited cards loaded', a: '', cat: '', gate: '', pillar: null });
      });
  }

  // ── Session control ────────────────────────────────────────────────────────
  function startSession() {
    doneScreen.style.display = 'none';
    cardEl.style.display = '';
    answerBtns.style.display = '';

    let source = allCards.filter(c => activeCats.has(c.cat));
    if (source.length === 0) source = allCards;

    if (mode === 'wrong') {
      const wrongIds = JSON.parse(localStorage.getItem('um_fc_wrong') || '[]');
      source = source.filter(c => wrongIds.includes(c.id));
      if (source.length === 0) source = allCards.filter(c => activeCats.has(c.cat));
    }

    deck = shuffle(source);
    idx = 0;
    rightCount = 0;
    wrongCount = 0;
    againQueue = [];
    flipped = false;
    cardEl.classList.remove('flipped');
    answerBtns.classList.add('hidden');
    updateStats();
    showCard();
  }

  function showCard() {
    if (idx >= deck.length) {
      if (againQueue.length > 0) {
        deck = deck.concat(shuffle(againQueue));
        againQueue = [];
      } else {
        showDone();
        return;
      }
    }
    flipped = false;
    cardEl.classList.remove('flipped');
    answerBtns.classList.add('hidden');
    renderCard(deck[idx]);
    updateStats();
  }

  function flipCard() {
    if (!deck.length) return;
    flipped = !flipped;
    cardEl.classList.toggle('flipped', flipped);
    if (flipped) {
      answerBtns.classList.remove('hidden');
    } else {
      answerBtns.classList.add('hidden');
    }
  }

  function answer(result) {
    if (!flipped) return;
    const card = deck[idx];
    if (result === 'right') {
      rightCount++;
      saveNotWrong(card.id);
    } else if (result === 'wrong') {
      wrongCount++;
      againQueue.push(card);
      saveWrong(card.id);
    } else {
      // 'again' — push to end, don't count
      againQueue.push(card);
    }
    idx++;
    showCard();
  }

  function showDone() {
    cardEl.style.display = 'none';
    answerBtns.style.display = 'none';
    doneScreen.style.display = 'block';
    const total = rightCount + wrongCount;
    const pct = total === 0 ? 0 : Math.round((rightCount / total) * 100);
    donePct.textContent = pct + '%';
    doneDetail.textContent = `${rightCount} correct · ${wrongCount} missed · ${deck.length} cards reviewed`;
  }

  // ── Render ─────────────────────────────────────────────────────────────────
  function renderCard(card) {
    cardQ.textContent = card.q || '';
    cardA.textContent = card.a || '';
    frontMeta.innerHTML = buildMeta(card);
    backMeta.innerHTML = buildMeta(card);
  }

  function buildMeta(card) {
    let html = '';
    if (card.cat)    html += `<span class="badge cat">${card.cat.replace('_', ' ')}</span>`;
    if (card.gate)   html += `<span class="badge gate">${card.gate}</span>`;
    if (card.pillar) html += `<span class="badge pillar">Pillar ${card.pillar}</span>`;
    return html;
  }

  // ── Stats ──────────────────────────────────────────────────────────────────
  function updateStats() {
    const total = deck.length;
    const done = idx;
    const pct = total === 0 ? 0 : Math.round((done / total) * 100);
    progFill.style.width = pct + '%';
    progLabel.textContent = `Card ${Math.min(done + 1, total)} / ${total}`;
    const rated = rightCount + wrongCount;
    accLabel.textContent = rated === 0 ? 'Accuracy: —' : `Accuracy: ${Math.round(rightCount / rated * 100)}%`;
    statRight.textContent = rightCount;
    statWrong.textContent = wrongCount;
    statRem.textContent = Math.max(0, total - done);
  }

  // ── Persistence ────────────────────────────────────────────────────────────
  function saveWrong(id) {
    try {
      const arr = JSON.parse(localStorage.getItem('um_fc_wrong') || '[]');
      if (!arr.includes(id)) { arr.push(id); localStorage.setItem('um_fc_wrong', JSON.stringify(arr)); }
    } catch (_) {}
  }

  function saveNotWrong(id) {
    try {
      const arr = JSON.parse(localStorage.getItem('um_fc_wrong') || '[]');
      const filtered = arr.filter(x => x !== id);
      localStorage.setItem('um_fc_wrong', JSON.stringify(filtered));
    } catch (_) {}
  }

  // ── Utils ──────────────────────────────────────────────────────────────────
  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  // ── Events ─────────────────────────────────────────────────────────────────
  btnStart.addEventListener('click', () => { mode = modeSelect.value; startSession(); });
  btnShuffle.addEventListener('click', () => { deck = shuffle(deck); idx = 0; showCard(); });
  btnAgainAll.addEventListener('click', () => { mode = modeSelect.value; startSession(); });
  cardEl.addEventListener('click', flipCard);
  btnWrong.addEventListener('click', () => answer('wrong'));
  btnAgain.addEventListener('click', () => answer('again'));
  btnRight.addEventListener('click', () => answer('right'));

  document.addEventListener('keydown', e => {
    if (e.target.tagName === 'SELECT' || e.target.tagName === 'BUTTON') return;
    if (e.code === 'Space') { e.preventDefault(); flipCard(); }
    if (e.key === '1') answer('wrong');
    if (e.key === '2') answer('again');
    if (e.key === '3') answer('right');
  });

  // ── Exports for testing ────────────────────────────────────────────────────
  if (typeof window !== 'undefined') {
    window._UM_FC = {
      shuffle,
      getState: () => ({ idx, rightCount, wrongCount, flipped, deckLen: deck.length }),
      _setAllCards: (cards) => { allCards = cards; },
      _startSession: startSession,
      _flipCard: flipCard,
      _answer: answer,
      CATEGORIES,
    };
  }
})();
