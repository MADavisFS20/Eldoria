// Third-person WASD + drag-look controller. Purely local movement within
// the current chunk -- never touches the network. Tile-boundary crossing
// is detected and handled separately (see interaction/crossing.js).
import * as THREE from "../vendor/three.module.js";

const SPEED = 6; // units/sec
const CAM_BACK = 6.5;
const CAM_UP = 3.2;

export function createController({ player, camera, canvas }) {
  const keys = new Set();
  window.addEventListener("keydown", (e) => keys.add(e.key.toLowerCase()));
  window.addEventListener("keyup", (e) => keys.delete(e.key.toLowerCase()));

  let yaw = Math.PI; // face into the chunk from the default spawn orientation
  let dragging = false;
  let lastX = 0;
  canvas.addEventListener("pointerdown", (e) => { dragging = true; lastX = e.clientX; });
  window.addEventListener("pointerup", () => { dragging = false; });
  window.addEventListener("pointermove", (e) => {
    if (!dragging) return;
    const dx = e.clientX - lastX;
    lastX = e.clientX;
    yaw -= dx * 0.005;
  });

  let locked = false;

  function desiredMove() {
    let x = 0, z = 0;
    if (keys.has("w") || keys.has("arrowup")) z -= 1;
    if (keys.has("s") || keys.has("arrowdown")) z += 1;
    if (keys.has("a") || keys.has("arrowleft")) x -= 1;
    if (keys.has("d") || keys.has("arrowright")) x += 1;
    if (keys.has("q")) yaw += 2.4 * 0.016;
    return { x, z };
  }

  function update(dt) {
    if (!locked) {
      const { x, z } = desiredMove();
      if (x !== 0 || z !== 0) {
        const len = Math.hypot(x, z) || 1;
        const nx = x / len, nz = z / len;
        const sinY = Math.sin(yaw), cosY = Math.cos(yaw);
        const worldX = nx * cosY - nz * sinY;
        const worldZ = nx * sinY + nz * cosY;
        player.position.x += worldX * SPEED * dt;
        player.position.z += worldZ * SPEED * dt;
        player.rotation.y = Math.atan2(worldX, worldZ);
      }
    }

    const camX = player.position.x - Math.sin(yaw) * CAM_BACK;
    const camZ = player.position.z - Math.cos(yaw) * CAM_BACK;
    camera.position.set(camX, player.position.y + CAM_UP, camZ);
    camera.lookAt(player.position.x, player.position.y + 1.2, player.position.z);
  }

  return {
    update,
    setLocked: (v) => { locked = v; },
    isLocked: () => locked,
  };
}
