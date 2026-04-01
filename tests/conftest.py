from fractions import Fraction
import pytest
from graph import BipartiteGraph


@pytest.fixture
def sample_graph() -> BipartiteGraph:
    return BipartiteGraph(
        u_vertices=frozenset({0, 1}),
        v_vertices=frozenset({2, 3}),
        weights={
            (0, 2): Fraction(3, 2),
            (1, 2): Fraction(1),
            (1, 3): Fraction(5),
        },
    )
