plugins {
    kotlin("jvm") version "2.0.21"
    application
}

repositories {
    mavenCentral()
}

kotlin {
    jvmToolchain(21)
}

application {
    mainClass.set("eldoria.core.MainKt")
}

tasks.test {
    useJUnitPlatform()
}

// The world-gen/QA report runs via the default `run` task (MainKt). The
// actual playable text-adventure demo runs via `gradle :core:play` instead,
// since it needs interactive stdin wired up (standardInput below) and a
// different entry point (GameKt).
tasks.register<JavaExec>("play") {
    group = "application"
    description = "Run the interactive Eldoria text-adventure demo."
    mainClass.set("eldoria.core.GameKt")
    classpath = sourceSets["main"].runtimeClasspath
    standardInput = System.`in`
}

dependencies {
    testImplementation(kotlin("test"))
}
