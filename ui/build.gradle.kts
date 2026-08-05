import org.jetbrains.compose.desktop.application.dsl.TargetFormat

plugins {
    kotlin("multiplatform")
    id("org.jetbrains.compose")
    kotlin("plugin.compose")
}

repositories {
    mavenCentral()
    google()
}

kotlin {
    jvmToolchain(21)

    jvm()

    // Same Chromium-only tradeoff as :core's wasmJs target -- see
    // /data/data/com.termux/files/home/.claude/plans/mossy-wandering-dusk.md
    wasmJs {
        browser()
        binaries.executable()
    }

    sourceSets {
        val commonMain by getting {
            dependencies {
                implementation(project(":core"))
                implementation(compose.runtime)
                implementation(compose.foundation)
                implementation(compose.material3)
                implementation(compose.ui)
            }
        }
        val jvmMain by getting {
            dependencies {
                implementation(compose.desktop.currentOs)
            }
        }
    }
}

compose.desktop {
    application {
        mainClass = "eldoria.ui.MainKt"
        nativeDistributions {
            targetFormats(TargetFormat.Deb, TargetFormat.Dmg, TargetFormat.Msi)
            packageName = "Eldoria"
            packageVersion = "1.0.0"
        }
    }
}
