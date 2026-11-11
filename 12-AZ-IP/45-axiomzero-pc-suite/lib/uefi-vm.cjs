// SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
// Copyright (C) 2026  ThomasCory Walker-Pearson
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const readline = require('node:readline');
const crypto = require('node:crypto');

const BANNER = 'Hello from AxiomZero.';
const MAX_SCREEN_BYTES = 64 * 1024 * 1024;
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function isKernelScreen(bytes, font) {
  const header = /^P6\s+(\d+)\s+(\d+)\s+255\s/.exec(bytes.subarray(0, 100).toString('ascii'));
  if (!header || font.length < 95 * 16) return false;
  const width = Number(header[1]), height = Number(header[2]), offset = header[0].length;
  if (width < 16 + BANNER.length * 8 || height < 272 ||
      width > 4096 || height > 4096 || bytes.length !== offset + width * height * 3) return false;
  const same = (at, rgb) => bytes[at] === rgb[0] && bytes[at + 1] === rgb[1] && bytes[at + 2] === rgb[2];
  for (let i = 0; i < BANNER.length; i++) {
    for (let y = 0; y < 16; y++) {
      const bits = font[(BANNER.charCodeAt(i) - 32) * 16 + y];
      for (let x = 0; x < 8; x++) {
        const index = offset + ((256 + y) * width + 16 + i * 8 + x) * 3;
        const foreground = (bits & (0x80 >> x)) !== 0;
        const a = foreground ? [240, 240, 255] : [8, 8, 16];
        const b = foreground ? [255, 240, 240] : [16, 8, 8];
        if (!same(index, a) && !same(index, b)) return false;
      }
    }
  }
  return true;
}

function qmpConnection(child) {
  let sequence = 0;
  const waiting = new Map();
  let greetResolve, greetReject;
  const greeting = new Promise((resolve, reject) => { greetResolve = resolve; greetReject = reject; });
  let greeted = false, failure = null;
  const fail = (error) => {
    if (failure) return;
    failure = error;
    if (!greeted) greetReject(error);
    for (const { reject } of waiting.values()) reject(error);
    waiting.clear();
  };
  child.once('error', fail);
  child.stdin.on('error', fail);
  child.once('close', (code) => fail(new Error(`QEMU exited (${code}) before VM shutdown.`)));
  readline.createInterface({ input: child.stdout }).on('line', (line) => {
    let message;
    try { message = JSON.parse(line); } catch { fail(new Error('QEMU returned invalid monitor data.')); return; }
    if (message.QMP && !greeted) { greeted = true; greetResolve(); return; }
    if (!waiting.has(message.id)) return;
    const item = waiting.get(message.id);
    waiting.delete(message.id);
    if (message.error) item.reject(new Error(`QEMU monitor: ${message.error.desc || 'command failed'}`));
    else item.resolve(message.return);
  });
  const bounded = async (promise) => {
    let timer;
    try {
      return await Promise.race([promise, new Promise((_, reject) => {
        timer = setTimeout(() => reject(new Error('QEMU monitor did not respond within 10 seconds.')), 10000);
      })]);
    } finally { clearTimeout(timer); }
  };
  return {
    greeting: () => bounded(greeting),
    command: (execute, args) => bounded(new Promise((resolve, reject) => {
      if (failure) { reject(failure); return; }
      const id = ++sequence;
      waiting.set(id, { resolve, reject });
      child.stdin.write(`${JSON.stringify({ execute, arguments: args || {}, id })}\n`, (error) => {
        if (error && waiting.delete(id)) reject(error);
      });
    })),
  };
}

function regularFile(file, maxBytes) {
  if (typeof file !== 'string' || !path.isAbsolute(file)) throw new Error('Choose an absolute local file.');
  const stat = fs.lstatSync(file);
  if (!stat.isFile() || stat.isSymbolicLink() || stat.size < 1 || stat.size > maxBytes) {
    throw new Error('Selected file must be a regular, non-symlink file within its size limit.');
  }
  return fs.realpathSync(file);
}

