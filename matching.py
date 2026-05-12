from fractions import Fraction
from graph import BipartiteGraph
import networkx as nx
from networkx.algorithms import max_weight_matching as mwm
from itertools import product
from dataclasses import dataclass

@dataclass(frozen=True)
class MaxWeightMatching:
    weight: Fraction
    matching: frozenset[tuple[int, int]]


def max_weight_matching(graph: BipartiteGraph) -> MaxWeightMatching:
    """
    Returns the unique MWM as a frozenset of (u, v) pairs.
    Wraps NetworkX's max_weight_matching.
    Non-degenerate assumption: the MWM is unique.
    """
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