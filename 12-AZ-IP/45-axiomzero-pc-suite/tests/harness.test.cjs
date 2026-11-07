const test = require("node:test");
const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { POLICY, ResearchHarness, searchCatalog, evidenceReport, composeReport } = require("../lib/harness.cjs");
const { buildCollection, saveCollection } = require("../lib/knowledge.cjs");
const { searchEvidence } = require("../lib/worker-search.cjs");

function fixture(t, tools = {}, options) {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "p45-harness-"));
  t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
  const file = path.join(directory, "harness.json");
  const calls = [];
  const handlers = Object.fromEntries(POLICY.tools.map((tool) => [tool, (request) => {
    calls.push(tool);
    return `${tool}: ${request.goal}`;
  }]));
  const harness = new ResearchHarness(file, { ...handlers, ...tools }, options);
  return { harness, file, directory, calls, handlers };
}

test("plan and results are durable, dependency-ordered and always unverified", async (t) => {
  const { harness, file, calls, handlers } = fixture(t);
  const run = harness.create({ goal: "PsiCat offline memory" });
  assert.equal(run.epistemicLabel, "UNVERIFIED");
  assert.equal(run.steps.length, 3);
  assert.deepEqual(calls, []);
  for (const tool of ["catalog.search", "evidence.search", "report.compose"]) {
    const proposal = harness.proposal(run.id);
    assert.equal(proposal.tool, tool);
    await harness.execute(proposal, async () => true);
  }
  assert.deepEqual(calls, ["catalog.search", "evidence.search", "report.compose"]);
  const restored = new ResearchHarness(file, handlers);
  assert.equal(restored.get(run.id).status, "completed");
  assert.equal(restored.get(run.id).attempts, 3);
  assert.throws(() => restored.proposal(run.id), /already finished/);
  const exported = restored.export(run.id);
  assert.equal(exported.run.steps[2].output, "report.compose: PsiCat offline memory");
  assert.equal(exported.events.length, 7);
  assert.ok(exported.events.every((event) => /^[0-9a-f]{64}$/.test(event.hash)));
});

test("approval is explicit, step-bound, non-replayable and denied by default", async (t) => {
  const { harness, calls } = fixture(t);
  const run = harness.create({ goal: "local models" });
  const proposal = harness.proposal(run.id);
  await harness.execute(proposal, async () => false);
  assert.deepEqual(calls, []);
  assert.equal(harness.get(run.id).attempts, 0);
  assert.equal(harness.snapshot().events.at(-1).action, "approval-declined");
  await assert.rejects(harness.execute(harness.proposal(run.id)), /approval callback/);
  await harness.execute(harness.proposal(run.id), async () => true);
  await assert.rejects(harness.execute(proposal, async () => true), /plan changed/i);
  assert.deepEqual(calls, ["catalog.search"]);
});

test("unknown tools, malformed goals/models and changed proposals are refused", async (t) => {
  const { harness } = fixture(t);
  for (const goal of ["", "?", "x".repeat(401), null]) assert.throws(() => harness.create({ goal }));
  for (const model of ["", "../bad model", "http://host name", "x".repeat(81), 3]) {
    assert.throws(() => harness.create({ goal: "memory", model }), /model/);
  }
  const run = harness.create({ goal: "memory", model: "llama3.2:3b" });
  const proposal = harness.proposal(run.id);
  await assert.rejects(harness.execute({ ...proposal, tool: "shell.run" }, async () => true), /plan changed/i);
  delete harness.tools["catalog.search"];
  assert.throws(() => harness.proposal(run.id), /unavailable or denied/);
});

test("only one step or approval dialog can occupy the execution slot", async (t) => {
  const { harness, calls } = fixture(t);
  const first = harness.create({ goal: "first task" });
  const second = harness.create({ goal: "second task" });
  let approve;
  const executing = harness.execute(harness.proposal(first.id), () => new Promise((resolve) => { approve = resolve; }));
  assert.throws(() => harness.proposal(second.id), /active/);
  harness.stop(first.id);
  approve(true);
  await executing;
  assert.deepEqual(calls, []);
  assert.equal(harness.get(first.id).status, "paused");
  await harness.execute(harness.proposal(second.id), async () => true);
});

test("pause and cancellation abort work and ignore late results", async (t) => {
  let finish;
  let signal;
  const { harness } = fixture(t, {
    "catalog.search": (request) => {
      signal = request.signal;
      return new Promise((resolve) => { finish = resolve; });
    }
  });
  const run = harness.create({ goal: "memory" });
  const executing = harness.execute(harness.proposal(run.id), async () => true);
  await new Promise((resolve) => setImmediate(resolve));
  harness.stop(run.id, true);
  assert.equal(signal.aborted, true);
  finish("late output");
  await executing;
  assert.equal(harness.get(run.id).status, "cancelled");
  assert.equal(harness.get(run.id).steps[0].output, null);
  harness.remove(run.id);
  assert.equal(harness.snapshot().runs.length, 0);
  assert.equal(harness.snapshot().events.at(-1).action, "removed");
});

