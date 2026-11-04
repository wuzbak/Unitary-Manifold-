const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { execFileSync } = require("node:child_process");
const { isPortfolioSource } = require("../lib/portfolio-source.cjs");

const root = path.resolve(__dirname, "../../..");
const destination = path.resolve(__dirname, "../build/portfolio");
fs.rmSync(destination, { recursive: true, force: true });
fs.mkdirSync(destination, { recursive: true });
const entries = execFileSync("git", ["ls-files", "--cached", "-s", "-z"], { cwd: root }).toString().split("\0").filter(Boolean);
const receipt = { schema: "axiomzero-portfolio-source-v1", head: execFileSync("git", ["rev-parse", "HEAD"], { cwd: root }).toString().trim(), files: [], excluded: [] };
const windowsPaths = new Map();
receipt.caseAliases = [];
for (const entry of entries) {
  const name = entry.slice(entry.indexOf("\t") + 1);
  if (!isPortfolioSource(name)) continue;
  const source = path.join(root, name);
  const stat = fs.lstatSync(source);
  if (entry.startsWith("120000 ") || !stat.isFile() || /(?:^|\/)(?:tests|node_modules|build|dist)(?:\/|$)/.test(name) ||
      /\.(?:zip|pdf|mp4|npz|sqlite|db)$/i.test(name) || stat.size > 8 * 1024 * 1024) {
    receipt.excluded.push(name);
    continue;
  }
  const data = fs.readFileSync(source);
  const digest = crypto.createHash("sha256").update(data).digest("hex");
  const key = name.toLowerCase();
  const prior = windowsPaths.get(key);
  if (prior) {
    if (prior.sha256 !== digest) throw new Error(`Windows source-path collision has different contents: ${prior.path} and ${name}`);
    receipt.excluded.push(name);
    receipt.caseAliases.push({ path: name, retainedPath: prior.path });
    continue;
  }
  windowsPaths.set(key, { path: name, sha256: digest });
  const target = path.join(destination, name);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, data);
  receipt.files.push({ path: name, bytes: data.length, sha256: digest });
}
fs.writeFileSync(path.join(destination, "SOURCE_RECEIPT.json"), `${JSON.stringify(receipt, null, 2)}\n`);
console.log(`Staged ${receipt.files.length} tracked portfolio/core source files; ${receipt.excluded.length} explicit exclusions.`);
