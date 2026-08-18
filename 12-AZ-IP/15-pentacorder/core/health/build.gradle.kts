// core:health — pure JVM module, no Android SDK dependency.
// rPPG heart-rate estimation, S Pen tremor screening, skin-color pallor/jaundice index.
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
