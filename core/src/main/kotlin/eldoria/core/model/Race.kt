package eldoria.core.model

/**
 * A race's fixed ability-score modifiers, applied once at character
 * creation on top of the rolled base scores.
 */
data class AbilityModifiers(val strength: Int, val agility: Int, val willpower: Int)

/**
 * The five playable peoples of Eldoria. Each has ability-score modifiers and
 * a set of skill affinities -- a starting-level bonus applied to a skill the
 * moment a character of that race first knows it (at creation for base
 * skills, or the moment it's learned from a trainer for locked ones).
 */
enum class Race(
    val displayName: String,
    val lore: String,
    val abilityModifiers: AbilityModifiers,
    val skillAffinities: Map<SkillType, Int>,
    /** Flavor line describing what this race is naturally resistant to. */
    val resistanceLore: String,
    /** Flat percent reduction applied to incoming magic damage (see CombatMath). */
    val magicResistancePercent: Int,
) {
    ELF(
        "Elf",
        "Long-lived and graceful, elves favor the bow and the arcane over brute force.",
        AbilityModifiers(strength = -1, agility = 2, willpower = 2),
        mapOf(
            SkillType.ARCHERY to 10,
            SkillType.SNEAK to 5,
            SkillType.DESTRUCTION to 10,
            SkillType.ILLUSION to 10,
            SkillType.ALTERATION to 5,
        ),
        resistanceLore = "resistant to poison",
        magicResistancePercent = 10,
    ),
    HUMAN(
        "Human",
        "Adaptable and ambitious, humans have no great weakness and a knack for dealing with others.",
        AbilityModifiers(strength = 0, agility = 0, willpower = 1),
        mapOf(
            SkillType.SPEECH to 10,
            SkillType.ONE_HANDED to 3,
            SkillType.LIGHT_ARMOR to 3,
            SkillType.BLOCK to 3,
            SkillType.SNEAK to 3,
        ),
        resistanceLore = "no special resistance, but no particular weakness either",
        magicResistancePercent = 0,
    ),
    NORD(
        "Nord",
        "Hardy warriors of the frozen north, raised on cold steel and colder winters.",
        AbilityModifiers(strength = 2, agility = 0, willpower = -1),
        mapOf(
            SkillType.TWO_HANDED to 10,
            SkillType.ONE_HANDED to 5,
            SkillType.BLOCK to 10,
            SkillType.HEAVY_ARMOR to 10,
        ),
        resistanceLore = "resistant to frost",
        magicResistancePercent = 20,
    ),
    DWARF(
        "Dwarf",
        "Stout and stubborn, unmatched at the forge and unshaken behind a shield wall.",
        AbilityModifiers(strength = 2, agility = -1, willpower = 1),
        mapOf(
            SkillType.BLACKSMITHING to 15,
            SkillType.HEAVY_ARMOR to 10,
            SkillType.BLOCK to 5,
            SkillType.ENCHANTING to 5,
        ),
        resistanceLore = "resistant to poison and disease",
        magicResistancePercent = 15,
    ),
    ORC(
        "Orc",
        "Fierce and imposing, orcs are bred for battle and have little patience for magic or manners.",
        AbilityModifiers(strength = 3, agility = 1, willpower = -2),
        mapOf(
            SkillType.TWO_HANDED to 10,
            SkillType.UNARMED to 10,
            SkillType.ONE_HANDED to 5,
            SkillType.HEAVY_ARMOR to 5,
            SkillType.SPEECH to -5,
        ),
        resistanceLore = "resistant to pain and fear effects",
        magicResistancePercent = 10,
    ),
}
