from networkx import bipartite
import networkx as nx
import matplotlib.pyplot as plt
from scipy.optimize import linear_sum_assignment

class Bipartite():
    def __init__(self, graph):
        self.graph = graph
        self.top, self.bottom = bipartite.sets(graph)
        self.adj_matrix = bipartite.biadjacency_matrix(self.graph, self.top).toarray()
        self.max_weight_matching = self._max_weight_matching()
        self.w_max = self._w_max()

    def _max_weight_matching(self):
        row_ind, col_ind = linear_sum_assignment(-self.adj_matrix)
        max_weight_matching = list(zip(map(int, row_ind), map(int, col_ind + len(self.top))))
        return max_weight_matching

    def _w_max(self):
        w_max = 0
        for u, v in self.max_weight_matching:
            w_max += self.adj_matrix[u, v - len(self.top)]
        return w_max

    def plot(self):
        pos = nx.bipartite_layout(self.graph)
        nx.draw(self.graph, pos=pos, with_labels=True)
        weights = nx.get_edge_attributes(self.graph, 'weight')
        if weights:
            nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=weights)
        plt.show()

