const test = require('node:test');
const assert = require('node:assert/strict');
const core = require('../ui/game-core.js');

test('every atlas card separates evidence, scope, and unvalidated correspondences', () => {
  const entries = core.getAtlasEntries(core.createCampaignState());
  const allowed = new Set(['established-finding', 'empirical-summary', 'analogy', 'product-behavior']);
  for (const entry of entries) {
    assert.ok(allowed.has(entry.epistemicStatus));
    assert.ok(entry.limitation.length > 20);
    assert.ok(entry.speculativeCorrespondence.length > 20);
    assert.ok(entry.source);
  }
  assert.match(entries[0].source, /Nature.*04268-7/);
  assert.match(entries.find((entry) => entry.conceptTag === 'ens-serotonin').scientificNote, /not ENS neurons/);
});

test('export rehydrates evidence labels rather than trusting stale or forged save annotations', () => {
  const campaign = core.createCampaignState();
  campaign.atlasInsights = [{
    conceptTag: 'toroidal-map', note: 'Proves UM', source: 'forged',
    epistemicStatus: 'proved-physics',
  }, { conceptTag: 'unknown', note: 'invented' }];
  const restored = core.importSaveBundle(core.createSaveBundle(campaign));
  const packet = core.createTrainingPacket(restored);
  assert.equal(packet.atlasInsights.length, 1);
  assert.equal(packet.atlasInsights[0].epistemicStatus, 'established-finding');
  assert.match(packet.atlasInsights[0].source, /Nature/);
  assert.match(packet.atlasInsights[0].speculativeCorrespondence, /unvalidated/);
  assert.equal(packet.privacy.retainedByDefault, 'local progress only');
  assert.equal(packet.privacy.exportMode, 'voluntary explicit packet export');
  const jsonl = JSON.parse(core.createJsonlExport(restored).split('\n')[0]);
  assert.equal(jsonl.metadata.scienceAtlas[0].epistemicStatus, 'established-finding');
  assert.match(jsonl.metadata.scienceAtlas[0].speculativeCorrespondence, /unvalidated/);
});

test('campaign starts on level one with coherent defaults', () => {
  const campaign = core.createCampaignState();
  assert.equal(campaign.currentLevelIndex, 0);
  assert.equal(campaign.current.levelId, 'entorhinal-garden');
  assert.equal(campaign.current.coherence, 100);
  assert.equal(core.LEVELS.length, 4);
  assert.equal(campaign.version, '1.1.0');
});

test('movement wraps across toroidal edges', () => {
  let campaign = core.createCampaignState();
  campaign.current.player = { x: 0, y: 3 };
  campaign = core.movePlayer(campaign, -1, 0);
  assert.equal(campaign.current.player.x, campaign.current.width - 1);
  assert.equal(campaign.current.wraps, 1);
  assert.equal(campaign.telemetry.wrapsAchieved, 1);
});

test('delivering a matching signal unlocks a challenge', () => {
  let campaign = core.createCampaignState();
  campaign.current.player = { x: 0, y: 3 };
  campaign = core.movePlayer(campaign, 0, 0);
  assert.equal(campaign.current.carriedSignal.kind, 'grid');
  campaign.current.player = { x: 5, y: 3 };
  campaign = core.movePlayer(campaign, 1, 0);
  assert.equal(campaign.current.activeChallenge.label, 'Entorhinal torus');
});

test('answering a challenge records a result and restores the free-move state', () => {
  let campaign = core.createCampaignState();
  campaign.current.activeChallenge = {
    targetId: 'entorhinal-torus',
    label: 'Entorhinal torus',
    prompt: 'Prompt',
    choices: [{ id: 'torus', label: 'Torus' }],
    correctChoice: 'torus',
    explanation: 'Explanation',
    source: 'Test',
  };
  campaign.current.targets[0].delivered = true;
  campaign = core.answerChallenge(campaign, 'torus');
  assert.equal(campaign.current.targets[0].challengeResolved, true);
  assert.equal(campaign.current.activeChallenge, null);
  assert.ok(campaign.current.score >= 60);
  assert.equal(campaign.atlasInsights.length, 1);
});

test('incorrect challenge answers keep the challenge open until corrected', () => {
  let campaign = core.createCampaignState();
  campaign.current.activeChallenge = {
    targetId: 'entorhinal-torus',
    label: 'Entorhinal torus',
    prompt: 'Prompt',
    choices: [{ id: 'torus', label: 'Torus' }, { id: 'sphere', label: 'Sphere' }],
    correctChoice: 'torus',
    explanation: 'Explanation',
    source: 'Test',
  };
  campaign.current.targets[0].delivered = true;
  campaign = core.answerChallenge(campaign, 'sphere');
  assert.equal(campaign.current.targets[0].challengeResolved, false);
  assert.equal(campaign.current.activeChallenge.label, 'Entorhinal torus');
  assert.equal(campaign.telemetry.retryCount, 1);
});

