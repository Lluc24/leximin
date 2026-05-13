"""Reusable graph fixtures for module-level test suites."""

from dataclasses import dataclass, field
from fractions import Fraction
from components import FundamentalComponent
from graph import BipartiteGraph
from utils import set_u_vertices, set_v_vertices
from classification import Classification

@dataclass(frozen=True)
class TestBipartiteGraph(BipartiteGraph):
    """Bipartite graph used for tests"""

    name: str
    classification: Classification = field(default_factory=Classification, repr=False)
    leximin_imp: dict[int, Fraction] = field(default_factory=dict, repr=False)
    components: list[FundamentalComponent] = field(default_factory=list, repr=False)


SAMPLE_GRAPH = TestBipartiteGraph(
    name="sample_2x2_graph",
    u_vertices=set_u_vertices(2),
    v_vertices=set_v_vertices(2, 2),
    weights={
        (0, 2): Fraction(3, 2),
        (1, 2): Fraction(1),
        (1, 3): Fraction(5),
    }
)

CLASSIFICATION_SINGLE_U_TWO_V_ALL_VIABLE_GRAPH = TestBipartiteGraph(
    name="single_u_two_v_all_viable",
    u_vertices=set_u_vertices(1),
    v_vertices=set_v_vertices(1, 2),
    weights={
        (0, 1): Fraction(1),
        (0, 2): Fraction(1),
    }
)

CLASSIFICATION_SINGLE_U_TWO_V_WITH_DELTA_DIFFERENCE_GRAPH = TestBipartiteGraph(
    name="single_u_two_v_with_delta_difference",
    u_vertices=set_u_vertices(1),
    v_vertices=set_v_vertices(1, 2),
    weights={
        (0, 1): Fraction(1),
        (0, 2): Fraction(101, 100),
    }
)

ALL_ONES_2X2_GRAPH = TestBipartiteGraph(
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

VIJAY_EXAMPLE_1_GRAPH = TestBipartiteGraph(
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
    },
    leximin_imp={
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

VIJAY_EXAMPLE_3_GRAPH = TestBipartiteGraph(
    name="vijay_example_3",
    u_vertices=set_u_vertices(2),
    v_vertices=set_v_vertices(2, 2),
    weights={
        (0, 2): Fraction(70),
        (1, 3): Fraction(100),
        (0, 3): Fraction(110),
    },
    leximin_imp={
        0: Fraction(40),
        1: Fraction(30),
        2: Fraction(30),
        3: Fraction(70),
    },
)

VIJAY_EXAMPLE_5_GRAPH = TestBipartiteGraph(
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
    },
    leximin_imp={
        0: Fraction(20),
        1: Fraction(50),
        2: Fraction(60),
        3: Fraction(30),
        4: Fraction(40),
        5: Fraction(20),
        6: Fraction(40),
        7: Fraction(30),
    },
)

HANDMADE_GRAPH = TestBipartiteGraph(
    name="handmade_graph",
    u_vertices=set_u_vertices(5),
    v_vertices=set_v_vertices(5, 3),
    weights={
        (0, 5): Fraction(10),
        (0, 6): Fraction(10),
        (1, 5): Fraction(10),
        (1, 6): Fraction(10),
        (2, 7): Fraction(10),
        (3, 5): Fraction(10),
        (3, 6): Fraction(1),
        (4, 5): Fraction(1),
        (4, 6): Fraction(1),
        (4, 7): Fraction(1),
    },
    classification=Classification(
        essential_u=frozenset({2}),
        essential_v=frozenset({5, 6, 7}),
        viable_u=frozenset({0, 1, 3}),
        subpar_u=frozenset({4}),
        essential_edges=frozenset({(2, 7)}),
        viable_edges=frozenset({(0, 5), (0, 6), (1, 5), (1, 6), (3, 5)}),
        subpar_edges=frozenset({(3, 6), (4, 5), (4, 6), (4, 7)}),
    ),
    leximin_imp={
        0: Fraction(0),
        1: Fraction(0),
        2: Fraction(5),
        3: Fraction(0),
        4: Fraction(0),
        5: Fraction(10),
        6: Fraction(10),
        7: Fraction(5),
    },
    components=[
        FundamentalComponent(U=frozenset({2}), V=frozenset({7})),
    ],
)
