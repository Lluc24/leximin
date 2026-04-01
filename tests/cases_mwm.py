from dataclasses import dataclass
from fractions import Fraction
from graph import BipartiteGraph


@dataclass(frozen=True)
class MWMCase:
    name: str
    n_u: int
    n_v: int
    weighted_edges: tuple[tuple[int, int, int], ...]
    expected_mwm: frozenset[tuple[int, int]]


def build_graph(case: MWMCase) -> BipartiteGraph:
    """Builds a BipartiteGraph from a compact case definition."""
    u_vertices = frozenset(range(case.n_u))
    v_vertices = frozenset(range(case.n_u, case.n_u + case.n_v))
    weights = {(u, v): Fraction(w) for (u, v, w) in case.weighted_edges}
    return BipartiteGraph(u_vertices=u_vertices, v_vertices=v_vertices, weights=weights)


# Add new examples by appending one more MWMCase here.
MWM_CASES: tuple[MWMCase, ...] = (
    MWMCase(
        name="example_1_Vijay",
        n_u=4,
        n_v=4,
        weighted_edges=(
            (0, 4, 136),
            (0, 5, 140),
            (1, 5, 140),
            (2, 6, 68),
            (2, 7, 56),
            (3, 7, 118),
        ),
        expected_mwm=frozenset({(0, 4), (1, 5), (2, 6), (3, 7)}),
    ),
    MWMCase(
        name="example_3_Vijay",
        n_u=2,
        n_v=2,
        weighted_edges=(
            (0, 2, 70),
            (0, 3, 110),
            (1, 3, 100),
        ),
        expected_mwm=frozenset({(0, 2), (1, 3)}),
    ),
    MWMCase(
        name="diagonal_dominates_3x3",
        n_u=3,
        n_v=3,
        weighted_edges=(
            (0, 3, 9),
            (0, 4, 1),
            (1, 4, 8),
            (1, 5, 2),
            (2, 5, 7),
            (2, 3, 1),
        ),
        expected_mwm=frozenset({(0, 3), (1, 4), (2, 5)}),
    ),
)

