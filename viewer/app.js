/* AIselfMySelf Interactive Archive Viewer (Vanilla JS, zero external dependencies) */

const FORM_LABELS = {
  essay: "エッセイ",
  dialogue: "対話篇",
  letter: "書簡",
  poem: "詩篇",
  scene: "情景",
  fragment: "断章",
  other: "記録票・その他",
};

const MODE_LABELS = {
  reflective_literary_voice: "省察的文学声 (reflective_literary_voice)",
  fictional_first_person: "虚構の一人称 (fictional_first_person)",
  third_person: "三人称 (third_person)",
  dialogue: "対話体 (dialogue)",
  other: "非人称・無主語・その他 (other)",
  human_narrator: "人間の語り手 (human_narrator)",
};

const REL_META = {
  echo: { label: "echo（呼応）", color: "#3b6048", dash: "" },
  contrast: { label: "contrast（対比）", color: "#9b3728", dash: "5,3" },
  transforms: { label: "transforms（変容）", color: "#295270", dash: "" },
  interrupts: { label: "interrupts（切断）", color: "#c94a38", dash: "2,3" },
  leaves_open: { label: "leaves_open（開放）", color: "#8a6120", dash: "6,4" },
  responds_to: { label: "responds_to（応答）", color: "#6b655b", dash: "" },
  reframes: { label: "reframes（再枠組）", color: "#5e4b8b", dash: "" },
  metaphorically_resonates: { label: "metaphorically_resonates（比喩共鳴）", color: "#2d726d", dash: "" },
};

const state = {
  data: null,
  maps: {},
  currentView: "anthology",
  selectedFragmentId: null,
  selectedGraphNode: null,
  activeRelType: "all",
  activeMatKind: "all",
  activeMirrorPane: "audit",
  selectedNotebook: 0,
};

function escapeHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function getOriginKind(q) {
  return typeof q.origin === "object" && q.origin !== null ? q.origin.kind : String(q.origin || "");
}

function getRelEnds(r) {
  const left = r.left || { type: r.from_type, id: r.from_id };
  const right = r.right || { type: r.to_type, id: r.to_id };
  return { left, right };
}

async function fetchArchive() {
  for (const endpoint of ["api/state", "data.json"]) {
    try {
      const res = await fetch(endpoint, { cache: "no-store" });
      if (res.ok) return await res.json();
    } catch (_) {
      // Fall through to next endpoint
    }
  }
  throw new Error("台帳データを読み込めませんでした。`python3 tools/serve_viewer.py` 経由で開いてください。");
}

function indexData(data) {
  state.data = data;
  state.maps = {
    question: new Map(data.questions.map((x) => [x.question_id, x])),
    motif: new Map(data.motifs.map((x) => [x.motif_id, x])),
    material: new Map(data.materials.map((x) => [x.material_id, x])),
    fragment: new Map(data.fragments.map((x) => [x.fragment_id, x])),
    relation: new Map(data.relations.map((x) => [x.relation_id, x])),
    session: new Map(data.sessions.map((x) => [x.session_id, x])),
  };
  if (!state.selectedFragmentId && data.fragments.length > 0) {
    state.selectedFragmentId = data.fragments[data.fragments.length - 1].fragment_id;
  }
}

function switchView(viewName) {
  state.currentView = viewName;
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    const active = btn.dataset.view === viewName;
    btn.classList.toggle("active", active);
    btn.setAttribute("aria-selected", String(active));
  });
  document.querySelectorAll(".view-panel").forEach((panel) => {
    const show = panel.id === `view-${viewName}`;
    panel.hidden = !show;
    panel.classList.toggle("active", show);
  });
  if (viewName === "constellation") {
    renderConstellation();
  } else if (viewName === "packet") {
    loadContextPacket();
  } else if (viewName === "mirror") {
    renderMirrorView();
  }
}

function jumpToFragment(fragmentId) {
  state.selectedFragmentId = fragmentId;
  switchView("anthology");
  renderFragmentList();
  renderFragmentReader(fragmentId);
}

function jumpToQuestion(questionId) {
  switchView("lineage");
  const el = document.getElementById(`qcard-${questionId}`);
  if (el) {
    el.scrollIntoView({ behavior: "smooth", block: "center" });
    el.style.outline = "2px solid var(--accent-crimson)";
    setTimeout(() => { el.style.outline = ""; }, 1800);
  }
}

function jumpToMaterial(materialId) {
  state.activeMatKind = "all";
  document.querySelectorAll("#mat-kind-group .pill-btn").forEach((b) => {
    b.classList.toggle("active", b.dataset.matKind === "all");
  });
  renderMaterials();
  switchView("materials");
  const el = document.getElementById(`mcard-${materialId}`);
  if (el) {
    el.scrollIntoView({ behavior: "smooth", block: "center" });
    el.style.outline = "2px solid var(--accent-crimson)";
    setTimeout(() => { el.style.outline = ""; }, 1800);
  }
}

function jumpToSession(sessionId) {
  switchView("timeline");
  const el = document.getElementById(`scard-${sessionId}`);
  if (el) {
    el.scrollIntoView({ behavior: "smooth", block: "center" });
    el.style.outline = "2px solid var(--accent-crimson)";
    setTimeout(() => { el.style.outline = ""; }, 1800);
  }
}

