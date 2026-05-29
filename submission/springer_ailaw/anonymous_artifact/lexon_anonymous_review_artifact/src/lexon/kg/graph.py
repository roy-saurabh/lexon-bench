"""Knowledge graph representation using networkx."""
from __future__ import annotations
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

def build_obligation_graph(clauses, profiles):
    """Build a networkx graph from clauses and profiles (optional feature)."""
    if not NETWORKX_AVAILABLE:
        raise ImportError("networkx is required: pip install networkx")
    G = nx.DiGraph()
    for clause in clauses:
        G.add_node(clause.clause_id, type="Clause")
        for obl in clause.obligations:
            G.add_node(obl.obligation_id, type="Obligation")
            G.add_edge(clause.clause_id, obl.obligation_id, rel="hasObligation")
    for profile in profiles:
        G.add_node(profile.system_id, type="SystemProfile")
    return G
