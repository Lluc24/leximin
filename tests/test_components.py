from fractions import Fraction
import pytest
from component import FundamentalComponent, ValidComponent
from tests.fixtues import (
    CHILD_FC,
    IMPUTATION_FOR_COMPONENTS,
    ROOT_FC,
    VALID_COMPONENT_CW,
)


def test_fundamental_component_vertices() -> None:
    fc = ROOT_FC
    assert fc.left == frozenset({0})
    assert fc.right == frozenset({2})
    assert fc.vertices == frozenset({0, 2})


def test_valid_component_vertices() -> None:
    vc = VALID_COMPONENT_CW
    assert vc.left == frozenset({0, 1})
    assert vc.right == frozenset({2, 3})
    assert vc.vertices == frozenset({0, 1, 2, 3})


def test_rotation_direction_sets() -> None:
    cw = VALID_COMPONENT_CW
    assert cw.increasing_vertices == frozenset({0, 1})
    assert cw.decreasing_vertices == frozenset({2, 3})


def test_get_fcs() -> None:
    vc = VALID_COMPONENT_CW
    assert vc.get_fcs() == frozenset({ROOT_FC, CHILD_FC})


def test_structural_eq() -> None:
    rebuilt = ValidComponent(
        root=FundamentalComponent(U=frozenset({0}), V=frozenset({2})),
        rotation="CW",
        children=frozenset(
            {
                ValidComponent(
                    root=FundamentalComponent(U=frozenset({1}), V=frozenset({3})),
                    rotation="CW",
                )
            }
        ),
    )
    assert VALID_COMPONENT_CW.structural_eq(rebuilt)
    assert not VALID_COMPONENT_CW == rebuilt


def test_component_profit_helpers() -> None:
    vc = VALID_COMPONENT_CW
    imp = IMPUTATION_FOR_COMPONENTS
    assert vc.min_left(imp) == Fraction(4)
    assert vc.min_right(imp) == Fraction(6)
    assert vc.has_min_on_left(imp)
    assert vc.min_profit(imp) == Fraction(4)
    assert vc.rotation_to_fully_repair(imp) == Fraction(1)


def test_add_child_at() -> None:
    base = ValidComponent(root=ROOT_FC, rotation="CW")
    updated = base.add_child_at(0, CHILD_FC)
    assert updated.structural_eq(VALID_COMPONENT_CW)


def test_add_child_at_raises_for_vertex_outside_component() -> None:
    base = ValidComponent(root=ROOT_FC, rotation="CW")
    with pytest.raises(ValueError, match="Vertex 99 is not in the component."):
        base.add_child_at(99, CHILD_FC)


def test_compute_min_sub3_and_remainder() -> None:
    vc = VALID_COMPONENT_CW
    min_sub = vc.compute_min_sub3(0)
    assert min_sub.get_fcs() == frozenset({ROOT_FC})
    assert vc.decompose_remainder(min_sub) == frozenset({CHILD_FC})