const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { createNativeModel } = require("../lib/native-model.cjs");

const directory = fs.mkdtempSync(path.join(os.tmpdir(), "psicat-native-smoke-"));
const resources = process.argv[2];
if (!resources || !path.isAbsolute(resources)) throw new Error("Supply the installed resources directory.");
const model = createNativeModel({
  executable: path.join(resources, "PsiCatCore", process.platform === "win32" ? "PsiCatCore.exe" : "PsiCatCore"),
  seed: path.join(resources, "psicat-seed.npz"),
  userDirectory: directory
});

(async () => {
  try {
    const status = await model.status();
    assert.equal(status.kind, "own-toroidal-character-model");
    assert.equal(status.completedSteps, 500);
    assert.ok(status.parameterCount > 0);
    const result = await model.generate("PsiCat");
    assert.equal(result.status, "completed");
    assert.equal(result.completion.length, 160);
    assert.equal(result.productionAssistantVerified, false);
    const unknown = await model.generate("\u{1f9ec}\u{1f984}");
    assert.equal(unknown.status, "blocked-vocabulary");
    const corpus = path.join(directory, "corpus.txt");
    fs.writeFileSync(corpus, "PsiCat native local model. ".repeat(100));
    const trained = await model.train(corpus, 1);
    assert.equal(trained.training.completed_steps, 1);
    assert.equal((await model.status()).completedSteps, 1);
    console.log("Installed native own-model status, offline generation, vocabulary refusal and real training passed.");
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
})().catch((error) => { console.error(error); process.exitCode = 1; });
