"""Table-driven cases for solver event dataclasses."""

from dataclasses import dataclass
from fractions import Fraction

from components import FundamentalComponent, ValidComponent
from tests.case import Case
from tests.graphs import SAMPLE_GRAPH


@dataclass(frozen=True)
class EventCase(Case[tuple[int, str]]):
    """Case for event payload and priority checks."""

    clock: Fraction
    fc: FundamentalComponent
    vc: ValidComponent
    edge: tuple[int, int]


FC = FundamentalComponent(0, 2)
VC = ValidComponent(root=FC, rotation="CW")


EVENT_CASES: tuple[EventCase, ...] = (
    EventCase(
        name="event_defaults",
        graph=SAMPLE_GRAPH,
        clock=Fraction(3, 2),
        fc=FC,
        vc=VC,
        edge=(0, 2),
        expected=(1, "priority_order_tight_before_bin_before_repaired"),
    ),
)
