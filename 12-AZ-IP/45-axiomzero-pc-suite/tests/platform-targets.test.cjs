// SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
// Copyright (C) 2026  ThomasCory Walker-Pearson
'use strict';

const test = require('node:test');
const { after } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { EventEmitter } = require('node:events');
const { PassThrough } = require('node:stream');
const { spawn, execFileSync } = require('node:child_process');
const { createPlatformTargets, parseBundledManifest, decodeWslList, resolveExecutable, sanitizedEnv } = require('../lib/platform-targets.cjs');

const WRAPPER_PROPS = 'distributionBase=GRADLE_USER_HOME\ndistributionPath=wrapper/dists\ndistributionUrl=https\\://services.gradle.org/distributions/gradle-8.6-bin.zip\nzipStoreBase=GRADLE_USER_HOME\nzipStorePath=wrapper/dists\n';
const DIST_URL = 'https://services.gradle.org/distributions/gradle-8.6-bin.zip';
const distHash = (url) => BigInt(`0x${crypto.createHash('md5').update(url).digest('hex')}`).toString(36);

function cacheGradle(home, { version = '8.6', ok = true, url = DIST_URL } = {}) {
  const dir = path.join(home, 'wrapper', 'dists', 'gradle-8.6-bin', distHash(url));
  writeFile(path.join(dir, `gradle-${version}`, 'bin', 'gradle.bat'));
  writeFile(path.join(dir, `gradle-${version}`, 'lib', `gradle-launcher-${version}.jar`));
  if (ok) writeFile(path.join(dir, 'gradle-8.6-bin.zip.ok'), '');
  return dir;
}

const fixtureRoot = path.join(__dirname, `.platform-targets-test-data-${process.pid}-${crypto.randomUUID()}`);
after(() => fs.rmSync(fixtureRoot, { recursive: true, force: true }));
let nextPid = 1000;

const ENV = {
  SystemRoot: 'C:\\Windows',
  PATH: 'C:\\Tools;relative\\bin',
  OPENROUTER_API_KEY: 'secret-openrouter',
  PSICAT_VITE_WORKBENCH_TOKEN: 'secret-token',
  WSLENV: 'OPENROUTER_API_KEY/u',
};

test('real emulator installs and launches both Android activities', {
  skip: !process.env.P45_ANDROID_EMULATOR_SERIAL,
  timeout: 120000,
}, async () => {
  const serial = process.env.P45_ANDROID_EMULATOR_SERIAL;
  const adb = process.env.P45_ANDROID_ADB;
  assert.ok(adb && path.isAbsolute(adb), 'P45_ANDROID_ADB must be an absolute executable path');
  const apps = [
    ['android-sdam', process.env.P45_ANDROID_SDAM_APK, 'com.sdam.debug'],
    ['android-pentacorder', process.env.P45_ANDROID_PENTACORDER_APK, 'com.axiomzero.pentacorder.debug'],
  ];
  const api = createPlatformTargets({
    repositoryRoot: path.resolve(__dirname, '../../..'),
    dataRoot: path.join(fixtureRoot, 'emulator'),
    platform: 'win32',
    env: { SystemRoot: 'C:\\Windows', PATH: 'C:\\Android' },
    fileExists: (file) => file === 'C:\\Android\\adb.exe',
    spawn: (_exe, args, options) => spawn(adb, args, {
      ...options, env: { HOME: process.env.HOME, PATH: process.env.PATH, ANDROID_HOME: process.env.ANDROID_HOME },
    }),
  });
  for (const [id, apk, packageName] of apps) {
    assert.ok(apk && path.isAbsolute(apk), `APK path is required for ${id}`);
    // Test-only emulator: grant requested runtime permissions so the app activity can be observed.
    execFileSync(adb, ['-s', serial, 'install', '-g', apk], { encoding: 'utf8', timeout: 60000 });
    const receipt = await api.launchAndroid(id, { serial });
    assert.equal(receipt.status, 'launched');
    assert.ok(execFileSync(adb, ['-s', serial, 'shell', 'pidof', packageName], { encoding: 'utf8' }).trim());
  }
  await api.close();
});

