import org.jetbrains.kotlin.gradle.targets.js.nodejs.NodeJsRootExtension
import org.jetbrains.kotlin.gradle.targets.js.nodejs.NodeJsRootPlugin

plugins {
    kotlin("multiplatform") version "2.0.21" apply false
    kotlin("plugin.serialization") version "2.0.21" apply false
    kotlin("plugin.compose") version "2.0.21" apply false
    id("org.jetbrains.compose") version "1.7.1" apply false
}

// Termux/Android has no glibc, so the Kotlin JS/Wasm plugin's own downloaded
// Node.js binary (linked against /lib/ld-linux-aarch64.so.1) can't execute.
// Use Termux's `pkg install nodejs` build from PATH instead.
plugins.withType<NodeJsRootPlugin> {
    rootProject.extensions.configure<NodeJsRootExtension> {
        download = false
    }
}
