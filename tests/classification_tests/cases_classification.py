"""Table-driven cases for graph classification tests."""

from classification import Classification
from tests.case import Case
from tests.graphs import (
    ALL_ONES_2X2_GRAPH,
    CLASSIFICATION_SINGLE_U_TWO_V_ALL_VIABLE_GRAPH,
    CLASSIFICATION_SINGLE_U_TWO_V_WITH_DELTA_DIFFERENCE_GRAPH,
)


ClassificationCase = Case[Classification]

CLASSIFICATION_CASES: tuple[ClassificationCase, ...] = (
    ClassificationCase(
        name="single_u_two_v_all_viable",
        graph=CLASSIFICATION_SINGLE_U_TWO_V_ALL_VIABLE_GRAPH,
        expected=Classification(
            essential_u=frozenset({0}),
            viable_v=frozenset({1, 2}),
            viable_edges=frozenset({(0, 1), (0, 2)}),
        ),
    ),
    ClassificationCase(
        name="single_u_two_v_with_delta_difference",
        graph=CLASSIFICATION_SINGLE_U_TWO_V_WITH_DELTA_DIFFERENCE_GRAPH,
        expected=Classification(
            essential_u=frozenset({0}),
            essential_v=frozenset({2}),
            subpar_v=frozenset({1}),
            essential_edges=frozenset({(0, 2)}),
            subpar_edges=frozenset({(0, 1)})
        ),
    ),
    ClassificationCase(
        name="two_u_two_v_all_essential",
		graph=ALL_ONES_2X2_GRAPH,
        expected=Classification(
            essential_u=frozenset({0, 1}),
            essential_v=frozenset({2, 3}),
            viable_edges=frozenset({(0, 2), (0, 3), (1, 2), (1, 3)}),
        ),
    )
)
