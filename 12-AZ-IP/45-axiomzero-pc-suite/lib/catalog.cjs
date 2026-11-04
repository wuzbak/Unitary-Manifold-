const fs = require("node:fs");

function loadProducts(file) {
  const rows = JSON.parse(fs.readFileSync(file, "utf8"));
  if (!Array.isArray(rows) || rows.length < 1) {
    throw new Error("The bundled product catalog is empty or invalid.");
  }
  const ids = new Set();
  for (const product of rows) {
    if (
      !product ||
      typeof product.id !== "string" ||
      !/^\d{2}$/.test(product.id) ||
      typeof product.name !== "string" ||
      typeof product.folder !== "string" ||
      !product.folder.startsWith("12-AZ-IP/") ||
      product.folder.split(/[\\/]/).includes("..") ||
      typeof product.description !== "string" ||
      typeof product.endpoint !== "string"
    ) {
      throw new Error("The bundled product catalog contains an invalid entry.");
    }
    if (ids.has(product.id)) {
      throw new Error(`The bundled product catalog repeats product ${product.id}.`);
    }
    ids.add(product.id);
  }
  return rows;
}

module.exports = { loadProducts };
