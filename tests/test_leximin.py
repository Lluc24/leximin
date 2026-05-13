"""End-to-end tests for the leximin solver."""

import logging

from components import FundamentalComponent
from graph import BipartiteGraph
from imputation import Imputation
from leximin import LeximinSolver
from tests.graphs import (
    TestBipartiteGraph,
    VIJAY_EXAMPLE_1_GRAPH,
    VIJAY_EXAMPLE_3_GRAPH,
    VIJAY_EXAMPLE_5_GRAPH,
    HANDMADE_GRAPH
)
from tests.imputation_tests.test_imputation import verify_is_in_core

LOGGER = logging.getLogger("tests.leximin")

TEST_GRAPHS: tuple[TestBipartiteGraph, ...] = (
    VIJAY_EXAMPLE_1_GRAPH,
    VIJAY_EXAMPLE_3_GRAPH,
    VIJAY_EXAMPLE_5_GRAPH,
    HANDMADE_GRAPH
)

def test_returns_expected_leximin_core_imputation() -> None:
    for graph in TEST_GRAPHS:
        solver = LeximinSolver(graph)
        imp = solver.solve()
        expected = Imputation(graph.leximin_imp)
        LOGGER.info("Graph %s: computed imputation %s", graph.name, imp)
        LOGGER.info("Graph %s: expected imputation %s", graph.name, expected)
        assert imp == expected
        verify_feasibility(graph, imp)

def verify_feasibility(graph: BipartiteGraph, imp: Imputation) -> None:
    """Validate non-negativity, dual feasibility, and core membership."""
    for u in graph.vertices:
        assert imp.profit(u) >= 0, f"Vertex {u} has negative profit: {imp.profit(u)}"
    for u, v in graph.edges:
        assert imp.slack(graph, u, v) >= 0, f"Edge ({u}, {v}) is not dual feasible: slack={imp.slack(graph, u, v)}"
    verify_is_in_core(graph, imp)
