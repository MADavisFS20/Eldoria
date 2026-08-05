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
    /** Chest slot (ItemKind.ARMOR). */
    val equippedArmor: Item? = null,
    /** Shield/off-hand slot -- ItemKind.OFFHAND. Merged in from the Python prototype's 6-slot equipment model (weapon/offhand/chest/head/ring/amulet), which Kotlin core originally didn't have at all. */
    val equippedOffhand: Item? = null,
    val equippedHead: Item? = null,
    val equippedRing: Item? = null,
    val equippedAmulet: Item? = null,
    /** A purchased boat, if any (kind=BOAT) -- wears down from sailing/combat, can be repaired or lost entirely. */
    val ownedBoat: Item? = null,
    /** Stackable crafting reagents (see data/CraftingMaterialContent.kt) -- material name -> count. */
    val materials: Map<String, Int> = emptyMap(),
    /** -100 (reviled) .. 100 (renowned). Shifts from combat outcomes and quest completion. */
    val reputation: Int = 0,
    /** Perk -> stack count. A Map rather than a Set so perks can be picked more than once -- merged in from the Python prototype, where every perk was stackable. See model/Perk.kt's doc. */
    val perks: Map<Perk, Int> = emptyMap(),
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
    fun perkRank(perk: Perk): Int = perks[perk] ?: 0

    /** Which of the 6 equip slots currently holds what, keyed by the ItemKind that slot accepts. Non-equippable kinds (QUEST_ITEM, TRINKET, MATERIAL, BOAT) return null. */
    fun equippedInSlot(kind: ItemKind): Item? = when (kind) {
        ItemKind.WEAPON -> equippedWeapon
        ItemKind.ARMOR -> equippedArmor
        ItemKind.OFFHAND -> equippedOffhand
        ItemKind.HEAD -> equippedHead
        ItemKind.RING -> equippedRing
        ItemKind.AMULET -> equippedAmulet
        else -> null
    }

    fun withEquippedInSlot(kind: ItemKind, item: Item?): PlayerCharacter = when (kind) {
        ItemKind.WEAPON -> copy(equippedWeapon = item)
        ItemKind.ARMOR -> copy(equippedArmor = item)
        ItemKind.OFFHAND -> copy(equippedOffhand = item)
        ItemKind.HEAD -> copy(equippedHead = item)
        ItemKind.RING -> copy(equippedRing = item)
        ItemKind.AMULET -> copy(equippedAmulet = item)
        else -> this
    }

    val reputationTitle: String get() = when {
        reputation <= -60 -> "Reviled"
        reputation <= -20 -> "Outlaw"
        reputation < 20 -> "Unknown"
        reputation < 60 -> "Recognized"
        else -> "Renowned"
    }
}