async function startUefiVm({ qemu, code, vars, artifact, artifactHash, font, dataDirectory, spawn, terminate,
  register, unregister, isQuitting, env, timeoutMs, display = 'default' }) {
  const executable = regularFile(qemu, 1024 * 1024 * 1024);
  if (!/^qemu-system-x86_64(?:\.exe)?$/i.test(path.basename(executable))) throw new Error('Select qemu-system-x86_64.');
  const codeFile = regularFile(code, 16 * 1024 * 1024);
  const varsFile = regularFile(vars, 16 * 1024 * 1024);
  const fontData = fs.readFileSync(font);
  const vmDir = fs.mkdtempSync(path.join(dataDirectory, 'preview-'));
  const disk = path.join(vmDir, 'disk');
  let child;
  try {
    fs.mkdirSync(path.join(disk, 'EFI', 'BOOT'), { recursive: true });
    const bootFile = path.join(disk, 'EFI', 'BOOT', 'BOOTX64.EFI');
    fs.copyFileSync(artifact, bootFile, fs.constants.COPYFILE_EXCL);
    if (crypto.createHash('sha256').update(fs.readFileSync(bootFile)).digest('hex') !== artifactHash) {
      throw new Error('The UEFI artifact changed while preparing the VM.');
    }
    fs.writeFileSync(path.join(disk, 'startup.nsh'), 'fs0:\\EFI\\BOOT\\BOOTX64.EFI\r\n', { flag: 'wx' });
    fs.copyFileSync(codeFile, path.join(vmDir, 'code.fd'), fs.constants.COPYFILE_EXCL);
    fs.copyFileSync(varsFile, path.join(vmDir, 'vars.fd'), fs.constants.COPYFILE_EXCL);
    const escaped = (value) => value.replace(/,/g, ',,');
    const screen = path.join(vmDir, 'screen.ppm');
    child = spawn(executable, [
      '-machine', 'q35,accel=tcg', '-m', '256', '-smp', '2',
      '-drive', `if=pflash,format=raw,readonly=on,file=${escaped(path.join(vmDir, 'code.fd'))}`,
      '-drive', `if=pflash,format=raw,file=${escaped(path.join(vmDir, 'vars.fd'))}`,
      '-drive', `format=raw,file=fat:rw:${escaped(disk)}`,
      '-display', display, '-qmp', 'stdio', '-monitor', 'none', '-serial', 'none',
      '-net', 'none', '-no-reboot',
    ], { cwd: vmDir, env, shell: false, windowsHide: false, stdio: ['pipe', 'pipe', 'pipe'] });
    register(child);
    let diagnostics = '';
    child.stderr.on('data', (chunk) => { diagnostics = (diagnostics + chunk.toString()).slice(-8192); });
    const exit = new Promise((resolve) => child.once('close', resolve));
    exit.then(() => {
      unregister(child);
      try { fs.rmSync(vmDir, { recursive: true, force: true }); }
      catch (error) { console.error(`UEFI VM cleanup failed for ${vmDir}: ${error.message}`); }
    });
    const qmp = qmpConnection(child);
    try {
      await qmp.greeting();
      await qmp.command('qmp_capabilities');
      const deadline = Date.now() + timeoutMs;
      while (Date.now() < deadline) {
        if (isQuitting()) throw new Error('The suite is shutting down.');
        const status = await qmp.command('query-status');
        if (!status || !status.running) throw new Error(`QEMU is not running: ${status?.status || 'unknown'}.`);
        await qmp.command('screendump', { filename: screen });
        const stat = fs.statSync(screen);
        if (stat.size > MAX_SCREEN_BYTES) throw new Error('VM framebuffer exceeds the size limit.');
        if (isKernelScreen(fs.readFileSync(screen), fontData)) {
          return {
            pid: child.pid, exited: exit, get closed() { return child.exitCode !== null || child.signalCode !== null; },
            stop: async () => { await terminate(child); await exit; },
          };
        }
        await sleep(1000);
      }
      throw new Error(`Kernel boot banner was not observed within ${timeoutMs} ms.`);
    } catch (error) {
      if (diagnostics) error.message += ` QEMU: ${diagnostics}`;
      await terminate(child);
      await exit;
      throw error;
    }
  } catch (error) {
    if (!child) fs.rmSync(vmDir, { recursive: true, force: true });
    throw error;
  }
}

module.exports = { isKernelScreen, startUefiVm };
