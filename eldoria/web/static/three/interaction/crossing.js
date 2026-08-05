// Tile-boundary crossing. Movement side effects (hazard rolls, street crime,
// ferry/balloon encounters, the scripted time-traveler intercept) all live
// in commands.move() server-side -- this module never simulates a crossing,
// it only detects the boundary, soft-locks input, and fires the real
// "north"/"south"/"east"/"west" command through bridge.js.
//
// Phase 2: chunks are positioned at true world coordinates (see
// worldManager.js), so once a crossing is confirmed the player is already
// standing at the contiguous edge of the next tile -- no repositioning
// needed, unlike Phase 1's single-chunk-at-origin model.
import { CHUNK_SIZE } from "../world/chunk.js";
import { tileWorldPosition } from "../world/worldManager.js";
import { fetchTiles3d } from "../api3d.js";

const HALF = CHUNK_SIZE / 2;
const MARGIN = 1.5;

const DIR_VECTOR = {
  north: { dx: 0, dz: -1 },
  south: { dx: 0, dz: 1 },
  east: { dx: 1, dz: 0 },
  west: { dx: -1, dz: 0 },
};

export function attachCrossing({ player, controller, sendGameCommand, onSync, onToast, streamRadius = 3 }) {
  let tile = null; // the tile the player is currently standing on
  let tileOrigin = { x: 0, z: 0 }; // that tile's world-space center

  function setCurrentTile(newTile) {
    tile = newTile;
    tileOrigin = tileWorldPosition(newTile.x, newTile.y);
  }

  async function crossTo(direction) {
    if (controller.isLocked() || !tile) return;
    if (!tile.exits || !tile.exits.includes(direction)) return;
    controller.setLocked(true);
    await sendGameCommand(direction);
  }

  function onCommandResult(log) {
    const notable = (log || []).find((l) => l.style === "red");
    if (notable && onToast) onToast(notable.text, true);

    fetchTiles3d({ radius: streamRadius }).then((data) => {
      controller.setLocked(false);
      if (!data.tiles || !data.tiles.length) return;
      const here = data.tiles.find((t) => t.id === `${data.you.x}_${data.you.y}`);
      onSync(data.tiles);
      if (here && (!tile || here.id !== tile.id)) {
        setCurrentTile(here);
      }
      // If the crossing was blocked server-side (water without a boat, a
      // dead end, etc.) `tile` stays the same and the player remains
      // clamped at the boundary from update() below -- no illusion of
      // arrival.
    });
  }

  function update() {
    if (controller.isLocked() || !tile) return;
    const p = player.position;
    const localX = p.x - tileOrigin.x;
    const localZ = p.z - tileOrigin.z;
    for (const dir in DIR_VECTOR) {
      const vec = DIR_VECTOR[dir];
      const edgeCoord = vec.dx !== 0 ? localX * vec.dx : localZ * vec.dz;
      if (edgeCoord > HALF - MARGIN) {
        if (tile.exits && tile.exits.includes(dir)) {
          crossTo(dir);
        } else if (vec.dx !== 0) {
          p.x = tileOrigin.x + (HALF - MARGIN) * vec.dx;
        } else {
          p.z = tileOrigin.z + (HALF - MARGIN) * vec.dz;
        }
        return;
      }
    }
  }

  return { update, setCurrentTile, onCommandResult, getCurrentTile: () => tile };
}
