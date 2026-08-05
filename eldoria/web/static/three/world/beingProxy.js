// Placeholder mesh for a creature/NPC, keyed off `kind`/`disposition` strings
// from the API -- never a hardcoded name, so new being types render with a
// sensible default (a capsule) without any code change here.
import * as THREE from "../vendor/three.module.js";

const COLOR_BY_DISPOSITION = { HOSTILE: 0xb43c3c, PASSIVE: 0x3c7ab4 };

export function beingProxy(being) {
  const g = new THREE.Group();
  const color = COLOR_BY_DISPOSITION[being.disposition] ?? 0x999999;
  const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.4, 1.1, 4, 8), new THREE.MeshLambertMaterial({ color }));
  body.position.y = 0.95;
  g.add(body);
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.32, 8, 8), new THREE.MeshLambertMaterial({ color: 0xe0c9a6 }));
  head.position.y = 1.75;
  g.add(head);
  g.userData.being = being;
  return g;
}
