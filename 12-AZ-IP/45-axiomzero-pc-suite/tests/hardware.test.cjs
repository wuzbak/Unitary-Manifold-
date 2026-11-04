const test = require("node:test");
const assert = require("node:assert/strict");
const { GIB, assessHardware, describeGpu, detectHardware } = require("../lib/hardware.cjs");

const measurement = {
  architecture: "x64", totalMemoryBytes: 16 * GIB,
  availableMemoryBytes: 8 * GIB, freeDiskBytes: 30 * GIB
};
const system = {
  totalmem: () => measurement.totalMemoryBytes,
  freemem: () => measurement.availableMemoryBytes,
  arch: () => "x64", platform: () => "win32",
  cpus: () => [{ model: "Test CPU" }, { model: "Test CPU" }]
};

test("hardware screens measured RAM/disk but never selects weights or authorizes training", () => {
  const result = assessHardware(measurement);
  assert.equal(result.status, "ready-for-model-evaluation");
  assert.equal(result.modelSelected, false);
  assert.equal(result.trainingReady, false);
  assert.deepEqual(result.blockers, []);
});

test("hardware thresholds are inclusive and low resource/unsupported arch blockers are explicit", () => {
  assert.equal(assessHardware({ ...measurement, totalMemoryBytes: 8 * GIB,
    availableMemoryBytes: 4 * GIB, freeDiskBytes: 10 * GIB }).blockers.length, 0);
  for (const [key, value] of [
    ["totalMemoryBytes", 8 * GIB - 1], ["availableMemoryBytes", 4 * GIB - 1],
    ["freeDiskBytes", 10 * GIB - 1], ["architecture", "arm64"]
  ]) {
    const result = assessHardware({ ...measurement, availableMemoryBytes: 4 * GIB, [key]: value });
    assert.equal(result.status, "blocked-for-model-evaluation");
    assert.equal(result.blockers.length, 1);
  }
});

test("invalid and inconsistent measurements fail explicitly", () => {
  for (const value of [-1, NaN, Infinity, "16000", Number.MAX_SAFE_INTEGER + 1]) {
    assert.throws(() => assessHardware({ ...measurement, freeDiskBytes: value }));
  }
  assert.throws(() => assessHardware({ ...measurement, availableMemoryBytes: 17 * GIB }), /inconsistent/);
  assert.throws(() => assessHardware({ ...measurement, architecture: "mips" }), /architecture/);
});

test("GPU diagnostic identifiers are not misrepresented as VRAM or compute verification", () => {
  const [gpu] = describeGpu({ gpuDevice: [{
    vendorId: 4318, deviceId: 1234, deviceString: "<untrusted gpu>", active: true,
    dedicatedVramBytes: 24 * GIB, serialNumber: "excluded", driverVersion: "test"
  }] });
  assert.equal(gpu.dedicatedVramBytes, null);
  assert.equal(gpu.computeVerified, false);
  assert.equal(gpu.serialNumber, undefined);
  assert.equal(gpu.active, true);
  assert.throws(() => describeGpu({}), /device list/);
});

test("local hardware detection reads only app-data volume and allowlisted GPU metadata", async () => {
  const report = await detectHardware("/app-data", async (kind) => {
    assert.equal(kind, "complete");
    return { gpuDevice: [{ vendorId: 4318, deviceId: 1234, active: true }] };
  }, {
    system,
    statfs: async (directory, options) => {
      assert.equal(directory, "/app-data");
      assert.equal(options.bigint, true);
      return { bavail: 30n * 1024n * 1024n, bsize: 1024n };
    },
    now: () => "2026-11-04T00:00:00Z"
  });
  assert.equal(report.freeDiskBytes, 30 * GIB);
  assert.equal(report.logicalCpuCount, 2);
  assert.equal(report.platform, "win32");
  assert.equal(report.assessment.modelSelected, false);
  assert.equal(report.schema, "axiomzero-hardware-assessment-v1");
  assert.equal(report.hostname, undefined);
});

test("diagnostic driver/disk errors and out-of-range free space remain visible", async () => {
  await assert.rejects(detectHardware("/app-data", async () => { throw new Error("driver failure"); }, {
    system, statfs: async () => ({ bavail: 1n, bsize: 1n })
  }), /driver failure/);
  await assert.rejects(detectHardware("/app-data", async () => ({ gpuDevice: [] }), {
    system, statfs: async () => ({ bavail: 2n ** 60n, bsize: 1n })
  }), /outside the supported range/);
});

test("stalled GPU diagnostics fail within the deadline, without automatic installation", async () => {
  await assert.rejects(detectHardware("/app-data", () => new Promise(() => {}), {
    system, statfs: async () => ({ bavail: 1n, bsize: 1n }), timeoutMs: 10
  }), /deadline/);
});
