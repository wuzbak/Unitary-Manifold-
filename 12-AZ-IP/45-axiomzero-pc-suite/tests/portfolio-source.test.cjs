const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const crypto = require("node:crypto");
const { materializePortfolioSource } = require("../lib/portfolio-source.cjs");

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
  assert.equal(fs.readFileSync(path.join(result, "12-AZ-IP/README.md"), "utf8"), "Portfolio");
  assert.equal(materializePortfolioSource(source, destination), result);
  assert.equal(fs.readFileSync(path.join(source, "12-AZ-IP/README.md"), "utf8"), "Portfolio");
});
test("source receipts fail closed on modified bytes, duplicate files and escaping paths", (t) => {
  const { source, destination, receipt, save } = fixture(t);
  fs.writeFileSync(path.join(source, "12-AZ-IP/README.md"), "modified");
  assert.throws(() => materializePortfolioSource(source, destination), /checksum/);
  fs.writeFileSync(path.join(source, "12-AZ-IP/README.md"), "Portfolio");
  receipt.files.push(receipt.files[0]); save();
  assert.throws(() => materializePortfolioSource(source, destination), /receipt/);
  receipt.files.pop(); receipt.files[0].path = "../outside"; save();
  assert.throws(() => materializePortfolioSource(source, destination), /invalid/);
  assert.equal(fs.existsSync(destination), false);
});
