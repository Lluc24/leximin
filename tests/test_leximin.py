from imputation import Imputation
from leximin import LeximinSolver
from tests.cases_leximin import LEXIMIN_CASES
import logging

LOGGER = logging.getLogger("tests.leximin")

def test_returns_expected_leximin_core_imputation() -> None:
    for case in LEXIMIN_CASES:
        graph = case.build_graph()
        solver = LeximinSolver(graph)
        imp = solver.solve()
        LOGGER.info("Case %s: computed imputation %s", case.name, imp)
        LOGGER.info("Case %s: expected imputation %s", case.name, Imputation(case.expected))
        assert imp == Imputation(case.expected)

