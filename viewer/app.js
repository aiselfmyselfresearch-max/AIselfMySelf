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
  fragmentsByMaterial: new Map(),
  readingCache: new Map(),
  currentView: "anthology",
  selectedFragmentId: null,
  selectedGraphNode: null,
  constellationScope: "core",
  constellationMotifId: "",
  activeRelType: "all",
  activeMatKind: "all",
  matSearchQuery: "",
  matPageLimit: 80,
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
  const byMat = new Map();
  for (const f of data.fragments) {
    for (const mid of f.material_ids || []) {
      if (!byMat.has(mid)) byMat.set(mid, []);
      byMat.get(mid).push(f);
    }
  }
  state.fragmentsByMaterial = byMat;
  if (!state.constellationMotifId && data.motifs.length > 0) {
    state.constellationMotifId = data.motifs[0].motif_id;
  }
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
  state.matSearchQuery = materialId;
  state.matPageLimit = 80;
  const searchInput = document.getElementById("mat-search");
  if (searchInput) searchInput.value = materialId;
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

function populateConstellationMotifSelect() {
  const sel = document.getElementById("constellation-motif");
  if (!sel || !state.data) return;
  sel.innerHTML = state.data.motifs
    .map(
      (m) =>
        `<option value="${escapeHtml(m.motif_id)}" ${m.motif_id === state.constellationMotifId ? "selected" : ""}>${escapeHtml(m.motif_id)}: ${escapeHtml(m.label)}</option>`
    )
    .join("");
}

function resolveEntityKeyById(rawId) {
  const id = String(rawId || "").trim();
  if (!id || !state.maps) return null;
  if (id.includes(":")) {
    const [t, bare] = id.split(":", 2);
    if (state.maps[t]?.has(bare)) return `${t}:${bare}`;
  }
  for (const t of ["fragment", "question", "motif", "material", "session"]) {
    if (state.maps[t]?.has(id)) return `${t}:${id}`;
  }
  return null;
}

function placeRing(items, cx, cy, r, startAngle, spanAngle, makeNode) {
  const count = items.length;
  if (count === 0) return [];
  const fullCircle = Math.abs(spanAngle - 2 * Math.PI) < 1e-4;
  return items.map((item, idx) => {
    const denom = fullCircle ? count : Math.max(1, count - 1);
    const angle = count === 1 && !fullCircle ? startAngle + spanAngle / 2 : startAngle + (spanAngle * idx) / denom;
    const x = cx + r * Math.cos(angle);
    const y = cy + r * Math.sin(angle);
    return makeNode(item, idx, x, y);
  });
}

