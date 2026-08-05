package eldoria.core.world

import eldoria.core.game.GameSession
import kotlinx.serialization.json.Json
import java.io.File

private val json = Json { ignoreUnknownKeys = true; allowStructuredMapKeys = true }

actual object SaveManager {
    private val saveFile = File("eldoria_save.json")
    private val tmpFile = File("eldoria_save.json.tmp")

    actual fun exists(): Boolean = saveFile.exists()

    actual fun save(snapshot: GameSession.Snapshot) {
        tmpFile.writeText(json.encodeToString(GameSession.Snapshot.serializer(), snapshot))
        if (saveFile.exists()) saveFile.delete()
        tmpFile.renameTo(saveFile)
    }

    actual fun load(): GameSession.Snapshot? {
        if (!saveFile.exists()) return null
        return json.decodeFromString(GameSession.Snapshot.serializer(), saveFile.readText())
    }
}
