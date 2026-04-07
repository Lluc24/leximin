from fractions import Fraction
from imputation import Imputation
from tests.case import Case
from dataclasses import dataclass, field


@dataclass(frozen=True)
class LeximinCase(Case[dict[int, Fraction]]):
    initial_imputation: Imputation = field(default_factory=dict)


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
            2: Fraction(70),
            3: Fraction(30),
            4: Fraction(40),
            5: Fraction(20),
            6: Fraction(30),
            7: Fraction(30),
        }),
        expected={
            0: Fraction(20),
            1: Fraction(50),
            2: Fraction(70),
            3: Fraction(30),
            4: Fraction(40),
            5: Fraction(20),
            6: Fraction(30),
            7: Fraction(30),
        },
    ),
)

