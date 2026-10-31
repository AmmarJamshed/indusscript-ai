"""Build a colourful university-facing HTML white paper into docs/whitepaper/."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "whitepaper"
FIG_SRC = ROOT / "gitbook" / ".gitbook" / "assets"
FIG_DST = OUT / "figures"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;0,700;1,600&family=Source+Sans+3:wght@400;600;700&display=swap');
:root{
  --sand:#F3E6D4; --paper:#FFFDF8; --edge:#E8D5B7; --terr:#B85C38; --clay:#8C4A2F;
  --seal:#1F4E5F; --ochre:#C4893B; --ink:#3D2B1F; --muted:#7A6A58; --ok:#5B6B3A;
}
*{box-sizing:border-box}
body{margin:0;font-family:'Source Sans 3',system-ui,sans-serif;color:var(--ink);
background:radial-gradient(ellipse at top,#F7EBDA,#F3E6D4 50%,#E5D2B8);line-height:1.65}
.wrap{max-width:920px;margin:2rem auto 3rem;background:var(--paper);
border:1px solid var(--edge);padding:2.5rem 2.75rem 3rem;
box-shadow:0 12px 40px rgba(44,36,27,.12),0 0 0 8px rgba(184,92,56,.07)}
h1,h2,h3{font-family:'Cormorant Garamond',Georgia,serif;color:var(--clay);border-bottom:1px solid var(--edge);padding-bottom:.25rem}
h1{color:var(--terr);font-size:2.5rem;border-bottom:3px solid var(--terr)}
.hero{background:linear-gradient(135deg,rgba(184,92,56,.12),rgba(31,78,95,.1));
border-left:6px solid var(--terr);padding:1rem 1.2rem;margin:1rem 0 1.5rem}
.danger{background:#F0D0C4;border-left:6px solid var(--terr);padding:.85rem 1rem;margin:1rem 0}
.info{background:#E5EFEA;border-left:6px solid var(--seal);padding:.85rem 1rem;margin:1rem 0}
.warn{background:#F5E0C8;border-left:6px solid var(--ochre);padding:.85rem 1rem;margin:1rem 0}
.ok{background:#E8EFDC;border-left:6px solid var(--ok);padding:.85rem 1rem;margin:1rem 0}
table{width:100%;border-collapse:collapse;margin:1rem 0;font-size:.95rem;background:#FFFcf7}
th,td{border:1px solid var(--edge);padding:.55rem .7rem;text-align:left;vertical-align:top}
th{background:var(--sand);color:var(--clay)}
figure{margin:1.5rem 0;text-align:center}
figure img{max-width:100%;border:1px solid var(--edge);background:#fff}
figcaption{color:var(--muted);font-size:.9rem;margin-top:.4rem}
.meta td:first-child{font-weight:700;width:28%;background:#FBF4EA}
.chips{display:flex;flex-wrap:wrap;gap:.4rem;margin:1rem 0}
.chip{padding:.3rem .65rem;border-radius:2px;color:#fff;font-size:.85rem;font-weight:700}
.chip.a{background:var(--terr)}.chip.b{background:var(--seal)}.chip.c{background:var(--ochre)}.chip.d{background:var(--clay)}
nav.toc a{color:var(--seal);text-decoration:none}
nav.toc li{margin:.25rem 0}
footer{margin-top:2rem;padding-top:1rem;border-top:1px solid var(--edge);color:var(--muted);font-size:.9rem}
@media print{body{background:#fff}.wrap{box-shadow:none;margin:0;border:none}}
"""


def fig(name: str, caption: str) -> str:
    return f'''<figure><img src="figures/{name}" alt="{caption}"/><figcaption>{caption}</figcaption></figure>'''


def build() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG_DST.mkdir(parents=True, exist_ok=True)
    for png in FIG_SRC.glob("*.png"):
        shutil.copy2(png, FIG_DST / png.name)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>IndusScript AI — University White Paper</title>
<style>{CSS}</style>
</head>
<body>
<article class="wrap">
<header>
<h1>IndusScript AI</h1>
<p style="font-size:1.25rem;color:var(--muted);margin-top:0">
A Computational Platform for Comparative Hypothesis Testing on the Undeciphered Indus Writing System
</p>
<p><strong>White Paper v1.0 · 31 October 2026 · University &amp; research audience</strong></p>
</header>

