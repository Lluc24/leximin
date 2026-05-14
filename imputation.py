"""Core-imputation representation and LP-based initialization routine."""

from fractions import Fraction
import logging
from pulp import LpMaximize, LpProblem, LpStatus, LpVariable, lpSum, value
from dataclasses import dataclass, field
from graph import BipartiteGraph
from matching import MaxWeightMatching

LOGGER = logging.getLogger(__name__)


@dataclass
class Imputation:
    """Mutable mapping from vertex id to rational profit."""

    profits: dict[int, Fraction] = field(default_factory=dict)

    def slack(self, graph: BipartiteGraph, u: int, v: int) -> Fraction:
        """Return edge slack `p(u) + p(v) - w(u, v)`."""
        return self.profits[u] + self.profits[v] - graph.weights[u, v]

    def is_tight(self, graph: BipartiteGraph, u: int, v: int) -> bool:
        """Return True when edge `(u, v)` is tight under current profits."""
        return self.slack(graph, u, v) == Fraction(0)

    def apply_rotation(self, increasing: frozenset[int], decreasing: frozenset[int], delta: Fraction) -> None:
        """Apply one rotation step by adding/subtracting `delta` on two vertex sets."""
        for v in increasing:
            self.profits[v] += delta
        for v in decreasing:
            self.profits[v] -= delta


def compute_imputation(graph: BipartiteGraph, mwm: MaxWeightMatching) -> Imputation:
    """Solve the dual LP to obtain one core imputation consistent with `mwm`."""
    LOGGER.info(
        "Computing initial imputation from LP (|V|=%d, |E|=%d, |M|=%d)",
        len(graph.vertices),
        len(graph.edges),
        len(mwm.matching),
    )
    prob = LpProblem("Imputation", LpMaximize)
    profits = {v: LpVariable(f"profit_{v}", lowBound=0) for v in graph.vertices}
    prob += lpSum(profits[v] for v in graph.vertices)

    for u, v in graph.edges:
        prob += (profits[u] + profits[v] >= graph.weights[u, v], f"Edge_{u}_{v}")

    for u, v in mwm.matching:
        # Tightness on matched edges pins down one optimal dual point.
        prob += (profits[u] + profits[v] == graph.weights[u, v], f"MatchingEdge_{u}_{v}")

    prob.solve()
    status = LpStatus.get(prob.status, f"status={prob.status}")
    LOGGER.debug("LP solved with status: %s", status)

    imputation = Imputation({
        v: Fraction(str(value(profits[v]))).limit_denominator(10_000)
        for v in graph.vertices
    })
    LOGGER.info("Initial imputation ready: %s", imputation)
    return imputation
