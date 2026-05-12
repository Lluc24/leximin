import logging

from fractions import Fraction
from itertools import combinations, chain

from graph import BipartiteGraph
from imputation import Imputation, compute_imputation
from matching import max_weight_matching
from tests.imputation_tests.cases_imputation import (
    IMPUTATION_CORE_CASES,
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


def verify_is_in_core(graph: BipartiteGraph, imputation: Imputation) -> None:
    vertices = tuple(sorted(graph.vertices))
    coalitions = chain.from_iterable(combinations(vertices, size) for size in range(len(vertices) + 1))
    for coalition in coalitions:
        coalition_set = frozenset(coalition)
        coalition_u = graph.u_vertices.intersection(coalition_set)
        coalition_v = graph.v_vertices.intersection(coalition_set)
        coalition_graph = BipartiteGraph(
            u_vertices=coalition_u,
            v_vertices=coalition_v,
            weights={
                (u, v): w
                for (u, v), w in graph.weights.items()
                if u in coalition_u and v in coalition_v
            },
        )
        coalition_value = max_weight_matching(coalition_graph).weight
        coalition_profit = sum((imputation.profit(v) for v in coalition_set), Fraction(0))
        assert coalition_profit >= coalition_value, (
            f"Coalition {coalition} violates core: "
            f"profit={coalition_profit}, value={coalition_value}"
        )


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


def test_compute_imputation_lies_in_core_for_all_coalitions() -> None:
    for case in IMPUTATION_CORE_CASES:
        imputation = compute_imputation(case.graph, max_weight_matching(case.graph))
        verify_is_in_core(case.graph, imputation)
