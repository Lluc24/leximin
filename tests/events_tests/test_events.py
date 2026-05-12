"""Tests for event payload fields and queue-priority ordering."""

from events import BinActivationEvent, FullyRepairedEvent, TightEdgeEvent
from tests.events_tests.cases_events import EVENT_CASES


def test_events_expose_expected_payload_and_priority() -> None:
    for case in EVENT_CASES:
        tight = TightEdgeEvent(clock=case.clock, edge=case.edge, source_vc=case.vc)
        activation = BinActivationEvent(clock=case.clock, fc=case.fc)
        repaired = FullyRepairedEvent(clock=case.clock, vc=case.vc)

        assert tight.clock == case.clock
        assert tight.edge == case.edge
        assert tight.source_vc == case.vc
        assert tight.priority == 1

        assert activation.clock == case.clock
        assert activation.fc == case.fc
        assert activation.priority == 2

        assert repaired.clock == case.clock
        assert repaired.vc == case.vc
        assert repaired.priority == 3


def test_event_priority_order_matches_solver_queue_contract() -> None:
    case = EVENT_CASES[0]
    ordered = sorted(
        [
            (FullyRepairedEvent(case.clock, case.vc).clock, FullyRepairedEvent(case.clock, case.vc).priority),
            (BinActivationEvent(case.clock, case.fc).clock, BinActivationEvent(case.clock, case.fc).priority),
            (TightEdgeEvent(case.clock, case.edge, case.vc).clock, TightEdgeEvent(case.clock, case.edge, case.vc).priority),
        ]
    )
    assert ordered == [(case.clock, 1), (case.clock, 2), (case.clock, 3)]
