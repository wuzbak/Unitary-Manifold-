const path = require("node:path");
const { Worker } = require("node:worker_threads");

function searchEvidence({ directory, ids, goal, signal }) {
  return new Promise((resolve, reject) => {
    if (signal.aborted) {
      reject(signal.reason);
      return;
    }
    const worker = new Worker(path.join(__dirname, "evidence-worker.cjs"), {
      workerData: { directory, ids, goal },
      resourceLimits: { maxOldGenerationSizeMb: 512 }
    });
    let settled = false;
    function finish(error, result) {
      if (settled) return;
      settled = true;
      signal.removeEventListener("abort", abort);
      worker.terminate().then(() => {
        if (error) reject(error);
        else resolve(result);
      }, reject);
    }
    const abort = () => finish(signal.reason || new Error("Evidence search aborted."));
    signal.addEventListener("abort", abort, { once: true });
    worker.once("message", (result) => finish(null, result));
    worker.once("error", (error) => finish(error));
    worker.once("exit", (code) => {
      if (!settled) finish(new Error(`Evidence worker exited without a result (code ${code}).`));
    });
  });
}

module.exports = { searchEvidence };
