const fs = require("node:fs");
const path = require("node:path");
const { spawn } = require("node:child_process");
const crypto = require("node:crypto");
const http = require("node:http");
const { createExclusiveOperation } = require("./operation-lock.cjs");
const { resolveNodeToolchain } = require("./node-toolchain.cjs");
const { installNodeLts } = require("./node-bootstrap.cjs");

function inside(root, relative) {
  if (typeof relative !== "string" || !relative || path.isAbsolute(relative) ||
      relative.split(/[\\/]/).includes("..")) throw new Error("Runtime path is invalid.");
  const target = fs.realpathSync(path.join(root, relative));
  const boundary = path.relative(fs.realpathSync(root), target);
  if (boundary.startsWith(`..${path.sep}`) || boundary === ".." || path.isAbsolute(boundary)) {
    throw new Error("Runtime path escapes the portfolio.");
  }
  return target;
}

function runCommand(executable, args, { cwd, timeoutMs = 600000, spawnProcess = spawn } = {}) {
  return new Promise((resolve, reject) => {
    const child = spawnProcess(executable, args, { cwd, shell: false, windowsHide: true, stdio: ["ignore", "pipe", "pipe"] });
    let output = "";
    let bytes = 0;
    let failure;
    const timer = setTimeout(() => { failure = new Error("Runtime setup exceeded its deadline."); child.kill(); }, timeoutMs);
    const collect = (chunk) => {
      bytes += chunk.length;
      if (bytes > 262144) { failure = new Error("Runtime setup diagnostics exceeded 256 KiB."); child.kill(); }
      else output += chunk.toString("utf8");
    };
    child.stdout.on("data", collect);
    child.stderr.on("data", collect);
    child.on("error", (error) => { failure = error; });
    child.on("close", (code) => {
      clearTimeout(timer);
      if (failure) reject(failure);
      else if (code !== 0) reject(new Error(`Runtime setup exited ${code}: ${output.slice(-4000)}`));
      else resolve({ output: output.slice(-4000) });
    });
  });
}

