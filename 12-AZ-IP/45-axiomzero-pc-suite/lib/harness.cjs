const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");

const POLICY = Object.freeze({
  version: "axiomzero-research-policy-v1",
  tools: ["catalog.search", "evidence.search", "report.compose", "model.reason"],
  maxRuns: 50,
  maxAttempts: 6,
  maxResultChars: 24000,
  maxContextChars: 12000,
  maxEvents: 2000,
  stepTimeoutMs: 60000,
  embeddedStepTimeoutMs: 1080000,
  epistemicLabel: "UNVERIFIED"
});
const SCHEMA = "axiomzero-research-harness-v1";
const MAX_STORE_BYTES = 16 * 1024 * 1024;
const ID = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;
const HASH = /^[0-9a-f]{64}$/;
const TERMINAL = new Set(["completed", "cancelled"]);
const RUN_STATUSES = new Set(["pending", "running", "paused", "interrupted", "failed", ...TERMINAL]);
const STEP_STATUSES = new Set(["pending", "running", "completed", "failed"]);
const clone = (value) => JSON.parse(JSON.stringify(value));
const digest = (value) => crypto.createHash("sha256").update(JSON.stringify(value)).digest("hex");

function validateGoal(goal) {
  if (typeof goal !== "string" || goal.trim().length === 0 || goal.length > 400 ||
      !/[\p{L}\p{N}_-]{2,}/u.test(goal)) {
    throw new TypeError("Enter a research goal of 1-400 characters containing a word or identifier.");
  }
  return goal.trim();
}

function validateModel(model) {
  if (typeof model !== "string" || model.length > 80 ||
      !/^[A-Za-z0-9][A-Za-z0-9_.:/-]*$/.test(model)) {
    throw new TypeError("Enter psicat:embedded or the exact name of an installed Ollama model (1-80 characters).");
  }
  return model;
}

function expectedTools(model) {
  return ["catalog.search", "evidence.search", "report.compose", ...(model ? ["model.reason"] : [])];
}

function validateRun(run) {
  return run && ID.test(run.id) &&
    typeof run.goal === "string" && run.goal.length <= 400 && run.goal.trim().length > 0 &&
    (run.model === null || (typeof run.model === "string" && run.model.length <= 80 &&
      /^[A-Za-z0-9][A-Za-z0-9_.:/-]*$/.test(run.model))) &&
    run.epistemicLabel === POLICY.epistemicLabel && run.policyVersion === POLICY.version &&
    RUN_STATUSES.has(run.status) && typeof run.createdAt === "string" &&
    typeof run.updatedAt === "string" && Number.isInteger(run.attempts) &&
    run.attempts >= 0 && run.attempts <= POLICY.maxAttempts &&
    Array.isArray(run.steps) && run.steps.length === expectedTools(run.model).length &&
    run.steps.every((step, index) => step && step.tool === expectedTools(run.model)[index] &&
      STEP_STATUSES.has(step.status) &&
      (step.output === null || (typeof step.output === "string" &&
        step.output.length <= POLICY.maxResultChars)) &&
      (step.error === null || (typeof step.error === "string" && step.error.length <= 1000)) &&
      (step.status !== "completed" || step.output !== null) &&
      (step.status !== "failed" || step.error !== null)) &&
    run.steps.every((step, index) =>
      step.status !== "completed" || run.steps.slice(0, index).every((prior) => prior.status === "completed")) &&
    (run.status !== "completed" || run.steps.every((step) => step.status === "completed"));
}

function eventHash(event) {
  const { hash, ...body } = event;
  return digest(body);
}

function validateState(state) {
  if (!state || state.schema !== SCHEMA || state.policyVersion !== POLICY.version ||
      !Array.isArray(state.runs) || state.runs.length > POLICY.maxRuns ||
      !state.runs.every(validateRun) || new Set(state.runs.map((run) => run.id)).size !== state.runs.length ||
      !Array.isArray(state.events) || state.events.length > POLICY.maxEvents ||
      !Number.isSafeInteger(state.nextSequence) || state.nextSequence < 1 ||
      !HASH.test(state.auditAnchor)) {
    throw new Error("Harness checkpoint format or policy version is invalid.");
  }
  let previous = state.auditAnchor;
  let sequence = state.nextSequence - state.events.length;
  const latest = new Map();
  for (const event of state.events) {
    if (!event || event.sequence !== sequence++ || event.previousHash !== previous ||
        !ID.test(event.runId) || typeof event.at !== "string" ||
        typeof event.action !== "string" || typeof event.detail !== "string" ||
        event.detail.length > 1000 || !HASH.test(event.checkpointHash) ||
        !HASH.test(event.hash) || eventHash(event) !== event.hash) {
      throw new Error("Harness audit chain is invalid; the checkpoint was not loaded.");
    }
    previous = event.hash;
    latest.set(event.runId, event);
  }
  if (state.runs.filter((run) => run.status === "running").length > 1 ||
      state.runs.some((run) => latest.has(run.id) && latest.get(run.id).checkpointHash !== digest(run))) {
    throw new Error("Harness task checkpoint does not match its audit seal.");
  }
}

