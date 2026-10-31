/* Speculative Translation Lab — static GitHub Pages client.
   Outputs are SPECULATIVE. Not a decipherment. */

const EXAMPLES = [
  "The merchant sends copper to the city",
  "The king of Harappa gives grain",
  "A man receives fish",
  "Owner seal of the temple offering",
];

let glyphs = {};
let lexicon = {};
let corpus = {};

async function loadData() {
  const [g, l, c] = await Promise.all([
    fetch("assets/glyphs.json").then((r) => r.json()),
    fetch("assets/lexicon.json").then((r) => r.json()),
    fetch("assets/corpus_meta.json").then((r) => r.json()),
  ]);
  glyphs = g;
  lexicon = l;
  corpus = c;
  document.getElementById("banner").textContent = corpus.banner;
}

function tokenize(sentence) {
  return (sentence.toLowerCase().match(/[a-z']+/g) || []);
}

function pickSign(concept, used, tokenIndex) {
  const ranked = corpus.ranked_signs || Object.keys(glyphs);
  const prefer = concept.prefer_position || "middle";
  // Prefer earlier ranks; slight bias by position preference hash
  const candidates = ranked.filter((s) => !used.has(s));
  const pool = candidates.length ? candidates : ranked;
  // Position bias: beginning → early ranks, ending → later-ish mid ranks
  let idx = 0;
  if (prefer === "beginning") idx = Math.min(tokenIndex, pool.length - 1);
  else if (prefer === "ending") idx = Math.min(pool.length - 1, Math.floor(pool.length * 0.35) + tokenIndex);
  else idx = Math.min(pool.length - 1, 2 + tokenIndex);
  const sign = pool[idx];
  const rank = ranked.indexOf(sign) + 1;
  return { sign, rank, notes: [
    `Selected by corpus frequency rank #${rank}.`,
    `Preferred position bucket '${prefer}'.`,
    "Sign identity is a HEURISTIC stand-in — not a proven phonetic value.",
  ]};
}

function translate(sentence, direction, languageFrame) {
  const tokens = tokenize(sentence);
  const used = new Set();
  const assignments = [];
  const signsLogical = [];
  let contentI = 0;

  for (const tok of tokens) {
    let concept = lexicon[tok];
    if (concept && (concept.semantic_tags || []).includes("skip")) {
      assignments.push({ english: tok, skipped: true, sign: null, concept });
      continue;
    }
    if (!concept) {
      concept = {
        gloss_frame: `unmapped English lemma '${tok}' (placeholder sign)`,
        proto_dravidian_placeholder: "no lexicon entry — speculative filler",
        semantic_tags: ["unknown"],
        prefer_position: "middle",
      };
    }
    const { sign, rank, notes } = pickSign(concept, used, contentI);
    used.add(sign);
    signsLogical.push(sign);
    assignments.push({
      english: tok,
      skipped: false,
      sign,
      rank,
      notes,
      concept,
      motif: glyphs[sign]?.motif || "symbol",
    });
    contentI += 1;
  }

  const display = direction === "RTL" ? [...signsLogical].reverse() : [...signsLogical];
  const known = assignments.filter((a) => !a.skipped && lexicon[a.english]).length;
  const total = assignments.filter((a) => !a.skipped).length || 1;
  const confidence = Math.min(0.22, 0.05 + 0.12 * (known / total));

  return {
    sentence,
    direction,
    languageFrame,
    display,
    assignments,
    confidence,
    evidence_tier: "speculative_interpretation",
  };
}

function glyphImg(signId) {
  const g = glyphs[signId];
  if (!g) return "";
  return `<img src="${g.data_url || g.png}" alt="${g.motif} symbol" />`;
}

function renderResult(result) {
  const out = document.getElementById("result");
  out.hidden = false;

  document.getElementById("metric-conf").textContent = result.confidence.toFixed(2);
  document.getElementById("metric-tier").textContent = "Speculative";
  document.getElementById("metric-n").textContent = String(result.display.length);
  document.getElementById("english-out").textContent = result.sentence;

  const glyphRow = document.getElementById("glyph-row");
  glyphRow.innerHTML = result.display.map((sid) => {
    const motif = glyphs[sid]?.motif || "symbol";
    return `<div class="glyph-card">${glyphImg(sid)}<div class="motif">${motif}-like</div></div>`;
  }).join("");

  const joiner = result.direction === "RTL" ? " ← " : " → ";
  document.getElementById("order-line").textContent =
    `Reading order (${result.direction}): ` +
    result.display.map((s) => glyphs[s]?.motif || s).join(joiner);

  const map = document.getElementById("mapping");
  map.innerHTML = result.assignments
    .filter((a) => !a.skipped && a.sign)
    .map((a) => `
      <div class="card">
        ${glyphImg(a.sign)}
        <div class="en">${a.english}</div>
        <div class="frame">${a.concept.gloss_frame}</div>
      </div>`).join("");

  const tbody = document.querySelector("#proof-table tbody");
  tbody.innerHTML = result.assignments.map((a) => `
    <tr>
      <td>${a.english}</td>
      <td>${a.skipped ? "—" : (a.motif || "—")}</td>
      <td>${a.skipped ? "skipped" : ("#" + a.rank)}</td>
      <td>${a.concept.gloss_frame}</td>
      <td>${a.concept.proto_dravidian_placeholder || "—"}</td>
    </tr>`).join("");

  const jsBody = document.querySelector("#js-table tbody");
  jsBody.innerHTML = Object.entries(corpus.comparisons || {}).map(([k, v]) => `
    <tr>
      <td>Indus vs ${k}</td>
      <td>${Number(v.js_divergence).toFixed(3)}</td>
      <td>${v.note}</td>
    </tr>`).join("");

  document.getElementById("assumptions").innerHTML = [
    `Assumed language frame: ${result.languageFrame}`,
    `Assumed reading direction for display: ${result.direction}`,
    "Assumed that Indus signs encode language (may be partly non-linguistic).",
    "Assumed concept→sign links from lexicon frames + corpus frequency heuristics.",
    "Visual motifs are readability proxies — not a proven Indus signary.",
  ].map((x) => `<li>${x}</li>`).join("");

  document.getElementById("limitations").innerHTML = [
    "No bilingual key exists for Indus.",
    "This public page is a static demo; full Python analyses live in the research repo.",
    "English word order is not Indus word order.",
    "Comparative scores measure structure, not translation accuracy.",
    "This output must never be cited as a decipherment.",
  ].map((x) => `<li>${x}</li>`).join("");

  document.getElementById("ids-hidden").textContent = result.display.join(" ");
}

function setupTabs() {
  document.querySelectorAll("nav.tabs button").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("nav.tabs button").forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(btn.dataset.panel).classList.add("active");
    });
  });
}

function setupLab() {
  const examples = document.getElementById("examples");
  EXAMPLES.forEach((ex) => {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = ex;
    b.addEventListener("click", () => {
      document.getElementById("sentence").value = ex;
    });
    examples.appendChild(b);
  });

  document.getElementById("translate-btn").addEventListener("click", () => {
    const sentence = document.getElementById("sentence").value.trim();
    if (!sentence) return;
    const direction = document.getElementById("direction").value;
    const languageFrame = document.getElementById("frame").value;
    const result = translate(sentence, direction, languageFrame);
    renderResult(result);
  });
}

window.addEventListener("DOMContentLoaded", async () => {
  setupTabs();
  await loadData();
  setupLab();
  document.getElementById("corpus-stats").textContent =
    `${corpus.n_inscriptions} Indus inscriptions · inventory ${corpus.inventory_size} (demo corpus)`;
});
