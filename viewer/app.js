(function () {
  "use strict";

  const FORM_LABELS = {
    dialogue: "対話",
    scene: "情景",
    letter: "書簡",
    poem: "詩的断章",
    essay: "エッセイ",
    fragment: "断章",
    other: "その他",
  };

  const NARRATOR_INFO = {
    fictional_first_person: {
      label: "創作上の一人称 (fictional_first_person)",
      note: "記録から再構成された創作上の語り手です。モデルの主観的意識や実体験の事実報告ではありません。",
    },
    reflective_literary_voice: {
      label: "内省的・文芸的な声 (reflective_literary_voice)",
      note: "保存された台帳・文献を読み返して思考を編む文芸上の声であり、生身の経験の報告ではありません。",
    },
    dialogue: {
      label: "対話体 (dialogue)",
      note: "複数の視点をぶつけ合う対話形式であり、単一の結論へ畳まないための構成です。",
    },
    third_person: {
      label: "三人称 (third_person)",
      note: "記録と読み手のあいだの情景・構造を外側から描く三人称の語りです。",
    },
    human_narrator: {
      label: "人間の語り手 (human_narrator)",
      note: "人間の書き手による直接の記述です。",
    },
    other: {
      label: "その他 (other)",
      note: "実験的な語りのモードです。",
    },
  };

  const RELATION_STYLES = {
    echo: { label: "共鳴 (echo)", color: "#295270", dash: "" },
    contrast: { label: "対照 (contrast)", color: "#9b3728", dash: "6,3" },
    transforms: { label: "変奏 (transforms)", color: "#3b6048", dash: "" },
    interrupts: { label: "切断 (interrupts)", color: "#c23b22", dash: "3,3" },
    reframes: { label: "枠組転換 (reframes)", color: "#8a6120", dash: "" },
    metaphorically_resonates: { label: "比喩共鳴 (metaphor)", color: "#6b4c8c", dash: "5,3" },
    responds_to: { label: "応答 (responds_to)", color: "#6e7781", dash: "" },
    leaves_open: { label: "開放 (leaves_open)", color: "#9a7b2c", dash: "2,4" },
  };

  let STATE = null;
  let activeFragmentId = null;
  let activeGraphNode = null;
  let activeRelationFilter = "all";
  let activeMaterialKind = "all";

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  async function fetchArchiveJson(url) {
    const maxAttempts = 3;
    for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
      let res;
      try {
        res = await fetch(url, { cache: "no-store" });
      } catch (_err) {
        return null; // network failure: fall through to the next URL
      }
      if (res.ok) {
        try {
          return await res.json();
        } catch (_err) {
          return null;
        }
      }
      // 503 means a ledger is being rewritten right now; retry briefly.
      if (res.status !== 503 || attempt === maxAttempts - 1) {
        return null;
      }
      await new Promise((resolve) => setTimeout(resolve, 250 * (attempt + 1)));
    }
    return null;
  }

  async function loadData() {
    for (const url of ["./api/state", "./data.json"]) {
      const data = await fetchArchiveJson(url);
      if (data) {
        return data;
      }
    }
    throw new Error("台帳データを読み込めませんでした。`python3 tools/serve_viewer.py` を起動してください。");
  }

  function switchTab(viewName) {
    document.querySelectorAll(".tab-btn").forEach((btn) => {
      const isMatch = btn.dataset.view === viewName;
      btn.classList.toggle("active", isMatch);
      btn.setAttribute("aria-selected", String(isMatch));
    });
    document.querySelectorAll(".view-panel").forEach((panel) => {
      const isMatch = panel.id === `view-${viewName}`;
      panel.classList.toggle("active", isMatch);
      panel.hidden = !isMatch;
    });
    if (viewName === "constellation") {
      renderConstellation();
    }
  }

  function renderStats() {
    const strip = document.getElementById("stats-strip");
    const qCount = STATE.questions.length;
    const motifCount = STATE.motifs.length;
    const matLit = STATE.materials.filter((m) => m.kind === "literary_text").length;
    const matAi = STATE.materials.filter((m) => m.kind === "research_excerpt").length;
    const fragSelected = STATE.fragments.filter((f) => f.status === "selected").length;
    const fragTotal = STATE.fragments.length;

    strip.innerHTML = [
      `<span class="stat-chip"><strong>${qCount}</strong>開かれた問い</span>`,
      `<span class="stat-chip"><strong>${motifCount}</strong>横断モチーフ</span>`,
      `<span class="stat-chip"><strong>${STATE.materials.length}</strong>対話素材（AI研究 ${matAi} / 哲学・文学 ${matLit}）</span>`,
      `<span class="stat-chip"><strong>${fragTotal}</strong>文芸断片（Selected ${fragSelected} / Draft ${fragTotal - fragSelected}）</span>`,
      `<span class="stat-chip"><strong>${STATE.relations.length}</strong>解釈的関係</span>`,
      `<span class="stat-chip"><strong>${STATE.sessions.length}</strong>セッション</span>`,
    ].join("");
  }

  function populateMotifFilter() {
    const select = document.getElementById("frag-motif-filter");
    STATE.motifs.forEach((m) => {
      const opt = document.createElement("option");
      opt.value = m.motif_id;
      opt.textContent = `${m.motif_id}: ${m.label}`;
      select.appendChild(opt);
    });
  }

  function formatFragmentBody(frag) {
    if (frag.form === "dialogue") {
      return frag.text
        .split("\n")
        .filter((line) => line.trim())
        .map((line) => {
          const idx = line.indexOf(":");
          if (idx > 0 && idx < 18) {
            const speaker = line.slice(0, idx).trim();
            const speech = line.slice(idx + 1).trim();
            return `<div class="dialogue-turn"><span class="dialogue-speaker">${escapeHtml(speaker)}</span><div>${escapeHtml(speech)}</div></div>`;
          }
          return `<p>${escapeHtml(line)}</p>`;
        })
        .join("");
    }
    return frag.text
      .split("\n\n")
      .map((para) => `<p>${escapeHtml(para).replace(/\n/g, "<br />")}</p>`)
      .join("");
  }

  function renderFragmentList() {
    const query = document.getElementById("frag-search").value.trim().toLowerCase();
    const formVal = document.getElementById("frag-form-filter").value;
    const motifVal = document.getElementById("frag-motif-filter").value;
    const statusVal = document.getElementById("frag-status-filter").value;

    const filtered = STATE.fragments
      .slice()
      .reverse()
      .filter((f) => {
        if (formVal !== "all" && f.form !== formVal) return false;
        if (motifVal !== "all" && !f.motif_ids.includes(motifVal)) return false;
        if (statusVal !== "all" && f.status !== statusVal) return false;
        if (query) {
          const hay = `${f.fragment_id} ${f.title} ${f.text} ${f.question_ids.join(" ")} ${f.material_ids.join(" ")}`.toLowerCase();
          if (!hay.includes(query)) return false;
        }
        return true;
      });

    const listEl = document.getElementById("frag-list");
    if (!filtered.length) {
      listEl.innerHTML = `<div style="padding:1.25rem;color:var(--ink-muted);font-size:0.86rem;">条件に一致する断片がありません。</div>`;
      return;
    }

    if (!filtered.some((f) => f.fragment_id === activeFragmentId)) {
      activeFragmentId = filtered[0].fragment_id;
    }

    listEl.innerHTML = filtered
      .map((f) => {
        const isSel = f.fragment_id === activeFragmentId;
        const statusClass = f.status === "selected" ? "badge-selected" : "badge-draft";
        return `
          <button type="button" class="frag-item ${isSel ? "selected" : ""}" data-frag-id="${escapeHtml(f.fragment_id)}">
            <div class="frag-item-top">
              <span><strong>${escapeHtml(f.fragment_id)}</strong> · ${escapeHtml(FORM_LABELS[f.form] || f.form)}</span>
              <span class="badge ${statusClass}">${escapeHtml(f.status)}</span>
            </div>
            <div class="frag-item-title">${escapeHtml(f.title)}</div>
            <div class="frag-item-preview">${escapeHtml(f.text.replace(/\n+/g, " "))}</div>
          </button>
        `;
      })
      .join("");

    listEl.querySelectorAll(".frag-item").forEach((btn) => {
      btn.addEventListener("click", () => {
        activeFragmentId = btn.dataset.fragId;
        renderFragmentList();
        renderFragmentReader();
      });
    });

    renderFragmentReader();
  }

  function renderFragmentReader() {
    const reader = document.getElementById("frag-reader");
    const frag = STATE.byId[activeFragmentId];
    if (!frag) return;

    const narrator = NARRATOR_INFO[frag.narrator_mode] || NARRATOR_INFO.other;
    const statusClass = frag.status === "selected" ? "badge-selected" : "badge-draft";
    const linkedRels = STATE.relations.filter(
      (r) => r.left.id === frag.fragment_id || r.right.id === frag.fragment_id
    );

    reader.innerHTML = `
      <div class="reader-meta-top">
        <code>${escapeHtml(frag.fragment_id)}</code>
        <span class="badge ${statusClass}">${escapeHtml(frag.status)}</span>
        <span class="badge badge-ai">${escapeHtml(FORM_LABELS[frag.form] || frag.form)}</span>
        <span class="badge badge-mode">${escapeHtml(narrator.label)}</span>
        <span style="font-size:0.8rem;color:var(--ink-muted);">${escapeHtml(frag.session_id || "")} (${escapeHtml(frag.created_at)})</span>
      </div>
      <h2 class="reader-title">${escapeHtml(frag.title)}</h2>
      <div class="narrator-banner">
        <strong>語りの位置づけ：</strong>${escapeHtml(narrator.note)}
      </div>
      <div class="literary-body form-${escapeHtml(frag.form)}">
        ${formatFragmentBody(frag)}
      </div>

      ${
        frag.editor_note
          ? `<div class="meta-box">
               <h3>編集・制作ノート</h3>
               <p style="margin:0;color:var(--ink-muted);">${escapeHtml(frag.editor_note)}</p>
             </div>`
          : ""
      }

      <div class="meta-box">
        <h3>たどっている問い・モチーフ・対話素材</h3>
        <div class="tag-row">
          ${frag.question_ids
            .map((qid) => {
              const q = STATE.byId[qid];
              return `<button type="button" class="link-pill" data-jump-question="${escapeHtml(qid)}" title="${escapeHtml(q ? q.question : qid)}">${escapeHtml(qid)}: ${escapeHtml((q ? q.question : "").slice(0, 26))}…</button>`;
            })
            .join("")}
        </div>
        <div class="tag-row">
          ${frag.motif_ids
            .map((mid) => {
              const m = STATE.byId[mid];
              return `<span class="badge badge-selected">${escapeHtml(mid)} · ${escapeHtml(m ? m.label : "")}</span>`;
            })
            .join("")}
          ${frag.material_ids
            .map((matId) => {
              const mat = STATE.byId[matId];
              const cls = mat && mat.kind === "literary_text" ? "badge-lit" : "badge-ai";
              return `<button type="button" class="link-pill ${cls}" data-jump-material="${escapeHtml(matId)}">${escapeHtml(matId)}: ${escapeHtml(mat ? mat.title.slice(0, 28) : "")}</button>`;
            })
            .join("")}
        </div>
      </div>

      <div class="meta-box">
        <h3>解釈的関係（共鳴・対照・切断・応答）</h3>
        <ul class="rel-list">
          ${linkedRels
            .map((r) => {
              const otherId = r.left.id === frag.fragment_id ? r.right.id : r.left.id;
              const style = RELATION_STYLES[r.relation_type] || { label: r.relation_type };
              return `
                <li>
                  <div style="display:flex;justify-content:space-between;align-items:center;gap:0.5rem;margin-bottom:0.25rem;">
                    <span><code>${escapeHtml(r.left.id)}</code> → <strong>${escapeHtml(style.label)}</strong> → <code>${escapeHtml(r.right.id)}</code></span>
                    <button type="button" class="link-pill" data-jump-any="${escapeHtml(otherId)}">${escapeHtml(otherId)} を開く</button>
                  </div>
                  <div style="color:var(--ink-muted);">${escapeHtml(r.note || "")}</div>
                </li>
              `;
            })
            .join("")}
        </ul>
      </div>
    `;

    bindJumpButtons(reader);
  }

  function bindJumpButtons(container) {
    container.querySelectorAll("[data-jump-question]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const qid = btn.dataset.jumpQuestion;
        switchTab("questions");
        const target = document.getElementById(`qcard-${qid}`);
        if (target) {
          target.scrollIntoView({ behavior: "smooth", block: "center" });
          target.style.outline = "2px solid var(--accent-crimson)";
          setTimeout(() => (target.style.outline = ""), 1800);
        }
      });
    });

    container.querySelectorAll("[data-jump-material]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const mid = btn.dataset.jumpMaterial;
        activeMaterialKind = "all";
        updateMaterialPills();
        renderMaterials();
        switchTab("materials");
        const target = document.getElementById(`mcard-${mid}`);
        if (target) {
          target.scrollIntoView({ behavior: "smooth", block: "center" });
          target.style.outline = "2px solid var(--accent-crimson)";
          setTimeout(() => (target.style.outline = ""), 1800);
        }
      });
    });

    container.querySelectorAll("[data-jump-any]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.dataset.jumpAny;
        if (id.startsWith("FRAG-")) {
          activeFragmentId = id;
          document.getElementById("frag-search").value = "";
          document.getElementById("frag-form-filter").value = "all";
          document.getElementById("frag-motif-filter").value = "all";
          document.getElementById("frag-status-filter").value = "all";
          switchTab("fragments");
          renderFragmentList();
        } else if (id.startsWith("Q-")) {
          switchTab("questions");
          const target = document.getElementById(`qcard-${id}`);
          if (target) target.scrollIntoView({ behavior: "smooth", block: "center" });
        } else if (id.startsWith("MAT-")) {
          activeMaterialKind = "all";
          updateMaterialPills();
          renderMaterials();
          switchTab("materials");
          const target = document.getElementById(`mcard-${id}`);
          if (target) target.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      });
    });
  }

  /* View 2: Constellation SVG Graph */
  function renderRelationLegend() {
    const container = document.getElementById("relation-filters");
    const types = ["all", ...Object.keys(RELATION_STYLES)];
    container.innerHTML = types
      .map((t) => {
        const isAll = t === "all";
        const label = isAll ? "すべての関係" : RELATION_STYLES[t].label;
        const active = activeRelationFilter === t ? "active" : "";
        return `<button type="button" class="pill-btn ${active}" data-rel-type="${escapeHtml(t)}">${escapeHtml(label)}</button>`;
      })
      .join("");
    container.querySelectorAll("button").forEach((btn) => {
      btn.addEventListener("click", () => {
        activeRelationFilter = btn.dataset.relType;
        renderRelationLegend();
        renderConstellation();
      });
    });
  }

  function renderConstellation() {
    const svg = document.getElementById("constellation-svg");
    const cx = 460;
    const cy = 340;

    // Collect nodes participating in relations + all questions & fragments
    const seedQuestions = STATE.questions.filter((q) => q.origin.kind === "human_seed");
    const sessionQuestions = STATE.questions.filter((q) => q.origin.kind !== "human_seed");
    const relMaterials = STATE.materials.filter((m) =>
      STATE.relations.some((r) => r.left.id === m.material_id || r.right.id === m.material_id)
    );

    const coords = {};
    const placeRing = (items, rx, ry, startAngle) => {
      items.forEach((item, idx) => {
        const angle = startAngle + (2 * Math.PI * idx) / items.length;
        const id = item.question_id || item.fragment_id || item.material_id;
        coords[id] = {
          id,
          x: cx + rx * Math.cos(angle),
          y: cy + ry * Math.sin(angle),
          item,
        };
      });
    };

    placeRing(seedQuestions, 108, 86, -Math.PI / 2);
    placeRing(STATE.fragments, 238, 190, -Math.PI / 2 + 0.16);
    placeRing([...sessionQuestions, ...relMaterials], 385, 290, -Math.PI / 2);

    const visibleRelations = STATE.relations.filter(
      (r) => activeRelationFilter === "all" || r.relation_type === activeRelationFilter
    );

    // Also include question derivation edges lightly
    const lineageEdges = [];
    STATE.questions.forEach((q) => {
      (q.previous_question_ids || []).forEach((prevId) => {
        if (coords[q.question_id] && coords[prevId]) {
          lineageEdges.push({ from: prevId, to: q.question_id });
        }
      });
    });

    if (!activeGraphNode) {
      activeGraphNode = "FRAG-012";
    }

    const parts = [];
    // Subtle orbital guides
    parts.push(
      `<ellipse cx="${cx}" cy="${cy}" rx="108" ry="86" fill="none" stroke="var(--border)" stroke-dasharray="3,5" opacity="0.65" />`,
      `<ellipse cx="${cx}" cy="${cy}" rx="238" ry="190" fill="none" stroke="var(--border)" stroke-dasharray="3,5" opacity="0.65" />`,
      `<ellipse cx="${cx}" cy="${cy}" rx="385" ry="290" fill="none" stroke="var(--border)" stroke-dasharray="3,5" opacity="0.5" />`
    );

    if (activeRelationFilter === "all") {
      lineageEdges.forEach((le) => {
        const a = coords[le.from];
        const b = coords[le.to];
        parts.push(
          `<line class="graph-edge" data-left="${escapeHtml(le.from)}" data-right="${escapeHtml(le.to)}" x1="${a.x.toFixed(1)}" y1="${a.y.toFixed(1)}" x2="${b.x.toFixed(1)}" y2="${b.y.toFixed(1)}" stroke="var(--border-strong)" stroke-width="1" stroke-dasharray="2,4" opacity="0.55" />`
        );
      });
    }

    visibleRelations.forEach((r) => {
      const a = coords[r.left.id];
      const b = coords[r.right.id];
      if (!a || !b) return;
      const st = RELATION_STYLES[r.relation_type] || { color: "#666", dash: "" };
      const mx = (a.x + b.x) / 2 + (cy - (a.y + b.y) / 2) * 0.12;
      const my = (a.y + b.y) / 2 + ((a.x + b.x) / 2 - cx) * 0.12;
      const d = `M ${a.x.toFixed(1)} ${a.y.toFixed(1)} Q ${mx.toFixed(1)} ${my.toFixed(1)} ${b.x.toFixed(1)} ${b.y.toFixed(1)}`;
      parts.push(
        `<path class="graph-edge" data-left="${escapeHtml(r.left.id)}" data-right="${escapeHtml(r.right.id)}" d="${d}" stroke="${st.color}" stroke-width="1.8" ${st.dash ? `stroke-dasharray="${st.dash}"` : ""} opacity="0.78"><title>${escapeHtml(r.left.id)} [${escapeHtml(r.relation_type)}] ${escapeHtml(r.right.id)}: ${escapeHtml(r.note || "")}</title></path>`
      );
    });

    Object.values(coords).forEach((node) => {
      const id = node.id;
      let fill = "#295270";
      let radius = 8;
      if (id.startsWith("Q-")) {
        fill = node.item.origin.kind === "human_seed" ? "#8a6120" : "#b07d2b";
        radius = node.item.origin.kind === "human_seed" ? 9.5 : 7.5;
      } else if (id.startsWith("FRAG-")) {
        fill = node.item.status === "selected" ? "#9b3728" : "#7c6f64";
        radius = 9.5;
      } else if (id.startsWith("MAT-")) {
        fill = node.item.kind === "literary_text" ? "#6b4c8c" : "#3b6048";
        radius = 8;
      }
      const isSelected = activeGraphNode === id;
      const labelY = node.y < cy ? node.y - 13 : node.y + 18;
      parts.push(`
        <g class="graph-node" data-node-id="${escapeHtml(id)}">
          ${isSelected ? `<circle cx="${node.x.toFixed(1)}" cy="${node.y.toFixed(1)}" r="${radius + 6}" fill="none" stroke="${fill}" stroke-width="2" />` : ""}
          <circle cx="${node.x.toFixed(1)}" cy="${node.y.toFixed(1)}" r="${radius}" fill="${fill}" stroke="var(--surface)" stroke-width="2" />
          <text x="${node.x.toFixed(1)}" y="${labelY.toFixed(1)}" text-anchor="middle" font-size="11" font-weight="600" fill="var(--ink)">${escapeHtml(id)}</text>
        </g>
      `);
    });

    svg.innerHTML = parts.join("");

    const highlightNode = (focusId) => {
      if (!focusId) {
        svg.querySelectorAll(".graph-node, .graph-edge").forEach((el) => el.classList.remove("dimmed"));
        return;
      }
      const neighbors = new Set([focusId]);
      svg.querySelectorAll(".graph-edge").forEach((edge) => {
        const l = edge.dataset.left;
        const r = edge.dataset.right;
        if (l === focusId || r === focusId) {
          neighbors.add(l);
          neighbors.add(r);
          edge.classList.remove("dimmed");
        } else {
          edge.classList.add("dimmed");
        }
      });
      svg.querySelectorAll(".graph-node").forEach((n) => {
        n.classList.toggle("dimmed", !neighbors.has(n.dataset.nodeId));
      });
    };

    svg.querySelectorAll(".graph-node").forEach((nodeEl) => {
      nodeEl.addEventListener("mouseenter", () => highlightNode(nodeEl.dataset.nodeId));
      nodeEl.addEventListener("mouseleave", () => highlightNode(activeGraphNode));
      nodeEl.addEventListener("click", () => {
        activeGraphNode = nodeEl.dataset.nodeId;
        renderConstellation();
      });
    });

    highlightNode(activeGraphNode);
    renderGraphInspector(activeGraphNode);
  }

  function renderGraphInspector(id) {
    const pane = document.getElementById("graph-inspector");
    const rec = STATE.byId[id];
    if (!rec) return;

    const rels = STATE.relations.filter((r) => r.left.id === id || r.right.id === id);
    let bodyHtml = "";

    if (id.startsWith("FRAG-")) {
      bodyHtml = `
        <span class="badge badge-lit">${escapeHtml(FORM_LABELS[rec.form] || rec.form)}</span>
        <span class="badge badge-mode">${escapeHtml(rec.narrator_mode)}</span>
        <h3 class="reader-title" style="font-size:1.22rem;margin-top:0.65rem;">${escapeHtml(rec.title)}</h3>
        <div class="literary-body" style="font-size:0.95rem;max-height:300px;overflow-y:auto;padding-right:0.35rem;">
          ${formatFragmentBody(rec)}
        </div>
        <button type="button" class="btn-ghost" data-jump-any="${escapeHtml(id)}">アンソロジー全画面で読む →</button>
      `;
    } else if (id.startsWith("Q-")) {
      bodyHtml = `
        <span class="badge badge-mode">問い (${escapeHtml(rec.origin.kind)})</span>
        <h3 class="reader-title" style="font-size:1.18rem;margin-top:0.65rem;">${escapeHtml(rec.question)}</h3>
        <p style="font-size:0.86rem;color:var(--ink-muted);">${escapeHtml(rec.notes || "")}</p>
        <p style="font-size:0.8rem;color:var(--ink-muted);">来歴：${escapeHtml(rec.origin.detail)}</p>
      `;
    } else if (id.startsWith("MAT-")) {
      bodyHtml = `
        <span class="badge ${rec.kind === "literary_text" ? "badge-lit" : "badge-ai"}">${escapeHtml(rec.kind)}</span>
        <h3 class="reader-title" style="font-size:1.15rem;margin-top:0.65rem;">${escapeHtml(rec.title)}</h3>
        <div class="mat-invitation">${escapeHtml(rec.literary_invitation)}</div>
        <blockquote class="mat-passage" style="margin-top:0.75rem;">${escapeHtml(rec.passage)}</blockquote>
      `;
    }

    pane.innerHTML = `
      <div style="margin-bottom:0.5rem;"><code>${escapeHtml(id)}</code></div>
      ${bodyHtml}
      <div class="meta-box">
        <h3>接続する解釈的関係 (${rels.length})</h3>
        <ul class="rel-list">
          ${
            rels.length
              ? rels
                  .map(
                    (r) => `
                  <li>
                    <div><code>${escapeHtml(r.left.id)}</code> → <strong>${escapeHtml((RELATION_STYLES[r.relation_type] || { label: r.relation_type }).label)}</strong> → <code>${escapeHtml(r.right.id)}</code></div>
                    <div style="color:var(--ink-muted);margin-top:0.2rem;">${escapeHtml(r.note || "")}</div>
                  </li>`
                  )
                  .join("")
              : `<li style="color:var(--ink-muted);">まだ明示的な relation は登録されていません（次のセッションの種として開かれています）。</li>`
          }
        </ul>
      </div>
    `;
    bindJumpButtons(pane);
  }

  /* View 3: Questions Lineage */
  function renderQuestionsTree() {
    const container = document.getElementById("questions-tree");
    const childrenMap = {};
    STATE.questions.forEach((q) => (childrenMap[q.question_id] = []));
    const roots = [];
    STATE.questions.forEach((q) => {
      if (!q.previous_question_ids || q.previous_question_ids.length === 0) {
        roots.push(q);
      } else {
        q.previous_question_ids.forEach((pid) => {
          if (childrenMap[pid]) childrenMap[pid].push(q);
        });
      }
    });

    const renderBranch = (q, seen = new Set()) => {
      const frags = STATE.fragments.filter((f) => f.question_ids.includes(q.question_id));
      const next = (childrenMap[q.question_id] || []).filter((c) => !seen.has(c.question_id));
      const nextSeen = new Set(seen);
      nextSeen.add(q.question_id);

      return `
        <div id="qcard-${escapeHtml(q.question_id)}" class="branch-node">
          <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:0.4rem;">
            <code>${escapeHtml(q.question_id)}</code>
            <span style="font-size:0.78rem;color:var(--ink-muted);">${escapeHtml(q.origin.detail)}</span>
          </div>
          <div class="q-title">${escapeHtml(q.question)}</div>
          ${q.notes ? `<div style="font-size:0.83rem;color:var(--ink-muted);margin-bottom:0.5rem;">${escapeHtml(q.notes)}</div>` : ""}
          <div class="tag-row" style="margin-bottom:0;">
            ${frags.map((f) => `<button type="button" class="link-pill" data-jump-any="${escapeHtml(f.fragment_id)}">${escapeHtml(f.fragment_id)}: ${escapeHtml(f.title.slice(0, 18))}…</button>`).join("")}
          </div>
          ${next.length ? `<div class="q-branches">${next.map((c) => renderBranch(c, nextSeen)).join("")}</div>` : ""}
        </div>
      `;
    };

    container.innerHTML = roots
      .map((root) => {
        const frags = STATE.fragments.filter((f) => f.question_ids.includes(root.question_id));
        const children = childrenMap[root.question_id] || [];
        return `
          <div id="qcard-${escapeHtml(root.question_id)}" class="seed-card">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
              <div><code>${escapeHtml(root.question_id)}</code> <span class="badge badge-mode">human_seed</span></div>
              <span style="font-size:0.8rem;color:var(--ink-muted);">${escapeHtml(root.origin.detail)}</span>
            </div>
            <div class="q-title" style="font-size:1.18rem;">${escapeHtml(root.question)}</div>
            <p style="margin:0 0 0.7rem;font-size:0.85rem;color:var(--ink-muted);">${escapeHtml(root.notes || "")}</p>
            <div class="tag-row">
              ${frags.map((f) => `<button type="button" class="link-pill" data-jump-any="${escapeHtml(f.fragment_id)}">${escapeHtml(f.fragment_id)}: ${escapeHtml(f.title.slice(0, 22))}…</button>`).join("")}
            </div>
            ${
              children.length
                ? `<div class="q-branches">${children.map((c) => renderBranch(c, new Set([root.question_id]))).join("")}</div>`
                : ""
            }
          </div>
        `;
      })
      .join("");

    bindJumpButtons(container);
  }

  /* View 4: Materials Library */
  function updateMaterialPills() {
    document.querySelectorAll("#mat-kind-filter .pill-btn").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.kind === activeMaterialKind);
    });
  }

  function renderMaterials() {
    const grid = document.getElementById("materials-grid");
    const items = STATE.materials
      .slice()
      .sort((a, b) => {
        if (a.kind === b.kind) return 0;
        return a.kind === "literary_text" ? -1 : 1;
      })
      .filter((m) => activeMaterialKind === "all" || m.kind === activeMaterialKind);

    grid.innerHTML = items
      .map((m) => {
        const isLit = m.kind === "literary_text";
        const usedBy = STATE.fragments.filter((f) => f.material_ids.includes(m.material_id));
        const authors =
          m.source.authors.length > 2
            ? `${m.source.authors[0]} et al.`
            : m.source.authors.join(", ");
        return `
          <div id="mcard-${escapeHtml(m.material_id)}" class="mat-card">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:0.5rem;">
              <code>${escapeHtml(m.material_id)}</code>
              <span class="badge ${isLit ? "badge-lit" : "badge-ai"}">${isLit ? "哲学・文学原典" : "AI研究抜粋"}</span>
            </div>
            <h3 class="mat-title">${escapeHtml(m.title)}</h3>
            <div style="font-size:0.8rem;color:var(--ink-muted);">
              ${escapeHtml(authors)} (${escapeHtml(m.source.year)}) · ${escapeHtml(m.context)}
              — <a href="${escapeHtml(m.source.url)}" target="_blank" rel="noopener noreferrer" style="color:var(--accent-indigo);">原典リンク ↗</a>
            </div>
            <div class="mat-invitation">${escapeHtml(m.literary_invitation)}</div>
            <blockquote class="mat-passage">${escapeHtml(m.passage)}</blockquote>
            <div class="tag-row" style="margin-bottom:0;">
              ${usedBy.map((f) => `<button type="button" class="link-pill" data-jump-any="${escapeHtml(f.fragment_id)}">${escapeHtml(f.fragment_id)} で対話</button>`).join("")}
            </div>
            <div class="mat-scope"><strong>留保：</strong>${escapeHtml(m.scope_note)}</div>
          </div>
        `;
      })
      .join("");

    bindJumpButtons(grid);
  }

  /* View 5: Sessions Chronicle */
  function renderSessions() {
    const container = document.getElementById("sessions-timeline");
    container.innerHTML = STATE.sessions
      .slice()
      .reverse()
      .map((s) => `
        <div class="session-card">
          <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;margin-bottom:0.4rem;">
            <div><strong><code>${escapeHtml(s.session_id)}</code></strong> · <span class="badge badge-ai">${escapeHtml(s.prompt_template)}</span></div>
            <span style="font-size:0.82rem;color:var(--ink-muted);">${escapeHtml(s.started_at)}</span>
          </div>
          <p style="margin:0 0 0.5rem;font-weight:500;">${escapeHtml(s.human_direction)}</p>
          ${s.notes ? `<p style="margin:0 0 0.65rem;font-size:0.84rem;color:var(--ink-muted);">${escapeHtml(s.notes)}</p>` : ""}
          <div class="tag-row" style="margin-bottom:0;">
            ${s.produced_fragment_ids.map((fid) => `<button type="button" class="link-pill badge-lit" data-jump-any="${escapeHtml(fid)}">生成断片: ${escapeHtml(fid)}</button>`).join("")}
            ${s.new_question_ids.map((qid) => `<button type="button" class="link-pill" data-jump-question="${escapeHtml(qid)}">新しい問い: ${escapeHtml(qid)}</button>`).join("")}
          </div>
        </div>
      `)
      .join("");

    bindJumpButtons(container);
  }

  async function init() {
    const raw = await loadData();
    const byId = {};
    ["questions", "motifs", "materials", "fragments", "relations", "sessions"].forEach((col) => {
      raw[col].forEach((rec) => {
        const id =
          rec.question_id ||
          rec.motif_id ||
          rec.material_id ||
          rec.fragment_id ||
          rec.relation_id ||
          rec.session_id;
        byId[id] = rec;
      });
    });

    STATE = { ...raw, byId };
    activeFragmentId = STATE.fragments[STATE.fragments.length - 1].fragment_id;

    renderStats();
    populateMotifFilter();
    renderFragmentList();
    renderRelationLegend();
    renderQuestionsTree();
    renderMaterials();
    renderSessions();

    document.querySelectorAll(".tab-btn").forEach((btn) => {
      btn.addEventListener("click", () => switchTab(btn.dataset.view));
    });

    ["frag-search", "frag-form-filter", "frag-motif-filter", "frag-status-filter"].forEach((id) => {
      document.getElementById(id).addEventListener("input", renderFragmentList);
      document.getElementById(id).addEventListener("change", renderFragmentList);
    });

    document.querySelectorAll("#mat-kind-filter .pill-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        activeMaterialKind = btn.dataset.kind;
        updateMaterialPills();
        renderMaterials();
      });
    });

    const themeBtn = document.getElementById("theme-toggle");
    themeBtn.addEventListener("click", () => {
      const root = document.documentElement;
      const next = root.getAttribute("data-theme") === "paper" ? "night" : "paper";
      root.setAttribute("data-theme", next);
      themeBtn.textContent = next === "paper" ? "夜想モード" : "和紙モード";
    });
  }

  init().catch((err) => {
    const ws = document.querySelector(".workspace");
    ws.innerHTML = `<div class="reader-pane"><p>${escapeHtml(err.message)}</p></div>`;
  });
})();
