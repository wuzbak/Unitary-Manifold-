const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");
const http = require("node:http");
const { EventEmitter } = require("node:events");
const { PassThrough } = require("node:stream");
const { createRuntimeManager, inside } = require("../lib/runtime-manager.cjs");

function fixture(t, execute, options = {}) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "portfolio-runtime-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const folder = path.join(root, "12-AZ-IP/20-psicat-navigator");
  fs.mkdirSync(folder, { recursive: true });
  fs.writeFileSync(path.join(folder, "requirements.txt"), "numpy\n");
  fs.writeFileSync(path.join(folder, "run.py"), "# reviewed entrypoint\n");
  const calls = [];
  const manager = createRuntimeManager({
    entries: [{
      id: "20", installMode: "python-venv",
      dependencyManifest: "12-AZ-IP/20-psicat-navigator/requirements.txt",
      productFolder: "12-AZ-IP/20-psicat-navigator",
      entrypoint: "12-AZ-IP/20-psicat-navigator/run.py", launchArgs: ["--port", "8020", "--no-open"],
      healthPath: "/api/psicat/status"
    }, { id: "02", installMode: "uefi-toolchain", limitation: "Requires a VM." }],
    sourceRoot: root, dataDirectory: path.join(root, "user"), platform: "win32",
    execute: execute || (async (exe, args, options) => {
      calls.push({ exe, args, options });
      if (args.includes("venv")) {
        fs.mkdirSync(path.join(args.at(-1), "Scripts"), { recursive: true });
        fs.writeFileSync(path.join(args.at(-1), "Scripts", "python.exe"), "runtime");
      }
      return { output: "" };
    }),
    ...options
  });
  return { manager, root, calls };
}
test("portfolio Python installs in separate environments and verifies dependencies", async (t) => {
  const { manager, calls } = fixture(t);
  const receipt = await manager.install("20");
  assert.equal(receipt.status, "installed");
  assert.equal(receipt.dependencySha256.length, 64);
  assert.equal(calls.length, 3);
  assert.deepEqual(calls[0].args.slice(0, 3), ["-3.12", "-m", "venv"]);
  assert.ok(calls[1].args.includes("-r"));
  assert.deepEqual(calls[2].args, ["-m", "pip", "check"]);
  assert.equal(manager.list()[0].receipt.status, "installed");
});
test("portfolio non-native target and invalid identifiers do not masquerade as installed", async (t) => {
  const { manager } = fixture(t);
  await assert.rejects(manager.install("02"), /uefi-toolchain/);
  await assert.rejects(manager.install("../../"), /identifier/);
});
test("failed dependencies persist error receipts and reject the operation", async (t) => {
  const { manager } = fixture(t, async () => { throw new Error("Python not installed"); });
  await assert.rejects(manager.install("20"), /Python not installed/);
  assert.equal(manager.list()[0].receipt.status, "failed");
});
test("portfolio paths reject traversal and symlink escape", (t) => {
  const { root } = fixture(t);
  assert.throws(() => inside(root, "../outside"), /invalid/);
  assert.throws(() => inside(root, "/etc/passwd"), /invalid/);
});
test("Python bootstrap uses the fixed user-scoped Windows package", async (t) => {
  const { manager, calls } = fixture(t);
  await manager.installPython();
  assert.equal(calls[0].exe, "winget");
  assert.ok(calls[0].args.includes("Python.Python.3.12"));
  assert.ok(calls[0].args.includes("user"));
});
test("loopback lifecycle checks health and owns the process without enabling PsiCat command execution", async (t) => {
  let child;
  let server;
  const { manager } = fixture(t, null, {
    spawnProcess(exe, args, options) {
      assert.match(exe, /python.exe$/);
      assert.ok(args.includes("--local-execution"));
      assert.equal(args.at(-1), "off");
      assert.equal(options.env.MERLIN_LOCAL_EXECUTION_ENABLED, "0");
      assert.equal(options.shell, false);
      child = new EventEmitter();
      child.stdout = new PassThrough(); child.stderr = new PassThrough();
      server = http.createServer((_request, response) => response.end("{}"));
      server.listen(8020, "127.0.0.1");
      child.kill = () => { server.close(() => child.emit("close", 0)); return true; };
      return child;
    }
  });
  t.after(() => manager.stopAll());
  await assert.rejects(manager.start("20"), /Install/);
  await manager.install("20");
  assert.equal((await manager.start("20")).endpoint, "http://127.0.0.1:8020");
  assert.equal(manager.list()[0].running, true);
  await assert.rejects(manager.start("20"), /already running/);
  await assert.rejects(manager.install("20"), /Stop this runtime/);
  manager.stop("20");
  await new Promise((resolve) => child.once("close", resolve));
  assert.equal(manager.list()[0].running, false);
  assert.throws(() => manager.stop("20"), /not running/);
});
test("changed source dependencies and missing executables cannot launch under an old receipt", async (t) => {
  const { manager, root } = fixture(t);
  await manager.install("20");
  fs.writeFileSync(path.join(root, "12-AZ-IP/20-psicat-navigator/requirements.txt"), "changed\n");
  await assert.rejects(manager.start("20"), /manifest changed/);
  fs.writeFileSync(path.join(root, "12-AZ-IP/20-psicat-navigator/requirements.txt"), "numpy\n");
  fs.unlinkSync(path.join(root, "user/environments/20/Scripts/python.exe"));
  await assert.rejects(manager.start("20"), /Python is missing/);
});
test("calculator requirements and pyproject packages are genuinely provisioned, incompatible Windows targets fail", async (t) => {
  const { root, calls } = fixture(t);
  const packageFolder = "12-AZ-IP/20-psicat-navigator";
  const calculatorManifest = "12-AZ-IP/45-axiomzero-pc-suite/requirements-calculators.txt";
  fs.mkdirSync(path.dirname(path.join(root, calculatorManifest)), { recursive: true });
  fs.writeFileSync(path.join(root, calculatorManifest), "numpy\nscipy\n");
  fs.writeFileSync(path.join(root, packageFolder, "pyproject.toml"), "[project]\n");
  const manager = createRuntimeManager({
    entries: [
      { id: "31", installMode: "python-venv", dependencyManifest: null, productFolder: packageFolder },
      { id: "44", installMode: "python-venv", dependencyManifest: `${packageFolder}/pyproject.toml`, productFolder: packageFolder },
      { id: "26", installMode: "python-venv" }, { id: "36", installMode: "python-venv" }
    ], sourceRoot: root, dataDirectory: path.join(root, "user"), platform: "win32",
    execute: async (exe, args) => { calls.push({ exe, args }); }
  });
  assert.equal((await manager.install("31")).dependencyManifest, calculatorManifest);
  await manager.install("44");
  assert.equal(calls[4].args.at(-1), path.join(root, packageFolder));
  assert.equal(calls[4].args.includes("-r"), false);
  await assert.rejects(manager.install("26"), /POSIX/);
  await assert.rejects(manager.install("36"), /JAX/);
});
test("Node workbench installs the lockfile, builds the actual dashboard and retains no token in receipts", async (t) => {
    const { root } = fixture(t);
    const folder = "12-AZ-IP/27-psicat-vite-web-workbench/";
    const target = path.join(root, folder);
    fs.mkdirSync(target, { recursive: true });
    fs.writeFileSync(path.join(target, "package.json"), JSON.stringify({ scripts: { build: "vite build --config vite.config.mjs" } }));
    fs.writeFileSync(path.join(target, "package-lock.json"), "{}");
    fs.writeFileSync(path.join(target, "server.js"), "");
    const node = path.join(root, "node.exe");
    fs.writeFileSync(node, "");
    const calls = [];
    let child;
    const manager = createRuntimeManager({
      entries: [{ id: "27", installMode: "node-npm", dependencyManifest: `${folder}package.json`, productFolder: folder, entrypoint: `${folder}server.js`, launchArgs: [], healthPath: "/health" }],
      sourceRoot: root, dataDirectory: path.join(root, "user"), platform: "win32",
      nodeToolchain: () => ({ node, npm: path.join(root, "npm-cli.js") }),
      execute: async (exe, args) => {
        calls.push({ exe, args });
        if (args.includes("ci")) {
          fs.mkdirSync(path.join(target, "node_modules/vite/bin"), { recursive: true });
          fs.writeFileSync(path.join(target, "node_modules/vite/bin/vite.js"), "");
        }
        if (args.includes("build")) {
          fs.mkdirSync(path.join(target, "dist"), { recursive: true });
          fs.writeFileSync(path.join(target, "dist/index.html"), "dashboard");
        }
      },
      spawnProcess(exe, args, options) {
        assert.equal(exe, node);
        assert.equal(options.env.PSICAT_VITE_WORKBENCH_HOST, "127.0.0.1");
        assert.match(options.env.PSICAT_VITE_WORKBENCH_TOKEN, /^[0-9a-f]{64}$/);
        child = new EventEmitter();
        child.stdout = new PassThrough(); child.stderr = new PassThrough();
        const server = http.createServer((_request, response) => response.end("{}"));
        server.listen(8327, "127.0.0.1");
        child.kill = () => { server.close(() => child.emit("close", 0)); return true; };
        return child;
      }
    });
    t.after(() => manager.stopAll());
    const receipt = await manager.install("27");
    assert.equal(calls.length, 3);
    assert.ok(calls[1].args.includes("ci"));
    assert.equal(receipt.lockSha256.length, 64);
    assert.equal(receipt.token, undefined);
    await manager.start("27");
    assert.equal(manager.access("27").token.length, 64);
    assert.equal(JSON.stringify(manager.list()).includes(manager.access("27").token), false);
    manager.stop("27");
    await new Promise((resolve) => child.once("close", resolve));
    assert.throws(() => manager.access("27"), /Start/);
    fs.writeFileSync(path.join(target, "package-lock.json"), "changed");
    await assert.rejects(manager.start("27"), /lockfile/);
});
