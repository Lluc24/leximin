import numpy as np
from networkx.algorithms import bipartite
from bipartite import Bipartite

class GraphGen:
    def __init__(self, seed=None):
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def weighted_bipartite(self, n, m, density=0.5, weight_range=(1, 10)):
        bip = bipartite.random_graph(n, m, density, seed=self.seed)
        for u, v in bip.edges():
            bip.edges[u, v]['weight'] = self.rng.integers(weight_range[0], weight_range[1] + 1)
        top, bottom = bipartite.sets(bip)
        return Bipartite(bip, top, bottom)

