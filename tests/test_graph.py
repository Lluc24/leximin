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


def test_edges_property_returns_defined_edges(sample_graph: BipartiteGraph) -> None:
    assert sample_graph.edges == {(0, 2), (1, 2), (1, 3)}


def test_vertices_property_returns_union(sample_graph: BipartiteGraph) -> None:
    assert sample_graph.vertices == {0, 1, 2, 3}


def test_add_operator_adds_edge_and_keeps_original_unchanged(sample_graph: BipartiteGraph) -> None:
    updated = sample_graph + (0, 3, Fraction(7))
    assert updated.weight(0, 3) == Fraction(7)
    assert sample_graph.weight(0, 3) == Fraction(0)


def test_add_operator_raises_if_vertices_not_in_graph(sample_graph: BipartiteGraph) -> None:
    with pytest.raises(ValueError):
        _ = sample_graph + (9, 3, Fraction(1))


def test_sub_operator_removes_edge_and_keeps_original_unchanged(sample_graph: BipartiteGraph) -> None:
    updated = sample_graph - (1, 3)
    assert (1, 3) not in updated.edges
    assert (1, 3) in sample_graph.edges


def test_sub_operator_raises_if_edge_not_present(sample_graph: BipartiteGraph) -> None:
    with pytest.raises(ValueError):
        _ = sample_graph - (0, 3)


def test_sub_operator_with_vertex_removes_vertex_and_incident_edges(sample_graph: BipartiteGraph) -> None:
    updated = sample_graph - 1
    assert 1 not in updated.vertices
    assert updated.edges == {(0, 2)}


def test_add_vertex_to_u(sample_graph: BipartiteGraph) -> None:
    updated = sample_graph.add_vertex_to_u(10)
    assert 10 in updated.u_vertices
    assert 10 not in sample_graph.u_vertices


def test_add_vertex_to_v(sample_graph: BipartiteGraph) -> None:
    updated = sample_graph.add_vertex_to_v(11)
    assert 11 in updated.v_vertices
    assert 11 not in sample_graph.v_vertices