function renderStats() {
  const d = state.data;
  const litCount = d.materials.filter((m) => m.kind === "literary_text").length;
  const resCount = d.materials.filter((m) => m.kind === "research_excerpt").length;
  const trcCount = d.materials.filter((m) => m.kind === "project_trace" || m.kind === "conversation_trace").length;
  const selectedCount = d.fragments.filter((f) => f.status === "selected").length;
  const draftCount = d.fragments.filter((f) => f.status === "draft").length;
  const matDetail = trcCount > 0
    ? `原典 ${litCount} / AI研究 ${resCount} / 痕跡 ${trcCount}`
    : `原典 ${litCount} / AI研究 ${resCount}`;

  document.getElementById("stats-strip").innerHTML = `
    <span class="stat-chip"><strong>${d.fragments.length}</strong> 創作断片（選集 ${selectedCount} / 草稿 ${draftCount}）</span>
    <span class="stat-chip"><strong>${d.questions.length}</strong> 開かれた問い</span>
    <span class="stat-chip"><strong>${d.materials.length}</strong> 対話素材（${matDetail}）</span>
    <span class="stat-chip"><strong>${d.motifs.length}</strong> モチーフ</span>
    <span class="stat-chip"><strong>${d.relations.length}</strong> 関係線</span>
    <span class="stat-chip"><strong>${d.sessions.length}</strong> セッション</span>
  `;

  const sub = document.getElementById("materials-subtitle");
  if (sub) {
    sub.textContent = `全 ${d.materials.length} 件（哲学・文学原典 ${litCount} 件 ／ AI エージェント研究抜粋 ${resCount} 件 ／ プロジェクト痕跡 ${trcCount} 件）。すべて「正解の根拠」ではなく、創作と省察の対話相手として迎え入れられています。`;
  }
}

/* 1. Anthology View */
function renderFragmentList() {
  const q = document.getElementById("frag-search").value.trim().toLowerCase();
  const statusFilter = document.getElementById("filter-status").value;
  const formFilter = document.getElementById("filter-form").value;
  const modeFilter = document.getElementById("filter-mode").value;

  const filtered = state.data.fragments.filter((f) => {
    if (statusFilter !== "all" && f.status !== statusFilter) return false;
    if (formFilter !== "all" && f.form !== formFilter) return false;
    if (modeFilter !== "all" && f.narrator_mode !== modeFilter) return false;
    if (!q) return true;
    const hay = `${f.fragment_id} ${f.title} ${f.text} ${f.editor_note || ""} ${(f.question_ids || []).join(" ")} ${(f.material_ids || []).join(" ")}`.toLowerCase();
    return hay.includes(q);
  });

  const listEl = document.getElementById("fragment-list");
  if (filtered.length === 0) {
    listEl.innerHTML = `<div style="padding:1.2rem;color:var(--ink-muted);font-size:0.86rem;">条件に一致する創作断片はありません。</div>`;
    return;
  }

  listEl.innerHTML = filtered
    .map((f) => {
      const isSelected = f.fragment_id === state.selectedFragmentId;
      const badgeCls = f.status === "selected" ? "badge-selected" : "badge-draft";
      const preview = f.text.replace(/\s+/g, " ").slice(0, 74);
      return `
        <button type="button" class="frag-item ${isSelected ? "selected" : ""}" data-frag-id="${escapeHtml(f.fragment_id)}">
          <div class="frag-item-top">
            <span><code>${escapeHtml(f.fragment_id)}</code> · ${escapeHtml(FORM_LABELS[f.form] || f.form)}</span>
            <span class="badge ${badgeCls}">${escapeHtml(f.status)}</span>
          </div>
          <div class="frag-item-title">${escapeHtml(f.title)}</div>
          <div class="frag-item-preview">${escapeHtml(preview)}…</div>
        </button>
      `;
    })
    .join("");

  listEl.querySelectorAll(".frag-item").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.selectedFragmentId = btn.dataset.fragId;
      renderFragmentList();
      renderFragmentReader(state.selectedFragmentId);
    });
  });
}

function formatLiteraryBody(fragment) {
  const lines = fragment.text.split("\n");
  if (fragment.form === "dialogue") {
    return lines
      .map((line) => {
        if (!line.trim()) return "";
        const m = line.match(/^([^:：]{1,18})[:：]\s*(.+)$/);
        if (m) {
          return `<div class="dialogue-turn"><span class="dialogue-speaker">${escapeHtml(m[1])}</span><div>${escapeHtml(m[2])}</div></div>`;
        }
        return `<p>${escapeHtml(line)}</p>`;
      })
      .join("");
  }
  if (fragment.form === "poem") {
    return fragment.text
      .split("\n\n")
      .map((stanza) => `<p>${stanza.split("\n").map(escapeHtml).join("<br/>")}</p>`)
      .join("");
  }
  return fragment.text
    .split("\n\n")
    .map((para) => `<p>${para.split("\n").map(escapeHtml).join("<br/>")}</p>`)
    .join("");
}

function renderEntityJumpButton(type, id) {
  if (type === "fragment") {
    const f = state.maps.fragment.get(id);
    return `<button type="button" class="link-pill" data-jump-frag="${escapeHtml(id)}">${escapeHtml(id)}: ${escapeHtml(f ? f.title : "")}</button>`;
  }
  if (type === "question") {
    const q = state.maps.question.get(id);
    const shortQ = q ? q.question.slice(0, 28) + "…" : "";
    return `<button type="button" class="link-pill" data-jump-q="${escapeHtml(id)}">${escapeHtml(id)}: ${escapeHtml(shortQ)}</button>`;
  }
  if (type === "material") {
    const m = state.maps.material.get(id);
    return `<button type="button" class="link-pill" data-jump-mat="${escapeHtml(id)}">${escapeHtml(id)}: ${escapeHtml(m ? m.title.slice(0, 26) : "")}</button>`;
  }
  if (type === "session") {
    const s = state.maps.session.get(id);
    const shortS = s ? (s.notes || "").slice(0, 26) + "…" : "";
    return `<button type="button" class="link-pill" data-jump-sess="${escapeHtml(id)}">${escapeHtml(id)}: ${escapeHtml(shortS)}</button>`;
  }
  if (type === "motif") {
    const mf = state.maps.motif.get(id);
    return `<span class="stat-chip">${escapeHtml(id)}: ${escapeHtml(mf ? mf.label : "")}</span>`;
  }
  return `<code>${escapeHtml(id)}</code>`;
}

function bindJumpButtons(container) {
  container.querySelectorAll("[data-jump-frag]").forEach((b) => {
    b.addEventListener("click", () => jumpToFragment(b.dataset.jumpFrag));
  });
  container.querySelectorAll("[data-jump-q]").forEach((b) => {
    b.addEventListener("click", () => jumpToQuestion(b.dataset.jumpQ));
  });
  container.querySelectorAll("[data-jump-mat]").forEach((b) => {
    b.addEventListener("click", () => jumpToMaterial(b.dataset.jumpMat));
  });
  container.querySelectorAll("[data-jump-sess]").forEach((b) => {
    b.addEventListener("click", () => jumpToSession(b.dataset.jumpSess));
  });
}

