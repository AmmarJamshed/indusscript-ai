# Dataset Provenance Register

This register summarises sources tracked by IndusScript AI. Runtime status is stored in SQLite table `sources` and viewable in dashboard section 14.

| source_id | name | civilisation | format | redistribution | download posture |
|-----------|------|--------------|--------|----------------|------------------|
| field_cady_indus | field-cady Indus corpus | indus | GitHub | verify LICENSE | probe only until licence review |
| hf_indus_decipher | HF joyboseroy/indus_decipher | indus | HF datasets | verify card | optional adapter |
| joyboseroy_github | joyboseroy/indus_decipher | indus | GitHub | verify LICENSE | not auto-mirrored |
| tejesh_raut_ivs | tejesh-raut site | indus | HTML | site terms | API limited |
| indusscript_in | indusscript.in | indus | Web app | site terms | API limited |
| epigraphica_indus | Epigraphica Indus | indus | HTML | site terms | API limited |
| yajnadevam_lipi | yajnadevam/lipi | indus | GitHub | verify LICENSE | contested hypothesis material |
| cdli | CDLI | sumerian/akkadian | catalogue | CDLI ToS | authorised exports only |
| oracc | ORACC | akkadian/sumerian | project corpora | project terms | selective import |
| etcsl | ETCSL | sumerian | XML/HTML | Oxford terms | API limited |
| nabucco | NaBuCCo | babylonian | API | project licence | probe + map endpoints |
| seal_huji | SEAL | akkadian | web DB | site terms | API limited |
| oracc_saao | SAAO | akkadian | ORACC | ORACC terms | selective |
| oracc_epsd2 | ePSD2 | sumerian | lexical | ORACC terms | selective |
| tla | TLA | egyptian | web/API | TLA terms | API limited |
| hf_bbaw_egyptian | HF BBAW Egyptian | egyptian | HF | verify card | optional adapter |
| imak_egyptian | egyptian-hieroglyph-datasets | egyptian | GitHub | verify LICENSE | vision benchmark candidate |
| egyptian_hieroglyphic_text | EgyptianHieroglyphicText | egyptian | GitHub | verify LICENSE | inspect first |
| digital_egyptology | Digital Egyptology texts | egyptian | web | site terms | API limited |
| damos | DaMoS Linear B | linear_b | web DB | site terms | API limited |
| maya_vase | Maya Vase DB | other | images | often restricted | blocked by default |
| packhum | PHI Greek Inscriptions | other | web | PHI terms | control corpus candidate |
| synthetic_test_corpora | SYNTHETIC test data | multiple | JSON | internal | software testing only |

## Policy notes

- Retrieval date and download status are written at runtime.
- Raw payloads are stored separately from normalised records.
- No fabricated CDLI/ORACC/TLA tablets are generated as “real” data.
- Proto-Dravidian / Munda lexicon stubs in the synthetic set are placeholders pending cited scholarly reconstructions.
