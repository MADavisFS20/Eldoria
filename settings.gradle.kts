rootProject.name = "Eldoria"

pluginManagement {
    repositories {
        gradlePluginPortal()
        google()
        mavenCentral()
    }
}

dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }
}

include(":core")
// ":app" (Android application module) will be added once the Android SDK
// is installed on this device. The core module has no Android dependency
// and already contains the entire world/game engine.
