"""Maximum-weight matching wrapper utilities.

Wraps NetworkX's ``max_weight_matching`` so the rest of the codebase works
with a typed result object and ``Fraction`` weights instead of floats.
"""

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
import networkx as nx
from networkx.algorithms import max_weight_matching as mwm

from utils import s


@dataclass(frozen=True)
class MaxWeightMatching:
    """Weight and edge set of a bipartite maximum-weight matching.

    Attributes
    ----------
    weight:
        Total weight of the matching as an exact ``Fraction``.
    matching:
        Frozenset of edges ``(u, v)`` with ``u < v`` that form the matching.
    """

    weight: Fraction
    matching: frozenset[tuple[int, int]]


def max_weight_matching(weights: dict[tuple[int, int], Fraction]) -> MaxWeightMatching:
    """Return a maximum-weight matching for the given weighted bipartite graph.

    Parameters
    ----------
    weights:
        Edge-weight dictionary ``{(u, v): Fraction}`` in canonical orientation
        (``u < v``).

    Returns
    -------
    MaxWeightMatching
        The matching with all edges in ``(u, v)`` orientation (``u < v``) and
        the total weight as an exact ``Fraction``.

    Notes
    -----
    NetworkX's ``max_weight_matching`` operates on general graphs.  To ensure
    it respects the bipartite structure and does not accidentally match two
    U-side or two V-side vertices together, this function adds every missing
    cross-side pair with weight 0.  Edges with zero weight are excluded from
    the returned matching set.
    """
    u_vertices = frozenset(u for u, v in weights)
    v_vertices = frozenset(v for u, v in weights)
    bip = nx.Graph()
    bip.add_nodes_from(u_vertices, bipartite=0)
    bip.add_nodes_from(v_vertices, bipartite=1)
    # Fill in zero-weight cross edges so NX sees a complete bipartite graph;
    # this prevents it from matching same-side vertices when the input is sparse.
    for e in product(u_vertices, v_vertices):
        bip.add_edge(*e, weight=weights[e] if e in weights else Fraction(0))
    matching = mwm(bip)
    # Keep only edges that belong to the original weight dict (positive weight).
    matching = frozenset(sorted([s(u, v) for u, v in matching if s(u, v) in weights]))
    weight = sum((weights[e] for e in matching), Fraction(0))
    return MaxWeightMatching(weight=weight, matching=matching)
