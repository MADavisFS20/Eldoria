// One GameLocation tile -> one THREE.Group. Deterministic and re-derivable
// purely from the tile data the /api/tiles3d endpoint already exposes --
// no extra network round trip needed to redraw a chunk that's been seen
// before in this session.
import * as THREE from "../vendor/three.module.js";
import { tileRng } from "./tileRng.js";
import { biomeKitFor } from "./biomeKit.js";
import { building, portalMarker, hazardMarker, itemMarker } from "./propBuilder.js";
import { beingProxy } from "./beingProxy.js";

export const CHUNK_SIZE = 40;
const HALF = CHUNK_SIZE / 2;
const SAFE = HALF - 4; // keep props off the exact edges/exit lanes

const EDGE = {
  north: { x: 0, z: -HALF + 0.05, rot: 0 },
  south: { x: 0, z: HALF - 0.05, rot: 0 },
  east: { x: HALF - 0.05, z: 0, rot: Math.PI / 2 },
  west: { x: -HALF + 0.05, z: 0, rot: Math.PI / 2 },
};

function pickWeighted(rng, props) {
  const roll = rng();
  let acc = 0;
  for (const p of props) {
    acc += p.weight;
    if (roll <= acc) return p;
  }
  return props[props.length - 1];
}

export function buildChunk(tile) {
  const group = new THREE.Group();
  group.name = `chunk:${tile.id}`;
  const kit = biomeKitFor(tile.biome);
  const rng = tileRng(tile.id);

  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(CHUNK_SIZE, CHUNK_SIZE),
    new THREE.MeshLambertMaterial({ color: kit.ground })
  );
  ground.rotation.x = -Math.PI / 2;
  group.add(ground);

  if (tile.terrain === "WATERWAY") {
    const water = new THREE.Mesh(
      new THREE.PlaneGeometry(CHUNK_SIZE, CHUNK_SIZE),
      new THREE.MeshLambertMaterial({ color: 0x1a5c86, transparent: true, opacity: 0.85 })
    );
    water.rotation.x = -Math.PI / 2;
    water.position.y = 0.05;
    group.add(water);
  } else if (tile.terrain === "BRIDGE") {
    const plank = new THREE.Mesh(new THREE.BoxGeometry(6, 0.3, CHUNK_SIZE), new THREE.MeshLambertMaterial({ color: 0x7a5a3a }));
    plank.position.y = 0.15;
    group.add(plank);
  }

  for (const dir of tile.exits || []) {
    const e = EDGE[dir];
    if (!e) continue;
    const strip = new THREE.Mesh(new THREE.PlaneGeometry(6, 3), new THREE.MeshBasicMaterial({ color: 0xd9c18a }));
    strip.rotation.x = -Math.PI / 2;
    strip.rotation.z = e.rot;
    strip.position.set(e.x, 0.02, e.z);
    group.add(strip);
  }

  const isSettled = tile.population_tier === "CITY" || tile.population_tier === "COUNTRYSIDE";
  if (isSettled) {
    const count = tile.population_tier === "CITY" ? 6 : 3;
    for (let i = 0; i < count; i++) {
      const b = building(rng, tile.population_tier === "CITY" ? "large" : "small");
      b.position.set((rng() * 2 - 1) * SAFE, 0, (rng() * 2 - 1) * SAFE);
      b.rotation.y = rng() * Math.PI * 2;
      group.add(b);
    }
  } else if (tile.terrain === "LAND" && kit.props.length) {
    for (let i = 0; i < kit.density; i++) {
      const chosen = pickWeighted(rng, kit.props);
      const prop = chosen.build(rng);
      prop.position.set((rng() * 2 - 1) * SAFE, 0, (rng() * 2 - 1) * SAFE);
      prop.rotation.y = rng() * Math.PI * 2;
      group.add(prop);
    }
  }

  if (tile.portal_kind) {
    group.add(portalMarker(tile.portal_kind));
  }
  if (tile.hazard) {
    const marker = hazardMarker();
    marker.position.set(SAFE * 0.3, 0, SAFE * 0.3);
    group.add(marker);
  }

  const beings = [];
  for (const being of tile.beings || []) {
    const proxy = beingProxy(being);
    proxy.position.set((rng() * 2 - 1) * SAFE * 0.6, 0, (rng() * 2 - 1) * SAFE * 0.6);
    group.add(proxy);
    beings.push(proxy);
  }

  const items = [];
  for (const item of tile.items || []) {
    const marker = itemMarker();
    marker.position.set((rng() * 2 - 1) * SAFE * 0.5, 0, (rng() * 2 - 1) * SAFE * 0.5);
    marker.userData.item = item;
    group.add(marker);
    items.push(marker);
  }

  // `doors` is always empty for overworld chunks -- boundary crossing here
  // is automatic (crossing.js) rather than proximity+interact, but the
  // shape matches subrealm/roomScene.js's chunks so proximity.js can treat
  // either kind of "current pocket" the same way.
  return { group, beings, items, doors: [], tile };
}
