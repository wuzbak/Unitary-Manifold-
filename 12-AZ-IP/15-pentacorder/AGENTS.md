# AGENTS.md — Unitary Pentacorder
## AI Agent Orientation

Read this before any session touching the Pentacorder Android app.

---

## 1 · What This Is

The **Unitary Pentacorder** (`apps/android/pentacorder/`) is a feature-complete
Android app that turns a Samsung Galaxy S24 Ultra (or any Android 8.0+ phone)
into a 5-dimensional Kaluza-Klein sensor instrument.

Every hardware sensor maps to a Walker-Pearson manifold field.
The AI assistant reads live sensor context into every prompt.
The app is the physical instrument for the Unitary Manifold framework.

**Package:** `com.axiomzero.pentacorder`  
**Namespace (internal):** `com.gibbernode` (legacy — do not rename without updating all 109 Kotlin files)  
**Min SDK:** 26 (Android 8.0)  **Target:** 34  
**Status:** ✅ Feature-complete — Phases P0–P6 done, P7–P9 remaining

---

## 2 · Project Layout

```
apps/android/pentacorder/
├── AGENTS.md           ← this file (read first)
├── README.md           ← user-facing docs (build, install, first launch)
├── ROADMAP.md          ← phased plan with completion status
├── settings.gradle.kts ← rootProject.name = "Pentacorder"
├── app/                ← application module
│   └── src/main/java/com/gibbernode/
│       ├── MainActivity.kt       ← Single-Activity host + FAB + NavController
│       ├── AssistantViewModel.kt ← AI assistant brain + proactive sentinel
│       ├── AssistantSheet.kt     ← bottom sheet chat UI + coherence bar
│       └── AdaptiveCard.kt       ← adaptive card components
├── core/
│   ├── gibberwave/     ← SensorBridge, AssistantEngine, AdaptiveStateHolder
│   ├── audio/          ← GGWaveEncoder/Decoder, AudioLoopService
│   ├── security/       ← AES-256-GCM, GibberKeyManager, AcousticAuth
│   ├── health/         ← PPGAdvisor, TremorAdvisor, SkinColorAdvisor
│   ├── optics/         ← 7 optical advisor modules
│   ├── interpret/      ← SensorInterpreter, PentadState, UserRole
│   └── [emf, acoustic, spen, uwb, enviro, contractor, energy, connectivity]
├── feature/
│   ├── dashboard/      ← Mode ring, Sentinel health, Calibration wizard
│   ├── tricorder/      ← 5D sensor view + pinned metrics + camera launchers
│   ├── medical/        ← NEWS2, φ-homeostasis, rPPG, neuro, skin, first-aid
│   ├── translate/      ← Language bridge, sensor intel, protocol decoder
│   ├── mode/           ← GREEN/RED/BLUE/AMBER + Gibberlink transmit
│   ├── labs/           ← 15-suite grid + data logger + manifold probe
│   └── [spen, emf, enviro, contractor, uwb, acoustic, science, optics]
└── scripts/
    ├── install_s24ultra.sh  ← primary install script (ADB, Linux/macOS)
    ├── install_s24ultra.bat ← Windows ADB install
    ├── install_bv9900.sh    ← BV9900 Pro install (Linux/macOS)
    └── ...
```

---

## 3 · Key Architecture Facts

| Fact | Value |
|------|-------|
| DI framework | Hilt (all ViewModels `@HiltViewModel`, singletons `@Singleton`) |
| UI | Jetpack Compose + Material 3 |
| Navigation | Navigation-Compose single-activity with `NavHostController` |
| Persistence | DataStore (adaptive state), Room (audit log, calibration) |
| Background | WorkManager (SentinelWorker), Foreground Service (AudioLoopService) |
| AI resolution | Remote API → Local Ollama (127.0.0.1:11434) → Static KB |
| Sensor bus | `SensorBridge` Hilt singleton — writes from Tricorder/Medical/Translate/SPen VMs |
| Adaptive UI | `AdaptiveStateHolder` Hilt singleton — DataStore-persisted, read by all screens |

---

## 4 · What Must Never Break

- **Ethical axioms I–V** in `AssistantEngine.SYSTEM_PROMPT` — never modify or remove
- **SensorBridge flows** — all VMs must push their values on every state update
- **Calibration Wizard** — must run on first launch before Dashboard is shown
- **Medical disclaimers** in `DisclaimerRegistry` — must accompany all health guidance
- **`applicationId = com.axiomzero.pentacorder`** — changing this breaks existing installs
- **`namespace = com.gibbernode`** in all module build.gradle.kts — changing requires renaming all 109 Kotlin source directories

---

## 5 · What Remains (see ROADMAP.md P7–P9)

1. **Native ggwave NDK build** — current JNI stub compiles but produces silence; real audio requires NDK compilation of the C++ ggwave core for `arm64-v8a`
2. **CI/Release pipeline** — GitHub Actions to publish signed APK artifact
3. **Field validation** — physical install + calibration on S24 Ultra

---

## 6 · Session Protocol

Start every session by reading:
1. This file (AGENTS.md)
2. `ROADMAP.md` (which phase are we in?)
3. `sessions/` (latest session handoff)

End every session by:
1. Updating `sessions/SESSION_XXX.md` with `Ψ_n` (what's done) and `Ψ_{n+1}` (next step)
2. Running `report_progress` to push changes

---

*AGENTS.md — Unitary Pentacorder — v1.0 — 2026-05-05*
