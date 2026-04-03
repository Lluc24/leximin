from fractions import Fraction
from graph import BipartiteGraph
from classification import Classification
from matching import MaxWeightMatching
from pulp import *


class Imputation:
    def __init__(self, profits: dict[int, Fraction]):
        self._profits = dict(profits)

    def profit(self, vertex: int) -> Fraction:
        return self._profits[vertex]

    def set_profit(self, vertex: int, value: Fraction) -> None:
        self._profits[vertex] = value

    def slack(self, graph: BipartiteGraph, u: int, v: int) -> Fraction:
        return self._profits[u] + self._profits[v] - graph.weight(u, v)

    def is_tight(self, graph: BipartiteGraph, u: int, v: int) -> bool:
        return self.slack(graph, u, v) == Fraction(0)

    def apply_rotation(self, increasing: frozenset[int], decreasing: frozenset[int], delta: Fraction) -> None:
        for v in increasing:
            self._profits[v] += delta
        for v in decreasing:
            self._profits[v] -= delta

    def copy(self) -> 'Imputation':
        return Imputation(dict(self._profits))

    def sorted_essential_profits(self, clf: Classification) -> list[Fraction]:
        return sorted(self._profits[v] for v in clf.essential_vertices)


def compute_imputation(graph: BipartiteGraph, mwm: MaxWeightMatching) -> Imputation:
    prob = LpProblem("Imputation", LpMaximize)
    profits = {v: LpVariable(f"profit_{v}", lowBound=0) for v in graph.vertices}
    prob += lpSum(profits[v] for v in graph.vertices)

    for u, v in graph.edges:
        prob += (profits[u] + profits[v] >= graph.weight(u, v), f"Edge_{u}_{v}")

    for u, v in mwm.matching:
        prob += (profits[u] + profits[v] == graph.weight(u, v), f"MatchingEdge_{u}_{v}")

    prob.solve()

    imputation = Imputation({v: value(profits[v]) for v in graph.vertices})
    return imputation