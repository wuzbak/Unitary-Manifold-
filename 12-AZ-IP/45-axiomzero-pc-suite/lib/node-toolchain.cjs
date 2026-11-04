const fs = require("node:fs");
const path = require("node:path");

function resolveNodeToolchain(environment = process.env, managedDirectory) {
  const directories = [
    ...(managedDirectory ? [managedDirectory] : []),
    path.join(environment.ProgramFiles || "C:\\Program Files", "nodejs"),
    ...(environment.PATH || environment.Path || "").split(path.delimiter).filter(Boolean)
  ];
  for (const directory of directories) {
    const candidate = path.resolve(directory, "node.exe");
    if (!fs.existsSync(candidate)) continue;
    const node = fs.realpathSync(candidate);
    const npm = path.join(path.dirname(node), "node_modules", "npm", "bin", "npm-cli.js");
    if (fs.existsSync(npm) && fs.statSync(npm).isFile()) return { node, npm };
  }
  throw new Error("Node.js with npm was not found. Install Node.js LTS, restart the suite, then retry.");
}

module.exports = { resolveNodeToolchain };
