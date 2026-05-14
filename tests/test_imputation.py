from fractions import Fraction
from tests.fixtures.graphs import ALL_GRAPHS, VAZIRANI_3
from imputation import compute_imputation
from tests.fixtures.imputations import IMPUTATION_FOR_VAZIRANI_3

def test_compute_imputation_in_core():
    for graph in ALL_GRAPHS:
        mwm = graph.matching
        imp = compute_imputation(graph, mwm)
        assert graph.is_imputation_in_core(imp.profits), f"Imputation {imp} not in core for graph {graph.name}"

def test_slack():
    graph = VAZIRANI_3
    imp = IMPUTATION_FOR_VAZIRANI_3
    assert imp.slack(graph, 0, 2) == Fraction(0), "Edge (0, 2) should be tight"
    assert imp.slack(graph, 1, 3) == Fraction(0), "Edge (1, 3) should be tight"
    assert imp.slack(graph, 0, 3) == Fraction(60), "Edge (0, 3) should have slack 60"

def test_is_tight():
    graph = VAZIRANI_3
    imp = IMPUTATION_FOR_VAZIRANI_3
    assert imp.is_tight(graph, 0, 2), "Edge (0, 2) should be tight"
    assert imp.is_tight(graph, 1, 3), "Edge (1, 3) should be tight"
    assert not imp.is_tight(graph, 0, 3), "Edge (0, 3) should not be tight"

def test_apply_rotation():
    imp = IMPUTATION_FOR_VAZIRANI_3
    imp.apply_rotation(increasing=frozenset({2}), decreasing=frozenset({0}), delta=Fraction(5))
    assert imp.profits[0] == Fraction(65), "Profit for vertex 0 should decrease by 5"
    assert imp.profits[2] == Fraction(5), "Profit for vertex 2 should increase by 5"
    assert imp.profits[1] == Fraction(0), "Profit for vertex 1 should remain unchanged"
    assert imp.profits[3] == Fraction(100), "Profit for vertex 3 should remain unchanged"