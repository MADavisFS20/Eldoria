// Entrypoint: renderer/camera/light setup, main loop, orchestrates every
// module below. The 3D canvas is a spatial front door to the existing
// text-command engine -- it never reimplements game logic.
import * as THREE from "./vendor/three.module.js";
import { createWorldManager, tileWorldPosition } from "./world/worldManager.js";
import { buildRoomChunk } from "./subrealm/roomScene.js";
import { biomeKitFor } from "./world/biomeKit.js";
import { fetchTiles3d } from "./api3d.js";
import { sendGameCommand, onGameStateUpdate, isGameActive } from "./bridge.js";
import { createController } from "./player/controller.js";
import { attachCrossing } from "./interaction/crossing.js";
import { attachProximity } from "./interaction/proximity.js";

const STREAM_RADIUS = 2; // 5x5 tile window kept loaded around the player, overworld only

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

  const fpsEl = document.createElement("div");
  fpsEl.id = "scene3d-fps";
  fpsEl.style.cssText =
    "position:fixed;top:0.6rem;left:0.7rem;z-index:2;font-family:monospace;font-size:.7rem;" +
    "color:rgba(212,175,106,.8);background:rgba(18,20,26,.5);padding:.15rem .4rem;border-radius:4px;pointer-events:none;";
  document.body.appendChild(fpsEl);
  let fpsFrames = 0;
  let fpsElapsed = 0;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xbfe0a0);
  scene.fog = new THREE.Fog(0xbfe0a0, 25, 90);

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

  const world = createWorldManager(scene);
  let lastBiome = null;
  let mode = "overworld"; // or "subrealm" -- see onGameStateUpdate below
  let roomChunk = null;

  function applyAtmosphereFor(biomeName) {
    if (!biomeName || biomeName === lastBiome) return;
    lastBiome = biomeName;
    const kit = biomeKitFor(biomeName);
    scene.background.set(kit.sky);
    scene.fog.color.set(kit.sky);
  }

  function disposeGroup(group) {
    group.traverse((o) => {
      if (o.geometry) o.geometry.dispose();
      if (o.material) {
        if (Array.isArray(o.material)) o.material.forEach((m) => m.dispose());
        else o.material.dispose();
      }
    });
  }

  function loadRoom(roomData) {
    if (roomChunk) {
      scene.remove(roomChunk.group);
      disposeGroup(roomChunk.group);
    }
    roomChunk = buildRoomChunk(roomData);
    scene.add(roomChunk.group);
    player.position.set(0, 0, 0);
    applyAtmosphereFor(roomData.biome);
  }

  function loadOverworldAt(tiles, here) {
    world.sync(tiles);
    crossing.setCurrentTile(here);
    const pos = tileWorldPosition(here.x, here.y);
    player.position.set(pos.x, 0, pos.z);
    applyAtmosphereFor(here.biome);
  }

  function refreshOverworld() {
    fetchTiles3d({ radius: STREAM_RADIUS }).then((data) => {
      if (!data.tiles || !data.tiles.length) return;
      const here = data.tiles.find((t) => t.id === `${data.you.x}_${data.you.y}`) || data.tiles[0];
      loadOverworldAt(data.tiles, here);
    });
  }

  function refreshRoom() {
    fetchTiles3d({}).then((data) => {
      if (data.room) loadRoom(data.room);
    });
  }

  const controller = createController({ player, camera, canvas });
  const crossing = attachCrossing({
    player,
    controller,
    sendGameCommand,
    onSync: (tiles) => world.sync(tiles),
    streamRadius: STREAM_RADIUS,
  });
  const proximity = attachProximity({
    player,
    getCurrentChunk: () => {
      if (mode === "subrealm") return roomChunk;
      const tile = crossing.getCurrentTile();
      return tile ? world.get(tile.id) : null;
    },
    sendGameCommand,
  });

  onGameStateUpdate((log, state) => {
    const notable = (log || []).find((l) => l.style === "red");
    if (notable) showToast(notable.text, true);

    const wasSubrealm = mode === "subrealm";
    const nowSubrealm = !!(state && state.in_sub_realm);

    if (nowSubrealm && !wasSubrealm) {
      mode = "subrealm";
      world.clear();
      refreshRoom();
    } else if (!nowSubrealm && wasSubrealm) {
      mode = "overworld";
      if (roomChunk) {
        scene.remove(roomChunk.group);
        disposeGroup(roomChunk.group);
        roomChunk = null;
      }
      lastBiome = null; // force atmosphere refresh back on overworld biome
      refreshOverworld();
    } else if (nowSubrealm) {
      refreshRoom();
    } else {
      crossing.onCommandResult();
    }
  });

  function tryInitialLoad() {
    if (!isGameActive()) {
      setTimeout(tryInitialLoad, 300);
      return;
    }
    fetchTiles3d({ radius: STREAM_RADIUS }).then((data) => {
      if (data.room) {
        mode = "subrealm";
        loadRoom(data.room);
      } else if (data.tiles && data.tiles.length) {
        const here = data.tiles.find((t) => t.id === `${data.you.x}_${data.you.y}`) || data.tiles[0];
        loadOverworldAt(data.tiles, here);
      }
    });
  }
  tryInitialLoad();

  const clock = new THREE.Clock();
  function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(0.05, clock.getDelta());
    controller.update(dt);
    if (mode === "overworld") {
      crossing.update();
      const current = crossing.getCurrentTile();
      if (current) applyAtmosphereFor(current.biome);
    }
    proximity.update();
    renderer.render(scene, camera);

    fpsFrames += 1;
    fpsElapsed += dt;
    if (fpsElapsed >= 0.5) {
      const fps = Math.round(fpsFrames / fpsElapsed);
      const objectCount = mode === "subrealm" ? (roomChunk ? roomChunk.group.children.length : 0) : world.size();
      fpsEl.textContent = `${fps} fps · ${mode} · ${objectCount} ${mode === "subrealm" ? "objects" : "chunks"}`;
      fpsFrames = 0;
      fpsElapsed = 0;
    }
  }
  animate();

  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
}
