from fractions import Fraction
from imputation import Imputation
from tests.case import Case
from dataclasses import dataclass
from tests.graphs import VIJAY_EXAMPLE_1_GRAPH, VIJAY_EXAMPLE_3_GRAPH, VIJAY_EXAMPLE_5_GRAPH


@dataclass(frozen=True)
class LeximinCase(Case[dict[int, Fraction]]):
    initial_imputation: Imputation | None = None


# Add new examples by appending one more LeximinCase here.
LEXIMIN_CASES: tuple[LeximinCase, ...] = (
    LeximinCase(
        name="vijay_example5_leximin_core_imputation",
        graph=VIJAY_EXAMPLE_5_GRAPH,
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
        graph=VIJAY_EXAMPLE_1_GRAPH,
        expected={
            0: Fraction(40),
            1: Fraction(30),
            2: Fraction(30),
            3: Fraction(70),
        },
    ),
    LeximinCase(
        name="vijay_example3_leximin_core_imputation",
        graph=VIJAY_EXAMPLE_3_GRAPH,
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

