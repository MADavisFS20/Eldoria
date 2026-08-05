package eldoria.core.model

/**
 * Three impossible pieces of technology, each hidden in a single far-flung
 * spot in the world (one per land biome, see WorldGenerator) -- deliberately
 * anachronistic ("odd space age technology") against the rest of the
 * hardcoded medieval-fantasy content. Picking one up (Game.kt's `take`)
 * auto-activates it permanently; it never sits in inventory and can't be
 * sold or lost. `attackBonus`/`armorClassBonus` are baked into the
 * character's stats once, at the moment of pickup (same pattern as
 * perks/subclasses); `telepathy` and `tradeDiscountPercent` are behavioral
 * flags checked at the point of use in Game.kt (`talk`, shop pricing).
 */
enum class ArtifactKind(
    val itemName: String,
    val lore: String,
    val activationLine: String,
    val telepathy: Boolean,
    val tradeDiscountPercent: Int,
    val attackBonus: Int,
    val armorClassBonus: Int,
) {
    TELEPATH_DEVICE(
        "Neural Resonance Circlet",
        "A thin band of some impossible dark alloy, warm to the touch, humming faintly even in dead silence.",
        "The moment it touches your skin it dissolves into your temple in a flash of cold light. Suddenly the " +
            "world is louder -- not with sound, but with something underneath it. You can hear what people are thinking.",
        telepathy = true, tradeDiscountPercent = 0, attackBonus = 0, armorClassBonus = 0,
    ),
    COERCION_DEVICE(
        "Neural Static Emitter",
        "A small device of matte black plating and blinking amber light, utterly unlike anything a blacksmith could forge.",
        "It fuses seamlessly into your palm, invisible beneath the skin. You flex your hand and feel something " +
            "new there -- a needle of pain you can point at anyone you choose, and they will never know where it came from.",
        telepathy = false, tradeDiscountPercent = 20, attackBonus = 0, armorClassBonus = 0,
    ),
    PRECOGNITION_DEVICE(
        "Chronal Lattice Implant",
        "A lattice of impossibly thin wire folded into a shape that hurts to look at directly, as if it exists half a second before it should.",
        "It sinks into your chest without leaving a mark. For one instant you see everything about to happen -- " +
            "then it's gone, but the feeling isn't. You'll always be just a heartbeat ahead of what comes next.",
        telepathy = false, tradeDiscountPercent = 0, attackBonus = 2, armorClassBonus = 2,
    ),
}
