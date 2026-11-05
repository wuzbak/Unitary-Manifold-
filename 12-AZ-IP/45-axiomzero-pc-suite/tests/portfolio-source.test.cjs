const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const crypto = require("node:crypto");
const { materializePortfolioSource, isPortfolioSource } = require("../lib/portfolio-source.cjs");

test("source packaging includes Navigator's exact bot import dependencies without unrelated bot data", () => {
  for (const name of ["__init__.py", "assistant_api.py", "rag_index.py", "session_bootstrap.py", "research_resources.py"]) {
    assert.equal(isPortfolioSource(`bot/${name}`), true, name);
  }
  for (const name of ["bot/private-export.json", "bot/.env", "bot/tests/test_api.py", ".env"]) {
    assert.equal(isPortfolioSource(name), false, name);
  }
  assert.equal(isPortfolioSource("src/infrastructure/execution_spine.py"), true);
});

function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "p45-source-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const source = path.join(root, "bundled");
  fs.mkdirSync(path.join(source, "12-AZ-IP"), { recursive: true });
  const receipt = { schema: "axiomzero-portfolio-source-v1", head: "a".repeat(40), excluded: [], files: [] };
  for (const [name, text] of [["12-AZ-IP/README.md", "Portfolio"], ["12-AZ-IP/IP_REGISTRY.json", "{}"]]) {
    fs.writeFileSync(path.join(source, name), text);
    receipt.files.push({ path: name, bytes: Buffer.byteLength(text), sha256: crypto.createHash("sha256").update(text).digest("hex") });
  }
  const save = () => fs.writeFileSync(path.join(source, "SOURCE_RECEIPT.json"), JSON.stringify(receipt));
  save();
  return { source, destination: path.join(root, "user"), receipt, save };
}
test("bundled source is checksum-verified and copied into a stable content-scoped user worktree", (t) => {
  const { source, destination } = fixture(t);
  const result = materializePortfolioSource(source, destination);
  assert.notEqual(result, source);
  const identity = crypto.createHash("sha256").update(fs.readFileSync(path.join(source, "SOURCE_RECEIPT.json"))).digest("hex");
  assert.equal(path.basename(result), identity);
  const windowsDirectory = "C:\\Users\\runneradmin\\AppData\\Local\\Temp\\p45-portfolio-smoke-123456\\source";
  const runtimeResource = "12-AZ-IP\\24-psicat-web-browser\\node_modules\\electron\\dist\\resources\\default_app.asar";
  assert.ok(path.win32.join(windowsDirectory, identity, runtimeResource).length < 260);
  assert.ok(path.win32.join(windowsDirectory, `${"a".repeat(40)}-${identity}`, runtimeResource).length >= 260);
  assert.equal(fs.readFileSync(path.join(result, "12-AZ-IP/README.md"), "utf8"), "Portfolio");
  assert.equal(materializePortfolioSource(source, destination), result);
  assert.equal(fs.readFileSync(path.join(source, "12-AZ-IP/README.md"), "utf8"), "Portfolio");
});
test("retries use a fresh staging directory when a prior fixed-name stage was abandoned", (t) => {
  const { source, destination } = fixture(t);
  const identity = crypto.createHash("sha256").update(fs.readFileSync(path.join(source, "SOURCE_RECEIPT.json"))).digest("hex");
  const abandoned = path.join(destination, `${identity}.pending`);
  fs.mkdirSync(abandoned, { recursive: true });
  fs.writeFileSync(path.join(abandoned, "interrupted-copy"), "preserve");
  const abandonedUnique = path.join(destination, ".p45-abandoned");
  fs.mkdirSync(abandonedUnique);
  fs.writeFileSync(path.join(abandonedUnique, "interrupted-copy"), "preserve");

  const result = materializePortfolioSource(source, destination);

  assert.equal(fs.readFileSync(path.join(result, "12-AZ-IP/README.md"), "utf8"), "Portfolio");
  assert.equal(fs.readFileSync(path.join(abandoned, "interrupted-copy"), "utf8"), "preserve");
  assert.equal(fs.readFileSync(path.join(abandonedUnique, "interrupted-copy"), "utf8"), "preserve");
  assert.deepEqual(fs.readdirSync(destination).filter((name) => name.startsWith(".p45-")),
    [".p45-abandoned"]);
});
test("reused source worktrees fail closed when a receipted file was modified", (t) => {
  const { source, destination } = fixture(t);
  const result = materializePortfolioSource(source, destination);
  fs.writeFileSync(path.join(result, "12-AZ-IP/README.md"), "changed");
  assert.throws(() => materializePortfolioSource(source, destination), /checksum failed/);
});
test("source receipts fail closed on modified bytes, duplicate files and escaping paths", (t) => {
  const { source, destination, receipt, save } = fixture(t);
  fs.writeFileSync(path.join(source, "12-AZ-IP/README.md"), "modified");
  assert.throws(() => materializePortfolioSource(source, destination), /checksum/);
  fs.writeFileSync(path.join(source, "12-AZ-IP/README.md"), "Portfolio");
  receipt.files.push(receipt.files[0]); save();
  assert.throws(() => materializePortfolioSource(source, destination), /receipt/);
  receipt.files.pop();
  receipt.files.push({ ...receipt.files[0], path: receipt.files[0].path.toLowerCase() }); save();
  assert.throws(() => materializePortfolioSource(source, destination), /receipt/);
  receipt.files.pop(); receipt.files[0].path = "../outside"; save();
  assert.throws(() => materializePortfolioSource(source, destination), /invalid/);
  assert.equal(fs.existsSync(destination), false);
});
