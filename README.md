# IndusScript AI

Computational linguistics, historical data mining and comparative decipherment **research platform** for investigating the undeciphered Indus Valley writing system.

> **Integrity notice:** This software does **not** claim that the Indus script has been deciphered. Similarity scores and candidate readings are hypotheses for scientific evaluation — not established translations or proof of linguistic ancestry.

## Research questions

Keep these distinct:

- **A** — Are the symbols visually similar?
- **B** — Do the writing systems exhibit similar structural properties?
- **C** — Is there evidence of linguistic relationships, borrowing or contact?
- **D** — Can any Indus sign sequences be assigned defensible candidate meanings?

## Features

1. Source registry with licence / availability / download status  
2. Ingestion adapters (probe + optional HF; synthetic test corpora)  
3. Unified SQLite data model (raw payloads preserved separately)  
4. Sign normalisation (no cross-civilisation merges without evidence)  
5. Frequency, n-gram, positional, entropy, embedding and structural analyses  
6. Meluhha evidence index + NetworkX trade graph  
7. Candidate language hypothesis scoring  
8. Speculative interpretation generator with evidence tiers  
9. Statistical falsification (shuffles, permutations, BH FDR, bootstrap)  
10. Optional OpenCV vision pipeline (question A)  
11. Streamlit dashboard (15 sections)  
12. Exportable JSON / CSV / Markdown reports  

## Requirements

- Python 3.11+ (tested on 3.12)
- See `requirements.txt`

Optional: `torch`, `transformers`, `datasets` for heavy ML / HF downloads.

## Public website (GitHub Pages)

Interactive browser demo (Speculative Translation Lab — static, no server):

**https://ammarjamshed.github.io/indusscript-ai/**

> GitHub Pages serves static sites only. The full Streamlit research dashboard needs a Python host (local or Streamlit Community Cloud). The Pages site covers the public translation lab with the parchment UI.

## Quick start (full research app)

```bash
cd indusscript-ai
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python app.py --report
streamlit run dashboard/app.py
```

Bootstrap with remote source probes (no bulk scrape):

```bash
python app.py --network --report
```

## Tests

```bash
pytest -q
```

## Project layout

```
indusscript-ai/
  app.py
  config/
  data/                # raw, processed, external, synthetic, SQLite DB
  ingestion/           # adapters + provenance registry
  normalisation/
  corpora/
  analysis/
  historical/
  hypotheses/
  vision/
  database/
  dashboard/
  reports/
  tests/
  documentation/
```

## Documentation

- [Research methodology](documentation/METHODOLOGY.md)
- [Provenance register](documentation/PROVENANCE_REGISTER.md)

## Synthetic data

When public APIs are licence-restricted or unavailable, the platform seeds **clearly labelled `SYNTHETIC`** corpora so the pipeline and dashboard remain demonstrable. Synthetic rows are never presented as historical evidence.

## Related prior work

An earlier visual-similarity experiment lives at `D:\indus-script-comparison`. IndusScript AI is a broader research platform with statistical falsification, Meluhha indexing and hypothesis testing — not a decipherment claim.

## Licence / scholarly use

Respect upstream dataset licences. Do not redistribute restricted corpora. Cite primary publications when replacing synthetic Meluhha stubs with real tablets.
