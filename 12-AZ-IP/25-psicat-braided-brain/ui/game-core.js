(function (global) {
  const VERSION = '1.1.0';
  const LEVELS = [
    {
      id: 'entorhinal-garden',
      name: 'Entorhinal Garden',
      shortLabel: 'Torus basics',
      board: { width: 7, height: 7 },
      start: { x: 3, y: 3 },
      wrapGoal: 2,
      moveBudget: 18,
      briefing: 'Guide PsiCat around a toroidal board. Wrapping across edges teaches how brain maps recycle space instead of ending at a wall.',
      sourceNote: 'Gardner et al. 2022 and /4-IMPLICATIONS/brain/TORUS_ARCHITECTURE.md',
      narrative: 'This opener teaches the foundational trick: real navigation codes can wrap in both directions. The board never ends because the science story never needed a wall in the first place.',
      difficulty: 'Starter',
      signals: [
        { id: 'grid-phase', kind: 'grid', label: 'Grid phase', x: 0, y: 3 },
        { id: 'theta-tilt', kind: 'theta', label: 'Theta tilt', x: 5, y: 1 },
      ],
      hazards: [{ x: 2, y: 2 }, { x: 4, y: 4 }],
      targets: [
        {
          id: 'entorhinal-torus',
          kind: 'grid',
          label: 'Entorhinal torus',
          x: 6,
          y: 3,
          scientificNote: 'Grid-cell population activity can be represented on a torus.',
          source: 'Gardner et al. 2022',
          conceptTag: 'toroidal-map',
          challenge: {
            prompt: 'What topology best matches the grid-cell population map?',
            choices: [
              { id: 'sphere', label: 'Sphere' },
              { id: 'torus', label: 'Torus' },
              { id: 'line', label: 'Straight line' },
            ],
            correctChoice: 'torus',
            explanation: 'A torus lets the activity wrap in both directions, just like the board you are playing on.',
          },
        },
        {
          id: 'theta-anchor',
          kind: 'theta',
          label: 'Theta anchor',
          x: 1,
          y: 6,
          scientificNote: 'Theta rhythms help coordinate navigation updates.',
          source: '/4-IMPLICATIONS/brain/TORUS_ARCHITECTURE.md',
          conceptTag: 'theta-coordination',
          challenge: {
            prompt: 'Why does theta matter in this level?',
            choices: [
              { id: 'timing', label: 'It provides timing for coordinated updates' },
              { id: 'color', label: 'It only changes colors on screen' },
              { id: 'gravity', label: 'It switches gravity on and off' },
            ],
            correctChoice: 'timing',
            explanation: 'Theta is modeled here as the timing lane that keeps the toroidal map coherent.',
          },
        },
      ],
    },
    {
      id: 'gut-loop-lagoon',
      name: 'Gut Loop Lagoon',
      shortLabel: 'ENS loop',
      board: { width: 8, height: 7 },
      start: { x: 4, y: 3 },
      wrapGoal: 2,
      moveBudget: 22,
      briefing: 'Stabilize the braided dialogue between cortex and enteric nervous system. The gut lane is modeled as a second-brain support loop, not as surveillance or mind reading.',
      sourceNote: 'Pillar 538 and /4-IMPLICATIONS/brain plus src/core/pillar538_enteric_neural_core.py',
      narrative: 'The ENS lane rewards players who can keep multiple loops in mind at once: central guidance, local autonomy, and explicit scientific humility.',
      difficulty: 'Intermediate',
      signals: [
        { id: 'serotonin-wave', kind: 'serotonin', label: 'Serotonin wave', x: 7, y: 3 },
        { id: 'autonomy-pulse', kind: 'autonomy', label: 'Autonomy pulse', x: 1, y: 1 },
      ],
      hazards: [{ x: 5, y: 3 }, { x: 2, y: 5 }, { x: 3, y: 0 }],
      targets: [
        {
          id: 'ens-hub',
          kind: 'serotonin',
          label: 'ENS hub',
          x: 0,
          y: 3,
          scientificNote: 'The ENS is often described as a second brain and produces most of the body’s serotonin.',
          source: 'src/core/pillar538_enteric_neural_core.py',
          conceptTag: 'ens-serotonin',
          challenge: {
            prompt: 'Which claim matches the repository ENS lane?',
            choices: [
              { id: 'analogy', label: 'A structural and quantitative analogy with explicit boundaries' },
              { id: 'proof', label: 'Proof that consciousness lives in the gut' },
              { id: 'nothing', label: 'No relationship at all' },
            ],
            correctChoice: 'analogy',
            explanation: 'The ENS lane is adjacent-track work with explicit non-overclaim boundaries.',
          },
        },
        {
          id: 'autonomy-gate',
          kind: 'autonomy',
          label: 'Autonomy gate',
          x: 6,
          y: 6,
          scientificNote: 'The ENS can retain substantial autonomy even when direct vagal input is disrupted.',
          source: 'src/core/pillar538_enteric_neural_core.py',
          conceptTag: 'distributed-control',
          challenge: {
            prompt: 'Why is autonomy a useful gameplay mechanic here?',
            choices: [
              { id: 'distributed', label: 'It teaches distributed control instead of one central puppet master' },
              { id: 'secret', label: 'It hides secret scores from the player' },
              { id: 'ads', label: 'It drives ad targeting' },
            ],
            correctChoice: 'distributed',
            explanation: 'The game uses autonomy to teach that real nervous systems mix local and global control.',
          },
        },
      ],
    },
    {
      id: 'fly-bridge-bay',
      name: 'Fly Bridge Bay',
      shortLabel: 'Connectome bridge',
      board: { width: 8, height: 8 },
      start: { x: 4, y: 4 },
      wrapGoal: 3,
      moveBudget: 26,
      briefing: 'Collect bridge signals from a compact MaleCNS-inspired deck. You are not proving a theory; you are learning how sensory, bridge, motor, and modulatory roles differ in a real connectome slice.',
      sourceNote: 'data/malecns/benchmark_panel.json and /4-IMPLICATIONS/brain/MALECNS_CONNECTOME_BRIDGE.md',
      narrative: 'This mission turns a real connectome benchmark into a playable role-recognition exercise. It is where play starts looking like practice.',
      difficulty: 'Research',
      signals: [
        { id: 'optic-trace', kind: 'optic', label: 'Optic trace', x: 1, y: 7 },
        { id: 'bridge-trace', kind: 'bridge', label: 'Bridge trace', x: 6, y: 0 },
        { id: 'modulator-trace', kind: 'modulator', label: 'Modulator trace', x: 0, y: 1 },
      ],
      hazards: [{ x: 3, y: 3 }, { x: 2, y: 6 }, { x: 6, y: 5 }, { x: 7, y: 2 }],
      targets: [
        {
          id: 'lplc2-lane',
          kind: 'optic',
          label: 'LPLC2 optic lane',
          x: 7,
          y: 7,
          scientificNote: 'LPLC2 is an optic projection surface and dominates throughput in the benchmark slice.',
          source: 'data/malecns/benchmark_panel.json',
          conceptTag: 'lplc2-optic',
          challenge: {
            prompt: 'In the committed benchmark panel, what is LPLC2 best treated as?',
            choices: [
              { id: 'optic', label: 'An optic-heavy projection lane' },
              { id: 'motor', label: 'A pure motor neuron' },
              { id: 'immune', label: 'An immune cell type' },
            ],
            correctChoice: 'optic',
            explanation: 'LPLC2 is explicitly described as an optic projection lane in the benchmark slice.',
          },
        },
        {
          id: 'an01b004-bridge',
          kind: 'bridge',
          label: 'AN01B004 bridge',
          x: 0,
          y: 7,
          scientificNote: 'AN01B004 is used as an ascending VNC-to-brain bridge surface in the compact panel.',
          source: '/4-IMPLICATIONS/brain/MALECNS_CONNECTOME_BRIDGE.md',
          conceptTag: 'ascending-bridge',
          challenge: {
            prompt: 'Why include AN01B004 in a teaching game?',
            choices: [
              { id: 'bridge', label: 'It is a tractable bridge between regions' },
              { id: 'myth', label: 'It proves every neuroscience claim in the repo' },
              { id: 'secret', label: 'It is a hidden lore-only bonus' },
            ],
            correctChoice: 'bridge',
            explanation: 'The bridge neurons are useful because they connect domains without inflating the claim class.',
          },
        },
        {
          id: '5htplp01-broadcast',
          kind: 'modulator',
          label: '5-HTPLP01 broadcast',
          x: 5,
          y: 4,
          scientificNote: '5-HTPLP01 is part of the modulatory surface in the benchmark slice.',
          source: 'data/malecns/benchmark_panel.json',
          conceptTag: 'modulatory-broadcast',
          challenge: {
            prompt: 'What kind of role does 5-HTPLP01 represent in this deck?',
            choices: [
              { id: 'broadcast', label: 'A modulatory broadcast role' },
              { id: 'wall', label: 'A static wall tile' },
              { id: 'planet', label: 'A planetary orbit' },
            ],
            correctChoice: 'broadcast',
            explanation: 'The deck uses 5-HTPLP01 to represent a broadcast/modulatory role.',
          },
        },
      ],
    },
    {
      id: 'phicat-braid-finale',
      name: 'PhiCat Braid Finale',
      shortLabel: 'Braided synthesis',
      board: { width: 9, height: 8 },
      start: { x: 4, y: 4 },
      wrapGoal: 3,
      moveBudget: 28,
      briefing: 'Finish by braiding PsiCat and PhiCat into a governed hemispheric partnership. The result is a voluntary training packet built from game decisions and science-card reasoning, not personal surveillance.',
      sourceNote: 'Product 20 PsiCat surfaces and the repository brain/connectome lanes',
      narrative: 'The finale turns all prior ideas into one governed synthesis: explicit memory, voluntary export, and a teaching loop that stays honest about what it knows.',
      difficulty: 'Finale',
      signals: [
        { id: 'left-hemisphere', kind: 'hemisphere', label: 'Left-hemisphere thread', x: 8, y: 4 },
        { id: 'right-hemisphere', kind: 'mirror', label: 'Right-hemisphere thread', x: 0, y: 4 },
        { id: 'training-knot', kind: 'training', label: 'Training knot', x: 4, y: 0 },
      ],
      hazards: [{ x: 2, y: 2 }, { x: 2, y: 5 }, { x: 6, y: 2 }, { x: 6, y: 5 }],
      targets: [
        {
          id: 'psicat-core',
          kind: 'hemisphere',
          label: 'PsiCat core',
          x: 1,
          y: 4,
          scientificNote: 'The playable metaphor is a braided partnership between local and global brain-style loops.',
          source: 'This product design lane',
          conceptTag: 'braided-partnership',
          challenge: {
            prompt: 'What should this game retain by default?',
            choices: [
              { id: 'task-data', label: 'Voluntary gameplay task traces and concept choices' },
              { id: 'surveillance', label: 'Biometric surveillance and hidden profiling' },
              { id: 'ads', label: 'Advertising identifiers' },
            ],
            correctChoice: 'task-data',
            explanation: 'Retention is limited to local progress and explicit training packets derived from the game tasks.',
          },
        },
        {
          id: 'phicat-core',
          kind: 'mirror',
          label: 'PhiCat mirror',
          x: 7,
          y: 4,
          scientificNote: 'The mirrored hemisphere mechanic teaches coordination instead of domination.',
          source: 'This product design lane',
          conceptTag: 'mirror-cooperation',
          challenge: {
            prompt: 'What is the intended relationship between PsiCat and PhiCat here?',
            choices: [
              { id: 'braid', label: 'A cooperative braid with explicit feedback' },
              { id: 'winner', label: 'One side permanently conquers the other' },
              { id: 'random', label: 'Pure randomness with no teaching value' },
            ],
            correctChoice: 'braid',
            explanation: 'The finale uses a cooperative braid metaphor to teach complementary cognition.',
          },
        },
        {
          id: 'training-loom',
          kind: 'training',
          label: 'Training loom',
          x: 4,
          y: 7,
          scientificNote: 'Training packets summarize voluntary puzzle outcomes into reusable science-and-game records.',
          source: 'Product 20 optional integration',
          conceptTag: 'structured-training',
          challenge: {
            prompt: 'What makes the training packet useful to PsiCat?',
            choices: [
              { id: 'structured', label: 'It is structured, grounded, and linked to explicit tasks' },
              { id: 'mystery', label: 'It hides the tasks inside mystery blobs' },
              { id: 'none', label: 'It contains no actual gameplay structure' },
            ],
            correctChoice: 'structured',
            explanation: 'Structured task traces are easier to review, transform, and reuse for future coaching or content design.',
          },
        },
      ],
    },
  ];

  function deepCopy(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function createRunId() {
    const cryptoApi = global.crypto || (typeof require === 'function' ? require('node:crypto').webcrypto : null);
    if (cryptoApi && typeof cryptoApi.randomUUID === 'function') {
      return `brain-${cryptoApi.randomUUID()}`;
    }
    return `brain-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
  }

  function getLevelById(levelId) {
    return LEVELS.find((level) => level.id === levelId) || LEVELS[0];
  }

  function calculateStarRating(state) {
    let stars = 1;
    if (state.coherence >= 72) stars += 1;
    if (state.wraps >= state.wrapGoal && state.movesLeft >= Math.ceil(getLevelById(state.levelId).moveBudget * 0.2)) stars += 1;
    return Math.max(1, Math.min(3, stars));
  }

  function calculateLevelMastery(state) {
    const allCorrect = state.targets.every((target) => target.challengeResult === 'correct');
    const efficient = state.movesLeft >= Math.floor(getLevelById(state.levelId).moveBudget * 0.25);
    const wrapDisciplined = state.wraps >= state.wrapGoal;
    const stars = calculateStarRating(state);
    return {
      stars,
      allCorrect,
      efficient,
      wrapDisciplined,
      badge: allCorrect && efficient ? 'Mastered' : stars === 3 ? 'Excellent' : stars === 2 ? 'Stable' : 'Learning',
    };
  }

  function createLevelState(levelIndex) {
    const level = LEVELS[levelIndex];
    const targets = level.targets.map((target) => ({
      ...deepCopy(target),
      delivered: false,
      challengeResolved: false,
      challengeResult: null,
    }));
    return {
      levelId: level.id,
      levelIndex,
      width: level.board.width,
      height: level.board.height,
      player: { ...level.start },
      carriedSignal: null,
      signals: level.signals.map((signal) => ({ ...signal })),
      hazards: deepCopy(level.hazards),
      targets,
      movesLeft: level.moveBudget,
      wrapGoal: level.wrapGoal,
      wraps: 0,
      wrapBonusAwarded: false,
      score: 0,
      coherence: 100,
      combo: 0,
      activeChallenge: null,
      completed: false,
      failed: false,
      briefing: level.briefing,
      shortLabel: level.shortLabel,
      sourceNote: level.sourceNote,
      narrative: level.narrative,
      difficulty: level.difficulty,
      missionLog: [`Mission loaded: ${level.name}.`],
      scienceLog: [],
      touchHistory: [],
      challengeHistory: [],
      collectedConcepts: [],
      retriedTargets: [],
    };
  }

  function createCampaignState() {
    return {
      version: VERSION,
      runId: createRunId(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      currentLevelIndex: 0,
      unlockedLevelIndex: 0,
      completedLevelIds: [],
      totalScore: 0,
      trainingRecords: [],
      coachNotes: [],
      achievements: [],
      atlasInsights: [],
      levelHistory: {},
      telemetry: {
        movesMade: 0,
        wrapsAchieved: 0,
        correctAnswers: 0,
        retryCount: 0,
      },
      installHints: {
        offlineReady: false,
        saveExports: 0,
      },
      profile: {
        playerName: 'PsiCat Pilot',
        preferredMode: 'Campaign',
      },
      current: createLevelState(0),
    };
  }

  function clampCoherence(value) {
    return Math.max(0, Math.min(100, value));
  }

  function isRecord(value) {
    return value !== null && typeof value === 'object' && !Array.isArray(value);
  }

  function clampInteger(value, min, max, fallback) {
    const numeric = Number(value);
    if (!Number.isInteger(numeric)) return fallback;
    return Math.max(min, Math.min(max, numeric));
  }

  function nonNegativeNumber(value, fallback = 0) {
    const numeric = Number(value);
    return Number.isFinite(numeric) ? Math.max(0, numeric) : fallback;
  }

  function normalizeWrap(value, size) {
    if (value < 0) return size - 1;
    if (value >= size) return 0;
    return value;
  }

  function recordLog(state, text) {
    state.missionLog = [text].concat(state.missionLog).slice(0, 8);
    return state;
  }

  function recordScience(state, text) {
    state.scienceLog = [text].concat(state.scienceLog).slice(0, 10);
    return state;
  }

  function findSignalAt(state, x, y) {
    return state.signals.find((signal) => signal.x === x && signal.y === y) || null;
  }

  function findTargetAt(state, x, y) {
    return state.targets.find((target) => target.x === x && target.y === y) || null;
  }

  function isHazard(state, x, y) {
    return state.hazards.some((hazard) => hazard.x === x && hazard.y === y);
  }

  function markLevelFailed(state, reason) {
    state.failed = true;
    state.completed = false;
    state.activeChallenge = null;
    return recordLog(state, reason);
  }

  function hasOutstandingObjectives(state) {
    return Boolean(state.activeChallenge) || !hasCompletedObjectives(state);
  }

  function hasCompletedObjectives(state) {
    return state.targets.every((item) => item.delivered && item.challengeResolved);
  }

  function ensureAchievement(campaign, achievement) {
    if (!campaign.achievements.find((item) => item.id === achievement.id)) {
      campaign.achievements = campaign.achievements.concat([achievement]);
    }
  }

  function mergeAtlasInsight(campaign, target) {
    if (!target.conceptTag) return;
    if (!campaign.atlasInsights.find((item) => item.conceptTag === target.conceptTag)) {
      campaign.atlasInsights = campaign.atlasInsights.concat([{
        conceptTag: target.conceptTag,
        title: target.label,
        note: target.scientificNote,
        source: target.source,
        unlockedAt: new Date().toISOString(),
      }]);
    }
  }

  function getAtlasEntries(campaign) {
    return LEVELS.flatMap((level) => level.targets.map((target) => ({
      levelId: level.id,
      levelName: level.name,
      label: target.label,
      conceptTag: target.conceptTag,
      scientificNote: target.scientificNote,
      source: target.source,
      unlocked: campaign.atlasInsights.some((item) => item.conceptTag === target.conceptTag),
    })));
  }

  function buildAchievementLedger(campaign) {
    const entries = [];
    if (campaign.completedLevelIds.length >= 1) entries.push({ id: 'first-braid', label: 'First braid complete', tone: 'gold' });
    if (campaign.telemetry.wrapsAchieved >= 8) entries.push({ id: 'torus-runner', label: 'Toroidal runner', tone: 'cyan' });
    if (campaign.atlasInsights.length >= 6) entries.push({ id: 'science-scout', label: 'Science scout', tone: 'violet' });
    if (campaign.trainingRecords.length >= 4) entries.push({ id: 'tether-ready', label: 'Tether ready', tone: 'emerald' });
    return entries;
  }

  function levelSummary(state) {
    return {
      levelId: state.levelId,
      levelIndex: state.levelIndex,
      score: state.score,
      wraps: state.wraps,
      coherence: state.coherence,
      movesUsed: LEVELS[state.levelIndex].moveBudget - state.movesLeft,
      mastery: calculateLevelMastery(state),
      cardResults: state.targets.map((target) => ({
        targetId: target.id,
        label: target.label,
        delivered: target.delivered,
        correct: target.challengeResult === 'correct',
        conceptTag: target.conceptTag,
      })),
      touchHistory: state.touchHistory.slice(0, 32),
      completedAt: new Date().toISOString(),
    };
  }

  function updateAchievements(campaign) {
    buildAchievementLedger(campaign).forEach((achievement) => ensureAchievement(campaign, achievement));
  }

  function maybeFinishLevel(campaign) {
    const state = campaign.current;
    const allDelivered = hasCompletedObjectives(state);
    if (!allDelivered || state.activeChallenge) return campaign;
    state.completed = true;
    state.failed = false;
    const summary = levelSummary(state);
    const existingRecordIndex = campaign.trainingRecords.findIndex((record) => record.levelId === state.levelId);
    if (existingRecordIndex >= 0) {
      campaign.trainingRecords = campaign.trainingRecords.map((record, index) => (
        index === existingRecordIndex ? summary : record
      ));
    } else {
      campaign.trainingRecords = campaign.trainingRecords.concat([summary]);
    }
    if (!campaign.completedLevelIds.includes(state.levelId)) {
      campaign.completedLevelIds = campaign.completedLevelIds.concat(state.levelId);
      campaign.unlockedLevelIndex = Math.max(campaign.unlockedLevelIndex, Math.min(LEVELS.length - 1, state.levelIndex + 1));
    }
    campaign.totalScore = campaign.trainingRecords.reduce((sum, record) => sum + Math.max(0, Number(record.score || 0)), 0);
    campaign.levelHistory[state.levelId] = summary;
    campaign.updatedAt = new Date().toISOString();
    updateAchievements(campaign);
    return campaign;
  }

  function movePlayer(campaign, dx, dy) {
    const next = deepCopy(campaign);
    const state = next.current;
    if (state.completed || state.failed || state.activeChallenge) return next;
    if (state.movesLeft <= 0) {
      markLevelFailed(state, 'Out of moves. Reset or try a new braid.');
      return next;
    }

    const rawX = state.player.x + dx;
    const rawY = state.player.y + dy;
    const wrapped = rawX < 0 || rawX >= state.width || rawY < 0 || rawY >= state.height;
    state.player.x = normalizeWrap(rawX, state.width);
    state.player.y = normalizeWrap(rawY, state.height);
    state.movesLeft -= 1;
    next.telemetry.movesMade += 1;
    state.touchHistory = state.touchHistory.concat([{ x: state.player.x, y: state.player.y }]).slice(-64);

    if (wrapped) {
      state.wraps += 1;
      next.telemetry.wrapsAchieved += 1;
      recordLog(state, 'Toroidal wrap completed. Space folds instead of ending.');
      if (!state.wrapBonusAwarded && state.wraps >= state.wrapGoal) {
        state.wrapBonusAwarded = true;
        state.score += 80;
        recordScience(state, `Wrap goal reached: ${state.wrapGoal} loops for ${state.shortLabel}.`);
      }
    }

    if (isHazard(state, state.player.x, state.player.y)) {
      state.coherence = clampCoherence(state.coherence - 12);
      state.combo = 0;
      recordLog(state, 'Noise field hit. Coherence dropped.');
    }

    const signal = findSignalAt(state, state.player.x, state.player.y);
    if (signal && !state.carriedSignal) {
      state.carriedSignal = { id: signal.id, kind: signal.kind, label: signal.label };
      state.signals = state.signals.filter((item) => item.id !== signal.id);
      state.score += 20;
      recordLog(state, `Collected ${signal.label}.`);
      recordScience(state, `${signal.label} picked up for ${state.shortLabel}.`);
    }

    const target = findTargetAt(state, state.player.x, state.player.y);
    if (target && !target.delivered && state.carriedSignal && state.carriedSignal.kind === target.kind) {
      target.delivered = true;
      state.score += 100 + state.combo * 10;
      state.combo += 1;
      recordLog(state, `Delivered ${state.carriedSignal.label} to ${target.label}.`);
      recordScience(state, `${target.label}: ${target.scientificNote}`);
      state.activeChallenge = {
        targetId: target.id,
        label: target.label,
        prompt: target.challenge.prompt,
        choices: deepCopy(target.challenge.choices),
        correctChoice: target.challenge.correctChoice,
        explanation: target.challenge.explanation,
        source: target.source,
      };
      state.carriedSignal = null;
    } else if (target && !target.delivered && state.carriedSignal) {
      recordLog(state, `${target.label} needs a different signal.`);
    }

    if (state.coherence <= 0) {
      markLevelFailed(state, 'Coherence collapsed. Reset the braid and try again.');
      next.updatedAt = new Date().toISOString();
      updateAchievements(next);
      return next;
    }
    if (state.movesLeft <= 0 && hasOutstandingObjectives(state)) {
      markLevelFailed(state, 'Out of moves before finishing the braid.');
      next.updatedAt = new Date().toISOString();
      updateAchievements(next);
      return next;
    }
    next.updatedAt = new Date().toISOString();
    updateAchievements(next);
    return next;
  }

  function answerChallenge(campaign, choiceId) {
    const next = deepCopy(campaign);
    const state = next.current;
    if (!state.activeChallenge) return next;
    const challenge = state.activeChallenge;
    const target = state.targets.find((item) => item.id === challenge.targetId);
    if (!target) return next;

    const correct = choiceId === challenge.correctChoice;
    state.challengeHistory = state.challengeHistory.concat([{ targetId: target.id, choiceId, correct }]);
    if (correct) {
      target.challengeResolved = true;
      target.challengeResult = 'correct';
      state.score += 60;
      state.coherence = clampCoherence(state.coherence + 6);
      state.collectedConcepts = Array.from(new Set(state.collectedConcepts.concat(target.conceptTag || [])));
      next.telemetry.correctAnswers += 1;
      recordLog(state, `${target.label} locked in.`);
      recordScience(state, `${target.label}: ${challenge.explanation}`);
      mergeAtlasInsight(next, target);
      state.activeChallenge = null;
      next.updatedAt = new Date().toISOString();
      updateAchievements(next);
      return maybeFinishLevel(next);
    }
    target.challengeResolved = false;
    target.challengeResult = 'retry';
    state.score = Math.max(0, state.score - 20);
    state.coherence = clampCoherence(state.coherence - 8);
    state.retriedTargets = Array.from(new Set(state.retriedTargets.concat(target.id)));
    next.telemetry.retryCount += 1;
    recordLog(state, `Not quite. ${challenge.explanation}`);
    recordScience(state, `${target.label}: retry required after incorrect answer.`);
    if (state.movesLeft <= 0 && hasOutstandingObjectives(state)) {
      markLevelFailed(state, 'Out of moves before finishing the braid.');
      next.updatedAt = new Date().toISOString();
      updateAchievements(next);
      return next;
    }
    next.updatedAt = new Date().toISOString();
    updateAchievements(next);
    return next;
  }

  function resetCurrentLevel(campaign) {
    const next = deepCopy(campaign);
    next.current = createLevelState(next.currentLevelIndex);
    next.updatedAt = new Date().toISOString();
    return next;
  }

  function jumpToLevel(campaign, levelIndex) {
    const safeIndex = Math.max(0, Math.min(LEVELS.length - 1, levelIndex));
    const next = deepCopy(campaign);
    if (safeIndex > next.unlockedLevelIndex) return next;
    next.currentLevelIndex = safeIndex;
    next.current = createLevelState(safeIndex);
    next.updatedAt = new Date().toISOString();
    return next;
  }

  function advanceLevel(campaign) {
    if (!campaign.current.completed) return deepCopy(campaign);
    const nextIndex = Math.min(LEVELS.length - 1, campaign.currentLevelIndex + 1);
    const next = deepCopy(campaign);
    next.currentLevelIndex = nextIndex;
    next.current = createLevelState(nextIndex);
    next.updatedAt = new Date().toISOString();
    return next;
  }

  function createTrainingPacket(campaign) {
    const packet = {
      schema: 'psicat-braided-brain-training-v2',
      product: 25,
      version: campaign.version,
      runId: campaign.runId,
      createdAt: campaign.createdAt,
      exportedAt: new Date().toISOString(),
      completedLevels: campaign.completedLevelIds.slice(),
      totalScore: campaign.totalScore + (campaign.current.completed ? 0 : campaign.current.score),
      achievements: campaign.achievements.slice(),
      atlasInsights: campaign.atlasInsights.slice(),
      currentLevel: {
        id: campaign.current.levelId,
        label: LEVELS[campaign.current.levelIndex].name,
        completed: campaign.current.completed,
        wraps: campaign.current.wraps,
        coherence: campaign.current.coherence,
        difficulty: campaign.current.difficulty,
      },
      telemetry: deepCopy(campaign.telemetry),
      trainingRecords: campaign.trainingRecords.concat(campaign.current.completed ? [] : [levelSummary(campaign.current)]),
      pedagogicalFocus: [
        'toroidal navigation',
        'distributed control',
        'connectome role recognition',
        'explicit epistemic boundaries',
        'voluntary local-first scientific play',
      ],
      privacy: {
        surveillance: 'none',
        retainedByDefault: 'local progress only',
        exportMode: 'voluntary explicit packet export',
      },
    };
    return packet;
  }

  function createJsonlExport(campaign) {
    const packet = createTrainingPacket(campaign);
    const records = packet.trainingRecords.map((record) => JSON.stringify({
      instruction: `Summarize the player reasoning and mission outcome for ${record.levelId}.`,
      input: record,
      output: {
        score: record.score,
        wraps: record.wraps,
        coherence: record.coherence,
        mastery: record.mastery,
        concepts: record.cardResults,
      },
      metadata: {
        product: 25,
        runId: packet.runId,
        schema: packet.schema,
      },
    }));
    return records.join('\n');
  }

  function createSaveBundle(campaign) {
    return {
      schema: 'psicat-braided-brain-save-v1',
      exportedAt: new Date().toISOString(),
      campaign: deepCopy(campaign),
      atlas: getAtlasEntries(campaign),
    };
  }

  function normalizeCampaign(candidate) {
    const base = createCampaignState();
    const incoming = isRecord(candidate) ? candidate : {};
    const knownLevelIds = new Set(LEVELS.map((level) => level.id));
    const hasTopLevelIndex = incoming.currentLevelIndex !== undefined && incoming.currentLevelIndex !== null;
    const clampedIncomingIndex = clampInteger(incoming.currentLevelIndex, 0, LEVELS.length - 1, 0);
    const rawLevelId = hasTopLevelIndex
      ? LEVELS[clampedIncomingIndex].id
      : (isRecord(incoming.current) ? incoming.current.levelId : null) || LEVELS[0].id;
    const resolvedLevel = getLevelById(rawLevelId);
    const resolvedLevelIndex = hasTopLevelIndex
      ? clampedIncomingIndex
      : Math.max(0, LEVELS.findIndex((level) => level.id === resolvedLevel.id));
    const incomingCurrent = isRecord(incoming.current) ? incoming.current : {};
    const incomingTargets = Array.isArray(incomingCurrent.targets) ? incomingCurrent.targets : [];
    const incomingSignals = Array.isArray(incomingCurrent.signals) ? incomingCurrent.signals : [];
    const validTargets = incomingTargets.every(isRecord);
    const validSignals = incomingSignals.every(isRecord);
    const savedSignalIds = new Set(
      (validSignals ? incomingSignals : [])
        .map((signal) => signal.id)
        .filter((id) => typeof id === 'string'),
    );
    const normalized = {
      ...base,
      ...incoming,
      completedLevelIds: Array.isArray(incoming.completedLevelIds)
        ? incoming.completedLevelIds.filter((id) => typeof id === 'string' && knownLevelIds.has(id))
        : base.completedLevelIds,
      totalScore: nonNegativeNumber(incoming.totalScore, base.totalScore),
      trainingRecords: Array.isArray(incoming.trainingRecords)
        ? incoming.trainingRecords
            .filter((record) => isRecord(record) && knownLevelIds.has(record.levelId))
            .map((record) => ({ ...record, score: nonNegativeNumber(record.score) }))
        : base.trainingRecords,
      coachNotes: Array.isArray(incoming.coachNotes)
        ? incoming.coachNotes.filter((note) => typeof note === 'string')
        : base.coachNotes,
      achievements: Array.isArray(incoming.achievements)
        ? incoming.achievements.filter((item) => isRecord(item) && typeof item.id === 'string')
        : base.achievements,
      atlasInsights: Array.isArray(incoming.atlasInsights)
        ? incoming.atlasInsights.filter((item) => isRecord(item) && typeof item.conceptTag === 'string')
        : base.atlasInsights,
      levelHistory: isRecord(incoming.levelHistory) ? incoming.levelHistory : base.levelHistory,
      telemetry: { ...base.telemetry, ...(isRecord(incoming.telemetry) ? incoming.telemetry : {}) },
      installHints: { ...base.installHints, ...(isRecord(incoming.installHints) ? incoming.installHints : {}) },
      profile: { ...base.profile, ...(isRecord(incoming.profile) ? incoming.profile : {}) },
      current: createLevelState(resolvedLevelIndex),
    };
    const levelTemplate = createLevelState(resolvedLevelIndex);
    const sameLevelPayload = !incomingCurrent.levelId || incomingCurrent.levelId === resolvedLevel.id;
    const levelSignalMap = new Map(levelTemplate.signals.map((signal) => [signal.id, signal]));
    const safeSignalIds = new Set(levelSignalMap.keys());
    const safeTargetIds = new Set(levelTemplate.targets.map((target) => target.id));
    const safeTargetMap = new Map(
      (validTargets ? incomingTargets : [])
        .filter((target) => typeof target.id === 'string')
        .map((target) => [target.id, target]),
    );
    const restoredCarriedSignal = sameLevelPayload && incomingCurrent.carriedSignal && safeSignalIds.has(incomingCurrent.carriedSignal.id)
      ? (() => {
          const templateSignal = levelSignalMap.get(incomingCurrent.carriedSignal.id);
          return templateSignal
            ? {
                id: templateSignal.id,
                kind: templateSignal.kind,
                label: templateSignal.label,
              }
            : null;
        })()
      : null;
    const restoredTargets = levelTemplate.targets.map((target) => {
      const savedTarget = sameLevelPayload && safeTargetIds.has(target.id) ? safeTargetMap.get(target.id) : null;
      const delivered = Boolean(savedTarget?.delivered);
      const challengeResolved = delivered && Boolean(savedTarget?.challengeResolved);
      return savedTarget
        ? {
            ...target,
            delivered,
            challengeResolved,
            challengeResult: challengeResolved ? 'correct' : savedTarget.challengeResult === 'retry' ? 'retry' : null,
          }
        : target;
    });
    normalized.currentLevelIndex = resolvedLevelIndex;
    normalized.unlockedLevelIndex = clampInteger(
      incoming.unlockedLevelIndex,
      0,
      LEVELS.length - 1,
      resolvedLevelIndex,
    );
    normalized.current = {
      ...levelTemplate,
      player: sameLevelPayload && isRecord(incomingCurrent.player)
        ? {
            x: clampInteger(incomingCurrent.player.x, 0, levelTemplate.width - 1, levelTemplate.player.x),
            y: clampInteger(incomingCurrent.player.y, 0, levelTemplate.height - 1, levelTemplate.player.y),
          }
        : levelTemplate.player,
      carriedSignal: restoredCarriedSignal,
      signals: sameLevelPayload && validSignals
        ? levelTemplate.signals.filter((signal) => (
            signal.id !== restoredCarriedSignal?.id
            && savedSignalIds.has(signal.id)
          ))
        : levelTemplate.signals,
      targets: restoredTargets,
      movesLeft: sameLevelPayload
        ? clampInteger(incomingCurrent.movesLeft, 0, levelTemplate.movesLeft, levelTemplate.movesLeft)
        : levelTemplate.movesLeft,
      wraps: sameLevelPayload ? clampInteger(incomingCurrent.wraps, 0, 100_000, levelTemplate.wraps) : levelTemplate.wraps,
      wrapBonusAwarded: sameLevelPayload ? Boolean(incomingCurrent.wrapBonusAwarded) : levelTemplate.wrapBonusAwarded,
      score: sameLevelPayload ? nonNegativeNumber(incomingCurrent.score, levelTemplate.score) : levelTemplate.score,
      coherence: sameLevelPayload
        ? clampCoherence(Number.isFinite(Number(incomingCurrent.coherence)) ? Number(incomingCurrent.coherence) : levelTemplate.coherence)
        : levelTemplate.coherence,
      combo: sameLevelPayload ? clampInteger(incomingCurrent.combo, 0, 100_000, levelTemplate.combo) : levelTemplate.combo,
      activeChallenge: sameLevelPayload
        && incomingCurrent.activeChallenge
        && safeTargetIds.has(incomingCurrent.activeChallenge.targetId)
        ? (() => {
            const target = restoredTargets.find((entry) => entry.id === incomingCurrent.activeChallenge.targetId);
            return target && !target.challengeResolved
              ? {
                  targetId: target.id,
                  label: target.label,
                  prompt: target.challenge.prompt,
                  choices: deepCopy(target.challenge.choices),
                  correctChoice: target.challenge.correctChoice,
                  explanation: target.challenge.explanation,
                  source: target.source,
                }
              : null;
          })()
        : null,
      completed: levelTemplate.completed,
      failed: levelTemplate.failed,
      missionLog: sameLevelPayload && Array.isArray(incomingCurrent.missionLog)
        ? incomingCurrent.missionLog.map((entry) => String(entry)).slice(0, 8)
        : levelTemplate.missionLog,
      scienceLog: sameLevelPayload && Array.isArray(incomingCurrent.scienceLog)
        ? incomingCurrent.scienceLog.map((entry) => String(entry)).slice(0, 10)
        : levelTemplate.scienceLog,
      touchHistory: sameLevelPayload
        && Array.isArray(incomingCurrent.touchHistory)
        && incomingCurrent.touchHistory.every(isRecord)
        ? incomingCurrent.touchHistory
            .map((entry) => ({
              x: clampInteger(entry.x, 0, levelTemplate.width - 1, levelTemplate.player.x),
              y: clampInteger(entry.y, 0, levelTemplate.height - 1, levelTemplate.player.y),
            }))
            .slice(-64)
        : levelTemplate.touchHistory,
      challengeHistory: sameLevelPayload
        && Array.isArray(incomingCurrent.challengeHistory)
        && incomingCurrent.challengeHistory.every(isRecord)
        ? incomingCurrent.challengeHistory
            .filter((entry) => safeTargetIds.has(entry.targetId))
            .map((entry) => ({
              targetId: String(entry.targetId),
              choiceId: String(entry.choiceId),
              correct: Boolean(entry.correct),
            }))
            .slice(-32)
        : levelTemplate.challengeHistory,
      collectedConcepts: sameLevelPayload && Array.isArray(incomingCurrent.collectedConcepts)
        ? incomingCurrent.collectedConcepts.filter((entry) => typeof entry === 'string').slice(0, 64)
        : levelTemplate.collectedConcepts,
      retriedTargets: sameLevelPayload && Array.isArray(incomingCurrent.retriedTargets)
        ? incomingCurrent.retriedTargets.filter((entry) => typeof entry === 'string' && safeTargetIds.has(entry)).slice(0, 32)
        : levelTemplate.retriedTargets,
      levelId: resolvedLevel.id,
      levelIndex: resolvedLevelIndex,
    };
    const restoredCompleted = sameLevelPayload
      ? Boolean(incomingCurrent.completed)
        && hasCompletedObjectives(normalized.current)
        && !normalized.current.activeChallenge
      : levelTemplate.completed;
    normalized.current.completed = restoredCompleted;
    normalized.current.failed = sameLevelPayload
      ? !restoredCompleted && (
          Boolean(incomingCurrent.failed)
          || normalized.current.coherence <= 0
          || (normalized.current.movesLeft <= 0 && hasOutstandingObjectives(normalized.current))
        )
      : levelTemplate.failed;
    normalized.version = VERSION;
    return normalized;
  }

  function importSaveBundle(bundle) {
    if (!bundle || bundle.schema !== 'psicat-braided-brain-save-v1' || !bundle.campaign) {
      throw new Error('Invalid PsiCat Braided Brain save bundle.');
    }
    return normalizeCampaign(bundle.campaign);
  }

  function suggestCoachQuery(campaign) {
    const packet = createTrainingPacket(campaign);
    return [
      'Coach me on the next best move in PsiCat Braided Brain.',
      `Current level: ${packet.currentLevel.label}`,
      `Wraps: ${packet.currentLevel.wraps}, coherence: ${packet.currentLevel.coherence}`,
      `Completed levels: ${packet.completedLevels.join(', ') || 'none yet'}`,
      `Atlas insights unlocked: ${packet.atlasInsights.length}`,
      'Keep the answer short, educational, and game-actionable.',
    ].join(' ');
  }

  function getCellRole(state, x, y) {
    if (state.player.x === x && state.player.y === y) return 'player';
    const target = findTargetAt(state, x, y);
    if (target) return target.delivered ? 'target-complete' : 'target';
    if (findSignalAt(state, x, y)) return 'signal';
    if (isHazard(state, x, y)) return 'hazard';
    return 'empty';
  }

  function getLevelDeck() {
    return LEVELS.map((level) => ({
      id: level.id,
      name: level.name,
      shortLabel: level.shortLabel,
      briefing: level.briefing,
      difficulty: level.difficulty,
    }));
  }

  function getCampaignSnapshot(campaign) {
    const current = campaign.current;
    return {
      version: campaign.version,
      totalScore: campaign.totalScore + (current.completed ? 0 : current.score),
      completedLevels: campaign.completedLevelIds.length,
      atlasInsights: campaign.atlasInsights.length,
      achievements: campaign.achievements.length,
      mastery: calculateLevelMastery(current),
      telemetry: deepCopy(campaign.telemetry),
    };
  }

  const api = {
    VERSION,
    LEVELS,
    createCampaignState,
    createLevelState,
    normalizeCampaign,
    importSaveBundle,
    movePlayer,
    answerChallenge,
    resetCurrentLevel,
    advanceLevel,
    jumpToLevel,
    createTrainingPacket,
    createJsonlExport,
    createSaveBundle,
    suggestCoachQuery,
    getCellRole,
    getLevelDeck,
    getAtlasEntries,
    getCampaignSnapshot,
    calculateLevelMastery,
    buildAchievementLedger,
  };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  }
  global.PsiCatBraidedBrainCore = api;
})(typeof window !== 'undefined' ? window : globalThis);
