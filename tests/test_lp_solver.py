"""End-to-end tests for the leximin LP solver."""

import logging

from lp_solver import LeximinLPSolver
from tests.fixtues import ALL_GRAPHS
from tests.test_leximin import verify_feasibility

LOGGER = logging.getLogger("tests.lp_solver")
TOLERANCE = 1e-6


def test_returns_expected_leximin_imputation() -> None:
    for graph in ALL_GRAPHS:
        LOGGER.info("Starting graph case: %s", graph.name)
        solver = LeximinLPSolver(graph)
        actual_imp = solver.solve()
        LOGGER.info("Graph %s: computed imputation %s", graph.name, actual_imp)
        LOGGER.info("Graph %s: expected imputation %s", graph.name, graph.leximin_imp)
        assert all(abs(actual_imp.profits[v] - graph.leximin_imp.profits[v]) <= TOLERANCE for v in graph.vertices), f"Leximin imputation does not match expected for graph {graph.name}"
        verify_feasibility(graph, actual_imp)
