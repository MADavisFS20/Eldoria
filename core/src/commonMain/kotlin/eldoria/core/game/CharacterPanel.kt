package eldoria.core.game

import eldoria.core.model.PlayerCharacter
import eldoria.core.world.LevelProgression

/**
 * The bordered "side window" character sheet: identity, HP/XP bars, core
 * stats, equipment, top skills, materials, and perks. Printed inline into
 * the scrolling log on the "character"/"c" command (see the split-pane
 * caveat in MapRenderer -- same limitation applies here).
 */
object CharacterPanel {
    private const val WIDTH = 46

    private fun bar(current: Int, max: Int, width: Int = 20): String {
        val filled = if (max <= 0) 0 else ((current.toDouble() / max) * width).toInt().coerceIn(0, width)
        return "[" + "#".repeat(filled) + "-".repeat(width - filled) + "]"
    }

    private fun line(s: String): String {
        val visibleLen = s.replace(Regex("\\[[0-9;]*m"), "").length
        val pad = (WIDTH - visibleLen).coerceAtLeast(0)
        return "| $s${" ".repeat(pad)} |"
    }

    fun render(player: PlayerCharacter): String {
        val sb = StringBuilder()
        val border = "+" + "-".repeat(WIDTH + 2) + "+"
        sb.append(AnsiText.bold(border)).append('\n')
        val subclassTag = player.subclass?.let { "  [${it.displayName}]" } ?: ""
        val gillsTag = if (player.hasGills) "  [Gilled]" else ""
        sb.append(line("${player.name} the ${player.race.displayName} ${player.characterClass.displayName}  (Lv${player.level})$subclassTag$gillsTag")).append('\n')
        sb.append(line("Reputation: ${player.reputationTitle} (${player.reputation})")).append('\n')
        sb.append(line("HP ${bar(player.currentHealth, player.maxHealth)} ${player.currentHealth}/${player.maxHealth}")).append('\n')
        sb.append(line("SP ${bar(player.currentStamina, player.maxStamina)} ${player.currentStamina}/${player.maxStamina}")).append('\n')
        val xpNeeded = LevelProgression.xpToNextLevel(player.level)
        sb.append(line("XP ${bar(player.experience, xpNeeded)} ${player.experience}/$xpNeeded")).append('\n')
        sb.append(line("STR ${player.strength}  AGI ${player.agility}  WIL ${player.willpower}")).append('\n')
        sb.append(line("AC ${player.armorClass}   SPD ${player.speed}   ATK ${if (player.attackBonus >= 0) "+" else ""}${player.attackBonus}")).append('\n')
        sb.append(line("Gold: ${player.gold}g")).append('\n')
        sb.append(line("-".repeat(WIDTH))).append('\n')
        sb.append(line("Weapon:  ${player.equippedWeapon?.name ?: "none"} ${player.equippedWeapon?.damage?.let { "($it)" } ?: ""}")).append('\n')
        sb.append(line("Chest:   ${player.equippedArmor?.name ?: "none"} ${player.equippedArmor?.armorClassBonus?.let { "(+$it AC)" } ?: ""}")).append('\n')
        sb.append(line("Offhand: ${player.equippedOffhand?.name ?: "none"} ${player.equippedOffhand?.armorClassBonus?.let { "(+$it AC)" } ?: ""}")).append('\n')
        sb.append(line("Head:    ${player.equippedHead?.name ?: "none"} ${player.equippedHead?.armorClassBonus?.let { "(+$it AC)" } ?: ""}")).append('\n')
        sb.append(line("Ring:    ${player.equippedRing?.name ?: "none"} ${player.equippedRing?.magicEffect?.let { "(${it.name})" } ?: ""}")).append('\n')
        sb.append(line("Amulet:  ${player.equippedAmulet?.name ?: "none"} ${player.equippedAmulet?.magicEffect?.let { "(${it.name})" } ?: ""}")).append('\n')
        sb.append(line("-".repeat(WIDTH))).append('\n')
        val topSkills = player.skills.values.sortedByDescending { it.level }.take(6)
        sb.append(line("Top skills:")).append('\n')
        for (s in topSkills) sb.append(line("  ${s.type.displayName}: ${s.level}")).append('\n')
        if (player.perks.isNotEmpty()) {
            sb.append(line("-".repeat(WIDTH))).append('\n')
            sb.append(line("Perks: " + player.perks.entries.joinToString(", ") { (perk, rank) ->
                if (rank > 1) "${perk.displayName} x$rank" else perk.displayName
            })).append('\n')
        }
        if (player.pendingPerkChoices > 0) {
            sb.append(line("Perk choices available: ${player.pendingPerkChoices} (use 'perk')")).append('\n')
        }
        if (player.artifacts.isNotEmpty()) {
            sb.append(line("-".repeat(WIDTH))).append('\n')
            sb.append(line("Artifacts: " + player.artifacts.joinToString(", ") { it.itemName })).append('\n')
        }
        player.companion?.let {
            sb.append(line("-".repeat(WIDTH))).append('\n')
            sb.append(line("Companion: ${it.name}${if (it.reviveUsed) " (revive used)" else " (can revive you once)"}")).append('\n')
        }
        sb.append(AnsiText.bold(border))
        return sb.toString()
    }

    fun renderInventory(player: PlayerCharacter): String {
        val sb = StringBuilder()
        val border = "+" + "-".repeat(WIDTH + 2) + "+"
        sb.append(AnsiText.bold(border)).append('\n')
        sb.append(line("Inventory")).append('\n')
        sb.append(line("-".repeat(WIDTH))).append('\n')
        if (player.inventory.isEmpty()) {
            sb.append(line("(empty)")).append('\n')
        } else {
            val equippedItems = setOfNotNull(player.equippedWeapon, player.equippedArmor, player.equippedOffhand, player.equippedHead, player.equippedRing, player.equippedAmulet)
            for (item in player.inventory) {
                val equipped = if (item in equippedItems) " [equipped]" else ""
                sb.append(line("${AnsiText.yellow(item.name)}$equipped -- ${item.value}g")).append('\n')
            }
        }
        if (player.materials.isNotEmpty()) {
            sb.append(line("-".repeat(WIDTH))).append('\n')
            sb.append(line("Materials:")).append('\n')
            for ((name, count) in player.materials) sb.append(line("  ${AnsiText.yellow(name)} x$count")).append('\n')
        }
        sb.append(AnsiText.bold(border))
        return sb.toString()
    }
}