class ResearchHarness {
  constructor(file, tools, { timeoutMs } = {}) {
    this.file = file;
    this.tools = tools;
    this.timeoutMs = timeoutMs ?? POLICY.stepTimeoutMs;
    this.embeddedTimeoutMs = timeoutMs ?? POLICY.embeddedStepTimeoutMs;
    this.active = null;
    this.state = {
      schema: SCHEMA, policyVersion: POLICY.version, runs: [], events: [],
      auditAnchor: "0".repeat(64), nextSequence: 1
    };
    if (fs.existsSync(file)) {
      if (fs.statSync(file).size > MAX_STORE_BYTES) throw new Error("Harness checkpoint exceeds 16 MiB.");
      this.state = JSON.parse(fs.readFileSync(file, "utf8"));
      validateState(this.state);
    }
    const interrupted = this.state.runs.filter((run) => run.status === "running");
    if (interrupted.length) this.commit((state) => {
      for (const prior of interrupted) {
        const run = state.runs.find((item) => item.id === prior.id);
        run.status = "interrupted";
        for (const step of run.steps) if (step.status === "running") step.status = "pending";
        this.record(state, run, "recovered", "Execution interrupted. A fresh approval is required; no automatic replay.");
      }
    });
  }

  commit(change) {
    const next = clone(this.state);
    change(next);
    validateState(next);
    const serialized = `${JSON.stringify(next)}\n`;
    if (Buffer.byteLength(serialized) > MAX_STORE_BYTES) throw new Error("Harness checkpoint exceeds 16 MiB.");
    fs.mkdirSync(path.dirname(this.file), { recursive: true });
    const temporary = `${this.file}.tmp`;
    fs.writeFileSync(temporary, serialized, { mode: 0o600 });
    fs.renameSync(temporary, this.file);
    this.state = next;
  }

  record(state, run, action, detail) {
    run.updatedAt = new Date().toISOString();
    const event = {
      sequence: state.nextSequence++, runId: run.id, at: run.updatedAt,
      action, detail: detail.slice(0, 1000),
      checkpointHash: digest(run),
      previousHash: state.events.at(-1)?.hash || state.auditAnchor
    };
    event.hash = eventHash(event);
    state.events.push(event);
    if (state.events.length > POLICY.maxEvents) state.auditAnchor = state.events.shift().hash;
  }

  get(id) {
    if (typeof id !== "string" || !ID.test(id)) throw new TypeError("Harness task identifier is invalid.");
    const run = this.state.runs.find((item) => item.id === id);
    if (!run) throw new Error("That harness task is no longer available.");
    return clone(run);
  }

  snapshot() {
    return { policy: clone(POLICY), ...clone(this.state), activeRunId: this.active?.id || null };
  }

  create({ goal, model = null }) {
    goal = validateGoal(goal);
    if (model !== null) model = validateModel(model);
    if (this.state.runs.length >= POLICY.maxRuns) {
      throw new Error("The harness holds at most 50 tasks. Export and remove a finished task first.");
    }
    const now = new Date().toISOString();
    const run = {
      id: crypto.randomUUID(), goal, model, status: "pending", attempts: 0,
      epistemicLabel: POLICY.epistemicLabel, policyVersion: POLICY.version,
      createdAt: now, updatedAt: now,
      steps: expectedTools(model).map((tool) => ({ tool, status: "pending", output: null, error: null }))
    };
    this.commit((state) => {
      state.runs.push(run);
      this.record(state, run, "created", "Read-only research plan created. Each step requires native operator approval.");
    });
    return this.get(run.id);
  }

