"""Reusable graph fixtures for module-level test suites."""

from dataclasses import dataclass
from fractions import Fraction

from graph import BipartiteGraph


def set_u_vertices(n_u: int) -> frozenset[int]:
    """Return U-side vertex ids in the repository convention."""
    return frozenset(range(n_u))

def set_v_vertices(n_u: int, n_v: int) -> frozenset[int]:
    """Return V-side vertex ids directly after U ids."""
    return frozenset(range(n_u, n_u + n_v))

@dataclass(frozen=True)
class NamedBipartiteGraph(BipartiteGraph):
    """Bipartite graph with a stable test case name."""

    name: str


SAMPLE_GRAPH = NamedBipartiteGraph(
    name="sample_2x2_graph",
    u_vertices=set_u_vertices(2),
    v_vertices=set_v_vertices(2, 2),
    weights={
        (0, 2): Fraction(3, 2),
        (1, 2): Fraction(1),
        (1, 3): Fraction(5),
    }
)

CLASSIFICATION_SINGLE_U_TWO_V_ALL_VIABLE_GRAPH = NamedBipartiteGraph(
    name="single_u_two_v_all_viable",
    u_vertices=set_u_vertices(1),
    v_vertices=set_v_vertices(1, 2),
    weights={
        (0, 1): Fraction(1),
        (0, 2): Fraction(1),
    }
)

CLASSIFICATION_SINGLE_U_TWO_V_WITH_DELTA_DIFFERENCE_GRAPH = NamedBipartiteGraph(
    name="single_u_two_v_with_delta_difference",
    u_vertices=set_u_vertices(1),
    v_vertices=set_v_vertices(1, 2),
    weights={
        (0, 1): Fraction(1),
        (0, 2): Fraction(101, 100),
    }
)

ALL_ONES_2X2_GRAPH = NamedBipartiteGraph(
    name="all_ones_2x2",
    u_vertices=set_u_vertices(2),
    v_vertices=set_v_vertices(2, 2),
    weights={
        (0, 2): Fraction(1),
        (0, 3): Fraction(1),
        (1, 2): Fraction(1),
        (1, 3): Fraction(1),
    }
)

CLASSIFICATION_TWO_U_TWO_V_ALL_ESSENTIAL_GRAPH = ALL_ONES_2X2_GRAPH

VIJAY_EXAMPLE_1_GRAPH = NamedBipartiteGraph(
    name="vijay_example_1",
    u_vertices=set_u_vertices(4),
    v_vertices=set_v_vertices(4, 4),
    weights={
        (0, 4): Fraction(136),
        (0, 5): Fraction(140),
        (1, 5): Fraction(76),
        (2, 6): Fraction(68),
        (2, 7): Fraction(56),
        (3, 7): Fraction(118),
    }
)

VIJAY_EXAMPLE_3_GRAPH = NamedBipartiteGraph(
    name="vijay_example_3",
    u_vertices=set_u_vertices(2),
    v_vertices=set_v_vertices(2, 2),
    weights={
        (0, 2): Fraction(70),
        (1, 3): Fraction(100),
        (0, 3): Fraction(110),
    }
)

VIJAY_EXAMPLE_5_GRAPH = NamedBipartiteGraph(
    name="vijay_example_5",
    u_vertices=set_u_vertices(4),
    v_vertices=set_v_vertices(4, 4),
    weights={
        (0, 4): Fraction(60),
        (1, 4): Fraction(90),
        (1, 5): Fraction(70),
        (2, 5): Fraction(80),
        (2, 6): Fraction(100),
        (3, 6): Fraction(60),
        (3, 7): Fraction(60),
    }
)
