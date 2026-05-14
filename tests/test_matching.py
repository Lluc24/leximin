from tests.fixtures.graphs import ALL_GRAPHS
import logging
from matching import max_weight_matching

LOGGER = logging.getLogger("test_matching")

def test_max_weight_matching():
    for graph in ALL_GRAPHS:
        expected_mwm = graph.matching
        computed_mwm = max_weight_matching(graph.weights)
        LOGGER.info("Graph %s: expected MWM weight %s", graph.name, expected_mwm.weight)
        LOGGER.info("Graph %s: computed MWM weight %s", graph.name, computed_mwm.weight)
        assert computed_mwm.weight == expected_mwm.weight, f"Expected weight {expected_mwm.weight} but got {computed_mwm.weight} for graph {graph.name}"
        if graph.degenerate:
            if expected_mwm == computed_mwm:
                LOGGER.info("Graph %s: Despite degeneracy, computed MWM matches expected %s", graph.name, expected_mwm.matching)
            else:
                LOGGER.info("Graph %s: Degenerate case, expected MWM %s, computed %s", graph.name, expected_mwm.matching, computed_mwm.matching)
        else:
            LOGGER.info("Graph %s: expected MWM matching %s", graph.name, expected_mwm.matching)
            LOGGER.info("Graph %s: computed MWM matching %s", graph.name, computed_mwm.matching)
            assert computed_mwm.matching == expected_mwm.matching, f"Expected MWM {expected_mwm.matching} but got {computed_mwm.matching} for graph {graph.name}"

