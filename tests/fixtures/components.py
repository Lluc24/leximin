"""Reusable component fixtures for module-level test suites."""

from fractions import Fraction
from component import FundamentalComponent, ValidComponent
from imputation import Imputation

ROOT_FC = FundamentalComponent(
    U=frozenset({0}),
    V=frozenset({2}),
)

CHILD_FC = FundamentalComponent(
    U=frozenset({1}),
    V=frozenset({3}),
)

VALID_COMPONENT_CW = ValidComponent(
    root=ROOT_FC,
    rotation="CW",
    children=frozenset(
        {
            ValidComponent(root=CHILD_FC, rotation="CW"),
        }
    ),
)

IMPUTATION_FOR_COMPONENTS = Imputation(
    {
        0: Fraction(4),
        1: Fraction(8),
        2: Fraction(6),
        3: Fraction(10),
    }
)