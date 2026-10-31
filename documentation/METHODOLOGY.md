# IndusScript AI — Research Methodology

## Integrity statement

IndusScript AI does **not** claim that the Indus script has been deciphered. The platform exists to **discover, test, rank and document** candidate hypotheses under explicit epistemic controls.

Similarity scores, embeddings and candidate readings are **not** proof of common ancestry, shared phonetics or established translations.

## Four research questions (never conflated)

| ID | Question | Typical modules |
|----|----------|-----------------|
| A | Are the symbols visually similar? | `vision/` |
| B | Do writing systems share structural properties? | `analysis/` (frequency, n-grams, entropy, embeddings, structure) |
| C | Is there evidence of linguistic relationships, borrowing or contact? | `historical/`, hypothesis contact criteria |
| D | Can Indus sequences be assigned defensible candidate meanings? | `hypotheses/inference.py`, validation, falsification |

A positive answer to A does not imply B, C or D. A positive answer to B does not imply C or D.

## Data policy

1. Inspect documentation for each source.
2. Identify format, licence and API limits.
3. Download only where permitted.
4. Record provenance and retrieval date in the source registry.
5. Preserve original payloads separately from normalised records.
6. Never silently substitute fabricated historical records.
7. Synthetic data is allowed **only** for software testing and must be labelled `SYNTHETIC`.

## Unified data model

Normalised `HistoricalRecord` objects separate:

- civilisation, language, writing system (distinct concepts)
- observed sign sequences
- attested translations (never invented for Indus)
- uncertainty annotations
- synthetic flag and translation status

## Comparative statistics

- Frequency distributions and Jensen–Shannon divergence
- N-grams (1–4) and conditional probabilities
- Positional probabilities; both orientations when direction is unknown
- Shannon / conditional entropy, mutual information, complexity proxies
- Word2Vec / FastText per corpus; optional masked-sign baselines
- Structural comparison reports

All of the above address **question B** unless explicitly linked to other evidence.

## Meluhha and trade

Mesopotamian references to Meluhha are indexed as **contact evidence (question C)**. Meluhha is **not** assumed to be identical to the Indus inscription language.

Trade graphs (NetworkX) encode historically discussed corridors (Dilmun, Magan, Mesopotamia, Indus) with confidence annotations.

## Hypothesis engine

Candidate language hypotheses include Proto-Dravidian, Early Dravidian, Munda-related, Indo-Aryan-related, other, isolate, and non-linguistic/administrative.

Each is scored on ten transparent criteria. Scores are **heuristic priors for research triage**, not empirical conclusions. Independent validation remains near zero until external bilinguals or reproducible mappings exist.

## Decipherment candidates

Candidate interpretations must show:

1. inscription and sign sequence  
2. archaeological context  
3. proposed structure  
4. language frame and vocabulary assumptions  
5. correspondence explanation  
6. alternatives  
7. held-out / contradiction notes  
8. evidence tier and confidence  

English glosses are **hypotheses**, never presented as facts.

## Falsification (mandatory)

Null models include:

- frequency-preserving shuffles
- random inventory draws
- length-matched donor controls
- permutation tests
- bootstrap confidence intervals
- Benjamini–Hochberg FDR correction
- cross-validation of structural metrics

Hypotheses are **penalised** when apparent similarity is reproducible under null models.

## Chronology, geography and genre

Analyses must account for chronological gaps, geographic distance, trade intermediaries, writing conventions, genre differences, short Indus inscription lengths, and uncertain archaeological attribution.

## Ultimate goal

Determine whether evidence **supports** a plausible decipherment pathway — not to manufacture one.
