"""Tests for maximum-weight matching wrapper behavior."""

import logging
from fractions import Fraction

from graph import BipartiteGraph
from matching import MaxWeightMatching, max_weight_matching
from tests.matching_tests.cases_mwm import MWM_CASES


LOGGER = logging.getLogger("tests.mwm")


def test_compute_returns_matching() -> None:
    case = MWM_CASES[0]
    matching = max_weight_matching(case.graph)
    assert isinstance(matching, MaxWeightMatching)


def test_cases_have_expected_mwm() -> None:
    for case in MWM_CASES:
        matching = max_weight_matching(case.graph)
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
