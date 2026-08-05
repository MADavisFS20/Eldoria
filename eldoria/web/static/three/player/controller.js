// Third-person WASD/touch-joystick + drag-look controller. Purely local
// movement within the current chunk/room -- never touches the network.
// Tile-boundary crossing is detected and handled separately (see
// interaction/crossing.js).
import * as THREE from "../vendor/three.module.js";

const SPEED = 6; // units/sec
const CAM_BACK = 6.5;
const CAM_UP = 3.2;
const JOYSTICK_RADIUS = 44; // px, knob travel range

function createJoystick() {
  const base = document.createElement("div");
  base.id = "scene3d-joystick-base";
  base.style.cssText =
    "position:fixed;left:22px;bottom:22px;width:100px;height:100px;border-radius:50%;" +
    "background:rgba(18,20,26,.35);border:1px solid rgba(212,175,106,.5);z-index:4;touch-action:none;";
  const knob = document.createElement("div");
  knob.id = "scene3d-joystick-knob";
  knob.style.cssText =
    "position:absolute;left:50%;top:50%;width:44px;height:44px;margin:-22px;border-radius:50%;" +
    "background:rgba(212,175,106,.55);border:1px solid rgba(212,175,106,.9);";
  base.appendChild(knob);
  document.body.appendChild(base);

  const state = { x: 0, z: 0, active: false };
  let pointerId = null;
  let originX = 0, originY = 0;

  function setKnob(dx, dz) {
    knob.style.transform = `translate(${dx}px, ${dz}px)`;
  }

  base.addEventListener("pointerdown", (e) => {
    pointerId = e.pointerId;
    state.active = true;
    const rect = base.getBoundingClientRect();
    originX = rect.left + rect.width / 2;
    originY = rect.top + rect.height / 2;
    base.setPointerCapture(pointerId);
  });
  base.addEventListener("pointermove", (e) => {
    if (e.pointerId !== pointerId || !state.active) return;
    let dx = e.clientX - originX;
    let dy = e.clientY - originY;
    const dist = Math.hypot(dx, dy);
    if (dist > JOYSTICK_RADIUS) {
      dx = (dx / dist) * JOYSTICK_RADIUS;
      dy = (dy / dist) * JOYSTICK_RADIUS;
    }
    setKnob(dx, dy);
    state.x = dx / JOYSTICK_RADIUS;
    state.z = dy / JOYSTICK_RADIUS;
  });
  function release(e) {
    if (e.pointerId !== pointerId) return;
    state.active = false;
    state.x = 0;
    state.z = 0;
    pointerId = null;
    setKnob(0, 0);
  }
  base.addEventListener("pointerup", release);
  base.addEventListener("pointercancel", release);

  return state;
}

export function createController({ player, camera, canvas }) {
  const keys = new Set();
  window.addEventListener("keydown", (e) => keys.add(e.key.toLowerCase()));
  window.addEventListener("keyup", (e) => keys.delete(e.key.toLowerCase()));

  const joystick = createJoystick();

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
    if (joystick.active && (Math.abs(joystick.x) > 0.05 || Math.abs(joystick.z) > 0.05)) {
      return { x: joystick.x, z: joystick.z, magnitude: Math.min(1, Math.hypot(joystick.x, joystick.z)) };
    }
    let x = 0, z = 0;
    if (keys.has("w") || keys.has("arrowup")) z -= 1;
    if (keys.has("s") || keys.has("arrowdown")) z += 1;
    if (keys.has("a") || keys.has("arrowleft")) x -= 1;
    if (keys.has("d") || keys.has("arrowright")) x += 1;
    if (keys.has("q")) yaw += 2.4 * 0.016;
    return { x, z, magnitude: 1 };
  }

  function update(dt) {
    if (!locked) {
      const { x, z, magnitude } = desiredMove();
      if (x !== 0 || z !== 0) {
        const len = Math.hypot(x, z) || 1;
        const nx = x / len, nz = z / len;
        const sinY = Math.sin(yaw), cosY = Math.cos(yaw);
        const worldX = nx * cosY - nz * sinY;
        const worldZ = nx * sinY + nz * cosY;
        player.position.x += worldX * SPEED * magnitude * dt;
        player.position.z += worldZ * SPEED * magnitude * dt;
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
