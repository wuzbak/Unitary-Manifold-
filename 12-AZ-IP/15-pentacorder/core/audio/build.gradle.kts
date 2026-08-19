// core:audio — JVM-only build for unit tests.
//
// Uses the kotlin("jvm") plugin so the module compiles and runs its JVM unit
// tests without the Android Gradle Plugin.  android.jar is added as compileOnly
// so all Android API references in the production sources resolve at compile time.
// A lightweight android.util.Log stub (src/test/java/android/util/Log.java)
// replaces the throwing stubs from android.jar at test runtime.
//
// AudioLoopService.kt references dagger.hilt.android.AndroidEntryPoint.  Since
// Hilt is an AGP-dependent framework, we provide a minimal stub annotation in
// src/jvm-stubs/java so the class compiles.  AudioLoopService is never
// instantiated by any JVM unit test, so the stub is safe here.
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

sourceSets {
    main {
        // jvm-stubs provides @AndroidEntryPoint stub for AudioLoopService.kt.
        java.srcDir("src/jvm-stubs/java")
    }
}

dependencies {
    // Android SDK stubs — needed to compile sources that reference android.util.Log,
    // android.media.*, etc.  Not on the runtime classpath; test sources provide
    // their own android.util.Log stub so Log calls are no-ops at test time.
    compileOnly(files(androidJar))
    testCompileOnly(files(androidJar))

    // Coroutines (StateFlow, SharedFlow, Mutex used in production sources)
    implementation(libs.coroutines.core)

    // javax.inject annotations (@Inject, @Singleton) used in production sources
    compileOnly(libs.javax.inject)

    testImplementation(libs.junit)
    testImplementation(libs.mockk)
}

