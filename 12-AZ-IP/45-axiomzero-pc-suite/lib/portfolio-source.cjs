const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { inside } = require("./runtime-manager.cjs");
const { validateCheckout } = require("./repository.cjs");

function materializePortfolioSource(source, directory) {
  const bytes = fs.readFileSync(path.join(source, "SOURCE_RECEIPT.json"));
  const receipt = JSON.parse(bytes);
  if (receipt.schema !== "axiomzero-portfolio-source-v1" || !/^[0-9a-f]{40}$/.test(receipt.head) ||
      !Array.isArray(receipt.files) || receipt.files.length < 1 || !Array.isArray(receipt.excluded)) {
    throw new Error("Bundled portfolio source receipt is invalid.");
  }
  const identity = crypto.createHash("sha256").update(bytes).digest("hex");
  const destination = path.join(directory, `${receipt.head}-${identity}`);
  if (fs.existsSync(destination)) return validateCheckout(destination);
  const seen = new Set();
  for (const file of receipt.files) {
    if (seen.has(file.path) || !Number.isSafeInteger(file.bytes) || file.bytes < 0 || !/^[0-9a-f]{64}$/.test(file.sha256)) {
      throw new Error("Bundled portfolio file receipt is invalid.");
    }
    seen.add(file.path);
    const content = fs.readFileSync(inside(source, file.path));
    if (content.length !== file.bytes || crypto.createHash("sha256").update(content).digest("hex") !== file.sha256) {
      throw new Error(`Bundled portfolio checksum failed: ${file.path}`);
    }
  }
  fs.mkdirSync(directory, { recursive: true });
  const pending = `${destination}.pending`;
  fs.mkdirSync(pending);
  try {
    for (const file of receipt.files) {
      const target = path.join(pending, file.path);
      fs.mkdirSync(path.dirname(target), { recursive: true });
      fs.copyFileSync(inside(source, file.path), target, fs.constants.COPYFILE_EXCL);
    }
    fs.writeFileSync(path.join(pending, "SOURCE_RECEIPT.json"), bytes, { flag: "wx" });
    validateCheckout(pending);
    fs.renameSync(pending, destination);
  } catch (error) {
    fs.rmSync(pending, { recursive: true, force: true });
    throw error;
  }
  return destination;
}

module.exports = { materializePortfolioSource };
