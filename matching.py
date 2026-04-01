from graph import BipartiteGraph
import networkx as nx
from networkx.algorithms import max_weight_matching
from itertools import product

class MaxWeightMatcher:
    def compute(self, graph: BipartiteGraph) -> frozenset[tuple[int, int]]:
        """
        Returns the unique MWM as a frozenset of (u, v) pairs.
        Wraps NetworkX's max_weight_matching.
        Non-degenerate assumption: the MWM is unique.
        """
        bip = nx.Graph()
        e = [(u, v, float(graph.weight(u, v))) for (u, v) in product(graph.u_vertices, graph.v_vertices)]
        bip.add_weighted_edges_from(e)
        m = max_weight_matching(bip)
        m = [(u, v) if u in graph.u_vertices else (v, u) for (u, v) in m]
        m.sort()
        return frozenset(m)