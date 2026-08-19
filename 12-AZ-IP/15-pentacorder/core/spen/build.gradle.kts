// core:spen — pure JVM module, no Android SDK dependency.
// S Pen stroke analysis, gesture classification, air-writing hashing.
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
