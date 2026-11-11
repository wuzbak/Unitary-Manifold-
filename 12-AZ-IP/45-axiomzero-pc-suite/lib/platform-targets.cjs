// SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
// Copyright (C) 2026  ThomasCory Walker-Pearson
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const http = require('node:http');
const crypto = require('node:crypto');
const { spawn } = require('node:child_process');

const MAX_OUTPUT = 128 * 1024;
const DEFAULT_TIMEOUT_MS = 30 * 60 * 1000;
const DEFAULT_STARTUP_MS = 90 * 1000;
const DEFAULT_STOP_MS = 15 * 1000;
const NAVIGATOR_PORT = 8020;
const NAVIGATOR_HEALTH = '/api/psicat/status';
const SYSTEM_TOOLS = new Set(['cmd.exe', 'wsl.exe', 'taskkill.exe', 'netstat.exe', 'tasklist.exe']);
const GRADLE_URL = /^https:\/\/services\.gradle\.org\/distributions\/gradle-(\d+\.\d+(?:\.\d+)?)-(bin|all)\.zip$/;
// Fixed script; every value reaches the final process only as positional argv.
const WSL_PID_SCRIPT = 'printf "AZPCSUITE_PID=%s\\n" "$$"; exec "$@"';
const WINDOWS_ENV_ALLOWLIST = [
  'SystemRoot', 'SYSTEMROOT', 'windir', 'ComSpec', 'PATH', 'Path', 'PATHEXT', 'TEMP', 'TMP',
  'USERPROFILE', 'LOCALAPPDATA', 'APPDATA', 'HOMEDRIVE', 'HOMEPATH', 'ProgramFiles',
  'ProgramFiles(x86)', 'ProgramW6432', 'ProgramData', 'NUMBER_OF_PROCESSORS',
  'PROCESSOR_ARCHITECTURE', 'OS', 'JAVA_HOME', 'ANDROID_HOME', 'ANDROID_SDK_ROOT',
  'GRADLE_USER_HOME', 'CARGO_HOME', 'RUSTUP_HOME',
];

const ANDROID = {
  'android-sdam': {
    productId: '14',
    name: 'SDAM Android APK',
    project: '12-AZ-IP/14-sdam/app',
    activity: 'com.sdam.debug/com.sdam.MainActivity',
    catalog: 'gradle/libs.versions.toml',
    artifact: ['app', 'build', 'outputs', 'apk', 'debug', 'app-debug.apk'],
  },
  'android-pentacorder': {
    productId: '15',
    name: 'Pentacorder Android APK',
    project: '12-AZ-IP/15-pentacorder',
    activity: 'com.axiomzero.pentacorder.debug/com.gibbernode.MainActivity',
    catalog: 'gradle/libs.versions.toml',
    artifact: ['app', 'build', 'outputs', 'apk', 'debug', 'app-debug.apk'],
  },
};
const UEFI = {
  productId: '02',
  name: 'AZ-KERNEL UEFI artifact',
  project: '12-AZ-IP/02-az-kernel',
  required: ['Cargo.toml', 'Cargo.lock', 'rust-toolchain.toml', 'assets/font8x16.bin'],
};
const NAVIGATOR = { productId: '20', project: '12-AZ-IP/20-psicat-navigator' };

function safeId(value) {
  if (typeof value !== 'string' || !/^[a-z0-9-]{1,64}$/.test(value)) throw new Error('Invalid platform target identifier.');
  return value;
}

function inside(root, candidate) {
  const r = path.resolve(root);
  const c = path.resolve(candidate);
  return c === r || c.startsWith(`${r}${path.sep}`);
}

function assertInside(root, candidate) {
  if (!inside(root, candidate)) throw new Error('Path must remain within its approved root.');
  return path.resolve(candidate);
}

function assertRegularFile(file) {
  const stat = fs.lstatSync(file);
  if (!stat.isFile() || stat.isSymbolicLink()) throw new Error('Expected a regular, non-symlink file.');
}

function hashFile(file) {
  return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
}

function hashFileAsync(file) {
  return new Promise((resolve, reject) => {
    const hash = crypto.createHash('sha256');
    let bytes = 0;
    fs.createReadStream(file).on('data', (chunk) => { bytes += chunk.length; hash.update(chunk); })
      .on('error', reject).on('end', () => resolve({ sha256: hash.digest('hex'), bytes }));
  });
}

const BUNDLED_MAX_BYTES = 256 * 1024 * 1024;
const BUNDLED_EXT = { 'android-sdam': '.apk', 'android-pentacorder': '.apk', 'uefi-az-kernel': '.efi' };

