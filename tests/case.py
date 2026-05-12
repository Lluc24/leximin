from dataclasses import dataclass
from typing import Generic, TypeVar
from tests.graphs import NamedBipartiteGraph


TExpected = TypeVar("TExpected")


@dataclass(frozen=True)
class Case(Generic[TExpected]):
	name: str
	graph: NamedBipartiteGraph
	expected: TExpected