function createRuntimeManager({
  entries, sourceRoot, dataDirectory, platform = process.platform, execute = runCommand,
  spawnProcess = spawn, serviceDeadlineMs = 30000, nodeToolchain,
  extractionScript = path.join(__dirname, "../scripts/extract-node.ps1")
}) {
  const tools = nodeToolchain || (() => resolveNodeToolchain(process.env, path.join(dataDirectory, "tools/node-lts")));
  const runExclusive = createExclusiveOperation("A runtime installation is already in progress.");
  const receiptsDirectory = path.join(dataDirectory, "receipts");
  const services = new Map();
  const credentials = new Map();
  const ports = new Map([["20", 8020], ["21", 8021], ["23", 8033], ["27", 8327], ...Array.from({ length: 16 }, (_, index) => [String(index + 28), 8128 + index]), ["44", 8144]]);
  function entryById(id) {
    const entry = entries.find((item) => item.id === id);
    if (!entry || typeof id !== "string" || !/^\d{2}$/.test(id)) throw new Error("Runtime product identifier is invalid.");
    return entry;
  }
  function readReceipt(id) {
    const file = path.join(receiptsDirectory, `${id}.json`);
    if (!fs.existsSync(file)) return null;
    const receipt = JSON.parse(fs.readFileSync(file, "utf8"));
    if (receipt.id !== id || !["installed", "failed"].includes(receipt.status)) throw new Error("Runtime receipt is invalid.");
    return receipt;
  }
  return {
    list: () => entries.map((entry) => ({ ...entry, receipt: readReceipt(entry.id), running: services.has(entry.id), managedService: ports.has(entry.id) && !["36"].includes(entry.id) })),
    install: (id) => runExclusive(async () => {
      const entry = entryById(id);
      if (services.has(id)) throw new Error("Stop this runtime before reinstalling its environment.");
      if (platform !== "win32") throw new Error("Managed portfolio provisioning currently requires Windows.");
      if (id !== "27" && entry.installMode !== "python-venv") {
        throw new Error(`Product ${id} requires ${entry.installMode}; its dedicated target installer is not managed here. ${entry.limitation}`);
      }
      if (id === "26") throw new Error("Product 26 requires POSIX fcntl/process groups; native Windows execution is not supported.");
      if (id === "36") throw new Error("Product 36 requires a working JAX backend; this native Windows installer has not verified that backend.");
      const root = typeof sourceRoot === "function" ? sourceRoot() : sourceRoot;
      const dependency = entry.dependencyManifest ||
        (Number(id) >= 28 && Number(id) <= 43 ? "12-AZ-IP/45-axiomzero-pc-suite/requirements-calculators.txt" : null);
      if (!dependency) throw new Error("This product has no reviewed dependency manifest.");
      const requirements = inside(root, dependency);
      if (id !== "27" && !/\.(?:txt|lock|toml)$/.test(requirements)) throw new Error("Unsupported dependency manifest.");
      const folder = inside(root, entry.productFolder);
      const environment = id === "27" ? folder : path.join(dataDirectory, "environments", id);
      const python = path.join(environment, "Scripts", "python.exe");
      const receiptFile = path.join(receiptsDirectory, `${id}.json`);
      fs.mkdirSync(receiptsDirectory, { recursive: true });
      fs.mkdirSync(path.dirname(environment), { recursive: true });
      const receipt = {
        id, status: "failed", dependencyManifest: dependency,
        sourceRoot: root,
        dependencySha256: crypto.createHash("sha256").update(fs.readFileSync(requirements)).digest("hex"),
        environment, at: new Date().toISOString()
      };
      try {
        if (id === "27") {
          const { node, npm } = tools();
          const lock = inside(root, `${entry.productFolder}package-lock.json`);
          const expected = JSON.parse(fs.readFileSync(requirements, "utf8"));
          if (expected.scripts?.build !== "vite build --config vite.config.mjs") throw new Error("The reviewed Node build command changed.");
          await execute(node, ["-e", "const [major,minor]=process.versions.node.split('.').map(Number);if(major<22||(major===22&&minor<12))throw Error('Node >=22.12 required')"], { cwd: folder });
          await execute(node, [npm, "ci", "--no-audit", "--no-fund"], { cwd: folder });
          await execute(node, [inside(root, `${entry.productFolder}node_modules/vite/bin/vite.js`), "build", "--config", "vite.config.mjs"], { cwd: folder });
          if (!fs.existsSync(path.join(folder, "dist/index.html"))) throw new Error("The Node dashboard build produced no index.html.");
          receipt.lockSha256 = crypto.createHash("sha256").update(fs.readFileSync(lock)).digest("hex");
          receipt.node = node;
          receipt.meaning = "Locked Node dependencies installed and dashboard built; external integrations are not certified.";
        } else {
          // The Windows Python launcher chooses the explicitly requested Python version.
          await execute("py", ["-3.12", "-m", "venv", environment], { cwd: folder, timeoutMs: 120000 });
          await execute(python, [
            "-m", "pip", "install", "--quiet", "--disable-pip-version-check",
            ...(requirements.endsWith("pyproject.toml") ? [folder] : ["-r", requirements])
          ], { cwd: folder });
          await execute(python, ["-m", "pip", "check"], { cwd: folder, timeoutMs: 120000 });
          receipt.meaning = "Dependencies installed and pip check passed; service/UI and external integrations are not certified.";
        }
        receipt.status = "installed";
        fs.writeFileSync(receiptFile, `${JSON.stringify(receipt, null, 2)}\n`, { mode: 0o600 });
        return receipt;
      } catch (error) {
        receipt.error = String(error.message).slice(0, 4000);
        fs.writeFileSync(receiptFile, `${JSON.stringify(receipt, null, 2)}\n`, { mode: 0o600 });
        throw error;
      }
    }),
    installPython: () => runExclusive(async () => {
      if (platform !== "win32") throw new Error("Windows Python bootstrap is only available on Windows.");
      fs.mkdirSync(dataDirectory, { recursive: true });
      return execute("winget", [
        "install", "--id", "Python.Python.3.12", "--exact", "--scope", "user",
        "--accept-package-agreements", "--accept-source-agreements"
      ], { cwd: dataDirectory, timeoutMs: 600000 });
    }),
    installNode: () => runExclusive(() => installNodeLts({
      directory: path.join(dataDirectory, "tools"), extractionScript, execute, platform
    })),
    start: (id) => runExclusive(async () => {
      const entry = entryById(id);
      if (services.has(id)) throw new Error("This runtime is already running.");
      if (!ports.has(id) || id === "36") throw new Error("This service has no verified native-loopback launch contract.");
      const receipt = readReceipt(id);
      if (!receipt || receipt.status !== "installed") throw new Error("Install this runtime's dependencies first.");
      const root = typeof sourceRoot === "function" ? sourceRoot() : sourceRoot;
      if (receipt.sourceRoot !== root) throw new Error("The selected portfolio source changed; reinstall this runtime.");
      const dependency = inside(root, receipt.dependencyManifest);
      if (crypto.createHash("sha256").update(fs.readFileSync(dependency)).digest("hex") !== receipt.dependencySha256) {
        throw new Error("The installed dependency manifest changed; reinstall this runtime.");
      }
      const script = inside(root, entry.entrypoint);
      const folder = inside(root, entry.productFolder);
      const executable = id === "27" ? tools().node : path.join(dataDirectory, "environments", id, "Scripts", "python.exe");
      if (!fs.existsSync(executable)) throw new Error("Installed runtime Python is missing; reinstall this product.");
      if (id === "27") {
        const lock = inside(root, `${entry.productFolder}package-lock.json`);
        if (crypto.createHash("sha256").update(fs.readFileSync(lock)).digest("hex") !== receipt.lockSha256 ||
            receipt.node !== executable) throw new Error("The Node lockfile or executable changed; reinstall this product.");
      }
      const port = ports.get(id);
      const net = require("node:net");
      await new Promise((resolve, reject) => {
        const probe = net.createServer();
        probe.once("error", () => reject(new Error(`Port ${port} is unavailable; refusing to attach to another service.`)));
        probe.listen(port, "127.0.0.1", () => probe.close(resolve));
      });
      const args = [...entry.launchArgs];
      if (id === "20") args.push("--host", "127.0.0.1", "--local-execution", "off");
      const token = id === "27" ? crypto.randomBytes(32).toString("hex") : null;
      const child = spawnProcess(executable, [script, ...args], {
        cwd: folder, shell: false, windowsHide: true, stdio: ["ignore", "pipe", "pipe"],
        env: {
          ...process.env, PYTHONPATH: root, PYTHONNOUSERSITE: "1",
          MERLIN_LOCAL_EXECUTION_ENABLED: "0",
          MERLIN_TRAINING_RUNTIME_DIR: path.join(dataDirectory, "psicat-training"),
          OPENBLAS_NUM_THREADS: "1", OMP_NUM_THREADS: "1",
          ...(id === "27" ? {
            PSICAT_VITE_WORKBENCH_HOST: "127.0.0.1", PSICAT_VITE_WORKBENCH_PORT: "8327",
            PSICAT_VITE_WORKBENCH_TOKEN: token,
            PSICAT_VITE_WORKBENCH_HOME: path.join(dataDirectory, "workbench")
          } : {})
        }
      });
      services.set(id, child);
      if (token) credentials.set(id, token);
      let failure;
      let output = "";
      const record = (chunk) => { output = (output + chunk.toString("utf8")).slice(-4000); };
      child.stdout.on("data", record);
      child.stderr.on("data", record);
      child.on("error", (error) => { failure = error; });
      child.on("close", (code) => {
        failure ||= new Error(`Runtime exited ${code}: ${output}`);
        services.delete(id);
        credentials.delete(id);
      });
      const deadline = Date.now() + serviceDeadlineMs;
      let lastError;
      while (Date.now() < deadline && !failure) {
        try {
          await new Promise((resolve, reject) => {
            const request = http.get({ hostname: "127.0.0.1", port, path: entry.healthPath || "/", timeout: 1500 }, (response) => {
              response.resume();
              if (response.statusCode === 200) resolve();
              else reject(new Error(`Runtime health returned ${response.statusCode}.`));
            });
            request.on("timeout", () => request.destroy(new Error("Health request timed out.")));
            request.on("error", reject);
          });
          if (failure) throw failure;
          return { id, status: "running", endpoint: `http://127.0.0.1:${port}` };
        } catch (error) { lastError = error; }
        await new Promise((resolve) => setTimeout(resolve, 300));
      }
      child.kill();
      throw failure || new Error(`Runtime did not become healthy: ${lastError?.message || "deadline"}`);
    }),
    access: (id) => {
      entryById(id);
      if (!services.has(id)) throw new Error("Start this managed runtime before opening it.");
      return { endpoint: `http://127.0.0.1:${ports.get(id)}`, token: credentials.get(id) || null };
    },
    stop: (id) => {
      entryById(id);
      const child = services.get(id);
      if (!child) throw new Error("That runtime is not running in this desktop session.");
      if (!child.kill()) throw new Error("The runtime could not be stopped.");
      return { id, status: "stopping" };
    },
    stopAll: () => {
      for (const child of services.values()) child.kill();
    }
  };
}

module.exports = { createRuntimeManager, runCommand, inside };
