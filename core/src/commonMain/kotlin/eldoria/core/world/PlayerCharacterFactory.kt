package eldoria.core.world

import eldoria.core.model.CharacterClass
import eldoria.core.model.DiceFormula
import eldoria.core.model.DieType
import eldoria.core.model.PlayerCharacter
import eldoria.core.model.Race
import eldoria.core.model.Skill
import eldoria.core.model.SkillType
import eldoria.core.model.StatBlock
import kotlin.random.Random

/**
 * Builds a fresh level-1 PlayerCharacter: rolls base ability scores (3d6,
 * race-modified), derives starting combat stats with the same formulas
 * LevelProgression uses at level 1 (so leveling up is a seamless
 * continuation, not a formula switch), and starts every base (non
 * trainer-locked) skill at a level shaped by class specialization and race
 * affinity. Trainer-locked skills (magic schools, crafting) start unknown
 * except for a class's one free `freeSignatureSkill`, if it has one --
 * everything else must be learned in the world (see SkillProgression).
 */
object PlayerCharacterFactory {

    private const val BASE_SKILL_FLOOR = 15
    private const val CLASS_PRIMARY_BONUS = 20
    private const val SIGNATURE_SKILL_START = 20

    fun create(name: String, race: Race, characterClass: CharacterClass, rng: Random): PlayerCharacter {
        val strength = (DiceFormula(3, DieType.D6, 0).roll(rng) + race.abilityModifiers.strength).coerceAtLeast(1)
        val agility = (DiceFormula(3, DieType.D6, 0).roll(rng) + race.abilityModifiers.agility).coerceAtLeast(1)
        val willpower = (DiceFormula(3, DieType.D6, 0).roll(rng) + race.abilityModifiers.willpower).coerceAtLeast(1)
        val strMod = StatBlock.modifierOf(strength)
        val agiMod = StatBlock.modifierOf(agility)

        val maxHealth = DiceFormula(2, DieType.D8, strMod * 2).roll(rng).coerceAtLeast(10)
        val maxStamina = DiceFormula(2, DieType.D8, agiMod * 2).roll(rng).coerceAtLeast(10)
        val baseArmorClass = 10 + agiMod
        val speed = (20 + agiMod * 2 + DiceFormula(1, DieType.D6).roll(rng)).coerceAtLeast(5)
        val attackBonus = strMod
        val unarmedDamage = DiceFormula(1, DieType.D6, strMod)
        val gold = DiceFormula(2, DieType.D8, 20).roll(rng)

        val skills = LinkedHashMap<SkillType, Skill>()
        for (type in SkillType.baseSkills) {
            val primaryBonus = if (type in characterClass.primarySkills) CLASS_PRIMARY_BONUS else 0
            val raceBonus = race.skillAffinities[type] ?: 0
            val level = (BASE_SKILL_FLOOR + primaryBonus + raceBonus).coerceIn(1, SkillProgression.MAX_SKILL_LEVEL)
            skills[type] = Skill(type, level)
        }
        characterClass.freeSignatureSkill?.let { type ->
            val raceBonus = race.skillAffinities[type] ?: 0
            val level = (SIGNATURE_SKILL_START + raceBonus).coerceIn(1, SkillProgression.MAX_SKILL_LEVEL)
            skills[type] = Skill(type, level)
        }

        val weapon = StatGenerator.weaponItem(characterClass.startingGear.weaponName, tier = 1, rng = rng)
        val armor = StatGenerator.armorItem(characterClass.startingGear.armorName, tier = 1, rng = rng)
        // Starting gear is equipped directly (bypassing Game.kt's equip(),
        // which normally bakes an item's bonus into the player's stats on
        // equip) -- so its armorClassBonus has to be folded in here too, or
        // new characters would start with armor that mechanically does
        // nothing until the player manually re-equips it.
        val armorClass = baseArmorClass + (armor.armorClassBonus ?: 0)

        return PlayerCharacter(
            name = name,
            race = race,
            characterClass = characterClass,
            level = 1,
            experience = 0,
            strength = strength,
            agility = agility,
            willpower = willpower,
            maxHealth = maxHealth,
            currentHealth = maxHealth,
            maxStamina = maxStamina,
            currentStamina = maxStamina,
            armorClass = armorClass,
            speed = speed,
            attackBonus = attackBonus,
            unarmedDamage = unarmedDamage,
            skills = skills,
            gold = gold,
            inventory = listOf(weapon, armor),
            equippedWeapon = weapon,
            equippedArmor = armor,
        )
    }
}
