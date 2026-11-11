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
    for (const [id, pathname, title] of [
      ["04", "/frontend/", "UM-SOS Prediction Explorer"],
      ["16", "/", "Oracle"],
      ["25", "/ui/index.html", "PsiCat Braided Brain"]
    ]) {
      assert.equal((await manager.install(id)).status, "installed");
      const started = await manager.start(id);
      const url = new URL(pathname, started.endpoint);
      const response = await fetch(url, { signal: AbortSignal.timeout(10000) });
      assert.equal(response.status, 200, `Product ${id} UI did not load.`);
      assert.match(await response.text(), new RegExp(title, "i"));
      manager.stop(id);
      for (let attempt = 0; attempt < 100 && manager.list().find((entry) => entry.id === id).running; attempt++) {
        await new Promise((resolve) => setTimeout(resolve, 100));
      }
      assert.equal(manager.list().find((entry) => entry.id === id).running, false);
      console.log(`Installed Product ${id}: loopback UI, start and stop passed.`);
    }
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
    assert.equal((await manager.install("36")).backend, "jax-cpu");
    const slider = await manager.start("36");
    const readingResponse = await fetch(`${slider.endpoint}/api/slider?phi0=10&n_w=5`, { signal: AbortSignal.timeout(30000) });
    const reading = await readingResponse.json();
    assert.equal(readingResponse.status, 200, reading.error || "Live CPU slider failed.");
    for (const [field, expected] of [["n_s", 0.6], ["dn_s_dphi0", 0.08], ["dn_s_dnw", -0.08]]) {
      assert.ok(Number.isFinite(reading[field]) && Math.abs(reading[field] - expected) < 1e-6, `Incorrect live slider field: ${field}`);
    }
    manager.stop("36");
    for (let attempt = 0; attempt < 100 && manager.list().find((entry) => entry.id === "36").running; attempt++) {
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
    assert.equal(manager.list().find((entry) => entry.id === "36").running, false);
    console.log("Installed CPU JAX dependencies, actual slider values/gradients and service start/stop passed.");
    await manager.installNode();
    await manager.install("27");
    const nodeRuntime = await manager.start("27");
    const access = manager.access("27");
    assert.equal(nodeRuntime.endpoint, "http://127.0.0.1:8327");
    assert.match(access.token, /^[0-9a-f]{64}$/);
    const unauthorized = await fetch(`${access.endpoint}/api/status`, { signal: AbortSignal.timeout(5000) });
    assert.equal(unauthorized.status, 401);
    const headers = { Authorization: `Bearer ${access.token}`, "Content-Type": "application/json" };
    async function action(value) {
      const response = await fetch(`${access.endpoint}/api/action`, {
        method: "POST", headers, body: JSON.stringify(value), signal: AbortSignal.timeout(30000)
      });
      const payload = await response.json();
      assert.equal(response.status, 200, payload.error || "Workbench action failed.");
      return payload;
    }
    assert.equal((await action({ action: "create", name: "installed-smoke" })).project.name, "installed-smoke");
    const configMarker = path.join(temporary, "unexpected-postcss-config");
    fs.writeFileSync(path.join(temporary, "runtimes", "workbench", "projects", "installed-smoke", "postcss.config.cjs"),
      `require('node:fs').writeFileSync(${JSON.stringify(configMarker)}, 'executed'); module.exports = { plugins: [] };`);
    await action({ action: "build", name: "installed-smoke" });
    assert.equal(fs.existsSync(configMarker), false, "Installed project build must not execute discovered PostCSS configuration.");
    const dashboard = await fetch(access.endpoint, { signal: AbortSignal.timeout(5000) });
    assert.equal(dashboard.status, 200);
    assert.match(await dashboard.text(), /PsiCat/);
    manager.stop("27");
    for (let attempt = 0; attempt < 100 && manager.list().find((entry) => entry.id === "27").running; attempt++) {
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
    assert.equal(manager.list().find((entry) => entry.id === "27").running, false);
    assert.throws(() => manager.access("27"), /Start/);
    console.log("Installed Node workbench locked dependencies, dashboard, authentication, project creation/build and start/stop passed.");
    await manager.install("24");
    let browser;
    try { browser = await manager.start("24"); }
    catch (error) {
      const folder = path.join(materializePortfolioSource(source, path.join(temporary, "source")), "12-AZ-IP/24-psicat-web-browser");
      const resources = ["desktop/main.js", "desktop/runtime.js", "desktop/lib/startup-diagnostics.js",
        "desktop/lib/suite-lifecycle.js", "node_modules/electron/dist/electron.exe",
        "node_modules/electron/dist/resources/default_app.asar", "node_modules/electron/dist/v8_context_snapshot.bin"];
      console.error("Installed browser bootstrap resource diagnostics:", resources.map((relative) => {
        const filename = path.join(folder, relative);
        return { resource: relative, pathLength: filename.length, exists: fs.existsSync(filename) };
      }));
      throw error;
    }
    assert.equal(browser.desktop, true);
    const syncResponse = await fetch("http://127.0.0.1:8787/api/sync/health", { signal: AbortSignal.timeout(5000) });
    assert.equal(syncResponse.status, 200);
    const sync = await syncResponse.json();
    assert.equal(sync.ok, true);
    assert.equal(sync.service, "psicat-sync-backend");
    const navigatorResponse = await fetch("http://127.0.0.1:8020/api/psicat/status", { signal: AbortSignal.timeout(5000) });
    assert.equal(navigatorResponse.status, 200);
    assert.equal((await navigatorResponse.json()).psicat_available, true);
    const stoppedBrowser = await manager.stop("24");
    assert.equal(stoppedBrowser.forced, false, "Normal installed browser shutdown must not require forced tree termination.");
    assert.equal(manager.list().find((entry) => entry.id === "24").running, false);
    for (const url of ["http://127.0.0.1:8787/api/sync/health", "http://127.0.0.1:8020/api/psicat/status"]) {
      await assert.rejects(fetch(url, { signal: AbortSignal.timeout(2000) }));
    }
    console.log("Installed pinned Windows Electron browser, owned Python sync/Navigator readiness and graceful sidecar shutdown passed.");
  } finally {
    await manager.stopAll();
    fs.rmSync(temporary, { recursive: true, force: true });
  }
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
