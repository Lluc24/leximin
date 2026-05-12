from matching import MaxWeightMatching
from tests.case import Case
from tests.graphs import MWM_EXAMPLE_1_VIJAY_GRAPH, MWM_EXAMPLE_3_GRAPH
from fractions import Fraction

MWMCase = Case[MaxWeightMatching]


# Add new examples by appending one more MWMCase here.
MWM_CASES: tuple[MWMCase, ...] = (
    MWMCase(
        name="example_1_Vijay",
        graph=MWM_EXAMPLE_1_VIJAY_GRAPH,
        expected=MaxWeightMatching(
            weight=Fraction(462),
            matching=frozenset({(0, 4), (1, 5), (2, 6), (3, 7)})
        )
    ),
    MWMCase(
        name="example_3_Vijay",
        graph=MWM_EXAMPLE_3_GRAPH,
        expected=MaxWeightMatching(
            weight=Fraction(170),
            matching=frozenset({(0, 2), (1, 3)})
        )
    ),
)

