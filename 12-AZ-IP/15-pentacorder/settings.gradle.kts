pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "Pentacorder"

// ── App ───────────────────────────────────────────────────────────────────────
include(":app")

// ── Core modules ──────────────────────────────────────────────────────────────
// JVM-only (kotlin.jvm) — no Android Gradle Plugin required
include(":core:audio")
include(":core:security")

// Pentacorder sensor-suite advisors — pure JVM, no AGP required
include(":core:spen")
include(":core:emf")
include(":core:enviro")
include(":core:health")
include(":core:contractor")
include(":core:uwb")
include(":core:acoustic")
include(":core:optics")

// Android library modules — require AGP + Google Maven
include(":core:gibberwave")
include(":core:ui")
include(":core:interpret")
include(":core:energy")
include(":core:connectivity")

// ── Feature modules (all android.library) ─────────────────────────────────────
include(":feature:dashboard")
include(":feature:mode")
include(":feature:registry")
include(":feature:audit")
include(":feature:medical")
include(":feature:tricorder")
include(":feature:translate")
include(":feature:labs")
include(":feature:spen")
include(":feature:emf")
include(":feature:enviro")
include(":feature:contractor")
include(":feature:uwb")
include(":feature:acoustic")
include(":feature:science")
include(":feature:optics")