function makeChild({ stdout = '', stderr = '', code = 0, keepOpen = false } = {}) {
  const child = new EventEmitter();
  child.pid = nextPid++;
  child.exitCode = null;
  child.signalCode = null;
  child.stdout = new PassThrough();
  child.stderr = new PassThrough();
  child.finish = (exitCode = 0, signal = null) => {
    if (child.exitCode !== null || child.signalCode !== null) return;
    child.exitCode = exitCode;
    child.signalCode = signal;
    child.stdout.end();
    child.stderr.end();
    child.emit('close', exitCode, signal);
  };
  child.kill = (signal) => { setImmediate(() => child.finish(null, signal || 'SIGTERM')); return true; };
  if (!keepOpen) setImmediate(() => {
    if (stdout) child.stdout.write(stdout);
    if (stderr) child.stderr.write(stderr);
    child.finish(code);
  });
  return child;
}

function writeFile(file, text = 'x') {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, text);
}

function harness({ handler, probe, pentacorderCatalog = false, gradleCached = true, bundle, extra = {} } = {}) {
  const base = path.join(fixtureRoot, crypto.randomUUID());
  const repo = path.join(base, 'repo');
  const data = path.join(base, 'data');
  for (const project of ['12-AZ-IP/14-sdam/app', '12-AZ-IP/15-pentacorder']) {
    for (const file of ['gradlew.bat', 'gradle/wrapper/gradle-wrapper.jar', 'settings.gradle.kts']) {
      writeFile(path.join(repo, project, file));
    }
    writeFile(path.join(repo, project, 'gradle/wrapper/gradle-wrapper.properties'), WRAPPER_PROPS);
  }
  writeFile(path.join(repo, '12-AZ-IP/14-sdam/app/gradle/libs.versions.toml'));
  if (pentacorderCatalog) writeFile(path.join(repo, '12-AZ-IP/15-pentacorder/gradle/libs.versions.toml'));
  for (const file of ['Cargo.toml', 'Cargo.lock', 'rust-toolchain.toml', 'assets/font8x16.bin']) writeFile(path.join(repo, '12-AZ-IP/02-az-kernel', file));
  for (const file of ['run.py', 'requirements.txt']) writeFile(path.join(repo, '12-AZ-IP/20-psicat-navigator', file));
  const gradleHome = path.join(base, 'gradle-home');
  if (gradleCached) cacheGradle(gradleHome);
  let bundledDirectory;
  if (bundle) {
    bundledDirectory = path.join(base, 'bundled');
    fs.mkdirSync(bundledDirectory, { recursive: true });
    bundle(bundledDirectory);
  }
  const calls = [];
  const children = new Map();
  const defaultHandler = (tool, args, opts) => {
    if (tool === 'taskkill.exe') {
      const target = children.get(Number(args[1]));
      const killer = makeChild();
      setImmediate(() => target?.finish(1));
      return killer;
    }
    if (tool === 'wsl.exe' && args[0] === '--list') return makeChild({ stdout: 'Ubuntu-24.04\r\nDebian\r\n' });
    if (tool === 'wsl.exe' && args.includes('wslpath')) return makeChild({ stdout: args.at(-1).includes('psicat') ? '/mnt/c/w/repo/12-AZ-IP/20-psicat-navigator\n' : '/mnt/c/w/repo\n' });
    if (tool === 'wsl.exe' && args.includes('printenv')) return makeChild({ stdout: '/home/alice\n' });
    if (tool === 'netstat.exe') return makeChild({ stdout: '\r\nActive Connections\r\n\r\n  Proto  Local Address  Foreign Address  State  PID\r\n  TCP    127.0.0.1:8020         0.0.0.0:0              LISTENING       7777\r\n  TCP    [::1]:8020             [::]:0                 LISTENING       7777\r\n  TCP    127.0.0.1:18020        0.0.0.0:0              LISTENING       5555\r\n' });
    if (tool === 'tasklist.exe') return makeChild({ stdout: `"${args[1] === 'PID eq 7777' ? 'wslrelay.exe' : 'other.exe'}","${args[1].slice(7)}","Console","1","8,000 K"\r\n` });
    if (tool === 'adb.exe' && args[0] === 'devices') return makeChild({ stdout: 'List of devices attached\nUSB:42\tdevice\nOther\tunauthorized\n' });
    if (tool === 'cmd.exe') {
      writeFile(path.join(opts.cwd, 'app/build/outputs/apk/debug/app-debug.apk'), 'apk fixture');
      return makeChild();
    }
    if (tool === 'cargo.exe') {
      writeFile(path.join(opts.cwd, 'target/x86_64-unknown-uefi', args.includes('--release') ? 'release' : 'debug', 'az-kernel.efi'), 'efi fixture');
      return makeChild();
    }
    return makeChild();
  };
  const spawn = (exe, args, opts) => {
    const tool = path.win32.basename(exe);
    calls.push({ exe, tool, args: [...args], opts });
    const child = (handler && handler(tool, args, opts, defaultHandler)) || defaultHandler(tool, args, opts);
    children.set(child.pid, child);
    return child;
  };
  const api = createPlatformTargets({
    repositoryRoot: repo, dataRoot: data, platform: 'win32', spawn, env: { ...ENV, GRADLE_USER_HOME: gradleHome }, bundledDirectory,
    fileExists: (file) => file.startsWith('C:\\'),
    probe: probe || (async () => ({ listening: false })),
    timeoutMs: 2000, startupTimeoutMs: 500, stopTimeoutMs: 300, pollMs: 5, ...extra,
  });
  return { repo, data, base, gradleHome, calls, children, api };
}

