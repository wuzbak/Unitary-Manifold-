const fs = require("node:fs");
const path = require("node:path");

function readSettings(file) {
  if (!fs.existsSync(file)) {
    return { repositoryRoot: null, knowledgeCollectionIds: [] };
  }
  let parsed;
  try {
    parsed = JSON.parse(fs.readFileSync(file, "utf8"));
  } catch (error) {
    throw new Error(`Suite settings could not be read: ${error.message}`, { cause: error });
  }
  if (
    !parsed ||
    typeof parsed !== "object" ||
    (parsed.repositoryRoot !== undefined &&
      parsed.repositoryRoot !== null &&
      typeof parsed.repositoryRoot !== "string") ||
    (parsed.knowledgeCollectionIds !== undefined &&
      (!Array.isArray(parsed.knowledgeCollectionIds) ||
        parsed.knowledgeCollectionIds.length > 5 ||
        parsed.knowledgeCollectionIds.some((id) =>
          typeof id !== "string" ||
          !/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(id)
        )))
  ) {
    throw new Error("Suite settings have an invalid format.");
  }
  return {
    repositoryRoot: parsed.repositoryRoot ?? null,
    knowledgeCollectionIds: [...new Set(parsed.knowledgeCollectionIds || [])]
  };
}

function writeSettings(file, settings) {
  const directory = path.dirname(file);
  fs.mkdirSync(directory, { recursive: true });
  const temporary = `${file}.tmp`;
  fs.writeFileSync(temporary, `${JSON.stringify(settings, null, 2)}\n`, { mode: 0o600 });
  fs.renameSync(temporary, file);
}

module.exports = { readSettings, writeSettings };
