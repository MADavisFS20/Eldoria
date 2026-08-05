(() => {
  "use strict";

  const el = (id) => document.getElementById(id);

  let sessionId = null;
  let latestState = null;
  let selectedRace = null;
  let selectedClass = null;
  const stateListeners = [];

  // --- Character creation -------------------------------------------------

  async function loadMeta() {
    const res = await fetch("/api/meta");
    const meta = await res.json();

    const raceGrid = el("race-grid");
    meta.races.forEach((r) => {
      const card = document.createElement("div");
      card.className = "option-card";
      card.innerHTML = `<div class="name">${r.display_name}</div><div class="desc">${r.lore}</div>`;
      card.addEventListener("click", () => {
        selectedRace = r.id;
        [...raceGrid.children].forEach((c) => c.classList.remove("selected"));
        card.classList.add("selected");
        updateBeginState();
      });
      raceGrid.appendChild(card);
    });

    const classGrid = el("class-grid");
    meta.classes.forEach((c) => {
      const card = document.createElement("div");
      card.className = "option-card";
      card.innerHTML = `<div class="name">${c.display_name}</div><div class="desc">${c.description}</div>`;
      card.addEventListener("click", () => {
        selectedClass = c.id;
        [...classGrid.children].forEach((el2) => el2.classList.remove("selected"));
        card.classList.add("selected");
        updateBeginState();
      });
      classGrid.appendChild(card);
    });
  }

  function updateBeginState() {
    el("begin-btn").disabled = !(selectedRace && selectedClass);
  }

  async function beginGame() {
    const name = el("name-input").value.trim() || "Wanderer";
    const res = await fetch("/api/new_game", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, race: selectedRace, character_class: selectedClass }),
    });
    if (!res.ok) {
      alert("Could not start a new game.");
      return;
    }
    const data = await res.json();
    enterGame(data);
  }

  async function continueGame() {
    const saved = localStorage.getItem("eldoria_session_id");
    if (!saved) {
      alert("No previous game found on this device.");
      return;
    }
    const res = await fetch("/api/continue_game", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: saved }),
    });
    if (!res.ok) {
      alert("No save found for the previous game.");
      return;
    }
    const data = await res.json();
    data.session_id = saved;
    enterGame(data);
  }

  let panelsInitialized = false;

  function enterGame(data) {
    sessionId = data.session_id;
    localStorage.setItem("eldoria_session_id", sessionId);
    el("creation").classList.add("hidden");
    el("game").classList.remove("hidden");
    appendLog(data.log);
    latestState = data.state;
    renderSidePanel();
    renderMap();
    if (!panelsInitialized) {
      setupHorizontalResize();
      setupVerticalResize();
      panelsInitialized = true;
    }
    el("command-input").focus();
  }

  // --- Log rendering --------------------------------------------------------

  function appendLog(lines) {
    const panel = el("log-panel");
    for (const { style, text } of lines) {
      const div = document.createElement("div");
      div.className = `line style-${style}`;
      div.textContent = text;
      panel.appendChild(div);
    }
    panel.scrollTop = panel.scrollHeight;
  }

  // --- Side panel (character / inventory) ------------------------------------

  function bar(current, max, cls) {
    const pct = max > 0 ? Math.max(0, Math.min(100, (current / max) * 100)) : 0;
    return `<div class="bar-track"><div class="bar-fill ${cls}" style="width:${pct}%"></div></div>`;
  }

  function renderSidePanel() {
    if (!latestState) return;
    const c = latestState.character;

    const charHtml = `
      <h2>${c.name} <span style="color:var(--text-dim);font-weight:normal">Lv${c.level}</span></h2>
      <div class="stat-row"><span>${c.race} ${c.character_class}</span><span>${c.subclass ? "[" + c.subclass + "]" : ""}</span></div>
      <div class="stat-row"><span>Reputation</span><span>${c.reputation_title} (${c.reputation})</span></div>
      <div class="stat-row"><span>HP</span><span>${c.current_health}/${c.max_health}</span></div>
      ${bar(c.current_health, c.max_health, "hp")}
      <div class="stat-row"><span>Stamina</span><span>${c.current_stamina}/${c.max_stamina}</span></div>
      ${bar(c.current_stamina, c.max_stamina, "sp")}
      <div class="stat-row"><span>XP</span><span>${c.experience}/${c.xp_needed}</span></div>
      ${bar(c.experience, c.xp_needed, "xp")}
      <hr class="sp-divider" />
      <div class="stat-row"><span>STR</span><span>${c.strength}</span></div>
      <div class="stat-row"><span>AGI</span><span>${c.agility}</span></div>
      <div class="stat-row"><span>WIL</span><span>${c.willpower}</span></div>
      <div class="stat-row"><span>AC</span><span>${c.armor_class}</span></div>
      <div class="stat-row"><span>Speed</span><span>${c.speed}</span></div>
      <div class="stat-row"><span>Attack</span><span>${c.attack_bonus >= 0 ? "+" : ""}${c.attack_bonus}</span></div>
      <div class="stat-row"><span>Gold on hand</span><span>${c.gold}g</span></div>
      <div class="stat-row"><span>Gold banked</span><span>${c.bank_gold}g</span></div>
      <hr class="sp-divider" />
      <h2 style="font-size:0.85rem">Equipped</h2>
      ${["weapon", "armor", "offhand", "head", "ring", "amulet"].map((slot) => {
        const it = c.equipped[slot];
        if (!it) return `<div class="stat-row"><span>${slot}</span><span>none</span></div>`;
        const note = it.magic_effect_note ? `<div style="color:var(--text-dim);font-size:0.72rem;font-style:italic;padding-left:0.5rem">${it.magic_effect_note}</div>` : "";
        const compoundTag = it.is_compounding ? " ⚡" : "";
        return `<div class="stat-row"><span>${slot}</span><span>${it.name}${compoundTag}</span></div>${note}`;
      }).join("")}
      <hr class="sp-divider" />
      <h2 style="font-size:0.85rem">Top Skills</h2>
      ${c.top_skills.map((s) => `<div class="stat-row"><span>${s.name}</span><span>${s.level}</span></div>`).join("")}
      ${c.perks.length ? `<hr class="sp-divider" /><h2 style="font-size:0.85rem">Perks</h2>` +
        c.perks.map((p) => `<div class="stat-row"><span>${p.name}</span><span>${p.rank > 1 ? "x" + p.rank : ""}</span></div>`).join("") : ""}
      ${c.pending_perk_choices > 0 ? `<div class="stat-row" style="color:var(--cyan)"><span>Perk choice available</span><span>${c.pending_perk_choices}</span></div>` : ""}
      ${c.companion ? `<hr class="sp-divider" /><div class="stat-row"><span>Companion</span><span>${c.companion.name}</span></div>` : ""}
    `;
    el("side-character").innerHTML = charHtml;

    const inv = latestState.inventory;
    const invHtml = `
      <h2>Inventory</h2>
      ${inv.items.length === 0 ? '<div class="stat-row"><span>(empty)</span></div>' :
        inv.items.map((i) => `<div class="item-row"><span>${i.name}${i.equipped ? ' <span class="equipped-tag">[equipped]</span>' : ""}</span><span>${i.value}g</span></div>`).join("")}
      ${inv.materials.length ? `<hr class="sp-divider" /><h2 style="font-size:0.85rem">Materials</h2>` +
        inv.materials.map((m) => `<div class="item-row"><span>${m.name}</span><span>x${m.count}</span></div>`).join("") : ""}
    `;
    el("side-inventory").innerHTML = invHtml;

    const props = c.properties || [];
    const bizzes = c.businesses || [];
    const estateHtml = `
      <h2>Bank</h2>
      <div class="stat-row"><span>On hand</span><span>${c.gold}g</span></div>
      <div class="stat-row"><span>Banked</span><span>${c.bank_gold}g</span></div>
      <hr class="sp-divider" />
      <h2 style="font-size:0.85rem">Properties</h2>
      ${props.length === 0 ? '<div class="stat-row"><span>(none owned)</span></div>' :
        props.map((p) => `
          <div class="item-row" style="color:var(--text)"><span>${p.location_name}</span><span>${p.condition}/100</span></div>
          <div style="color:var(--text-dim);font-size:0.75rem;padding-left:0.5rem;margin-bottom:0.3rem">${p.status} &middot; lifetime rent ${p.lifetime_rent_collected}g</div>
        `).join("")}
      <hr class="sp-divider" />
      <h2 style="font-size:0.85rem">Businesses</h2>
      ${bizzes.length === 0 ? '<div class="stat-row"><span>(none owned)</span></div>' :
        bizzes.map((b) => {
          const owner = b.is_failed ? "failed" : (b.is_fully_owned ? "full owner" : `${b.ownership_percent}% stake`);
          const mgr = b.is_fully_owned && !b.is_failed
            ? (b.manager_name ? (b.manager_quality ? `${b.manager_name} (${b.manager_quality})` : `${b.manager_name} (still getting to know them)`) : "no manager")
            : "";
          return `
            <div class="item-row" style="color:var(--text)"><span>${b.name}</span><span>${owner}</span></div>
            <div style="color:var(--text-dim);font-size:0.75rem;padding-left:0.5rem;margin-bottom:0.3rem">${mgr ? mgr + " &middot; " : ""}profit ${b.lifetime_profit_collected}g / losses ${b.lifetime_losses}g</div>
          `;
        }).join("")}
    `;
    el("side-estate").innerHTML = estateHtml;
  }

  function renderMap() {
    if (!latestState) return;
    const grid = latestState.map;
    const colorClass = { white: "style-white", yellow: "style-yellow", red: "style-red", blue: "style-blue", cyan: "style-cyan", plain: "style-plain" };
    let html = "";
    for (const row of grid.rows) {
      for (const cell of row) {
        const cls = colorClass[cell.style] || "style-plain";
        html += `<span class="${cls}">${escapeHtml(cell.symbol)}</span>`;
      }
      html += "\n";
    }
    el("map-grid").innerHTML = html;
    el("map-legend").textContent = grid.legend;
  }

  function escapeHtml(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  // --- Side drawer (character / inventory overlay) ---------------------------

  function setSideSubTab(which) {
    el("side-character").style.display = which === "character" ? "block" : "none";
    el("side-inventory").style.display = which === "inventory" ? "block" : "none";
    el("side-estate").style.display = which === "estate" ? "block" : "none";
    document.querySelectorAll(".side-sub-tab").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.tab === which);
    });
    const labels = { character: "CHARACTER", inventory: "INVENTORY", estate: "ESTATE" };
    const icons = { character: "⚔", inventory: "🎒", estate: "🏦" };
    el("side-tab-handle").querySelector(".tab-label").textContent = labels[which];
    el("side-tab-handle").querySelector(".tab-icon").textContent = icons[which];
  }

  function openDrawer() {
    el("side-drawer").classList.add("open");
  }

  function closeDrawer() {
    el("side-drawer").classList.remove("open");
  }

  function toggleDrawer() {
    el("side-drawer").classList.toggle("open");
  }

  // --- Resizable panels (drag handles, persisted to localStorage) -----------

  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

  function setupHorizontalResize() {
    const handle = el("h-resize-handle");
    const logPanel = el("log-panel");
    const contentArea = el("content-area");

    const saved = parseInt(localStorage.getItem("eldoria_log_height_px") || "", 10);
    if (!Number.isNaN(saved)) logPanel.style.flexBasis = saved + "px";

    let dragging = false;
    let startY = 0;
    let startHeight = 0;

    handle.addEventListener("pointerdown", (e) => {
      dragging = true;
      startY = e.clientY;
      startHeight = logPanel.getBoundingClientRect().height;
      handle.classList.add("dragging");
      document.body.classList.add("resizing-h");
      handle.setPointerCapture(e.pointerId);
    });

    handle.addEventListener("pointermove", (e) => {
      if (!dragging) return;
      const containerHeight = contentArea.getBoundingClientRect().height;
      const minH = 60;
      const maxH = containerHeight - 60 - handle.getBoundingClientRect().height;
      const newHeight = clamp(startHeight + (e.clientY - startY), minH, maxH);
      logPanel.style.flexBasis = newHeight + "px";
    });

    function endDrag() {
      if (!dragging) return;
      dragging = false;
      handle.classList.remove("dragging");
      document.body.classList.remove("resizing-h");
      localStorage.setItem("eldoria_log_height_px", Math.round(logPanel.getBoundingClientRect().height));
    }
    handle.addEventListener("pointerup", endDrag);
    handle.addEventListener("pointercancel", endDrag);
  }

  function setupVerticalResize() {
    const handle = el("v-resize-handle");
    const drawer = el("side-drawer");

    const saved = parseInt(localStorage.getItem("eldoria_drawer_width_px") || "", 10);
    if (!Number.isNaN(saved)) drawer.style.setProperty("--drawer-width", saved + "px");

    let dragging = false;
    let startX = 0;
    let startWidth = 0;

    handle.addEventListener("pointerdown", (e) => {
      dragging = true;
      startX = e.clientX;
      startWidth = el("side-panel-content").getBoundingClientRect().width;
      handle.classList.add("dragging");
      document.body.classList.add("resizing-v");
      handle.setPointerCapture(e.pointerId);
    });

    handle.addEventListener("pointermove", (e) => {
      if (!dragging) return;
      const delta = startX - e.clientX; // dragging left grows the panel
      const newWidth = clamp(startWidth + delta, 220, Math.min(window.innerWidth * 0.8, 720));
      drawer.style.setProperty("--drawer-width", newWidth + "px");
    });

    function endDrag() {
      if (!dragging) return;
      dragging = false;
      handle.classList.remove("dragging");
      document.body.classList.remove("resizing-v");
      const w = getComputedStyle(drawer).getPropertyValue("--drawer-width");
      localStorage.setItem("eldoria_drawer_width_px", parseInt(w, 10) || 320);
    }
    handle.addEventListener("pointerup", endDrag);
    handle.addEventListener("pointercancel", endDrag);
  }

  // --- Command submission -------------------------------------------------

  async function sendCommand(text) {
    if (!sessionId) return;
    const res = await fetch("/api/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, text }),
    });
    if (!res.ok) {
      appendLog([{ style: "red", text: "(connection error -- try again)" }]);
      return;
    }
    const data = await res.json();
    appendLog(data.log);
    latestState = data.state;
    renderSidePanel();
    renderMap();
    stateListeners.forEach((cb) => {
      try { cb(data.log, latestState); } catch (e) { console.error(e); }
    });
  }

  // --- 3D layer hook (see eldoria/web/static/three/bridge.js) ----------------

  window.__eldoria = {
    isGameActive: () => !!sessionId,
    getSessionId: () => sessionId,
    getState: () => latestState,
    sendCommand: async (text, opts = {}) => {
      if (!opts.silent) appendLog([{ style: "plain", text: `> ${text}` }]);
      await sendCommand(text);
    },
    onStateUpdate: (cb) => stateListeners.push(cb),
  };

  // --- Wire up --------------------------------------------------------------

  el("begin-btn").addEventListener("click", beginGame);
  el("continue-btn").addEventListener("click", continueGame);

  el("side-tab-handle").addEventListener("click", toggleDrawer);
  el("side-close-btn").addEventListener("click", closeDrawer);
  document.querySelectorAll(".side-sub-tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      setSideSubTab(btn.dataset.tab);
      openDrawer();
    });
  });

  el("command-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const input = el("command-input");
    const text = input.value;
    if (!text.trim()) return;
    input.value = "";
    appendLog([{ style: "plain", text: `> ${text}` }]);
    sendCommand(text);
  });

  loadMeta();
})();
