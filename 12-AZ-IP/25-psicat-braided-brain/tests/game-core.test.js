const test = require('node:test');
const assert = require('node:assert/strict');
const core = require('../ui/game-core.js');

test('campaign starts on level one with coherent defaults', () => {
  const campaign = core.createCampaignState();
  assert.equal(campaign.currentLevelIndex, 0);
  assert.equal(campaign.current.levelId, 'entorhinal-garden');
  assert.equal(campaign.current.coherence, 100);
  assert.equal(core.LEVELS.length, 4);
});

test('movement wraps across toroidal edges', () => {
  let campaign = core.createCampaignState();
  campaign.current.player = { x: 0, y: 3 };
  campaign = core.movePlayer(campaign, -1, 0);
  assert.equal(campaign.current.player.x, campaign.current.width - 1);
  assert.equal(campaign.current.wraps, 1);
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
});

test('training packet keeps privacy posture explicit', () => {
  const packet = core.createTrainingPacket(core.createCampaignState());
  assert.equal(packet.product, 25);
  assert.equal(packet.privacy.surveillance, 'none');
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
