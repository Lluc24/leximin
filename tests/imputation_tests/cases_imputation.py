from dataclasses import dataclass
from fractions import Fraction

from classification import Classification
from tests.case import Case
from tests.graphs import ALL_ONES_2X2_GRAPH, SAMPLE_GRAPH


@dataclass(frozen=True)
class ImputationProfitCase(Case[dict[int, Fraction]]):
    profits: dict[int, Fraction]


@dataclass(frozen=True)
class ImputationSlackCase(Case[dict[tuple[int, int], Fraction]]):
    profits: dict[int, Fraction]


@dataclass(frozen=True)
class ImputationRotationCase(Case[dict[int, Fraction]]):
    profits: dict[int, Fraction]
    increasing: frozenset[int]
    decreasing: frozenset[int]
    delta: Fraction


@dataclass(frozen=True)
class ImputationCopyCase(Case[dict[int, Fraction]]):
    profits: dict[int, Fraction]
    mutated_vertex: int
    mutated_value: Fraction


@dataclass(frozen=True)
class ImputationEssentialProfitsCase(Case[list[Fraction]]):
    profits: dict[int, Fraction]
    classification: Classification


IMPUTATION_PROFIT_CASES: tuple[ImputationProfitCase, ...] = (
    ImputationProfitCase(
        name="lookup_initial_profits",
        graph=SAMPLE_GRAPH,
        profits={
            0: Fraction(3, 2),
            1: Fraction(2),
            2: Fraction(1, 2),
            3: Fraction(4),
        },
        expected={
            0: Fraction(3, 2),
            1: Fraction(2),
            2: Fraction(1, 2),
            3: Fraction(4),
        },
    ),
)


IMPUTATION_SLACK_CASES: tuple[ImputationSlackCase, ...] = (
    ImputationSlackCase(
        name="slack_and_tight_edges",
        graph=SAMPLE_GRAPH,
        profits={
            0: Fraction(3, 2),
            1: Fraction(2),
            2: Fraction(0),
            3: Fraction(3),
        },
        expected={
            (0, 2): Fraction(0),
            (1, 2): Fraction(1),
            (1, 3): Fraction(0),
        },
    ),
)


IMPUTATION_ROTATION_CASES: tuple[ImputationRotationCase, ...] = (
    ImputationRotationCase(
        name="apply_rotation_changes_profits",
        graph=SAMPLE_GRAPH,
        profits={
            0: Fraction(1),
            1: Fraction(2),
            2: Fraction(1, 2),
            3: Fraction(4),
        },
        increasing=frozenset({0, 2}),
        decreasing=frozenset({1, 3}),
        delta=Fraction(1, 4),
        expected={
            0: Fraction(5, 4),
            1: Fraction(7, 4),
            2: Fraction(3, 4),
            3: Fraction(15, 4),
        },
    ),
)


IMPUTATION_COPY_CASES: tuple[ImputationCopyCase, ...] = (
    ImputationCopyCase(
        name="copy_is_independent_from_original",
        graph=SAMPLE_GRAPH,
        profits={
            0: Fraction(1, 2),
            1: Fraction(1),
            2: Fraction(3, 2),
            3: Fraction(2),
        },
        mutated_vertex=1,
        mutated_value=Fraction(7, 2),
        expected={
            0: Fraction(1, 2),
            1: Fraction(1),
            2: Fraction(3, 2),
            3: Fraction(2),
        },
    ),
)


IMPUTATION_ESSENTIAL_PROFITS_CASES: tuple[ImputationEssentialProfitsCase, ...] = (
    ImputationEssentialProfitsCase(
        name="sorted_essential_profits_uses_classification",
        graph=ALL_ONES_2X2_GRAPH,
        profits={
            0: Fraction(4),
            1: Fraction(1),
            2: Fraction(3),
            3: Fraction(2),
        },
        classification=Classification(
            essential_u=frozenset({0, 1}),
            essential_v=frozenset({2, 3}),
            viable_edges=frozenset({(0, 2), (0, 3), (1, 2), (1, 3)}),
        ),
        expected=[Fraction(1), Fraction(2), Fraction(3), Fraction(4)],
    ),
)