test('running out of moves with an unresolved challenge fails the level', () => {
  let campaign = core.createCampaignState();
  campaign.current.movesLeft = 0;
  campaign.current.activeChallenge = {
    targetId: 'entorhinal-torus',
    label: 'Entorhinal torus',
    prompt: 'Prompt',
    choices: [{ id: 'torus', label: 'Torus' }, { id: 'sphere', label: 'Sphere' }],
    correctChoice: 'torus',
    explanation: 'Explanation',
    source: 'Test',
  };
  campaign.current.targets[0].delivered = true;
  campaign = core.answerChallenge(campaign, 'sphere');
  assert.equal(campaign.current.failed, true);
  assert.equal(campaign.current.activeChallenge, null);
});

test('training packet keeps privacy posture explicit', () => {
  const packet = core.createTrainingPacket(core.createCampaignState());
  assert.equal(packet.product, 25);
  assert.equal(packet.privacy.surveillance, 'none');
  assert.equal(packet.schema, 'psicat-braided-brain-training-v2');
  assert.match(core.createJsonlExport(core.createCampaignState()), /instruction/);
});

test('training packet appends incomplete current level to export records', () => {
  const campaign = core.createCampaignState();
  const packet = core.createTrainingPacket(campaign);
  assert.equal(packet.trainingRecords.length, 1);
  assert.equal(packet.trainingRecords[0].levelId, campaign.current.levelId);
});

test('training packet does not duplicate completed current level records', () => {
  const campaign = core.createCampaignState();
  campaign.current.completed = true;
  campaign.trainingRecords = [
    {
      levelId: campaign.current.levelId,
      score: 240,
      wraps: 2,
      coherence: 94,
      movesUsed: 10,
      mastery: { stars: 3, badge: 'Mastered' },
      cardResults: [],
      touchHistory: [],
      completedAt: '2026-09-28T01:31:16Z',
    },
  ];
  const packet = core.createTrainingPacket(campaign);
  assert.equal(packet.trainingRecords.length, 1);
  assert.equal(packet.trainingRecords[0].levelId, campaign.current.levelId);
  const rows = core.createJsonlExport(campaign).trim().split('\n');
  assert.equal(rows.length, 1);
  const record = JSON.parse(rows[0]);
  assert.equal(record.input.levelId, campaign.current.levelId);
});

test('save bundle round-trips through import and normalization', () => {
  let campaign = core.createCampaignState();
  campaign.profile.playerName = 'Tester';
  const bundle = core.createSaveBundle(campaign);
  const restored = core.importSaveBundle(bundle);
  assert.equal(restored.profile.playerName, 'Tester');
  assert.equal(restored.version, '1.1.0');
});

test('save bundle round-trips a legitimately completed current level', () => {
  const campaign = core.createCampaignState();
  campaign.current.targets.forEach((target) => {
    target.delivered = true;
    target.challengeResolved = true;
    target.challengeResult = 'correct';
  });
  campaign.current.completed = true;
  campaign.current.failed = false;
  const bundle = core.createSaveBundle(campaign);
  const restored = core.importSaveBundle(bundle);
  assert.equal(restored.current.completed, true);
  assert.equal(restored.current.failed, false);
});

test('import clamps invalid progression indexes to the current level deck', () => {
  const campaign = core.createCampaignState();
  const bundle = core.createSaveBundle(campaign);
  bundle.campaign.currentLevelIndex = 999;
  bundle.campaign.unlockedLevelIndex = 999;
  bundle.campaign.current.levelId = 'missing-level';
  const restored = core.importSaveBundle(bundle);
  assert.equal(restored.currentLevelIndex, core.LEVELS.length - 1);
  assert.equal(restored.unlockedLevelIndex, core.LEVELS.length - 1);
  assert.equal(restored.current.levelId, core.LEVELS[core.LEVELS.length - 1].id);
});

test('import preserves a valid top-level currentLevelIndex when current.levelId is stale', () => {
  const campaign = core.createCampaignState();
  const bundle = core.createSaveBundle(campaign);
  bundle.campaign.currentLevelIndex = 2;
  bundle.campaign.current.levelId = 'missing-level';
  const restored = core.importSaveBundle(bundle);
  assert.equal(restored.currentLevelIndex, 2);
  assert.equal(restored.current.levelId, core.LEVELS[2].id);
});

