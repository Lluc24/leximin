"""Table-driven expected outcomes for max-weight matching tests."""

from fractions import Fraction

from matching import MaxWeightMatching
from tests.case import Case
from tests.graphs import VIJAY_EXAMPLE_1_GRAPH, VIJAY_EXAMPLE_3_GRAPH

MWMCase = Case[MaxWeightMatching]


# Add new examples by appending one more MWMCase here.
MWM_CASES: tuple[MWMCase, ...] = (
    MWMCase(
        name=f"{VIJAY_EXAMPLE_1_GRAPH.name}_mwm",
        graph=VIJAY_EXAMPLE_1_GRAPH,
        expected=MaxWeightMatching(
            weight=Fraction(398),
            matching=frozenset({(0, 4), (1, 5), (2, 6), (3, 7)})
        )
    ),
    MWMCase(
        name=f"{VIJAY_EXAMPLE_3_GRAPH.name}_mwm",
        graph=VIJAY_EXAMPLE_3_GRAPH,
        expected=MaxWeightMatching(
            weight=Fraction(170),
            matching=frozenset({(0, 2), (1, 3)})
        )
    ),
)
