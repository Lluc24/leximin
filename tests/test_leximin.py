from imputation import Imputation
from leximin import solver
from tests.cases_leximin import LEXIMIN_CASES


def test_returns_expected_leximin_core_imputation() -> None:
    for case in LEXIMIN_CASES:
        graph = case.build_graph()
        result = solver(graph)

        assert isinstance(result, Imputation)
        for vertex, expected_profit in case.expected.items():
            assert result.profit(vertex) == expected_profit, f"Unexpected profit for vertex {vertex} in case {case.name}"


