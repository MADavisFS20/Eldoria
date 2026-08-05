import { getSessionId } from "./bridge.js";

export async function fetchTiles3d({ cx, cy, radius = 3 } = {}) {
  const sid = getSessionId();
  if (!sid) return { tiles: [], you: { x: 0, y: 0 } };
  const params = new URLSearchParams();
  if (cx !== undefined) params.set("cx", cx);
  if (cy !== undefined) params.set("cy", cy);
  params.set("radius", radius);
  const res = await fetch(`/api/tiles3d/${sid}?${params.toString()}`);
  if (!res.ok) return { tiles: [], you: { x: 0, y: 0 } };
  return res.json();
}