test('lists real targets and reports only actually missing build inputs', () => {
  const h = harness();
  const targets = Object.fromEntries(h.api.list().map((target) => [target.id, target]));
  assert.equal(targets['android-sdam'].status, 'buildable');
  assert.equal(targets['android-pentacorder'].status, 'blocked');
  assert.deepEqual(targets['android-pentacorder'].missing, ['12-AZ-IP/15-pentacorder/gradle/libs.versions.toml']);
  assert.match(targets['uefi-az-kernel'].notes, /never modifies physical firmware/);
  assert.equal(targets['wsl-psicat-navigator'].kind, 'wsl2');
  const restored = harness({ pentacorderCatalog: true });
  assert.equal(restored.api.list().find((target) => target.id === 'android-pentacorder').status, 'buildable');
});

test('resolves system tools from absolute SystemRoot and other tools only from absolute PATH entries', () => {
  const exists = (file) => file === 'C:\\Windows\\System32\\wsl.exe' || file === 'C:\\Tools\\adb.exe';
  assert.equal(resolveExecutable('wsl.exe', ENV, exists), 'C:\\Windows\\System32\\wsl.exe');
  assert.equal(resolveExecutable('adb.exe', ENV, exists), 'C:\\Tools\\adb.exe');
  assert.throws(() => resolveExecutable('cargo.exe', ENV, exists), /not found/);
  assert.throws(() => resolveExecutable('wsl.exe', { SystemRoot: 'Windows' }, exists), /absolute/);
  const env = sanitizedEnv(ENV);
  assert.equal(env.OPENROUTER_API_KEY, undefined);
  assert.equal(env.PSICAT_VITE_WORKBENCH_TOKEN, undefined);
  assert.equal(env.WSLENV, undefined);
});

test('prepares SDAM offline by default and installs only to the exact selected serial', async () => {
  const h = harness();
  const prepared = await h.api.prepare('android-sdam');
  assert.equal(prepared.networkAllowed, false);
  assert.match(prepared.sha256, /^[a-f0-9]{64}$/);
  const build = h.calls.find((call) => call.tool === 'cmd.exe');
  assert.equal(build.exe, 'C:\\Windows\\System32\\cmd.exe');
  assert.match(build.args.at(-1), /--offline assembleDebug$/);
  assert.equal(build.opts.shell, false);
  assert.equal(build.opts.env.OPENROUTER_API_KEY, undefined);
  assert.deepEqual(await h.api.listDevices(), [{ serial: 'USB:42', state: 'device' }, { serial: 'Other', state: 'unauthorized' }]);
  const installed = await h.api.install('android-sdam', { serial: 'USB:42', apkPath: prepared.artifactPath });
  const adb = h.calls.find((call) => call.tool === 'adb.exe' && call.args.includes('install'));
  assert.deepEqual(adb.args, ['-s', 'USB:42', 'install', prepared.artifactPath]);
  const receipt = JSON.parse(fs.readFileSync(installed.receiptPath, 'utf8'));
  assert.equal(receipt.deviceSerial, undefined);
  assert.match(receipt.deviceSerialSha256, /^[a-f0-9]{64}$/);
});

