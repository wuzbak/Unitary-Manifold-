const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const crypto = require("node:crypto");
const { installNodeLts } = require("../lib/node-bootstrap.cjs");

function fixture(t, { corrupt = false, httpFailure = false, missingFiles = false } = {}) {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "p45-node-bootstrap-"));
  t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
  const archive = Buffer.from("official archive fixture");
  const digest = crypto.createHash("sha256").update(archive).digest("hex");
  const urls = [];
  const calls = [];
  const options = {
    directory, extractionScript: path.join(directory, "extract.ps1"), platform: "win32", architecture: "x64",
    fetchResource: async (url, request) => {
      urls.push(url);
      assert.equal(request.redirect, "error");
      assert.ok(request.signal);
      return {
        ok: !httpFailure, status: httpFailure ? 503 : 200,
        body: (async function* () {
          yield url.endsWith(".txt")
            ? Buffer.from(`${digest}  node-v24.22.2-win-x64.zip\n`)
            : corrupt ? Buffer.from("modified archive") : archive;
        })()
      };
    },
    execute: async (executable, args) => {
      calls.push({ executable, args });
      if (executable === "powershell.exe" && !missingFiles) {
        const extracted = args[args.indexOf("-Destination") + 1];
        const target = path.join(extracted, "node-v24.22.2-win-x64");
        fs.mkdirSync(path.join(target, "node_modules/npm/bin"), { recursive: true });
        for (const file of ["node.exe", "node_modules/npm/bin/npm-cli.js", "LICENSE"]) fs.writeFileSync(path.join(target, file), "");
      }
    }
  };
  return { options, directory, urls, calls };
}

test("private Node installation is fixed-origin, checksum-verified, user-scoped and includes licenses", async (t) => {
  const { options, directory, urls, calls } = fixture(t);
  const receipt = await installNodeLts(options);
  assert.equal(receipt.version, "v24.22.2");
  assert.deepEqual(urls, [
    "https://nodejs.org/dist/latest-v24.x/SHASUMS256.txt",
    "https://nodejs.org/dist/v24.22.2/node-v24.22.2-win-x64.zip"
  ]);
  assert.equal(calls[0].executable, "powershell.exe");
  assert.ok(calls[0].args.includes("-File"));
  assert.equal(calls[0].args.includes("-Command"), false);
  assert.deepEqual(calls[1].args, ["--version"]);
  assert.ok(fs.existsSync(path.join(directory, "node-lts/LICENSE")));
  assert.deepEqual(fs.readdirSync(directory), ["node-lts"]);
  await assert.rejects(installNodeLts(options), /already installed/);
});
test("corrupt, unavailable and incomplete Node downloads never become successful installations", async (t) => {
  for (const variant of [{ corrupt: true }, { httpFailure: true }, { missingFiles: true }]) {
    const { options, directory } = fixture(t, variant);
    await assert.rejects(installNodeLts(options), /checksum|HTTP|missing/);
    assert.deepEqual(fs.readdirSync(directory), []);
  }
});
test("Node bootstrap rejects unsupported targets before download", async (t) => {
  const { options, urls } = fixture(t);
  await assert.rejects(installNodeLts({ ...options, architecture: "arm64" }), /Windows x64/);
  assert.equal(urls.length, 0);
});
