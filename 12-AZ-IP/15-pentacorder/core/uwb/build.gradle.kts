// core:uwb — pure JVM module, no Android SDK dependency.
// UWB trilateration, "point-to-control" azimuth logic.
// Wraps the Android UwbManager API in an advisor that can be unit-tested on JVM.
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
