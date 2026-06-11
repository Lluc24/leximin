"""Core-imputation representation and LP-based initialisation routine.

An *imputation* for the assignment game is a profit vector ``p : V → Q≥0``
that is efficient (``Σ p(v) = W_max``) and in the core (``p(u) + p(v) ≥ w(u,v)``
for every edge, with equality on every matched edge).

This module provides:
- ``Imputation`` — a mutable container for the profit vector, with helpers
  for computing edge slack and applying rotation updates.
- ``compute_imputation`` — solves the dual LP to obtain the U-optimal core
  imputation (maximizes ``Σ_{u∈U} p(u)``), which is used as the starting
  point for the leximin event loop.

The U-optimal starting point is convenient but not required for correctness;
any core imputation that is tight on all matched edges would work.
"""

from fractions import Fraction
import logging
from pulp import LpMaximize, LpProblem, LpStatus, LpVariable, lpSum, value
from dataclasses import dataclass, field
from graph import BipartiteGraph
from matching import MaxWeightMatching

LOGGER = logging.getLogger(__name__)


@dataclass
class Imputation:
    """Mutable mapping from vertex id to rational profit.

    The ``profits`` dict is updated in-place by ``apply_rotation`` during the
    event loop, so all component references to this object see the current
    values without copying.

    Attributes
    ----------
    profits:
        Dictionary ``{vertex_id: Fraction}`` covering every vertex in the graph
        (including subpar vertices, which receive ``Fraction(0)``).
    """

    profits: dict[int, Fraction] = field(default_factory=dict)

    def slack(self, graph: BipartiteGraph, u: int, v: int) -> Fraction:
        """Return the dual slack ``p(u) + p(v) - w(u, v)`` for edge ``(u, v)``.

        A slack of zero means the edge is *tight* (binding in the dual LP).
        Tight subpar edges are *legitimate* and drive the event loop.
        """
        return self.profits[u] + self.profits[v] - graph.weights[u, v]

    def is_tight(self, graph: BipartiteGraph, u: int, v: int) -> bool:
        """Return True when edge ``(u, v)`` is tight under current profits."""
        return self.slack(graph, u, v) == Fraction(0)

    def apply_rotation(self, increasing: frozenset[int], decreasing: frozenset[int], delta: Fraction) -> None:
        """Apply a dual rotation by shifting two disjoint vertex sets by ``±delta``.

        CW rotation: left vertices increase, right vertices decrease.
        CCW rotation: right vertices increase, left vertices decrease.
        Essential edges within the component remain tight after the rotation
        because both their endpoints move by the same absolute amount.
        """
        for v in increasing:
            self.profits[v] += delta
        for v in decreasing:
            self.profits[v] -= delta


def compute_imputation(graph: BipartiteGraph, mwm: MaxWeightMatching) -> Imputation:
    """Solve the dual LP to obtain a core imputation consistent with ``mwm``.

    The LP maximises ``Σ_{u∈U} p(u)`` subject to:
    - Efficiency: ``Σ_v p(v) = W_max``
    - Non-negativity: ``p(v) ≥ 0`` for all ``v``
    - Dual feasibility: ``p(u) + p(v) ≥ w(u,v)`` for every edge
    - Tightness on matched edges: ``p(u) + p(v) = w(u,v)`` for ``(u,v) ∈ M``

    This gives the U-optimal extreme core imputation, which concentrates as
    much profit as possible on the U side.  Any core imputation that is tight
    on all matched edges would serve as a valid starting point.

    Parameters
    ----------
    graph:
        The input bipartite graph.
    mwm:
        A maximum-weight matching; its edges are forced tight in the LP.

    Returns
    -------
    Imputation
        The U-optimal core imputation with profits as ``Fraction`` values
        obtained by rationalising the LP solution to a denominator ≤ 10 000.
    """
    LOGGER.info(
        "Computing initial imputation from LP (|V|=%d, |E|=%d, |M|=%d)",
        len(graph.vertices),
        len(graph.edges),
        len(mwm.matching),
    )
    prob = LpProblem("Imputation", LpMaximize)
    profits = {v: LpVariable(f"profit_{v}", lowBound=0) for v in graph.vertices}
    prob += lpSum(profits[v] for v in graph.u_vertices)

    prob += (lpSum(profits[v] for v in graph.vertices) == mwm.weight, "Efficiency")

    for u, v in graph.edges:
        prob += (profits[u] + profits[v] >= graph.weights[u, v], f"Edge_{u}_{v}")

    for u, v in mwm.matching:
        # Tightness on matched edges pins down one optimal dual point.
        prob += (profits[u] + profits[v] == graph.weights[u, v], f"MatchingEdge_{u}_{v}")

    prob.solve()
    status = LpStatus.get(prob.status, f"status={prob.status}")
    LOGGER.debug("LP solved with status: %s", status)

    # PuLP returns float values; rationalise to avoid drift in the event loop.
    imputation = Imputation({
        v: Fraction(str(value(profits[v]))).limit_denominator(10_000)
        for v in graph.vertices
    })
    LOGGER.info("Initial imputation ready: %s", imputation)
    return imputation
