package eldoria.core.world

import eldoria.core.game.GameSession
import kotlinx.browser.localStorage
import kotlinx.serialization.json.Json

private val json = Json { ignoreUnknownKeys = true; allowStructuredMapKeys = true }
private const val SAVE_KEY = "eldoria_save"

actual object SaveManager {
    actual fun exists(): Boolean = localStorage.getItem(SAVE_KEY) != null

    actual fun save(snapshot: GameSession.Snapshot) {
        localStorage.setItem(SAVE_KEY, json.encodeToString(GameSession.Snapshot.serializer(), snapshot))
    }

    actual fun load(): GameSession.Snapshot? {
        val raw = localStorage.getItem(SAVE_KEY) ?: return null
        return json.decodeFromString(GameSession.Snapshot.serializer(), raw)
    }
}