<div class="danger">
<strong>Integrity statement.</strong> This paper does <em>not</em> claim that the Indus script has been deciphered.
Similarity scores, Meluhha references, embeddings, and assumed English readings are hypotheses for evaluation —
not established phonetics, grammar, or ancestry.
</div>

<div class="hero">
<strong>Abstract.</strong> IndusScript AI is open research infrastructure for testing whether comparative evidence
can support, weaken, or falsify candidate readings of Indus inscriptions. It separates visual (A), structural (B),
contact (C), and semantic (D) questions; tracks dataset provenance; indexes Meluhha/trade evidence; scores language
hypotheses transparently; and <em>requires</em> statistical falsification before interpretive claims.
</div>

<div class="chips">
<span class="chip a">A Visual</span>
<span class="chip b">B Structure</span>
<span class="chip c">C Contact</span>
<span class="chip d">D Meaning</span>
</div>

<table class="meta">
<tr><td>Code</td><td><a href="https://github.com/AmmarJamshed/indusscript-ai">github.com/AmmarJamshed/indusscript-ai</a></td></tr>
<tr><td>Public lab</td><td><a href="https://ammarjamshed.github.io/indusscript-ai/">ammarjamshed.github.io/indusscript-ai</a></td></tr>
<tr><td>GitBook source</td><td><code>gitbook/</code> in the repository (Git Sync ready)</td></tr>
<tr><td>Stack</td><td>Python · SQLite · Streamlit · SciPy/NetworkX · OpenCV · GitHub Pages demo</td></tr>
</table>

<nav class="toc">
<h2>Contents</h2>
<ol>
<li><a href="#exec">Executive summary for universities</a></li>
<li><a href="#gap">Motivation &amp; research gap</a></li>
<li><a href="#bg">Background</a></li>
<li><a href="#arch">Architecture</a></li>
<li><a href="#methods">Methods</a></li>
<li><a href="#fals">Falsification</a></li>
<li><a href="#results">Demonstration results</a></li>
<li><a href="#lab">Speculative Translation Lab</a></li>
<li><a href="#uni">University adoption case</a></li>
<li><a href="#lim">Limitations &amp; non-claims</a></li>
<li><a href="#cite">Cite &amp; reproduce</a></li>
</ol>
</nav>

<h2 id="exec">1. Executive summary for universities</h2>
<div class="info">
<strong>One sentence.</strong> IndusScript AI is not a decipherment product; it is a reproducible experimental apparatus
for evaluating Indus hypotheses under explicit epistemic controls.
</div>
<p>Departments need tooling that stops visual lookalikes, uncontrolled statistics, and viral “translations” from being
confused with peer-reviewed decipherment. This platform makes those risks methodologically visible for teaching and research.</p>
<table>
<tr><th>Deliverable</th><th>Academic use</th></tr>
<tr><td>Provenance registry</td><td>Data ethics / compliance seminars</td></tr>
<tr><td>Comparative engines</td><td>Corpus linguistics &amp; information-theory labs</td></tr>
<tr><td>Meluhha + trade graph</td><td>Bronze Age contact modules</td></tr>
<tr><td>Falsification suite</td><td>Training against overclaiming</td></tr>
<tr><td>Public Pages lab</td><td>Responsible outreach</td></tr>
</table>

<h2 id="gap">2. Motivation &amp; research gap</h2>
<p>Short inscriptions, unknown language identity, uncertain direction, and no bilingual key create a vacuum filled by
over-interpreted similarities. IndusScript AI implements a multi-channel, falsification-first workflow instead of a
single preferred “answer.”</p>
{fig("fig3_questions.png", "Figure 3. Questions A–D colour-coded and kept distinct.")}

<h2 id="bg">3. Background: Indus, Meluhha, comparanda</h2>
<p>Meluhha references in Mesopotamian sources are evidence of <strong>contact</strong> (Question C), not automatic
identification of the Indus inscription language (Question D). Egyptian data may serve as a labelled vision benchmark;
Linear B offers a deciphered control corpus for method checks.</p>
{fig("fig5_trade.png", "Figure 5. Schematic Dilmun–Magan–Meluhha–Mesopotamia corridors.")}

