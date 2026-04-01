from fractions import Fraction

import pytest

from graph import BipartiteGraph


def test_neighbors_of_u_vertex(sample_graph: BipartiteGraph) -> None:
    assert set(sample_graph.neighbors_of(1)) == {2, 3}


def test_neighbors_of_v_vertex(sample_graph: BipartiteGraph) -> None:
    assert set(sample_graph.neighbors_of(2)) == {0, 1}


def test_neighbors_of_invalid_vertex_raises(sample_graph: BipartiteGraph) -> None:
    with pytest.raises(ValueError):
        sample_graph.neighbors_of(99)


def test_weight_existing_edge(sample_graph: BipartiteGraph) -> None:
    assert sample_graph.weight(0, 2) == Fraction(3, 2)


def test_weight_missing_edge_is_zero(sample_graph: BipartiteGraph) -> None:
    assert sample_graph.weight(0, 3) == Fraction(0)


def test_all_edges_returns_defined_edges(sample_graph: BipartiteGraph) -> None:
    assert set(sample_graph.all_edges()) == {(0, 2), (1, 2), (1, 3)}

