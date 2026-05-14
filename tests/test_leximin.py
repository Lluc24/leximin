"""End-to-end tests for the leximin solver."""

import logging

from graph import BipartiteGraph
from imputation import Imputation
from leximin import LeximinSolver
from tests.fixtures.graphs import ALL_GRAPHS, VAZIRANI_5

LOGGER = logging.getLogger("tests.leximin")

def test_leximin_on_vazirani_5() -> None:
    graph = VAZIRANI_5
    solver = LeximinSolver(graph)
    actual_imp = solver.solve()
    LOGGER.info("Graph %s: computed imputation %s", graph.name, actual_imp)
    LOGGER.info("Graph %s: expected imputation %s", graph.name, graph.leximin_imp)
    assert actual_imp == graph.leximin_imp, f"Leximin imputation does not match expected for graph {graph.name}"
    verify_feasibility(graph, actual_imp)

def test_returns_expected_leximin_imputation() -> None:
    for graph in ALL_GRAPHS:
        solver = LeximinSolver(graph)
        actual_imp = solver.solve()
        LOGGER.info("Graph %s: computed imputation %s", graph.name, actual_imp)
        LOGGER.info("Graph %s: expected imputation %s", graph.name, graph.leximin_imp)
        assert actual_imp == graph.leximin_imp, f"Leximin imputation does not match expected for graph {graph.name}"
        verify_feasibility(graph, actual_imp)


def verify_feasibility(graph: BipartiteGraph, imp: Imputation) -> None:
    """Validate non-negativity, dual feasibility, and core membership."""
    for u in graph.vertices:
        assert imp.profits[u] >= 0, f"Vertex {u} has negative profit: {imp.profits[u]}"
    for u, v in graph.edges:
        assert imp.slack(graph, u, v) >= 0, f"Edge ({u}, {v}) is not dual feasible: slack={imp.slack(graph, u, v)}"
    graph.is_imputation_in_core(imp.profits)