test('launches each debug activity only on the explicitly selected authorized target', async () => {
  const h = harness({
    handler(tool, args) {
      if (tool === 'adb.exe' && args.includes('start')) {
        return makeChild({ stdout: `Starting: Intent\nStatus: ok\nActivity: ${args.at(-1)}\n` });
      }
    }
  });
  for (const [id, activity] of [
    ['android-sdam', 'com.sdam.debug/com.sdam.MainActivity'],
    ['android-pentacorder', 'com.axiomzero.pentacorder.debug/com.gibbernode.MainActivity'],
  ]) {
    const receipt = await h.api.launchAndroid(id, { serial: 'USB:42' });
    assert.equal(receipt.status, 'launched');
    assert.equal(receipt.activity, activity);
    assert.deepEqual(h.calls.filter((call) => call.tool === 'adb.exe' && call.args.includes('start')).at(-1).args,
      ['-s', 'USB:42', 'shell', 'am', 'start', '-W', '-n', activity]);
    assert.equal(receipt.deviceSerial, undefined);
  }
  await assert.rejects(h.api.launchAndroid('android-sdam', { serial: 'Other' }), /not connected/);
  await assert.rejects(h.api.launchAndroid('android-sdam', { serial: 'bad serial' }), /exact ADB/);
  await assert.rejects(h.api.launchAndroid('uefi-az-kernel', { serial: 'USB:42' }), /Only registered Android/);
});

test('does not report success when Android fails or starts a different activity', async () => {
  for (const output of [
    'Error: Activity class does not exist.\n',
    'Status: timeout\nActivity: com.sdam.debug/com.sdam.MainActivity\n',
    'Status: ok\nActivity: unrelated.package/.MainActivity\n',
    'Starting: Intent { cmp=other/package }\nStatus: ok\nActivity: com.google.android.permissioncontroller/com.android.permissioncontroller.permission.ui.GrantPermissionsActivity\n',
  ]) {
    const h = harness({ handler(tool, args) {
      if (tool === 'adb.exe' && args.includes('start')) return makeChild({ stdout: output });
    } });
    await assert.rejects(h.api.launchAndroid('android-sdam', { serial: 'USB:42' }), /did not confirm/);
  }
});

test('reports an Android permission prompt without claiming the app activity launched', async () => {
  const h = harness({ handler(tool, args) {
    if (tool === 'adb.exe' && args.includes('start')) return makeChild({
      stdout: `Starting: Intent { cmp=${args.at(-1)} }\nStatus: ok\nActivity: com.google.android.permissioncontroller/com.android.permissioncontroller.permission.ui.GrantPermissionsActivity\n`,
    });
  } });
  const receipt = await h.api.launchAndroid('android-sdam', { serial: 'USB:42' });
  assert.equal(receipt.status, 'permission-required');
  assert.match(receipt.note, /not yet confirmed/);
});

test('rejects unauthorized devices, foreign artifacts and path escapes without installing', async () => {
  const h = harness();
  const prepared = await h.api.prepare('android-sdam', { allowNetwork: true });
  assert.doesNotMatch(h.calls.find((call) => call.tool === 'cmd.exe').args.at(-1), /--offline/);
  await assert.rejects(h.api.install('android-sdam', { serial: 'USB:42', apkPath: path.join(h.data, 'outside.apk') }), /approved root|not prepared/);
  await assert.rejects(h.api.install('android-sdam', { serial: 'bad serial', apkPath: prepared.artifactPath }), /exact ADB device serial/);
  await assert.rejects(h.api.install('android-sdam', { serial: 'Other', apkPath: prepared.artifactPath }), /no device was selected automatically/);
  await assert.rejects(h.api.install('android-pentacorder', { serial: 'USB:42', apkPath: prepared.artifactPath }), /not prepared for this target/);
  await assert.rejects(h.api.prepare('android-sdam', { allowNetwork: 'yes' }), /boolean/);
  assert.ok(!h.calls.some((call) => call.tool === 'adb.exe' && call.args.includes('install')));
});

test('keeps Pentacorder blocked until its catalog exists and exports UEFI without firmware mutation', async () => {
  const h = harness();
  await assert.rejects(h.api.prepare('android-pentacorder'), /libs\.versions\.toml/);
  const receipt = await h.api.prepare('uefi-az-kernel', { profile: 'release' });
  assert.equal(path.extname(receipt.artifact), '.efi');
  const cargo = h.calls.find((call) => call.tool === 'cargo.exe');
  assert.deepEqual(cargo.args, ['build', '--locked', '--target', 'x86_64-unknown-uefi', '--offline', '--release']);
  assert.equal(cargo.opts.env.RUSTUP_AUTO_INSTALL, '0');
  assert.ok(h.calls.every((call) => !/bcdedit|efibootmgr|mountvol|flash|diskpart/i.test([call.exe, ...call.args].join(' '))));
  await assert.rejects(h.api.prepare('uefi-az-kernel', { profile: '../x' }), /debug or release/);
});