<h2 id="arch">4. Architecture</h2>
{fig("fig1_architecture.png", "Figure 1. Modular research architecture.")}
<p>Raw source payloads are stored separately from normalised records. Cross-civilisation sign merges require explicit
approved evidence. Synthetic rows are labelled <code>SYNTHETIC</code> and never silently presented as historical tablets.</p>
{fig("fig6_tiers.png", "Figure 6. Evidence tiers from observed facts to independent validation.")}

<h2 id="methods">5. Methods</h2>
<ul>
<li><strong>Statistics:</strong> frequencies, Jensen–Shannon divergence, n-grams, positional probabilities, entropy/MI, embeddings, structure reports</li>
<li><strong>History:</strong> Meluhha evidence objects + NetworkX trade graph</li>
<li><strong>Hypotheses:</strong> Proto-Dravidian, Munda, Indo-Aryan, isolate, non-linguistic, and other frames scored on ten transparent criteria</li>
</ul>
{fig("fig2_js_divergence.png", "Figure 2. Structural JS divergence on the demonstration corpus (not semantic proof).")}
{fig("fig4_hypotheses.png", "Figure 4. Heuristic language-hypothesis triage (independent validation near zero).")}

<h2 id="fals">6. Falsification framework</h2>
<div class="danger">Mandatory: hypotheses are penalised when apparent similarity is reproducible by frequency-preserving shuffles, random draws, or length-matched controls. BH-FDR corrects multiple tests.</div>
<p>Rejecting a null is still not decipherment; failing to reject is not proof of unrelatedness. Theses should publish the falsification table beside any positive structural finding.</p>

<h2 id="results">7. Demonstration results</h2>
<div class="warn">Quantitative demo figures may use labelled SYNTHETIC corpora that exercise software paths. Replace with licence-cleared CDLI/ORACC/TLA/Indus datasets for empirical publications.</div>
<table>
<tr><th>Module</th><th>Approx. demo records</th></tr>
<tr><td>Indus</td><td>25</td></tr>
<tr><td>Sumerian / Akkadian / Egyptian</td><td>25 each</td></tr>
<tr><td>Linear B</td><td>15</td></tr>
</table>

<h2 id="lab">8. Speculative Translation Lab</h2>
<p>English sentences map to assumed Indus motif glyphs via corpus frequency/position heuristics and transparent concept frames.
Confidence remains low (≈0.15 band in demos). Catalogue IDs stay collapsed for general readers.</p>
<div class="ok">Try the live lab: <a href="https://ammarjamshed.github.io/indusscript-ai/">ammarjamshed.github.io/indusscript-ai</a></div>

<h2 id="uni">9. Why universities should engage</h2>
<p>Treat the platform as shared lab infrastructure: CL departments run entropy labs; archaeology seminars teach Meluhha
citation hygiene; statistics courses stress-test cultural claims; communications offices get outreach that models caution.</p>
<div class="info">Suggested 12-hour module: provenance → frequency/JS → position/entropy → Meluhha historiography → hypothesis scoring → falsification practicum.</div>

<h2 id="lim">10. Limitations &amp; non-claims</h2>
<ul>
<li>Indus is not claimed deciphered</li>
<li>Meluhha ≠ proven Indus language identity</li>
<li>JS / embeddings / vision ≠ shared meaning</li>
<li>Glyph motif names ≠ established sign values</li>
<li>Lab English ≠ attested translations</li>
</ul>

<h2 id="cite">11. Cite &amp; reproduce</h2>
<pre style="background:#FBF4EA;border:1px solid var(--edge);padding:1rem;overflow:auto">Ammar Jamshed (2026). IndusScript AI: A Computational Platform for Comparative
Hypothesis Testing on the Undeciphered Indus Writing System (White Paper v1.0).
https://github.com/AmmarJamshed/indusscript-ai</pre>
<pre style="background:#FBF4EA;border:1px solid var(--edge);padding:1rem;overflow:auto">git clone https://github.com/AmmarJamshed/indusscript-ai.git
cd indusscript-ai
pip install -r requirements.txt
python app.py --report
streamlit run dashboard/app.py
pytest -q</pre>

<footer>
Colour system: terracotta (Indus), seal teal (comparison), ochre (contact/caution), clay (limits).
Print to PDF via the browser if needed. GitBook edition syncs from <code>gitbook/</code>.
</footer>
</article>
</body>
</html>
"""
    path = OUT / "index.html"
    path.write_text(html, encoding="utf-8")
    return path


if __name__ == "__main__":
    p = build()
    print("wrote", p)
