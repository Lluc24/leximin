"""Generic test-case container used by table-driven tests."""

from dataclasses import dataclass
from typing import Generic, TypeVar

from tests.graphs import NamedBipartiteGraph


TExpected = TypeVar("TExpected")


@dataclass(frozen=True)
class Case(Generic[TExpected]):
    """Base test case with graph input and expected output."""

    name: str
    graph: NamedBipartiteGraph
    expected: TExpected
