// The ONLY module allowed to touch window.__eldoria (exposed by app.js).
// Every other module goes through here so app.js stays the single owner of
// sessionId/latestState and its own log/side-panel rendering.
export function isGameActive() {
  return !!(window.__eldoria && window.__eldoria.isGameActive());
}

export function getSessionId() {
  return window.__eldoria ? window.__eldoria.getSessionId() : null;
}

export function getLatestState() {
  return window.__eldoria ? window.__eldoria.getState() : null;
}

export async function sendGameCommand(text, opts) {
  if (!window.__eldoria) return;
  await window.__eldoria.sendCommand(text, opts);
}

export function onGameStateUpdate(cb) {
  if (window.__eldoria) window.__eldoria.onStateUpdate(cb);
}
