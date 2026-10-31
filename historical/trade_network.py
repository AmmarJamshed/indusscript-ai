"""Bronze Age trade network graph (Indus / Meluhha / Dilmun / Magan / Mesopotamia)."""

from __future__ import annotations

import networkx as nx

from database.db import get_db
from historical.meluhha import search_meluhha

# Edges encode historically discussed contact corridors — not linguistic identity.
BASE_NODES = {
    "Indus_Valley": {"region": "South Asia", "notes": "Harappan urban sphere"},
    "Meluhha": {
        "region": "debated",
        "notes": "Mesopotamian exonym; often linked to Indus but not proven identical to IVC language",
    },
    "Dilmun": {"region": "Persian Gulf", "notes": "Bahrain / Eastern Arabia association"},
    "Magan": {"region": "Oman / SE Arabia", "notes": "Copper source in Mesopotamian texts"},
    "Mesopotamia": {"region": "Iraq / Syria", "notes": "Sumer / Akkad / Babylon"},
    "Ur": {"region": "Southern Mesopotamia", "parent": "Mesopotamia"},
    "Uruk": {"region": "Southern Mesopotamia", "parent": "Mesopotamia"},
    "Lagash": {"region": "Southern Mesopotamia", "parent": "Mesopotamia"},
}


BASE_EDGES = [
    ("Indus_Valley", "Meluhha", {"relation": "possible_identity_or_overlap", "confidence": 0.4}),
    ("Meluhha", "Dilmun", {"relation": "trade", "confidence": 0.6}),
    ("Dilmun", "Magan", {"relation": "trade", "confidence": 0.6}),
    ("Magan", "Mesopotamia", {"relation": "trade", "confidence": 0.7}),
    ("Dilmun", "Mesopotamia", {"relation": "trade", "confidence": 0.8}),
    ("Meluhha", "Mesopotamia", {"relation": "trade", "confidence": 0.7}),
    ("Indus_Valley", "Dilmun", {"relation": "maritime_trade", "confidence": 0.5}),
    ("Indus_Valley", "Magan", {"relation": "maritime_trade", "confidence": 0.5}),
    ("Ur", "Mesopotamia", {"relation": "part_of", "confidence": 1.0}),
    ("Uruk", "Mesopotamia", {"relation": "part_of", "confidence": 1.0}),
    ("Lagash", "Mesopotamia", {"relation": "part_of", "confidence": 1.0}),
]


def build_trade_graph(include_meluhha_evidence: bool = True) -> nx.Graph:
    g = nx.Graph()
    for node, attrs in BASE_NODES.items():
        g.add_node(node, **attrs)
    for a, b, attrs in BASE_EDGES:
        g.add_edge(a, b, **attrs)

    if include_meluhha_evidence:
        for ev in search_meluhha(get_db()):
            node_id = ev.evidence_id
            g.add_node(
                node_id,
                kind="evidence",
                period=ev.period,
                is_synthetic=ev.is_synthetic,
                citation=ev.source_citation,
            )
            g.add_edge("Meluhha", node_id, relation="attested_in", confidence=ev.confidence)
            if ev.historical_location:
                loc = ev.historical_location.split("(")[0].strip()
                if loc in g:
                    g.add_edge(node_id, loc, relation="findspot_or_archive", confidence=0.3)
    return g


def graph_summary(g: nx.Graph | None = None) -> dict:
    g = g or build_trade_graph()
    return {
        "research_question": "C",
        "n_nodes": g.number_of_nodes(),
        "n_edges": g.number_of_edges(),
        "nodes": [
            {"id": n, **g.nodes[n]} for n in g.nodes
        ],
        "edges": [
            {"source": u, "target": v, **g.edges[u, v]} for u, v in g.edges
        ],
        "caveat": (
            "Trade contact can transmit goods, names and intermediaries without "
            "implying that Indus inscriptions encode Sumerian, Akkadian or any "
            "specific language family."
        ),
    }


def to_plotly_elements(g: nx.Graph | None = None) -> dict:
    """Positions for Plotly visualisation."""
    g = g or build_trade_graph()
    pos = nx.spring_layout(g, seed=42, k=0.6)
    edge_x, edge_y = [], []
    for u, v in g.edges:
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
    node_x = [pos[n][0] for n in g.nodes]
    node_y = [pos[n][1] for n in g.nodes]
    node_text = [str(n) for n in g.nodes]
    return {
        "edge_x": edge_x,
        "edge_y": edge_y,
        "node_x": node_x,
        "node_y": node_y,
        "node_text": node_text,
    }
