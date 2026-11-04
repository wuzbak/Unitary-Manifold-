const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { EventEmitter } = require("node:events");
const { PassThrough } = require("node:stream");
const { createNativeModel } = require("../lib/native-model.cjs");

function fixture(t, responder) {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "psicat-native-test-"));
  t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
  const seed = path.join(directory, "seed.npz");
  fs.writeFileSync(seed, "test");
  let child;
  const runtime = createNativeModel({
    executable: path.join(directory, "PsiCatCore.exe"), seed, userDirectory: directory,
    spawnProcess(executable, args, options) {
      assert.equal(options.shell, false);
      assert.equal(options.windowsHide, true);
      child = new EventEmitter();
      child.stdin = new PassThrough();
      child.stdout = new PassThrough();
      child.stderr = new PassThrough();
      child.kill = () => { setImmediate(() => child.emit("close", null)); return true; };
      const input = [];
      child.stdin.on("data", (data) => input.push(data));
      child.stdin.on("finish", () => responder(child, JSON.parse(Buffer.concat(input).toString())));
      return child;
    }
  });
  return { runtime, directory };
}
const response = { status: "ready", epistemicLabel: "UNVERIFIED", productionAssistantVerified: false };
function finish(child, result, code = 0) {
  setImmediate(() => { child.stdout.write(JSON.stringify(result)); child.emit("close", code); });
}

test("native protocol uses the seed and refuses invalid prompts without spawning shell", async (t) => {
  const { runtime } = fixture(t, (child, request) => {
    assert.match(request.checkpoint, /seed.npz$/);
    finish(child, response);
  });
  assert.equal((await runtime.status()).status, "ready");
  assert.throws(() => runtime.generate("x".repeat(401)), /Prompt/);
  assert.throws(() => runtime.cancel(), /No native/);
});
test("native failures, bad JSON and promoted model claims fail explicitly", async (t) => {
  const { runtime } = fixture(t, (child) => finish(child, { ...response, productionAssistantVerified: true }));
  await assert.rejects(runtime.status(), /violates/);
  const failed = fixture(t, (child) => finish(child, { status: "failed", error: "bad checkpoint" }, 1));
  await assert.rejects(failed.runtime.status(), /bad checkpoint/);
  const invalid = fixture(t, (child) => { child.stdout.write("not-json"); setImmediate(() => child.emit("close", 0)); });
  await assert.rejects(invalid.runtime.status(), /valid response/);
  for (const value of [null, [], 17, "ready"]) {
    const malformed = fixture(t, (child) => finish(child, value));
    await assert.rejects(malformed.runtime.status(), /valid response object/);
  }
});
test("native cancellation prevents late success and keeps the prior checkpoint", async (t) => {
  const { runtime } = fixture(t, () => {});
  const work = runtime.status();
  assert.equal(runtime.isActive(), true);
  await assert.rejects(runtime.status(), /busy/);
  runtime.cancel();
  await assert.rejects(work, /cancelled/);
  assert.equal(runtime.isActive(), false);
});
test("native oversized output is rejected", async (t) => {
  const { runtime } = fixture(t, (child) => child.stdout.write("x".repeat(65537)));
  await assert.rejects(runtime.status(), /64 KiB/);
});
test("native replies must match the requested action", async (t) => {
  const { runtime } = fixture(t, (child) => finish(child, response));
  await assert.rejects(runtime.generate("Hello"), /requested action/);
});
test("successful training promotes a real pending file and switches future inference", async (t) => {
  const { runtime, directory } = fixture(t, (child, request) => {
    if (request.action === "train") {
      fs.writeFileSync(request.checkpoint, "trained checkpoint");
      finish(child, { ...response, status: "completed", training: {} });
    } else {
      assert.match(request.checkpoint, /psicat-trained.npz$/);
      finish(child, response);
    }
  });
  await runtime.train(path.join(directory, "corpus.txt"), 1);
  assert.equal(fs.readFileSync(path.join(directory, "psicat-trained.npz"), "utf8"), "trained checkpoint");
  await runtime.status();
});
