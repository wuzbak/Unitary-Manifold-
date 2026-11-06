const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

test("Windows UI smoke quotes and verifies its user-data path", () => {
  const script = fs.readFileSync(path.join(__dirname, "../scripts/windows-smoke.ps1"), "utf8");
  assert.match(script, /\$userData = Join-Path \$suiteDirectory "build\\p45 smoke-/);
  assert.match(script, /\$arguments = @\("--remote-debugging-port=\$port", \('--user-data-dir="\{0\}"' -f \$userData\)\)/);
  assert.match(script, /Test-Path -LiteralPath \$userData -PathType Container/);
});

test("Windows qualification installs the real local companion model and rejects missing or tampered parts", () => {
  const script = fs.readFileSync(path.join(__dirname, "../scripts/windows-smoke.ps1"), "utf8");
  assert.match(script, /Assert-InstallerRejected "missing"/);
  assert.match(script, /Assert-InstallerRejected "tampered"/);
  assert.match(script, /instruction_smoke\.cjs"\) \(Join-Path \$installDirectory "resources\\psicat-instruction"\)/);
  assert.doesNotMatch(script, /\$portable|win-unpacked/);
});

test("UI diagnostics retain bounded time for awaited installed-resource verification", () => {
  const script = fs.readFileSync(path.join(__dirname, "../scripts/electron-ui-smoke.cjs"), "utf8");
  assert.match(script, /params\.awaitPromise \? 60000 : 5000/);
  assert.match(script, /getNativeModel\(\)/);
  assert.match(script, /listRuntimes\(\)/);
  assert.match(script, /assert\.deepEqual\(exceptions, \[\]/);
});

test("native qualification requires consecutive fresh-process passes without retrying failures", () => {
  const workflow = fs.readFileSync(path.join(__dirname, "../../../.github/workflows/pc-suite-embedded-model.yml"), "utf8");
  assert.match(workflow, /foreach \(\$trial in 1\.\.3\) \{/);
  assert.match(workflow, /node 12-AZ-IP\/45-axiomzero-pc-suite\/scripts\/instruction_smoke\.cjs/);
  assert.match(workflow, /if \(\$LASTEXITCODE -ne 0\) \{ throw "Actual governed Node instruction runtime failed on trial \$trial\." \}/);
});
