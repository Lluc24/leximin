"""Cross-validation tests comparing LeximinSolver and LeximinLPSolver on all graphs in experiments/data.

These tests are excluded from the default test run because they are too slow (1020 graphs).
Run them explicitly with: pytest -m crossval
"""

import logging
import pathlib

import pytest

from graph import BipartiteGraph
from leximin import LeximinSolver
from lp_solver import LeximinLPSolver

LOGGER = logging.getLogger("tests.random_crossval")
TOLERANCE = 1e-6
DATA_DIR = pathlib.Path(__file__).parent.parent / "experiments" / "data"


@pytest.mark.crossval
def test_random_crossval() -> None:
    graph_files = sorted(DATA_DIR.glob("*.json"))
    assert graph_files, f"No graph files found in {DATA_DIR}"

    for path in graph_files:
        graph = BipartiteGraph.load(path)
        LOGGER.info("Cross-validating graph %s", path.name)

        imp_leximin = LeximinSolver(graph).solve()
        imp_lp = LeximinLPSolver(graph).solve()

        max_diff = 0.0
        for v in graph.vertices:
            diff = abs(float(imp_leximin.profits[v]) - imp_lp.profits[v])
            max_diff = max(max_diff, diff)
            assert diff <= TOLERANCE, (
                f"Graph {path.name}: vertex {v} imputation mismatch "
                f"(LeximinSolver={imp_leximin.profits[v]}, LeximinLPSolver={imp_lp.profits[v]}, diff={diff})"
            )
        LOGGER.info(f"Graph {path.name} has maximum difference {max_diff}")