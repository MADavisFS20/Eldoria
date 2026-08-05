// Deterministic per-tile PRNG, seeded from the tile's id string ("12_7").
// Mirrors the *pattern* of eldoria/world/deterministic_random.py's seeded
// per-cell RNGs -- no bit-parity with Python is needed, only stability
// within a browser session so re-entering a chunk reproduces the same
// prop layout without an extra round trip.
export function tileRng(seedStr) {
  let h = 1779033703 ^ seedStr.length;
  for (let i = 0; i < seedStr.length; i++) {
    h = Math.imul(h ^ seedStr.charCodeAt(i), 3432918353);
    h = (h << 13) | (h >>> 19);
  }
  return function next() {
    h = Math.imul(h ^ (h >>> 16), 2246822507);
    h = Math.imul(h ^ (h >>> 13), 3266489909);
    h ^= h >>> 16;
    return (h >>> 0) / 4294967296;
  };
}