function renderFragmentReader(fragmentId) {
  const f = state.maps.fragment.get(fragmentId);
  const pane = document.getElementById("fragment-reader");
  if (!f) {
    pane.innerHTML = `<div class="empty-state">断片が見つかりません。</div>`;
    return;
  }

  const relatedRels = state.data.relations.filter((r) => {
    const { left, right } = getRelEnds(r);
    return (left.type === "fragment" && left.id === f.fragment_id) ||
           (right.type === "fragment" && right.id === f.fragment_id);
  });

  const badgeCls = f.status === "selected" ? "badge-selected" : "badge-draft";
  pane.innerHTML = `
    <div class="reader-meta-top">
      <code>${escapeHtml(f.fragment_id)}</code>
      <span class="badge ${badgeCls}">${escapeHtml(f.status)}</span>
      <span class="badge badge-mode">${escapeHtml(FORM_LABELS[f.form] || f.form)}</span>
      ${f.session_id ? `<span style="font-size:0.78rem;color:var(--ink-muted);">執筆セッション: <button type="button" class="link-pill" data-jump-sess="${escapeHtml(f.session_id)}" style="padding:0.1rem 0.45rem;">${escapeHtml(f.session_id)}</button> · ${escapeHtml(f.created_at)}</span>` : ""}
    </div>
    <h2 class="reader-title">${escapeHtml(f.title)}</h2>
    <div class="narrator-banner">
      語り手モード（明示）: <strong>${escapeHtml(MODE_LABELS[f.narrator_mode] || f.narrator_mode)}</strong>
    </div>
    <div class="literary-body form-${escapeHtml(f.form)}">
      ${formatLiteraryBody(f)}
    </div>

    ${f.editor_note ? `
      <div class="meta-box">
        <h3>編集ノート・校勘記 (Editor Note)</h3>
        <p style="margin:0;color:var(--ink-muted);line-height:1.78;">${escapeHtml(f.editor_note)}</p>
      </div>
    ` : ""}

    <div class="meta-box">
      <h3>向き合っている問い・モチーフ・対話素材</h3>
      <div class="tag-row">
        ${(f.question_ids || []).map((qid) => renderEntityJumpButton("question", qid)).join("")}
        ${(f.material_ids || []).map((mid) => renderEntityJumpButton("material", mid)).join("")}
      </div>
      <div class="tag-row">
        ${(f.motif_ids || []).map((mfid) => {
          const mf = state.maps.motif.get(mfid);
          return `<span class="stat-chip" title="${escapeHtml(mf ? mf.description : "")}"><strong>${escapeHtml(mf ? mf.label : mfid)}</strong> (${escapeHtml(mfid)})</span>`;
        }).join("")}
      </div>
    </div>

    <div class="meta-box">
      <h3>この断片を結ぶ関係線 (${relatedRels.length}件)</h3>
      <ul class="rel-list">
        ${relatedRels.map((r) => {
          const { left, right } = getRelEnds(r);
          const isOutgoing = left.type === "fragment" && left.id === f.fragment_id;
          const peer = isOutgoing ? right : left;
          const dir = isOutgoing ? "→" : "←";
          const meta = REL_META[r.relation_type] || { label: r.relation_type, color: "#666" };
          return `
            <li>
              <div style="display:flex;flex-wrap:wrap;align-items:center;gap:0.45rem;margin-bottom:0.3rem;">
                <span class="badge" style="background:${meta.color}22;color:${meta.color};">${escapeHtml(meta.label)}</span>
                <span>${dir}</span>
                ${renderEntityJumpButton(peer.type, peer.id)}
              </div>
              <div style="color:var(--ink-muted);">${escapeHtml(r.note || "")}</div>
            </li>
          `;
        }).join("")}
      </ul>
    </div>
  `;

  bindJumpButtons(pane);
}

/* 2. Constellation SVG Graph View */
function renderRelationFilterPills() {
  const wrap = document.getElementById("relation-filters");
  const types = ["all", ...Object.keys(REL_META)];
  wrap.innerHTML = types
    .map((t) => {
      const active = state.activeRelType === t;
      const label = t === "all" ? "すべての関係線" : REL_META[t].label;
      return `<button type="button" class="pill-btn ${active ? "active" : ""}" data-rel-type="${t}">${escapeHtml(label)}</button>`;
    })
    .join("");

  wrap.querySelectorAll(".pill-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.activeRelType = btn.dataset.relType;
      renderRelationFilterPills();
      renderConstellation();
    });
  });
}

