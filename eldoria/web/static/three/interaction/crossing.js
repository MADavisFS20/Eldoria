// Tile-boundary crossing. Movement side effects (hazard rolls, street crime,
// ferry/balloon encounters, the scripted time-traveler intercept) all live
// in commands.move() server-side -- this module never simulates a crossing,
// it only detects the boundary, soft-locks input, and fires the real
// "north"/"south"/"east"/"west" command through bridge.js.
import { CHUNK_SIZE } from "../world/chunk.js";
import { fetchTiles3d } from "../api3d.js";

const HALF = CHUNK_SIZE / 2;
const MARGIN = 1.5;

const DIR_VECTOR = {
  north: { dx: 0, dz: -1 },
  south: { dx: 0, dz: 1 },
  east: { dx: 1, dz: 0 },
  west: { dx: -1, dz: 0 },
};

function entryPositionFor(direction) {
  const vec = DIR_VECTOR[direction];
  const inset = HALF - MARGIN * 2;
  return { x: -vec.dx * inset, z: -vec.dz * inset };
}

export function attachCrossing({ player, controller, sendGameCommand, onChunkChange, onToast }) {
  let tile = null;
  let lastDirection = null;

  function setCurrentTile(newTile) {
    tile = newTile;
  }

  async function crossTo(direction) {
    if (controller.isLocked() || !tile) return;
    if (!tile.exits || !tile.exits.includes(direction)) return;
    lastDirection = direction;
    controller.setLocked(true);
    await sendGameCommand(direction);
  }

  function onCommandResult(log) {
    const notable = (log || []).find((l) => l.style === "red");
    if (notable && onToast) onToast(notable.text, true);

    fetchTiles3d({ radius: 1 }).then((data) => {
      controller.setLocked(false);
      if (!data.tiles || !data.tiles.length) return;
      const here = data.tiles.find((t) => t.id === `${data.you.x}_${data.you.y}`);
      if (!here) return;
      const moved = !tile || here.id !== tile.id;
      setCurrentTile(here);
      onChunkChange(here);
      if (moved && lastDirection) {
        const entry = entryPositionFor(lastDirection);
        player.position.set(entry.x, player.position.y, entry.z);
      } else if (!moved) {
        // Crossing was blocked server-side (e.g. water without a boat) --
        // stay put at the boundary rather than implying arrival.
      }
      lastDirection = null;
    });
  }

  function update() {
    if (controller.isLocked() || !tile) return;
    const p = player.position;
    for (const dir in DIR_VECTOR) {
      const vec = DIR_VECTOR[dir];
      const edgeCoord = vec.dx !== 0 ? p.x * vec.dx : p.z * vec.dz;
      if (edgeCoord > HALF - MARGIN) {
        if (tile.exits && tile.exits.includes(dir)) {
          crossTo(dir);
        } else if (vec.dx !== 0) {
          p.x = (HALF - MARGIN) * vec.dx;
        } else {
          p.z = (HALF - MARGIN) * vec.dz;
        }
        return;
      }
    }
  }

  return { update, setCurrentTile, onCommandResult };
}
