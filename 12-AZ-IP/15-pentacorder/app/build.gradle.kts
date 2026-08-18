plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.kapt)
    alias(libs.plugins.hilt.android)
}

android {
    namespace = "com.gibbernode"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.axiomzero.pentacorder"
        minSdk = 26
        targetSdk = 34
        versionCode = 2
        versionName = "1.0.0-pentacorder"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
        debug {
            isMinifyEnabled = false
            applicationIdSuffix = ".debug"
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        compose = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = libs.versions.compose.compiler.get()
    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    // AndroidX Core
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.lifecycle.viewmodel.compose)
    implementation(libs.androidx.activity.compose)

    // Compose BOM
    implementation(platform(libs.compose.bom))
    implementation(libs.compose.ui)
    implementation(libs.compose.ui.tooling.preview)
    implementation(libs.compose.material3)
    implementation(libs.compose.material.icons.extended)
    debugImplementation(libs.compose.ui.tooling)

    // Material (View-system — required for Theme.Material3.* XML themes)
    implementation(libs.material)

    // Navigation
    implementation(libs.navigation.compose)

    // Hilt
    implementation(libs.hilt.android)
    kapt(libs.hilt.compiler)
    implementation(libs.hilt.navigation.compose)

    // Room
    implementation(libs.room.runtime)
    implementation(libs.room.ktx)
    kapt(libs.room.compiler)

    // DataStore
    implementation(libs.datastore.preferences)

    // WorkManager
    implementation(libs.work.runtime.ktx)
    implementation(libs.hilt.work)
    kapt(libs.hilt.work.compiler)

    // Coroutines
    implementation(libs.coroutines.android)

    // Network
    implementation(libs.okhttp)
    implementation(libs.gson)

    // ZXing QR
    implementation(libs.zxing.core)

    // Feature modules
    implementation(project(":core:audio"))
    implementation(project(":core:security"))
    implementation(project(":core:gibberwave"))
    implementation(project(":core:ui"))
    implementation(project(":core:interpret"))
    implementation(project(":feature:dashboard"))
    implementation(project(":feature:mode"))
    implementation(project(":feature:registry"))
    implementation(project(":feature:audit"))
    implementation(project(":feature:medical"))
    implementation(project(":feature:tricorder"))
    implementation(project(":feature:translate"))

    // Pentacorder sensor-suite feature modules
    implementation(project(":feature:labs"))
    implementation(project(":feature:spen"))
    implementation(project(":feature:emf"))
    implementation(project(":feature:enviro"))
    implementation(project(":feature:contractor"))
    implementation(project(":feature:uwb"))
    implementation(project(":feature:acoustic"))
    implementation(project(":feature:science"))
    implementation(project(":feature:optics"))

    // Test
    testImplementation(libs.junit)
    testImplementation(libs.mockk)
}

kapt {
    correctErrorTypes = true
}