function parseBundledManifest(text) {
  let manifest;
  try { manifest = JSON.parse(text); } catch { throw new Error('Bundled manifest is not valid JSON.'); }
  if (!manifest || typeof manifest !== 'object' || Array.isArray(manifest) || manifest.formatVersion !== 1 || !Array.isArray(manifest.assets)) {
    throw new Error('Bundled manifest must have formatVersion 1 and an assets array.');
  }
  if (manifest.assets.length < 1 || manifest.assets.length > Object.keys(BUNDLED_EXT).length) throw new Error('Bundled manifest has an invalid asset count.');
  const assets = new Map();
  for (const asset of manifest.assets) {
    if (!asset || typeof asset !== 'object' || Array.isArray(asset)) throw new Error('Bundled asset entries must be objects.');
    const keys = Object.keys(asset).sort().join(',');
    if (keys !== 'file,sha256,sizeBytes,target') throw new Error('Bundled asset entries must contain exactly target, file, sha256, sizeBytes.');
    const { target, file, sha256, sizeBytes } = asset;
    if (!Object.prototype.hasOwnProperty.call(BUNDLED_EXT, target)) throw new Error('Bundled asset names an unknown target.');
    if (assets.has(target)) throw new Error(`Bundled manifest lists ${target} more than once.`);
    if (file !== `${target}${BUNDLED_EXT[target]}`) throw new Error(`Bundled asset file for ${target} must be exactly ${target}${BUNDLED_EXT[target]}.`);
    if (typeof sha256 !== 'string' || !/^[a-f0-9]{64}$/.test(sha256)) throw new Error('Bundled asset sha256 must be 64 lowercase hex characters.');
    if (!Number.isSafeInteger(sizeBytes) || sizeBytes < 1 || sizeBytes > BUNDLED_MAX_BYTES) throw new Error('Bundled asset sizeBytes is outside 1..256 MiB.');
    assets.set(target, { target, file, sha256, sizeBytes });
  }
  return assets;
}

function decodeWslList(text) {
  let value = String(text || '');
  if (value.includes('\0')) value = Buffer.from(value, 'binary').toString('utf16le');
  return value.replace(/^\uFEFF/, '').split(/\r?\n/).map((line) => line.replace(/\0/g, '').trim())
    .filter((line) => line && !line.startsWith('Windows Subsystem for Linux'));
}

function sanitizedEnv(source, extra = {}) {
  const env = {};
  for (const key of WINDOWS_ENV_ALLOWLIST) if (typeof source[key] === 'string') env[key] = source[key];
  return { ...env, ...extra };
}

function readWrapperProperties(file) {
  const props = {};
  for (const raw of fs.readFileSync(file, 'utf8').split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith('#') || line.startsWith('!')) continue;
    const match = /^([^=:\s]+)\s*[=:]\s*(.*)$/.exec(line);
    if (match) props[match[1]] = match[2].replace(/\\(.)/g, '$1');
  }
  return props;
}

// Mirrors the Gradle wrapper PathAssembler: <GRADLE_USER_HOME>/<distributionPath>/<dist>/<base36(md5(url))>.
function gradleWrapperCache(projectDir, env) {
  const props = readWrapperProperties(path.join(projectDir, 'gradle', 'wrapper', 'gradle-wrapper.properties'));
  const url = props.distributionUrl || '';
  const match = GRADLE_URL.exec(url);
  if (!match) throw new Error('Gradle wrapper distributionUrl is not an official services.gradle.org distribution.');
  if ((props.distributionBase || 'GRADLE_USER_HOME') !== 'GRADLE_USER_HOME' || (props.zipStoreBase || 'GRADLE_USER_HOME') !== 'GRADLE_USER_HOME') {
    throw new Error('Only GRADLE_USER_HOME wrapper distribution bases are supported.');
  }
  const distPath = props.distributionPath || 'wrapper/dists';
  if (path.isAbsolute(distPath) || path.win32.isAbsolute(distPath) || distPath.split(/[\\/]/).includes('..')) throw new Error('Gradle distributionPath must be relative.');
  let home = env.GRADLE_USER_HOME;
  if (typeof home !== 'string' || !home) {
    if (typeof env.USERPROFILE !== 'string' || !path.win32.isAbsolute(env.USERPROFILE)) throw new Error('USERPROFILE must be absolute to locate the Gradle cache.');
    home = path.join(env.USERPROFILE, '.gradle');
  } else if (!path.win32.isAbsolute(home)) {
    throw new Error('GRADLE_USER_HOME must be an absolute path.');
  }
  const version = match[1];
  const zipName = url.slice(url.lastIndexOf('/') + 1);
  const distName = zipName.slice(0, -4);
  const hash = BigInt(`0x${crypto.createHash('md5').update(url, 'utf8').digest('hex')}`).toString(36);
  const dir = path.join(home, ...distPath.split(/[\\/]/), distName, hash);
  const result = { version, distribution: distName, gradleUserHome: home, cached: false, reason: '' };
  try {
    const realHome = fs.realpathSync(home);
    const realDir = fs.realpathSync(dir);
    if (!realDir.startsWith(realHome + path.sep)) throw new Error('escape');
    if (!fs.lstatSync(path.join(realDir, `${zipName}.ok`)).isFile()) throw new Error('marker');
    const install = path.join(realDir, `gradle-${version}`);
    if (!fs.lstatSync(path.join(install, 'bin', 'gradle.bat')).isFile()) throw new Error('launcher');
    const versionJar = new RegExp(`^gradle-[a-z0-9-]+-${version.replace(/\./g, '\\.')}\\.jar$`);
    if (!fs.readdirSync(path.join(install, 'lib')).some((name) => versionJar.test(name))) throw new Error('version');
    result.cached = true;
  } catch {
    result.reason = `Gradle ${version} (${distName}) is not fully cached with a .zip.ok marker under GRADLE_USER_HOME; the wrapper would download it.`;
  }
  return result;
}