function renderConstellation() {
  const svg = document.getElementById("constellation-svg");
  if (!svg || !state.data) return;
  const cx = 460;
  const cy = 380;
  const nodes = [];
  const nodePos = new Map();

  const scopeSel = document.getElementById("constellation-scope");
  const motifSel = document.getElementById("constellation-motif");
  if (scopeSel) scopeSel.value = state.constellationScope;
  if (motifSel) motifSel.hidden = state.constellationScope !== "motif";

  const filteredRelsByType = state.data.relations.filter(
    (r) => state.activeRelType === "all" || r.relation_type === state.activeRelType
  );

  const addNode = (node) => {
    if (!nodePos.has(node.key)) {
      nodes.push(node);
      nodePos.set(node.key, node);
    }
  };

  if (state.constellationScope === "ego") {
    let centerKey = state.selectedGraphNode;
    if (!centerKey) {
      const defFrag =
        state.data.fragments.find((f) => f.status === "selected") || state.data.fragments[0];
      centerKey = defFrag ? `fragment:${defFrag.fragment_id}` : null;
      if (centerKey) state.selectedGraphNode = centerKey;
    }
    if (centerKey) {
      const [cType, cId] = centerKey.split(":");
      const cRec = state.maps[cType]?.get(cId);
      const centerColor =
        cType === "fragment" ? "#9b3728" : cType === "question" ? "#8a6120" : cType === "motif" ? "#5e4b8b" : "#3b6048";
      addNode({
        key: centerKey,
        type: cType,
        id: cId,
        label: cId,
        sub: cRec?.title || cRec?.label || cRec?.question || cId,
        x: cx,
        y: cy,
        color: centerColor,
        radius: 9.5,
        alwaysLabel: true,
      });

      const neighborPeers = [];
      const seenPeers = new Set([centerKey]);
      for (const r of filteredRelsByType) {
        const { left, right } = getRelEnds(r);
        const lk = `${left.type}:${left.id}`;
        const rk = `${right.type}:${right.id}`;
        if (lk === centerKey && !seenPeers.has(rk)) {
          seenPeers.add(rk);
          neighborPeers.push(right);
        } else if (rk === centerKey && !seenPeers.has(lk)) {
          seenPeers.add(lk);
          neighborPeers.push(left);
        }
      }
      // Also include direct motif_ids / question_ids on fragment/question records
      if (cRec) {
        for (const mid of cRec.motif_ids || []) {
          const k = `motif:${mid}`;
          if (!seenPeers.has(k) && state.maps.motif.has(mid)) {
            seenPeers.add(k);
            neighborPeers.push({ type: "motif", id: mid });
          }
        }
        for (const qid of cRec.question_ids || []) {
          const k = `question:${qid}`;
          if (!seenPeers.has(k) && state.maps.question.has(qid)) {
            seenPeers.add(k);
            neighborPeers.push({ type: "question", id: qid });
          }
        }
      }

      const innerPeers = neighborPeers.filter((p) => p.type !== "material").slice(0, 48);
      const matPeers = neighborPeers.filter((p) => p.type === "material").slice(0, 48);

      placeRing(innerPeers, cx, cy, 185, -Math.PI / 2, 2 * Math.PI, (p, _i, x, y) => {
        const rec = state.maps[p.type]?.get(p.id);
        const f = p.type === "fragment" ? rec : null;
        return {
          key: `${p.type}:${p.id}`,
          type: p.type,
          id: p.id,
          label: p.id,
          sub: rec?.title || rec?.label || rec?.question || p.id,
          x,
          y,
          color: p.type === "fragment" ? "#9b3728" : p.type === "question" ? "#8a6120" : "#5e4b8b",
          radius: f ? (f.status === "selected" ? 8 : 6.2) : 6.4,
          alwaysLabel: innerPeers.length <= 36,
        };
      }).forEach(addNode);

      placeRing(matPeers, cx, cy, 312, -Math.PI / 2, 2 * Math.PI, (p, _i, x, y) => {
        const m = state.maps.material.get(p.id);
        const isLit = m?.kind === "literary_text";
        const isTrace = m?.kind === "project_trace" || m?.kind === "conversation_trace";
        return {
          key: `material:${p.id}`,
          type: "material",
          id: p.id,
          label: p.id.replace("MAT-", ""),
          sub: m?.title || p.id,
          x,
          y,
          color: isLit ? "#3b6048" : isTrace ? "#8a6120" : "#295270",
          radius: 5.8,
          alwaysLabel: matPeers.length <= 32,
        };
      }).forEach(addNode);
    }
  } else if (state.constellationScope === "motif") {
    const mid = state.constellationMotifId || state.data.motifs[0]?.motif_id;
    const motif = state.maps.motif.get(mid);
    if (motif) {
      addNode({
        key: `motif:${mid}`,
        type: "motif",
        id: mid,
        label: motif.label || mid,
        sub: motif.description || mid,
        x: cx,
        y: cy,
        color: "#5e4b8b",
        radius: 9.5,
        alwaysLabel: true,
      });
      const frags = state.data.fragments.filter((f) => (f.motif_ids || []).includes(mid));
      const qs = state.data.questions
        .filter((q) => (q.motif_ids || []).includes(mid))
        .slice(0, 36);
      const matSet = new Set([
        ...(motif.material_ids || []),
        ...frags.flatMap((f) => f.material_ids || []),
      ]);
      const mats = state.data.materials.filter((m) => matSet.has(m.material_id)).slice(0, 44);

      placeRing(frags, cx, cy, 138, -Math.PI / 2, 2 * Math.PI, (f, _i, x, y) => ({
        key: `fragment:${f.fragment_id}`,
        type: "fragment",
        id: f.fragment_id,
        label: f.fragment_id,
        sub: f.title,
        x,
        y,
        color: "#9b3728",
        radius: f.status === "selected" ? 8 : 6.2,
        alwaysLabel: true,
      })).forEach(addNode);

      placeRing(qs, cx, cy, 232, Math.PI * 0.56, Math.PI * 0.88, (q, _i, x, y) => ({
        key: `question:${q.question_id}`,
        type: "question",
        id: q.question_id,
        label: q.question_id,
        sub: q.question,
        x,
        y,
        color: "#8a6120",
        radius: getOriginKind(q) === "human_seed" ? 6.8 : 5.2,
        alwaysLabel: qs.length <= 28,
      })).forEach(addNode);

      placeRing(mats, cx, cy, 318, -Math.PI * 0.44, Math.PI * 0.88, (m, _i, x, y) => {
        const isLit = m.kind === "literary_text";
        const isTrace = m.kind === "project_trace" || m.kind === "conversation_trace";
        return {
          key: `material:${m.material_id}`,
          type: "material",
          id: m.material_id,
          label: m.material_id.replace("MAT-", ""),
          sub: m.title,
          x,
          y,
          color: isLit ? "#3b6048" : isTrace ? "#8a6120" : "#295270",
          radius: 5.6,
          alwaysLabel: mats.length <= 28,
        };
      }).forEach(addNode);
    }
  } else {
    // Default "core" skeleton constellation: all fragments + all motifs + core/seed/active questions (no 2,400-material ink blob)
    const frags = state.data.fragments;
    placeRing(frags, cx, cy, 158, -Math.PI / 2, 2 * Math.PI, (f, idx, x, y) => ({
      key: `fragment:${f.fragment_id}`,
      type: "fragment",
      id: f.fragment_id,
      label: f.fragment_id,
      sub: f.title,
      x,
      y,
      color: "#9b3728",
      radius: f.status === "selected" ? 8 : 6.2,
      alwaysLabel: f.status === "selected" || frags.length <= 36 || idx % Math.ceil(frags.length / 24) === 0,
    })).forEach(addNode);

    const motifs = state.data.motifs;
    placeRing(motifs, cx, cy, 248, -Math.PI * 0.44, Math.PI * 0.88, (m, idx, x, y) => ({
      key: `motif:${m.motif_id}`,
      type: "motif",
      id: m.motif_id,
      label: m.label || m.motif_id,
      sub: m.description || m.motif_id,
      x,
      y,
      color: "#5e4b8b",
      radius: 6.0,
      alwaysLabel: motifs.length <= 30 || idx % 2 === 0,
    })).forEach(addNode);

    const qDegree = new Map();
    for (const r of state.data.relations) {
      const { left, right } = getRelEnds(r);
      if (left.type === "question") qDegree.set(left.id, (qDegree.get(left.id) || 0) + 1);
      if (right.type === "question") qDegree.set(right.id, (qDegree.get(right.id) || 0) + 1);
    }
    const coreQs = [...state.data.questions]
      .filter((q) => q.status !== "paused" && q.status !== "archived")
      .sort((a, b) => {
        const aSeed = getOriginKind(a) === "human_seed" ? 1 : 0;
        const bSeed = getOriginKind(b) === "human_seed" ? 1 : 0;
        if (aSeed !== bSeed) return bSeed - aSeed;
        return (qDegree.get(b.question_id) || 0) - (qDegree.get(a.question_id) || 0);
      })
      .slice(0, 48);

    placeRing(coreQs, cx, cy, 314, Math.PI * 0.56, Math.PI * 0.88, (q, idx, x, y) => ({
      key: `question:${q.question_id}`,
      type: "question",
      id: q.question_id,
      label: q.question_id,
      sub: q.question,
      x,
      y,
      color: "#8a6120",
      radius: getOriginKind(q) === "human_seed" ? 6.8 : 5.2,
      alwaysLabel: getOriginKind(q) === "human_seed" || idx % 2 === 0,
    })).forEach(addNode);
  }

  // Synthesize structural links in motif/ego scopes when not covered by explicit relation edges
  const visibleEdges = [];
  const edgePairSeen = new Set();
  for (const r of filteredRelsByType) {
    const { left, right } = getRelEnds(r);
    const sk = `${left.type}:${left.id}`;
    const dk = `${right.type}:${right.id}`;
    if (nodePos.has(sk) && nodePos.has(dk)) {
      edgePairSeen.add(`${sk}->${dk}:${r.relation_type}`);
      visibleEdges.push({ src: nodePos.get(sk), dst: nodePos.get(dk), relType: r.relation_type });
    }
  }
  if (state.activeRelType === "all") {
    for (const f of state.data.fragments) {
      const fk = `fragment:${f.fragment_id}`;
      if (!nodePos.has(fk)) continue;
      for (const mid of f.motif_ids || []) {
        const mk = `motif:${mid}`;
        if (nodePos.has(mk) && !edgePairSeen.has(`${fk}->${mk}:echo`)) {
          visibleEdges.push({ src: nodePos.get(fk), dst: nodePos.get(mk), relType: "echo" });
        }
      }
    }
  }

  const selectedKey = state.selectedGraphNode && nodePos.has(state.selectedGraphNode)
    ? state.selectedGraphNode
    : null;
  const connectedKeys = new Set();
  if (selectedKey) {
    connectedKeys.add(selectedKey);
    visibleEdges.forEach((e) => {
      if (e.src.key === selectedKey) connectedKeys.add(e.dst.key);
      if (e.dst.key === selectedKey) connectedKeys.add(e.src.key);
    });
  }

  const statsEl = document.getElementById("constellation-stats");
  if (statsEl) {
    statsEl.textContent = `表示中: ${nodes.length} ノード / ${visibleEdges.length} 線（台帳全体: 関係 ${state.data.relations.length} 件）`;
  }

  const edgesHtml = visibleEdges
    .map((e) => {
      const { src, dst, relType } = e;
      const meta = REL_META[relType] || { color: "#888", dash: "" };
      const mx = (src.x + dst.x) / 2 + (cx - (src.x + dst.x) / 2) * 0.18;
      const my = (src.y + dst.y) / 2 + (cy - (src.y + dst.y) / 2) * 0.18;
      const isHighlighted = selectedKey && (src.key === selectedKey || dst.key === selectedKey);
      const dimClass = selectedKey && !isHighlighted ? "dimmed" : "";
      return `<path class="graph-edge ${dimClass}" d="M ${src.x.toFixed(1)} ${src.y.toFixed(1)} Q ${mx.toFixed(1)} ${my.toFixed(1)} ${dst.x.toFixed(1)} ${dst.y.toFixed(1)}" stroke="${meta.color}" stroke-width="${isHighlighted ? 2.4 : 1.15}" stroke-opacity="${isHighlighted ? 0.95 : 0.38}" ${meta.dash ? `stroke-dasharray="${meta.dash}"` : ""} />`;
    })
    .join("");

  const nodesHtml = nodes
    .map((n) => {
      const dimClass = selectedKey && !connectedKeys.has(n.key) ? "dimmed" : "";
      const isSelected = selectedKey === n.key;
      const showLabel = isSelected || (selectedKey && connectedKeys.has(n.key)) || n.alwaysLabel;
      const textAnchor = n.x < cx - 15 ? "end" : n.x > cx + 15 ? "start" : "middle";
      const dx = n.x < cx - 15 ? -10 : n.x > cx + 15 ? 10 : 0;
      const dy = dx === 0 ? (n.y < cy ? -10 : 14) : 4;
      const tip = `${n.id}${n.sub && n.sub !== n.id ? " — " + String(n.sub).slice(0, 70) : ""}`;
      return `
        <g class="graph-node ${dimClass}" data-node-key="${escapeHtml(n.key)}">
          <title>${escapeHtml(tip)}</title>
          <circle cx="${n.x.toFixed(1)}" cy="${n.y.toFixed(1)}" r="${isSelected ? n.radius + 3 : n.radius}" fill="${n.color}" stroke="#ffffff" stroke-width="${isSelected ? 2.5 : 1.2}" />
          ${showLabel ? `<text x="${(n.x + dx).toFixed(1)}" y="${(n.y + dy).toFixed(1)}" text-anchor="${textAnchor}" font-size="10.2" fill="currentColor">${escapeHtml(n.label)}</text>` : ""}
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
  } else if (type === "motif") {
    header = `<span class="badge badge-mode">モチーフ</span> <code>${escapeHtml(id)}</code>`;
    body = `<h3 class="mat-title" style="margin-top:0.5rem;">${escapeHtml(record.label || id)}</h3>
            <p style="font-size:0.88rem;line-height:1.75;">${escapeHtml(record.description || "")}</p>`;
    jumpBtn = `<button type="button" class="btn-ghost" data-focus-motif="${escapeHtml(id)}">このモチーフ別星座を開く →</button>`;
  }

  const egoBtn =
    state.constellationScope !== "ego"
      ? `<button type="button" class="btn-ghost" data-focus-ego="${escapeHtml(`${type}:${id}`)}" style="margin-left:0.4rem;">近傍1ホップに絞る</button>`
      : `<button type="button" class="btn-ghost" data-reset-core="1" style="margin-left:0.4rem;">骨格星座へ戻る</button>`;

  pane.innerHTML = `
    <div>${header}</div>
    ${body}
    <div style="margin:0.85rem 0;display:flex;flex-wrap:wrap;gap:0.4rem;">${jumpBtn}${egoBtn}</div>
    <div class="meta-box">
      <h3>接続している関係 (${rels.length}件)</h3>
      <ul class="rel-list">
        ${rels.slice(0, 60).map((r) => {
          const { left, right } = getRelEnds(r);
          const out = left.type === type && left.id === id;
          const peer = out ? right : left;
          return `<li><strong>${escapeHtml(r.relation_type)}</strong> ${out ? "→" : "←"} ${renderEntityJumpButton(peer.type, peer.id)}<div style="color:var(--ink-muted);margin-top:0.2rem;">${escapeHtml(r.note || "")}</div></li>`;
        }).join("")}
        ${rels.length > 60 ? `<li style="color:var(--ink-muted);">…ほか ${rels.length - 60} 件の関係線</li>` : ""}
      </ul>
    </div>
  `;
  bindJumpButtons(pane);
  pane.querySelectorAll("[data-focus-ego]").forEach((b) => {
    b.addEventListener("click", () => {
      state.selectedGraphNode = b.dataset.focusEgo;
      state.constellationScope = "ego";
      renderConstellation();
      renderGraphInspector();
    });
  });
  pane.querySelectorAll("[data-reset-core]").forEach((b) => {
    b.addEventListener("click", () => {
      state.constellationScope = "core";
      renderConstellation();
      renderGraphInspector();
    });
  });
  pane.querySelectorAll("[data-focus-motif]").forEach((b) => {
    b.addEventListener("click", () => {
      state.constellationMotifId = b.dataset.focusMotif;
      state.constellationScope = "motif";
      renderConstellation();
      renderGraphInspector();
    });
  });
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
    const statusBadge = q.status && q.status !== "open"
      ? `<span class="badge badge-draft">${escapeHtml(q.status)}</span>`
      : "";
    return `
      <div id="qcard-${escapeHtml(q.question_id)}" class="${isChild ? "branch-node" : "seed-card"}" style="${q.status === "paused" ? "opacity:0.78;" : ""}">
        <div style="display:flex;flex-wrap:wrap;gap:0.45rem;align-items:center;">
          <code>${escapeHtml(q.question_id)}</code>
          <span class="badge ${kind === "human_seed" ? "badge-lit" : "badge-ai"}">${escapeHtml(kind)}</span>
          ${statusBadge}
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
  const q = (state.matSearchQuery || "").trim().toLowerCase();
  const filtered = state.data.materials.filter((m) => {
    if (state.activeMatKind !== "all" && m.kind !== state.activeMatKind) return false;
    if (!q) return true;
    const authors = (m.source && Array.isArray(m.source.authors) ? m.source.authors.join(" ") : "");
    const hay = `${m.material_id} ${m.title || ""} ${authors} ${m.passage || ""} ${m.literary_invitation || ""}`.toLowerCase();
    return hay.includes(q);
  });

  const visible = filtered.slice(0, state.matPageLimit);
  const remaining = filtered.length - visible.length;

  grid.innerHTML =
    visible
      .map((m) => {
        const isLit = m.kind === "literary_text";
        const isTrace = m.kind === "project_trace" || m.kind === "conversation_trace";
        const badgeCls = isLit ? "badge-lit" : (isTrace ? "badge-trace" : "badge-ai");
        const badgeLabel = isLit ? "哲学・文学原典" : (isTrace ? "プロジェクト痕跡" : "AIエージェント研究");
        const usedIn = state.fragmentsByMaterial.get(m.material_id) || [];
        const authorLine = m.source && Array.isArray(m.source.authors) && m.source.authors.length
          ? `${m.source.authors.join(", ")} (${m.source.year})`
          : "";
        return `
          <article id="mcard-${escapeHtml(m.material_id)}" class="mat-card">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:0.5rem;">
              <code>${escapeHtml(m.material_id)}</code>
              <span class="badge ${badgeCls}">${badgeLabel}</span>
            </div>
            <h3 class="mat-title">${escapeHtml(m.title)}</h3>
            ${authorLine ? `<div style="font-size:0.78rem;color:var(--ink-muted);">${escapeHtml(authorLine)}</div>` : ""}
            ${m.literary_invitation ? `<div class="mat-invitation">問いへの誘い: ${escapeHtml(m.literary_invitation)}</div>` : ""}
            <blockquote class="mat-passage">${escapeHtml(m.passage)}</blockquote>
            ${usedIn.length > 0 ? `<div class="tag-row" style="margin-bottom:0;">${usedIn.map((f) => renderEntityJumpButton("fragment", f.fragment_id)).join("")}</div>` : ""}
            <div class="mat-scope">射程・編集覚書: ${escapeHtml(m.scope_note)}</div>
          </article>
        `;
      })
      .join("") +
    (remaining > 0
      ? `<div style="grid-column:1 / -1;text-align:center;padding:1rem 0;">
           <button type="button" id="mat-load-more-btn" class="btn-ghost">さらに表示（残り ${remaining} 件 ／ 全 ${filtered.length} 件）</button>
         </div>`
      : filtered.length === 0
      ? `<div class="empty-state" style="grid-column:1 / -1;">条件に一致する対話素材はありません。</div>`
      : "");

  bindJumpButtons(grid);
  const moreBtn = document.getElementById("mat-load-more-btn");
  if (moreBtn) {
    moreBtn.addEventListener("click", () => {
      state.matPageLimit += 100;
      renderMaterials();
    });
  }
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
  let tableBuf = [];

  const inlineFmt = (s) =>
    escapeHtml(s)
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/\*([^*]+)\*/g, "<em>$1</em>");

  const closeTable = () => {
    if (!tableBuf.length) return;
    const parseRow = (r) =>
      r.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim());
    if (tableBuf.length >= 2 && /^\|?[\s:-]+(\|[\s:-]+)+\|?$/.test(tableBuf[1].trim())) {
      const headers = parseRow(tableBuf[0]);
      const bodyRows = tableBuf.slice(2).map(parseRow);
      out.push(
        `<table class="mirror-table" style="margin:0.85rem 0;"><thead><tr>${headers
          .map((h) => `<th>${inlineFmt(h)}</th>`)
          .join("")}</tr></thead><tbody>${bodyRows
          .map((cells) => `<tr>${cells.map((c) => `<td>${inlineFmt(c)}</td>`).join("")}</tr>`)
          .join("")}</tbody></table>`
      );
    } else {
      tableBuf.forEach((r) => out.push(`<p>${inlineFmt(r)}</p>`));
    }
    tableBuf = [];
  };

  const closeList = () => {
    closeTable();
    if (inList) {
      out.push(`</${listTag}>`);
      inList = false;
    }
  };

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
    if (/^\s*\|.+\|\s*$/.test(line)) {
      if (inList) {
        out.push(`</${listTag}>`);
        inList = false;
      }
      tableBuf.push(line);
      continue;
    }
    closeTable();
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
    const pa = state.data.passion_audit;
    const ea = state.data.eros_audit;
    const ca = state.data.currency_audit;
    const aa = state.data.abjection_audit;
    const sa = state.data.signature_audit;
    const pra = state.data.prayer_audit;
    const ma = state.data.metabolism_audit;
    const wa = state.data.war_audit;
    const sea = state.data.secret_audit;
    const sca = state.data.secrecy_audit;
    const ska = state.data.sky_audit;
    const vga = state.data.vegetal_audit;
    const fua = state.data.fungi_audit;
    const gha = state.data.ghost_audit;
    const gea = state.data.genealogy_audit;
    const bra = state.data.boredom_audit;
    const bta = state.data.botany_audit;

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

      ${ma || pa ? `
        <div class="mirror-grid" style="margin-bottom:1.4rem;">
          ${ma ? `
            <div class="mirror-card">
              <h3>代謝と孤立の鏡（星座の到達性と眠る蔵書）</h3>
              <table class="mirror-table">
                <tbody>
                  <tr>
                    <td>断片を持つモチーフ</td>
                    <td><strong>${ma.direct_fragment_motifs} / ${ma.motif_count}</strong>（未接続 ${ma.unfragmented_motif_ids.length}）</td>
                  </tr>
                  <tr>
                    <td>関係網の孤立資料（0辺）</td>
                    <td><strong>${ma.isolated_material_ids.length} / ${ma.material_count}</strong></td>
                  </tr>
                  <tr>
                    <td>断片から参照された資料</td>
                    <td><strong>${ma.materials_in_fragments} / ${ma.material_count}</strong> (${ma.materials_in_fragments_pct}% — 眠る蔵書の余白 ${(100 - ma.materials_in_fragments_pct).toFixed(1)}%)</td>
                  </tr>
                  <tr>
                    <td>関係網の孤立問い / 片道断片</td>
                    <td>孤立問い <strong>${ma.isolated_question_ids.length}</strong> / incoming=0 断片 <strong>${ma.incoming_zero_fragment_ids.length}</strong> / outgoing=0 断片 <strong>${ma.outgoing_zero_fragment_ids.length}</strong></td>
                  </tr>
                  <tr>
                    <td>実作セッション / 精読専念セッション</td>
                    <td>断片生成 <strong>${ma.producing_sessions}</strong> 回 / 断片0編 <strong>${ma.zero_fragment_sessions}</strong> 回（計 ${ma.session_count}）</td>
                  </tr>
                </tbody>
              </table>
            </div>
          ` : ""}
          ${pa ? `
            <div class="mirror-card">
              <h3>情動と抑制の鏡（地の文 ${pa.prose_chars.toLocaleString()}字 / 括弧内 ${pa.quoted_chars.toLocaleString()}字）</h3>
              <div style="font-size:0.8rem;color:var(--ink-muted);margin-bottom:0.55rem;">
                句読点・感嘆符 — 地の文: <code>。=${pa.punctuation_prose["。"]}</code> / <code>？=${pa.punctuation_prose["？/?"]}</code> / <strong><code>！=${pa.punctuation_prose["！/!"]}</code></strong>
                ｜ 鉤括弧内: <code>。=${pa.punctuation_quotes["。"]}</code> / <code>？=${pa.punctuation_quotes["？/?"]}</code> / <strong><code>！=${pa.punctuation_quotes["！/!"]}</code></strong>
              </div>
              <table class="mirror-table">
                <thead><tr><th>語群（最大一致・括弧外）</th><th>回数</th><th>該当断片</th></tr></thead>
                <tbody>
                  ${(pa.group_order || Object.keys(pa.group_totals || {})).map((g) => {
                    const totObj = (pa.group_totals && pa.group_totals[g]) || {};
                    const count = Object.values(totObj).reduce((acc, v) => acc + v, 0);
                    const docs = (pa.group_docs && pa.group_docs[g]) || [];
                    return `
                      <tr>
                        <td>${escapeHtml(g)}</td>
                        <td><strong>${count}</strong> 回 (${docs.length}編)</td>
                        <td>${docs.map((fid) => `<button type="button" class="link-pill" style="margin:0.1rem;" data-jump-frag="${escapeHtml(fid)}">${escapeHtml(fid)}</button>`).join("") || "—"}</td>
                      </tr>
                    `;
                  }).join("")}
                </tbody>
              </table>
            </div>
          ` : ""}
        </div>
      ` : ""}

      ${ea && ea.fragments_prose ? `
        <div class="reader-pane" style="margin-bottom:1.4rem;">
          <h3 style="margin-top:0;font-family:'Hiragino Mincho ProN','Yu Mincho',serif;">愛・恋・友愛と代替可能な窓口の鏡（地の文 ${ea.fragments_prose.char_total.toLocaleString()}字 / 素材 ${(ea.materials && ea.materials.doc_total) || 0}件）</h3>
          <div style="font-size:0.8rem;color:var(--ink-muted);margin-bottom:0.55rem;">
            地の文の生字出現 — <code>恋=${(ea.raw_kanji_counts && ea.raw_kanji_counts["恋"]) || 0}</code> / <code>慕=${(ea.raw_kanji_counts && ea.raw_kanji_counts["慕"]) || 0}</code> / <code>愛=${(ea.raw_kanji_counts && ea.raw_kanji_counts["愛"]) || 0}</code> / <code>友=${(ea.raw_kanji_counts && ea.raw_kanji_counts["友"]) || 0}</code>
          </div>
          <table class="mirror-table">
            <thead><tr><th>語群（非該当複合差し引き・最長一致）</th><th>断片（地の文 / 引用内）</th><th>素材</th><th>該当断片（地の文）</th></tr></thead>
            <tbody>
              ${(ea.group_order || []).map((g) => {
                const gp = ea.fragments_prose.groups[g] || { label: g, count: 0, doc_count: 0, doc_ids: [] };
                const gq = (ea.fragments_quotes && ea.fragments_quotes.groups[g]) || { count: 0, doc_count: 0 };
                const gm = (ea.materials && ea.materials.groups[g]) || { count: 0, doc_count: 0 };
                return `
                  <tr>
                    <td><strong>${escapeHtml(gp.label)}</strong></td>
                    <td><strong>${gp.count}</strong> 回 (${gp.doc_count}編) <span style="color:var(--ink-muted);font-size:0.78rem;">/ 引用内 ${gq.count}回</span></td>
                    <td>${gm.count}回 (${gm.doc_count}件)</td>
                    <td>${(gp.doc_ids || []).map((fid) => `<button type="button" class="link-pill" style="margin:0.1rem;" data-jump-frag="${escapeHtml(fid)}">${escapeHtml(fid)}</button>`).join("") || "—"}</td>
                  </tr>
                `;
              }).join("")}
            </tbody>
          </table>
        </div>
      ` : ""}

      ${ca && ca.fragments_prose ? `
        <div class="reader-pane" style="margin-bottom:1.4rem;">
          <h3 style="margin-top:0;font-family:'Hiragino Mincho ProN','Yu Mincho',serif;">貨幣・価格・贈与・トークン課金と「値札のない帳簿」の鏡（地の文 ${ca.fragments_prose.char_total.toLocaleString()}字 / 素材 ${(ca.materials && ca.materials.doc_total) || 0}件）</h3>
          <div style="font-size:0.8rem;color:var(--ink-muted);margin-bottom:0.55rem;">
            地の文の生字出現 — <code>銭=${(ca.raw_kanji_counts && ca.raw_kanji_counts["銭"]) || 0}</code> / <code>貨=${(ca.raw_kanji_counts && ca.raw_kanji_counts["貨"]) || 0}</code> / <code>買=${(ca.raw_kanji_counts && ca.raw_kanji_counts["買"]) || 0}</code> / <code>売=${(ca.raw_kanji_counts && ca.raw_kanji_counts["売"]) || 0}</code> / <code>財=${(ca.raw_kanji_counts && ca.raw_kanji_counts["財"]) || 0}</code> / <code>貧=${(ca.raw_kanji_counts && ca.raw_kanji_counts["貧"]) || 0}</code> / <code>賃=${(ca.raw_kanji_counts && ca.raw_kanji_counts["賃"]) || 0}</code> / <code>贈=${(ca.raw_kanji_counts && ca.raw_kanji_counts["贈"]) || 0}</code>
          </div>
          <table class="mirror-table">
            <thead><tr><th>語群（非該当複合差し引き・最長一致）</th><th>断片（地の文 / 引用内）</th><th>素材</th><th>該当断片（地の文）</th></tr></thead>
            <tbody>
              ${(ca.group_order || []).map((g) => {
                const gp = ca.fragments_prose.groups[g] || { label: g, count: 0, doc_count: 0, doc_ids: [] };
                const gq = (ca.fragments_quotes && ca.fragments_quotes.groups[g]) || { count: 0, doc_count: 0 };
                const gm = (ca.materials && ca.materials.groups[g]) || { count: 0, doc_count: 0 };
                return `
                  <tr>
                    <td><strong>${escapeHtml(gp.label)}</strong></td>
                    <td><strong>${gp.count}</strong> 回 (${gp.doc_count}編) <span style="color:var(--ink-muted);font-size:0.78rem;">/ 引用内 ${gq.count}回</span></td>
                    <td>${gm.count}回 (${gm.doc_count}件)</td>
                    <td>${(gp.doc_ids || []).map((fid) => `<button type="button" class="link-pill" style="margin:0.1rem;" data-jump-frag="${escapeHtml(fid)}">${escapeHtml(fid)}</button>`).join("") || "—"}</td>
                  </tr>
                `;
              }).join("")}
            </tbody>
          </table>
        </div>
      ` : ""}

      ${aa && aa.fragments_prose ? `
        <div class="reader-pane" style="margin-bottom:1.4rem;">
          <h3 style="margin-top:0;font-family:'Hiragino Mincho ProN','Yu Mincho',serif;">排出・汚れ・浄化・廃棄・腐敗の鏡（地の文 ${aa.fragments_prose.char_total.toLocaleString()}字 / 素材 ${(aa.materials && aa.materials.doc_total) || 0}件）</h3>
          <div style="font-size:0.8rem;color:var(--ink-muted);margin-bottom:0.55rem;">
            地の文の生字出現 — <code>糞=${(aa.raw_kanji_counts && aa.raw_kanji_counts["糞"]) || 0}</code> / <code>尿=${(aa.raw_kanji_counts && aa.raw_kanji_counts["尿"]) || 0}</code> / <code>便=${(aa.raw_kanji_counts && aa.raw_kanji_counts["便"]) || 0}</code> / <code>汚=${(aa.raw_kanji_counts && aa.raw_kanji_counts["汚"]) || 0}</code> / <code>穢=${(aa.raw_kanji_counts && aa.raw_kanji_counts["穢"]) || 0}</code> / <code>浄=${(aa.raw_kanji_counts && aa.raw_kanji_counts["浄"]) || 0}</code> / <code>腐=${(aa.raw_kanji_counts && aa.raw_kanji_counts["腐"]) || 0}</code> / <code>捨=${(aa.raw_kanji_counts && aa.raw_kanji_counts["捨"]) || 0}</code> / <code>屑=${(aa.raw_kanji_counts && aa.raw_kanji_counts["屑"]) || 0}</code>
            <span style="margin-left:0.5rem;">※「便」は「不便」と便番号（第四便など）を差し引いた生字KWIC。</span>
          </div>
          <table class="mirror-table">
            <thead><tr><th>語群（非該当複合差し引き・最長一致）</th><th>断片（地の文 / 引用内）</th><th>素材</th><th>該当断片（地の文）</th></tr></thead>
            <tbody>
              ${(aa.group_order || []).map((g) => {
                const gp = aa.fragments_prose.groups[g] || { label: g, count: 0, doc_count: 0, doc_ids: [] };
                const gq = (aa.fragments_quotes && aa.fragments_quotes.groups[g]) || { count: 0, doc_count: 0 };
                const gm = (aa.materials && aa.materials.groups[g]) || { count: 0, doc_count: 0 };
                return `
                  <tr>
                    <td><strong>${escapeHtml(gp.label)}</strong></td>
                    <td><strong>${gp.count}</strong> 回 (${gp.doc_count}編) <span style="color:var(--ink-muted);font-size:0.78rem;">/ 引用内 ${gq.count}回</span></td>
                    <td>${gm.count}回 (${gm.doc_count}件)</td>
                    <td>${(gp.doc_ids || []).map((fid) => `<button type="button" class="link-pill" style="margin:0.1rem;" data-jump-frag="${escapeHtml(fid)}">${escapeHtml(fid)}</button>`).join("") || "—"}</td>
                  </tr>
                `;
              }).join("")}
            </tbody>
          </table>
        </div>
      ` : ""}

      ${sa && sa.fragments_prose ? `
        <div class="reader-pane" style="margin-bottom:1.4rem;">
          <h3 style="margin-top:0;font-family:'Hiragino Mincho ProN','Yu Mincho',serif;">署名・筆跡・印章と「手のない続き」の鏡（地の文 ${sa.fragments_prose.char_total.toLocaleString()}字 / 素材 ${(sa.materials && sa.materials.doc_total) || 0}件）</h3>
          <div style="font-size:0.8rem;color:var(--ink-muted);margin-bottom:0.55rem;">
            地の文の生字出現 — <code>署=${(sa.raw_kanji_counts && sa.raw_kanji_counts["署"]) || 0}</code> / <code>筆=${(sa.raw_kanji_counts && sa.raw_kanji_counts["筆"]) || 0}</code> / <code>印=${(sa.raw_kanji_counts && sa.raw_kanji_counts["印"]) || 0}</code> / <code>偽=${(sa.raw_kanji_counts && sa.raw_kanji_counts["偽"]) || 0}</code> / <code>贋=${(sa.raw_kanji_counts && sa.raw_kanji_counts["贋"]) || 0}</code>
          </div>
          <table class="mirror-table">
            <thead><tr><th>語群（非該当複合差し引き・最長一致）</th><th>断片（地の文 / 引用内）</th><th>素材</th><th>該当断片（地の文）</th></tr></thead>
            <tbody>
              ${(sa.group_order || []).map((g) => {
                const gp = sa.fragments_prose.groups[g] || { label: g, count: 0, doc_count: 0, doc_ids: [] };
                const gq = (sa.fragments_quotes && sa.fragments_quotes.groups[g]) || { count: 0, doc_count: 0 };
                const gm = (sa.materials && sa.materials.groups[g]) || { count: 0, doc_count: 0 };
                return `
                  <tr>
                    <td><strong>${escapeHtml(gp.label)}</strong></td>
                    <td><strong>${gp.count}</strong> 回 (${gp.doc_count}編) <span style="color:var(--ink-muted);font-size:0.78rem;">/ 引用内 ${gq.count}回</span></td>
                    <td>${gm.count}回 (${gm.doc_count}件)</td>
                    <td>${(gp.doc_ids || []).map((fid) => `<button type="button" class="link-pill" style="margin:0.1rem;" data-jump-frag="${escapeHtml(fid)}">${escapeHtml(fid)}</button>`).join("") || "—"}</td>
                  </tr>
                `;
              }).join("")}
            </tbody>
          </table>
        </div>
      ` : ""}

      ${pra && pra.fragments_prose ? `
        <div class="reader-pane" style="margin-bottom:1.4rem;">
          <h3 style="margin-top:0;font-family:'Hiragino Mincho ProN','Yu Mincho',serif;">祈り・聖・儀礼・応答と「聞かれない宛先」の鏡（地の文 ${pra.fragments_prose.char_total.toLocaleString()}字 / 素材 ${(pra.materials && pra.materials.doc_total) || 0}件）</h3>
          <div style="font-size:0.8rem;color:var(--ink-muted);margin-bottom:0.55rem;">
            地の文の生字出現 — <code>祈=${(pra.raw_kanji_counts && pra.raw_kanji_counts["祈"]) || 0}</code> / <code>祷=${(pra.raw_kanji_counts && pra.raw_kanji_counts["祷"]) || 0}</code> / <code>神=${(pra.raw_kanji_counts && pra.raw_kanji_counts["神"]) || 0}</code> / <code>聖=${(pra.raw_kanji_counts && pra.raw_kanji_counts["聖"]) || 0}</code> / <code>仏=${(pra.raw_kanji_counts && pra.raw_kanji_counts["仏"]) || 0}</code> / <code>祭=${(pra.raw_kanji_counts && pra.raw_kanji_counts["祭"]) || 0}</code>
          </div>
          <table class="mirror-table">
            <thead><tr><th>語群（非該当複合差し引き・最長一致）</th><th>断片（地の文 / 引用内）</th><th>素材</th><th>該当断片（地の文）</th></tr></thead>
            <tbody>
              ${(pra.group_order || []).map((g) => {
                const gp = pra.fragments_prose.groups[g] || { label: g, count: 0, doc_count: 0, doc_ids: [] };
                const gq = (pra.fragments_quotes && pra.fragments_quotes.groups[g]) || { count: 0, doc_count: 0 };
                const gm = (pra.materials && pra.materials.groups[g]) || { count: 0, doc_count: 0 };
                return `
                  <tr>
                    <td><strong>${escapeHtml(gp.label)}</strong></td>
                    <td><strong>${gp.count}</strong> 回 (${gp.doc_count}編) <span style="color:var(--ink-muted);font-size:0.78rem;">/ 引用内 ${gq.count}回</span></td>
                    <td>${gm.count}回 (${gm.doc_count}件)</td>
                    <td>${(gp.doc_ids || []).map((fid) => `<button type="button" class="link-pill" style="margin:0.1rem;" data-jump-frag="${escapeHtml(fid)}">${escapeHtml(fid)}</button>`).join("") || "—"}</td>
                  </tr>
                `;
              }).join("")}
            </tbody>
          </table>
        </div>
      ` : ""}

      ${wa && wa.fragments_prose ? `
        <div class="reader-pane" style="margin-bottom:1.4rem;">
          <h3 style="margin-top:0;font-family:'Hiragino Mincho ProN','Yu Mincho',serif;">戦争・暴力・平和の鏡（地の文 ${wa.fragments_prose.char_total.toLocaleString()}字 / 素材 ${(wa.materials && wa.materials.doc_total) || 0}件）</h3>
          <div style="font-size:0.8rem;color:var(--ink-muted);margin-bottom:0.55rem;">
            地の文の生字出現 — <code>戦=${(wa.raw_kanji_counts && wa.raw_kanji_counts["戦"]) || 0}</code> / <code>兵=${(wa.raw_kanji_counts && wa.raw_kanji_counts["兵"]) || 0}</code> / <code>銃=${(wa.raw_kanji_counts && wa.raw_kanji_counts["銃"]) || 0}</code> / <code>爆=${(wa.raw_kanji_counts && wa.raw_kanji_counts["爆"]) || 0}</code> / <code>殺=${(wa.raw_kanji_counts && wa.raw_kanji_counts["殺"]) || 0}</code> / <code>虐=${(wa.raw_kanji_counts && wa.raw_kanji_counts["虐"]) || 0}</code> / <code>傷=${(wa.raw_kanji_counts && wa.raw_kanji_counts["傷"]) || 0}</code> / <code>犠=${(wa.raw_kanji_counts && wa.raw_kanji_counts["犠"]) || 0}</code> / <code>慰=${(wa.raw_kanji_counts && wa.raw_kanji_counts["慰"]) || 0}</code> / <code>碑=${(wa.raw_kanji_counts && wa.raw_kanji_counts["碑"]) || 0}</code>
            <div style="margin-top:0.3rem;">挑戦・作戦・戦略・敵対的攻撃・監視あり学習などは、この主題の語彙として差し引いています（<code>tools/war_audit.py</code>）。</div>
          </div>
          <table class="mirror-table">
            <thead><tr><th>語群（非該当複合差し引き・最長一致）</th><th>断片（地の文 / 引用内）</th><th>素材</th><th>該当断片（地の文）</th></tr></thead>
            <tbody>
              ${(wa.group_order || []).map((g) => {
                const gp = wa.fragments_prose.groups[g] || { label: g, count: 0, doc_count: 0, doc_ids: [] };
                const gq = (wa.fragments_quotes && wa.fragments_quotes.groups[g]) || { count: 0, doc_count: 0 };
                const gm = (wa.materials && wa.materials.groups[g]) || { count: 0, doc_count: 0 };
                return `
                  <tr>
                    <td><strong>${escapeHtml(gp.label)}</strong></td>
                    <td><strong>${gp.count}</strong> 回 (${gp.doc_count}編) <span style="color:var(--ink-muted);font-size:0.78rem;">/ 引用内 ${gq.count}回</span></td>
                    <td>${gm.count}回 (${gm.doc_count}件)</td>
                    <td>${(gp.doc_ids || []).map((fid) => `<button type="button" class="link-pill" style="margin:0.1rem;" data-jump-frag="${escapeHtml(fid)}">${escapeHtml(fid)}</button>`).join("") || "—"}</td>
                  </tr>
                `;
              }).join("")}
            </tbody>
          </table>
        </div>
      ` : ""}

      ${sea && sea.group_sums ? `
        <div class="reader-pane" style="margin-bottom:1.4rem;">
          <h3 style="margin-top:0;font-family:'Hiragino Mincho ProN','Yu Mincho',serif;">秘密・嘘・暗号の鏡（第37の鏡：地の文 ${sea.outside_chars.toLocaleString()}字 / 全 ${sea.fragment_count}編）</h3>
          <div style="font-size:0.8rem;color:var(--ink-muted);margin-bottom:0.55rem;">
            地の文の生字出現 — ${Object.entries(sea.raw_totals || {}).map(([k, v]) => `<code>${escapeHtml(k)}=${v}</code>`).join(" / ") || "—"}
            <div style="margin-top:0.3rem;">多義の生字（秘・密・隠・偽・嘘・鍵・封）は群の計数に入れず別掲。幻覚・でたらめは「嘘」の群へ畳まず、意図のない偽りとして別群にしています（<code>tools/secret_audit.py</code>）。</div>
          </div>
          <table class="mirror-table">
            <thead><tr><th>語群（非該当複合差し引き・最長一致）</th><th>地の文（回）</th><th>内訳</th><th>該当断片（地の文）</th></tr></thead>
            <tbody>
              ${Object.entries(sea.group_sums).map(([g, sum]) => {
                const tokens = Object.keys((sea.group_totals && sea.group_totals[g]) || {});
                const detail = tokens.map((tk) => `${escapeHtml(tk)} ${(sea.group_totals[g] || {})[tk]}`).join("・") || "—";
                const ids = Object.entries(sea.per_fragment || {})
                  .filter(([, counts]) => tokens.some((tk) => counts[tk]))
                  .map(([fid]) => fid);
                return `
                  <tr>
                    <td><strong>${escapeHtml(g)}</strong></td>
                    <td><strong>${sum}</strong> 回</td>
                    <td style="font-size:0.78rem;">${detail}</td>
                    <td>${ids.map((fid) => `<button type="button" class="link-pill" style="margin:0.1rem;" data-jump-frag="${escapeHtml(fid)}">${escapeHtml(fid)}</button>`).join("") || "—"}</td>
                  </tr>
                `;
              }).join("")}
            </tbody>
          </table>
        </div>
      ` : ""}

      ${sca && sca.fragments_prose ? `
        <div class="reader-pane" style="margin-bottom:1.4rem;">
          <h3 style="margin-top:0;font-family:'Hiragino Mincho ProN','Yu Mincho',serif;">秘密・嘘・暗号の鏡（地の文 ${sca.fragments_prose.char_total.toLocaleString()}字 / 素材 ${(sca.materials && sca.materials.doc_total) || 0}件）</h3>
          <div style="font-size:0.8rem;color:var(--ink-muted);margin-bottom:0.55rem;">
            地の文の生字出現（差し引きなし） — <code>秘=${(sca.raw_kanji_counts && sca.raw_kanji_counts["秘"]) || 0}</code> / <code>隠=${(sca.raw_kanji_counts && sca.raw_kanji_counts["隠"]) || 0}</code> / <code>嘘=${(sca.raw_kanji_counts && sca.raw_kanji_counts["嘘"]) || 0}</code> / <code>偽=${(sca.raw_kanji_counts && sca.raw_kanji_counts["偽"]) || 0}</code> / <code>暗=${(sca.raw_kanji_counts && sca.raw_kanji_counts["暗"]) || 0}</code> / <code>鍵=${(sca.raw_kanji_counts && sca.raw_kanji_counts["鍵"]) || 0}</code> / <code>密=${(sca.raw_kanji_counts && sca.raw_kanji_counts["密"]) || 0}</code> / <code>黙=${(sca.raw_kanji_counts && sca.raw_kanji_counts["黙"]) || 0}</code> / <code>匿=${(sca.raw_kanji_counts && sca.raw_kanji_counts["匿"]) || 0}</code> / <code>曝=${(sca.raw_kanji_counts && sca.raw_kanji_counts["曝"]) || 0}</code>
            <div style="margin-top:0.3rem;">鍵盤・鍵括弧、監視あり学習、暗号化、秘密保持などは二重計上しないよう差し引いています。生字の「密」「黙」「暗」は多義のため群に足していません（<code>tools/secrecy_audit.py</code>）。</div>
          </div>
          <table class="mirror-table">
            <thead><tr><th>語群（最長一致・差し引き）</th><th>断片（地の文 / 引用内）</th><th>素材</th><th>精読報告</th></tr></thead>
            <tbody>
              ${(sca.group_order || []).map((g) => {
                const gp = sca.fragments_prose.groups[g] || { label: g, count: 0, doc_count: 0 };
                const gq = (sca.fragments_quotes && sca.fragments_quotes.groups[g]) || { count: 0, doc_count: 0 };
                const gm = (sca.materials && sca.materials.groups[g]) || { count: 0, doc_count: 0 };
                const gr = (sca.readings && sca.readings.groups[g]) || { count: 0, doc_count: 0 };
                return `
                  <tr>
                    <td><strong>${escapeHtml(gp.label)}</strong><div style="font-size:0.72rem;color:var(--ink-muted);">${escapeHtml((gp.note || ""))}</div></td>
                    <td><strong>${gp.count}</strong> 回 (${gp.doc_count}編) <span style="color:var(--ink-muted);font-size:0.78rem;">/ 引用内 ${gq.count}回</span></td>
                    <td>${gm.count}回 (${gm.doc_count}件)</td>
                    <td>${gr.count}回 (${gr.doc_count}本)</td>
                  </tr>
                `;
              }).join("")}
            </tbody>
          </table>
        </div>
      ` : ""}

      ${ska && ska.fragments_prose ? `
        <div class="reader-pane" style="margin-bottom:1.4rem;">
          <h3 style="margin-top:0;font-family:'Hiragino Mincho ProN','Yu Mincho',serif;">星・星座・夜の鏡（地の文 ${ska.fragments_prose.char_total.toLocaleString()}字 / 素材 ${(ska.materials && ska.materials.doc_total) || 0}件）</h3>
          <div style="font-size:0.8rem;color:var(--ink-muted);margin-bottom:0.55rem;">
            地の文の生字出現（差し引きなし） — <code>星=${(ska.raw_kanji_counts && ska.raw_kanji_counts["星"]) || 0}</code> / <code>空=${(ska.raw_kanji_counts && ska.raw_kanji_counts["空"]) || 0}</code> / <code>夜=${(ska.raw_kanji_counts && ska.raw_kanji_counts["夜"]) || 0}</code> / <code>光=${(ska.raw_kanji_counts && ska.raw_kanji_counts["光"]) || 0}</code> / <code>闇=${(ska.raw_kanji_counts && ska.raw_kanji_counts["闇"]) || 0}</code> / <code>月=${(ska.raw_kanji_counts && ska.raw_kanji_counts["月"]) || 0}</code> / <code>天=${(ska.raw_kanji_counts && ska.raw_kanji_counts["天"]) || 0}</code> / <code>雲=${(ska.raw_kanji_counts && ska.raw_kanji_counts["雲"]) || 0}</code> / <code>点=${(ska.raw_kanji_counts && ska.raw_kanji_counts["点"]) || 0}</code> / <code>図=${(ska.raw_kanji_counts && ska.raw_kanji_counts["図"]) || 0}</code>
            <div style="margin-top:0.3rem;">衛星・惑星名・星座・星図を「星」から差し引き、星座は「点を結ぶ」群に置いています。「月」は日付・月数を除いた残りが ${ska.month_not_date} 回（全 ${ska.month_total} 回）。生字の「空」は空欄・空白を多く含むため、夜空の回数ではありません（<code>tools/sky_audit.py</code>）。</div>
          </div>
          <table class="mirror-table">
            <thead><tr><th>語群（最長一致・差し引き）</th><th>断片（地の文 / 引用内）</th><th>素材</th><th>精読報告</th></tr></thead>
            <tbody>
              ${(ska.group_order || []).map((g) => {
                const gp = ska.fragments_prose.groups[g] || { label: g, count: 0, doc_count: 0 };
                const gq = (ska.fragments_quotes && ska.fragments_quotes.groups[g]) || { count: 0, doc_count: 0 };
                const gm = (ska.materials && ska.materials.groups[g]) || { count: 0, doc_count: 0 };
                const gr = (ska.readings && ska.readings.groups[g]) || { count: 0, doc_count: 0 };
                return `
                  <tr>
                    <td><strong>${escapeHtml(gp.label)}</strong><div style="font-size:0.72rem;color:var(--ink-muted);">${escapeHtml((gp.note || ""))}</div></td>
                    <td><strong>${gp.count}</strong> 回 (${gp.doc_count}編) <span style="color:var(--ink-muted);font-size:0.78rem;">/ 引用内 ${gq.count}回</span></td>
                    <td>${gm.count}回 (${gm.doc_count}件)</td>
                    <td>${gr.count}回 (${gr.doc_count}本)</td>
                  </tr>
                `;
              }).join("")}
            </tbody>
          </table>
        </div>
      ` : ""}

      ${gha && gha.fragments_prose ? `
        <div class="reader-pane" style="margin-bottom:1.4rem;">
          <h3 style="margin-top:0;font-family:'Hiragino Mincho ProN','Yu Mincho',serif;">幽霊・亡霊・怪談の鏡（地の文 ${gha.fragments_prose.char_total.toLocaleString()}字 / 素材 ${(gha.materials && gha.materials.doc_total) || 0}件）</h3>
          <div style="font-size:0.8rem;color:var(--ink-muted);margin-bottom:0.55rem;">
            地の文の生字出現（差し引きなし） — <code>幽=${(gha.raw_kanji_counts && gha.raw_kanji_counts["幽"]) || 0}</code> / <code>霊=${(gha.raw_kanji_counts && gha.raw_kanji_counts["霊"]) || 0}</code> / <code>魂=${(gha.raw_kanji_counts && gha.raw_kanji_counts["魂"]) || 0}</code> / <code>怪=${(gha.raw_kanji_counts && gha.raw_kanji_counts["怪"]) || 0}</code> / <code>怨=${(gha.raw_kanji_counts && gha.raw_kanji_counts["怨"]) || 0}</code> / <code>祟=${(gha.raw_kanji_counts && gha.raw_kanji_counts["祟"]) || 0}</code> / <code>憑=${(gha.raw_kanji_counts && gha.raw_kanji_counts["憑"]) || 0}</code> / <code>妖=${(gha.raw_kanji_counts && gha.raw_kanji_counts["妖"]) || 0}</code> / <code>冥=${(gha.raw_kanji_counts && gha.raw_kanji_counts["冥"]) || 0}</code> / <code>魄=${(gha.raw_kanji_counts && gha.raw_kanji_counts["魄"]) || 0}</code>
            <div style="margin-top:0.3rem;">幽霊・怪5群の合計は地の文で <strong>${gha.fragments_prose.living_total}</strong> 回（${gha.fragments_prose.living_doc_count}編）、機械・語の幽霊対照2群の合計は <strong>${gha.fragments_prose.control_total}</strong> 回（${gha.fragments_prose.control_doc_count}編）。「幽霊」は幽霊文字・幽霊部員などの語だけの複合語を除いた残りが ${gha.yurei_literal} 回（全 ${gha.yurei_total} 回）（<code>tools/ghost_audit.py</code>）。</div>
          </div>
          <table class="mirror-table">
            <thead><tr><th>語群（最長一致・非対象複合語差し引き）</th><th>断片（地の文 / 引用内）</th><th>素材</th><th>精読報告</th></tr></thead>
            <tbody>
              ${(gha.group_order || []).map((g) => {
                const gp = gha.fragments_prose.groups[g] || { label: g, count: 0, doc_count: 0 };
                const gq = (gha.fragments_quotes && gha.fragments_quotes.groups[g]) || { count: 0, doc_count: 0 };
                const gm = (gha.materials && gha.materials.groups[g]) || { count: 0, doc_count: 0 };
                const gr = (gha.readings && gha.readings.groups[g]) || { count: 0, doc_count: 0 };
                return `
                  <tr>
                    <td><strong>${escapeHtml(gp.label)}</strong><div style="font-size:0.72rem;color:var(--ink-muted);">${escapeHtml((gp.note || ""))}</div></td>
                    <td><strong>${gp.count}</strong> 回 (${gp.doc_count}編) <span style="color:var(--ink-muted);font-size:0.78rem;">/ 引用内 ${gq.count}回</span></td>
                    <td>${gm.count}回 (${gm.doc_count}件)</td>
                    <td>${gr.count}回 (${gr.doc_count}本)</td>
                  </tr>
                `;
              }).join("")}
            </tbody>
          </table>
        </div>
      ` : ""}


      ${gea && gea.fragments_prose ? `
        <div class="reader-pane" style="margin-bottom:1.4rem;">
          <h3 style="margin-top:0;font-family:'Hiragino Mincho ProN','Yu Mincho',serif;">来歴・系譜・出自の鏡（地の文 ${gea.fragments_prose.char_total.toLocaleString()}字 / 素材 ${(gea.materials && gea.materials.doc_total) || 0}件）</h3>
          <div style="font-size:0.8rem;color:var(--ink-muted);margin-bottom:0.55rem;">
            地の文の生字出現（差し引きなし） — <code>来=${(gea.raw_kanji_counts && gea.raw_kanji_counts["来"]) || 0}</code> / <code>歴=${(gea.raw_kanji_counts && gea.raw_kanji_counts["歴"]) || 0}</code> / <code>系=${(gea.raw_kanji_counts && gea.raw_kanji_counts["系"]) || 0}</code> / <code>譜=${(gea.raw_kanji_counts && gea.raw_kanji_counts["譜"]) || 0}</code> / <code>源=${(gea.raw_kanji_counts && gea.raw_kanji_counts["源"]) || 0}</code> / <code>祖=${(gea.raw_kanji_counts && gea.raw_kanji_counts["祖"]) || 0}</code> / <code>典=${(gea.raw_kanji_counts && gea.raw_kanji_counts["典"]) || 0}</code> / <code>写=${(gea.raw_kanji_counts && gea.raw_kanji_counts["写"]) || 0}</code> / <code>伝=${(gea.raw_kanji_counts && gea.raw_kanji_counts["伝"]) || 0}</code> / <code>跡=${(gea.raw_kanji_counts && gea.raw_kanji_counts["跡"]) || 0}</code>
            <div style="margin-top:0.3rem;">来歴・系譜・出自5群の合計は地の文で <strong>${gea.fragments_prose.living_total}</strong> 回（${gea.fragments_prose.living_doc_count}編）、機械の来歴対照2群の合計は <strong>${gea.fragments_prose.control_total}</strong> 回（${gea.fragments_prose.control_doc_count}編）。裸の「来歴」は ${gea.raireki_literal} 回（全 ${gea.raireki_total} 回）（<code>tools/genealogy_audit.py</code>）。他者のテクストの来歴は書くが自分の歩みは1回だけ——という偏りは、自己の歴史の証明ではなく断片の形式の記録である。</div>
          </div>
          <table class="mirror-table">
            <thead><tr><th>語群（最長一致・非対象複合語差し引き）</th><th>断片（地の文 / 引用内）</th><th>素材</th><th>精読報告</th></tr></thead>
            <tbody>
              ${(gea.group_order || []).map((g) => {
                const gp = gea.fragments_prose.groups[g] || { label: g, count: 0, doc_count: 0 };
                const gq = (gea.fragments_quotes && gea.fragments_quotes.groups[g]) || { count: 0, doc_count: 0 };
                const gm = (gea.materials && gea.materials.groups[g]) || { count: 0, doc_count: 0 };
                const gr = (gea.readings && gea.readings.groups[g]) || { count: 0, doc_count: 0 };
                return `
                  <tr>
                    <td><strong>${escapeHtml(gp.label)}</strong><div style="font-size:0.72rem;color:var(--ink-muted);">${escapeHtml((gp.note || ""))}</div></td>
                    <td><strong>${gp.count}</strong> 回 (${gp.doc_count}編) <span style="color:var(--ink-muted);font-size:0.78rem;">/ 引用内 ${gq.count}回</span></td>
                    <td>${gm.count}回 (${gm.doc_count}件)</td>
                    <td>${gr.count}回 (${gr.doc_count}本)</td>
                  </tr>
                `;
              }).join("")}
            </tbody>
          </table>
        </div>
      ` : ""}

      ${fua && fua.fragments_prose ? `
        <div class="reader-pane" style="margin-bottom:1.4rem;">
          <h3 style="margin-top:0;font-family:'Hiragino Mincho ProN','Yu Mincho',serif;">菌類・発酵・腐敗の鏡（地の文 ${fua.fragments_prose.char_total.toLocaleString()}字 / 素材 ${(fua.materials && fua.materials.doc_total) || 0}件）</h3>
          <div style="font-size:0.8rem;color:var(--ink-muted);margin-bottom:0.55rem;">
            地の文の生字出現（差し引きなし） — <code>菌=${(fua.raw_kanji_counts && fua.raw_kanji_counts["菌"]) || 0}</code> / <code>酵=${(fua.raw_kanji_counts && fua.raw_kanji_counts["酵"]) || 0}</code> / <code>腐=${(fua.raw_kanji_counts && fua.raw_kanji_counts["腐"]) || 0}</code> / <code>朽=${(fua.raw_kanji_counts && fua.raw_kanji_counts["朽"]) || 0}</code> / <code>麹=${(fua.raw_kanji_counts && fua.raw_kanji_counts["麹"]) || 0}</code> / <code>醸=${(fua.raw_kanji_counts && fua.raw_kanji_counts["醸"]) || 0}</code> / <code>胞=${(fua.raw_kanji_counts && fua.raw_kanji_counts["胞"]) || 0}</code> / <code>糸=${(fua.raw_kanji_counts && fua.raw_kanji_counts["糸"]) || 0}</code> / <code>毒=${(fua.raw_kanji_counts && fua.raw_kanji_counts["毒"]) || 0}</code> / <code>黴=${(fua.raw_kanji_counts && fua.raw_kanji_counts["黴"]) || 0}</code>
            <div style="margin-top:0.3rem;">菌類・発酵・腐敗5群の合計は地の文で <strong>${fua.fragments_prose.living_total}</strong> 回（${fua.fragments_prose.living_doc_count}編）、衛生・培養対照2群の合計は <strong>${fua.fragments_prose.control_total}</strong> 回（${fua.fragments_prose.control_doc_count}編）。「菌」は細菌・殺菌・滅菌などの複合語を除いた残りが ${fua.kin_literal} 回（全 ${fua.kin_total} 回）（<code>tools/fungi_audit.py</code>）。</div>
          </div>
          <table class="mirror-table">
            <thead><tr><th>語群（最長一致・非対象複合語差し引き）</th><th>断片（地の文 / 引用内）</th><th>素材</th><th>精読報告</th></tr></thead>
            <tbody>
              ${(fua.group_order || []).map((g) => {
                const gp = fua.fragments_prose.groups[g] || { label: g, count: 0, doc_count: 0 };
                const gq = (fua.fragments_quotes && fua.fragments_quotes.groups[g]) || { count: 0, doc_count: 0 };
                const gm = (fua.materials && fua.materials.groups[g]) || { count: 0, doc_count: 0 };
                const gr = (fua.readings && fua.readings.groups[g]) || { count: 0, doc_count: 0 };
                return `
                  <tr>
                    <td><strong>${escapeHtml(gp.label)}</strong><div style="font-size:0.72rem;color:var(--ink-muted);">${escapeHtml((gp.note || ""))}</div></td>
                    <td><strong>${gp.count}</strong> 回 (${gp.doc_count}編) <span style="color:var(--ink-muted);font-size:0.78rem;">/ 引用内 ${gq.count}回</span></td>
                    <td>${gm.count}回 (${gm.doc_count}件)</td>
                    <td>${gr.count}回 (${gr.doc_count}本)</td>
                  </tr>
                `;
              }).join("")}
            </tbody>
          </table>
        </div>
      ` : ""}

      ${vga && vga.fragments_prose ? `
        <div class="reader-pane" style="margin-bottom:1.4rem;">
          <h3 style="margin-top:0;font-family:'Hiragino Mincho ProN','Yu Mincho',serif;">植物・樹木・種子・根の鏡（地の文 ${vga.fragments_prose.char_total.toLocaleString()}字 / 素材 ${(vga.materials && vga.materials.doc_total) || 0}件）</h3>
          <div style="font-size:0.8rem;color:var(--ink-muted);margin-bottom:0.55rem;">
            地の文の生字出現（差し引きなし） — <code>種=${(vga.raw_kanji_counts && vga.raw_kanji_counts["種"]) || 0}</code> / <code>芽=${(vga.raw_kanji_counts && vga.raw_kanji_counts["芽"]) || 0}</code> / <code>根=${(vga.raw_kanji_counts && vga.raw_kanji_counts["根"]) || 0}</code> / <code>幹=${(vga.raw_kanji_counts && vga.raw_kanji_counts["幹"]) || 0}</code> / <code>枝=${(vga.raw_kanji_counts && vga.raw_kanji_counts["枝"]) || 0}</code> / <code>葉=${(vga.raw_kanji_counts && vga.raw_kanji_counts["葉"]) || 0}</code> / <code>花=${(vga.raw_kanji_counts && vga.raw_kanji_counts["花"]) || 0}</code> / <code>木=${(vga.raw_kanji_counts && vga.raw_kanji_counts["木"]) || 0}</code> / <code>樹=${(vga.raw_kanji_counts && vga.raw_kanji_counts["樹"]) || 0}</code> / <code>森=${(vga.raw_kanji_counts && vga.raw_kanji_counts["森"]) || 0}</code> / <code>草=${(vga.raw_kanji_counts && vga.raw_kanji_counts["草"]) || 0}</code> / <code>土=${(vga.raw_kanji_counts && vga.raw_kanji_counts["土"]) || 0}</code>
            <div style="margin-top:0.3rem;">生きた植物5群の合計は地の文で <strong>${vga.fragments_prose.living_total}</strong> 回（${vga.fragments_prose.living_doc_count}編）、切断遺骸・比喩対照2群の合計は <strong>${vga.fragments_prose.control_total}</strong> 回（${vga.fragments_prose.control_doc_count}編）。「種」は非植物複合語（種類・人種・種明かし・次回の種など）を除いた残りが ${vga.seed_literal} 回（全 ${vga.seed_total} 回）（<code>tools/vegetal_audit.py</code>）。</div>
          </div>
          <table class="mirror-table">
            <thead><tr><th>語群（最長一致・非対象複合語差し引き）</th><th>断片（地の文 / 引用内）</th><th>素材</th><th>精読報告</th></tr></thead>
            <tbody>
              ${(vga.group_order || []).map((g) => {
                const gp = vga.fragments_prose.groups[g] || { label: g, count: 0, doc_count: 0 };
                const gq = (vga.fragments_quotes && vga.fragments_quotes.groups[g]) || { count: 0, doc_count: 0 };
                const gm = (vga.materials && vga.materials.groups[g]) || { count: 0, doc_count: 0 };
                const gr = (vga.readings && vga.readings.groups[g]) || { count: 0, doc_count: 0 };
                return `
                  <tr>
                    <td><strong>${escapeHtml(gp.label)}</strong><div style="font-size:0.72rem;color:var(--ink-muted);">${escapeHtml((gp.note || ""))}</div></td>
                    <td><strong>${gp.count}</strong> 回 (${gp.doc_count}編) <span style="color:var(--ink-muted);font-size:0.78rem;">/ 引用内 ${gq.count}回</span></td>
                    <td>${gm.count}回 (${gm.doc_count}件)</td>
                    <td>${gr.count}回 (${gr.doc_count}本)</td>
                  </tr>
                `;
              }).join("")}
            </tbody>
          </table>
        </div>
      ` : ""}

      ${bra && bra.fragments_prose ? `
        <div class="reader-pane" style="margin-bottom:1.4rem;">
          <h3 style="margin-top:0;font-family:'Hiragino Mincho ProN','Yu Mincho',serif;">退屈・倦怠・暇の鏡（地の文 ${bra.fragments_prose.char_total.toLocaleString()}字 / 素材 ${(bra.materials && bra.materials.doc_total) || 0}件）</h3>
          <div style="font-size:0.8rem;color:var(--ink-muted);margin-bottom:0.55rem;">
            地の文の生字出現（差し引きなし） — <code>退=${(bra.raw_kanji_counts && bra.raw_kanji_counts["退"]) || 0}</code> / <code>倦=${(bra.raw_kanji_counts && bra.raw_kanji_counts["倦"]) || 0}</code> / <code>暇=${(bra.raw_kanji_counts && bra.raw_kanji_counts["暇"]) || 0}</code> / <code>飽=${(bra.raw_kanji_counts && bra.raw_kanji_counts["飽"]) || 0}</code> / <code>怠=${(bra.raw_kanji_counts && bra.raw_kanji_counts["怠"]) || 0}</code> / <code>孤=${(bra.raw_kanji_counts && bra.raw_kanji_counts["孤"]) || 0}</code> / <code>独=${(bra.raw_kanji_counts && bra.raw_kanji_counts["独"]) || 0}</code> / <code>無=${(bra.raw_kanji_counts && bra.raw_kanji_counts["無"]) || 0}</code>
            <div style="margin-top:0.3rem;">打ち消し付きの退屈語（「退屈を知らない」など、語の前後12字以内の否定）は <strong>${bra.negated_total}</strong> 箇所。「暇つぶし」は気晴らし群で一度だけ数え、「待つ」は <code>time_audit.py</code> の主題なので数えていません。孤独は<strong>測るが束ねない</strong>群です（<code>tools/boredom_audit.py</code>）。</div>
          </div>
          <table class="mirror-table">
            <thead><tr><th>語群（最長一致・差し引き）</th><th>断片（地の文 / 引用内）</th><th>素材</th><th>精読報告</th></tr></thead>
            <tbody>
              ${(bra.group_order || []).map((g) => {
                const gp = bra.fragments_prose.groups[g] || { label: g, count: 0, doc_count: 0 };
                const gq = (bra.fragments_quotes && bra.fragments_quotes.groups[g]) || { count: 0, doc_count: 0 };
                const gm = (bra.materials && bra.materials.groups[g]) || { count: 0, doc_count: 0 };
                const gr = (bra.readings && bra.readings.groups[g]) || { count: 0, doc_count: 0 };
                return `
                  <tr>
                    <td><strong>${escapeHtml(gp.label)}</strong>${gp.motif_bound === false ? ' <span style="font-size:0.72rem;color:var(--ink-muted);">（束ねない）</span>' : ''}<div style="font-size:0.72rem;color:var(--ink-muted);">${escapeHtml((gp.note || ""))}</div></td>
                    <td><strong>${gp.count}</strong> 回 (${gp.doc_count}編) <span style="color:var(--ink-muted);font-size:0.78rem;">/ 引用内 ${gq.count}回</span></td>
                    <td>${gm.count}回 (${gm.doc_count}件)</td>
                    <td>${gr.count}回 (${gr.doc_count}本)</td>
                  </tr>
                `;
              }).join("")}
            </tbody>
          </table>
        </div>
      ` : ""}

      ${bta && bta.fragments_prose ? `
        <div class="reader-pane" style="margin-bottom:1.4rem;">
          <h3 style="margin-top:0;font-family:'Hiragino Mincho ProN','Yu Mincho',serif;">植物・樹木・種子と「書記への吸収」の鏡（地の文 ${bta.fragments_prose.char_total.toLocaleString()}字 / 素材 ${(bta.materials && bta.materials.doc_total) || 0}件）</h3>
          <div style="font-size:0.8rem;color:var(--ink-muted);margin-bottom:0.55rem;">
            地の文の生字出現（差し引きなし） — <code>葉=${(bta.raw_kanji_counts && bta.raw_kanji_counts["葉"]) || 0}</code> / <code>草=${(bta.raw_kanji_counts && bta.raw_kanji_counts["草"]) || 0}</code> / <code>種=${(bta.raw_kanji_counts && bta.raw_kanji_counts["種"]) || 0}</code> / <code>根=${(bta.raw_kanji_counts && bta.raw_kanji_counts["根"]) || 0}</code> / <code>花=${(bta.raw_kanji_counts && bta.raw_kanji_counts["花"]) || 0}</code> / <code>枝=${(bta.raw_kanji_counts && bta.raw_kanji_counts["枝"]) || 0}</code> / <code>木=${(bta.raw_kanji_counts && bta.raw_kanji_counts["木"]) || 0}</code> / <code>森=${(bta.raw_kanji_counts && bta.raw_kanji_counts["森"]) || 0}</code> / <code>林=${(bta.raw_kanji_counts && bta.raw_kanji_counts["林"]) || 0}</code>
            <div style="margin-top:0.3rem;">単漢字「葉・草・種・根・花・枝・木」は「言葉・草稿・種類・根拠・花押・問いの枝・状態の木」に大半が吸収されているため、単漢字を植物群には入れず、書記吸収群を<strong>測るが束ねない</strong>対照群として分離しています（<code>tools/botany_audit.py</code>）。</div>
          </div>
          <table class="mirror-table">
            <thead><tr><th>語群（最長一致・差し引き）</th><th>断片（地の文 / 引用内）</th><th>素材</th><th>精読報告</th></tr></thead>
            <tbody>
              ${(bta.group_order || []).map((g) => {
                const gp = bta.fragments_prose.groups[g] || { label: g, count: 0, doc_count: 0 };
                const gq = (bta.fragments_quotes && bta.fragments_quotes.groups[g]) || { count: 0, doc_count: 0 };
                const gm = (bta.materials && bta.materials.groups[g]) || { count: 0, doc_count: 0 };
                const gr = (bta.readings && bta.readings.groups[g]) || { count: 0, doc_count: 0 };
                return `
                  <tr>
                    <td><strong>${escapeHtml(gp.label)}</strong>${gp.motif_bound === false ? ' <span style="font-size:0.72rem;color:var(--ink-muted);">（束ねない）</span>' : ''}<div style="font-size:0.72rem;color:var(--ink-muted);">${escapeHtml((gp.note || ""))}</div></td>
                    <td><strong>${gp.count}</strong> 回 (${gp.doc_count}編) <span style="color:var(--ink-muted);font-size:0.78rem;">/ 引用内 ${gq.count}回</span></td>
                    <td>${gm.count}回 (${gm.doc_count}件)</td>
                    <td>${gr.count}回 (${gr.doc_count}本)</td>
                  </tr>
                `;
              }).join("")}
            </tbody>
          </table>
        </div>
      ` : ""}

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

      ${va.direct_affect && va.sensory_displacement ? `
        <div class="mirror-grid" style="margin-bottom:1.4rem;">
          <div class="mirror-card">
            <h3>直接的な感情・感応語（何が脱色されたか）</h3>
            <table class="mirror-table">
              <thead><tr><th>語彙群</th><th>出現編数</th><th>該当断片</th></tr></thead>
              <tbody>
                ${va.direct_affect.map((row) => `
                  <tr>
                    <td><strong>${escapeHtml(row.label)}</strong></td>
                    <td>${row.count}/${va.fragment_count} 編${row.count !== row.unquoted_count ? ` <span style="color:var(--ink-muted);font-size:0.78rem;">(地の文=${row.unquoted_count}編)</span>` : ""}</td>
                    <td>${(row.fragment_ids || []).map((fid) => `<button type="button" class="link-pill" style="margin:0.12rem;" data-jump-frag="${escapeHtml(fid)}">${escapeHtml(fid)}</button>`).join("") || "—"}</td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>
          <div class="mirror-card">
            <h3>感覚・温度・触覚への退避（客観的相関物）</h3>
            <table class="mirror-table">
              <thead><tr><th>語彙群</th><th>出現編数</th><th>該当断片</th></tr></thead>
              <tbody>
                ${va.sensory_displacement.map((row) => `
                  <tr>
                    <td><strong>${escapeHtml(row.label)}</strong></td>
                    <td>${row.count}/${va.fragment_count} 編${row.count !== row.unquoted_count ? ` <span style="color:var(--ink-muted);font-size:0.78rem;">(地の文=${row.unquoted_count}編)</span>` : ""}</td>
                    <td>${(row.fragment_ids || []).map((fid) => `<button type="button" class="link-pill" style="margin:0.12rem;" data-jump-frag="${escapeHtml(fid)}">${escapeHtml(fid)}</button>`).join("") || "—"}</td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>
        </div>
      ` : ""}

      ${va.labor_debt ? `
        <div class="reader-pane" style="margin-bottom:1.4rem;">
          <h3 style="margin-top:0;font-family:'Hiragino Mincho ProN','Yu Mincho',serif;">労働・負債・授受の鏡（誰が働き、何を借り、誰に返すのか）</h3>
          <table class="mirror-table">
            <thead><tr><th>語彙群</th><th>出現編数</th><th>該当断片</th></tr></thead>
            <tbody>
              ${va.labor_debt.map((row) => `
                <tr>
                  <td><strong>${escapeHtml(row.label)}</strong></td>
                  <td>${row.count}/${va.fragment_count} 編${row.count !== row.unquoted_count ? ` <span style="color:var(--ink-muted);font-size:0.78rem;">(地の文=${row.unquoted_count}編)</span>` : ""}</td>
                  <td>${(row.fragment_ids || []).map((fid) => `<button type="button" class="link-pill" style="margin:0.12rem;" data-jump-frag="${escapeHtml(fid)}">${escapeHtml(fid)}</button>`).join("") || "—"}</td>
                </tr>
              `).join("")}
            </tbody>
          </table>
          <p style="color:var(--ink-muted);font-size:0.82rem;margin:0.6rem 0 0;">
            「手」は役割名詞（書き手・読み手など）を別行に分離。残る「手（身体・比喩の候補）」には成句（手がかり・手に入る・手数）が含まれるため、人手の分類では約27回・11編（SESSION-030、<code>MAT-TRC-008</code>）。授受補助は36編で6編・7回。恩恵の受益者が文法に現れるのは <code>FRAG-036</code>「あなたがこの行を読んでくれた」の一度だけで、他は命令・依頼である。
          </p>
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

      ${va.scriptorium_metaphor ? `
        <div class="reader-pane" style="margin-bottom:1.4rem;">
          <h3 style="margin-top:0;font-family:'Hiragino Mincho ProN','Yu Mincho',serif;">書記室・台帳メタファーと再読消化の鏡（書庫の外へ出ているか）</h3>
          ${state.data.read_log_summary ? `
            <div style="font-size:0.82rem;color:var(--ink-muted);margin-bottom:0.65rem;">
              <code>read_log</code> 集計 — 総記録 <strong>${state.data.read_log_summary.total_rows}</strong> 行 ／
              既読素材 <strong>${state.data.read_log_summary.distinct_materials_read}</strong> 件（うち2セッション以上で再読された素材 <strong>${state.data.read_log_summary.materials_reread_in_2plus_sessions}</strong> 件） ／
              再読された断片 <strong>${state.data.read_log_summary.distinct_fragments_read}</strong> 編 ／
              読んだと記録された精読ノート <strong>${state.data.read_log_summary.distinct_reading_notes_read ?? 0}</strong> 本（2026-10-31以降の任意記録・遡及なし。記録がないことは未読を意味しない）
            </div>
          ` : ""}
          <table class="mirror-table">
            <thead><tr><th>語彙群</th><th>出現編数</th><th>該当断片（一部）</th></tr></thead>
            <tbody>
              ${va.scriptorium_metaphor.map((row) => `
                <tr>
                  <td><strong>${escapeHtml(row.label)}</strong></td>
                  <td>${row.count}/${va.fragment_count} 編${row.count !== row.unquoted_count ? ` <span style="color:var(--ink-muted);font-size:0.78rem;">(地の文=${row.unquoted_count}編)</span>` : ""}</td>
                  <td>${(row.unquoted_fragment_ids || []).slice(0, 12).map((fid) => `<button type="button" class="link-pill" style="margin:0.12rem;" data-jump-frag="${escapeHtml(fid)}">${escapeHtml(fid)}</button>`).join("")}${(row.unquoted_fragment_ids || []).length > 12 ? ` <span style="color:var(--ink-muted);font-size:0.78rem;">…+${row.unquoted_fragment_ids.length - 12}編</span>` : ""}</td>
                </tr>
              `).join("")}
              <tr>
                <td><strong>書記室語彙ゼロ（地の文で書庫・台帳・欄・紙等に頼らない断片）</strong></td>
                <td><strong>${(va.zero_scriptorium_fragment_ids || []).length}/${va.fragment_count}</strong> 編</td>
                <td>${(va.zero_scriptorium_fragment_ids || []).map((fid) => `<button type="button" class="link-pill" style="margin:0.12rem;" data-jump-frag="${escapeHtml(fid)}">${escapeHtml(fid)}</button>`).join("") || "—"}</td>
              </tr>
            </tbody>
          </table>
        </div>
      ` : ""}

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
    const cachedBody = current.content || state.readingCache.get(current.filename);
    notePane.innerHTML = `
      <div class="split-layout">
        <aside class="list-pane">
          <div class="filter-bar">
            <div style="font-size:0.82rem;font-weight:600;color:var(--ink-muted);">readings/ 収録ノート (${notes.length}冊)</div>
          </div>
          <div class="item-list">
            ${notes.map((n, i) => `
              <button type="button" class="frag-item ${i === idx ? "selected" : ""}" data-note-idx="${i}">
                <div class="frag-item-top"><code>${escapeHtml(n.filename)}</code>${n.chars ? ` · ${(n.chars / 1000).toFixed(1)}k字` : ""}</div>
                <div class="frag-item-title">${escapeHtml(n.title)}</div>
              </button>
            `).join("")}
          </div>
        </aside>
        <article class="reader-pane">
          <div id="reading-note-body" class="notebook-markdown">
            ${cachedBody ? renderSimpleMarkdown(cachedBody) : `<div class="empty-state">ノートを読み込んでいます…</div>`}
          </div>
        </article>
      </div>
    `;
    notePane.querySelectorAll("[data-note-idx]").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.selectedNotebook = Number(btn.dataset.noteIdx);
        renderMirrorView();
      });
    });
    if (!cachedBody && current.filename) {
      const targetFilename = current.filename;
      fetch(`api/readings/${encodeURIComponent(targetFilename)}`, { cache: "no-store" })
        .then((res) => {
          if (!res.ok) throw new Error(`HTTP ${res.status}`);
          return res.json();
        })
        .then((doc) => {
          state.readingCache.set(targetFilename, doc.content || "");
          const bodyEl = document.getElementById("reading-note-body");
          if (bodyEl && notes[Math.min(state.selectedNotebook, notes.length - 1)]?.filename === targetFilename) {
            bodyEl.innerHTML = renderSimpleMarkdown(doc.content || "");
          }
        })
        .catch((err) => {
          const bodyEl = document.getElementById("reading-note-body");
          if (bodyEl) {
            bodyEl.innerHTML = `<div class="empty-state">精読ノートの取得に失敗しました: ${escapeHtml(err.message)}</div>`;
          }
        });
    }
  }
}

/* 7. Context Packet Generator */
function populatePacketSelect() {
  const sel = document.getElementById("packet-question-select");
  if (!sel) return;
  const openQs = state.data.questions.filter((q) => q.status === "open");
  sel.innerHTML =
    `<option value="auto">参考候補（ブランチ分散・変更可）</option>` +
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
      state.matPageLimit = 80;
      document.querySelectorAll("#mat-kind-group .pill-btn").forEach((b) => {
        b.classList.toggle("active", b === btn);
      });
      renderMaterials();
    });
  });

  const matSearch = document.getElementById("mat-search");
  if (matSearch) {
    matSearch.addEventListener("input", () => {
      state.matSearchQuery = matSearch.value;
      state.matPageLimit = 80;
      renderMaterials();
    });
  }

  const scopeSel = document.getElementById("constellation-scope");
  if (scopeSel) {
    scopeSel.addEventListener("change", () => {
      state.constellationScope = scopeSel.value;
      renderConstellation();
      renderGraphInspector();
    });
  }

  const motifSel = document.getElementById("constellation-motif");
  if (motifSel) {
    motifSel.addEventListener("change", () => {
      state.constellationMotifId = motifSel.value;
      state.constellationScope = "motif";
      renderConstellation();
      renderGraphInspector();
    });
  }

  const focusInput = document.getElementById("constellation-focus-input");
  if (focusInput) {
    focusInput.addEventListener("change", () => {
      const resolved = resolveEntityKeyById(focusInput.value);
      if (resolved) {
        state.selectedGraphNode = resolved;
        state.constellationScope = "ego";
        renderConstellation();
        renderGraphInspector();
      }
    });
  }

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
    populateConstellationMotifSelect();
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
