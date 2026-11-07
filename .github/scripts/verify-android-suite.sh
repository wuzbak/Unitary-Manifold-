#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 ThomasCory Walker-Pearson
set -euo pipefail

./gradlew --no-daemon :app:connectedDebugAndroidTest
mkdir -p build/device-verification
# Gradle removes the application and test package after connected tests.
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb install -r app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
adb shell run-as com.axiomzero.androidsuite rm -f files/local-model-smoke-receipt.json

timeout 35m adb shell am instrument -w \
  -e class com.axiomzero.androidsuite.LocalModelSmokeTest \
  -e requireRealModel true \
  -e modelSource app-download \
  -e timeout_msec 1800000 \
  com.axiomzero.androidsuite.test/androidx.test.runner.AndroidJUnitRunner \
  | tee build/device-verification/real-model-instrumentation.txt

# ADB can exit successfully even when Android instrumentation reports failure.
if ! grep -Eq '^OK \([1-9][0-9]* tests?\)' build/device-verification/real-model-instrumentation.txt; then
  echo "::error::Required real-model Android instrumentation did not pass."
  exit 1
fi

adb exec-out run-as com.axiomzero.androidsuite \
  cat files/local-model-smoke-receipt.json \
  > build/device-verification/local-model-smoke-receipt.json
python3 - <<'PY'
import json
from pathlib import Path

receipt = json.loads(Path("build/device-verification/local-model-smoke-receipt.json").read_text())
expected = {
    "mode": "real-pinned-model-app-download",
    "synthetic": False,
    "inference_executed": True,
    "import_verified": True,
    "source": "app-download",
    "model_bytes": 1280835840,
    "model_sha256": "aaf42c8b7c3cab2bf3d69c355048d4a0ee9973d48f16c731c0520ee914699223",
    "context_tokens": 512,
    "generation_max_tokens": 16,
}
for key, value in expected.items():
    if type(receipt.get(key)) is not type(value) or receipt[key] != value:
        raise SystemExit(f"Android real-model receipt has an invalid {key!r} value")
if not isinstance(receipt.get("output"), str) or not receipt["output"].strip():
    raise SystemExit("Android real-model inference produced no output")
print("Verified Android download, private import, native load and bounded real-model inference.")
PY