test('preserves build failures and does not fabricate artifacts', async () => {
  const h = harness({ handler: (tool) => (tool === 'cargo.exe' ? makeChild({ code: 101, stderr: 'error: toolchain nightly-2024-09-01 is not installed' }) : null) });
  await assert.rejects(h.api.prepare('uefi-az-kernel'), (error) => /exit 101/.test(error.message) && /not installed/.test(error.stderr));
  assert.equal(fs.existsSync(path.join(h.data, 'artifacts')), false);
});

test('provisions only a registered distro with argv-only isolated venv calls', async () => {
  const h = harness();
  assert.deepEqual(await h.api.listDistros(), ['Ubuntu-24.04', 'Debian']);
  await assert.rejects(h.api.provisionPosix({ distro: 'Ubuntu-24.04; whoami' }), /registered list/);
  await assert.rejects(h.api.provisionPosix({ distro: 'Arch' }), /not registered/);
  await h.api.provisionPosix({ distro: 'Debian' });
  const wsl = h.calls.filter((call) => call.tool === 'wsl.exe');
  assert.ok(wsl.every((call) => call.exe === 'C:\\Windows\\System32\\wsl.exe' && call.opts.shell === false));
  assert.ok(wsl.filter((call) => call.args[0] !== '--list').every((call) => call.args[0] === '--distribution' && call.args[1] === 'Debian'));
  assert.ok(wsl.some((call) => call.args.includes('venv') && call.args.includes('/home/alice/.local/share/axiomzero-pc-suite/product20')));
  assert.ok(wsl.some((call) => call.args.includes('check')));
});

function readyHarness(overrides = {}) {
  let service;
  let health = 0;
  const h = harness({
    probe: overrides.probe || (async () => (service && health++ > 0 ? { listening: true, statusCode: 200 } : { listening: false })),
    handler(tool, args) {
      if (tool === 'wsl.exe' && args.includes('/bin/sh')) {
        service = makeChild({ keepOpen: true });
        setImmediate(() => service.stdout.write('AZPCSUITE_PID=4242\nLocal URL\n'));
        return service;
      }
      if (tool === 'wsl.exe' && args.includes('ss')) return makeChild({ stdout: overrides.ss || 'LISTEN 0 5 127.0.0.1:8020 0.0.0.0:* users:(("python",pid=4242,fd=3))\n' });
      if (tool === 'netstat.exe' && overrides.netstat !== undefined) return makeChild({ stdout: overrides.netstat });
      if (tool === 'netstat.exe' && overrides.netstatPid) return makeChild({ stdout: `  TCP    127.0.0.1:8020   0.0.0.0:0   LISTENING   7777\r\n  TCP    0.0.0.0:8020   0.0.0.0:0   LISTENING   ${overrides.netstatPid}\r\n` });
      if (tool === 'wsl.exe' && args.includes('kill')) {
        setImmediate(() => service?.finish(0));
        return makeChild();
      }
      return null;
    },
  });
  return { h, getService: () => service };
}

test('launches managed Navigator with stripped env, local execution off, and returns only after owned readiness', async () => {
  const { h } = readyHarness();
  const handle = await h.api.runPosix({ distro: 'Ubuntu-24.04' });
  const launch = h.calls.find((call) => call.args.includes('/bin/sh'));
  const argv = launch.args;
  assert.ok(argv.includes('-i'));
  assert.ok(argv.includes('PYTHONPATH=/mnt/c/w/repo'));
  assert.ok(argv.includes('PYTHONNOUSERSITE=1'));
  assert.ok(argv.includes('MERLIN_LOCAL_EXECUTION_ENABLED=0'));
  assert.deepEqual(argv.slice(-9), ['/home/alice/.local/share/axiomzero-pc-suite/product20/bin/python', 'run.py', '--host', '127.0.0.1', '--port', '8020', '--no-open', '--local-execution', 'off']);
  assert.deepEqual(argv.slice(0, 9), ['--distribution', 'Ubuntu-24.04', '--cd', '/mnt/c/w/repo/12-AZ-IP/20-psicat-navigator', '--exec', '/bin/sh', '-c', 'printf "AZPCSUITE_PID=%s\\n" "$$"; exec "$@"', 'az-pc-suite']);
  assert.equal(launch.opts.env.OPENROUTER_API_KEY, undefined);
  assert.equal(launch.opts.env.WSLENV, undefined);
  assert.ok(!argv.some((arg) => /secret/.test(arg)));
  assert.equal(h.api.status().service.distro, 'Ubuntu-24.04');
  await h.api.stopPosix();
  assert.equal(handle.closed, true);
  assert.ok(h.calls.some((call) => call.args.includes('kill') && call.args.includes('4242')));
  assert.equal(h.api.status().service, null);
});

