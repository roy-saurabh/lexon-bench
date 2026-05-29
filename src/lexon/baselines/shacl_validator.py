"""
SHACL baseline validator — STUB.

Optional semantic-web comparator. Requires rdflib extra.
See docs/shacl_baseline.md.

This baseline does not implement stratified activation semantics,
exception firing, three-valued applicability, or LEXON derivation traces.
"""

from __future__ import annotations


def validate(profile_graph_path: str, shapes_path: str) -> dict:
    """Validate a system profile graph against SHACL shapes. Requires rdflib."""
    try:
        from rdflib import Graph
        from pyshacl import validate as shacl_validate  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "SHACL baseline requires rdflib and pyshacl: pip install -e '.[rdf]'"
        ) from exc

    data_graph = Graph()
    data_graph.parse(profile_graph_path)

    shapes_graph = Graph()
    shapes_graph.parse(shapes_path)

    conforms, _, results_text = shacl_validate(data_graph, shacl_graph=shapes_graph)
    return {"conforms": conforms, "results": results_text}
