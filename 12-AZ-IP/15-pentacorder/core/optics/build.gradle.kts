// core:optics — pure JVM module, no Android SDK dependency.
// Five optical-physics advisors for the S24 Ultra camera unlocks:
//   NLOSAdvisor, HyperspectralAdvisor, MotionMagnificationAdvisor,
//   VisualMicrophoneAdvisor, SyntheticApertureAdvisor.
plugins {
    alias(libs.plugins.kotlin.jvm)
}

kotlin {
    jvmToolchain(17)
}

dependencies {
    testImplementation(libs.junit)
    testImplementation(libs.mockk)
}