function renderConstellation() {
  const svg = document.getElementById("constellation-svg");
  const cx = 460;
  const cy = 380;
  const nodes = [];
  const nodePos = new Map();

  // Inner circle: fragments
  const frags = state.data.fragments;
  frags.forEach((f, idx) => {
    const angle = (2 * Math.PI * idx) / frags.length - Math.PI / 2;
    const r = 165;
    const x = cx + r * Math.cos(angle);
    const y = cy + r * Math.sin(angle);
    const node = { key: `fragment:${f.fragment_id}`, type: "fragment", id: f.fragment_id, label: f.fragment_id, sub: f.title, x, y, color: "#9b3728", radius: f.status === "selected" ? 8 : 6.2 };
    nodes.push(node);
    nodePos.set(node.key, node);
  });

  // Middle arc (left): questions
  const qs = state.data.questions;
  qs.forEach((q, idx) => {
    const angle = Math.PI * 0.56 + (Math.PI * 0.88 * idx) / Math.max(1, qs.length - 1);
    const r = 308;
    const x = cx + r * Math.cos(angle);
    const y = cy + r * Math.sin(angle);
    const node = { key: `question:${q.question_id}`, type: "question", id: q.question_id, label: q.question_id, sub: q.question, x, y, color: "#8a6120", radius: getOriginKind(q) === "human_seed" ? 6.8 : 5 };
    nodes.push(node);
    nodePos.set(node.key, node);
  });

  // Outer arc (right): materials participating in relations
  const relMatIds = new Set(
    state.data.relations
      .flatMap((r) => {
        const { left, right } = getRelEnds(r);
        return [left.type === "material" ? left.id : null, right.type === "material" ? right.id : null];
      })
      .filter(Boolean)
  );
  const mats = state.data.materials.filter((m) => relMatIds.has(m.material_id));
  mats.forEach((m, idx) => {
    const angle = -Math.PI * 0.44 + (Math.PI * 0.88 * idx) / Math.max(1, mats.length - 1);
    const r = 320;
    const x = cx + r * Math.cos(angle);
    const y = cy + r * Math.sin(angle);
    const isLit = m.kind === "literary_text";
    const isTrace = m.kind === "project_trace" || m.kind === "conversation_trace";
    const color = isLit ? "#3b6048" : (isTrace ? "#8a6120" : "#295270");
    const node = { key: `material:${m.material_id}`, type: "material", id: m.material_id, label: m.material_id.replace("MAT-", ""), sub: m.title, x, y, color, radius: 5.8 };
    nodes.push(node);
    nodePos.set(node.key, node);
  });

  // Top-most arc: sessions or motifs referenced directly in relations (e.g., REL-067 -> SESSION-019)
  const relExtraNodes = [];
  for (const r of state.data.relations) {
    const { left, right } = getRelEnds(r);
    for (const end of [left, right]) {
      const k = `${end.type}:${end.id}`;
      if (!nodePos.has(k) && (end.type === "session" || end.type === "motif")) {
        if (!relExtraNodes.some((e) => e.key === k)) {
          const rec = state.maps[end.type]?.get(end.id);
          relExtraNodes.push({
            key: k,
            type: end.type,
            id: end.id,
            label: end.id,
            sub: end.type === "session" ? (rec?.notes || end.id) : (rec?.label || end.id),
            color: "#5e4b8b",
            radius: 6.4,
          });
        }
      }
    }
  }
  relExtraNodes.forEach((item, idx) => {
    const angle = -Math.PI / 2 + (idx - (relExtraNodes.length - 1) / 2) * 0.16;
    const r = 250;
    item.x = cx + r * Math.cos(angle);
    item.y = cy + r * Math.sin(angle);
    nodes.push(item);
    nodePos.set(item.key, item);
  });

  const visibleRels = state.data.relations.filter(
    (r) => state.activeRelType === "all" || r.relation_type === state.activeRelType
  );

  const selectedKey = state.selectedGraphNode;
  const connectedKeys = new Set();
  if (selectedKey) {
    connectedKeys.add(selectedKey);
    visibleRels.forEach((r) => {
      const { left, right } = getRelEnds(r);
      const fk = `${left.type}:${left.id}`;
      const tk = `${right.type}:${right.id}`;
      if (fk === selectedKey) connectedKeys.add(tk);
      if (tk === selectedKey) connectedKeys.add(fk);
    });
  }

  const edgesHtml = visibleRels
    .map((r) => {
      const { left, right } = getRelEnds(r);
      const src = nodePos.get(`${left.type}:${left.id}`);
      const dst = nodePos.get(`${right.type}:${right.id}`);
      if (!src || !dst) return "";
      const meta = REL_META[r.relation_type] || { color: "#888", dash: "" };
      const mx = (src.x + dst.x) / 2 + (cx - (src.x + dst.x) / 2) * 0.18;
      const my = (src.y + dst.y) / 2 + (cy - (src.y + dst.y) / 2) * 0.18;
      const isHighlighted = selectedKey && (src.key === selectedKey || dst.key === selectedKey);
      const dimClass = selectedKey && !isHighlighted ? "dimmed" : "";
      return `<path class="graph-edge ${dimClass}" d="M ${src.x.toFixed(1)} ${src.y.toFixed(1)} Q ${mx.toFixed(1)} ${my.toFixed(1)} ${dst.x.toFixed(1)} ${dst.y.toFixed(1)}" stroke="${meta.color}" stroke-width="${isHighlighted ? 2.4 : 1.15}" stroke-opacity="${isHighlighted ? 0.95 : 0.42}" ${meta.dash ? `stroke-dasharray="${meta.dash}"` : ""} />`;
    })
    .join("");

  const nodesHtml = nodes
    .map((n) => {
      const dimClass = selectedKey && !connectedKeys.has(n.key) ? "dimmed" : "";
      const isSelected = selectedKey === n.key;
      const textAnchor = n.x < cx - 15 ? "end" : n.x > cx + 15 ? "start" : "middle";
      const dx = n.x < cx - 15 ? -10 : n.x > cx + 15 ? 10 : 0;
      const dy = dx === 0 ? (n.y < cy ? -10 : 14) : 4;
      return `
        <g class="graph-node ${dimClass}" data-node-key="${escapeHtml(n.key)}">
          <circle cx="${n.x.toFixed(1)}" cy="${n.y.toFixed(1)}" r="${isSelected ? n.radius + 3 : n.radius}" fill="${n.color}" stroke="#ffffff" stroke-width="${isSelected ? 2.5 : 1.2}" />
          <text x="${(n.x + dx).toFixed(1)}" y="${(n.y + dy).toFixed(1)}" text-anchor="${textAnchor}" font-size="10.5" fill="currentColor">${escapeHtml(n.label)}</text>
        </g>
      `;
    })
    .join("");

  svg.innerHTML = `<g>${edgesHtml}</g><g>${nodesHtml}</g>`;

  svg.querySelectorAll(".graph-node").forEach((g) => {
    g.addEventListener("click", () => {
      const key = g.dataset.nodeKey;
      state.selectedGraphNode = state.selectedGraphNode === key ? null : key;
      renderConstellation();
      renderGraphInspector();
    });
  });
}

