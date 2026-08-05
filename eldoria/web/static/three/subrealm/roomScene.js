// Discrete room-to-room 3D view for dungeons/sky-realms. Sub-realms are
// room GRAPHS, not grids (see eldoria/models/sub_realm.py) -- there's no
// spatial relationship between rooms to stream, so only ever one room is
// built at a time, replaced wholesale on every crossing. Traversal is
// proximity+interact through a door marker (see interaction/proximity.js's
// `doors` handling), not continuous walk-to-the-edge like the overworld --
// commands.move() skips all hazard/crime/encounter rolls inside a
// sub-realm, so there's no "confirm before showing arrival" concern here.
import * as THREE from "../vendor/three.module.js";
import { tileRng } from "../world/tileRng.js";
import { biomeKitFor } from "../world/biomeKit.js";
import { beingProxy } from "../world/beingProxy.js";
import { itemMarker } from "../world/propBuilder.js";

const BASE_SIZE = 22;
const BOSS_SIZE = 32;
const WALL_HEIGHT = 6;

const CARDINAL_WALL = {
  north: { x: 0, z: -1, axis: "z" },
  south: { x: 0, z: 1, axis: "z" },
  east: { x: 1, z: 0, axis: "x" },
  west: { x: -1, z: 0, axis: "x" },
};
const CORNER_ANGLES = [Math.PI / 4, (3 * Math.PI) / 4, (5 * Math.PI) / 4, (7 * Math.PI) / 4];

function doorFrame(color) {
  const g = new THREE.Group();
  const postMat = new THREE.MeshLambertMaterial({ color: 0x5a4632 });
  const postGeo = new THREE.BoxGeometry(0.4, 3.4, 0.4);
  const left = new THREE.Mesh(postGeo, postMat);
  left.position.set(-1.1, 1.7, 0);
  g.add(left);
  const right = new THREE.Mesh(postGeo, postMat);
  right.position.set(1.1, 1.7, 0);
  g.add(right);
  const lintel = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.4, 0.4), postMat);
  lintel.position.set(0, 3.4, 0);
  g.add(lintel);
  const glow = new THREE.Mesh(
    new THREE.PlaneGeometry(2, 3.2),
    new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.25, side: THREE.DoubleSide })
  );
  glow.position.set(0, 1.6, 0);
  g.add(glow);
  return g;
}

function leaveSigil() {
  const g = new THREE.Mesh(
    new THREE.RingGeometry(1.0, 1.6, 16),
    new THREE.MeshBasicMaterial({ color: 0x6fae4a, transparent: true, opacity: 0.5, side: THREE.DoubleSide })
  );
  g.rotation.x = -Math.PI / 2;
  return g;
}

export function buildRoomChunk(room) {
  const size = room.is_boss_room ? BOSS_SIZE : BASE_SIZE;
  const half = size / 2;
  const kit = biomeKitFor(room.biome);
  const rng = tileRng(room.id);

  const group = new THREE.Group();
  group.name = `room:${room.id}`;

  const floorColor = room.is_boss_room ? 0x2a2016 : kit.ground;
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(size, size), new THREE.MeshLambertMaterial({ color: floorColor }));
  floor.rotation.x = -Math.PI / 2;
  group.add(floor);

  const ceiling = new THREE.Mesh(
    new THREE.PlaneGeometry(size, size),
    new THREE.MeshLambertMaterial({ color: 0x1a1712, side: THREE.BackSide })
  );
  ceiling.rotation.x = -Math.PI / 2;
  ceiling.position.y = WALL_HEIGHT;
  group.add(ceiling);

  const wallMat = new THREE.MeshLambertMaterial({ color: room.is_boss_room ? 0x3a2a20 : 0x554433 });
  const wallGeoNS = new THREE.BoxGeometry(size, WALL_HEIGHT, 0.5);
  const wallGeoEW = new THREE.BoxGeometry(0.5, WALL_HEIGHT, size);

  const north = new THREE.Mesh(wallGeoNS, wallMat);
  north.position.set(0, WALL_HEIGHT / 2, -half);
  group.add(north);
  const south = new THREE.Mesh(wallGeoNS, wallMat);
  south.position.set(0, WALL_HEIGHT / 2, half);
  group.add(south);
  const east = new THREE.Mesh(wallGeoEW, wallMat);
  east.position.set(half, WALL_HEIGHT / 2, 0);
  group.add(east);
  const west = new THREE.Mesh(wallGeoEW, wallMat);
  west.position.set(-half, WALL_HEIGHT / 2, 0);
  group.add(west);

  if (room.is_boss_room) {
    const glow = new THREE.PointLight(0xff6a3a, 1.2, size * 1.2);
    glow.position.set(0, WALL_HEIGHT - 1, 0);
    group.add(glow);
  }

  const doors = [];
  const cardinalDirs = [];
  const extraDirs = [];
  for (const dir of room.exits || []) {
    if (CARDINAL_WALL[dir]) cardinalDirs.push(dir);
    else extraDirs.push(dir);
  }
  for (const dir of cardinalDirs) {
    const wall = CARDINAL_WALL[dir];
    const frame = doorFrame(0xd4af6a);
    frame.position.set(wall.x * half, 0, wall.z * half);
    if (wall.axis === "x") frame.rotation.y = Math.PI / 2;
    frame.userData.door = { direction: dir };
    group.add(frame);
    doors.push(frame);
  }
  // Synthetic "passage_to_N" exits (rare -- only rooms with degree above the
  // 6 compass/vertical directions get these) go in whichever corners the
  // cardinal doors didn't already claim.
  extraDirs.forEach((dir, i) => {
    const angle = CORNER_ANGLES[i % CORNER_ANGLES.length];
    const frame = doorFrame(0xd4af6a);
    frame.position.set(Math.cos(angle) * half * 0.98, 0, Math.sin(angle) * half * 0.98);
    frame.rotation.y = angle + Math.PI / 2;
    frame.userData.door = { direction: dir };
    group.add(frame);
    doors.push(frame);
  });

  if (room.is_entry_room) {
    const sigil = leaveSigil();
    sigil.position.set(0, 0.05, half - 3);
    sigil.userData.door = { direction: "leave" };
    group.add(sigil);
    doors.push(sigil);
  }

  const beings = [];
  for (const being of room.beings || []) {
    const proxy = beingProxy(being);
    proxy.position.set((rng() * 2 - 1) * (half - 3), 0, (rng() * 2 - 1) * (half - 3));
    group.add(proxy);
    beings.push(proxy);
  }

  const items = [];
  for (const item of room.items || []) {
    const marker = itemMarker();
    marker.position.set((rng() * 2 - 1) * (half - 3), 0, (rng() * 2 - 1) * (half - 3));
    marker.userData.item = item;
    group.add(marker);
    items.push(marker);
  }

  return { group, beings, items, doors, room };
}
