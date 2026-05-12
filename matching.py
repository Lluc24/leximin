"""Maximum-weight matching wrapper utilities."""

from dataclasses import dataclass
from fractions import Fraction
from itertools import product

import networkx as nx
from networkx.algorithms import max_weight_matching as mwm

from graph import BipartiteGraph

@dataclass(frozen=True)
class MaxWeightMatching:
    """Weight and edge set of a bipartite maximum-weight matching."""

    weight: Fraction
    matching: frozenset[tuple[int, int]]


def max_weight_matching(graph: BipartiteGraph) -> MaxWeightMatching:
    """Return a maximum-weight matching in `(u, v)` orientation."""
    bip = nx.Graph()
    bip.add_nodes_from(graph.u_vertices, bipartite=0)
    bip.add_nodes_from(graph.v_vertices, bipartite=1)
    for e in product(graph.u_vertices, graph.v_vertices):
        bip.add_edge(*e, weight=graph.weight(*e))
    matching = mwm(bip)
    matching = [(u, v) if u in graph.u_vertices else (v, u) for (u, v) in matching]
    matching = frozenset(sorted(matching))
    weight = sum((graph.weight(*e) for e in matching), Fraction(0))
    return MaxWeightMatching(weight=weight, matching=matching)
