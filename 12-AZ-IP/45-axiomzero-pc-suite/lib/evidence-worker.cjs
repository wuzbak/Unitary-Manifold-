const { parentPort, workerData } = require("node:worker_threads");
const { loadCollection, searchCollections } = require("./knowledge.cjs");
const { evidenceReport } = require("./harness.cjs");

const collections = workerData.ids.map((id) => loadCollection(workerData.directory, id));
parentPort.postMessage(evidenceReport(searchCollections(collections, workerData.goal, 4), collections));
