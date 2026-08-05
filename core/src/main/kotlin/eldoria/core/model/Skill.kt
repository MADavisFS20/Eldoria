package eldoria.core.model

enum class SkillCategory { COMBAT, MAGIC, STEALTH, CRAFTING }

/**
 * Every skill a character can practice. COMBAT and STEALTH skills are known
 * from character creation (everyone has picked up the basics of a blade or
 * of moving quietly). MAGIC and CRAFTING skills are `trainerLocked`: a
 * character knows nothing of them until they find and learn from the right
 * NPC trainer somewhere in the world (see SkillTrainerContentRegistry).
 */
enum class SkillType(val displayName: String, val category: SkillCategory, val trainerLocked: Boolean) {
    // Combat -- known from level 1.
    ONE_HANDED("One-Handed Weapons", SkillCategory.COMBAT, trainerLocked = false),
    TWO_HANDED("Two-Handed Weapons", SkillCategory.COMBAT, trainerLocked = false),
    ARCHERY("Archery", SkillCategory.COMBAT, trainerLocked = false),
    BLOCK("Block", SkillCategory.COMBAT, trainerLocked = false),
    HEAVY_ARMOR("Heavy Armor", SkillCategory.COMBAT, trainerLocked = false),
    LIGHT_ARMOR("Light Armor", SkillCategory.COMBAT, trainerLocked = false),
    UNARMED("Unarmed Combat", SkillCategory.COMBAT, trainerLocked = false),

    // Stealth -- known from level 1.
    SNEAK("Sneak", SkillCategory.STEALTH, trainerLocked = false),
    LOCKPICKING("Lockpicking", SkillCategory.STEALTH, trainerLocked = false),
    PICKPOCKETING("Pickpocketing", SkillCategory.STEALTH, trainerLocked = false),
    SPEECH("Speech", SkillCategory.STEALTH, trainerLocked = false),

    // Magic schools -- must be learned from a trainer.
    DESTRUCTION("Destruction Magic", SkillCategory.MAGIC, trainerLocked = true),
    RESTORATION("Restoration Magic", SkillCategory.MAGIC, trainerLocked = true),
    ALTERATION("Alteration Magic", SkillCategory.MAGIC, trainerLocked = true),
    ILLUSION("Illusion Magic", SkillCategory.MAGIC, trainerLocked = true),
    CONJURATION("Conjuration Magic", SkillCategory.MAGIC, trainerLocked = true),

    // Crafting -- must be learned from a trainer.
    BLACKSMITHING("Blacksmithing", SkillCategory.CRAFTING, trainerLocked = true),
    ALCHEMY("Alchemy", SkillCategory.CRAFTING, trainerLocked = true),
    ENCHANTING("Enchanting", SkillCategory.CRAFTING, trainerLocked = true),
    WOODWORKING("Woodworking", SkillCategory.CRAFTING, trainerLocked = true),
    LEATHERWORKING("Leatherworking", SkillCategory.CRAFTING, trainerLocked = true);

    companion object {
        val baseSkills: List<SkillType> = entries.filter { !it.trainerLocked }
        val trainerLockedSkills: List<SkillType> = entries.filter { it.trainerLocked }
    }
}

/** One skill's mastery: level 1..100, plus banked xp toward the next level. Use raises it -- nothing else does. */
data class Skill(val type: SkillType, val level: Int, val xp: Int = 0) : java.io.Serializable
