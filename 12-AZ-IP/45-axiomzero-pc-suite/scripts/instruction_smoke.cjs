const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { createInstructionModel } = require("../lib/instruction-model.cjs");

async function main() {
  const resourcesDirectory = path.resolve(process.argv[2]);
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "p45-instruction-smoke-"));
  const model = createInstructionModel({ resourcesDirectory, dataDirectory: temporary });
  try {
    const status = await model.status();
    assert.notEqual(status.productionAssistantVerified, true);
    const result = await model.answer({
      question: "Can Product 45 run Android and UEFI applications natively on Windows? Cite the supplied evidence.",
      evidence: [{
        id: "C1",
        text: "Product 45 is a Windows portfolio suite. Android applications require an Android device or emulator. UEFI components require a separate UEFI boot environment; they are not Windows programs. Do not flash firmware. Installed dependencies do not certify every product."
      }]
    });
    assert.equal(result.epistemicLabel, "UNVERIFIED");
    assert.ok(typeof result.answer === "string" && result.answer.trim());
    assert.ok(result.citations.includes("C1"), "The actual answer must cite supplied platform evidence.");
    assert.match(result.answer, /Android/i);
    assert.match(result.answer, /UEFI/i);
    console.log("Installed offline instruction model produced a cited platform-boundary answer; expert quality is not certified.");
  } finally {
    await model.stopAll();
    fs.rmSync(temporary, { recursive: true, force: true });
  }
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
