const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

test("Windows UI smoke quotes and verifies its user-data path", () => {
  const script = fs.readFileSync(path.join(__dirname, "../scripts/windows-smoke.ps1"), "utf8");
  assert.match(script, /\$userData = Join-Path \$env:TEMP "p45 smoke-/);
  assert.match(script, /\$arguments = @\("--remote-debugging-port=\$port", \('--user-data-dir="\{0\}"' -f \$userData\)\)/);
  assert.match(script, /Test-Path -LiteralPath \$userData -PathType Container/);
});
