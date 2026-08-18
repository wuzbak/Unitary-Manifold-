// core:acoustic — pure JVM module, no Android SDK dependency.
// FFT-based acoustic event detection: smoke alarm, glass break, engine knock, pipe leak.
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
