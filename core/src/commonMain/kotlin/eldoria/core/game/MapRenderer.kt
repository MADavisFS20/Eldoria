package eldoria.core.game

import eldoria.core.model.PopulationTier
import eldoria.core.model.RealmKind
import eldoria.core.model.TerrainKind

/**
 * Renders a bordered ASCII viewport of the map centered on the player.
 * True fog of war: a tile only ever shows a symbol once the player has
 * physically stood on it (GameSession.discoveredLocations) -- everything
 * else is blank, per the "toggle map that's visible once a tile is
 * discovered" spec. This is an inline "print the map into the scrolling
 * log" toggle, not a persistent split-pane -- a real fixed split-screen
 * needs a proper terminal UI (or the eventual Android app), tracked as
 * future UI work.
 */
object MapRenderer {
    private const val HALF_WIDTH = 12
    private const val HALF_HEIGHT = 6

    fun render(session: GameSession): String {
        val world = session.world
        val player = session.currentLocation
        val sb = StringBuilder()
        val width = HALF_WIDTH * 2 + 1
        sb.append(AnsiText.bold("+" + "-".repeat(width) + "+")).append('\n')

        for (dy in -HALF_HEIGHT..HALF_HEIGHT) {
            val y = player.y + dy
            sb.append(AnsiText.bold("|"))
            for (dx in -HALF_WIDTH..HALF_WIDTH) {
                val x = player.x + dx
                sb.append(symbolAt(session, world, x, y))
            }
            sb.append(AnsiText.bold("|")).append('\n')
        }
        sb.append(AnsiText.bold("+" + "-".repeat(width) + "+")).append('\n')
        sb.append(
            "Legend: ${AnsiText.cyan("@")}=you  ${AnsiText.yellow("C")}=city  ${AnsiText.yellow("v")}=village  " +
                "${AnsiText.red("D")}=dungeon  ${AnsiText.blue("S")}=sky realm  ${AnsiText.blue("~")}=water  ${AnsiText.yellow("=")}=bridge  " +
                "${AnsiText.red("!")}=hazard  ${AnsiText.white(".")}=explored  (blank)=undiscovered"
        )
        return sb.toString()
    }

    private fun symbolAt(session: GameSession, world: eldoria.core.model.World, x: Int, y: Int): String {
        if (x == session.currentLocation.x && y == session.currentLocation.y) return AnsiText.cyan("@")
        if (x < 0 || y < 0 || x >= world.width || y >= world.height) return " "
        val loc = world.locationAt(x, y) ?: return " "
        if (loc.id !in session.discoveredLocations) return " "
        return when {
            loc.portalKind == RealmKind.DUNGEON -> AnsiText.red("D")
            loc.portalKind == RealmKind.SKY_REALM -> AnsiText.blue("S")
            loc.populationTier == PopulationTier.CITY -> AnsiText.yellow("C")
            loc.populationTier == PopulationTier.COUNTRYSIDE -> AnsiText.yellow("v")
            loc.hazard != null -> AnsiText.red("!")
            loc.terrain == TerrainKind.BRIDGE -> AnsiText.yellow("=")
            loc.terrain == TerrainKind.WATERWAY -> AnsiText.blue("~")
            else -> AnsiText.white(".")
        }
    }
}