function resolveExecutable(name, env, exists) {
  if (SYSTEM_TOOLS.has(name)) {
    const systemRoot = env.SystemRoot || env.SYSTEMROOT;
    if (typeof systemRoot !== 'string' || !path.win32.isAbsolute(systemRoot)) throw new Error('SystemRoot must be an absolute Windows path.');
    const file = path.win32.join(systemRoot, 'System32', name);
    if (!exists(file)) throw new Error(`Required Windows component is unavailable: ${name}`);
    return file;
  }
  const entries = String(env.PATH || env.Path || '').split(';')
    .map((entry) => entry.trim().replace(/^"(.*)"$/, '$1'))
    .filter((entry) => entry && path.win32.isAbsolute(entry));
  for (const entry of entries) {
    const file = path.win32.join(entry, name);
    if (exists(file)) return file;
  }
  throw new Error(`Required tool was not found in an absolute PATH entry: ${name}`);
}

function trackExit(child) {
  if (child.__azExit) return child.__azExit;
  let resolve;
  const state = { done: child.exitCode !== null && child.exitCode !== undefined, promise: null };
  state.promise = new Promise((r) => { resolve = r; });
  const done = (code, signal) => {
    if (state.done && state.settled) return;
    state.done = true;
    state.settled = true;
    resolve({ code, signal });
  };
  child.once('close', done);
  child.once('error', () => done(null, 'error'));
  if (state.done) done(child.exitCode, child.signalCode);
  Object.defineProperty(child, '__azExit', { value: state });
  return state;
}

function waitFor(promise, ms) {
  let timer;
  return Promise.race([
    promise.then((value) => ({ value, timedOut: false })),
    new Promise((resolve) => { timer = setTimeout(() => resolve({ timedOut: true }), ms); }),
  ]).finally(() => clearTimeout(timer));
}

function defaultProbe(port, pathname, timeoutMs = 1500) {
  return new Promise((resolve) => {
    const req = http.get({ hostname: '127.0.0.1', port, path: pathname, timeout: timeoutMs }, (res) => {
      res.resume();
      resolve({ listening: true, statusCode: res.statusCode });
    });
    req.on('timeout', () => { req.destroy(); resolve({ listening: true, statusCode: 0 }); });
    req.on('error', (error) => resolve({ listening: error.code !== 'ECONNREFUSED', statusCode: 0, error: error.code }));
  });
}

