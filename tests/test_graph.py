from tests.fixtues import IMPUTATION_FOR_VAZIRANI_3, VAZIRANI_3
from fractions import Fraction
from copy import deepcopy

def test_vertices() -> None:
    graph = VAZIRANI_3
    assert graph.vertices == frozenset({0, 1, 2, 3})

def test_edges() -> None:
    graph = VAZIRANI_3
    assert graph.edges == frozenset({(0, 2), (1, 3), (0, 3)})

def test_weighted_edges() -> None:
    graph = VAZIRANI_3
    assert graph.weighted_edges == frozenset({(0, 2, Fraction(70)), (1, 3, Fraction(100)), (0, 3, Fraction(110))})

def test_neighbors_of() -> None:
    graph = VAZIRANI_3
    assert graph.neighbors_of(0) == frozenset({2, 3})
    assert graph.neighbors_of(1) == frozenset({3})
    assert graph.neighbors_of(2) == frozenset({0})
    assert graph.neighbors_of(3) == frozenset({0, 1})

def test_subtract_edge() -> None:
    graph = VAZIRANI_3
    new_graph = graph - (0, 2)
    assert new_graph.edges == frozenset({(1, 3), (0, 3)})
    assert new_graph.weights == {(1, 3): Fraction(100), (0, 3): Fraction(110)}

def test_subtract_vertex() -> None:
    graph = VAZIRANI_3
    new_graph = graph - 0
    assert new_graph.vertices == frozenset({1, 2, 3})
    assert new_graph.edges == frozenset({(1, 3)})
    assert new_graph.weights == {(1, 3): Fraction(100)}

def test_is_imputation_in_core() -> None:
    graph = VAZIRANI_3
    imputation = deepcopy(IMPUTATION_FOR_VAZIRANI_3)
    assert graph.is_imputation_in_core(imputation.profits) == True
    imputation.profits[0] -= 1
    assert graph.is_imputation_in_core(imputation.profits) == False
