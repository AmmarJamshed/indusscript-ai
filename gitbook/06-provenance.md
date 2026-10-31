# Data Provenance & Ethics

## Policy (non-negotiable)

1. Inspect documentation for every URL
2. Identify format, licence, API limits
3. Download only where permitted
4. Record retrieval status and notes in `sources`
5. Preserve original payloads separately
6. Never fabricate historical tablets or API responses
7. Label software-test rows `SYNTHETIC`

## Registry coverage (examples)

| Source family | Examples | Default posture |
| --- | --- | --- |
| Indus corpora | field-cady repo, HF datasets, epigraphic portals | Probe / licence review before mirror |
| Mesopotamia | CDLI, ORACC, ETCSL, NaBuCCo, SEAL | API-limited; authorised exports preferred |
| Egyptian | TLA, HF BBAW, hieroglyph datasets | Licence check; vision benchmark use |
| Other | DaMoS (Linear B), PHI, Maya Vase | Controls / restricted images |

Full machine-readable registry: SQLite table `sources` and `documentation/PROVENANCE_REGISTER.md` in the repository.

## University compliance angle

Research offices can audit which datasets were touched, which were blocked by licence, and which rows are synthetic. That audit trail is itself a pedagogical artefact for digital humanities ethics courses.
