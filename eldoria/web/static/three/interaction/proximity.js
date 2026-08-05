// Walking up to a being/item/portal/door shows a prompt that fires the
// exact same text command the manual command form would send -- full name
// (or direction, for doors), never a cached index (commands.py resolves
// by live substring match, and list order isn't stable across
// defeat/respawn).
//
// Only ever checks the player's actual CURRENT tile/room, matching the
// server: session.current_beings()/current_items() only ever reflect that
// spot, so a being sitting in an already-streamed neighboring tile simply
// isn't interactable yet -- faithful to how "attack"/"talk" already worked.
import * as THREE from "../vendor/three.module.js";
import { tileWorldPosition } from "../world/worldManager.js";

const INTERACT_RADIUS = 3.2;
const _tmp = new THREE.Vector3();

function verbFor(being) {
  return being.disposition === "HOSTILE" ? "attack" : "talk";
}

function doorLabel(direction) {
  if (direction === "leave") return "Leave";
  if (direction.startsWith("passage_to_")) return "Go through the passage";
  return `Go ${direction}`;
}

export function attachProximity({ player, getCurrentChunk, sendGameCommand }) {
  let promptEl = null;
  let target = null;

  function ensurePrompt() {
    if (promptEl) return promptEl;
    promptEl = document.createElement("div");
    promptEl.id = "scene3d-prompt";
    promptEl.style.cssText =
      "position:fixed;bottom:18%;left:50%;transform:translate(-50%,0);padding:.4rem .9rem;" +
      "border-radius:6px;font-family:Georgia,serif;font-size:.95rem;z-index:5;" +
      "background:rgba(18,20,26,.85);color:#d4af6a;border:1px solid #d4af6a;cursor:pointer;display:none;";
    document.body.appendChild(promptEl);
    promptEl.addEventListener("click", interact);
    window.addEventListener("keydown", (e) => {
      if (e.key.toLowerCase() === "e") interact();
    });
    return promptEl;
  }

  function interact() {
    if (!target) return;
    if (target.kind === "being") {
      sendGameCommand(`${verbFor(target.data)} ${target.name}`);
    } else if (target.kind === "item") {
      sendGameCommand(`take ${target.name}`);
    } else if (target.kind === "portal") {
      sendGameCommand("enter");
    } else if (target.kind === "door") {
      sendGameCommand(target.direction);
    }
  }

  function update() {
    const chunk = getCurrentChunk();
    const p = ensurePrompt();
    if (!chunk) {
      p.style.display = "none";
      target = null;
      return;
    }

    let closest = null;
    let closestDist = INTERACT_RADIUS;

    for (const proxy of chunk.beings || []) {
      proxy.getWorldPosition(_tmp);
      const d = player.position.distanceTo(_tmp);
      if (d < closestDist) {
        closestDist = d;
        closest = { kind: "being", name: proxy.userData.being.name, data: proxy.userData.being };
      }
    }
    for (const proxy of chunk.items || []) {
      proxy.getWorldPosition(_tmp);
      const d = player.position.distanceTo(_tmp);
      if (d < closestDist) {
        closestDist = d;
        closest = { kind: "item", name: proxy.userData.item.name };
      }
    }
    for (const proxy of chunk.doors || []) {
      proxy.getWorldPosition(_tmp);
      const d = player.position.distanceTo(_tmp);
      if (d < closestDist) {
        closestDist = d;
        closest = { kind: "door", direction: proxy.userData.door.direction };
      }
    }
    if (chunk.tile && chunk.tile.portal_kind) {
      const origin = tileWorldPosition(chunk.tile.x, chunk.tile.y);
      const d = Math.hypot(player.position.x - origin.x, player.position.z - origin.z);
      if (d < closestDist) {
        closestDist = d;
        closest = { kind: "portal", name: "Enter" };
      }
    }

    target = closest;
    if (target) {
      let label;
      if (target.kind === "being") label = `${verbFor(target.data).replace(/^./, (c) => c.toUpperCase())} ${target.name}`;
      else if (target.kind === "item") label = `Take ${target.name}`;
      else if (target.kind === "door") label = doorLabel(target.direction);
      else label = "Enter";
      p.textContent = `[E] ${label}`;
      p.style.display = "block";
    } else {
      p.style.display = "none";
    }
  }

  return { update };
}