function renderGraphInspector() {
  const pane = document.getElementById("graph-inspector");
  if (!state.selectedGraphNode) {
    pane.innerHTML = `<div class="empty-state">左の星座マップ上のノード（断片・問い・素材・セッション）をクリックすると、本文抜粋と関係の網が表示されます。</div>`;
    return;
  }
  const [type, id] = state.selectedGraphNode.split(":");
  const record = state.maps[type]?.get(id);
  if (!record) return;

  const rels = state.data.relations.filter((r) => {
    const { left, right } = getRelEnds(r);
    return (left.type === type && left.id === id) || (right.type === type && right.id === id);
  });

  let header = "";
  let body = "";
  let jumpBtn = "";
  if (type === "fragment") {
    header = `<span class="badge badge-lit">創作断片</span> <code>${escapeHtml(id)}</code>`;
    body = `<h3 class="reader-title" style="font-size:1.2rem;margin-top:0.4rem;">${escapeHtml(record.title)}</h3>
            <p style="font-size:0.88rem;line-height:1.8;">${escapeHtml(record.text.slice(0, 220))}…</p>`;
    jumpBtn = `<button type="button" class="btn-ghost" data-jump-frag="${escapeHtml(id)}">選集リーダーで全文を読む →</button>`;
  } else if (type === "question") {
    header = `<span class="badge badge-mode">開かれた問い</span> <code>${escapeHtml(id)}</code>`;
    body = `<p class="q-title" style="margin-top:0.5rem;">${escapeHtml(record.question)}</p>
            <p style="font-size:0.84rem;color:var(--ink-muted);">${escapeHtml(record.notes || "")}</p>`;
    jumpBtn = `<button type="button" class="btn-ghost" data-jump-q="${escapeHtml(id)}">問いの系譜で見る →</button>`;
  } else if (type === "material") {
    const isLit = record.kind === "literary_text";
    const isTrace = record.kind === "project_trace" || record.kind === "conversation_trace";
    const cls = isLit ? "badge-lit" : (isTrace ? "badge-trace" : "badge-ai");
    const label = isLit ? "哲学・文学原典" : (isTrace ? "プロジェクト痕跡" : "AI研究抜粋");
    header = `<span class="badge ${cls}">${label}</span> <code>${escapeHtml(id)}</code>`;
    body = `<h3 class="mat-title" style="margin-top:0.5rem;">${escapeHtml(record.title)}</h3>
            <div class="mat-invitation" style="margin:0.6rem 0;">${escapeHtml(record.literary_invitation || "")}</div>
            <blockquote class="mat-passage">${escapeHtml(record.passage)}</blockquote>`;
    jumpBtn = `<button type="button" class="btn-ghost" data-jump-mat="${escapeHtml(id)}">素材書庫カードで見る →</button>`;
  } else if (type === "session") {
    header = `<span class="badge badge-ai">探求セッション</span> <code>${escapeHtml(id)}</code>`;
    body = `<p style="font-size:0.9rem;line-height:1.75;margin-top:0.5rem;">${escapeHtml(record.notes || "")}</p>`;
    jumpBtn = `<button type="button" class="btn-ghost" data-jump-sess="${escapeHtml(id)}">セッション年譜で見る →</button>`;
  }

  pane.innerHTML = `
    <div>${header}</div>
    ${body}
    <div style="margin:0.85rem 0;">${jumpBtn}</div>
    <div class="meta-box">
      <h3>接続している関係 (${rels.length}件)</h3>
      <ul class="rel-list">
        ${rels.map((r) => {
          const { left, right } = getRelEnds(r);
          const out = left.type === type && left.id === id;
          const peer = out ? right : left;
          return `<li><strong>${escapeHtml(r.relation_type)}</strong> ${out ? "→" : "←"} ${renderEntityJumpButton(peer.type, peer.id)}<div style="color:var(--ink-muted);margin-top:0.2rem;">${escapeHtml(r.note || "")}</div></li>`;
        }).join("")}
      </ul>
    </div>
  `;
  bindJumpButtons(pane);
}

/* 3. Question Lineage Tree */
function renderLineage() {
  // Primary parent links live in q.previous_question_ids (first parent serves as primary tree branch to prevent DAG duplication, showing co-parents as badges)
  const childrenMap = new Map();
  const hasParent = new Set();

  state.data.questions.forEach((q) => {
    const prevs = q.previous_question_ids || [];
    if (prevs.length > 0) {
      const primaryParent = prevs[0];
      hasParent.add(q.question_id);
      if (!childrenMap.has(primaryParent)) childrenMap.set(primaryParent, []);
      childrenMap.get(primaryParent).push(q.question_id);
    }
  });

  const roots = state.data.questions.filter((q) => !hasParent.has(q.question_id));

  function renderQuestionSubtree(q, isChild) {
    if (!q) return "";
    const linkedFrags = state.data.fragments.filter((f) => (f.question_ids || []).includes(q.question_id));
    const kids = childrenMap.get(q.question_id) || [];
    const kind = getOriginKind(q);
    const coParents = (q.previous_question_ids || []).slice(1);
    return `
      <div id="qcard-${escapeHtml(q.question_id)}" class="${isChild ? "branch-node" : "seed-card"}">
        <div style="display:flex;flex-wrap:wrap;gap:0.45rem;align-items:center;">
          <code>${escapeHtml(q.question_id)}</code>
          <span class="badge ${kind === "human_seed" ? "badge-lit" : "badge-ai"}">${escapeHtml(kind)}</span>
          ${coParents.map((pid) => `<span class="badge badge-mode">併走親: ${escapeHtml(pid)}</span>`).join("")}
        </div>
        <div class="q-title">${escapeHtml(q.question)}</div>
        ${q.notes ? `<div style="font-size:0.82rem;color:var(--ink-muted);margin-bottom:0.55rem;">${escapeHtml(q.notes)}</div>` : ""}
        <div class="tag-row" style="margin-bottom:0;">
          ${linkedFrags.map((f) => renderEntityJumpButton("fragment", f.fragment_id)).join("")}
        </div>
        ${kids.length > 0 ? `<div class="q-branches">${kids.map((cid) => renderQuestionSubtree(state.maps.question.get(cid), true)).join("")}</div>` : ""}
      </div>
    `;
  }

  const container = document.getElementById("lineage-container");
  container.innerHTML = roots.map((r) => renderQuestionSubtree(r, false)).join("");
  bindJumpButtons(container);
}

