// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: AGPL-3.0-or-later
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const suiteRoot = path.resolve(__dirname, "..");
const repositoryRoot = path.resolve(suiteRoot, "../..");
const products = JSON.parse(fs.readFileSync(path.join(suiteRoot, "catalog/products.json"), "utf8"));
const runtimes = JSON.parse(fs.readFileSync(path.join(suiteRoot, "catalog/runtimes.json"), "utf8"));
const kinds = new Set(["python-service", "python-library", "static", "node", "desktop", "android", "uefi"]);
const installModes = new Set(["python-venv", "source-only", "node-npm", "android-sdk", "uefi-toolchain", "desktop"]);
const compatibleModes = {
  "python-service": new Set(["python-venv"]),
  "python-library": new Set(["python-venv", "source-only"]),
  static: new Set(["source-only"]),
  node: new Set(["node-npm"]),
  desktop: new Set(["desktop"]),
  android: new Set(["android-sdk"]),
  uefi: new Set(["uefi-toolchain"])
};

function safeRelativePath(value) {
  assert.equal(typeof value, "string");
  assert.ok(value.length > 0);
  assert.ok(!/[\u0000-\u001f\u007f\\:]/u.test(value), `Unsafe path: ${value}`);
  assert.ok(!path.posix.isAbsolute(value) && !path.win32.isAbsolute(value), `Absolute path: ${value}`);
  assert.ok(value.split("/").every((part) => part && part !== "." && part !== ".."), `Unsafe segments: ${value}`);
  const resolved = path.resolve(repositoryRoot, ...value.split("/"));
  const relative = path.relative(repositoryRoot, resolved);
  assert.ok(relative && !relative.startsWith(`..${path.sep}`) && !path.isAbsolute(relative));
  return resolved;
}

test("runtime manifest covers Products 01-45, excluding the Android-only suite", () => {
  assert.ok(Array.isArray(runtimes));
  assert.equal(runtimes.length, 45);
  const expected = Array.from({ length: 45 }, (_, index) => String(index + 1).padStart(2, "0"));
  const ids = runtimes.map((runtime) => runtime.id);
  assert.equal(new Set(ids).size, 45);
  assert.deepEqual([...ids].sort(), expected);
  assert.deepEqual(products.map((product) => product.id), [...expected, "46"]);
  assert.equal(products.at(-1).name, "AxiomZero Android Suite For Mobile Phones");
});

test("every runtime has fixed enums, prerequisites and an explicit limitation", () => {
  for (const runtime of runtimes) {
    assert.match(runtime.id, /^\d{2}$/u);
    assert.ok(kinds.has(runtime.kind), `${runtime.id}: invalid kind`);
    assert.ok(installModes.has(runtime.installMode), `${runtime.id}: invalid install mode`);
    assert.ok(compatibleModes[runtime.kind].has(runtime.installMode), `${runtime.id}: incompatible install mode`);
    assert.ok(Array.isArray(runtime.prerequisites), `${runtime.id}: prerequisites must be an array`);
    assert.ok(runtime.prerequisites.length > 0);
    assert.ok(runtime.prerequisites.every((item) => typeof item === "string" && item.trim().length > 0));
    assert.equal(typeof runtime.limitation, "string");
    assert.ok(runtime.limitation.trim().length > 0);
    assert.ok(!Object.hasOwn(runtime, "version"));
    assert.ok(!Object.hasOwn(runtime, "ready"));
    assert.ok(!Object.hasOwn(runtime, "command"), "No shell command strings");
  }
});

test("every non-null dependency manifest and entrypoint is a safe existing checkout file", () => {
  for (const runtime of runtimes) {
    const product = products.find((item) => item.id === runtime.id);
    assert.equal(runtime.productFolder, product.folder);
    const folder = safeRelativePath(runtime.productFolder.replace(/\/$/u, ""));
    assert.ok(fs.statSync(folder).isDirectory(), `${runtime.id}: product folder must exist`);
    for (const field of ["dependencyManifest", "entrypoint"]) {
      assert.ok(Object.hasOwn(runtime, field), `${runtime.id}: missing ${field}`);
      if (runtime[field] === null) continue;
      const file = safeRelativePath(runtime[field]);
      assert.ok(runtime[field].startsWith(product.folder), `${runtime.id}: ${field} outside product`);
      assert.ok(fs.statSync(file).isFile(), `${runtime.id}: ${field} must exist as a file`);
      const actual = path.relative(fs.realpathSync(repositoryRoot), fs.realpathSync(file));
      assert.ok(actual && actual !== ".." && !actual.startsWith(`..${path.sep}`) && !path.isAbsolute(actual),
        `${runtime.id}: ${field} symlink escapes checkout`);
    }
  }
});

