package eldoria.core.model

import kotlinx.serialization.Serializable

/**
 * The player's own character sheet. Immutable like every other model in the
 * engine -- progression (world/PlayerCharacterFactory, SkillProgression,
 * LevelProgression) always returns an updated copy, never mutates in place.
 *
 * Two independent progression tracks, per design:
 *  - `level`/`experience` (1..50) rises from combat/quest XP (LevelProgression)
 *    and grants small across-the-board stat growth, health and strength most.
 *  - `skills` (each 1..100) rise purely from using that skill (SkillProgression)
 *    and never feed back into character level.
 */
@Serializable
data class PlayerCharacter(
    val name: String,
    val race: Race,
    val characterClass: CharacterClass,
    val level: Int,
    val experience: Int,
    val strength: Int,
    val agility: Int,
    val willpower: Int,
    val maxHealth: Int,
    val currentHealth: Int,
    val maxStamina: Int,
    val currentStamina: Int,
    val armorClass: Int,
    val speed: Int,
    val attackBonus: Int,
    val unarmedDamage: DiceFormula,
    val skills: Map<SkillType, Skill>,
    val gold: Int,
    val inventory: List<Item> = emptyList(),
    val equippedWeapon: Item? = null,
    val equippedArmor: Item? = null,
    /** A purchased boat, if any (kind=BOAT) -- wears down from sailing/combat, can be repaired or lost entirely. */
    val ownedBoat: Item? = null,
    /** Stackable crafting reagents (see data/CraftingMaterialContent.kt) -- material name -> count. */
    val materials: Map<String, Int> = emptyMap(),
    /** -100 (reviled) .. 100 (renowned). Shifts from combat outcomes and quest completion. */
    val reputation: Int = 0,
    val perks: Set<Perk> = emptySet(),
    /** Perk picks earned but not yet spent -- one banked every 5 character levels. */
    val pendingPerkChoices: Int = 0,
    /** Set once per rest by SECOND_WIND; consumed the next time it saves the player from a killing blow. */
    val secondWindReady: Boolean = false,
    /** Vampire or Werewolf, if requested from the one NPC who offers each -- permanent and mutually exclusive. */
    val subclass: Subclass? = null,
    /** The Mad Scientist's bionic upgrade can only ever be taken once per character. */
    val bionicUpgradeUsed: Boolean = false,
    /** Hidden sci-fi artifacts found and auto-activated -- see model/Artifact.kt. Never sit in inventory. */
    val artifacts: Set<ArtifactKind> = emptySet(),
    /** A hired companion, if any -- see model/Companion.kt. Leaves after 3 real hours, can revive the player once per employment. */
    val companion: HiredCompanion? = null,
    /** Granted permanently by defeating The Big Kahoon-a -- lets the player swim any WATERWAY tile without a boat. */
    val hasGills: Boolean = false,
    /** The Big Kahoon-a is a unique boss; this just stops the gills-grant message from repeating on a rematch. */
    val defeatedBigKahoona: Boolean = false,
) {
    val isAlive: Boolean get() = currentHealth > 0
    val isExhausted: Boolean get() = currentStamina <= 0
    fun skillLevel(type: SkillType): Int = skills[type]?.level ?: 0
    fun knowsSkill(type: SkillType): Boolean = skills.containsKey(type)

    val reputationTitle: String get() = when {
        reputation <= -60 -> "Reviled"
        reputation <= -20 -> "Outlaw"
        reputation < 20 -> "Unknown"
        reputation < 60 -> "Recognized"
        else -> "Renowned"
    }
}
