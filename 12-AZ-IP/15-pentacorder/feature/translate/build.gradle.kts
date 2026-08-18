plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.kapt)
    alias(libs.plugins.hilt.android)
}

android {
    namespace = "com.gibbernode.feature.translate"
    compileSdk = 34

    defaultConfig {
        minSdk = 26
        consumerProguardFiles("consumer-rules.pro")
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
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
}

dependencies {
    // Compose BOM
    implementation(platform(libs.compose.bom))
    implementation(libs.compose.ui)
    implementation(libs.compose.ui.tooling.preview)
    implementation(libs.compose.material3)
    implementation(libs.compose.material.icons.extended)
    debugImplementation(libs.compose.ui.tooling)

    // Lifecycle / ViewModel
    implementation(libs.androidx.lifecycle.viewmodel.compose)
    implementation(libs.androidx.lifecycle.runtime.compose)

    // Navigation + Hilt
    implementation(libs.hilt.navigation.compose)
    implementation(libs.navigation.compose)

    // Hilt
    implementation(libs.hilt.android)
    kapt(libs.hilt.compiler)

    // Coroutines
    implementation(libs.coroutines.android)
    // Coroutines Play Services adapter — provides .await() for ML Kit Tasks
    implementation(libs.coroutines.play.services)

    // ML Kit — on-device language translation (59 languages, works offline)
    implementation(libs.mlkit.translate)
    // ML Kit — on-device language identification
    implementation(libs.mlkit.language.id)
    // ML Kit — on-device text recognition (Latin script, no network required)
    implementation(libs.mlkit.text.recognition)
    // ML Kit — on-device object detection (base model, no network required)
    implementation(libs.mlkit.objectdetection)

    // CameraX — single-frame capture for OCR and hazard scan
    implementation(libs.camera.core)
    implementation(libs.camera.camera2)
    implementation(libs.camera.lifecycle)

    // Internal modules
    implementation(project(":core:gibberwave"))
    implementation(project(":core:ui"))
    implementation(project(":core:interpret"))

    testImplementation(libs.junit)
    testImplementation(libs.mockk)
}

kapt {
    correctErrorTypes = true
}
