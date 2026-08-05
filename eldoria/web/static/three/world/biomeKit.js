// Per-biome visual variety, keyed by the same enum names the API returns
// (GameLocation.biome.name -- MOUNTAINS/PLAINS/DESERT/JUNGLE/TUNDRA/SEA).
// Adding a biome or swapping a prop for a real asset later means editing
// exactly one entry here -- chunk.js, scene.js, and the controller never
// need to change.
import { tree, snowPine, palm, rock, iceRock, duneRock, cactus } from "./propBuilder.js";

export const BIOME_KIT = {
  MOUNTAINS: { ground: 0x8a8a86, props: [{ build: rock, weight: 0.5 }, { build: snowPine, weight: 0.5 }], density: 14 },
  PLAINS: { ground: 0x6fae4a, props: [{ build: tree, weight: 0.7 }, { build: rock, weight: 0.3 }], density: 10 },
  DESERT: { ground: 0xd9c18a, props: [{ build: cactus, weight: 0.5 }, { build: duneRock, weight: 0.5 }], density: 6 },
  JUNGLE: { ground: 0x2f6b3a, props: [{ build: palm, weight: 0.6 }, { build: rock, weight: 0.4 }], density: 18 },
  TUNDRA: { ground: 0xe4ecf0, props: [{ build: snowPine, weight: 0.6 }, { build: iceRock, weight: 0.4 }], density: 8 },
  SEA: { ground: 0x1a5c86, props: [], density: 0 },
};

export function biomeKitFor(biomeName) {
  return BIOME_KIT[biomeName] || BIOME_KIT.PLAINS;
}
