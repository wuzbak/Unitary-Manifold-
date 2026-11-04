const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");
const { resolveNodeToolchain } = require("../lib/node-toolchain.cjs");

test("Windows Node resolution invokes npm through its JavaScript CLI, never a cmd shim", (t) => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "p45-node-"));
  t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
  assert.throws(() => resolveNodeToolchain({ ProgramFiles: directory, PATH: directory }), /not found/);
  fs.writeFileSync(path.join(directory, "node.exe"), "");
  assert.throws(() => resolveNodeToolchain({ ProgramFiles: directory, PATH: directory }), /not found/);
  const npm = path.join(directory, "node_modules/npm/bin/npm-cli.js");
  fs.mkdirSync(path.dirname(npm), { recursive: true }); fs.writeFileSync(npm, "");
  const tools = resolveNodeToolchain({ ProgramFiles: directory, PATH: directory });
  assert.equal(tools.node, fs.realpathSync(path.join(directory, "node.exe")));
  assert.equal(tools.npm, npm);
});
