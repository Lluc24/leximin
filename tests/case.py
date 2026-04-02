from dataclasses import dataclass
from fractions import Fraction
from typing import Generic, TypeVar

from graph import BipartiteGraph


TExpected = TypeVar("TExpected")


@dataclass(frozen=True)
class Case(Generic[TExpected]):
	name: str
	n_u: int
	n_v: int
	weighted_edges: tuple[tuple[int, int, Fraction], ...]
	expected: TExpected

	def build_graph(self) -> BipartiteGraph:
		u_vertices = frozenset(range(self.n_u))
		v_vertices = frozenset(range(self.n_u, self.n_u + self.n_v))
		weights = {(u, v): Fraction(w) for (u, v, w) in self.weighted_edges}
		return BipartiteGraph(u_vertices=u_vertices, v_vertices=v_vertices, weights=weights)


