"""Core-imputation representation and LP-based initialization routine."""

from fractions import Fraction
from pulp import LpMaximize, LpProblem, LpVariable, lpSum, value

from classification import Classification
from graph import BipartiteGraph
from matching import MaxWeightMatching


class Imputation:
    """Mutable mapping from vertex id to rational profit."""

    def __init__(self, profits: dict[int, Fraction]):
        """Create an imputation from vertex-profit pairs."""
        self._profits = dict(profits)

    def profit(self, vertex: int) -> Fraction:
        """Return the current profit of one vertex."""
        return self._profits[vertex]

    def set_profit(self, vertex: int, value: Fraction) -> None:
        """Overwrite one vertex profit."""
        self._profits[vertex] = value

    def slack(self, graph: BipartiteGraph, u: int, v: int) -> Fraction:
        """Return edge slack `p(u) + p(v) - w(u, v)`."""
        return self._profits[u] + self._profits[v] - graph.weight(u, v)

    def is_tight(self, graph: BipartiteGraph, u: int, v: int) -> bool:
        """Return True when edge `(u, v)` is tight under current profits."""
        return self.slack(graph, u, v) == Fraction(0)

    def apply_rotation(self, increasing: frozenset[int], decreasing: frozenset[int], delta: Fraction) -> None:
        """Apply one rotation step by adding/subtracting `delta` on two vertex sets."""
        for v in increasing:
            self._profits[v] += delta
        for v in decreasing:
            self._profits[v] -= delta

    def copy(self) -> 'Imputation':
        """Return an independent copy of this imputation."""
        return Imputation(dict(self._profits))

    def sorted_essential_profits(self, clf: Classification) -> list[Fraction]:
        """Return essential-vertex profits sorted increasingly."""
        return sorted(self._profits[v] for v in clf.essential_vertices)

    def __eq__(self, other):
        """Compare by exact profit map."""
        if not isinstance(other, Imputation):
            return NotImplemented
        return self._profits == other._profits

    def __repr__(self):
        """Return a debug-friendly representation."""
        return f"Imputation({self._profits})"


def compute_imputation(graph: BipartiteGraph, mwm: MaxWeightMatching) -> Imputation:
    """Solve the dual LP to obtain one core imputation consistent with `mwm`."""
    prob = LpProblem("Imputation", LpMaximize)
    profits = {v: LpVariable(f"profit_{v}", lowBound=0) for v in graph.vertices}
    prob += lpSum(profits[v] for v in graph.vertices)

    for u, v in graph.edges:
        prob += (profits[u] + profits[v] >= graph.weight(u, v), f"Edge_{u}_{v}")

    for u, v in mwm.matching:
        # Tightness on matched edges pins down one optimal dual point.
        prob += (profits[u] + profits[v] == graph.weight(u, v), f"MatchingEdge_{u}_{v}")

    prob.solve()

    imputation = Imputation({
        v: Fraction(str(value(profits[v]))).limit_denominator(10_000)
        for v in graph.vertices
    })
    return imputation
