"""Classification of vertices and edges for the assignment-game algorithm."""

from dataclasses import dataclass, field

from graph import BipartiteGraph
from matching import max_weight_matching

@dataclass(frozen=True)
class Classification:
    """Partition of graph elements into essential, viable, and subpar sets."""

    essential_u: frozenset[int] = field(default_factory=frozenset)
    essential_v: frozenset[int] = field(default_factory=frozenset)
    viable_u: frozenset[int] = field(default_factory=frozenset)
    viable_v: frozenset[int] = field(default_factory=frozenset)
    subpar_u: frozenset[int] = field(default_factory=frozenset)
    subpar_v: frozenset[int] = field(default_factory=frozenset)

    essential_edges: frozenset[tuple[int, int]] = field(default_factory=frozenset)
    viable_edges: frozenset[tuple[int, int]] = field(default_factory=frozenset)
    subpar_edges: frozenset[tuple[int, int]] = field(default_factory=frozenset)


def classify(graph: BipartiteGraph) -> Classification:
    """Compute edge/vertex classes from matching-sensitivity tests."""
    matching = max_weight_matching(graph.weights)

    essential_edges = frozenset()
    for edge in graph.edges:
        tmp_graph = graph - edge
        tmp_matching = max_weight_matching(tmp_graph.weights)
        if tmp_matching.weight < matching.weight:
            essential_edges |= {edge}

    subpar_edges = graph.edges - essential_edges
    viable_edges = frozenset()
    for u, v in subpar_edges.copy():
        tmp_graph = graph - u - v
        tmp_matching = max_weight_matching(tmp_graph.weights)
        if tmp_matching.weight == matching.weight - graph.weights[u, v]:
            viable_edges |= {(u, v)}
            subpar_edges -= {(u, v)}

    def classify_vertices(u_vertices: bool) -> tuple[frozenset[int], frozenset[int], frozenset[int]]:
        """Classify either the U side or the V side against the computed edge sets."""
        vertices_set = graph.u_vertices if u_vertices else graph.v_vertices
        essential = frozenset()
        for vtx in vertices_set:
            tmp_g = graph - vtx
            tmp_mwm = max_weight_matching(tmp_g.weights)
            if tmp_mwm.weight < matching.weight:
                essential |= {vtx}
        viable = frozenset(u_ if u_vertices else v_ for u_, v_ in viable_edges) - essential
        subpar = vertices_set - essential - viable
        return essential, viable, subpar

    essential_u, viable_u, subpar_u = classify_vertices(u_vertices=True)
    essential_v, viable_v, subpar_v = classify_vertices(u_vertices=False)

    return Classification(
        essential_u=essential_u,
        essential_v=essential_v,
        viable_u=viable_u,
        viable_v=viable_v,
        subpar_u=subpar_u,
        subpar_v=subpar_v,
        essential_edges=essential_edges,
        viable_edges=viable_edges,
        subpar_edges=subpar_edges
    )
