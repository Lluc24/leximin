"""Immutable bipartite graph model with weighted edges."""
import pathlib
from fractions import Fraction
from dataclasses import dataclass
from itertools import product

import matplotlib.pyplot as plt
import networkx as nx
from matching import max_weight_matching
from utils import subsets


@dataclass(frozen=True)
class BipartiteGraph:
    """Bipartite graph with integer-labeled vertices and rational edge weights."""

    u_vertices: frozenset[int]  # IDs 0 to n_u - 1
    v_vertices: frozenset[int]  # IDs n_u to n_v - 1
    weights: dict[tuple[int, int], Fraction]  # (u, v) -> weight

    @property
    def vertices(self) -> frozenset[int]:
        """Return all vertices in the graph."""
        return self.u_vertices | self.v_vertices

    @property
    def edges(self) -> frozenset[tuple[int, int]]:
        """Return all edges in the graph."""
        return frozenset(self.weights.keys())

    @property
    def weighted_edges(self) -> frozenset[tuple[int, int, Fraction]]:
        """Return all edges with their weights."""
        return frozenset((u, v, w) for (u, v), w in self.weights.items())

    def neighbors_of(self, vertex: int) -> frozenset[int]:
        """Return all neighbors of `vertex` on the opposite side of the bipartition."""
        if vertex in self.u_vertices:
            return frozenset(v for u, v in self.weights if u == vertex)
        elif vertex in self.v_vertices:
            return frozenset(u for u, v in self.weights if v == vertex)
        else:
            raise ValueError(f"Vertex {vertex} is not in the graph.")

    def __sub__(self, other: tuple[int, int] | int) -> 'BipartiteGraph':
        """Return a new graph with one edge or one vertex removed."""
        if isinstance(other, tuple) and len(other) == 2:
            u, v = other
            if (u, v) not in self.weights:
                raise ValueError(f"Edge ({u}, {v}) does not exist in the graph.")
            new_weights = self.weights.copy()
            del new_weights[(u, v)]
            return BipartiteGraph(
                u_vertices=self.u_vertices,
                v_vertices=self.v_vertices,
                weights=new_weights
            )
        elif isinstance(other, int):
            vertex = other
            if vertex not in self.u_vertices and vertex not in self.v_vertices:
                raise ValueError(f"Vertex {vertex} does not exist in the graph.")
            new_u_vertices = self.u_vertices - frozenset({vertex})
            new_v_vertices = self.v_vertices - frozenset({vertex})
            new_weights = {edge: w for edge, w in self.weights.items() if vertex not in edge}
            return BipartiteGraph(
                u_vertices=new_u_vertices,
                v_vertices=new_v_vertices,
                weights=new_weights
            )
        else:
            raise ValueError("Invalid operand for subtraction. Must be an edge tuple or a vertex ID.")

    def plot(self) -> None:
        """Plot the bipartite graph using NetworkX layout."""
        g = nx.Graph()
        g.add_nodes_from(self.u_vertices, bipartite=0)
        g.add_nodes_from(self.v_vertices, bipartite=1)
        for (u, v), w in self.weights.items():
            g.add_edge(u, v, weight=w)

        plt.figure(figsize=(8, 6))
        pos = nx.bipartite_layout(g, self.u_vertices)
        nx.draw(g, pos=pos, with_labels=True)
        weights = nx.get_edge_attributes(g, 'weight')
        if weights:
            nx.draw_networkx_edge_labels(
                g, pos, edge_labels=weights, label_pos=0.15
            )
        plt.show()

    def is_imputation_in_core(self, profits: dict[int, Fraction]) -> bool:
        """Assert that every coalition receives at least its matching value."""
        for coalition in subsets(self.vertices):
            coalition_set = frozenset(coalition)
            coalition_u = self.u_vertices.intersection(coalition_set)
            coalition_v = self.v_vertices.intersection(coalition_set)
            # Coalition value is evaluated on the induced bipartite subgraph.
            weights={
                (u, v): self.weights[(u, v)]
                for u, v in product(coalition_u, coalition_v)
                if (u, v) in self.weights
            }
            coalition_value = max_weight_matching(weights).weight
            coalition_profit = sum((profits[v] for v in coalition_set), Fraction(0))
            if coalition_profit < coalition_value:
                return False
        return True

    def save(self, path: str | pathlib.Path) -> None:
        """Save the graph to a JSON file."""
        import json
        data = {
            "u_vertices": list(self.u_vertices),
            "v_vertices": list(self.v_vertices),
            "weights": {f"{u},{v}": str(w) for (u, v), w in self.weights.items()}
        }
        with open(path, "w") as f:
            json.dump(data, f)