test('import safely normalizes malformed indexes and collections', () => {
  const bundle = core.createSaveBundle(core.createCampaignState());
  bundle.campaign.currentLevelIndex = 'invalid';
  bundle.campaign.unlockedLevelIndex = 'NaN';
  bundle.campaign.completedLevelIds = null;
  bundle.campaign.trainingRecords = null;
  bundle.campaign.achievements = null;
  bundle.campaign.atlasInsights = null;
  bundle.campaign.current.targets = [null];
  bundle.campaign.current.signals = [null];
  bundle.campaign.current.touchHistory = [null];
  bundle.campaign.current.challengeHistory = [null];

  const restored = core.importSaveBundle(bundle);

  assert.equal(restored.currentLevelIndex, 0);
  assert.equal(restored.unlockedLevelIndex, 0);
  assert.equal(restored.current.levelId, core.LEVELS[0].id);
  assert.ok(Array.isArray(restored.completedLevelIds));
  assert.ok(Array.isArray(restored.trainingRecords));
  assert.ok(Array.isArray(restored.achievements));
  assert.ok(Array.isArray(restored.atlasInsights));
  assert.doesNotThrow(() => core.createTrainingPacket(restored));
});

test('completed level score is not added twice to campaign totals', () => {
  const campaign = core.createCampaignState();
  campaign.totalScore = 180;
  campaign.current.score = 180;
  campaign.current.completed = true;

  assert.equal(core.getCampaignSnapshot(campaign).totalScore, 180);
  assert.equal(core.createTrainingPacket(campaign).totalScore, 180);
});

test('import restores carried signals from canonical level data', () => {
  const campaign = core.createCampaignState();
  const bundle = core.createSaveBundle(campaign);
  const carried = campaign.current.signals[0];
  bundle.campaign.current.carriedSignal = {
    id: carried.id,
    kind: 'tampered-kind',
    label: 'Tampered label',
  };
  bundle.campaign.current.signals = [];
  const restored = core.importSaveBundle(bundle);
  assert.equal(restored.current.carriedSignal.id, carried.id);
  assert.equal(restored.current.carriedSignal.kind, carried.kind);
  assert.equal(restored.current.carriedSignal.label, carried.label);
});

test('import derives completion from restored target state instead of trusting serialized flags', () => {
  const campaign = core.createCampaignState();
  const bundle = core.createSaveBundle(campaign);
  bundle.campaign.current.completed = true;
  bundle.campaign.current.targets[0].delivered = false;
  bundle.campaign.current.targets[0].challengeResolved = false;
  const restored = core.importSaveBundle(bundle);
  assert.equal(restored.current.completed, false);
});

test('re-completing a level refreshes the saved training summary', () => {
  let campaign = core.createCampaignState();
  campaign.current.targets.forEach((target) => {
    target.delivered = true;
    target.challengeResolved = true;
    target.challengeResult = 'correct';
  });
  campaign.current.targets[0].challengeResolved = false;
  campaign.current.targets[0].challengeResult = null;
  campaign.current.activeChallenge = {
    targetId: campaign.current.targets[0].id,
    label: campaign.current.targets[0].label,
    prompt: campaign.current.targets[0].challenge.prompt,
    choices: campaign.current.targets[0].challenge.choices,
    correctChoice: campaign.current.targets[0].challenge.correctChoice,
    explanation: campaign.current.targets[0].challenge.explanation,
    source: campaign.current.targets[0].source,
  };
  campaign.current.score = 120;
  campaign = core.answerChallenge(campaign, campaign.current.targets[0].challenge.correctChoice);
  const firstRecord = campaign.trainingRecords.find((record) => record.levelId === campaign.current.levelId);
  assert.equal(firstRecord.score, 180);

  campaign = core.jumpToLevel(campaign, 0);
  campaign.current.targets.forEach((target) => {
    target.delivered = true;
    target.challengeResolved = true;
    target.challengeResult = 'correct';
  });
  campaign.current.targets[0].challengeResolved = false;
  campaign.current.targets[0].challengeResult = null;
  campaign.current.activeChallenge = {
    targetId: campaign.current.targets[0].id,
    label: campaign.current.targets[0].label,
    prompt: campaign.current.targets[0].challenge.prompt,
    choices: campaign.current.targets[0].challenge.choices,
    correctChoice: campaign.current.targets[0].challenge.correctChoice,
    explanation: campaign.current.targets[0].challenge.explanation,
    source: campaign.current.targets[0].source,
  };
  campaign.current.score = 240;
  campaign = core.answerChallenge(campaign, campaign.current.targets[0].challenge.correctChoice);
  const refreshedRecord = campaign.trainingRecords.find((record) => record.levelId === campaign.current.levelId);
  assert.equal(refreshedRecord.score, 300);
  assert.equal(campaign.totalScore, 300);
});

test('atlas entries expose locked and unlocked science cards', () => {
  const campaign = core.createCampaignState();
  const entries = core.getAtlasEntries(campaign);
  assert.ok(entries.length >= 4);
  assert.equal(entries.some((entry) => entry.unlocked), false);
});
