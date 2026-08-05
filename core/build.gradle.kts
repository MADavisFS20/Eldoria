plugins {
    kotlin("multiplatform")
    kotlin("plugin.serialization")
}

repositories {
    mavenCentral()
}

kotlin {
    jvmToolchain(21)

    // Note: deliberately NOT using jvm { withJava() } + the `application`
    // plugin -- that combination conflicts with Gradle's configuration-role
    // locking on this Gradle/Kotlin version pairing ("Cannot change the
    // allowed usage of configuration ':core:apiElements'"). The `run` and
    // `play` tasks below are plain JavaExec tasks wired directly to the jvm
    // target's compilation output instead, which sidesteps that entirely.
    jvm()

    // Chromium-only (WasmGC requires Chrome/Edge 119+) -- accepted tradeoff,
    // this is a personal local web app, not a public site. See
    // /data/data/com.termux/files/home/.claude/plans/mossy-wandering-dusk.md
    wasmJs {
        browser()
        binaries.executable()
    }

    // androidTarget() is deliberately NOT declared yet: it requires the
    // Android Gradle Plugin, which requires real Android SDK access this
    // device doesn't have. Adding it now would break configuration entirely
    // rather than sit "inert". It's added in Phase 5, once SDK access
    // (a separate machine or CI) is in place. See
    // /data/data/com.termux/files/home/.claude/plans/mossy-wandering-dusk.md

    sourceSets {
        val commonMain by getting {
            dependencies {
                implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.3")
                // Multiplatform-safe wall-clock (epoch millis) -- replaces
                // System.currentTimeMillis(), which is JVM-only.
                implementation("org.jetbrains.kotlinx:kotlinx-datetime:0.6.1")
            }
        }
        val commonTest by getting {
            dependencies {
                implementation(kotlin("test"))
            }
        }
        val wasmJsMain by getting {
            dependencies {
                // Browser-target bindings (localStorage, etc.) -- split out of
                // stdlib for Kotlin/Wasm, unlike the older Kotlin/JS target.
                implementation("org.jetbrains.kotlinx:kotlinx-browser:0.3")
            }
        }
    }
}

tasks.named<Test>("jvmTest") {
    useJUnitPlatform()
}

val jvmMainCompilation = kotlin.jvm().compilations.getByName("main")

// Headless world-gen/QA report.
tasks.register<JavaExec>("run") {
    group = "application"
    description = "Run the headless world-gen QA report (MainKt)."
    mainClass.set("eldoria.core.MainKt")
    classpath = jvmMainCompilation.output.allOutputs + jvmMainCompilation.runtimeDependencyFiles!!
}

// The interactive text-adventure demo -- needs interactive stdin wired up
// (standardInput below) and a different entry point (GameKt) than `run`.
tasks.register<JavaExec>("play") {
    group = "application"
    description = "Run the interactive Eldoria text-adventure demo."
    mainClass.set("eldoria.core.GameKt")
    classpath = jvmMainCompilation.output.allOutputs + jvmMainCompilation.runtimeDependencyFiles!!
    standardInput = System.`in`
}