test('never adopts an occupied port', async () => {
  const { h } = readyHarness({ probe: async () => ({ listening: true, statusCode: 200 }) });
  await assert.rejects(h.api.runPosix({ distro: 'Ubuntu-24.04' }), /never adopted/);
  assert.ok(!h.calls.some((call) => call.args.includes('/bin/sh')));
});

test('rejects a healthy port owned by another process and cleans up the launched child', async () => {
  const { h, getService } = readyHarness({ ss: 'LISTEN users:(("python",pid=999,fd=3))\n' });
  await assert.rejects(h.api.runPosix({ distro: 'Ubuntu-24.04' }), /not owned/);
  assert.equal(getService().exitCode !== null || getService().signalCode !== null, true);
  assert.equal(h.api.status().service, null);
});

test('fails startup on timeout with diagnostics and terminates the owned process tree', async () => {
  const { h, getService } = readyHarness({ probe: async () => ({ listening: false }) });
  await assert.rejects(h.api.runPosix({ distro: 'Ubuntu-24.04' }), (error) => /not ready/.test(error.message) && /AZPCSUITE_PID/.test(error.diagnostics));
  assert.ok(getService().exitCode !== null || getService().signalCode !== null);
});

test('serializes operations and close terminates active work through absolute taskkill', async () => {
  let running;
  const h = harness({ handler: (tool) => (tool === 'cmd.exe' ? (running = makeChild({ keepOpen: true })) : null) });
  const preparing = h.api.prepare('android-sdam');
  const outcome = preparing.then(() => null, (error) => error);
  await new Promise((resolve) => setImmediate(resolve));
  await assert.rejects(h.api.install('android-sdam', { serial: 'USB:42', apkPath: 'x.apk' }), /already running/);
  await h.api.close();
  assert.ok((await outcome) instanceof Error);
  const kill = h.calls.find((call) => call.tool === 'taskkill.exe');
  assert.equal(kill.exe, 'C:\\Windows\\System32\\taskkill.exe');
  assert.deepEqual(kill.args, ['/pid', String(running.pid), '/t', '/f']);
  await assert.rejects(h.api.prepare('android-sdam'), /shutting down/);
});

test('close reports and retains ownership when taskkill cannot stop a child', async () => {
  const h = harness({
    handler(tool) {
      if (tool === 'cmd.exe') return makeChild({ keepOpen: true });
      if (tool === 'taskkill.exe') return makeChild({ code: 128 });
      return null;
    },
  });
  const outcome = h.api.prepare('android-sdam').then(() => null, (error) => error);
  await new Promise((resolve) => setImmediate(resolve));
  await assert.rejects(h.api.close(), /ownership retained/);
  void outcome;
});

test('decodes WSL UTF-16 output and rejects non-Windows actions', async () => {
  assert.deepEqual(decodeWslList(Buffer.from('\uFEFFUbuntu\r\nDebian\r\n', 'utf16le').toString('binary')), ['Ubuntu', 'Debian']);
  const other = createPlatformTargets({ repositoryRoot: fixtureRoot, dataRoot: path.join(fixtureRoot, 'none'), platform: 'linux' });
  await assert.rejects(other.listDistros(), /only on Windows/);
  await assert.rejects(other.prepare('android-sdam'), /only on Windows/);
});

function writeBundle(dir, assets, content = {}) {
  for (const [file, text] of Object.entries(content)) writeFile(path.join(dir, file), text);
  writeFile(path.join(dir, 'manifest.json'), JSON.stringify({ formatVersion: 1, assets }));
}
const sha = (text) => crypto.createHash('sha256').update(text).digest('hex');
const asset = (target, text, ext = '.apk') => ({ target, file: `${target}${ext}`, sha256: sha(text), sizeBytes: Buffer.byteLength(text) });

