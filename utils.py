from matplotlib import pyplot as plt
import networkx as nx

def plot_bipartite(B):
    pos = nx.bipartite_layout(B)
    nx.draw(B, pos=pos, with_labels=True)
    plt.show()