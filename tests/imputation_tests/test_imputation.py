import logging

from fractions import Fraction

from imputation import Imputation
from tests.imputation_tests.cases_imputation import (
    IMPUTATION_COPY_CASES,
    IMPUTATION_ESSENTIAL_PROFITS_CASES,
    IMPUTATION_PROFIT_CASES,
    IMPUTATION_ROTATION_CASES,
    IMPUTATION_SLACK_CASES,
)


LOGGER = logging.getLogger("tests.imputation")


def assert_profits(imputation: Imputation, expected: dict[int, Fraction]) -> None:
    for vertex, value in expected.items():
        assert imputation.profit(vertex) == value, f"Unexpected profit for vertex {vertex}"


def test_profit_returns_expected_values() -> None:
    for case in IMPUTATION_PROFIT_CASES:
        imputation = Imputation(case.profits)
        assert_profits(imputation, case.expected)


def test_slack_and_tightness_match_expected_values() -> None:
    for case in IMPUTATION_SLACK_CASES:
        imputation = Imputation(case.profits)
        for (u, v), expected_slack in case.expected.items():
            slack = imputation.slack(case.graph, u, v)
            LOGGER.info(
                "case=%s edge=(%s, %s) slack=%s expected=%s",
                case.name,
                u,
                v,
                slack,
                expected_slack,
            )
            assert slack == expected_slack, f"Unexpected slack for edge ({u}, {v}) in case {case.name}"
            assert imputation.is_tight(case.graph, u, v) is (expected_slack == Fraction(0))


def test_apply_rotation_updates_profits() -> None:
    for case in IMPUTATION_ROTATION_CASES:
        imputation = Imputation(case.profits)
        imputation.apply_rotation(case.increasing, case.decreasing, case.delta)
        assert_profits(imputation, case.expected)


def test_copy_keeps_an_independent_snapshot() -> None:
    for case in IMPUTATION_COPY_CASES:
        original = Imputation(case.profits)
        copied = original.copy()
        original.set_profit(case.mutated_vertex, case.mutated_value)

        assert copied is not original
        assert_profits(copied, case.expected)
        assert original.profit(case.mutated_vertex) == case.mutated_value


def test_sorted_essential_profits_uses_classification() -> None:
    for case in IMPUTATION_ESSENTIAL_PROFITS_CASES:
        imputation = Imputation(case.profits)
        assert imputation.sorted_essential_profits(case.classification) == case.expected

