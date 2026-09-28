(function (global) {
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
    return `brain-${Math.random().toString(36).slice(2, 10)}`;
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
      targets,
      hazards: deepCopy(level.hazards),
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
      missionLog: [`Mission loaded: ${level.name}.`],
      scienceLog: [],
      touchHistory: [],
      challengeHistory: [],
    };
  }

  function createCampaignState() {
    return {
      version: '1.0.0',
      runId: createRunId(),
      createdAt: new Date().toISOString(),
      currentLevelIndex: 0,
      unlockedLevelIndex: 0,
      completedLevelIds: [],
      totalScore: 0,
      trainingRecords: [],
      coachNotes: [],
      current: createLevelState(0),
    };
  }

  function clampCoherence(value) {
    return Math.max(0, Math.min(100, value));
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

  function maybeFinishLevel(campaign) {
    const state = campaign.current;
    const allDelivered = state.targets.every((target) => target.delivered && target.challengeResolved);
    if (!allDelivered || state.activeChallenge) return campaign;
    state.completed = true;
    state.failed = false;
    const summary = levelSummary(state);
    if (!campaign.completedLevelIds.includes(state.levelId)) {
      campaign.completedLevelIds = campaign.completedLevelIds.concat(state.levelId);
      campaign.trainingRecords = campaign.trainingRecords.concat([summary]);
      campaign.totalScore += state.score;
      campaign.unlockedLevelIndex = Math.max(campaign.unlockedLevelIndex, Math.min(LEVELS.length - 1, state.levelIndex + 1));
    }
    return campaign;
  }

  function levelSummary(state) {
    return {
      levelId: state.levelId,
      levelIndex: state.levelIndex,
      score: state.score,
      wraps: state.wraps,
      coherence: state.coherence,
      movesUsed: LEVELS[state.levelIndex].moveBudget - state.movesLeft,
      cardResults: state.targets.map((target) => ({
        targetId: target.id,
        label: target.label,
        delivered: target.delivered,
        correct: target.challengeResult === 'correct',
      })),
      touchHistory: state.touchHistory.slice(0, 32),
      completedAt: new Date().toISOString(),
    };
  }

  function movePlayer(campaign, dx, dy) {
    const next = deepCopy(campaign);
    const state = next.current;
    if (state.completed || state.failed || state.activeChallenge) return next;
    if (state.movesLeft <= 0) return markLevelFailed(state, 'Out of moves. Reset or try a new braid.');

    const rawX = state.player.x + dx;
    const rawY = state.player.y + dy;
    const wrapped = rawX < 0 || rawX >= state.width || rawY < 0 || rawY >= state.height;
    state.player.x = normalizeWrap(rawX, state.width);
    state.player.y = normalizeWrap(rawY, state.height);
    state.movesLeft -= 1;
    state.touchHistory = state.touchHistory.concat([{ x: state.player.x, y: state.player.y }]).slice(-64);

    if (wrapped) {
      state.wraps += 1;
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
      return markLevelFailed(state, 'Coherence collapsed. Reset the braid and try again.');
    }
    if (state.movesLeft <= 0 && !state.activeChallenge && !state.targets.every((item) => item.delivered)) {
      return markLevelFailed(state, 'Out of moves before finishing the braid.');
    }
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
    target.challengeResolved = true;
    target.challengeResult = correct ? 'correct' : 'retry';
    state.challengeHistory = state.challengeHistory.concat([{ targetId: target.id, choiceId, correct }]);
    if (correct) {
      state.score += 60;
      state.coherence = clampCoherence(state.coherence + 6);
      recordLog(state, `${target.label} locked in.`);
    } else {
      state.score = Math.max(0, state.score - 20);
      state.coherence = clampCoherence(state.coherence - 8);
      recordLog(state, `Not quite. ${challenge.explanation}`);
    }
    recordScience(state, `${target.label}: ${challenge.explanation}`);
    state.activeChallenge = null;
    return maybeFinishLevel(next);
  }

  function resetCurrentLevel(campaign) {
    const next = deepCopy(campaign);
    next.current = createLevelState(next.currentLevelIndex);
    return next;
  }

  function jumpToLevel(campaign, levelIndex) {
    const safeIndex = Math.max(0, Math.min(LEVELS.length - 1, levelIndex));
    const next = deepCopy(campaign);
    if (safeIndex > next.unlockedLevelIndex) return next;
    next.currentLevelIndex = safeIndex;
    next.current = createLevelState(safeIndex);
    return next;
  }

  function advanceLevel(campaign) {
    if (!campaign.current.completed) return deepCopy(campaign);
    const nextIndex = Math.min(LEVELS.length - 1, campaign.currentLevelIndex + 1);
    const next = deepCopy(campaign);
    next.currentLevelIndex = nextIndex;
    next.current = createLevelState(nextIndex);
    return next;
  }

  function createTrainingPacket(campaign) {
    const packet = {
      schema: 'psicat-braided-brain-training-v1',
      product: 25,
      runId: campaign.runId,
      createdAt: campaign.createdAt,
      exportedAt: new Date().toISOString(),
      completedLevels: campaign.completedLevelIds.slice(),
      totalScore: campaign.totalScore + (campaign.current.completed ? 0 : campaign.current.score),
      currentLevel: {
        id: campaign.current.levelId,
        label: LEVELS[campaign.current.levelIndex].name,
        completed: campaign.current.completed,
        wraps: campaign.current.wraps,
        coherence: campaign.current.coherence,
      },
      trainingRecords: campaign.trainingRecords.concat(campaign.current.completed ? [] : [levelSummary(campaign.current)]),
      pedagogicalFocus: [
        'toroidal navigation',
        'distributed control',
        'connectome role recognition',
        'explicit epistemic boundaries',
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

  function suggestCoachQuery(campaign) {
    const packet = createTrainingPacket(campaign);
    return [
      'Coach me on the next best move in PsiCat Braided Brain.',
      `Current level: ${packet.currentLevel.label}`,
      `Wraps: ${packet.currentLevel.wraps}, coherence: ${packet.currentLevel.coherence}`,
      `Completed levels: ${packet.completedLevels.join(', ') || 'none yet'}`,
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
    }));
  }

  const api = {
    LEVELS,
    createCampaignState,
    createLevelState,
    movePlayer,
    answerChallenge,
    resetCurrentLevel,
    advanceLevel,
    jumpToLevel,
    createTrainingPacket,
    createJsonlExport,
    suggestCoachQuery,
    getCellRole,
    getLevelDeck,
  };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  }
  global.PsiCatBraidedBrainCore = api;
})(typeof window !== 'undefined' ? window : globalThis);
