"""Tests for component tree operations used by the leximin solver."""

from fractions import Fraction
import pytest
from components import FundamentalComponent, ValidComponent
from tests.components_tests.cases_components import (
    BASE_COMPONENT,
    BASE_IMPUTATION,
    CHILD_EXCLUDE,
    MIN_SUB1_CASES,
    MIN_SUB2_CASES,
    MIN_SUB3_CASES,
    fc_pairs,
)


def test_fundamental_component_profit_helpers() -> None:
    fc = FundamentalComponent(
        U=frozenset({0}),
        V=frozenset({1}),
    )
    imp = BASE_IMPUTATION.copy()
    imp.set_profit(0, Fraction(3))
    imp.set_profit(1, Fraction(7))

    assert fc.has_min_on_left(imp)
    assert not fc.has_min_on_right(imp)
    assert not fc.has_min_equal(imp)
    assert fc.min_profit(imp) == Fraction(3)
    assert fc.rotation_to_fully_repair(imp) == Fraction(2)


def test_valid_component_compute_min_sub1_cases() -> None:
    for case in MIN_SUB1_CASES:
        min_sub = case.component.compute_min_sub1(case.imputation)
        assert fc_pairs(min_sub) == case.expected, f"Unexpected min_sub1 for case: {case.name}"


def test_valid_component_compute_min_sub2_cases() -> None:
    for case in MIN_SUB2_CASES:
        min_self, min_other = case.source.compute_min_sub2(case.other, case.i, case.j)
        assert (fc_pairs(min_self), fc_pairs(min_other)) == case.expected, (
            f"Unexpected min_sub2 for case: {case.name}"
        )


def test_valid_component_compute_min_sub3_cases() -> None:
    for case in MIN_SUB3_CASES:
        min_sub = case.component.compute_min_sub3(2)
        assert fc_pairs(min_sub) == case.expected, f"Unexpected min_sub3 for case: {case.name}"


def test_valid_component_decompose_remainder() -> None:
    min_sub = BASE_COMPONENT.compute_min_sub3(2)
    remainder_pairs = {(fc.u, fc.v) for fc in BASE_COMPONENT.decompose_remainder(min_sub)}
    assert remainder_pairs == {(1, 4)}


def test_valid_component_add_child_at_recurses_to_matching_child() -> None:
    component = ValidComponent(
        root=FundamentalComponent(
            U=frozenset({0}),
            V=frozenset({3}),
        ),
        rotation="CW",
        children=frozenset({
            ValidComponent(
                root=FundamentalComponent(
                    U=frozenset({1}),
                    V=frozenset({4}),
                ),
                rotation="CW"
            )
        }),
    )
    updated = component.add_child_at(1, CHILD_EXCLUDE)

    assert fc_pairs(updated) == {(0, 3), (1, 4), (2, 5)}
    assert fc_pairs(component) == {(0, 3), (1, 4)}


def test_valid_component_add_child_at_raises_for_unknown_vertex() -> None:
    with pytest.raises(ValueError):
        BASE_COMPONENT.add_child_at(99, CHILD_EXCLUDE)
