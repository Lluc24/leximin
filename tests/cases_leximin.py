from fractions import Fraction

from tests.case import Case


LeximinCase = Case[dict[int, Fraction]]


# Add new examples by appending one more LeximinCase here.
LEXIMIN_CASES: tuple[LeximinCase, ...] = (
    LeximinCase(
        name="vijay_example_leximin_core_imputation",
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
        expected={
            0: Fraction(100),
            1: Fraction(36),
            2: Fraction(28),
            3: Fraction(90),
            4: Fraction(36),
            5: Fraction(40),
            6: Fraction(40),
            7: Fraction(28),
        },
    ),
)