test('offline Android prepare refuses before invoking the wrapper when the Gradle distribution is not cached', async () => {
  const h = harness({ gradleCached: false });
  await assert.rejects(h.api.prepare('android-sdam'), (error) => error.code === 'GRADLE_DISTRIBUTION_NOT_CACHED' && /allowNetwork: true/.test(error.message));
  assert.ok(!h.calls.some((call) => call.tool === 'cmd.exe'));
  assert.equal(h.api.list().find((t) => t.id === 'android-sdam').gradleOfflineReady, false);
  const online = await h.api.prepare('android-sdam', { allowNetwork: true });
  assert.equal(online.networkAllowed, true);
  const build = h.calls.find((call) => call.tool === 'cmd.exe');
  assert.doesNotMatch(build.args.at(-1), /--offline/);
  assert.equal(build.opts.env.GRADLE_USER_HOME, h.gradleHome);
});

test('offline Gradle check rejects a missing .zip.ok marker, wrong-version install and wrong URL hash directory', async () => {
  for (const variant of [{ ok: false }, { version: '8.5' }, { url: 'https://services.gradle.org/distributions/gradle-8.6-all.zip' }]) {
    const h = harness({ gradleCached: false });
    cacheGradle(h.gradleHome, variant);
    await assert.rejects(h.api.prepare('android-sdam'), { code: 'GRADLE_DISTRIBUTION_NOT_CACHED' });
    assert.ok(!h.calls.some((call) => call.tool === 'cmd.exe'));
  }
  const h = harness();
  assert.equal(h.api.list().find((t) => t.id === 'android-sdam').gradleOfflineReady, true);
});

test('offline Gradle check rejects non-official wrapper URLs and relative GRADLE_USER_HOME', async () => {
  const h = harness();
  writeFile(path.join(h.repo, '12-AZ-IP/14-sdam/app/gradle/wrapper/gradle-wrapper.properties'), 'distributionUrl=https\\://example.test/gradle-8.6-bin.zip\n');
  await assert.rejects(h.api.prepare('android-sdam'), /official/);
  const r = harness({ extra: { env: { ...ENV, GRADLE_USER_HOME: 'relative\\gradle' } } });
  await assert.rejects(r.api.prepare('android-sdam'), /absolute/);
  assert.ok(!h.calls.concat(r.calls).some((call) => call.tool === 'cmd.exe'));
});

test('imports a verified bundled APK without any build or download and install accepts it', async () => {
  const h = harness({ gradleCached: false, bundle: (dir) => writeBundle(dir, [asset('android-sdam', 'bundled apk')], { 'android-sdam.apk': 'bundled apk' }) });
  const target = h.api.list().find((t) => t.id === 'android-sdam');
  assert.equal(target.bundled, true);
  assert.ok(target.actions.includes('importBundled'));
  const imported = await h.api.importBundled('android-sdam');
  assert.equal(imported.source, 'bundled');
  assert.equal(imported.networkAllowed, false);
  assert.equal(imported.sha256, sha('bundled apk'));
  assert.equal(fs.readFileSync(imported.artifactPath, 'utf8'), 'bundled apk');
  assert.ok(!h.calls.some((call) => ['cmd.exe', 'cargo.exe'].includes(call.tool)));
  await h.api.install('android-sdam', { serial: 'USB:42', apkPath: imported.artifactPath });
  assert.ok(h.calls.some((call) => call.tool === 'adb.exe' && call.args.includes('install')));
});

test('imports a bundled UEFI image as export-only artifact', async () => {
  const h = harness({ bundle: (dir) => writeBundle(dir, [asset('uefi-az-kernel', 'efi bytes', '.efi')], { 'uefi-az-kernel.efi': 'efi bytes' }) });
  const imported = await h.api.importBundled('uefi-az-kernel');
  assert.match(imported.artifact, /^uefi-az-kernel-.*\.efi$/);
  assert.equal(imported.productId, '02');
  await assert.rejects(h.api.importBundled('android-sdam'), /No bundled artifact is listed/);
  await assert.rejects(h.api.importBundled('wsl-psicat-navigator'), /no bundled artifact action/);
});

test('target inspection surfaces corrupt bundled manifests instead of silently hiding bundled actions', () => {
  const h = harness({ bundle: (dir) => writeFile(path.join(dir, 'manifest.json'), '{broken') });
  assert.throws(() => h.api.list(), /JSON|Unexpected|manifest/i);
});

test('rejects bundled hash and size mismatches and leaves no artifact behind', async () => {
  const wrongHash = { ...asset('android-sdam', 'expected'), sizeBytes: Buffer.byteLength('tampered') };
  for (const [entry, text, pattern] of [[wrongHash, 'tampered', /hash\/size/], [asset('android-sdam', 'expected'), 'longer content', /size does not match/]]) {
    const h = harness({ bundle: (dir) => writeBundle(dir, [entry], { 'android-sdam.apk': text }) });
    await assert.rejects(h.api.importBundled('android-sdam'), pattern);
    const artifacts = path.join(h.data, 'artifacts');
    assert.deepEqual(fs.existsSync(artifacts) ? fs.readdirSync(artifacts) : [], []);
  }
});

