// Low-poly primitive builders. Every function takes a tileRng() stream and
// returns a THREE.Group -- pure, no side effects, no shared geometry state.
// This is the extensibility seam: a new prop type is one new function here,
// referenced from biomeKit.js's lookup table. Nothing else needs to change.
import * as THREE from "../vendor/three.module.js";

function lambert(color) {
  return new THREE.MeshLambertMaterial({ color });
}

export function tree(rng) {
  const g = new THREE.Group();
  const trunkH = 2 + rng() * 1.5;
  const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.22, trunkH, 6), lambert(0x6b4a2f));
  trunk.position.y = trunkH / 2;
  g.add(trunk);
  const foliageH = 2 + rng() * 1.5;
  const foliage = new THREE.Mesh(new THREE.ConeGeometry(1.1 + rng() * 0.4, foliageH, 7), lambert(0x2e7d32));
  foliage.position.y = trunkH + foliageH / 2 - 0.3;
  g.add(foliage);
  return g;
}

export function snowPine(rng) {
  const g = tree(rng);
  g.children[1].material = g.children[1].material.clone();
  g.children[1].material.color.set(0xdfe9ef);
  return g;
}

export function palm(rng) {
  const g = new THREE.Group();
  const h = 3 + rng() * 1.5;
  const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.2, h, 6), lambert(0x8a6b3f));
  trunk.position.y = h / 2;
  trunk.rotation.z = (rng() - 0.5) * 0.25;
  g.add(trunk);
  for (let i = 0; i < 5; i++) {
    const frond = new THREE.Mesh(new THREE.ConeGeometry(0.15, 1.6, 4), lambert(0x2e7d32));
    frond.position.y = h;
    frond.rotation.x = Math.PI / 2.2;
    frond.rotation.z = (i / 5) * Math.PI * 2;
    g.add(frond);
  }
  return g;
}

export function rock(rng) {
  const s = 0.5 + rng() * 0.8;
  const m = new THREE.Mesh(new THREE.DodecahedronGeometry(s, 0), lambert(0x8a8a86));
  m.position.y = s * 0.5;
  m.rotation.set(rng() * Math.PI, rng() * Math.PI, rng() * Math.PI);
  return m;
}

export function iceRock(rng) {
  const r = rock(rng);
  r.material = r.material.clone();
  r.material.color.set(0xcfe7f0);
  return r;
}

export function duneRock(rng) {
  const r = rock(rng);
  r.material = r.material.clone();
  r.material.color.set(0xc9a86a);
  return r;
}

export function cactus(rng) {
  const g = new THREE.Group();
  const h = 1.5 + rng();
  const body = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.3, h, 8), lambert(0x4c7a3f));
  body.position.y = h / 2;
  g.add(body);
  if (rng() < 0.6) {
    const arm = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.18, 0.8, 6), lambert(0x4c7a3f));
    arm.position.set(0.3, h * 0.6, 0);
    arm.rotation.z = Math.PI / 2.5;
    g.add(arm);
  }
  return g;
}

export function building(rng, size = "small") {
  const g = new THREE.Group();
  const w = size === "large" ? 5 + rng() * 2 : 3 + rng() * 1.5;
  const d = w * (0.8 + rng() * 0.3);
  const h = size === "large" ? 3.5 + rng() : 2.2 + rng() * 0.6;
  const body = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), lambert(0xc9b189));
  body.position.y = h / 2;
  g.add(body);
  const roofH = 1.2 + rng() * 0.5;
  const roof = new THREE.Mesh(new THREE.ConeGeometry(Math.max(w, d) * 0.75, roofH, 4), lambert(0x7a3b2e));
  roof.rotation.y = Math.PI / 4;
  roof.position.y = h + roofH / 2 - 0.2;
  g.add(roof);
  return g;
}

export function portalMarker(kind) {
  const g = new THREE.Group();
  if (kind === "DUNGEON") {
    const ring = new THREE.Mesh(new THREE.TorusGeometry(1.2, 0.15, 8, 16), new THREE.MeshBasicMaterial({ color: 0x8b1a1a }));
    ring.rotation.x = Math.PI / 2;
    ring.position.y = 0.05;
    g.add(ring);
  } else {
    const stalk = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.3, 4, 6), lambert(0x3f7a3f));
    stalk.position.y = 2;
    g.add(stalk);
  }
  return g;
}

export function hazardMarker() {
  const m = new THREE.Mesh(new THREE.ConeGeometry(0.4, 0.8, 4), new THREE.MeshBasicMaterial({ color: 0xd4af6a }));
  m.position.y = 0.4;
  return m;
}

export function itemMarker() {
  const g = new THREE.Group();
  const box = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.35, 0.35), new THREE.MeshBasicMaterial({ color: 0xd4af6a }));
  box.position.y = 0.6;
  g.add(box);
  return g;
}
