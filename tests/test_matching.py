import logging
from matching import MaxWeightMatching, max_weight_matching
from tests.cases_mwm import MWM_CASES
from graph import BipartiteGraph
from fractions import Fraction


LOGGER = logging.getLogger("tests.mwm")


def test_compute_returns_matching() -> None:
    case = MWM_CASES[0]
    graph = case.build_graph()
    matching = max_weight_matching(graph)
    assert isinstance(matching, MaxWeightMatching)


def test_cases_have_expected_mwm() -> None:
    for case in MWM_CASES:
        graph = case.build_graph()
        matching = max_weight_matching(graph)
        LOGGER.info(
            "case=%s expected=%s computed=%s",
            case.name,
            case.expected,
            matching,
        )
        assert matching == case.expected, f"Unexpected matching for case: {case.name}"

def test_correct_weight(sample_graph: BipartiteGraph) -> None:
    sample_matching: MaxWeightMatching = max_weight_matching(sample_graph)
    expected_weight = sum((sample_graph.weight(*e) for e in sample_matching.matching), Fraction(0))
    LOGGER.info(
        "sample_matching=%s expected_weight=%s computed_weight=%s",
        sample_matching.matching,
        expected_weight,
        sample_matching.weight,
    )
    assert sample_matching.weight == expected_weight