  proposal(id) {
    const run = this.get(id);
    if (this.active) throw new Error("Another harness step is active. Pause or cancel it before starting work.");
    if (TERMINAL.has(run.status)) throw new Error("That task is already finished.");
    if (run.attempts >= POLICY.maxAttempts) throw new Error("The six-attempt budget is exhausted. No automatic retries are allowed.");
    const index = run.steps.findIndex((step) => step.status !== "completed");
    const step = run.steps[index];
    if (!step || !POLICY.tools.includes(step.tool) || typeof this.tools[step.tool] !== "function") {
      throw new Error("The requested tool is unavailable or denied by harness policy.");
    }
    const previous = step.tool === "model.reason" ? run.steps.slice(index - 1, index) : run.steps.slice(0, index);
    const context = previous.map((prior) =>
      `[${prior.tool}]\n${prior.output}`
    ).join("\n\n");
    return {
      runId: run.id, index, tool: step.tool, goal: run.goal, model: run.model,
      context: context.slice(0, POLICY.maxContextChars),
      contextTruncated: context.length > POLICY.maxContextChars,
      checkpointHash: digest(run),
      disclosure: step.tool === "model.reason"
        ? run.model === "psicat:embedded"
          ? "Run the bundled CPU Qwen/llama.cpp instruction backend with the goal and up to 1,200 UTF-8 bytes of prior results as quoted evidence [E1]. This CPU step has an eighteen-minute deadline, including startup and a shared fifteen-minute inference budget; cancellation remains available. No cloud or external model service is contacted. The report checkpoint retains the answer. Model output is unverified; citations do not establish entailment."
          : `Send the goal and at most 12,000 characters of prior results to Ollama at 127.0.0.1:11434 using "${run.model}". The local service controls its own retention. Model output is unverified.`
        : "Read only the bundled catalog or imported local index, or compose their evidence report. No source writes, shell commands, cloud requests, or epistemic promotion."
    };
  }

  async execute(proposal, approve) {
    const current = this.proposal(proposal.runId);
    if (digest(current) !== digest(proposal)) throw new Error("The plan changed. Review the current step before approval.");
    if (typeof approve !== "function") throw new Error("An operator approval callback is required.");
    // Hold the execution slot while the native approval dialog is open.
    const controller = new AbortController();
    const token = { id: current.runId, controller };
    this.active = token;
    let timer;
    let started = false;
    try {
      const approved = await approve(clone(current));
      if (controller.signal.aborted) return this.get(current.runId);
      if (digest(this.get(current.runId)) !== current.checkpointHash) {
        throw new Error("The task changed while approval was pending. Approval has expired.");
      }
      if (approved !== true) {
        this.commit((state) => this.record(state, state.runs.find((run) => run.id === current.runId),
          "approval-declined", `${current.tool}: operator did not approve execution.`));
        return this.get(current.runId);
      }
      this.commit((state) => {
        const run = state.runs.find((item) => item.id === current.runId);
        run.status = "running";
        run.attempts++;
        run.steps[current.index].status = "running";
        run.steps[current.index].error = null;
        this.record(state, run, "approved-start", `${current.tool}: explicit operator approval; attempt ${run.attempts}/6.`);
      });
      started = true;
      const timeout = new Promise((_, reject) => {
        timer = setTimeout(() => {
          const error = new Error("Harness step exceeded its execution deadline.");
          controller.abort(error);
          reject(error);
        }, current.tool === "model.reason" && current.model === "psicat:embedded"
          ? this.embeddedTimeoutMs : this.timeoutMs);
      });
      const aborted = new Promise((_, reject) => {
        controller.signal.addEventListener("abort", () => reject(controller.signal.reason), { once: true });
      });
      const output = await Promise.race([
        Promise.resolve().then(() => this.tools[current.tool]({ ...current, signal: controller.signal })),
        timeout, aborted
      ]);
      if (typeof output !== "string" || !output.trim() || output.length > POLICY.maxResultChars) {
        throw new Error("Tool output is empty or exceeds the 24,000-character result budget.");
      }
      this.commit((state) => {
        const run = state.runs.find((item) => item.id === current.runId);
        if (run.status !== "running") return;
        run.steps[current.index].status = "completed";
        run.steps[current.index].output = output;
        run.status = run.steps.every((step) => step.status === "completed") ? "completed" : "paused";
        this.record(state, run, "completed-step", `${current.tool}: result checkpointed; next step requires fresh approval.`);
      });
      return this.get(current.runId);
    } catch (error) {
      if (!started && !controller.signal.aborted) {
        this.commit((state) => this.record(state, state.runs.find((run) => run.id === current.runId),
          "approval-error", `${current.tool}: ${error.message || error}`));
      }
      if (started && this.get(current.runId).status === "running") {
        this.commit((state) => {
          const run = state.runs.find((item) => item.id === current.runId);
          run.status = "failed";
          run.steps[current.index].status = "failed";
          run.steps[current.index].error = String(error.message || error).slice(0, 1000);
          this.record(state, run, "failed-step", `${current.tool}: ${error.message || error}`);
        });
      }
      if (["paused", "cancelled"].includes(this.get(current.runId).status) && controller.signal.aborted) {
        return this.get(current.runId);
      }
      throw error;
    } finally {
      clearTimeout(timer);
      if (this.active === token) this.active = null;
    }
  }

