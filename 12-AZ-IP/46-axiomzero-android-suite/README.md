# Product 46 — AxiomZero Android Suite For Mobile Phones

**Version 0.1.0 · native Android app · readiness not assessed**

Product 46 adapts the Product 45 suite for Android phones. It provides the
same core offline portfolio front door, selected-checkout documentation,
private local evidence search, and governed research notes in a native,
single-column mobile interface. The bundled 46-product catalog is synchronized
from Product 45's canonical catalog builder.

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
- Keep imported evidence and notes on-device. There is no account, analytics,
  background network access, cloud fallback or automatic tool execution.

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

The "Ask" feature is local keyword retrieval, **not an AI model or generated
answer**. A matching excerpt does not prove that it supports a question.
Research notes remain UNVERIFIED. Product 45's experimental native model,
model training, Windows Python/Node runtime manager, supervised desktop
workbench, hardware diagnostics and Windows installer are not claimed as
Android capabilities in this version.

Import limits: 2 MiB per text document, 16 MiB of expanded ZIP data,
8 MiB total indexed text and 500 documents. Unsupported archive members within
the per-entry limit are skipped; oversized or malformed entries produce a
visible error. Only text entries are indexed. Product README display is capped
at 256 KiB.

## Build and install

Requirements: Android Studio with Android SDK 34 and JDK 17. Open this
directory as a Gradle project, allow Android Studio to resolve the pinned
Gradle plugin/library versions, then run `./gradlew :app:assembleDebug` or
`./gradlew :app:testDebugUnitTest`. The output is an unsigned debug APK under
`app/build/outputs/apk/debug/`; it is not a Play Store or release-signed
artifact. Enable developer installation or use Android Studio's Run action
to install it on a test phone.

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
