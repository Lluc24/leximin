from dataclasses import dataclass, field
from fractions import Fraction
from components import FundamentalComponent, ValidComponent


@dataclass
class BinActivationEvent:
    clock: Fraction
    fc: FundamentalComponent = field(compare=False)
    priority: int = field(default=2, init=False, compare=False)

@dataclass
class FullyRepairedEvent:
    clock: Fraction
    vc: ValidComponent = field(compare=False)
    priority: int = field(default=3, init=False, compare=False)

@dataclass
class TightEdgeEvent:
    clock: Fraction
    edge: tuple[int, int] = field(compare=False)
    source_vc: ValidComponent = field(compare=False)
    priority: int = field(default=1, init=False, compare=False)


Event = BinActivationEvent | FullyRepairedEvent | TightEdgeEvent