test("failures are visible, retries require new approval and six attempts is a hard cap", async (t) => {
  const { harness } = fixture(t, {
    "catalog.search": () => { throw new Error("provider unavailable"); }
  });
  const run = harness.create({ goal: "memory" });
  for (let index = 0; index < 6; index++) {
    await assert.rejects(harness.execute(harness.proposal(run.id), async () => true), /provider unavailable/);
    assert.equal(harness.get(run.id).status, "failed");
    assert.equal(harness.get(run.id).steps[0].error, "provider unavailable");
    assert.equal(harness.get(run.id).attempts, index + 1);
  }
  assert.throws(() => harness.proposal(run.id), /budget is exhausted/);
});

test("timeouts abort tool signals and preserve an explicit failed checkpoint", async (t) => {
  let signal;
  const { harness } = fixture(t, {
    "catalog.search": (request) => { signal = request.signal; return new Promise(() => {}); }
  }, { timeoutMs: 10 });
  const run = harness.create({ goal: "memory" });
  await assert.rejects(harness.execute(harness.proposal(run.id), async () => true), /deadline/);
  assert.equal(signal.aborted, true);
  assert.equal(harness.get(run.id).status, "failed");
  assert.equal(harness.active, null);
});

test("external long-budget reasoning remains cancellable after the ordinary deadline", async (t) => {
  t.mock.timers.enable({ apis: ["setTimeout"] });
  let signal;
  const { harness } = fixture(t, {
    "model.reason": (request) => { signal = request.signal; return new Promise(() => {}); }
  });
  const run = harness.create({ goal: "PsiCat memory", model: "operator-27b:iq3" });
  for (let step = 0; step < 3; step++) await harness.execute(harness.proposal(run.id), async () => true);
  const pending = harness.execute(harness.proposal(run.id), async () => true);
  await new Promise((resolve) => setImmediate(resolve));
  t.mock.timers.tick(POLICY.stepTimeoutMs);
  assert.equal(signal.aborted, false);
  harness.stop(run.id, true);
  await pending;
  assert.equal(signal.aborted, true);
  assert.equal(harness.get(run.id).status, "cancelled");
  assert.equal(harness.active, null);
});

test("explicitly selected embedded and external reasoning get eighteen minutes; other steps keep sixty seconds", async (t) => {
  t.mock.timers.enable({ apis: ["setTimeout"] });
  for (const model of ["psicat:embedded", "llama3.2:3b"]) {
    let signal;
    const { harness } = fixture(t, {
      "model.reason": (request) => { signal = request.signal; return new Promise(() => {}); }
    });
    const run = harness.create({ goal: "PsiCat offline memory", model });
    for (let step = 0; step < 3; step++) await harness.execute(harness.proposal(run.id), async () => true);
    const proposal = harness.proposal(run.id);
    assert.match(proposal.disclosure, /eighteen-minute (?:total )?deadline/);
    const pending = assert.rejects(harness.execute(proposal, async () => true), /deadline/);
    await new Promise((resolve) => setImmediate(resolve));
    t.mock.timers.tick(POLICY.stepTimeoutMs);
    assert.equal(signal.aborted, false);
    const deadline = model === "psicat:embedded" ? POLICY.embeddedStepTimeoutMs : POLICY.externalStepTimeoutMs;
    t.mock.timers.tick(deadline - POLICY.stepTimeoutMs - 1);
    assert.equal(signal.aborted, false);
    t.mock.timers.tick(1);
    await pending;
    assert.equal(signal.aborted, true);
    assert.equal(harness.get(run.id).status, "failed");
  }
});

test("oversized or empty output is a failure, not a success-shaped fallback", async (t) => {
  const { harness } = fixture(t, { "catalog.search": () => "x".repeat(POLICY.maxResultChars + 1) });
  const run = harness.create({ goal: "memory" });
  await assert.rejects(harness.execute(harness.proposal(run.id), async () => true), /result budget/);
  harness.tools["catalog.search"] = () => "";
  await assert.rejects(harness.execute(harness.proposal(run.id), async () => true), /empty/);
});

test("restart recovers interrupted work without replay or retained approval", async (t) => {
  const { harness, file, handlers, calls } = fixture(t, { "catalog.search": () => new Promise(() => {}) });
  const run = harness.create({ goal: "memory" });
  const executing = harness.execute(harness.proposal(run.id), async () => true);
  await new Promise((resolve) => setImmediate(resolve));
  const restored = new ResearchHarness(file, handlers);
  assert.equal(restored.get(run.id).status, "interrupted");
  assert.equal(restored.get(run.id).steps[0].status, "pending");
  assert.equal(restored.get(run.id).attempts, 1);
  assert.deepEqual(calls, []);
  assert.equal(restored.snapshot().events.at(-1).action, "recovered");
  harness.stop(run.id);
  await executing;
});

