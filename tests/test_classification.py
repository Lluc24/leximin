from tests.fixtures.graphs import ALL_GRAPHS
from classification import Classification, classify
import logging

LOGGER = logging.getLogger("tests.classification")

def test_classification():
    for graph in ALL_GRAPHS:
        LOGGER.info("Starting graph case: %s", graph.name)
        expected = graph.classification
        actual = classify(graph)
        LOGGER.info("Graph: %s, Expected: %s", graph.name, expected)
        LOGGER.info("Graph: %s, Actual: %s", graph.name, actual)
        assert actual == expected, f"Classification mismatch for graph {graph.name}: expected {expected}, got {actual}"