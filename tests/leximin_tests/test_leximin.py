"""End-to-end tests for the leximin solver."""

import logging
from graph import BipartiteGraph
from imputation import Imputation
from leximin import LeximinSolver
from tests.leximin_tests.cases_leximin import LEXIMIN_CASES
from tests.imputation_tests.test_imputation import verify_is_in_core

LOGGER = logging.getLogger("tests.leximin")

def test_returns_expected_leximin_core_imputation() -> None:
    for case in LEXIMIN_CASES:
        LOGGER.info("Case %s: using initial imputation %s", case.name, case.initial_imputation)
        solver = LeximinSolver(case.graph, case.initial_imputation)
        imp = solver.solve()
        LOGGER.info("Case %s: computed imputation %s", case.name, imp)
        LOGGER.info("Case %s: expected imputation %s", case.name, Imputation(case.expected))
        assert imp == Imputation(case.expected)
        verify_feasibility(case.graph, imp)

def verify_feasibility(graph: BipartiteGraph, imp: Imputation) -> None:
    """Validate non-negativity, dual feasibility, and core membership."""
    for u in graph.vertices:
        assert imp.profit(u) >= 0, f"Vertex {u} has negative profit: {imp.profit(u)}"
    for u, v in graph.edges:
        assert imp.slack(graph, u, v) >= 0, f"Edge ({u}, {v}) is not dual feasible: slack={imp.slack(graph, u, v)}"
    verify_is_in_core(graph, imp)
