"""Event objects scheduled in the leximin solver priority queue."""

from dataclasses import dataclass, field
from fractions import Fraction
from component import FundamentalComponent, ValidComponent


@dataclass
class BinActivationEvent:
    """Activate a fundamental component at the given clock time."""

    clock: Fraction
    fc: FundamentalComponent = field(compare=False)
    priority: int = field(default=2, init=False, compare=False)

@dataclass
class FullyRepairedEvent:
    """Finish repairing an active valid component."""

    clock: Fraction
    vc: ValidComponent = field(compare=False)
    priority: int = field(default=3, init=False, compare=False)

@dataclass
class TightEdgeEvent:
    """Process a newly tight subpar edge touching an active component."""

    clock: Fraction
    edge: tuple[int, int] = field(compare=False)
    source_vc: ValidComponent = field(compare=False)
    priority: int = field(default=1, init=False, compare=False)


Event = BinActivationEvent | FullyRepairedEvent | TightEdgeEvent