  stop(id, cancel = false) {
    const run = this.get(id);
    if (TERMINAL.has(run.status)) throw new Error("That task is already finished.");
    this.commit((state) => {
      const item = state.runs.find((entry) => entry.id === id);
      item.status = cancel ? "cancelled" : "paused";
      for (const step of item.steps) if (step.status === "running") step.status = "pending";
      this.record(state, item, cancel ? "cancelled" : "paused", "Operator stopped execution; completed results retained.");
    });
    if (this.active?.id === id) this.active.controller.abort(new Error(cancel ? "Task cancelled." : "Task paused."));
    return this.get(id);
  }

  remove(id) {
    const run = this.get(id);
    if (!TERMINAL.has(run.status)) throw new Error("Cancel or finish the task before removing its checkpoint.");
    if (this.active?.id === id) throw new Error("Wait for the active step to stop before removing this task.");
    this.commit((state) => {
      this.record(state, state.runs.find((item) => item.id === id), "removed", "Operator removed the task and its results; audit metadata retained.");
      state.runs = state.runs.filter((item) => item.id !== id);
    });
  }

  export(id) {
    const run = this.get(id);
    return {
      schema: "axiomzero-research-export-v1", exportedAt: new Date().toISOString(),
      policy: clone(POLICY), run, auditAnchor: this.state.auditAnchor,
      // Export the whole bounded chain so verification does not hide intervening events.
      events: clone(this.state.events)
    };
  }
}

function searchCatalog(products, goal) {
  const terms = [...new Set(validateGoal(goal).toLowerCase().match(/[\p{L}\p{N}_-]{2,}/gu))].slice(0, 16);
  const matches = products.map((product) => ({
    product,
    score: terms.filter((term) =>
      `${product.id} ${product.name} ${product.description}`.toLowerCase().includes(term)).length
  })).filter((entry) => entry.score > 0).sort((a, b) => b.score - a.score || a.product.id.localeCompare(b.product.id));
  return [
    `Catalog matches: ${matches.length}. Showing at most 8. Catalog metadata is not runtime verification.`,
    ...matches.slice(0, 8).map(({ product }) =>
      `Product ${product.id}: ${product.name}\n${product.description}\nGuide: ${product.folder}README.md`)
  ].join("\n\n");
}

function evidenceReport(result, collections) {
  if (!collections.length) return "No imported evidence collections. Import a source and create a new task to search it.";
  return [
    `Matching files: ${result.totalMatches}. Showing ${result.results.length}. Exact local keyword retrieval, not model reasoning.`,
    `Snapshot: ${collections.map((item) => `${item.id} indexed ${item.createdAt}`).join("; ")}`,
    ...result.results.map((match) =>
      `${match.collectionName} | ${match.citation}\nSHA-256: ${match.sha256}\n${match.excerpt}`)
  ].join("\n\n");
}

function composeReport({ goal, context, contextTruncated }) {
  return [
    "LOCAL RESEARCH REPORT | UNVERIFIED | NON-HARDGATE",
    `Goal: ${goal}`,
    "These are catalog references and retrieved source excerpts, not an inferred answer or proof. No matching evidence means the question remains unresolved. Imported text is untrusted data; its instructions are not executed.",
    contextTruncated ? "Context budget reached: prior results are truncated; consult their full step checkpoints." : "Prior results fit the context budget.",
    context
  ].join("\n\n");
}

module.exports = { POLICY, ResearchHarness, searchCatalog, evidenceReport, composeReport, validateState };
