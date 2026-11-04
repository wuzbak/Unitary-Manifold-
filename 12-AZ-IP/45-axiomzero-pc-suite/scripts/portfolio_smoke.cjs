const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { materializePortfolioSource } = require("../lib/portfolio-source.cjs");
const { createRuntimeManager } = require("../lib/runtime-manager.cjs");

async function main() {
  if (process.platform !== "win32") throw new Error("This installation smoke requires native Windows.");
  const source = path.resolve(process.argv[2]);
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "p45-portfolio-smoke-"));
  const entries = JSON.parse(fs.readFileSync(path.join(__dirname, "../catalog/runtimes.json"), "utf8"));
  const manager = createRuntimeManager({
    entries, sourceRoot: () => materializePortfolioSource(source, path.join(temporary, "source")),
    dataDirectory: path.join(temporary, "runtimes")
  });
  try {
    const receipt = await manager.install("43");
    assert.equal(receipt.status, "installed");
    const started = await manager.start("43");
    assert.equal(started.endpoint, "http://127.0.0.1:8143");
    const response = await fetch(`${started.endpoint}/api/status`, { signal: AbortSignal.timeout(5000) });
    assert.equal(response.status, 200);
    const payload = await response.json();
    assert.ok(payload && typeof payload === "object");
    manager.stop("43");
    for (let attempt = 0; attempt < 100 && manager.list().find((entry) => entry.id === "43").running; attempt++) {
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
    assert.equal(manager.list().find((entry) => entry.id === "43").running, false);
    console.log("Installed bundled-source checksums, isolated Python dependencies and Product 43 loopback start/health/stop passed.");
  } finally {
    manager.stopAll();
    fs.rmSync(temporary, { recursive: true, force: true });
  }
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
