# Product 46 — AxiomZero Android Suite For Mobile Phones

**Version 0.1.0 · native Android app · readiness not assessed**

Product 46 adapts the Product 45 suite for Android phones. It provides the
same portfolio front door, selected-checkout documentation, private local
evidence search, governed research notes, and optional on-device AI in a
native, single-column mobile interface. The bundled 46-product catalog is
synchronized from Product 45's canonical catalog builder.

## Features

- Search all registered AxiomZero products offline, with version, readiness
  label, endpoint, description and folder.
- Optionally select a repository checkout using Android's Storage Access
  Framework, then read a product's `README.md` in-app. Access is read-only and
  limited to the folder the user selected.
- Import user-selected supported text files or ZIP archives into the app's
  private storage. Supported text types are TXT, Markdown, JSON, CSV, Python,
  Kotlin, Java, HTML, XML, YAML, TOML, reStructuredText and logs. Archive
  members are indexed in memory; they are not extracted to shared storage.
- Search local text by keyword and return excerpts with source names, line
  numbers and SHA-256 digests. Save those results as explicitly UNVERIFIED
  research notes and export the notebook to a user-selected destination.
- Optionally download or import a pinned Qwen3.5-2B GGUF model. Either transfer
  requires an explicit user action. A strict size-and-SHA-256 check precedes
  atomic installation into private app storage; inference runs locally through
  pinned llama.cpp JNI on arm64-v8a or x86_64.
- Run bounded, CPU-only model inference only after an explicit tap and only
  when matching local evidence exists. At most three local excerpts are
  supplied as context; answers and sources remain explicitly UNVERIFIED.
- Keep imported evidence, model weights and notes on-device. There is no
  account, analytics, background network access, cloud fallback, external
  inference service, or automatic tool/write execution. Internet permission
  is used only for the explicit model-download action.

## Android-specific boundaries

Android app installation and updates remain controlled by Android's package
installer and the user. Product 46 does not use ADB, silently replace apps,
install system runtimes, request all-files access, or run arbitrary portfolio
commands. The app asks for access only through Android's document pickers.

The local evidence index and notebook are plaintext in private app storage,
not encrypted memory. Clearing app data removes them. Exports may contain
private excerpts and are written only after the user picks a destination.
ZIP processing accepts only bounded supported text entries; it does not
extract, execute, or follow archive paths.

The Evidence tab's "Ask" feature is local keyword retrieval, **not an AI model
or generated answer**. The separate Local AI tab optionally runs Qwen3.5-2B
offline, grounded only in at most three retrieved snippets; this is not a
verification mechanism. A matching excerpt does not prove that it supports a
question, and all model output and research notes remain UNVERIFIED. No model
is bundled in the APK. Product 45's model training, Windows Python/Node runtime
manager, supervised desktop workbench, hardware diagnostics and Windows
installer are not Android capabilities.

