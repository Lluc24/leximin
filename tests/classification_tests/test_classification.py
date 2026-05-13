"""Tests for the essential/viable/subpar classification routine."""
import logging
from classification import classify, Classification
from tests.graphs import TestBipartiteGraph, HANDMADE_GRAPH

LOGGER = logging.getLogger("tests.classification")

GRAPHS: tuple[TestBipartiteGraph, ...] = (
    HANDMADE_GRAPH,
)

def test_returns_classification() -> None:
    graph = GRAPHS[0]
    classification = classify(graph)
    assert isinstance(classification, Classification), "Expected classify to return an instance of Classification"

def test_classification_cases_match_expected() -> None:
    for graph in GRAPHS:
        expected = graph.classification
        classification = classify(graph)
        LOGGER.info("Testing graph %s: computed classification %s", graph.name, classification)
        LOGGER.info("Testing graph %s: expected classification %s", graph.name, expected)
        assert classify(graph) == expected, f"Unexpected classification for case: {graph.name}"
