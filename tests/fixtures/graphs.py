"""Reusable graph fixtures for module-level test suites."""

from dataclasses import dataclass, field
from fractions import Fraction
from components import FundamentalComponent
from graph import BipartiteGraph
from imputation import Imputation
from utils import set_u_vertices, set_v_vertices
from classification import Classification
from matching import MaxWeightMatching

@dataclass(frozen=True)
class TestBipartiteGraph(BipartiteGraph):
    """Bipartite graph used for tests"""

    name: str
    degenerate: bool = field(default=False, repr=False)
    matching: MaxWeightMatching = field(default_factory=MaxWeightMatching, repr=False)
    classification: Classification = field(default_factory=Classification, repr=False)
    leximin_imp: Imputation = field(default_factory=Imputation, repr=False)
    fcs: set[FundamentalComponent] = field(default_factory=set, repr=False)


"""
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
"""

VAZIRANI_1 = TestBipartiteGraph(
    name="vazirani_1",
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
    degenerate=False,
    matching=MaxWeightMatching(
        weight=Fraction(398),
        matching=frozenset({(0, 4), (1, 5), (2, 6), (3, 7)}),
    ),
    classification=Classification(
        essential_u=frozenset({0, 1, 2, 3}),
        essential_v=frozenset({4, 5, 6, 7}),
        essential_edges=frozenset({(0, 4), (1, 5), (2, 6), (3, 7)}),
        subpar_edges=frozenset({(0, 5), (2, 7)})
    ),
    leximin_imp=Imputation(
        {
            0: Fraction(100),
            1: Fraction(36),
            2: Fraction(34),
            3: Fraction(59),
            4: Fraction(36),
            5: Fraction(40),
            6: Fraction(34),
            7: Fraction(59),
        }
    ),
    fcs={
        FundamentalComponent(
            U=frozenset({0}),
            V=frozenset({4}),
        ),
        FundamentalComponent(
            U=frozenset({1}),
            V=frozenset({5}),
        ),
        FundamentalComponent(
            U=frozenset({2}),
            V=frozenset({6}),
        ),
        FundamentalComponent(
            U=frozenset({3}),
            V=frozenset({7}),
        )
    }
)

VAZIRANI_3 = TestBipartiteGraph(
    name="vazirani_3",
    u_vertices=set_u_vertices(2),
    v_vertices=set_v_vertices(2, 2),
    weights={
        (0, 2): Fraction(70),
        (1, 3): Fraction(100),
        (0, 3): Fraction(110),
    },
    degenerate=False,
    matching=MaxWeightMatching(
        weight=Fraction(170),
        matching=frozenset({(0, 2), (1, 3)}),
    ),
    classification=Classification(
        essential_u=frozenset({0, 1}),
        essential_v=frozenset({2, 3}),
        essential_edges=frozenset({(0, 2), (1, 3)}),
        subpar_edges=frozenset({(0, 3)}),
    ),
    leximin_imp=Imputation(
        {
            0: Fraction(40),
            1: Fraction(30),
            2: Fraction(30),
            3: Fraction(70),
        }
    ),
    fcs={
        FundamentalComponent(
            U=frozenset({0}),
            V=frozenset({2}),
        ),
        FundamentalComponent(
            U=frozenset({1}),
            V=frozenset({3}),
        )
    }
)

VAZIRANI_5 = TestBipartiteGraph(
    name="vazirani_5",
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
    degenerate=False,
    matching=MaxWeightMatching(
        weight=Fraction(290),
        matching=frozenset({(0, 4), (1, 5), (2, 6), (3, 7)}),
    ),
    classification=Classification(
        essential_u=frozenset({0, 1, 2, 3}),
        essential_v=frozenset({4, 5, 6, 7}),
        essential_edges=frozenset({(0, 4), (1, 5), (2, 6), (3, 7)}),
        subpar_edges=frozenset({(1, 4), (2, 5), (3, 6)}),
    ),
    leximin_imp=Imputation(
        {
            0: Fraction(20),
            1: Fraction(50),
            2: Fraction(60),
            3: Fraction(30),
            4: Fraction(40),
            5: Fraction(20),
            6: Fraction(40),
            7: Fraction(30),
        }
    ),
    fcs={
        FundamentalComponent(
            U=frozenset({0}),
            V=frozenset({4}),
        ),
        FundamentalComponent(
            U=frozenset({1}),
            V=frozenset({5}),
        ),
        FundamentalComponent(
            U=frozenset({2}),
            V=frozenset({6}),
        ),
        FundamentalComponent(
            U=frozenset({3}),
            V=frozenset({7}),
        )
    }
)

SANTAMARIA_1 = TestBipartiteGraph(
    name="santamaria_1",
    u_vertices=set_u_vertices(2),
    v_vertices=set_v_vertices(2, 2),
    weights={
        (0, 2): Fraction(3, 2),
        (1, 2): Fraction(1),
        (1, 3): Fraction(5),
    },
    degenerate=False,
    matching=MaxWeightMatching(
        weight=Fraction(13, 2),
        matching=frozenset({(0, 2), (1, 3)}),
    ),
    classification=Classification(
        essential_u=frozenset({0, 1}),
        essential_v=frozenset({2, 3}),
        essential_edges=frozenset({(0, 2), (1, 3)}),
        subpar_edges=frozenset({(1, 2)}),
    ),
    leximin_imp=Imputation(
        {
            0: Fraction(3, 4),
            1: Fraction(5, 2),
            2: Fraction(3, 4),
            3: Fraction(5, 2),
        }
    ),
    fcs={
        FundamentalComponent(
            U=frozenset({0}),
            V=frozenset({2}),
        ),
        FundamentalComponent(
            U=frozenset({1}),
            V=frozenset({3}),
        ),
    }
)

SANTAMARIA_2 = TestBipartiteGraph(
    name="santamaria_2",
    u_vertices=set_u_vertices(5),
    v_vertices=set_v_vertices(5, 3),
    degenerate=True,
    matching=MaxWeightMatching(
        weight=Fraction(30),
        matching=frozenset({(0, 5), (1, 6), (2, 7)}),
    ),
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
    leximin_imp=Imputation(
        {
            0: Fraction(0),
            1: Fraction(0),
            2: Fraction(5),
            3: Fraction(0),
            4: Fraction(0),
            5: Fraction(10),
            6: Fraction(10),
            7: Fraction(5),
        }
    ),
    fcs={
        FundamentalComponent(
            U=frozenset({2}),
            V=frozenset({7})),
    },
)

ALL_GRAPHS = (
    VAZIRANI_1,
    VAZIRANI_3,
    VAZIRANI_5,
    SANTAMARIA_1,
    SANTAMARIA_2,
)
