// Entrypoint: renderer/camera/light setup, main loop, orchestrates every
// module below. The 3D canvas is a spatial front door to the existing
// text-command engine -- it never reimplements game logic.
import * as THREE from "./vendor/three.module.js";
import { buildChunk, CHUNK_SIZE } from "./world/chunk.js";
import { fetchTiles3d } from "./api3d.js";
import { sendGameCommand, onGameStateUpdate, isGameActive } from "./bridge.js";
import { createController } from "./player/controller.js";
import { attachCrossing } from "./interaction/crossing.js";
import { attachProximity } from "./interaction/proximity.js";

const canvas = document.getElementById("scene3d");
if (canvas) {
  const toggleBtn = document.getElementById("hud-toggle-btn");
  const gameEl = document.getElementById("game");
  if (toggleBtn && gameEl) {
    toggleBtn.addEventListener("click", () => gameEl.classList.toggle("hud-collapsed"));
  }

  let toastEl = null;
  function showToast(text, danger) {
    if (!toastEl) {
      toastEl = document.createElement("div");
      toastEl.id = "scene3d-toast";
      toastEl.style.cssText =
        "position:fixed;top:14%;left:50%;transform:translate(-50%,0);padding:.5rem 1rem;" +
        "border-radius:6px;font-family:Georgia,serif;font-size:.95rem;z-index:5;pointer-events:none;" +
        "opacity:0;transition:opacity .25s;background:rgba(20,10,10,.85);color:#f0d9a0;border:1px solid #7a3b2e;";
      document.body.appendChild(toastEl);
    }
    toastEl.textContent = text;
    toastEl.style.borderColor = danger ? "#b43c3c" : "#7a3b2e";
    toastEl.style.opacity = "1";
    clearTimeout(toastEl._hideTimer);
    toastEl._hideTimer = setTimeout(() => { toastEl.style.opacity = "0"; }, 2200);
  }

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xbfe0a0);
  scene.fog = new THREE.Fog(0xbfe0a0, 20, 60);

  const camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 500);

  scene.add(new THREE.HemisphereLight(0xffffff, 0x445533, 1.0));
  const sun = new THREE.DirectionalLight(0xfff2d0, 1.1);
  sun.position.set(15, 25, 10);
  scene.add(sun);

  const player = new THREE.Group();
  const playerMesh = new THREE.Mesh(
    new THREE.CapsuleGeometry(0.4, 1.1, 4, 8),
    new THREE.MeshLambertMaterial({ color: 0xd4af6a })
  );
  playerMesh.position.y = 0.95;
  player.add(playerMesh);
  scene.add(player);

  let currentChunk = null;

  function loadChunk(tile) {
    if (currentChunk) {
      scene.remove(currentChunk.group);
      currentChunk.group.traverse((o) => {
        if (o.geometry) o.geometry.dispose();
        if (o.material) o.material.dispose();
      });
    }
    currentChunk = buildChunk(tile);
    scene.add(currentChunk.group);
    scene.background.set(0xbfe0a0);
    scene.fog.color.set(0xbfe0a0);
    return currentChunk;
  }

  const controller = createController({ player, camera, canvas });
  const crossing = attachCrossing({
    player,
    controller,
    sendGameCommand,
    onChunkChange: loadChunk,
    onToast: showToast,
  });
  const proximity = attachProximity({
    player,
    getChunk: () => currentChunk,
    sendGameCommand,
  });

  onGameStateUpdate((log) => crossing.onCommandResult(log));

  function tryInitialLoad() {
    if (!isGameActive()) {
      setTimeout(tryInitialLoad, 300);
      return;
    }
    fetchTiles3d({ radius: 1 }).then((data) => {
      if (!data.tiles || !data.tiles.length) return;
      const here = data.tiles.find((t) => t.id === `${data.you.x}_${data.you.y}`) || data.tiles[0];
      crossing.setCurrentTile(here);
      player.position.set(0, 0, 0);
      loadChunk(here);
    });
  }
  tryInitialLoad();

  const clock = new THREE.Clock();
  function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(0.05, clock.getDelta());
    controller.update(dt);
    crossing.update();
    proximity.update();
    renderer.render(scene, camera);
  }
  animate();

  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
}
