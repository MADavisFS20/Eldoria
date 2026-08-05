package eldoria.core.model

/** Starting gear flavor for a class -- names only; StatGenerator rolls the actual dice values at tier 1. */
data class StartingGear(val weaponName: String, val armorName: String)

/**
 * The seven playable archetypes. `primarySkills` start higher and gain xp
 * faster from use (see SkillProgression). `freeSignatureSkill`, when set, is
 * a single trainer-locked skill this class already knows a little of at
 * creation (a mage's first cantrip, a cleric's first prayer) -- every other
 * trainer-locked skill must still be found and learned in the world.
 */
enum class CharacterClass(
    val displayName: String,
    val description: String,
    val primarySkills: Set<SkillType>,
    val freeSignatureSkill: SkillType?,
    val startingGear: StartingGear,
) {
    WARRIOR(
        "Warrior",
        "A frontline fighter who wins battles through steel, armor, and grit.",
        setOf(SkillType.ONE_HANDED, SkillType.TWO_HANDED, SkillType.BLOCK, SkillType.HEAVY_ARMOR),
        freeSignatureSkill = null,
        StartingGear("Iron Longsword", "Iron Armor"),
    ),
    MAGE(
        "Mage",
        "A scholar of the arcane, trading steel for spellcraft across every school of magic.",
        setOf(SkillType.DESTRUCTION, SkillType.ALTERATION, SkillType.RESTORATION, SkillType.CONJURATION, SkillType.ILLUSION),
        freeSignatureSkill = SkillType.DESTRUCTION,
        StartingGear("Apprentice's Staff", "Padded Robes"),
    ),
    ROGUE(
        "Rogue",
        "A quick-fingered opportunist who prefers a hidden blade to an honest fight.",
        setOf(SkillType.ONE_HANDED, SkillType.SNEAK, SkillType.LOCKPICKING, SkillType.PICKPOCKETING, SkillType.LIGHT_ARMOR, SkillType.SPEECH),
        freeSignatureSkill = null,
        StartingGear("Steel Dagger", "Leather Jerkin"),
    ),
    RANGER(
        "Ranger",
        "A wilderness hunter, equally at home tracking prey and putting an arrow through it.",
        setOf(SkillType.ARCHERY, SkillType.LIGHT_ARMOR, SkillType.SNEAK, SkillType.UNARMED),
        freeSignatureSkill = null,
        StartingGear("Hunting Bow", "Leather Jerkin"),
    ),
    CLERIC(
        "Cleric",
        "A devoted healer who channels faith into restorative and protective magic.",
        setOf(SkillType.RESTORATION, SkillType.BLOCK, SkillType.LIGHT_ARMOR, SkillType.SPEECH),
        freeSignatureSkill = SkillType.RESTORATION,
        StartingGear("Mace of the Faithful", "Padded Robes"),
    ),
    PALADIN(
        "Paladin",
        "A holy warrior blending swordsmanship with the power to mend and protect.",
        setOf(SkillType.ONE_HANDED, SkillType.HEAVY_ARMOR, SkillType.BLOCK, SkillType.RESTORATION),
        freeSignatureSkill = SkillType.RESTORATION,
        StartingGear("Blessed Longsword", "Chainmail Armor"),
    ),
    /** Ported from the Python prototype's fifth class. No dedicated Necromancy skill exists yet, so life-drain/dark-rite flavor is expressed through Conjuration (raising/binding) and Destruction (dark damage) instead of inventing a new SkillType for one class. */
    NECROMANCER(
        "Necromancer",
        "A dark practitioner who trades in life drain, venomous curses, and forbidden rites.",
        setOf(SkillType.CONJURATION, SkillType.DESTRUCTION, SkillType.ALTERATION),
        freeSignatureSkill = SkillType.CONJURATION,
        StartingGear("Bone-Inlaid Staff", "Tattered Death Shroud"),
    ),
}
