const fs = require("node:fs");
const path = require("node:path");

function validateCheckout(root) {
  if (typeof root !== "string" || root.length === 0) {
    throw new TypeError("Repository folder must be a non-empty path.");
  }
  const resolved = fs.realpathSync(path.resolve(root));
  const readme = path.join(resolved, "12-AZ-IP", "README.md");
  const registry = path.join(resolved, "12-AZ-IP", "IP_REGISTRY.json");
  if (!fs.existsSync(readme) || !fs.statSync(readme).isFile()) {
    throw new Error("Selected folder is not a repository checkout with 12-AZ-IP/README.md.");
  }
  if (!fs.existsSync(registry) || !fs.statSync(registry).isFile()) {
    throw new Error("Selected checkout is missing 12-AZ-IP/IP_REGISTRY.json.");
  }
  return resolved;
}

function resolveProductFolder(root, relativeFolder) {
  if (
    typeof relativeFolder !== "string" ||
    !relativeFolder.startsWith("12-AZ-IP/") ||
    relativeFolder.split(/[\\/]/).includes("..")
  ) {
    throw new Error("Product folder is outside the AxiomZero portfolio.");
  }
  const resolvedRoot = fs.realpathSync(path.resolve(root));
  const target = path.resolve(resolvedRoot, relativeFolder);
  const relative = path.relative(resolvedRoot, target);
  if (relative === ".." || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) {
    throw new Error("Product folder escapes the selected repository.");
  }
  return resolveRealPathInside(resolvedRoot, target);
}

function resolveProductReadme(root, relativeFolder) {
  const folder = resolveProductFolder(root, relativeFolder);
  return resolveRealPathInside(fs.realpathSync(root), path.join(folder, "README.md"));
}

function resolveRealPathInside(root, target) {
  const canonicalRoot = fs.realpathSync(root);
  const canonicalTarget = fs.realpathSync(target);
  const relative = path.relative(canonicalRoot, canonicalTarget);
  if (relative === ".." || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) {
    throw new Error("Selected portfolio path resolves outside the repository.");
  }
  return canonicalTarget;
}

module.exports = { validateCheckout, resolveProductFolder, resolveProductReadme };
