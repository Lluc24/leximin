import logging
from matching import MaxWeightMatcher
from tests.cases_mwm import MWM_CASES, build_graph


LOGGER = logging.getLogger("tests.mwm")


def test_compute_returns_frozenset() -> None:
    case = MWM_CASES[0]
    graph = build_graph(case)
    matching = MaxWeightMatcher().compute(graph)
    assert isinstance(matching, frozenset)


def test_cases_have_expected_mwm() -> None:
    matcher = MaxWeightMatcher()

    for case in MWM_CASES:
        graph = build_graph(case)
        matching = matcher.compute(graph)
        LOGGER.info(
            "case=%s expected=%s computed=%s",
            case.name,
            sorted(case.expected_mwm),
            sorted(matching),
        )
        assert matching == case.expected_mwm, f"Unexpected matching for case: {case.name}"

