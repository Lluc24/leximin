"""Tests for the essential/viable/subpar classification routine."""

from classification import classify, Classification
from tests.classification_tests.cases_classification import CLASSIFICATION_CASES

def test_returns_classification() -> None:
    case = CLASSIFICATION_CASES[0]
    classification = classify(case.graph)
    assert isinstance(classification, Classification), "Expected classify to return an instance of Classification"

def test_classification_cases_match_expected() -> None:
    for case in CLASSIFICATION_CASES:
        assert classify(case.graph) == case.expected, f"Unexpected classification for case: {case.name}"


def test_essential_vertices_property_matches_essential_parts() -> None:
    for case in CLASSIFICATION_CASES:
        classification = classify(case.graph)
        assert classification.essential_vertices == classification.essential_u | classification.essential_v
