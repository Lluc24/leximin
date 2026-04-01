from fractions import Fraction
from dataclasses import dataclass

@dataclass
class BipartiteGraph:
    u_vertices: frozenset[int]  # IDs 0 to n_u - 1
    v_vertices: frozenset[int]  # IDs n_u to n_v - 1
    weights: dict[tuple[int,int], Fraction]  # (u, v) -> weight

    def neighbors_of(self, vertex: int) -> list[int]:
        """All neighbors of vertex across the bipartition."""
        if vertex in self.u_vertices:
            return [v for (u, v) in self.weights if u == vertex]
        elif vertex in self.v_vertices:
            return [u for (u, v) in self.weights if v == vertex]
        else:
            raise ValueError(f"Vertex {vertex} is not in the graph.")

    def weight(self, u: int, v: int) -> Fraction:
        if (u, v) in self.weights:
            return self.weights[(u, v)]
        else:
            return Fraction(0) # No edge means weight 0

    def all_edges(self) -> list[tuple[int, int]]:
        return list(self.weights.keys())