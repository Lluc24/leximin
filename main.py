from graph_gen import GraphGen

if __name__ == "__main__":
    gen = GraphGen(seed=1)
    bip = gen.weighted_bipartite(5, 5)
    print(bip.max_weight_matching)
    print(bip.w_max)
    bip.plot()
