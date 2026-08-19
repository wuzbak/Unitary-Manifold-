// core:enviro — pure JVM module, no Android SDK dependency.
// Barometer-based weather analysis, indoor floor estimation, light-lab science.
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
