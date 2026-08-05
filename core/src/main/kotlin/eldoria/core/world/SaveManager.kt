package eldoria.core.world

import eldoria.core.game.GameSession
import java.io.File
import java.io.ObjectInputStream
import java.io.ObjectOutputStream

/**
 * File-based save/load, plain Java serialization -- no external dependency
 * needed for a single-player local save. Per explicit spec: autosave every
 * 10 real minutes (and on sleep) works by deleting the old save and writing
 * a fresh one, not versioning multiple saves. Writes to a temp file first
 * and only replaces the real save file once the write succeeds, so a crash
 * mid-write can't corrupt the existing save.
 */
object SaveManager {
    private val saveFile = File("eldoria_save.dat")
    private val tmpFile = File("eldoria_save.dat.tmp")

    fun exists(): Boolean = saveFile.exists()

    fun save(snapshot: GameSession.Snapshot) {
        ObjectOutputStream(tmpFile.outputStream()).use { it.writeObject(snapshot) }
        if (saveFile.exists()) saveFile.delete()
        tmpFile.renameTo(saveFile)
    }

    fun load(): GameSession.Snapshot? {
        if (!saveFile.exists()) return null
        return ObjectInputStream(saveFile.inputStream()).use { it.readObject() as GameSession.Snapshot }
    }
}