test("root-relative path validation rejects POSIX and Windows escape forms", () => {
  for (const unsafe of [
    "", "/etc/passwd", "../outside", "12-AZ-IP/../outside", "12-AZ-IP//file",
    "./12-AZ-IP/file", "12-AZ-IP/file/", "C:/Windows/file", "C:relative",
    "\\\\server\\share\\file", "12-AZ-IP\\file", "12-AZ-IP/file:stream",
    "12-AZ-IP/\u0000file", "12-AZ-IP/\nfile"
  ]) {
    assert.throws(() => safeRelativePath(unsafe), undefined, unsafe);
  }
  assert.equal(safeRelativePath("12-AZ-IP/45-axiomzero-pc-suite/package.json"),
    path.join(suiteRoot, "package.json"));
});

test("service launches use fixed string argument arrays and implemented endpoint paths", () => {
  for (const runtime of runtimes) {
    if (runtime.kind === "python-service") {
      assert.ok(runtime.entrypoint !== null, `${runtime.id}: service requires an entrypoint`);
      assert.ok(Array.isArray(runtime.launchArgs), `${runtime.id}: service requires launchArgs`);
      assert.ok(runtime.entrypoint.endsWith("/run.py"));
    }
    if (Object.hasOwn(runtime, "launchArgs")) {
      assert.ok(Array.isArray(runtime.launchArgs));
      for (const argument of runtime.launchArgs) {
        assert.equal(typeof argument, "string");
        assert.ok(argument.length > 0 && !/[\u0000-\u001f\u007f]/u.test(argument));
      }
    }
    if (Object.hasOwn(runtime, "healthPath")) {
      assert.ok(["python-service", "node"].includes(runtime.kind));
      assert.match(runtime.healthPath, /^\/[a-zA-Z0-9/_-]+$/u);
      assert.ok(!runtime.healthPath.includes("//") && !runtime.healthPath.includes(".."));
    }
    if (Object.hasOwn(runtime, "importName")) {
      assert.equal(runtime.kind, "python-library");
      assert.match(runtime.importName, /^[a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*$/u);
      const product = products.find((item) => item.id === runtime.id);
      const packagePath = path.join(repositoryRoot, product.folder, ...runtime.importName.split("."));
      assert.ok(fs.existsSync(`${packagePath}.py`) || fs.existsSync(path.join(packagePath, "__init__.py")),
        `${runtime.id}: import package source must exist`);
    }
  }
});

test("registered non-default Python service modes match checked launcher syntax", () => {
  const expected = {
    "19": ["--no-open"],
    "20": ["--port", "8020", "--no-open"],
    "21": ["serve"],
    "23": ["--port", "8033"],
    "26": ["serve", "--host", "127.0.0.1", "--port", "8765"],
    "28": ["serve", "--port", "8128"],
    "29": ["serve", "--port", "8129"],
    "30": ["serve", "--port", "8130"],
    "31": ["serve", "--port", "8131"],
    "32": ["serve", "--port", "8132"],
    "33": ["serve", "--port", "8133"],
    "34": ["serve", "--port", "8134"],
    "35": ["serve", "--port", "8135"],
    "36": ["--serve", "--port", "8136"],
    "37": ["--serve", "--port", "8137"],
    "38": ["--serve", "--port", "8138"],
    "39": ["--serve", "--port", "8139"],
    "40": ["--serve", "--port", "8140"],
    "41": ["serve", "--port", "8141"],
    "42": ["serve", "--port", "8142"],
    "43": ["serve", "--port", "8143"],
    "44": ["serve", "--port", "8144"]
  };
  for (const [id, args] of Object.entries(expected)) {
    assert.deepEqual(runtimes.find((runtime) => runtime.id === id).launchArgs, args, id);
  }
  for (const id of ["01", "11", "13", "22"]) {
    const runtime = runtimes.find((item) => item.id === id);
    assert.notEqual(runtime.kind, "python-service", `${id}: known blocked/bootstrap command must not be registered`);
    assert.equal(runtime.entrypoint, null);
  }
  assert.match(runtimes.find((runtime) => runtime.id === "26").limitation, /fcntl.*native Windows/u);
});
