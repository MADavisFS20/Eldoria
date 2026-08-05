package eldoria.core.world

import kotlin.random.Random

/**
 * Shared deterministic hashing used by WorldGenerator and SubRealmGenerator.
 * No stored RNG state: any (seed, ...parts) always mixes down to the same
 * Random stream, so the whole world (overworld + every dungeon/sky realm)
 * is fully reproducible from one top-level seed.
 */
object DeterministicRandom {
    // splitmix64-style mixer. NOTE: Kotlin hex Long literals must not have the
    // sign bit set unless written with a leading '-' (magnitude < 0x8000000000000000).
    fun mix64(z0: Long): Long {
        var z = z0
        z = (z xor (z ushr 30)) * -0xAE502812AA7333L
        z = (z xor (z ushr 27)) * -0x3B314601E57A13ADL
        return z xor (z ushr 31)
    }

    fun seed(vararg parts: Long): Long {
        var acc = 0L
        for (p in parts) acc = mix64(acc xor mix64(p))
        return acc
    }

    fun random(vararg parts: Long): Random = Random(seed(*parts))
}
