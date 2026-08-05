package eldoria.core.world

import eldoria.core.model.Perk
import eldoria.core.model.PlayerCharacter
import eldoria.core.model.SkillType

/**
 * Applies a chosen Perk's permanent effect. Most perks bake a flat stat
 * bump in immediately (same "recompute once, store the result" style as
 * LevelProgression); SECOND_WIND and MASTER_TRADER don't touch a stat here
 * -- they're behavioral flags the game loop checks at the point of use
 * (a near-death save, a shop discount).
 */
object PerkEffects {
    fun applyPerk(player: PlayerCharacter, perk: Perk): PlayerCharacter {
        require(player.pendingPerkChoices > 0) { "No perk choice banked" }
        val withPerk = player.copy(perks = player.perks + perk, pendingPerkChoices = player.pendingPerkChoices - 1)
        return when (perk) {
            Perk.POWER_ATTACK -> withPerk.copy(attackBonus = withPerk.attackBonus + 2)
            Perk.IRON_SKIN -> withPerk.copy(armorClass = withPerk.armorClass + 1)
            Perk.QUICK_REFLEXES -> withPerk.copy(speed = withPerk.speed + 3)
            Perk.ARCANE_RESERVE -> withPerk.copy(willpower = withPerk.willpower + 2)
            Perk.SILENT_STEP -> {
                val sneak = withPerk.skills[SkillType.SNEAK]
                if (sneak == null) withPerk else withPerk.copy(
                    skills = withPerk.skills + (SkillType.SNEAK to sneak.copy(level = (sneak.level + 15).coerceAtMost(SkillProgression.MAX_SKILL_LEVEL))),
                )
            }
            Perk.TOUGHNESS -> withPerk.copy(maxHealth = withPerk.maxHealth + 15, currentHealth = withPerk.currentHealth + 15)
            Perk.SECOND_WIND -> withPerk // behavioral flag only, checked via `Perk.SECOND_WIND in player.perks`
            Perk.MASTER_TRADER -> withPerk // behavioral flag only, checked by ShopGenerator/shop commands
        }
    }
}