test("audit and checkpoint tampering fails closed instead of resetting memory", async (t) => {
  const { harness, file, handlers } = fixture(t);
  const run = harness.create({ goal: "memory" });
  await harness.execute(harness.proposal(run.id), async () => true);
  const original = fs.readFileSync(file, "utf8");
  const state = JSON.parse(original);
  state.events[0].detail = "altered";
  fs.writeFileSync(file, JSON.stringify(state));
  assert.throws(() => new ResearchHarness(file, handlers), /audit chain/);
  const changed = JSON.parse(original);
  changed.runs[0].steps[0].output = "altered checkpoint";
  fs.writeFileSync(file, JSON.stringify(changed));
  assert.throws(() => new ResearchHarness(file, handlers), /audit seal/);
  fs.writeFileSync(file, "{bad");
  assert.throws(() => new ResearchHarness(file, handlers));
});

test("failed persistence does not acknowledge a task or consume an attempt", (t) => {
  const { harness, directory } = fixture(t);
  harness.file = directory;
  assert.throws(() => harness.create({ goal: "memory" }));
  assert.equal(harness.snapshot().runs.length, 0);
});

test("saved task cap requires explicit terminal removal; exports are local data", (t) => {
  const { harness } = fixture(t);
  for (let i = 0; i < POLICY.maxRuns; i++) harness.create({ goal: `research ${i}` });
  assert.throws(() => harness.create({ goal: "extra research" }), /at most 50/);
  const id = harness.snapshot().runs[0].id;
  assert.throws(() => harness.remove(id), /Cancel or finish/);
  harness.stop(id, true);
  assert.equal(harness.export(id).run.goal, "research 0");
  harness.remove(id);
  harness.create({ goal: "new research" });
  assert.equal(harness.snapshot().runs.length, POLICY.maxRuns);
});

test("context compression is explicit, bounded and preserves full checkpoints", async (t) => {
  const { harness } = fixture(t, { "catalog.search": () => "a".repeat(20000) });
  const run = harness.create({ goal: "memory", model: "llama3.2:3b" });
  await harness.execute(harness.proposal(run.id), async () => true);
  const next = harness.proposal(run.id);
  assert.equal(next.context.length, POLICY.maxContextChars);
  assert.equal(next.contextTruncated, true);
  assert.equal(harness.get(run.id).steps[0].output.length, 20000);
});

test("bounded audit retention preserves its hash anchor and survives restart", async (t) => {
  const { harness, file, handlers } = fixture(t);
  const run = harness.create({ goal: "memory" });
  // Build a large valid history without 2,000 disk writes.
  harness.commit((state) => {
    const item = state.runs[0];
    for (let i = 0; i < POLICY.maxEvents + 5; i++) harness.record(state, item, "approval-declined", "operator declined");
  });
  assert.equal(harness.snapshot().events.length, POLICY.maxEvents);
  assert.notEqual(harness.snapshot().auditAnchor, "0".repeat(64));
  assert.equal(new ResearchHarness(file, handlers).get(run.id).goal, "memory");
  const exported = harness.export(run.id);
  for (const event of exported.events) {
    const { hash, ...body } = event;
    assert.equal(hash, crypto.createHash("sha256").update(JSON.stringify(body)).digest("hex"));
  }
});

test("catalog/evidence reports retain references and do not invent missing evidence", () => {
  const catalog = searchCatalog([{ id: "20", name: "PsiCat", description: "Offline memory", folder: "12-AZ-IP/20-psicat-navigator/" }], "PsiCat");
  assert.match(catalog, /20-psicat-navigator\/README.md/);
  assert.match(searchCatalog([], "no evidence"), /Catalog matches: 0/);
  assert.match(evidenceReport({ totalMatches: 0, results: [] }, []), /No imported evidence/);
  assert.match(composeReport({ goal: "memory", context: catalog, contextTruncated: false }), /not an inferred answer or proof/);
});

test("evidence search runs in a cancellable worker with persisted source citations", async (t) => {
  const { directory } = fixture(t);
  const source = path.join(directory, "source");
  fs.mkdirSync(source);
  fs.writeFileSync(path.join(source, "mind.txt"), "PsiCat offline memory\nsource evidence\n");
  const collection = await buildCollection(source);
  const indices = path.join(directory, "indices");
  saveCollection(indices, collection);
  const controller = new AbortController();
  const report = await searchEvidence({ directory: indices, ids: [collection.id], goal: "memory", signal: controller.signal });
  assert.match(report, /mind.txt:1-2/);
  assert.match(report, new RegExp(collection.files[0].sha256));
  controller.abort(new Error("cancelled"));
  await assert.rejects(searchEvidence({ directory: indices, ids: [], goal: "memory", signal: controller.signal }), /cancelled/);
});

test("worker errors and in-flight cancellation are explicit", async (t) => {
  const { directory } = fixture(t);
  await assert.rejects(searchEvidence({
    directory, ids: [crypto.randomUUID()], goal: "memory", signal: new AbortController().signal
  }), /could not be read/);
  const controller = new AbortController();
  const pending = searchEvidence({ directory, ids: [], goal: "memory", signal: controller.signal });
  controller.abort(new Error("operator pause"));
  await assert.rejects(pending, /operator pause/);
});
