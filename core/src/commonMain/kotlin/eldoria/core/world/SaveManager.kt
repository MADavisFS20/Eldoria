package eldoria.core.world

import eldoria.core.game.GameSession

/**
 * Single-player local save. Per explicit spec: autosave every 10 real
 * minutes (and on sleep) works by deleting the old save and writing a fresh
 * one, not versioning multiple saves.
 *
 * Platform-specific: JVM writes to a temp file first and only replaces the
 * real save file once the write succeeds, so a crash mid-write can't corrupt
 * the existing save (see jvmMain's actual). Wasm/browser uses localStorage,
 * which has no equivalent partial-write failure mode (see wasmJsMain's actual).
 */
expect object SaveManager {
    fun exists(): Boolean
    fun save(snapshot: GameSession.Snapshot)
    fun load(): GameSession.Snapshot?
}
