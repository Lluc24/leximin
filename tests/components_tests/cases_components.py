"""Table-driven cases for component-subtree operations."""

from dataclasses import dataclass
from fractions import Fraction

from components import FundamentalComponent, ValidComponent
from imputation import Imputation
from tests.case import Case
from tests.graphs import SAMPLE_GRAPH


def fc_pairs(component: ValidComponent) -> frozenset[tuple[int, int]]:
    """Project a valid component to `(u, v)` pairs for concise assertions."""
    return frozenset((fc.u, fc.v) for fc in component.all_fcs)


@dataclass(frozen=True)
class MinSubCase(Case[frozenset[tuple[int, int]]]):
    """Case for a single minimal-subtree extraction."""

    component: ValidComponent
    imputation: Imputation


@dataclass(frozen=True)
class MinSub2Case(Case[tuple[frozenset[tuple[int, int]], frozenset[tuple[int, int]]]]):
    """Case for two-component minimal subtree extraction."""

    source: ValidComponent
    other: ValidComponent
    i: int
    j: int


ROOT = FundamentalComponent(0, 3)
CHILD_INCLUDE = FundamentalComponent(1, 4)
CHILD_EXCLUDE = FundamentalComponent(2, 5)

BASE_COMPONENT = ValidComponent(
    root=ROOT,
    rotation="CW",
    children=frozenset(
        {
            ValidComponent(root=CHILD_INCLUDE, rotation="CW"),
            ValidComponent(root=CHILD_EXCLUDE, rotation="CW"),
        }
    ),
)

BASE_IMPUTATION = Imputation(
    {
        0: Fraction(5),
        1: Fraction(3),
        2: Fraction(4),
        3: Fraction(2),
        4: Fraction(5),  # Includes CHILD_INCLUDE in compute_min_sub1 for CW.
        5: Fraction(7),
    }
)


MIN_SUB1_CASES: tuple[MinSubCase, ...] = (
    MinSubCase(
        name="cw_root_plus_descendants_with_matching_profit",
        graph=SAMPLE_GRAPH,
        component=BASE_COMPONENT,
        imputation=BASE_IMPUTATION,
        expected=frozenset({(0, 3), (1, 4)}),
    ),
)


MIN_SUB3_CASES: tuple[MinSubCase, ...] = (
    MinSubCase(
        name="path_to_selected_vertex_is_kept",
        graph=SAMPLE_GRAPH,
        component=BASE_COMPONENT,
        imputation=BASE_IMPUTATION,
        expected=frozenset({(0, 3), (2, 5)}),
    ),
)


MIN_SUB2_CASES: tuple[MinSub2Case, ...] = (
    MinSub2Case(
        name="extracts_min_trees_around_tight_edge_endpoints",
        graph=SAMPLE_GRAPH,
        source=ValidComponent(
            root=ROOT,
            rotation="CW",
            children=frozenset({ValidComponent(root=CHILD_INCLUDE, rotation="CW")}),
        ),
        other=ValidComponent(root=CHILD_EXCLUDE, rotation="CW"),
        i=1,
        j=5,
        expected=(frozenset({(0, 3), (1, 4)}), frozenset({(2, 5)})),
    ),
)
