"""Shared dashboard helpers."""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from config.settings import INTEGRITY_NOTICE, RESEARCH_QUESTIONS
from database.db import get_db
from dashboard.theme import (
    IVC,
    apply_ivc_theme,
    paper_note,
    plotly_ivc_layout,
    speculative_banner,
)

try:
    import plotly.express as px
    import plotly.graph_objects as go

    HAS_PLOTLY = True
except ImportError:
    px = None  # type: ignore
    go = None  # type: ignore
    HAS_PLOTLY = False


@st.cache_resource
def db():
    return get_db()


def show_integrity_banner() -> None:
    paper_note(INTEGRITY_NOTICE)


def show_research_questions() -> None:
    st.markdown("### Four research questions (kept distinct)")
    for k, v in RESEARCH_QUESTIONS.items():
        st.markdown(f"**{k}.** {v}")


def records_frame(civilisation: str | None = None) -> pd.DataFrame:
    recs = db().get_records(civilisation=civilisation)
    rows = []
    for r in recs:
        from vision.glyph_render import motif_name

        motifs = " · ".join(motif_name(s) for s in r.sign_sequence) if r.sign_sequence else ""
        rows.append(
            {
                "Record": r.record_id.replace("SYNTHETIC-", ""),
                "Civilisation": r.civilisation,
                "Language": r.language or "unknown",
                "Writing system": r.writing_system,
                "Site": r.archaeological_site,
                "Object": r.object_type,
                "Direction": r.reading_direction,
                "Length": len(r.sign_sequence),
                "Symbol motifs": motifs,
                "Translation status": r.translation_status,
                "Test data": "Yes" if r.is_synthetic else "No",
            }
        )
    return pd.DataFrame(rows)


def plot_trade_network(elements: dict):
    if not HAS_PLOTLY:
        return None
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=elements["edge_x"],
            y=elements["edge_y"],
            mode="lines",
            line=dict(width=1.5, color=IVC["ochre"]),
            hoverinfo="none",
            name="links",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=elements["node_x"],
            y=elements["node_y"],
            mode="markers+text",
            text=elements["node_text"],
            textposition="top center",
            marker=dict(size=16, color=IVC["terracotta"], line=dict(width=1, color=IVC["clay"])),
            name="nodes",
            textfont=dict(color=IVC["charcoal"]),
        )
    )
    fig.update_layout(
        title="Bronze Age contact / trade graph (schematic)",
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=520,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return plotly_ivc_layout(fig)


def download_json_button(data: dict, filename: str, label: str = "Download data file") -> None:
    with st.expander("Advanced: download machine-readable data", expanded=False):
        st.download_button(
            label,
            data=json.dumps(data, indent=2, ensure_ascii=False),
            file_name=filename,
            mime="application/json",
        )


def bar_from_counter_items(items: list[tuple], title: str):
    if not items:
        return None
    # Prefer motif labels over raw IDs when possible
    from vision.glyph_render import motif_name

    labels = []
    for i in items:
        sid = str(i[0])
        labels.append(motif_name(sid) if sid.startswith("IVS") or sid.startswith("EGY") or sid.startswith("SUM") or sid.startswith("AKK") else sid)
    values = [i[1] for i in items]
    if HAS_PLOTLY:
        fig = px.bar(
            x=labels,
            y=values,
            title=title,
            labels={"x": "symbol motif", "y": "count"},
            color_discrete_sequence=[IVC["terracotta"]],
        )
        fig.update_layout(xaxis_tickangle=-35)
        return plotly_ivc_layout(fig)
    return pd.DataFrame({"symbol": labels, "count": values}).set_index("symbol")


def render_chart(fig_or_df, *, use_container_width: bool = True) -> None:
    if fig_or_df is None:
        st.write("No chart data.")
        return
    if HAS_PLOTLY and not isinstance(fig_or_df, pd.DataFrame):
        st.plotly_chart(plotly_ivc_layout(fig_or_df), use_container_width=use_container_width)
    elif isinstance(fig_or_df, pd.DataFrame):
        st.bar_chart(fig_or_df)
    else:
        st.write(fig_or_df)


def js_plain_table(js_map: dict) -> None:
    """Render JS divergence as a readable table, not JSON."""
    if not js_map:
        paper_note("No comparison available yet.")
        return
    rows = []
    for key, val in js_map.items():
        if isinstance(val, dict):
            score = val.get("js_divergence", val)
            note = val.get("note", "")
        else:
            score = val
            note = "Lower score means more similar frequency structure (not shared meaning)."
        label = key.replace("__vs__", " vs ").replace("_", " ")
        rows.append(
            {
                "Comparison": label,
                "Structural difference score": round(float(score), 4) if score is not None else None,
                "How to read it": note
                or "Lower = closer sign-frequency shape. This is not a translation score.",
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def boundary_plain_table(items: list[dict], title: str = "Boundary-leaning symbols") -> None:
    from vision.glyph_render import ensure_glyphs, motif_name

    if not items:
        paper_note("No boundary pattern found.")
        return
    st.markdown(f"**{title}**")
    cols = st.columns(min(len(items), 5))
    for i, item in enumerate(items[:5]):
        sign = item.get("sign", "")
        with cols[i % len(cols)]:
            if sign:
                st.image(ensure_glyphs([sign], size=100)[sign], use_container_width=True)
                st.caption(
                    f"{motif_name(sign)}-like · "
                    f"start {item.get('beginning', 0)} · "
                    f"end {item.get('ending', 0)}"
                )
