package eldoria.core.world

import eldoria.core.model.CharacterClass
import eldoria.core.model.Perk
import eldoria.core.model.Race
import kotlin.random.Random
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith

/** Covers Phase 1's perk-stacking merge (perks: Set<Perk> -> Map<Perk, Int>). */
class PerkEffectsPhase1Test {

    private fun playerWithPendingChoices(n: Int) =
        PlayerCharacterFactory.create("Test", Race.HUMAN, CharacterClass.WARRIOR, Random(1))
            .copy(pendingPerkChoices = n)

    @Test
    fun `picking the same perk three times stacks its rank and its effect`() {
        var player = playerWithPendingChoices(3)
        val startingAc = player.armorClass

        repeat(3) { player = PerkEffects.applyPerk(player, Perk.IRON_SKIN) }

        assertEquals(3, player.perkRank(Perk.IRON_SKIN))
        assertEquals(startingAc + 3, player.armorClass, "each IRON_SKIN pick should add +1 AC, stacking to +3")
        assertEquals(0, player.pendingPerkChoices)
    }

    @Test
    fun `applying a perk with no pending choices throws`() {
        val player = playerWithPendingChoices(0)
        assertFailsWith<IllegalArgumentException> { PerkEffects.applyPerk(player, Perk.TOUGHNESS) }
    }

    @Test
    fun `distinct perks each get their own independent rank`() {
        var player = playerWithPendingChoices(2)
        player = PerkEffects.applyPerk(player, Perk.IRON_SKIN)
        player = PerkEffects.applyPerk(player, Perk.TOUGHNESS)

        assertEquals(1, player.perkRank(Perk.IRON_SKIN))
        assertEquals(1, player.perkRank(Perk.TOUGHNESS))
        assertEquals(0, player.perkRank(Perk.QUICK_REFLEXES), "an unpicked perk must read as rank 0, not throw")
    }
}
