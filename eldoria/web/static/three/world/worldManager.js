// Multi-chunk streaming: chunks are positioned at their true world
// coordinates (tile.x/y * CHUNK_SIZE) instead of always sitting at the
// scene origin, so several tiles can be visible/loaded at once and walking
// across a tile boundary is just continuing to walk -- no teleport needed.
//
// Note on scale: at CHUNK_SIZE=40 the full 130x90 world spans about
// 5200x3600 units, comfortably inside float32 precision, so no
// origin-rebasing trick is needed even at full-map scope (Phase 3+).
//
// Not yet done (documented rather than half-built): cross-chunk
// InstancedMesh batching for trees/rocks. Per-chunk load/unload is simple
// because every mesh in a chunk's Group is disposed together; batching
// props into shared InstancedMeshes across chunks would need a separate
// pooling layer that doesn't fit that model cleanly. For now, streaming
// radius + the reduced per-biome densities in biomeKit.js keep the total
// object count bounded instead.
import { buildChunk, CHUNK_SIZE } from "./chunk.js";

export function tileWorldPosition(x, y) {
  return { x: x * CHUNK_SIZE, z: y * CHUNK_SIZE };
}

export function createWorldManager(scene) {
  const loaded = new Map(); // tile.id -> chunk data from buildChunk()

  function disposeChunk(chunk) {
    chunk.group.traverse((o) => {
      if (o.geometry) o.geometry.dispose();
      if (o.material) {
        if (Array.isArray(o.material)) o.material.forEach((m) => m.dispose());
        else o.material.dispose();
      }
    });
  }

  function sync(tiles) {
    const seen = new Set();
    for (const tile of tiles) {
      seen.add(tile.id);
      if (loaded.has(tile.id)) continue;
      const chunk = buildChunk(tile);
      const pos = tileWorldPosition(tile.x, tile.y);
      chunk.group.position.set(pos.x, 0, pos.z);
      scene.add(chunk.group);
      loaded.set(tile.id, chunk);
    }
    for (const [id, chunk] of loaded) {
      if (seen.has(id)) continue;
      scene.remove(chunk.group);
      disposeChunk(chunk);
      loaded.delete(id);
    }
  }

  function get(tileId) {
    return loaded.get(tileId);
  }

  function clear() {
    for (const chunk of loaded.values()) {
      scene.remove(chunk.group);
      disposeChunk(chunk);
    }
    loaded.clear();
  }

  return { sync, get, clear, size: () => loaded.size };
}