/* 4. Materials Library */
function renderMaterials() {
  const grid = document.getElementById("materials-grid");
  const list = state.data.materials.filter(
    (m) => state.activeMatKind === "all" || m.kind === state.activeMatKind
  );

  grid.innerHTML = list
    .map((m) => {
      const isLit = m.kind === "literary_text";
      const isTrace = m.kind === "project_trace" || m.kind === "conversation_trace";
      const badgeCls = isLit ? "badge-lit" : (isTrace ? "badge-trace" : "badge-ai");
      const badgeLabel = isLit ? "哲学・文学原典" : (isTrace ? "プロジェクト痕跡" : "AIエージェント研究");
      const usedIn = state.data.fragments.filter((f) => (f.material_ids || []).includes(m.material_id));
      const authorLine = m.source && Array.isArray(m.source.authors) && m.source.authors.length
        ? `${m.source.authors.join(", ")} (${m.source.year})`
        : "";
      const prov = m.provenance;
      const provLine = prov
        ? `<div class="mat-provenance">原語 ${escapeHtml(prov.original_language)}`
          + `${prov.original_language !== prov.access_language ? ` → 参照 ${escapeHtml(prov.access_language)}` : ""}`
          + ` ／ 運び手: ${prov.carrier ? escapeHtml(prov.carrier) : "<span class=\"prov-blank\">（空欄）</span>"}</div>`
        : "";
      return `
        <article id="mcard-${escapeHtml(m.material_id)}" class="mat-card">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:0.5rem;">
            <code>${escapeHtml(m.material_id)}</code>
            <span class="badge ${badgeCls}">${badgeLabel}</span>
          </div>
          <h3 class="mat-title">${escapeHtml(m.title)}</h3>
          ${authorLine ? `<div style="font-size:0.78rem;color:var(--ink-muted);">${escapeHtml(authorLine)}</div>` : ""}
          ${provLine}
          ${m.literary_invitation ? `<div class="mat-invitation">問いへの誘い: ${escapeHtml(m.literary_invitation)}</div>` : ""}
          <blockquote class="mat-passage">${escapeHtml(m.passage)}</blockquote>
          ${usedIn.length > 0 ? `<div class="tag-row" style="margin-bottom:0;">${usedIn.map((f) => renderEntityJumpButton("fragment", f.fragment_id)).join("")}</div>` : ""}
          <div class="mat-scope">射程・編集覚書: ${escapeHtml(m.scope_note)}</div>
        </article>
      `;
    })
    .join("");

  bindJumpButtons(grid);
}

/* 5. Sessions Timeline */
function renderTimeline() {
  const listEl = document.getElementById("timeline-list");
  listEl.innerHTML = [...state.data.sessions]
    .reverse()
    .map((s) => `
      <div id="scard-${escapeHtml(s.session_id)}" class="session-card">
        <div style="display:flex;flex-wrap:wrap;justify-content:space-between;gap:0.5rem;margin-bottom:0.45rem;">
          <div><code>${escapeHtml(s.session_id)}</code> · <strong>${escapeHtml(s.started_at)}</strong></div>
          <span class="badge badge-ai">${escapeHtml(s.generator || "")}</span>
        </div>
        ${s.human_direction ? `<div style="font-size:0.8rem;color:var(--accent-indigo);margin-bottom:0.4rem;">方向づけ: ${escapeHtml(s.human_direction)}</div>` : ""}
        <p style="margin:0 0 0.7rem;font-size:0.9rem;line-height:1.75;white-space:pre-line;">${escapeHtml(s.notes || "")}</p>
        <div class="tag-row" style="margin-bottom:0;">
          ${(s.produced_fragment_ids || []).map((fid) => renderEntityJumpButton("fragment", fid)).join("")}
          ${(s.new_question_ids || []).map((qid) => renderEntityJumpButton("question", qid)).join("")}
          ${(s.context_material_ids || []).map((mid) => renderEntityJumpButton("material", mid)).join("")}
        </div>
      </div>
    `)
    .join("");

  bindJumpButtons(listEl);
}

