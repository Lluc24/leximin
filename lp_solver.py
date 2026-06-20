"""LP-based reference solver for the leximin core imputation.

This module implements the iterative saturation approach to computing the
leximin core imputation using a general-purpose LP solver (PuLP/CBC).  It
serves as an *independent reference* for validating the output of the
combinatorial ``LeximinSolver`` in ``leximin.py``.

Algorithm outline
-----------------
Each round solves an LP that maximizes a common lower bound ``λ`` subject to:
- all standard dual feasibility constraints (core membership),
- equality constraints fixing the profits of already-saturated vertices, and
- a lower bound ``p(v) ≥ λ`` for every unsaturated vertex.

After solving, any vertex whose profit equals ``λ`` *and* cannot be raised
above ``λ`` without violating core membership is declared saturated at ``λ``
and fixed for all future rounds.  The algorithm continues until every vertex
is saturated.

Because this solver makes no use of the combinatorial structure of the
problem, it runs in pseudo-polynomial time and is only practical for the
small instances used in the test suite.
"""

import logging
from fractions import Fraction

from pulp import LpProblem, LpVariable, LpMaximize, lpSum, value
from graph import BipartiteGraph
from imputation import Imputation
from matching import max_weight_matching

LOGGER = logging.getLogger(__name__)
_DENOMINATOR_LIMIT = 10**6
_FLOAT_TOL = 1e-6


def _to_frac(val: float) -> Fraction:
    """Convert a PuLP float result to a Fraction, clamping the denominator."""
    return Fraction(val).limit_denominator(_DENOMINATOR_LIMIT)


class LeximinLPSolver:
    """Iterative LP solver that computes the leximin core imputation.

    This solver is intended as a correctness reference only.  For the efficient
    combinatorial implementation, see ``LeximinSolver`` in ``leximin.py``.

    Attributes
    ----------
    graph:
        The input bipartite graph.
    mwm:
        A fixed maximum-weight matching used to add tightness constraints.
    saturated:
        Vertices whose leximin profit has been determined (fixed across rounds).
    unfixed:
        Vertices still being optimized.
    profits:
        The LP solution from the most recent round.
    lambda_val:
        The maximum ``λ`` achieved in the most recent round.
    round_num:
        Current round counter (for logging).
    """

    def __init__(self, graph: BipartiteGraph):
        self.graph = graph
        self.mwm = max_weight_matching(graph.weights)
        self.saturated: dict[int, Fraction] = {}
        self.unfixed: frozenset[int] = frozenset(graph.vertices)
        self.profits = {v: Fraction(0) for v in graph.vertices}
        self.lambda_val = Fraction(0)
        self.round_num = 1

    def solve(self) -> Imputation:
        """Compute the leximin core imputation via iterative LP saturation.

        Returns
        -------
        Imputation
            The leximin core imputation.
        """
        LOGGER.info(f"Leximin LP solver starting  |V|={len(self.graph.vertices)}  |E|={len(self.graph.edges)}  W_max={self.mwm.weight}")
        while self.unfixed:
            self._solve_round()
            new_unfixed = self.unfixed.copy()
            for v in self.unfixed:
                at_lambda = abs(float(self.profits[v]) - float(self.lambda_val)) <= _FLOAT_TOL
                if at_lambda and self._is_saturated(v):
                    self.saturated[v] = self.lambda_val
                    new_unfixed = new_unfixed - frozenset({v})
            self.unfixed = new_unfixed
            LOGGER.info(f"Round {self.round_num}  alpha={self.lambda_val}  unfixed={sorted(self.unfixed)}  newly_saturated={sorted(self.saturated.keys())}")
            self.round_num += 1
        return Imputation(self.saturated)

    def _solve_round(self) -> None:
        """Solve one round: maximise λ subject to dual constraints and current fixings."""
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
        """Return True if vertex ``v`` cannot exceed ``lambda_val`` in any core imputation.

        A separate LP maximizes ``p(v)`` subject to the same dual constraints
        and all current fixings.  If the optimal value is still ``≤ lambda_val``,
        the vertex is saturated and can be fixed for all future rounds.
        """
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
        return float(max_v) <= float(self.lambda_val) + _FLOAT_TOL

    def _add_dual_constraints(self, prob: LpProblem, p: dict[int, LpVariable]) -> None:
        """Add efficiency, matched-edge tightness, and dual-feasibility constraints."""
        prob += (lpSum(p[v] for v in self.graph.vertices) == float(self.mwm.weight), "Efficiency")
        for u, v in self.graph.edges:
            if (u, v) in self.mwm.matching:
                prob += (p[u] + p[v] == float(self.graph.weights[u, v]), f"Tight_{u}_{v}")
            else:
                prob += (p[u] + p[v] >= float(self.graph.weights[u, v]), f"DF_{u}_{v}")