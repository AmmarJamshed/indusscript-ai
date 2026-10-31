"""IndusScript AI — Streamlit research dashboard."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from analysis.embeddings import embedding_report
from analysis.frequency import frequency_report, frequencies_by_site
from analysis.ngrams import ngram_report
from analysis.positional import compare_directions
from analysis.sequence_analysis import compare_corpora
from config.settings import RESEARCH_QUESTIONS, ensure_directories
from corpora.loader import load_sequences
from dashboard.helpers import (
    HAS_PLOTLY,
    bar_from_counter_items,
    boundary_plain_table,
    db,
    download_json_button,
    js_plain_table,
    plot_trade_network,
    records_frame,
    render_chart,
    show_integrity_banner,
    show_research_questions,
)
from dashboard.theme import apply_ivc_theme, paper_note, section_rule, speculative_banner

try:
    import plotly.express as px
except ImportError:
    px = None  # type: ignore
from historical.meluhha import meluhha_summary, search_meluhha
from historical.trade_network import graph_summary, to_plotly_elements
from hypotheses.candidate_languages import score_hypotheses
from hypotheses.falsification import run_falsification_suite
from hypotheses.inference import generate_candidates, interpretation_report
from hypotheses.speculative_translator import (
    SPECULATIVE_BANNER,
    english_to_indus,
    indus_to_english_hypothesis,
)
from ingestion.pipeline import run_ingestion
from reports.generator import export_report
from vision.glyph_render import ensure_glyphs, motif_name

st.set_page_config(
    page_title="IndusScript AI",
    page_icon="📜",
    layout="wide",
)

SECTIONS = [
    "1. Executive Research Overview",
    "2. Corpus Explorer",
    "3. Indus Inscription Explorer",
    "4. Sign Frequency Analysis",
    "5. N-gram Analysis",
    "6. Historical Trade Network",
    "7. Meluhha Evidence Explorer",
    "8. Babylonian Comparison",
    "9. Egyptian Comparison",
    "10. Dravidian and Munda Hypothesis Testing",
    "11. Sign Embedding Visualisation",
    "12. Candidate Interpretation Explorer",
    "13. Statistical Falsification",
    "14. Source and Provenance Registry",
    "15. Research Reports",
    "16. Speculative Translation Lab",
]


def ensure_data() -> None:
    ensure_directories()
    database = db()
    if not database.count_by_civilisation():
        with st.spinner("Seeding synthetic corpora and probing source availability..."):
            run_ingestion(database, include_network_probes=False, include_synthetic=True)


def main() -> None:
    apply_ivc_theme()
    ensure_data()
    st.sidebar.markdown("## IndusScript AI")
    st.sidebar.caption("Comparative research · parchment view")
    # Default to Speculative Translation Lab for the interactive demo
    default_idx = SECTIONS.index("16. Speculative Translation Lab")
    section = st.sidebar.radio("Section", SECTIONS, index=default_idx)
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "<div style='padding:0.6rem;border:1px solid #C4893B;background:#3A2F26'>"
        "Indus remains undeciphered. What you see are hypotheses for testing."
        "</div>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        "<div style='margin-top:0.6rem;padding:0.6rem;border:1px solid #B85C38;"
        "background:#4A3428'>Open <b>16. Speculative Translation Lab</b> for "
        "English → assumed Indus symbols.</div>",
        unsafe_allow_html=True,
    )

    if section.startswith("1."):
        page_overview()
    elif section.startswith("2."):
        page_corpus()
    elif section.startswith("3."):
        page_indus()
    elif section.startswith("4."):
        page_frequency()
    elif section.startswith("5."):
        page_ngrams()
    elif section.startswith("6."):
        page_trade()
    elif section.startswith("7."):
        page_meluhha()
    elif section.startswith("8."):
        page_babylonian()
    elif section.startswith("9."):
        page_egyptian()
    elif section.startswith("10."):
        page_hypotheses()
    elif section.startswith("11."):
        page_embeddings()
    elif section.startswith("12."):
        page_interpretations()
    elif section.startswith("13."):
        page_falsification()
    elif section.startswith("14."):
        page_sources()
    elif section.startswith("15."):
        page_reports()
    else:
        page_speculative_lab()


def page_overview() -> None:
    st.title("Executive Research Overview")
    show_integrity_banner()
    show_research_questions()
    section_rule()
    counts = db().count_by_civilisation()
    cols = st.columns(4)
    for i, (civ, n) in enumerate(sorted(counts.items())):
        cols[i % 4].metric(civ.replace("_", " ").title(), n)
    paper_note(
        "Platform purpose: discover, test, rank and document candidate linguistic "
        "hypotheses about the Indus writing system — without manufacturing a decipherment. "
        "Rows marked as test data exist only to exercise the software when licence-restricted "
        "sources cannot be mirrored automatically."
    )
    if st.button("Re-run ingestion (synthetic + local)"):
        run_ingestion(db(), include_network_probes=True, include_synthetic=True)
        st.success("Ingestion finished")
        st.rerun()


def page_corpus() -> None:
    st.title("Corpus Explorer")
    show_integrity_banner()
    df = records_frame()
    civs = ["(all)"] + sorted(df["Civilisation"].unique().tolist()) if not df.empty else ["(all)"]
    civ = st.selectbox("Civilisation", civs)
    site = st.text_input("Filter archaeological site contains")
    view = df if civ == "(all)" else df[df["Civilisation"] == civ]
    if site and not view.empty:
        view = view[view["Site"].fillna("").str.contains(site, case=False)]
    st.dataframe(view, use_container_width=True, hide_index=True)
    st.download_button(
        "Export table",
        view.to_csv(index=False),
        file_name="corpus_export.csv",
        mime="text/csv",
    )


def page_indus() -> None:
    st.title("Indus Inscription Explorer")
    show_integrity_banner()
    paper_note("Translations are never invented as facts for Indus records.")
    df = records_frame("indus")
    q = st.text_input("Search motifs or record id")
    sites = sorted({s for s in df["Site"].dropna().unique()}) if not df.empty else []
    site = st.selectbox("Site", ["(all)"] + sites)
    view = df
    if site != "(all)":
        view = view[view["Site"] == site]
    if q and not view.empty:
        mask = view.apply(
            lambda r: q.lower() in str(r.get("Symbol motifs", "")).lower()
            or q.lower() in str(r.get("Record", "")).lower(),
            axis=1,
        )
        view = view[mask]
    st.dataframe(view, use_container_width=True, hide_index=True)
    if not view.empty:
        # Map display Record back to full id
        display_ids = view["Record"].tolist()
        chosen = st.selectbox("Inspect inscription", display_ids)
        full_ids = [
            r.record_id
            for r in db().get_records("indus")
            if r.record_id.replace("SYNTHETIC-", "") == chosen or r.record_id == chosen
        ]
        rid = full_ids[0] if full_ids else None
        rec = db().get_record(rid) if rid else None
        if rec:
            section_rule()
            st.markdown(f"### {rec.archaeological_site or 'Unknown site'} · {rec.object_type or 'object'}")
            paths = ensure_glyphs(rec.sign_sequence, size=120)
            cols = st.columns(min(len(rec.sign_sequence), 8))
            for i, sign in enumerate(rec.sign_sequence):
                with cols[i % len(cols)]:
                    st.image(paths[sign], use_container_width=True)
                    st.caption(motif_name(sign))
            paper_note(
                f"Direction: {rec.reading_direction or 'unknown'} · "
                f"Status: {rec.translation_status} · "
                f"{'Test data' if rec.is_synthetic else 'Source record'}"
            )


def page_frequency() -> None:
    st.title("Sign Frequency Analysis")
    paper_note(RESEARCH_QUESTIONS["B"])
    civ = st.selectbox("Corpus", sorted(db().count_by_civilisation().keys()), index=0)
    seqs = load_sequences(civ, db())
    report = frequency_report(seqs)
    render_chart(bar_from_counter_items(report["top_20"], f"Most common symbols — {civ}"))
    c1, c2, c3 = st.columns(3)
    c1.metric("Inscriptions", report["n_sequences"])
    c2.metric("Symbol inventory", report["inventory_size"])
    c3.metric("Total signs counted", report["token_count"])
    paper_note(report.get("caveat", ""))
    if civ == "indus":
        by_site = frequencies_by_site(db().get_records("indus"))
        st.subheader("By archaeological site")
        site_df = pd.DataFrame(
            [{"Site": s, "Distinct symbols": len(c), "Signs counted": sum(c.values())} for s, c in by_site.items()]
        )
        st.dataframe(site_df, use_container_width=True, hide_index=True)
    download_json_button(report, f"frequency_{civ}.json")


def page_ngrams() -> None:
    st.title("N-gram Analysis")
    paper_note(RESEARCH_QUESTIONS["B"])
    civ = st.selectbox("Corpus", sorted(db().count_by_civilisation().keys()))
    seqs = load_sequences(civ, db())
    report = ngram_report(seqs)
    for order, payload in report["orders"].items():
        st.subheader(f"Common {order}-symbol patterns")
        top = payload["top"]
        if top:
            df = pd.DataFrame(
                [
                    {
                        "Motif pattern": " · ".join(motif_name(s) for s in t["sequence"]),
                        "Times seen": t["count"],
                    }
                    for t in top
                ]
            )
            if HAS_PLOTLY and px is not None:
                render_chart(
                    px.bar(
                        df.head(12),
                        x="Motif pattern",
                        y="Times seen",
                        title=f"Top {order}-symbol patterns",
                    )
                )
            else:
                st.bar_chart(df.head(12).set_index("Motif pattern")["Times seen"])
    st.subheader("Repeated sequences")
    rep = pd.DataFrame(
        [
            {
                "Length": r["n"],
                "Motif pattern": " · ".join(motif_name(s) for s in r["sequence"]),
                "Times seen": r["count"],
            }
            for r in report["repeated"]
        ]
    )
    st.dataframe(rep, use_container_width=True, hide_index=True)
    paper_note(report.get("caveat", ""))
    download_json_button(report, f"ngrams_{civ}.json")


def page_trade() -> None:
    st.title("Historical Trade Network")
    paper_note(RESEARCH_QUESTIONS["C"])
    summary = graph_summary()
    speculative_banner(summary["caveat"])
    fig = plot_trade_network(to_plotly_elements())
    if fig is not None:
        render_chart(fig)
    else:
        paper_note("Interactive graph needs plotly. Showing places as a list instead.")
        st.dataframe(pd.DataFrame(summary["nodes"]), use_container_width=True, hide_index=True)
    c1, c2 = st.columns(2)
    c1.metric("Places & records", summary["n_nodes"])
    c2.metric("Links", summary["n_edges"])
    download_json_button(summary, "trade_network.json")


def page_meluhha() -> None:
    st.title("Meluhha Evidence Explorer")
    st.caption(RESEARCH_QUESTIONS["C"])
    period = st.text_input("Period filter")
    interpreter = st.checkbox("Interpreter references only")
    query = st.text_input("Keyword search")
    rows = search_meluhha(
        db(),
        interpreter_only=interpreter,
        period=period or None,
        query=query or None,
    )
    st.info(meluhha_summary(db())["caveat"])
    st.dataframe(pd.DataFrame([r.to_dict() for r in rows]), use_container_width=True)


def page_babylonian() -> None:
    st.title("Babylonian / Mesopotamian Comparison")
    show_integrity_banner()
    paper_note(
        "Structural comparison only (research question B). "
        "Similar writing patterns are not proof of shared language or meaning."
    )
    corpora = {
        "indus": load_sequences("indus", db()),
        "sumerian": load_sequences("sumerian", db()),
        "akkadian": load_sequences("akkadian", db()),
    }
    report = compare_corpora({k: v for k, v in corpora.items() if v})
    st.subheader("How similar are the sign-frequency shapes?")
    js_plain_table(report.get("js_divergence", {}))
    paper_note(str(report.get("integrity_note", "")))
    download_json_button(report, "babylonian_comparison.json")


def page_egyptian() -> None:
    st.title("Egyptian Comparison")
    show_integrity_banner()
    paper_note(
        "This page compares structure and positions (questions A/B). "
        "It does not translate Indus with Egyptian."
    )
    corpora = {
        "indus": load_sequences("indus", db()),
        "egyptian": load_sequences("egyptian", db()),
    }
    report = compare_corpora({k: v for k, v in corpora.items() if v})
    pos = compare_directions(corpora["indus"]) if corpora["indus"] else {}
    st.subheader("Structural difference (Indus vs Egyptian)")
    js_plain_table(report.get("js_divergence", {}))
    section_rule()
    st.subheader("Indus direction sensitivity")
    paper_note(
        pos.get("note")
        or "When reading direction is uncertain, both orientations are examined."
    )
    boundary_plain_table(
        pos.get("boundary_enriched_original", [])[:5],
        "Symbols that favour the start or end of inscriptions",
    )
    download_json_button(report, "egyptian_comparison.json")


def page_hypotheses() -> None:
    st.title("Dravidian and Munda Hypothesis Testing")
    paper_note(RESEARCH_QUESTIONS["C"] + " / " + RESEARCH_QUESTIONS["D"])
    scores = [h.to_dict() for h in score_hypotheses()]
    df = pd.DataFrame(
        [
            {
                "Hypothesis": s["label"],
                "Overall score": round(s["overall"], 3),
                **{k.replace("_", " ").title(): round(v, 2) for k, v in s["scores"].items()},
            }
            for s in scores
        ]
    )
    if HAS_PLOTLY and px is not None:
        render_chart(
            px.bar(
                df,
                x="Hypothesis",
                y="Overall score",
                title="Heuristic scores (research triage — not proof)",
            )
        )
    else:
        st.bar_chart(df.set_index("Hypothesis")["Overall score"])
    st.dataframe(df, use_container_width=True, hide_index=True)
    speculative_banner(
        "Do not force a language family onto the evidence. Independent validation is near zero."
    )


def page_embeddings() -> None:
    st.title("Sign Embedding Visualisation")
    paper_note(RESEARCH_QUESTIONS["B"] + " — closeness in the chart is not shared meaning.")
    civ = st.selectbox("Corpus", ["indus", "sumerian", "akkadian", "egyptian"])
    seqs = load_sequences(civ, db())
    with st.spinner("Learning symbol neighbourhoods..."):
        report = embedding_report(seqs, civ)
    sample = report.get("word2vec_vectors_sample", {})
    if sample:
        rows = []
        for tok, vec in sample.items():
            rows.append(
                {
                    "motif": motif_name(tok),
                    "dim0": vec[0],
                    "dim1": vec[1] if len(vec) > 1 else 0.0,
                }
            )
        emb_df = pd.DataFrame(rows)
        if HAS_PLOTLY and px is not None:
            fig = px.scatter(
                emb_df,
                x="dim0",
                y="dim1",
                text="motif",
                title="Sample symbol neighbourhoods",
            )
            render_chart(fig)
        else:
            st.scatter_chart(emb_df, x="dim0", y="dim1")
            st.dataframe(emb_df, use_container_width=True, hide_index=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Method", report.get("backend", "—"))
    c2.metric("Vocabulary size", report.get("word2vec_vocab", 0))
    mb = report.get("masked_baseline", {})
    c3.metric("Naive predict accuracy", f"{mb.get('accuracy', 0):.2f}")
    paper_note(report.get("caveat", ""))
    download_json_button(report, f"embeddings_{civ}.json")


def page_interpretations() -> None:
    st.title("Candidate Interpretation Explorer")
    paper_note(RESEARCH_QUESTIONS["D"])
    speculative_banner("Candidate readings are SPECULATIVE. They are not established translations.")
    lang = st.selectbox(
        "Candidate language frame",
        ["Proto-Dravidian", "Munda-related", "Language isolate", "Non-linguistic"],
    )
    if st.button("Generate / refresh candidates"):
        generate_candidates(db(), candidate_language=lang)
    report = interpretation_report(db())
    paper_note(report["integrity"])
    for c in report["candidates"]:
        title = (
            f"{c['interpretation_id']} · confidence {c['confidence']:.2f} · "
            f"{' · '.join(motif_name(s) for s in c.get('sign_sequence', []))}"
        )
        with st.expander(title):
            if c.get("sign_sequence"):
                paths = ensure_glyphs(c["sign_sequence"], size=100)
                cols = st.columns(min(len(c["sign_sequence"]), 6))
                for i, sign in enumerate(c["sign_sequence"]):
                    with cols[i % len(cols)]:
                        st.image(paths[sign], use_container_width=True)
            st.markdown(f"**Context:** {c.get('archaeological_context')}")
            st.markdown(f"**Language frame:** {c.get('candidate_language')}")
            st.markdown(f"**Explanation:** {c.get('correspondence_explanation')}")
            st.markdown("**Alternatives**")
            for alt in c.get("alternative_explanations", []):
                st.write(f"- {alt}")
            st.markdown("**Contradictions**")
            for contra in c.get("contradictions", []):
                st.write(f"- {contra}")


def page_falsification() -> None:
    st.title("Statistical Falsification")
    paper_note("Mandatory controls: does an apparent similarity survive random reshuffles?")
    comparison = st.selectbox("Comparison corpus", ["sumerian", "akkadian", "egyptian", "linear_b"])
    n_perm = st.slider("Random trials", 50, 1000, 200, 50)
    if st.button("Run falsification suite"):
        indus = load_sequences("indus", db())
        other = load_sequences(comparison, db())
        with st.spinner("Running null models..."):
            result = run_falsification_suite(indus, other, n_perm=n_perm)
        obs = result.get("observed", {})
        c1, c2, c3 = st.columns(3)
        c1.metric("Indus vs comparison difference", f"{obs.get('js_divergence_indus_vs_comparison', 0):.3f}")
        c2.metric("Indus mutual information", f"{obs.get('indus_mutual_information', 0):.3f}")
        c3.metric("Negative-control difference", f"{obs.get('negative_control_js', 0):.3f}")
        st.subheader("Test results")
        rows = []
        for name, test in result.get("tests", {}).items():
            rows.append(
                {
                    "Test": name.replace("_", " "),
                    "Observed": round(test.get("observed", 0), 4),
                    "Random average": round(test.get("null_mean", 0), 4),
                    "p-value": round(test.get("p_value", 1), 4),
                    "Still notable after correction": result.get("bh_significant", {}).get(name, False),
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        guide = result.get("interpretation_guide", {})
        paper_note(guide.get("penalty_rule", ""))
        paper_note(guide.get("caveat", ""))
        download_json_button(result, "falsification.json")


def page_sources() -> None:
    st.title("Source and Provenance Registry")
    sources = db().list_sources()
    st.dataframe(pd.DataFrame(sources), use_container_width=True)
    st.markdown(
        "Unavailable or licence-restricted sources are logged honestly. "
        "Synthetic data is never silently substituted as historical fact."
    )
    download_json_button({"sources": sources}, "provenance_registry.json")


def page_reports() -> None:
    st.title("Research Reports")
    show_integrity_banner()
    n_perm = st.slider("Falsification permutations for report", 50, 500, 100, 50)
    if st.button("Generate exportable report"):
        paths = export_report(n_perm=n_perm)
        st.success("Report written")
        for kind, path in paths.items():
            st.write(f"{kind}: `{path}`")
            if path.suffix == ".md":
                st.markdown(path.read_text(encoding="utf-8"))
            elif path.suffix == ".json":
                download_json_button(
                    __import__("json").loads(path.read_text(encoding="utf-8")),
                    path.name,
                )


def page_speculative_lab() -> None:
    """Easy-read English ↔ Indus speculative translation with proof panel."""
    st.title("Speculative Translation Lab")
    speculative_banner(SPECULATIVE_BANNER)
    paper_note(
        "How to use this page: type an English sentence (or pick an example). "
        "The lab draws an assumed Indus symbol line from corpus frequency, "
        "position patterns, and language-frame hypotheses. "
        "Proof below explains why each symbol was chosen — and what remains unproven. "
        "This is a hypothesis sandbox, not a decoder."
    )

    examples = [
        "The merchant sends copper to the city",
        "The king of Harappa gives grain",
        "A man of Meluhha receives fish",
        "Owner seal of the temple offering",
    ]
    col_a, col_b = st.columns([2, 1])
    with col_a:
        example = st.selectbox("Example sentences", examples)
        sentence = st.text_area(
            "English sentence",
            value=example,
            height=90,
            help="Content words map to speculative concept frames; a/the are skipped.",
        )
    with col_b:
        language_frame = st.selectbox(
            "Assumed language frame",
            [
                "Proto-Dravidian (assumed)",
                "Munda-related (assumed)",
                "Language isolate (assumed)",
                "Non-linguistic / admin marks (assumed)",
            ],
        )
        direction = st.radio("Display reading direction", ["RTL", "LTR"], index=0)
        st.caption("RTL is commonly discussed for Indus; both remain options.")

    go = st.button("Build assumed Indus writing", type="primary")
    if go or sentence.strip():
        result = english_to_indus(
            sentence.strip(),
            db(),
            language_frame=language_frame,
            reading_direction=direction,
        )

        st.markdown("---")
        st.subheader("Assumed translation (SPECULATIVE)")
        m1, m2, m3 = st.columns(3)
        m1.metric("Confidence", f"{result.confidence:.2f}")
        m2.metric("Evidence tier", result.evidence_tier)
        m3.metric("Signs assigned", len(result.sign_sequence))

        st.markdown("#### English")
        st.info(result.english_sentence)

        st.markdown("#### How it might look in Indus signs (assumed)")
        st.caption(
            "Symbols below are visual proxies for readability — not scanned seal photos "
            "and not a proven palaeographic catalogue. Catalogue IDs stay in the proof table."
        )
        if result.sign_sequence:
            paths = ensure_glyphs(result.sign_sequence, size=160)
            n = len(result.sign_sequence)
            tile_cols = st.columns(min(n, 8))
            for i, sign in enumerate(result.sign_sequence):
                with tile_cols[i % len(tile_cols)]:
                    st.image(paths[sign], use_container_width=True)
                    st.markdown(
                        f"<p style='text-align:center;margin:0;font-size:0.85rem'>"
                        f"<b>{motif_name(sign)}</b>-like motif</p>",
                        unsafe_allow_html=True,
                    )
            # Reading order strip
            order = " ← ".join(motif_name(s) for s in result.sign_sequence) if direction == "RTL" else " → ".join(motif_name(s) for s in result.sign_sequence)
            st.markdown(f"**Reading order ({direction}):** {order}")
        else:
            st.write("No signs assigned.")

        with st.expander("Catalogue IDs (for researchers only)", expanded=False):
            st.text(result.display_line)

        st.markdown("#### Word-by-word assumed mapping")
        if result.sign_sequence:
            map_cols = st.columns(min(max(len([a for a in result.assignments if not a.skipped]), 1), 6))
            visible = [a for a in result.assignments if not a.skipped and a.assigned_sign]
            glyph_paths = ensure_glyphs([a.assigned_sign for a in visible], size=120)
            for i, a in enumerate(visible):
                with map_cols[i % len(map_cols)]:
                    st.image(glyph_paths[a.assigned_sign], use_container_width=True)
                    st.markdown(f"**{a.english_token}**")
                    st.caption(a.assumed_gloss_frame)
        rows = []
        for a in result.assignments:
            rows.append(
                {
                    "English": a.english_token,
                    "Skipped": a.skipped,
                    "Symbol motif": motif_name(a.assigned_sign) if a.assigned_sign else "—",
                    "Catalogue ID": a.assigned_sign or "—",
                    "Corpus rank": a.sign_rank if a.sign_rank is not None else "—",
                    "Seen in corpus (count)": a.sign_frequency,
                    "Assumed meaning frame": a.assumed_gloss_frame,
                    "Reconstructed placeholder": a.reconstructed_placeholder,
                    "Preferred position": a.position_preference,
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

        with st.expander("Why this mapping? (proof from analysed corpora)", expanded=True):
            st.markdown("**Method**")
            st.write(result.proof["method"])
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Indus corpus used**")
                st.write(
                    f"- Inscriptions: **{result.proof['corpus']['n_indus_inscriptions']}**\n"
                    f"- Sign inventory: **{result.proof['corpus']['inventory_size']}**"
                )
                st.markdown("**Top signs in corpus**")
                top = result.proof["corpus"]["top_10_signs"]
                st.dataframe(
                    pd.DataFrame(
                        [{"sign": t[0], "count": t[1], "rank": t[2]} for t in top]
                    ),
                    use_container_width=True,
                )
            with c2:
                st.markdown("**Comparative structural similarity (JS divergence)**")
                st.caption("Question B only — not proof of shared meaning.")
                js = result.proof["comparative_js_divergence"]
                if js:
                    st.dataframe(
                        pd.DataFrame(
                            [
                                {
                                    "corpus": k,
                                    "js_divergence": round(v["js_divergence"], 4),
                                    "note": v["note"],
                                }
                                for k, v in js.items()
                            ]
                        ),
                        use_container_width=True,
                    )
                else:
                    st.write("No comparison corpora loaded.")

            st.markdown("**Do these assumed sign pairs actually appear together?**")
            bg = result.proof.get("bigram_attestation") or []
            if bg:
                st.dataframe(pd.DataFrame(bg), use_container_width=True)
            else:
                st.write("Need at least two content signs to check bigrams.")

            st.markdown("**Recurring Indus sequences in corpus (independent of your sentence)**")
            rep = result.proof["corpus"]["recurring_sequences_sample"]
            if rep:
                st.dataframe(
                    pd.DataFrame(
                        [
                            {"n": r["n"], "sequence": " ".join(r["sequence"]), "count": r["count"]}
                            for r in rep
                        ]
                    ),
                    use_container_width=True,
                )

            st.markdown("**Per-token selection notes**")
            for a in result.assignments:
                if a.skipped:
                    continue
                st.markdown(f"- **{a.english_token}** → `{a.assigned_sign}`")
                for note in a.evidence_notes:
                    st.caption(f"  · {note}")

        with st.expander("Assumptions & limitations (read these)", expanded=True):
            st.markdown("**Assumptions**")
            for line in result.assumptions:
                st.write(f"- {line}")
            st.markdown("**Limitations**")
            for line in result.limitations:
                st.write(f"- {line}")

        download_json_button(result.to_dict(), "speculative_translation.json")

    st.markdown("---")
    st.subheader("Reverse: Indus signs → speculative English slots")
    st.caption(
        "Fluent English reverse translations are refused as facts. "
        "You get ordered meaning *slots* only."
    )
    indus_df = records_frame("indus")
    if not indus_df.empty:
        rid = st.selectbox("Pick an Indus inscription", indus_df["record_id"].tolist())
        rec = db().get_record(rid)
        if rec and st.button("Show speculative slot reading"):
            rev = indus_to_english_hypothesis(rec.sign_sequence, db(), language_frame)
            st.warning(rev["banner"])
            paths = ensure_glyphs(rec.sign_sequence, size=140)
            cols = st.columns(min(len(rec.sign_sequence), 8))
            for i, sign in enumerate(rec.sign_sequence):
                with cols[i % len(cols)]:
                    st.image(paths[sign], use_container_width=True)
                    st.caption(motif_name(sign))
            with st.expander("Catalogue IDs (researchers only)"):
                st.text(" ".join(rec.sign_sequence))
            st.write(rev["readable_summary"])
            st.info(rev["speculative_slot_reading"])
            slot_rows = []
            for row in rev["sign_rows"]:
                slot_rows.append({**row, "motif": motif_name(row["sign"])})
            st.dataframe(pd.DataFrame(slot_rows), use_container_width=True)


if __name__ == "__main__":
    main()
