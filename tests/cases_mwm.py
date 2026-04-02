from matching import MaxWeightMatching
from tests.case import Case
from fractions import Fraction

MWMCase = Case[MaxWeightMatching]


# Add new examples by appending one more MWMCase here.
MWM_CASES: tuple[MWMCase, ...] = (
    MWMCase(
        name="example_1_Vijay",
        n_u=4,
        n_v=4,
        weighted_edges=(
            (0, 4, Fraction(136)),
            (0, 5, Fraction(140)),
            (1, 5, Fraction(140)),
            (2, 6, Fraction(68)),
            (2, 7, Fraction(56)),
            (3, 7, Fraction(118)),
        ),
        expected=MaxWeightMatching(
            weight=Fraction(462),
            matching=frozenset({(0, 4), (1, 5), (2, 6), (3, 7)})
        )
    ),
    MWMCase(
        name="example_3_Vijay",
        n_u=2,
        n_v=2,
        weighted_edges=(
            (0, 2, Fraction(70)),
            (0, 3, Fraction(110)),
            (1, 3, Fraction(100)),
        ),
        expected=MaxWeightMatching(
            weight=Fraction(170),
            matching=frozenset({(0, 2), (1, 3)})
        )
    ),
)

