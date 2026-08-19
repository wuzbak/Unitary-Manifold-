// core:emf — pure JVM module, no Android SDK dependency.
// Magnetometer-based stud-finding, EMF zone classification, dirty-electricity analysis.
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
