const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { execFileSync } = require("node:child_process");

const root = path.resolve(__dirname, "../../..");
const destination = path.resolve(__dirname, "../build/portfolio");
fs.rmSync(destination, { recursive: true, force: true });
fs.mkdirSync(destination, { recursive: true });
const paths = execFileSync("git", ["ls-files", "--cached", "-z"], { cwd: root }).toString().split("\0").filter(Boolean);
const receipt = { schema: "axiomzero-portfolio-source-v1", head: execFileSync("git", ["rev-parse", "HEAD"], { cwd: root }).toString().trim(), files: [], excluded: [] };
const prefixes = ["12-AZ-IP/", "src/", "claims/", "recycling/", "5-GOVERNANCE/Unitary Pentad/"];
for (const name of paths) {
  if (!prefixes.some((prefix) => name.startsWith(prefix)) && !["requirements.txt", "README.md", "FALLIBILITY.md"].includes(name)) continue;
  const source = path.join(root, name);
  const stat = fs.lstatSync(source);
  if (!stat.isFile() || /(?:^|\/)(?:tests|node_modules|build|dist)(?:\/|$)/.test(name) ||
      /\.(?:zip|pdf|mp4|npz|sqlite|db)$/i.test(name) || stat.size > 8 * 1024 * 1024) {
    receipt.excluded.push(name);
    continue;
  }
  const data = fs.readFileSync(source);
  const target = path.join(destination, name);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, data);
  receipt.files.push({ path: name, bytes: data.length, sha256: crypto.createHash("sha256").update(data).digest("hex") });
}
fs.writeFileSync(path.join(destination, "SOURCE_RECEIPT.json"), `${JSON.stringify(receipt, null, 2)}\n`);
console.log(`Staged ${receipt.files.length} tracked portfolio/core source files; ${receipt.excluded.length} explicit exclusions.`);
