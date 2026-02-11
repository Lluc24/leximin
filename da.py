import networkx as nx
from networkx.algorithms import bipartite
from utils import plot_bipartite
import numpy as np

def deferred_acceptance(B):
    workers, firms = bipartite.sets(B)
    if len(workers) != len(firms):
        raise ValueError("The number of workers and firms must be equal.")
    rejection = True
    while rejection:
        rejection = False
        for f in firms:
            proposals = [w for w in workers if B.nodes[w]["checklist"][0] == f]
            if proposals:
                best = min(proposals, key=lambda w: B.nodes[f]["prefs"].tolist().index(w))
                for w in proposals:
                    if w != best:
                        rejection = True
                        B.nodes[w]["checklist"] = np.delete(B.nodes[w]["checklist"], 0)
    return {w: int(B.nodes[w]["checklist"][0]) for w in workers}

if __name__ == "__main__":
    rng = np.random.default_rng(seed=1)
    B = bipartite.random_graph(10, 10, 1, seed=1)
    # plot_bipartite(B)
    for n in B.nodes():
        B.nodes[n]["prefs"] = rng.permutation(list(B.neighbors(n)))
        B.nodes[n]["checklist"] = B.nodes[n]["prefs"].copy()
    matching = deferred_acceptance(B)
    print("Final matching:", matching)


