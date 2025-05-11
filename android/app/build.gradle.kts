plugins {
    id("com.android.application")
}

android {
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.word_learning_app"
        minSdk = 21
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("debug")
            isMinifyEnabled = false
            isShrinkResources = false
        }
    }
}

dependencies {
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("androidx.webview:webview:1.0.0")
}