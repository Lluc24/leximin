"""Maximum-weight matching wrapper utilities."""

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
import networkx as nx
from networkx.algorithms import max_weight_matching as mwm

from utils import s


@dataclass(frozen=True)
class MaxWeightMatching:
    """Weight and edge set of a bipartite maximum-weight matching."""

    weight: Fraction
    matching: frozenset[tuple[int, int]]


def max_weight_matching(weights: dict[tuple[int, int], Fraction]) -> MaxWeightMatching:
    """Return a maximum-weight matching in `(u, v)` orientation."""
    u_vertices = frozenset(u for u, v in weights)
    v_vertices = frozenset(v for u, v in weights)
    bip = nx.Graph()
    bip.add_nodes_from(u_vertices, bipartite=0)
    bip.add_nodes_from(v_vertices, bipartite=1)
    for e in product(u_vertices, v_vertices):
        bip.add_edge(*e, weight=weights[e] if e in weights else Fraction(0))
    matching = mwm(bip)
    matching = frozenset(sorted([s(u, v) for u, v in matching]))
    weight = sum((weights[e] for e in matching), Fraction(0))
    return MaxWeightMatching(weight=weight, matching=matching)
