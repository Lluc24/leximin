"""Event objects scheduled in the leximin solver priority queue.

Three event types drive the clock-based simulation in ``LeximinSolver``.
Each carries a ``clock`` value (the global clock time at which it fires)
and a fixed ``priority`` used to break ties when two events are scheduled
at the same clock time.

Priority ordering (lower number = higher urgency, processed first):
  1. ``TightEdgeEvent``   — a subpar edge just became tight; must be
     handled before any activation or repair at the same clock so that
     the correct cascade of merges/freezes is applied first (Remark 2
     of Vazirani 2025).
  2. ``BinActivationEvent`` — a BIN component reached the clock level and
     should be moved to ACTIVE before any fully-repaired bookkeeping.
  3. ``FullyRepairedEvent`` — a component has been fully repaired; handled
     last because tight-edge merges may change which component is repaired.
"""

from dataclasses import dataclass, field
from fractions import Fraction
from component import FundamentalComponent, ValidComponent


@dataclass
class BinActivationEvent:
    """Activate a fundamental component when the global clock reaches its minimum profit.

    Fires when ``clock == min_profit(fc)``, i.e., the rising global clock
    has caught up to the smallest profit currently held by any vertex in
    ``fc``.  The handler moves ``fc`` out of BIN and creates a new active
    ``ValidComponent`` with the appropriate rotation direction.
    """

    clock: Fraction
    fc: FundamentalComponent = field(compare=False)
    # Priority 2: processed after tight-edge events but before fully-repaired.
    priority: int = field(default=2, init=False, compare=False)


@dataclass
class FullyRepairedEvent:
    """Finish repairing an active valid component.

    Fires when the ongoing rotation of ``vc`` would equalise the minimum
    profit on both sides of the component.  The handler extracts the
    minimal sub-component (Min-Sub1) that truly reached parity, moves it
    to FULLY-REPAIRED, and returns the remaining fundamental components to
    BIN.
    """

    clock: Fraction
    vc: ValidComponent = field(compare=False)
    # Priority 3: processed last so that tight-edge events can alter the
    # component structure before the repair bookkeeping runs.
    priority: int = field(default=3, init=False, compare=False)


@dataclass
class TightEdgeEvent:
    """Process a newly tight subpar edge incident on an active component.

    Fires at the clock time when ``slack(u, v) == 0`` for a subpar edge
    ``(u, v)`` with one endpoint inside ``source_vc``.  Depending on
    the status of the opposite endpoint (BIN, ACTIVE, FROZEN, or
    FULLY-REPAIRED), the handler either absorbs, merges, or freezes the
    relevant sub-components.
    """

    clock: Fraction
    edge: tuple[int, int]
    source_vc: ValidComponent = field(compare=False)
    # Priority 1: must be handled before activations and repairs at the
    # same clock (see module-level docstring and Remark 2 of Vazirani 2025).
    priority: int = field(default=1, init=False, compare=False)


Event = BinActivationEvent | FullyRepairedEvent | TightEdgeEvent
