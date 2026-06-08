import logging
from fractions import Fraction

from pulp import LpProblem, LpVariable, LpMaximize, lpSum, value
from graph import BipartiteGraph
from imputation import Imputation
from matching import max_weight_matching

LOGGER = logging.getLogger(__name__)
_DENOMINATOR_LIMIT = 10**6

def _to_frac(val: float) -> Fraction:
    """Convert a float to a Fraction, handling small numerical errors."""
    return Fraction(val).limit_denominator(_DENOMINATOR_LIMIT)

class LeximinLPSolver:
    def __init__(self, graph: BipartiteGraph):
        self.graph = graph
        self.mwm = max_weight_matching(graph.weights)
        self.saturated: dict[int, Fraction] = {}   # vertex -> known leximin profit
        self.unfixed: frozenset[int] = frozenset(graph.vertices)
        self.profits = {v: Fraction(0) for v in graph.vertices}  # current LP solution
        self.lambda_val = Fraction(0)  # current round's minimum profit
        self.round_num = 1

    def solve(self) -> Imputation:
        """Compute the leximin core imputation."""
        LOGGER.info(f"Leximin LP solver starting  |V|={len(self.graph.vertices)}  |E|={len(self.graph.edges)}  W_max={self.mwm.weight}")
        while self.unfixed:
            self._solve_round()
            new_unfixed = self.unfixed.copy()
            for v in self.unfixed:
                if self.profits[v] == self.lambda_val and self._is_saturated(v):
                    self.saturated[v] = self.lambda_val
                    new_unfixed = new_unfixed - frozenset({v})
            self.unfixed = new_unfixed
            LOGGER.info(f"Round {self.round_num}  alpha={self.lambda_val}  unfixed={sorted(self.unfixed)}  newly_saturated={sorted(self.saturated.keys())}")
            self.round_num += 1
        return Imputation(self.saturated)

    def _solve_round(self) -> None:
        """Perform one round of the iterative saturation algorithm."""
        prob = LpProblem(f"Leximin_round{self.round_num}", LpMaximize)
        p = {v: LpVariable(f"p{v}", lowBound=0) for v in self.graph.vertices}
        lambda_ = LpVariable("lambda_", lowBound=0)
        prob += lambda_
        self._add_dual_constraints(prob, p)
        for v, val in self.saturated.items():
            prob += (p[v] == float(val), f"Sat_{v}")
        for v in self.unfixed:
            prob += (p[v] >= lambda_, f"LB_{v}")
        prob.solve()

        self.lambda_val = _to_frac(value(lambda_))
        self.profits = {v: _to_frac(value(p[v])) for v in self.graph.vertices}

    def _is_saturated(self, v: int) -> bool:
        """Check if vertex v is saturated at the current lambda."""
        prob = LpProblem(f"Sat_check_v{v}_round{self.round_num}", LpMaximize)
        p = {u: LpVariable(f"p{u}", lowBound=0) for u in self.graph.vertices}
        prob += p[v]
        self._add_dual_constraints(prob, p)
        for u, val in self.saturated.items():
            prob += (p[u] == float(val), f"Sat_{u}")
        for u in self.unfixed:
            prob += (p[u] >= float(self.lambda_val), f"LB_{u}")
        prob.solve()
        max_v = _to_frac(value(p[v]))
        return max_v <= self.lambda_val

    def _add_dual_constraints(self, prob: LpProblem, p: dict[int, LpVariable]) -> None:
        """Add efficiency, tightness on M*, and dual-feasibility to *prob*."""
        prob += (lpSum(p[v] for v in self.graph.vertices) == float(self.mwm.weight), "Efficiency")
        for u, v in self.graph.edges:
            if (u, v) in self.mwm.matching:
                prob += (p[u] + p[v] == float(self.graph.weights[u, v]), f"Tight_{u}_{v}")
            else:
                prob += (p[u] + p[v] >= float(self.graph.weights[u, v]), f"DF_{u}_{v}")