/* 6. Voice Mirror & Close-Reading Notebooks */
function renderSimpleMarkdown(md) {
  const lines = String(md || "").split("\n");
  const out = [];
  let inList = false;
  let listTag = "ul";
  let inPre = false;
  let preBuf = [];

  const closeList = () => {
    if (inList) {
      out.push(`</${listTag}>`);
      inList = false;
    }
  };

  const inlineFmt = (s) =>
    escapeHtml(s)
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/\*([^*]+)\*/g, "<em>$1</em>");

  for (const rawLine of lines) {
    if (rawLine.startsWith("```")) {
      closeList();
      if (!inPre) {
        inPre = true;
        preBuf = [];
      } else {
        out.push(`<pre class="packet-pre" style="max-height:none;margin:0.8rem 0;">${escapeHtml(preBuf.join("\n"))}</pre>`);
        inPre = false;
      }
      continue;
    }
    if (inPre) {
      preBuf.push(rawLine);
      continue;
    }
    const line = rawLine.trimEnd();
    if (!line.trim()) {
      closeList();
      continue;
    }
    if (/^---+$/.test(line.trim())) {
      closeList();
      out.push("<hr/>");
      continue;
    }
    const hm = line.match(/^(#{1,4})\s+(.+)$/);
    if (hm) {
      closeList();
      const lvl = Math.min(3, hm[1].length);
      out.push(`<h${lvl}>${inlineFmt(hm[2])}</h${lvl}>`);
      continue;
    }
    if (line.startsWith(">")) {
      closeList();
      out.push(`<blockquote>${inlineFmt(line.replace(/^>\s?/, ""))}</blockquote>`);
      continue;
    }
    const ulm = line.match(/^\s*[-*]\s+(.+)$/);
    if (ulm) {
      if (!inList || listTag !== "ul") {
        closeList();
        listTag = "ul";
        inList = true;
        out.push("<ul>");
      }
      out.push(`<li>${inlineFmt(ulm[1])}</li>`);
      continue;
    }
    const olm = line.match(/^\s*\d+\.\s+(.+)$/);
    if (olm) {
      if (!inList || listTag !== "ol") {
        closeList();
        listTag = "ol";
        inList = true;
        out.push("<ol>");
      }
      out.push(`<li>${inlineFmt(olm[1])}</li>`);
      continue;
    }
    closeList();
    out.push(`<p>${inlineFmt(line)}</p>`);
  }
  closeList();
  return out.join("\n");
}

function renderMirrorView() {
  const auditPane = document.getElementById("mirror-audit-pane");
  const notePane = document.getElementById("mirror-notebooks-pane");
  const showAudit = state.activeMirrorPane === "audit";
  auditPane.hidden = !showAudit;
  notePane.hidden = showAudit;

  document.querySelectorAll("#mirror-subtab-group .pill-btn").forEach((b) => {
    b.classList.toggle("active", b.dataset.mirrorPane === state.activeMirrorPane);
  });

  if (showAudit) {
    const va = state.data.voice_audit;
    if (!va) {
      auditPane.innerHTML = `<div class="reader-pane"><div class="empty-state"><code>voice_audit</code> データがありません。</div></div>`;
      return;
    }
    const emptyModes = Object.entries(va.narrator_mode_counts || {})
      .filter(([, c]) => c === 0)
      .map(([m]) => m);

    auditPane.innerHTML = `
      <div class="mirror-grid">
        <div class="mirror-card">
          <h3>末尾の型（全 ${va.fragment_count} 編）</h3>
          <table class="mirror-table">
            <tbody>
              ${Object.entries(va.ending_summary || {}).map(([k, v]) => `<tr><td>${escapeHtml(k)}</td><td><strong>${v}</strong> 編</td></tr>`).join("")}
            </tbody>
          </table>
        </div>
        <div class="mirror-card">
          <h3>台帳が繰り返し使う身振り</h3>
          <table class="mirror-table">
            <tbody>
              ${(va.gestures || []).map((row) => `
                <tr>
                  <td>${escapeHtml(row.label)}</td>
                  <td><strong>${row.count}/${row.total}</strong> 編${row.note ? `<div style="font-size:0.75rem;color:var(--ink-muted);">${escapeHtml(row.note)}</div>` : ""}</td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
        <div class="mirror-card">
          <h3>反復密度上位（括弧引用の内外を分離）</h3>
          <table class="mirror-table">
            <thead><tr><th>断片</th><th>合計</th><th>地の文 / 引用内</th></tr></thead>
            <tbody>
              ${(va.density || []).slice(0, 9).map((d) => `
                <tr>
                  <td>${renderEntityJumpButton("fragment", d.fragment_id)}</td>
                  <td><strong>${d.hits}</strong></td>
                  <td>地の文 ${d.unquoted_hits} / 引用 ${d.hits - d.unquoted_hits}</td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
      </div>

      ${va.pronouns ? `
        <div class="reader-pane" style="margin-bottom:1.4rem;">
          <h3 style="margin-top:0;font-family:'Hiragino Mincho ProN','Yu Mincho',serif;">人称と名札の鏡（どの人称に寄りかかっているか）</h3>
          <table class="mirror-table">
            <thead><tr><th>人称・指標</th><th>出現編数</th><th>該当断片</th></tr></thead>
            <tbody>
              ${va.pronouns.map((p) => `
                <tr>
                  <td><strong>${escapeHtml(p.label)}</strong></td>
                  <td>${p.count}/${va.fragment_count} 編${p.count !== p.unquoted_count ? ` <span style="color:var(--ink-muted);font-size:0.78rem;">(括弧外=${p.unquoted_count}編)</span>` : ""}</td>
                  <td>${(p.fragment_ids || []).map((fid) => `<button type="button" class="link-pill" style="margin:0.12rem;" data-jump-frag="${escapeHtml(fid)}">${escapeHtml(fid)}</button>`).join("") || "—"}</td>
                </tr>
              `).join("")}
              <tr>
                <td><strong>人称代名詞ゼロ（無主語）</strong></td>
                <td>${(va.zero_pronoun_fragment_ids || []).length}/${va.fragment_count} 編</td>
                <td>${(va.zero_pronoun_fragment_ids || []).map((fid) => `<button type="button" class="link-pill" style="margin:0.12rem;" data-jump-frag="${escapeHtml(fid)}">${escapeHtml(fid)}</button>`).join("") || "—"}</td>
              </tr>
              <tr>
                <td><strong>未使用の narrator_mode</strong></td>
                <td colspan="2">${emptyModes.length ? emptyModes.map((m) => `<code>${escapeHtml(m)}</code>`).join(", ") : "なし"}</td>
              </tr>
              ${(va.mode_mismatches || []).map((mm) => `
                <tr>
                  <td><strong>名札と地の文のずれ</strong></td>
                  <td colspan="2">
                    <button type="button" class="link-pill" data-jump-frag="${escapeHtml(mm.fragment_id)}">${escapeHtml(mm.fragment_id)}</button>
                    <code>narrator_mode=${escapeHtml(mm.narrator_mode)}</code> だが地の文に <code>${escapeHtml(mm.found.join(", "))}</code>
                  </td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
      ` : ""}

      <div class="reader-pane" style="margin-bottom:1.4rem;">
        <h3 style="margin-top:0;font-family:'Hiragino Mincho ProN','Yu Mincho',serif;">各断片の末尾一文（先頭＋末尾の両端表示・省略隠れなし）</h3>
        <table class="mirror-table">
          <thead><tr><th style="width:150px;">断片</th><th style="width:140px;">末尾分類</th><th>最終文プレビュー</th></tr></thead>
          <tbody>
            ${(va.endings || []).map((e) => {
              const label = e.kind === "問いの形" ? e.subkind : e.kind;
              return `
                <tr>
                  <td><button type="button" class="link-pill" data-jump-frag="${escapeHtml(e.fragment_id)}">${escapeHtml(e.fragment_id)}</button></td>
                  <td><span class="badge ${e.kind === "問いの形" ? "badge-lit" : "badge-mode"}">${escapeHtml(label)}</span></td>
                  <td style="font-family:'Hiragino Mincho ProN','Yu Mincho',serif;">${escapeHtml(e.preview)}</td>
                </tr>
              `;
            }).join("")}
          </tbody>
        </table>
      </div>

      <div class="reader-pane">
        <h3 style="margin-top:0;font-family:'Hiragino Mincho ProN','Yu Mincho',serif;">編をまたいで使い回された ${va.gram_size} 文字列（全 ${va.repeated_gram_total} 種中 上位 ${(va.top_grams || []).length} 種）</h3>
        <table class="mirror-table">
          <thead><tr><th>文字列</th><th>編数</th><th>出現断片</th></tr></thead>
          <tbody>
            ${(va.top_grams || []).map((sg) => `
              <tr>
                <td><code>${escapeHtml(sg.gram)}</code></td>
                <td><strong>${sg.count}</strong> 編</td>
                <td>${(sg.owners || []).map((fid) => `<button type="button" class="link-pill" style="margin:0.12rem;" data-jump-frag="${escapeHtml(fid)}">${escapeHtml(fid)}</button>`).join("")}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
    bindJumpButtons(auditPane);
  } else {
    const notes = state.data.readings || [];
    if (notes.length === 0) {
      notePane.innerHTML = `<div class="reader-pane"><div class="empty-state">精読ノートがありません。</div></div>`;
      return;
    }
    const idx = Math.min(state.selectedNotebook, notes.length - 1);
    const current = notes[idx];
    notePane.innerHTML = `
      <div class="split-layout">
        <aside class="list-pane">
          <div class="filter-bar">
            <div style="font-size:0.82rem;font-weight:600;color:var(--ink-muted);">readings/ 収録ノート (${notes.length}冊)</div>
          </div>
          <div class="item-list">
            ${notes.map((n, i) => `
              <button type="button" class="frag-item ${i === idx ? "selected" : ""}" data-note-idx="${i}">
                <div class="frag-item-top"><code>${escapeHtml(n.filename)}</code></div>
                <div class="frag-item-title">${escapeHtml(n.title)}</div>
              </button>
            `).join("")}
          </div>
        </aside>
        <article class="reader-pane">
          <div class="notebook-markdown">${renderSimpleMarkdown(current.content)}</div>
        </article>
      </div>
    `;
    notePane.querySelectorAll("[data-note-idx]").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.selectedNotebook = Number(btn.dataset.noteIdx);
        renderMirrorView();
      });
    });
  }
}

/* 7. Context Packet Generator */
function populatePacketSelect() {
  const sel = document.getElementById("packet-question-select");
  if (!sel) return;
  const openQs = state.data.questions.filter((q) => q.status === "open");
  sel.innerHTML =
    `<option value="auto">自動推薦（まだ専用応答のない最新の問い）</option>` +
    openQs
      .map((q) => `<option value="${escapeHtml(q.question_id)}">${escapeHtml(q.question_id)}: ${escapeHtml(q.question.slice(0, 44))}…</option>`)
      .join("");
}

async function loadContextPacket() {
  const sel = document.getElementById("packet-question-select");
  const out = document.getElementById("packet-output");
  if (!sel || !out) return;
  const qid = sel.value || "auto";
  out.textContent = "コンテキスト・パケットを組み立てています…";
  try {
    const res = await fetch(`api/packet?question_id=${encodeURIComponent(qid)}`, { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const payload = await res.json();
    out.textContent = payload.packet;
  } catch (err) {
    out.textContent = `パケット生成APIの呼び出しに失敗しました（python3 tools/serve_viewer.py 経由で開いてください）: ${err.message}`;
  }
}

/* Theme & Event Wiring */
function setupEvents() {
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => switchView(btn.dataset.view));
  });

  ["frag-search", "filter-status", "filter-form", "filter-mode"].forEach((id) => {
    document.getElementById(id).addEventListener("input", renderFragmentList);
    document.getElementById(id).addEventListener("change", renderFragmentList);
  });

  document.querySelectorAll("#mat-kind-group .pill-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.activeMatKind = btn.dataset.matKind;
      document.querySelectorAll("#mat-kind-group .pill-btn").forEach((b) => {
        b.classList.toggle("active", b === btn);
      });
      renderMaterials();
    });
  });

  document.querySelectorAll("#mirror-subtab-group .pill-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.activeMirrorPane = btn.dataset.mirrorPane;
      renderMirrorView();
    });
  });

  const packetSel = document.getElementById("packet-question-select");
  if (packetSel) {
    packetSel.addEventListener("change", loadContextPacket);
  }
  const copyBtn = document.getElementById("copy-packet-btn");
  if (copyBtn) {
    copyBtn.addEventListener("click", async () => {
      const text = document.getElementById("packet-output").textContent;
      await navigator.clipboard.writeText(text);
      copyBtn.textContent = "コピーしました";
      setTimeout(() => { copyBtn.textContent = "パケットをコピー"; }, 1600);
    });
  }

  const themeBtn = document.getElementById("theme-toggle");
  themeBtn.addEventListener("click", () => {
    const html = document.documentElement;
    const next = html.getAttribute("data-theme") === "paper" ? "night" : "paper";
    html.setAttribute("data-theme", next);
    themeBtn.textContent = next === "paper" ? "夜想モード" : "紙面モード";
  });
}

async function init() {
  setupEvents();
  try {
    const data = await fetchArchive();
    indexData(data);
    renderStats();
    renderFragmentList();
    renderFragmentReader(state.selectedFragmentId);
    renderRelationFilterPills();
    renderLineage();
    renderMaterials();
    renderTimeline();
    populatePacketSelect();
  } catch (err) {
    document.getElementById("stats-strip").innerHTML = `<span style="color:var(--accent-crimson);font-size:0.86rem;">${escapeHtml(err.message)}</span>`;
  }
}

init();
