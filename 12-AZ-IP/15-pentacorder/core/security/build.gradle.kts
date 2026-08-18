// core:security — JVM-only build for unit tests.
//
// Mirrors the approach in :core:audio.  GibberKeyManager is mocked via MockK in
// all tests so android.security.keystore.* and android.util.Base64 are never
// called at runtime.  android.jar on the compile classpath is sufficient.
plugins {
    alias(libs.plugins.kotlin.jvm)
}

val androidHome: String =
    System.getenv("ANDROID_HOME")
        ?: System.getenv("ANDROID_SDK_ROOT")
        ?: "/usr/local/lib/android/sdk"
val androidJar = file("$androidHome/platforms/android-34/android.jar")

kotlin {
    jvmToolchain(17)
}

dependencies {
    compileOnly(files(androidJar))
    testCompileOnly(files(androidJar))

    implementation(libs.coroutines.core)
    compileOnly(libs.javax.inject)

    // ZXing and Gson are used in GibberKeyManager (which is mocked in tests)
    // but we keep them so the production source compiles correctly.
    compileOnly(libs.gson)
    compileOnly(libs.zxing.core)

    testImplementation(libs.junit)
    testImplementation(libs.mockk)
}

