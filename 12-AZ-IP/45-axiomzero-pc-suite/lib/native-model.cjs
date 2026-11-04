const fs = require("node:fs");
const path = require("node:path");
const { spawn } = require("node:child_process");

const MAX_OUTPUT_BYTES = 65536;
const MAX_REQUEST_BYTES = 16384;

function createNativeModel({ executable, prefix = [], seed, userDirectory, spawnProcess = spawn }) {
  if (!path.isAbsolute(executable) || !path.isAbsolute(seed) || !path.isAbsolute(userDirectory)) {
    throw new Error("Native runtime locations must be absolute.");
  }
  let active = null;
  let cancelActive;
  const checkpoint = path.join(userDirectory, "psicat-trained.npz");
  function invoke(request, timeoutMs = 120000) {
    if (active) return Promise.reject(new Error("The native PsiCat runtime is busy."));
    const body = JSON.stringify(request);
    if (Buffer.byteLength(body) > MAX_REQUEST_BYTES) return Promise.reject(new Error("Native request exceeds 16 KiB."));
    return new Promise((resolve, reject) => {
      const child = spawnProcess(executable, prefix, {
        shell: false, windowsHide: true,
        stdio: ["pipe", "pipe", "pipe"],
        env: { ...process.env, OPENBLAS_NUM_THREADS: "1", OMP_NUM_THREADS: "1", PYTHONNOUSERSITE: "1" }
      });
      active = child;
      const chunks = [];
      let bytes = 0;
      let error;
      cancelActive = () => {
        error = new Error("Native PsiCat operation cancelled by the operator.");
        child.kill();
      };
      const timer = setTimeout(() => {
        error = new Error("Native PsiCat operation exceeded its deadline.");
        child.kill();
      }, timeoutMs);
      function fail(failure) {
        error = failure;
        child.kill();
      }
      child.on("error", (failure) => { error = failure; });
      child.stdin.on("error", (failure) => { error = failure; });
      child.stdout.on("data", (chunk) => {
        bytes += chunk.length;
        if (bytes > MAX_OUTPUT_BYTES) fail(new Error("Native output exceeded 64 KiB."));
        else chunks.push(chunk);
      });
      let stderrBytes = 0;
      child.stderr.on("data", (chunk) => {
        stderrBytes += chunk.length;
        if (stderrBytes > MAX_OUTPUT_BYTES) fail(new Error("Native diagnostics exceeded 64 KiB."));
      });
      child.on("close", (code) => {
        clearTimeout(timer);
        active = null;
        cancelActive = null;
        if (error) { reject(error); return; }
        let result;
        try { result = JSON.parse(Buffer.concat(chunks).toString("utf8")); }
        catch (failure) { reject(new Error("Native runtime did not return a valid response.", { cause: failure })); return; }
        if (!result || typeof result !== "object" || Array.isArray(result)) {
          reject(new Error("Native runtime did not return a valid response object.")); return;
        }
        if (code !== 0 || result.status === "failed") { reject(new Error(result.error || `Native runtime exited ${code}.`)); return; }
        if (!["ready", "completed", "blocked-vocabulary"].includes(result.status) ||
            result.productionAssistantVerified !== false || result.epistemicLabel !== "UNVERIFIED") {
          reject(new Error("Native runtime response violates the model contract.")); return;
        }
        const statuses = { status: ["ready"], train: ["completed"], generate: ["completed", "blocked-vocabulary"] };
        if (!statuses[request.action].includes(result.status) ||
            (request.action === "generate" && result.status === "completed" && (typeof result.completion !== "string" || result.completion.length > 320))) {
          reject(new Error("Native response does not match the requested action.")); return;
        }
        resolve(result);
      });
      child.stdin.end(body);
    });
  }
  function currentCheckpoint() {
    if (fs.existsSync(checkpoint)) return checkpoint;
    if (!fs.existsSync(seed)) throw new Error("The packaged own-model seed checkpoint is missing.");
    return seed;
  }
  return {
    status: () => invoke({ action: "status", checkpoint: currentCheckpoint() }),
    generate: (prompt) => {
      if (typeof prompt !== "string" || prompt.length < 1 || prompt.length > 400) throw new Error("Prompt must contain 1-400 characters.");
      return invoke({ action: "generate", checkpoint: currentCheckpoint(), prompt });
    },
    train: async (corpus, steps) => {
      if (typeof corpus !== "string" || !path.isAbsolute(corpus) ||
          !Number.isInteger(steps) || steps < 1 || steps > 2000) throw new Error("Training corpus or step budget is invalid.");
      fs.mkdirSync(userDirectory, { recursive: true });
      // Do not overwrite a useful prior checkpoint until a complete training run succeeded.
      const pending = path.join(userDirectory, "psicat-next.npz");
      const result = await invoke({ action: "train", corpus, steps, checkpoint: pending }, 600000);
      fs.renameSync(pending, checkpoint);
      return result;
    },
    cancel: () => {
      if (!active) throw new Error("No native operation is active.");
      cancelActive();
    },
    isActive: () => Boolean(active)
  };
}

module.exports = { createNativeModel };
