from classification import Classification
from tests.case import Case
from fractions import Fraction


ClassificationCase = Case[Classification]


# Add new examples by appending one more ClassificationCase here.
CLASSIFICATION_CASES: tuple[ClassificationCase, ...] = (
    ClassificationCase(
        name="single_u_two_v_all_viable",
        n_u=1,
        n_v=2,
        weighted_edges=(
            (0, 1, Fraction(1)),
            (0, 2, Fraction(1)),
        ),
        expected=Classification(
            essential_u=frozenset({0}),
            viable_v=frozenset({1, 2}),
            viable_edges=frozenset({(0, 1), (0, 2)}),
        ),
    ),
    ClassificationCase(
        name="single_u_two_v_with_delta_difference",
        n_u=1,
        n_v=2,
        weighted_edges=(
            (0, 1, Fraction(1)),
            (0, 2, Fraction(101, 100)),
        ),
        expected=Classification(
            essential_u=frozenset({0}),
            essential_v=frozenset({2}),
            subpar_v=frozenset({1}),
            essential_edges=frozenset({(0, 2)}),
            subpar_edges=frozenset({(0, 1)})
        ),
    ),
    ClassificationCase(
        name="two_u_two_v_all_essential",
        n_u=2,
        n_v=2,
        weighted_edges=(
            (0, 2, Fraction(1)),
            (0, 3, Fraction(1)),
            (1, 2, Fraction(1)),
            (1, 3, Fraction(1)),
        ),
        expected=Classification(
            essential_u=frozenset({0, 1}),
            essential_v=frozenset({2, 3}),
            viable_edges=frozenset({(0, 2), (0, 3), (1, 2), (1, 3)}),
        ),
    )
)

