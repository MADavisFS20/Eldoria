// Per-biome visual variety, keyed by the same enum names the API returns
// (GameLocation.biome.name -- MOUNTAINS/PLAINS/DESERT/JUNGLE/TUNDRA/SEA).
// Adding a biome or swapping a prop for a real asset later means editing
// exactly one entry here -- chunk.js, scene.js, and the controller never
// need to change.
import { tree, snowPine, palm, rock, iceRock, duneRock, cactus } from "./propBuilder.js";

// `sky` doubles as both scene.background and fog color for that biome --
// cheap per-tile atmosphere with a big visual payoff when crossing bands.
export const BIOME_KIT = {
  // Densities kept modest -- Phase 2 keeps several tiles loaded at once
  // (streaming radius), so per-tile counts multiply fast. See chunk.js's
  // note on InstancedMesh as the follow-up if this isn't enough headroom.
  MOUNTAINS: { ground: 0x8a8a86, sky: 0x9fb0c2, props: [{ build: rock, weight: 0.5 }, { build: snowPine, weight: 0.5 }], density: 10 },
  PLAINS: { ground: 0x6fae4a, sky: 0xbfe0a0, props: [{ build: tree, weight: 0.7 }, { build: rock, weight: 0.3 }], density: 8 },
  DESERT: { ground: 0xd9c18a, sky: 0xf0dfae, props: [{ build: cactus, weight: 0.5 }, { build: duneRock, weight: 0.5 }], density: 5 },
  JUNGLE: { ground: 0x2f6b3a, sky: 0x8fae8a, props: [{ build: palm, weight: 0.6 }, { build: rock, weight: 0.4 }], density: 12 },
  TUNDRA: { ground: 0xe4ecf0, sky: 0xd7e5ee, props: [{ build: snowPine, weight: 0.6 }, { build: iceRock, weight: 0.4 }], density: 6 },
  SEA: { ground: 0x1a5c86, sky: 0x9fc4d8, props: [], density: 0 },
};

export function biomeKitFor(biomeName) {
  return BIOME_KIT[biomeName] || BIOME_KIT.PLAINS;
}
