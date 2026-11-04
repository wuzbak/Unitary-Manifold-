const os = require("node:os");
const fs = require("node:fs/promises");

const GIB = 1024 ** 3;
const DETECTION_TIMEOUT_MS = 15000;

function assessHardware({ totalMemoryBytes, availableMemoryBytes, freeDiskBytes, architecture }) {
  for (const [label, value] of Object.entries({ totalMemoryBytes, availableMemoryBytes, freeDiskBytes })) {
    if (!Number.isSafeInteger(value) || value < 0) throw new Error(`Hardware ${label} measurement is invalid.`);
  }
  if (availableMemoryBytes > totalMemoryBytes || totalMemoryBytes === 0) {
    throw new Error("Hardware memory measurements are inconsistent.");
  }
  if (!["x64", "arm64", "ia32"].includes(architecture)) {
    throw new Error("This hardware architecture is not supported by the assessment.");
  }
  const blockers = [];
  if (architecture !== "x64") blockers.push("The current Windows installer targets x64 only.");
  if (totalMemoryBytes < 8 * GIB) blockers.push("Less than 8 GiB total RAM: defer model installation pending a measured small-model trial.");
  if (availableMemoryBytes < 4 * GIB) blockers.push("Less than 4 GiB RAM currently available: close applications before model evaluation.");
  if (freeDiskBytes < 10 * GIB) blockers.push("Less than 10 GiB free on the application-data volume: free space before staging model files.");
  return {
    status: blockers.length ? "blocked-for-model-evaluation" : "ready-for-model-evaluation",
    blockers,
    modelSelected: false,
    trainingReady: false,
    explanation: "These are conservative screening thresholds, not a model-fit or performance guarantee. Select exact licensed weights only after measuring their memory, context, disk and latency requirements. GPU compute capability and dedicated VRAM remain unverified; do not start fine-tuning from this report."
  };
}

function describeGpu(info) {
  if (!info || !Array.isArray(info.gpuDevice)) throw new Error("GPU diagnostics did not return a device list.");
  if (info.gpuDevice.length > 16) throw new Error("GPU diagnostics returned too many devices.");
  return info.gpuDevice.map((device) => {
    if (!device || typeof device !== "object") throw new Error("GPU diagnostic device is invalid.");
    const text = (value) => typeof value === "string" ? value.slice(0, 200) : null;
    const identifier = (value) => Number.isSafeInteger(value) && value >= 0 ? value : null;
    return {
      vendorId: identifier(device.vendorId),
      deviceId: identifier(device.deviceId),
      vendor: text(device.vendorString),
      device: text(device.deviceString),
      driverVersion: text(device.driverVersion),
      active: device.active === true,
      dedicatedVramBytes: null,
      computeVerified: false
    };
  });
}

async function detectHardware(dataDirectory, getGpuInfo, {
  system = os, statfs = fs.statfs, now = () => new Date().toISOString(),
  timeoutMs = DETECTION_TIMEOUT_MS
} = {}) {
  if (typeof getGpuInfo !== "function") throw new Error("GPU diagnostic capability is unavailable.");
  let timer;
  let volume;
  let gpuInfo;
  try {
    [volume, gpuInfo] = await Promise.race([
      Promise.all([statfs(dataDirectory, { bigint: true }), getGpuInfo("complete")]),
      new Promise((_, reject) => {
        timer = setTimeout(() => reject(new Error("Hardware diagnostics exceeded the 15-second deadline.")), timeoutMs);
      })
    ]);
  } finally {
    clearTimeout(timer);
  }
  const disk = volume.bavail * volume.bsize;
  if (disk < 0n || disk > BigInt(Number.MAX_SAFE_INTEGER)) throw new Error("Free-disk measurement is outside the supported range.");
  const cpus = system.cpus();
  const measurements = {
    totalMemoryBytes: system.totalmem(),
    availableMemoryBytes: system.freemem(),
    freeDiskBytes: Number(disk),
    architecture: system.arch()
  };
  return {
    schema: "axiomzero-hardware-assessment-v1",
    measuredAt: now(),
    platform: system.platform(),
    cpuModel: cpus[0]?.model?.slice(0, 200) || "CPU model unavailable",
    logicalCpuCount: cpus.length,
    ...measurements,
    diskScope: "Application-data volume only; other drives are not scanned.",
    gpus: describeGpu(gpuInfo),
    assessment: assessHardware(measurements),
    privacy: "Local diagnostics only. No hostname, account name, serial number, files, network request or automatic model download. Not retained unless explicitly exported."
  };
}

module.exports = { GIB, DETECTION_TIMEOUT_MS, assessHardware, describeGpu, detectHardware };
