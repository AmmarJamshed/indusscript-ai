# Architecture

## Layers

1. **Ingestion** — source-specific adapters, provenance registry, retries/caching  
2. **Storage** — SQLite (`database/`), raw payloads vs normalised records  
3. **Normalisation** — per-civilisation sign vocabularies; no cross-script merges without evidence  
4. **Analysis** — frequency, n-grams, position, entropy, embeddings, structure  
5. **Historical** — Meluhha evidence + trade network graph  
6. **Hypotheses** — language candidates, interpretation generator, falsification  
7. **Vision** — optional CV for question A  
8. **Presentation** — Streamlit dashboard + report exporter  

## Epistemic tiers

`EvidenceTier` enumerates: observed fact → computational observation → linguistic hypothesis → speculative interpretation → independently validated.

Indus translations default to `none` / hypothesis status and are never stored as attested facts when invented.

## Entry points

- `python app.py` — bootstrap DB + synthetic corpora  
- `streamlit run dashboard/app.py` — interactive UI  
- `pytest` — unit tests  
