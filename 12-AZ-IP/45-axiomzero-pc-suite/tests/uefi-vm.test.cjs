// SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
// Copyright (C) 2026  ThomasCory Walker-Pearson
'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const crypto = require('node:crypto');
const { spawn } = require('node:child_process');
const { isKernelScreen, startUefiVm } = require('../lib/uefi-vm.cjs');
const { createPlatformTargets } = require('../lib/platform-targets.cjs');

function frame(font) {
  const width = 256, height = 272;
  const header = Buffer.from(`P6\n${width} ${height}\n255\n`);
  const pixels = Buffer.alloc(width * height * 3);
  for (let i = 0; i < width * height; i++) Buffer.from([8, 8, 16]).copy(pixels, i * 3);
  for (const [i, ch] of [...'Hello from AxiomZero.'].entries()) {
    for (let y = 0; y < 16; y++) for (let x = 0; x < 8; x++) {
      if (font[(ch.charCodeAt(0) - 32) * 16 + y] & (0x80 >> x)) {
        Buffer.from([240, 240, 255]).copy(pixels, ((256 + y) * width + 16 + i * 8 + x) * 3);
      }
    }
  }
  return Buffer.concat([header, pixels]);
}

test('kernel boot requires the exact rendered banner, not just a live VM or background color', () => {
  const font = fs.readFileSync(path.join(__dirname, '../../02-az-kernel/assets/font8x16.bin'));
  const image = frame(font);
  assert.equal(isKernelScreen(image, font), true);
  image[image.length - 1] = 0;
  assert.equal(isKernelScreen(image.subarray(0, -1), font), false);
  const header = image.indexOf('\n255\n') + 5;
  image[header + ((256 * 256 + 16) * 3)] ^= 255;
  assert.equal(isKernelScreen(image, font), false);
  assert.equal(isKernelScreen(Buffer.from('not a framebuffer'), font), false);
});

test('UEFI image hash is rechecked after copying and before launching QEMU', async (t) => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'p45-uefi-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  const qemu = path.join(dir, 'qemu-system-x86_64'), code = path.join(dir, 'code'), vars = path.join(dir, 'vars');
  const artifact = path.join(dir, 'artifact'), font = path.join(dir, 'font');
  for (const file of [qemu, code, vars, artifact, font]) fs.writeFileSync(file, 'fixture');
  let spawned = false;
  await assert.rejects(startUefiVm({
    qemu, code, vars, artifact, artifactHash: '0'.repeat(64), font, dataDirectory: dir,
    spawn: () => { spawned = true; }, terminate: async () => {}, register: () => {}, unregister: () => {},
    isQuitting: () => false, timeoutMs: 1000,
  }), /artifact changed/);
  assert.equal(spawned, false);
  assert.equal(fs.readdirSync(dir).some((name) => name.startsWith('preview-')), false);
});

test('real QEMU boots the prepared kernel and stops its isolated VM', {
  skip: !process.env.P45_UEFI_QEMU, timeout: 120000,
}, async (t) => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'p45-real-uefi-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  const artifact = process.env.P45_UEFI_EFI;
  const contents = fs.readFileSync(artifact);
  const digest = crypto.createHash('sha256').update(contents).digest('hex');
  const bundle = path.join(dir, 'bundle');
  fs.mkdirSync(bundle);
  fs.writeFileSync(path.join(bundle, 'uefi-az-kernel.efi'), contents);
  fs.writeFileSync(path.join(bundle, 'manifest.json'), JSON.stringify({
    formatVersion: 1, assets: [{ target: 'uefi-az-kernel', file: 'uefi-az-kernel.efi', sha256: digest, sizeBytes: contents.length }],
  }));
  const manager = createPlatformTargets({
    repositoryRoot: path.resolve(__dirname, '../../..'), dataRoot: path.join(dir, 'data'),
    bundledDirectory: bundle, platform: 'linux', env: process.env, spawn, vmDisplay: 'none', startupTimeoutMs: 90000,
  });
  const inputCode = fs.readFileSync(process.env.P45_UEFI_CODE);
  const inputVars = fs.readFileSync(process.env.P45_UEFI_VARS);
  const prepared = await manager.importBundled('uefi-az-kernel');
  const result = await manager.startVm({
    qemu: process.env.P45_UEFI_QEMU, code: process.env.P45_UEFI_CODE, vars: process.env.P45_UEFI_VARS,
    artifactPath: prepared.artifactPath,
  });
  assert.equal(result.status, 'boot-banner-observed');
  await assert.rejects(manager.startVm({ artifactPath: prepared.artifactPath }), /already running/);
  assert.equal((await manager.stopVm()).status, 'stopped');
  await manager.close();
  assert.deepEqual(fs.readFileSync(process.env.P45_UEFI_CODE), inputCode);
  assert.deepEqual(fs.readFileSync(process.env.P45_UEFI_VARS), inputVars);
  assert.deepEqual(fs.readdirSync(path.join(dir, 'data', 'uefi-vm')), []);

  const invalid = Buffer.from('not an EFI application');
  fs.writeFileSync(path.join(bundle, 'uefi-az-kernel.efi'), invalid);
  fs.writeFileSync(path.join(bundle, 'manifest.json'), JSON.stringify({
    formatVersion: 1, assets: [{ target: 'uefi-az-kernel', file: 'uefi-az-kernel.efi',
      sha256: crypto.createHash('sha256').update(invalid).digest('hex'), sizeBytes: invalid.length }],
  }));
  const failed = createPlatformTargets({
    repositoryRoot: path.resolve(__dirname, '../../..'), dataRoot: path.join(dir, 'failed'),
    bundledDirectory: bundle, platform: 'linux', env: process.env, spawn, vmDisplay: 'none', startupTimeoutMs: 5000,
  });
  const bad = await failed.importBundled('uefi-az-kernel');
  await assert.rejects(failed.startVm({
    qemu: process.env.P45_UEFI_QEMU, code: process.env.P45_UEFI_CODE, vars: process.env.P45_UEFI_VARS,
    artifactPath: bad.artifactPath,
  }), /boot banner was not observed/);
  await failed.close();
  assert.deepEqual(fs.readdirSync(path.join(dir, 'failed', 'uefi-vm')), []);
});