function createPlatformTargets(options = {}) {
  const repositoryRoot = path.resolve(options.repositoryRoot || path.resolve(__dirname, '../../..'));
  if (options.bundledDirectory !== undefined && (typeof options.bundledDirectory !== 'string' || !path.isAbsolute(options.bundledDirectory))) {
    throw new Error('bundledDirectory must be an absolute path.');
  }
  const bundledDirectory = options.bundledDirectory ? path.resolve(options.bundledDirectory) : null;
  const dataRoot = path.resolve(options.dataRoot || path.join(os.homedir(), 'AppData', 'Local', 'AxiomZero PC Suite', 'platform-targets'));
  const platform = options.platform || process.platform;
  const spawnImpl = options.spawn || spawn;
  const probe = options.probe || defaultProbe;
  const exists = options.fileExists || ((file) => fs.existsSync(file));
  const baseEnv = options.env || process.env;
  const bound = (value, fallback) => (Number.isInteger(value) && value > 0 ? Math.min(value, fallback) : fallback);
  const timeoutMs = bound(options.timeoutMs, DEFAULT_TIMEOUT_MS);
  const startupTimeoutMs = bound(options.startupTimeoutMs, DEFAULT_STARTUP_MS);
  const stopTimeoutMs = bound(options.stopTimeoutMs, DEFAULT_STOP_MS);
  const pollMs = bound(options.pollMs, 1000);

  let activeOperation = null;
  let quitting = false;
  let service = null;
  const liveChildren = new Set();

  const requireWindows = () => {
    if (platform !== 'win32') throw new Error('This action is available only on Windows.');
  };
  const exe = (name) => resolveExecutable(name, baseEnv, exists);

  async function terminate(child) {
    const exit = trackExit(child);
    if (exit.done) return;
    if (platform === 'win32' && Number.isInteger(child.pid)) {
      const killer = spawnImpl(exe('taskkill.exe'), ['/pid', String(child.pid), '/t', '/f'], {
        shell: false, windowsHide: true, stdio: 'ignore', env: sanitizedEnv(baseEnv),
      });
      const killed = await waitFor(trackExit(killer).promise, stopTimeoutMs);
      if (killed.timedOut) throw new Error(`taskkill did not finish for owned PID ${child.pid}.`);
      if (killed.value.code !== 0 && !exit.done) throw new Error(`taskkill failed (${killed.value.code}) for owned PID ${child.pid}.`);
    } else {
      child.kill('SIGTERM');
    }
    let result = await waitFor(exit.promise, stopTimeoutMs);
    if (result.timedOut && platform !== 'win32') {
      child.kill('SIGKILL');
      result = await waitFor(exit.promise, stopTimeoutMs);
    }
    if (result.timedOut) throw new Error(`Owned process ${child.pid ?? ''} did not exit after termination.`);
  }

  function capture(file, args, cwd, extraEnv = {}) {
    if (quitting) return Promise.reject(new Error('Platform target manager is shutting down.'));
    if (!Array.isArray(args) || args.some((arg) => typeof arg !== 'string' || arg.includes('\0'))) {
      return Promise.reject(new Error('Process arguments must be a string array.'));
    }
    return new Promise((resolve, reject) => {
      let child;
      try {
        child = spawnImpl(file, args, {
          cwd, env: sanitizedEnv(baseEnv, extraEnv), shell: false, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'],
        });
      } catch (error) {
        reject(error);
        return;
      }
      liveChildren.add(child);
      const exit = trackExit(child);
      const out = { value: '' };
      const err = { value: '' };
      const collect = (target) => (chunk) => {
        const next = target.value + chunk.toString();
        target.value = next.length > MAX_OUTPUT ? next.slice(-MAX_OUTPUT) : next;
      };
      child.stdout?.on('data', collect(out));
      child.stderr?.on('data', collect(err));
      let spawnError = null;
      child.once('error', (error) => { spawnError = error; });
      let timedOut = false;
      const timer = setTimeout(() => {
        timedOut = true;
        terminate(child).catch((error) => { spawnError = error; });
      }, timeoutMs);
      exit.promise.then(({ code, signal }) => {
        clearTimeout(timer);
        liveChildren.delete(child);
        const tail = err.value.trim().slice(-2000);
        if (timedOut || spawnError || code !== 0) {
          const reason = timedOut ? `timed out after ${timeoutMs} ms` : spawnError ? spawnError.message : `exit ${code ?? signal}`;
          const error = new Error(`${path.win32.basename(file)} failed: ${reason}${tail ? ` — ${tail}` : ''}`);
          Object.assign(error, { code: timedOut ? 'ETIMEDOUT' : code, signal, stdout: out.value, stderr: err.value });
          reject(error);
        } else {
          resolve({ stdout: out.value, stderr: err.value });
        }
      });
    });
  }

  async function exclusive(fn) {
    if (quitting) throw new Error('Platform target manager is shutting down.');
    if (activeOperation) throw new Error('Another platform target operation is already running.');
    const run = (async () => fn())();
    activeOperation = run.catch(() => {});
    try { return await run; } finally { activeOperation = null; }
  }

  const productPath = (relative) => {
    const candidate = assertInside(repositoryRoot, path.join(repositoryRoot, relative));
    const realRoot = fs.realpathSync(repositoryRoot);
    const real = fs.realpathSync(candidate);
    if (!inside(realRoot, real)) throw new Error('Product path resolves outside the repository.');
    return real;
  };
  const checkedFile = (root, candidate) => {
    const file = assertInside(root, candidate);
    assertRegularFile(file);
    if (!inside(fs.realpathSync(root), fs.realpathSync(file))) throw new Error('File resolves outside its approved root.');
    return file;
  };
  const dataDirectory = (name) => {
    fs.mkdirSync(dataRoot, { recursive: true });
    const realRoot = fs.realpathSync(dataRoot);
    const directory = path.join(realRoot, name);
    fs.mkdirSync(directory, { recursive: true });
    const real = fs.realpathSync(directory);
    if (real === realRoot || !inside(realRoot, real)) throw new Error('Data directory resolves outside its approved root.');
    return real;
  };
  const writeReceipt = (data) => {
    const receipts = dataDirectory('receipts');
    const receipt = { schemaVersion: 1, completedAt: new Date().toISOString(), ...data };
    const file = path.join(receipts, `${Date.now()}-${crypto.randomUUID()}-${data.target}-${data.action}.json`);
    fs.writeFileSync(file, `${JSON.stringify(receipt, null, 2)}\n`, { flag: 'wx' });
    return { ...receipt, receiptPath: file };
  };

  function missingFiles(project, files) {
    let root;
    try { root = productPath(project); } catch { return [project]; }
    return files.filter((file) => {
      try { checkedFile(root, path.join(root, file)); return false; } catch { return true; }
    }).map((file) => `${project}/${file}`);
  }

  function androidMissing(spec) {
    return missingFiles(spec.project, ['gradlew.bat', 'gradle/wrapper/gradle-wrapper.jar', 'gradle/wrapper/gradle-wrapper.properties', 'settings.gradle.kts', spec.catalog]);
  }

  function list() {
    let bundledTargets = new Set();
    if (bundledDirectory) {
      try { bundledTargets = new Set(readBundledManifest().keys()); }
      catch (error) { if (error.code !== 'ENOENT') throw error; }
    }
    const targets = Object.entries(ANDROID).map(([id, spec]) => {
      const missing = androidMissing(spec);
      let gradleOfflineReady = false;
      let gradleOfflineError = null;
      if (!missing.length) {
        try { gradleOfflineReady = gradleWrapperCache(productPath(spec.project), baseEnv).cached; }
        catch (error) { gradleOfflineError = error.message; }
      }
      return {
        id, productId: spec.productId, name: spec.name, kind: 'android',
        status: missing.length ? 'blocked' : 'buildable', missing, gradleOfflineReady, gradleOfflineError, bundled: bundledTargets.has(id),
        actions: [...(missing.length ? [] : ['prepare']), ...(bundledTargets.has(id) ? ['importBundled'] : []), 'install', 'launchAndroid'],
        notes: 'Gradle assembleDebug from tracked source; install is a non-replacing adb install to one exact selected serial. Launch requires an already running authorized Android device or emulator and the installed debug APK; hardware-dependent features may be unavailable.',
      };
    });
    const uefiMissing = missingFiles(UEFI.project, UEFI.required);
    targets.push({
      id: 'uefi-az-kernel', productId: UEFI.productId, name: UEFI.name, kind: 'uefi',
      status: uefiMissing.length ? 'blocked' : 'buildable', missing: uefiMissing, bundled: bundledTargets.has('uefi-az-kernel'),
      actions: [...(uefiMissing.length ? [] : ['prepare']), ...(bundledTargets.has('uefi-az-kernel') ? ['importBundled'] : [])],
      notes: 'Exports the Cargo x86_64-unknown-uefi .efi file only; never writes firmware, removable media, ESP partitions, or boot variables.',
    });
    targets.push({
      id: 'wsl-psicat-navigator', productId: NAVIGATOR.productId, name: 'PsiCat Navigator (WSL2)', kind: 'wsl2',
      status: 'conditional', missing: missingFiles(NAVIGATOR.project, ['run.py', 'requirements.txt']),
      actions: ['provisionPosix', 'runPosix'],
      notes: 'Requires an explicitly selected registered WSL distro with python3-venv and ss (iproute2). Local execution is forced off.',
    });
    return targets;
  }

  async function prepare(id, opts = {}) {
    safeId(id);
    if (opts.allowNetwork !== undefined && typeof opts.allowNetwork !== 'boolean') throw new Error('allowNetwork must be boolean.');
    const allowNetwork = opts.allowNetwork === true;
    return exclusive(async () => {
      requireWindows();
      let product, file, args, artifact, extraEnv = {}, productId;
      if (ANDROID[id]) {
        const spec = ANDROID[id];
        const missing = androidMissing(spec);
        if (missing.length) throw new Error(`${spec.name} is blocked; missing: ${missing.join(', ')}`);
        product = productPath(spec.project);
        productId = spec.productId;
        file = exe('cmd.exe');
        const cache = gradleWrapperCache(product, baseEnv);
        if (!allowNetwork && !cache.cached) {
          const error = new Error(`${cache.reason} Offline prepare refused; run one consented build with allowNetwork: true first.`);
          error.code = 'GRADLE_DISTRIBUTION_NOT_CACHED';
          throw error;
        }
        extraEnv = { GRADLE_USER_HOME: cache.gradleUserHome };
        args = ['/d', '/s', '/c', `gradlew.bat --no-daemon${allowNetwork ? '' : ' --offline'} assembleDebug`];
        artifact = path.join(product, ...spec.artifact);
      } else if (id === 'uefi-az-kernel') {
        const missing = missingFiles(UEFI.project, UEFI.required);
        if (missing.length) throw new Error(`UEFI build is blocked; missing: ${missing.join(', ')}`);
        if (opts.profile !== undefined && !['debug', 'release'].includes(opts.profile)) throw new Error('profile must be debug or release.');
        const profile = opts.profile || 'debug';
        product = productPath(UEFI.project);
        productId = UEFI.productId;
        file = exe('cargo.exe');
        args = ['build', '--locked', '--target', 'x86_64-unknown-uefi'];
        if (!allowNetwork) args.push('--offline');
        if (profile === 'release') args.push('--release');
        if (!allowNetwork) extraEnv = { RUSTUP_AUTO_INSTALL: '0' };
        artifact = path.join(product, 'target', 'x86_64-unknown-uefi', profile, 'az-kernel.efi');
      } else {
        throw new Error('This target has no prepare action.');
      }
      const startedAt = Date.now();
      await capture(file, args, product, extraEnv);
      const built = checkedFile(product, artifact);
      if (fs.statSync(built).mtimeMs < startedAt - 2000) throw new Error('Build did not produce a fresh artifact.');
      const artifacts = dataDirectory('artifacts');
      const dest = path.join(artifacts, `${id}-${Date.now()}-${crypto.randomUUID()}${path.extname(built)}`);
      fs.copyFileSync(built, dest, fs.constants.COPYFILE_EXCL);
      return writeReceipt({
        target: id, productId, action: 'prepare', status: 'success', source: 'build', networkAllowed: allowNetwork,
        artifact: path.basename(dest), artifactPath: dest, bytes: fs.statSync(dest).size, sha256: hashFile(dest),
      });
    });
  }

  function readBundledManifest() {
    if (!bundledDirectory) throw new Error('No bundled artifact directory is configured.');
    const file = path.join(bundledDirectory, 'manifest.json');
    assertRegularFile(file);
    if (fs.statSync(file).size > 64 * 1024) throw new Error('Bundled manifest is too large.');
    return parseBundledManifest(fs.readFileSync(file, 'utf8'));
  }

  async function importBundled(id) {
    safeId(id);
    if (!Object.prototype.hasOwnProperty.call(BUNDLED_EXT, id)) throw new Error('This target has no bundled artifact action.');
    return exclusive(async () => {
      if (quitting) throw new Error('Platform target manager is shutting down.');
      const asset = readBundledManifest().get(id);
      if (!asset) throw new Error(`No bundled artifact is listed for ${id}.`);
      const realBundle = fs.realpathSync(bundledDirectory);
      const source = path.join(realBundle, asset.file);
      assertRegularFile(source);
      if (!inside(realBundle, fs.realpathSync(source))) throw new Error('Bundled artifact resolves outside the bundled directory.');
      if (fs.statSync(source).size !== asset.sizeBytes) throw new Error(`Bundled ${asset.file} size does not match the manifest.`);
      const artifacts = dataDirectory('artifacts');
      const dest = path.join(artifacts, `${id}-${Date.now()}-${crypto.randomUUID()}${BUNDLED_EXT[id]}`);
      fs.copyFileSync(source, dest, fs.constants.COPYFILE_EXCL);
      // Verify the copy that will actually be used, so a source swapped after the checks cannot slip through.
      const actual = await hashFileAsync(dest);
      if (actual.bytes !== asset.sizeBytes || actual.sha256 !== asset.sha256) {
        fs.rmSync(dest, { force: true });
        throw new Error(`Bundled ${asset.file} does not match its manifest hash/size; nothing was imported.`);
      }
      return writeReceipt({
        target: id, productId: id === 'uefi-az-kernel' ? UEFI.productId : ANDROID[id].productId, action: 'prepare', status: 'success',
        source: 'bundled', networkAllowed: false, artifact: path.basename(dest), artifactPath: dest, bytes: actual.bytes, sha256: actual.sha256,
      });
    });
  }

  function hasPrepareReceipt(id, artifactName, sha256) {
    const receipts = dataDirectory('receipts');
    const names = fs.readdirSync(receipts).filter((name) => name.endsWith(`-${id}-prepare.json`));
    if (names.length > 10000) throw new Error('Too many receipts to verify artifact provenance.');
    return names.some((name) => {
      try {
        const file = path.join(receipts, name);
        assertRegularFile(file);
        const receipt = JSON.parse(fs.readFileSync(file, 'utf8'));
        return receipt.target === id && receipt.action === 'prepare' && receipt.status === 'success' && receipt.artifact === artifactName && receipt.sha256 === sha256;
      } catch { return false; }
    });
  }

  async function adbDevices() {
    requireWindows();
    const listing = await capture(exe('adb.exe'), ['devices'], repositoryRoot);
    return listing.stdout.split(/\r?\n/).slice(1)
      .map((line) => line.trim().split(/\s+/))
      .filter((row) => row.length >= 2 && /^[A-Za-z0-9._:-]{1,128}$/.test(row[0]))
      .map(([serial, state]) => ({ serial, state }));
  }

  async function install(id, opts = {}) {
    safeId(id);
    if (!ANDROID[id]) throw new Error('Only Android APK targets support adb install.');
    const { serial, apkPath } = opts;
    if (typeof serial !== 'string' || !/^[A-Za-z0-9._:-]{1,128}$/.test(serial)) throw new Error('An exact ADB device serial is required.');
    if (typeof apkPath !== 'string' || apkPath.includes('\0')) throw new Error('Select a previously prepared APK.');
    return exclusive(async () => {
      requireWindows();
      const artifacts = dataDirectory('artifacts');
      const apk = assertInside(artifacts, apkPath);
      if (!path.basename(apk).startsWith(`${id}-`) || path.extname(apk).toLowerCase() !== '.apk') throw new Error('Selected artifact was not prepared for this target.');
      checkedFile(artifacts, apk);
      const devices = await adbDevices();
      if (!devices.some((device) => device.serial === serial && device.state === 'device')) {
        throw new Error('The explicitly selected ADB serial is not connected in device state; no device was selected automatically.');
      }
      const sha256 = hashFile(apk);
      if (!hasPrepareReceipt(id, path.basename(apk), sha256)) throw new Error('Selected APK has no matching prepare receipt (built or bundled); refusing to install.');
      await capture(exe('adb.exe'), ['-s', serial, 'install', apk], repositoryRoot);
      return writeReceipt({
        target: id, productId: ANDROID[id].productId, action: 'install', status: 'success',
        deviceSerialSha256: crypto.createHash('sha256').update(serial).digest('hex'), apk: path.basename(apk), sha256,
      });
    });
  }

  async function launchAndroid(id, opts = {}) {
    safeId(id);
    if (!ANDROID[id]) throw new Error('Only registered Android APK targets can be launched.');
    const { serial } = opts;
    if (typeof serial !== 'string' || !/^[A-Za-z0-9._:-]{1,128}$/.test(serial)) throw new Error('An exact ADB device serial is required.');
    return exclusive(async () => {
      requireWindows();
      const devices = await adbDevices();
      if (!devices.some((device) => device.serial === serial && device.state === 'device')) {
        throw new Error('The explicitly selected ADB serial is not connected in device state; no device was selected automatically.');
      }
      const activity = ANDROID[id].activity;
      const result = await capture(exe('adb.exe'), ['-s', serial, 'shell', 'am', 'start', '-W', '-n', activity], repositoryRoot);
      if (!/^Status:\s*ok\s*$/mi.test(result.stdout) ||
          !new RegExp(`^Activity:\\s*${activity.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s*$`, 'mi').test(result.stdout)) {
        throw new Error(`Android did not confirm the requested activity launch: ${(result.stdout + result.stderr).slice(-2000)}`);
      }
      return writeReceipt({
        target: id, productId: ANDROID[id].productId, action: 'launchAndroid', status: 'launched',
        deviceSerialSha256: crypto.createHash('sha256').update(serial).digest('hex'), activity,
      });
    });
  }

  async function listDistros() {
    requireWindows();
    const result = await capture(exe('wsl.exe'), ['--list', '--quiet'], repositoryRoot);
    return decodeWslList(result.stdout);
  }

  async function selectedDistro(value) {
    if (typeof value !== 'string' || !/^[A-Za-z0-9._-]{1,64}$/.test(value)) throw new Error('Select a WSL distribution from the registered list.');
    if (!(await listDistros()).includes(value)) throw new Error('Selected WSL distribution is not registered.');
    return value;
  }

  const linuxPathPattern = /^\/[^\0\r\n:]*$/;
  async function wslContext(distro) {
    const wsl = exe('wsl.exe');
    const run = async (args) => (await capture(wsl, ['--distribution', distro, '--exec', ...args], repositoryRoot)).stdout.trim();
    const product = await run(['wslpath', '-a', productPath(NAVIGATOR.project)]);
    const repo = await run(['wslpath', '-a', fs.realpathSync(repositoryRoot)]);
    const home = await run(['printenv', 'HOME']);
    if (![product, repo, home].every((value) => linuxPathPattern.test(value))) throw new Error('WSL returned an unsupported path.');
    if (!/^\/[A-Za-z0-9._/-]+$/.test(home)) throw new Error('WSL returned an unsupported home directory.');
    return { wsl, run, product, repo, home, venv: path.posix.join(home, '.local', 'share', 'axiomzero-pc-suite', 'product20') };
  }

  async function provisionPosix(opts = {}) {
    return exclusive(async () => {
      requireWindows();
      if (service) throw new Error('Stop the running WSL Navigator before provisioning.');
      const distro = await selectedDistro(opts.distro);
      const ctx = await wslContext(distro);
      await ctx.run(['python3', '-m', 'venv', ctx.venv]);
      await capture(ctx.wsl, ['--distribution', distro, '--cd', ctx.product, '--exec',
        '/usr/bin/env', 'PYTHONNOUSERSITE=1', `${ctx.venv}/bin/python`, '-m', 'pip', 'install', '--disable-pip-version-check', '-r', 'requirements.txt'], repositoryRoot);
      await ctx.run([`${ctx.venv}/bin/python`, '-m', 'pip', 'check']);
      return writeReceipt({ target: 'wsl-psicat-navigator', productId: NAVIGATOR.productId, action: 'provision', status: 'success', distro });
    });
  }

  // Every Windows loopback listener on the port must be the WSL localhost relay; anything else (or none, e.g. mirrored networking) fails.
  async function verifyWindowsListener() {
    const table = (await capture(exe('netstat.exe'), ['-a', '-n', '-o'], dataDirectory('logs'))).stdout;
    const pids = new Set();
    for (const line of table.split(/\r?\n/)) {
      const cols = line.trim().split(/\s+/);
      if (cols.length !== 5 || !/^TCP$/i.test(cols[0]) || !/^(0\.0\.0\.0|\[::\]):0$/.test(cols[2])) continue;
      if (!new RegExp(`:${NAVIGATOR_PORT}$`).test(cols[1]) || !/^\d+$/.test(cols[4])) continue;
      pids.add(Number(cols[4]));
    }
    if (!pids.size) throw new Error('Windows-side listener ownership cannot be proven (no WSL relay listener; mirrored networking is unsupported).');
    for (const pid of pids) {
      const row = (await capture(exe('tasklist.exe'), ['/fi', `PID eq ${pid}`, '/fo', 'csv', '/nh'], dataDirectory('logs'))).stdout;
      const image = /^"([^"]+)","(\d+)"/.exec(row.trim());
      if (!image || Number(image[2]) !== pid || image[1].toLowerCase() !== 'wslrelay.exe') {
        throw new Error(`Windows port ${NAVIGATOR_PORT} listener PID ${pid} is not the WSL relay; refusing to treat it as the Navigator.`);
      }
    }
  }

  async function runPosix(opts = {}) {
    if (service) throw new Error('A WSL Navigator managed by this suite is already running.');
    return exclusive(async () => {
      requireWindows();
      const distro = await selectedDistro(opts.distro);
      const ctx = await wslContext(distro);
      await ctx.run(['test', '-x', `${ctx.venv}/bin/python`]);
      const before = await probe(NAVIGATOR_PORT, NAVIGATOR_HEALTH);
      if (before.listening) throw new Error(`Port ${NAVIGATOR_PORT} is already in use; an existing service is never adopted.`);
      if (quitting) throw new Error('Platform target manager is shutting down.');
      const child = spawnImpl(ctx.wsl, [
        '--distribution', distro, '--cd', ctx.product, '--exec', '/bin/sh', '-c', WSL_PID_SCRIPT, 'az-pc-suite',
        '/usr/bin/env', '-i', `HOME=${ctx.home}`, 'PATH=/usr/local/bin:/usr/bin:/bin', 'LANG=C.UTF-8',
        `PYTHONPATH=${ctx.repo}`, 'PYTHONNOUSERSITE=1', 'MERLIN_LOCAL_EXECUTION_ENABLED=0',
        `${ctx.venv}/bin/python`, 'run.py', '--host', '127.0.0.1', '--port', String(NAVIGATOR_PORT), '--no-open', '--local-execution', 'off',
      ], { cwd: repositoryRoot, env: sanitizedEnv(baseEnv), shell: false, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] });
      liveChildren.add(child);
      const exit = trackExit(child);
      const log = { value: '' };
      const collect = (chunk) => {
        const next = log.value + chunk.toString();
        log.value = next.length > MAX_OUTPUT ? next.slice(-MAX_OUTPUT) : next;
      };
      child.stdout?.on('data', collect);
      child.stderr?.on('data', collect);
      let linuxPid = null;
      const handle = {
        target: 'wsl-psicat-navigator', distro, port: NAVIGATOR_PORT,
        url: `http://127.0.0.1:${NAVIGATOR_PORT}/ox-navigator.html`,
        get pid() { return child.pid; },
        get closed() { return exit.done; },
        exited: exit.promise,
        diagnostics: () => log.value.slice(-8192),
        stop: () => stopService(),
      };
      const stopOwned = async () => {
        const errors = [];
        if (linuxPid && !exit.done) {
          try { await ctx.run(['kill', '-TERM', String(linuxPid)]); } catch (error) { if (!exit.done) errors.push(error); }
          const graceful = await waitFor(exit.promise, stopTimeoutMs);
          if (graceful.timedOut) {
            try { await ctx.run(['kill', '-KILL', String(linuxPid)]); } catch (error) { if (!exit.done) errors.push(error); }
          }
        }
        if (!exit.done) {
          try { await terminate(child); } catch (error) { errors.push(error); }
        }
        if (!exit.done) {
          throw new AggregateError(errors, 'WSL Navigator process did not exit; ownership retained.');
        }
        liveChildren.delete(child);
      };
      service = { handle, stopOwned };
      exit.promise.then(() => {
        liveChildren.delete(child);
        if (service && service.handle === handle) service = null;
      });
      try {
        const deadline = Date.now() + startupTimeoutMs;
        while (true) {
          if (exit.done) throw new Error('WSL Navigator exited before readiness.');
          if (quitting) throw new Error('Platform target manager is shutting down.');
          if (!linuxPid) {
            const match = /AZPCSUITE_PID=(\d+)/.exec(log.value);
            if (match) linuxPid = Number(match[1]);
          }
          if (linuxPid) {
            const health = await probe(NAVIGATOR_PORT, NAVIGATOR_HEALTH);
            if (health.statusCode === 200) {
              const listeners = await ctx.run(['ss', '-Hltnp', `sport = :${NAVIGATOR_PORT}`]);
              const pids = [...listeners.matchAll(/pid=(\d+)/g)].map((m) => Number(m[1]));
              if (!pids.length || pids.some((pid) => pid !== linuxPid)) throw new Error('Port listener is not owned by the launched Navigator process.');
              await verifyWindowsListener();
              return handle;
            }
          }
          if (Date.now() > deadline) throw new Error(`WSL Navigator was not ready within ${startupTimeoutMs} ms.`);
          await new Promise((resolve) => setTimeout(resolve, pollMs));
        }
      } catch (error) {
        try { await stopOwned(); } catch (stopError) { error.message += ` Cleanup failed: ${stopError.message}`; }
        if (service && service.handle === handle && exit.done) service = null;
        error.diagnostics = log.value.slice(-8192);
        throw error;
      }
    });
  }

  async function stopService() {
    if (!service) return;
    const current = service;
    await current.stopOwned();
    if (service === current) service = null;
  }

  async function close() {
    quitting = true;
    const errors = [];
    if (service) {
      try { await stopService(); } catch (error) { errors.push(error); }
    }
    for (const child of [...liveChildren]) {
      try { await terminate(child); liveChildren.delete(child); } catch (error) { errors.push(error); }
    }
    if (activeOperation) {
      const settled = await waitFor(activeOperation, stopTimeoutMs);
      if (settled.timedOut) errors.push(new Error('Active platform operation did not settle.'));
    }
    if (errors.length || liveChildren.size) throw new AggregateError(errors, 'Owned platform processes did not all exit; ownership retained.');
  }

  return Object.freeze({
    list,
    prepare,
    importBundled,
    listDevices: adbDevices,
    launchAndroid,
    install,
    listDistros,
    provisionPosix,
    runPosix,
    stopPosix: stopService,
    status: () => ({ busy: Boolean(activeOperation), quitting, service: service ? { target: service.handle.target, distro: service.handle.distro, url: service.handle.url } : null }),
    close,
  });
}

module.exports = { createPlatformTargets, parseBundledManifest, gradleWrapperCache, decodeWslList, resolveExecutable, sanitizedEnv, WSL_PID_SCRIPT };
