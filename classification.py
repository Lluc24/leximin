from dataclasses import dataclass, field
from graph import BipartiteGraph
from matching import max_weight_matching
from itertools import chain

@dataclass(frozen=True)
class Classification:
    essential_u: frozenset[int] = field(default_factory=frozenset)
    essential_v: frozenset[int] = field(default_factory=frozenset)
    viable_u: frozenset[int] = field(default_factory=frozenset)
    viable_v: frozenset[int] = field(default_factory=frozenset)
    subpar_u: frozenset[int] = field(default_factory=frozenset)
    subpar_v: frozenset[int] = field(default_factory=frozenset)

    essential_edges: frozenset[tuple[int, int]] = field(default_factory=frozenset)
    viable_edges: frozenset[tuple[int, int]] = field(default_factory=frozenset)
    subpar_edges: frozenset[tuple[int, int]] = field(default_factory=frozenset)

    @property
    def essential_vertices(self) -> frozenset[int]:
        return self.essential_u | self.essential_v


def classify(graph: BipartiteGraph) -> Classification:
    matching = max_weight_matching(graph)

    essential_edges = set()
    for edge in graph.edges:
        tmp_graph = graph - edge
        tmp_matching = max_weight_matching(tmp_graph)
        if tmp_matching.weight < matching.weight:
            essential_edges.add(edge)

    subpar_edges = graph.edges - essential_edges
    viable_edges = set()
    for u, v in subpar_edges.copy():
        tmp_graph = graph - u - v
        tmp_matching = max_weight_matching(tmp_graph)
        if tmp_matching.weight == matching.weight - graph.weight(u, v):
            viable_edges.add((u, v))
            subpar_edges.remove((u, v))

    essential = set()
    for vertex in graph.vertices:
        tmp_graph = graph - vertex
        tmp_matching = max_weight_matching(tmp_graph)
        if tmp_matching.weight < matching.weight:
            essential.add(vertex)
    essential_u = essential & graph.u_vertices
    essential_v = essential & graph.v_vertices

    viable = set(chain.from_iterable(viable_edges)) - essential_u - essential_v
    viable_u = viable & graph.u_vertices
    viable_v = viable & graph.v_vertices

    subpar_u = graph.u_vertices - essential_u - viable_u
    subpar_v = graph.v_vertices - essential_v - viable_v

    return Classification(
        essential_u=frozenset(essential_u),
        essential_v=frozenset(essential_v),
        viable_u=frozenset(viable_u),
        viable_v=frozenset(viable_v),
        subpar_u=frozenset(subpar_u),
        subpar_v=frozenset(subpar_v),
        essential_edges=frozenset(essential_edges),
        viable_edges=frozenset(viable_edges),
        subpar_edges=frozenset(subpar_edges)
    )