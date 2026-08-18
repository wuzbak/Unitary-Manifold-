// core:contractor — pure JVM module, no Android SDK dependency.
// Acoustic impedance material classifier, barometric level, 200 MP doc-forensics helpers.
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
