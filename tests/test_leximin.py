from classification import Classification
from graph import BipartiteGraph
from imputation import Imputation
from leximin import LeximinSolver
from tests.cases_leximin import LEXIMIN_CASES
import logging

LOGGER = logging.getLogger("tests.leximin")

def test_returns_expected_leximin_core_imputation() -> None:
    for case in LEXIMIN_CASES:
        graph = case.build_graph()
        LOGGER.info("Case %s: using initial imputation %s", case.name, case.initial_imputation)
        solver = LeximinSolver(graph, case.initial_imputation)
        imp = solver.solve()
        LOGGER.info("Case %s: computed imputation %s", case.name, imp)
        LOGGER.info("Case %s: expected imputation %s", case.name, Imputation(case.expected))
        assert imp == Imputation(case.expected)
        verify_feasibility(graph, imp)

def verify_feasibility(graph: BipartiteGraph, imp: Imputation) -> None:
    for u in graph.vertices:
        assert imp.profit(u) >= 0, f"Vertex {u} has negative profit: {imp.profit(u)}"
    for u, v in graph.edges:
        assert imp.slack(graph, u, v) >= 0, f"Edge ({u}, {v}) is not dual feasible: slack={imp.slack(graph, u, v)}"