The bounded mobile answer path uses Qwen3.5's non-thinking assistant prefix,
so its token budget is spent on a direct answer rather than an unfinished
scratchpad. This formatting follows the
[Qwen3.5 template included in the pinned engine](https://github.com/ggml-org/llama.cpp/blob/9f0e5098a5d5d8adb8dd5c59036ae2a38ab07db9/models/templates/Qwen3.5-4B.jinja).
Runtime qualification requires an actual completed greeting, not merely
nonempty reasoning or error text; it does not certify general answer quality.

Import limits: 2 MiB per text document, 16 MiB of expanded ZIP data,
8 MiB total indexed text and 500 documents. Unsupported archive members within
the per-entry limit are skipped; oversized or malformed entries produce a
visible error. Only text entries are indexed. Product README display is capped
at 256 KiB. Model transfer is fixed to 1,280,835,840 bytes and the pinned
SHA-256 below; other files cannot be installed as models. At least 4 GiB total
RAM is required before inference and 1.75 GiB free private storage before a
model transfer. Model weights use CPU memory, so inference may still be slow
or fail under memory pressure.

## Pinned on-device model and native engine

- GGUF artifact: [`Qwen3.5-2B-Q4_K_M.gguf`](https://huggingface.co/Unsloth/Qwen3.5-2B-GGUF/blob/802854bfd388ed92748de119df31327962811548/Qwen3.5-2B-Q4_K_M.gguf)
- Immutable repository revision: `802854bfd388ed92748de119df31327962811548`
- Exact size: `1280835840` bytes
- SHA-256: `aaf42c8b7c3cab2bf3d69c355048d4a0ee9973d48f16c731c0520ee914699223`
- Base model card/license: [Qwen/Qwen3.5-2B](https://huggingface.co/Qwen/Qwen3.5-2B) (Apache-2.0)
- Native engine: [llama.cpp](https://github.com/ggml-org/llama.cpp), pinned to
  commit `9f0e5098a5d5d8adb8dd5c59036ae2a38ab07db9` (MIT; see
  [`LLAMA_CPP_LICENSE.txt`](LLAMA_CPP_LICENSE.txt)).
- The GGUF is a third-party quantized distribution, fetched only after a user
  selects Download or imported via Android's file picker. Its card and license
  terms should be reviewed before use. The project does not redistribute the
  weights in source or APKs.

The native build retrieves llama.cpp at the immutable Git commit using CMake
FetchContent and checks the checked-out revision. The Android Gradle project
pins JDK 17, Android Gradle Plugin 8.3.2, NDK `26.1.10909125`, CMake `3.22.1`,
API 34, and ABI filters `arm64-v8a` and `x86_64`. CI needs Git access to
`github.com` to fetch the source at build time.

## Build and install

Requirements: Android SDK 34, JDK 17, NDK `26.1.10909125`, and CMake `3.22.1`.
Open this directory as a Gradle project and allow Android Studio to resolve
the pinned plugin/library versions, NDK and CMake, then run
`./gradlew :app:assembleDebug` or `./gradlew :app:testDebugUnitTest`.
The output is a debug APK under
`app/build/outputs/apk/debug/`, signed with a non-production Android debug key;
it is not production/release-signed or Play Store-ready. Enable developer
installation or use Android Studio's Run action to install it on a test phone.

The `android-suite-v<versionName>` tag workflow publishes this APK and its
SHA-256 checksum as a GitHub pre-release. The main website's Product 46
download button links to those test releases. Install only on a device where
you accept test-build software; no physical-device qualification is claimed.
Each workflow build uses its runner's non-production debug signing key, so a
later test APK may not install as an in-place update. Uninstalling first
clears the app's private data; export any notes you need before reinstalling.

The native smoke test is `com.axiomzero.androidsuite.LocalModelSmokeTest`.
`./gradlew :app:connectedDebugAndroidTest` exercises JNI loading on a connected
emulator/device without downloading model weights; its JSON receipt explicitly
records `"mode":"synthetic-linkage"`, `"synthetic":true`, and
`"inference_executed":false` at `files/native-linkage-smoke-receipt.json`.
It also runs `LocalModelRuntimeOwnershipTest`, which races native cancellation
against session close using lightweight native session probes and no weights.
The separate real-model test is skipped unless `modelPath` or
`modelSource=app-download` is provided. CI should use an API 34 x86_64 emulator
(6 GiB RAM is suitable for the real-model lane). No model is in the APK.

Optional real-model emulator smoke using the app's own pinned HTTPS downloader
(no host model file or APK-bundled weights are needed):

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell run-as com.axiomzero.androidsuite mkdir -p no_backup/models
adb shell am instrument -w -e class com.axiomzero.androidsuite.LocalModelSmokeTest -e requireRealModel true -e modelSource app-download -e timeout_msec 3600000 com.axiomzero.androidsuite.test/androidx.test.runner.AndroidJUnitRunner
adb shell run-as com.axiomzero.androidsuite cat files/local-model-smoke-receipt.json
```

The real-model test rechecks exact size and SHA-256, loads the GGUF at a
512-token context and requires the exact direct answer `HELLO` within at most
16 generated tokens. Its receipt uses
`"mode":"real-pinned-model-app-download"`, `"synthetic":false`, and
`"inference_executed":true`, and includes model identity, bounded output, and
`"import_verified":true`. Before inference, the test streams the downloaded
file through the same verified private-store importer into a separate
temporary cache directory, checks its size/hash again, and deletes that copy
after the test. The app-download plus import-copy qualification needs roughly
2.56 GiB of free app storage while both verified files coexist.
The test receipt is diagnostic evidence, not proof of answer accuracy. A real
device/model performance or compatibility qualification is not claimed until
the corresponding emulator/device run succeeds.

To exercise the private-file/import path using a model placed by the workflow
with `adb run-as` (instead of downloading again):

```bash
adb shell run-as com.axiomzero.androidsuite mkdir -p no_backup/models
adb shell mkdir -p /sdcard/Android/data/com.axiomzero.androidsuite/files
adb push Qwen3.5-2B-Q4_K_M.gguf /sdcard/Android/data/com.axiomzero.androidsuite/files/Qwen3.5-2B-Q4_K_M.gguf
adb shell run-as com.axiomzero.androidsuite cp /sdcard/Android/data/com.axiomzero.androidsuite/files/Qwen3.5-2B-Q4_K_M.gguf no_backup/models/Qwen3.5-2B-Q4_K_M.gguf
adb shell am instrument -w -e class com.axiomzero.androidsuite.LocalModelSmokeTest -e requireRealModel true -e modelSource private-file -e modelPath /data/user/0/com.axiomzero.androidsuite/no_backup/models/Qwen3.5-2B-Q4_K_M.gguf -e timeout_msec 3600000 com.axiomzero.androidsuite.test/androidx.test.runner.AndroidJUnitRunner
```

The stream verifier, strict length/hash gates, and same-directory atomic
installer are also covered by `MobileModelTest`.

Before building, verify the bundled catalog from the repository root:

```bash
python 12-AZ-IP/46-axiomzero-android-suite/scripts/build_catalog.py --check
```

To refresh the Android asset after the canonical portfolio catalog changes:

```bash
python 12-AZ-IP/46-axiomzero-android-suite/scripts/build_catalog.py
```

No physical Android device, signed release, performance profile or production
readiness has been verified by the source or unit tests.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*

*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
