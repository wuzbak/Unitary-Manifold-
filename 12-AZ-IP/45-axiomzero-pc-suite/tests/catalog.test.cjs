const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");
const { loadProducts } = require("../lib/catalog.cjs");
const {
  resolveProductFolder,
  resolveProductReadme,
  validateCheckout
} = require("../lib/repository.cjs");
const { readSettings, writeSettings } = require("../lib/settings.cjs");
const { createExclusiveOperation } = require("../lib/operation-lock.cjs");
const fs = require("node:fs");
const os = require("node:os");

const suiteDir = path.resolve(__dirname, "..");
const repositoryRoot = path.resolve(suiteDir, "../..");

test("bundled catalog contains Products 01-45 with unique safe folder references", () => {
  const products = loadProducts(path.join(suiteDir, "catalog", "products.json"));
  assert.equal(products.length, 45);
  assert.equal(products[0].id, "01");
  assert.equal(products.at(-1).id, "45");
  assert.equal(new Set(products.map((product) => product.id)).size, products.length);
});

test("product folders stay within the selected checkout", () => {
  validateCheckout(repositoryRoot);
  const target = resolveProductFolder(repositoryRoot, "12-AZ-IP/44-axiomzero-weave/");
  assert.equal(target, path.join(repositoryRoot, "12-AZ-IP", "44-axiomzero-weave"));
  assert.equal(
    resolveProductReadme(repositoryRoot, "12-AZ-IP/44-axiomzero-weave/"),
    path.join(repositoryRoot, "12-AZ-IP", "44-axiomzero-weave", "README.md")
  );
  assert.throws(() => resolveProductFolder(repositoryRoot, "12-AZ-IP/../../etc/"));
  assert.throws(() => validateCheckout(os.tmpdir()), /not a repository checkout/);
});

test("settings are stored and restored without accepting malformed data", () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "az-suite-"));
  const file = path.join(directory, "settings.json");
  assert.deepEqual(readSettings(file), { repositoryRoot: null, knowledgeCollectionIds: [] });
  writeSettings(file, { repositoryRoot, knowledgeCollectionIds: [] });
  assert.deepEqual(readSettings(file), { repositoryRoot, knowledgeCollectionIds: [] });
  fs.writeFileSync(file, JSON.stringify({ repositoryRoot }));
  assert.deepEqual(readSettings(file), { repositoryRoot, knowledgeCollectionIds: [] });
  fs.writeFileSync(file, JSON.stringify({ repositoryRoot, knowledgeCollectionIds: ["invalid"] }));
  assert.throws(() => readSettings(file), /invalid format/);
  fs.writeFileSync(file, "{broken");
  assert.throws(() => readSettings(file), /could not be read/);
  fs.rmSync(directory, { recursive: true, force: true });
});

test("local library mutations reject overlapping work and release after failure", async () => {
  const runExclusive = createExclusiveOperation("busy");
  let release;
  const first = runExclusive(() => new Promise((resolve) => {
    release = resolve;
  }));
  await assert.rejects(runExclusive(async () => "overlap"), /busy/);
  release("finished");
  assert.equal(await first, "finished");
  await assert.rejects(runExclusive(async () => {
    throw new Error("operation failed");
  }), /operation failed/);
  assert.equal(await runExclusive(async () => "ready"), "ready");
});
