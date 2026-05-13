"""Immutable bipartite graph model with weighted edges."""

from fractions import Fraction
from dataclasses import dataclass
import matplotlib.pyplot as plt
import networkx as nx

@dataclass(frozen=True)
class BipartiteGraph:
    """Bipartite graph with integer-labeled vertices and rational edge weights."""

    u_vertices: frozenset[int]  # IDs 0 to n_u - 1
    v_vertices: frozenset[int]  # IDs n_u to n_v - 1
    weights: dict[tuple[int, int], Fraction]  # (u, v) -> weight

    def neighbors_of(self, vertex: int) -> frozenset[int]:
        """Return all neighbors of `vertex` on the opposite side of the bipartition."""
        if vertex in self.u_vertices:
            return frozenset(v for u, v in self.weights if u == vertex)
        elif vertex in self.v_vertices:
            return frozenset(u for u, v in self.weights if v == vertex)
        else:
            raise ValueError(f"Vertex {vertex} is not in the graph.")

    def weight(self, u: int, v: int) -> Fraction:
        """Return edge weight, defaulting to zero for missing edges."""
        if (u, v) in self.weights:
            return self.weights[(u, v)]
        else:
            return Fraction(0)  # No edge means weight 0

    @property
    def edges(self) -> frozenset[tuple[int, int]]:
        """Return all explicit edges."""
        return frozenset(self.weights.keys())

    @property
    def vertices(self) -> frozenset[int]:
        """Return all vertices across both sides."""
        return frozenset(self.u_vertices) | set(self.v_vertices)

    @property
    def weighted_edges(self) -> frozenset[tuple[int, int, Fraction]]:
        """Return all edges together with their weights."""
        return frozenset((u, v, w) for (u, v), w in self.weights.items())

    def __add__(self, other: tuple[int, int, Fraction]) -> 'BipartiteGraph':
        """Returns a new graph with the given edge added."""
        u, v, w = other
        if u not in self.u_vertices or v not in self.v_vertices:
            raise ValueError(f"Vertices {u} and {v} must be in the graph.")
        new_weights = self.weights.copy()
        new_weights[(u, v)] = w
        return BipartiteGraph(
            u_vertices=self.u_vertices,
            v_vertices=self.v_vertices,
            weights=new_weights
        )

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

    def add_vertex_to_u(self, vertex: int) -> 'BipartiteGraph':
        """Returns a new graph with the given vertex added to U."""
        if vertex in self.u_vertices or vertex in self.v_vertices:
            raise ValueError(f"Vertex {vertex} already exists in the graph.")
        new_u_vertices = self.u_vertices | frozenset({vertex})
        return BipartiteGraph(
            u_vertices=new_u_vertices,
            v_vertices=self.v_vertices,
            weights=self.weights
        )

    def add_vertex_to_v(self, vertex: int) -> 'BipartiteGraph':
        """Returns a new graph with the given vertex added to V."""
        if vertex in self.u_vertices or vertex in self.v_vertices:
            raise ValueError(f"Vertex {vertex} already exists in the graph.")
        new_v_vertices = self.v_vertices | frozenset({vertex})
        return BipartiteGraph(
            u_vertices=self.u_vertices,
            v_vertices=new_v_vertices,
            weights=self.weights
        )

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
                g, pos, edge_labels=weights, label_pos=0.1
            )
        plt.show()