test('bundled manifest validation rejects malformed, duplicate, traversal, oversized and unknown entries', () => {
  const ok = asset('android-sdam', 'x');
  const bad = [
    'not json',
    JSON.stringify({ formatVersion: 2, assets: [ok] }),
    JSON.stringify({ formatVersion: 1, assets: [] }),
    JSON.stringify({ formatVersion: 1, assets: [ok, ok] }),
    JSON.stringify({ formatVersion: 1, assets: [{ ...ok, file: '../android-sdam.apk' }] }),
    JSON.stringify({ formatVersion: 1, assets: [{ ...ok, file: 'android-sdam.efi' }] }),
    JSON.stringify({ formatVersion: 1, assets: [{ ...ok, target: 'wsl-psicat-navigator', file: 'wsl-psicat-navigator.apk' }] }),
    JSON.stringify({ formatVersion: 1, assets: [{ ...ok, sha256: 'ABC' }] }),
    JSON.stringify({ formatVersion: 1, assets: [{ ...ok, sizeBytes: 256 * 1024 * 1024 + 1 }] }),
    JSON.stringify({ formatVersion: 1, assets: [{ ...ok, extra: true }] }),
  ];
  for (const text of bad) assert.throws(() => parseBundledManifest(text));
  assert.equal(parseBundledManifest(JSON.stringify({ formatVersion: 1, assets: [ok] })).get('android-sdam').file, 'android-sdam.apk');
});

test('bundled import refuses symlinked assets and missing files; invalid bundledDirectory option is rejected', async (t) => {
  const outside = path.join(fixtureRoot, `outside-${crypto.randomUUID()}.apk`);
  writeFile(outside, 'x');
  const h = harness({ bundle: (dir) => {
    writeBundle(dir, [asset('android-sdam', 'x'), asset('android-pentacorder', 'y')]);
    try { fs.symlinkSync(outside, path.join(dir, 'android-sdam.apk')); } catch { t.skip('symlinks unavailable'); }
  } });
  await assert.rejects(h.api.importBundled('android-sdam'), /non-symlink/);
  await assert.rejects(h.api.importBundled('android-pentacorder'), /ENOENT|non-symlink/);
  assert.throws(() => createPlatformTargets({ bundledDirectory: 'relative/dir' }), /absolute/);
});

test('install refuses an APK without a matching prepare receipt even if named like an artifact', async () => {
  const h = harness();
  const forged = path.join(h.data, 'artifacts', 'android-sdam-1-forged.apk');
  writeFile(forged, 'forged');
  await assert.rejects(h.api.install('android-sdam', { serial: 'USB:42', apkPath: forged }), /no matching prepare receipt/);
  assert.ok(!h.calls.some((call) => call.tool === 'adb.exe' && call.args.includes('install')));
});

test('UEFI VM refuses artifacts without a matching prepare receipt', async () => {
  const h = harness();
  const forged = path.join(h.data, 'artifacts', 'uefi-az-kernel-forged.efi');
  writeFile(forged, 'forged');
  await assert.rejects(h.api.startVm({ artifactPath: forged }), /no matching prepare receipt/);
  assert.equal(h.calls.length, 0);
});

test('WSL readiness requires every Windows port listener to be the WSL relay', async () => {
  const foreign = readyHarness({ netstatPid: 9999 });
  await assert.rejects(foreign.h.api.runPosix({ distro: 'Ubuntu-24.04' }), /not the WSL relay/);
  assert.equal(foreign.h.api.status().service, null);
  const none = readyHarness({ netstat: '' });
  await assert.rejects(none.h.api.runPosix({ distro: 'Ubuntu-24.04' }), /cannot be proven/);
  const ok = readyHarness();
  await ok.h.api.runPosix({ distro: 'Ubuntu-24.04' });
  const netstat = ok.h.calls.find((call) => call.tool === 'netstat.exe');
  assert.equal(netstat.exe, 'C:\\Windows\\System32\\netstat.exe');
  assert.deepEqual(ok.h.calls.find((call) => call.tool === 'tasklist.exe').args, ['/fi', 'PID eq 7777', '/fo', 'csv', '/nh']);
  await ok.h.api.stopPosix();
});
