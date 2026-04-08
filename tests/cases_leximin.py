from fractions import Fraction
from imputation import Imputation
from tests.case import Case
from dataclasses import dataclass


@dataclass(frozen=True)
class LeximinCase(Case[dict[int, Fraction]]):
    initial_imputation: Imputation | None = None


# Add new examples by appending one more LeximinCase here.
LEXIMIN_CASES: tuple[LeximinCase, ...] = (
    LeximinCase(
        name="vijay_example5_leximin_core_imputation",
        n_u=4,
        n_v=4,
        weighted_edges=(
            (0, 4, Fraction(60)),
            (1, 4, Fraction(90)),
            (1, 5, Fraction(70)),
            (2, 5, Fraction(80)),
            (2, 6, Fraction(100)),
            (3, 6, Fraction(60)),
            (3, 7, Fraction(60)),
        ),
        initial_imputation=Imputation({
            0: Fraction(20),
            1: Fraction(50),
            2: Fraction(60),
            3: Fraction(20),
            4: Fraction(40),
            5: Fraction(20),
            6: Fraction(40),
            7: Fraction(40),
        }),
        expected={
            0: Fraction(20),
            1: Fraction(50),
            2: Fraction(60),
            3: Fraction(30),
            4: Fraction(40),
            5: Fraction(20),
            6: Fraction(40),
            7: Fraction(30),
        },
    ),
    LeximinCase(
        name="vijay_example1_leximin_core_imputation",
        n_u=2,
        n_v=2,
        weighted_edges=(
            (0, 2, Fraction(70)),
            (1, 3, Fraction(100)),
            (0, 3, Fraction(110))
        ),
        expected={
            0: Fraction(40),
            1: Fraction(30),
            2: Fraction(30),
            3: Fraction(70),
        },
    ),
    LeximinCase(
        name="vijay_example3_leximin_core_imputation",
        n_u=4,
        n_v=4,
        weighted_edges=(
            (0, 4, Fraction(136)),
            (0, 5, Fraction(140)),
            (1, 5, Fraction(76)),
            (2, 6, Fraction(68)),
            (2, 7, Fraction(56)),
            (3, 7, Fraction(118)),
        ),
        expected={
            0: Fraction(100),
            1: Fraction(36),
            2: Fraction(34),
            3: Fraction(59),
            4: Fraction(36),
            5: Fraction(40),
            6: Fraction(34),
            7: Fraction(59),
        },
    )
)

