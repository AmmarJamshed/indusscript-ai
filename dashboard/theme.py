"""IVC parchment theme for the Streamlit dashboard."""

from __future__ import annotations

import streamlit as st

# Indus Valley palette — terracotta, sandstone, indigo seal-ink, clay
IVC = {
    "sand": "#F3E6D4",
    "paper": "#FFF8EE",
    "paper_edge": "#E8D5B7",
    "terracotta": "#B85C38",
    "clay": "#8C4A2F",
    "charcoal": "#2C241B",
    "ink": "#3D2B1F",
    "seal_blue": "#1F4E5F",
    "ochre": "#C4893B",
    "muted": "#7A6A58",
    "success": "#5B6B3A",
    "warning_bg": "#F5E0C8",
    "danger_bg": "#F0D0C4",
    "info_bg": "#E5EFEA",
}

IVC_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,700;1,500&family=Source+Sans+3:wght@400;600&display=swap');

html, body, [class*="css"] {{
  font-family: 'Source Sans 3', 'Segoe UI', sans-serif;
  color: {IVC["ink"]};
}}

/* App background — warm clay wash */
.stApp {{
  background:
    radial-gradient(ellipse at top, #F7EBDA 0%, {IVC["sand"]} 55%, #E5D2B8 100%);
}}

/* Main sheet = simulated white / ivory paper */
.block-container {{
  background: {IVC["paper"]};
  background-image:
    linear-gradient(180deg, rgba(255,255,255,0.55) 0%, rgba(255,248,238,0.2) 40%, rgba(232,213,183,0.25) 100%);
  border: 1px solid {IVC["paper_edge"]};
  border-radius: 4px;
  box-shadow:
    0 1px 0 rgba(255,255,255,0.7) inset,
    0 12px 40px rgba(44, 36, 27, 0.12),
    0 0 0 8px rgba(184, 92, 56, 0.06);
  padding-top: 2rem !important;
  padding-bottom: 3rem !important;
  max-width: 1100px;
}}

h1, h2, h3, h4 {{
  font-family: 'Cormorant Garamond', Georgia, serif !important;
  color: {IVC["charcoal"]} !important;
  letter-spacing: 0.02em;
  border-bottom: 1px solid {IVC["paper_edge"]};
  padding-bottom: 0.25rem;
}}

h1 {{
  color: {IVC["terracotta"]} !important;
  border-bottom: 2px solid {IVC["terracotta"]};
}}

/* Sidebar — dark seal stone */
section[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, #3A2F26 0%, #2C241B 100%) !important;
  border-right: 3px solid {IVC["terracotta"]};
}}
section[data-testid="stSidebar"] * {{
  color: #F3E6D4 !important;
}}
section[data-testid="stSidebar"] .stRadio label {{
  font-size: 0.92rem;
}}
section[data-testid="stSidebar"] [data-baseweb="radio"] > div {{
  background: transparent !important;
}}

/* Soft paper cards / alerts */
div[data-testid="stAlert"] {{
  background: {IVC["info_bg"]} !important;
  border-left: 4px solid {IVC["seal_blue"]} !important;
  color: {IVC["ink"]} !important;
  border-radius: 2px;
}}

/* Metrics as clay tiles */
div[data-testid="stMetric"] {{
  background: #FFFDF8;
  border: 1px solid {IVC["paper_edge"]};
  border-top: 3px solid {IVC["terracotta"]};
  padding: 0.75rem 1rem;
  border-radius: 2px;
}}
div[data-testid="stMetric"] label {{
  color: {IVC["muted"]} !important;
}}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
  color: {IVC["clay"]} !important;
  font-family: 'Cormorant Garamond', Georgia, serif;
}}

/* Tables — manuscript lines */
div[data-testid="stDataFrame"] {{
  border: 1px solid {IVC["paper_edge"]};
  background: #FFFcf7;
}}

/* Buttons — terracotta seals */
.stButton > button {{
  background: {IVC["terracotta"]} !important;
  color: #FFF8EE !important;
  border: none !important;
  border-radius: 2px !important;
  font-weight: 600;
  letter-spacing: 0.03em;
  box-shadow: 0 2px 0 {IVC["clay"]};
}}
.stButton > button:hover {{
  background: {IVC["clay"]} !important;
  color: #fff !important;
}}

/* Hide default Streamlit chrome noise */
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
header {{ visibility: hidden; }}

/* Paper note callouts */
.ivc-paper-note {{
  background: #FFFDF8;
  border: 1px solid {IVC["paper_edge"]};
  border-left: 5px solid {IVC["ochre"]};
  padding: 1rem 1.25rem;
  margin: 0.75rem 0 1.25rem 0;
  font-size: 1.05rem;
  line-height: 1.55;
  color: {IVC["ink"]};
}}
.ivc-speculative {{
  background: {IVC["warning_bg"]};
  border: 1px solid {IVC["ochre"]};
  border-left: 5px solid {IVC["terracotta"]};
  padding: 0.9rem 1.2rem;
  margin: 0.5rem 0 1rem 0;
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 1.2rem;
  color: {IVC["charcoal"]};
}}
.ivc-section-rule {{
  height: 1px;
  background: linear-gradient(90deg, transparent, {IVC["terracotta"]}, transparent);
  margin: 1.5rem 0;
  border: none;
}}
.ivc-plain {{
  font-size: 1.05rem;
  line-height: 1.6;
  color: {IVC["ink"]};
}}
</style>
"""


def apply_ivc_theme() -> None:
    st.markdown(IVC_CSS, unsafe_allow_html=True)


def paper_note(text: str) -> None:
    st.markdown(f'<div class="ivc-paper-note">{text}</div>', unsafe_allow_html=True)


def speculative_banner(text: str) -> None:
    st.markdown(f'<div class="ivc-speculative">{text}</div>', unsafe_allow_html=True)


def section_rule() -> None:
    st.markdown('<hr class="ivc-section-rule" />', unsafe_allow_html=True)


def plotly_ivc_layout(fig):
    """Apply IVC colours to a Plotly figure when available."""
    if fig is None:
        return None
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFDF8",
        font=dict(color=IVC["ink"], family="Source Sans 3"),
        title_font=dict(family="Cormorant Garamond", color=IVC["charcoal"]),
        colorway=[IVC["terracotta"], IVC["seal_blue"], IVC["ochre"], IVC["clay"], IVC["success"]],
    )
    fig.update_xaxes(gridcolor=IVC["paper_edge"])
    fig.update_yaxes(gridcolor=IVC["paper_edge"])
    return fig
