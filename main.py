from graph_gen import GraphGen

def essential_edges(bip):
    essential = set()
    for u, v in bip.max_weight_matching:
        temp_graph = bip.without_edge(u, v)
        if temp_graph.w_max < bip.w_max:
            essential.add((u, v))
    return essential

def viable_edges(bip, essential):
    viable = set()
    non_essential = bip.edges - essential
    for u, v in non_essential:
        w = bip.graph.edges[u, v]['weight']
        temp_graph = bip.without_vertex(u).without_vertex(v)
        if temp_graph.w_max == bip.w_max - w:
            viable.add((u, v))
    return viable

def essential_vertices(bip):
    essential = set()
    for u in bip.vertices:
        temp_graph = bip.without_vertex(u)
        if temp_graph.w_max < bip.w_max:
            essential.add(u)
    return essential

def viable_vertices(viable_edges, essential):
    essential_or_viable = {v for edge in viable_edges for v in edge}
    viable = essential_or_viable - essential
    return viable

def subpar_vertices(bip, essential_edges, viable_edges):
    subpar = bip.vertices
    for u, v in essential_edges | viable_edges:
        subpar -= {u, v}
    return subpar

def main():
    gen = GraphGen(seed=1)
    bip = gen.weighted_bipartite(5, 5)
    print("Max weight matching:", bip.max_weight_matching)
    print("W_max:", bip.w_max)
    all_edges = bip.edges
    print("Edges:", all_edges)
    essential = essential_edges(bip)
    print("Essential edges:", essential)
    non_essential = all_edges - essential
    print("Non-essential edges:", non_essential)
    viable = viable_edges(bip, essential)
    print("Viable edges:", viable)
    essential_vertices_set = essential_vertices(bip)
    print("Essential vertices:", essential_vertices_set)
    viable_vertices_set = viable_vertices(viable, essential_vertices_set)
    print("Viable vertices:", viable_vertices_set)
    subpar = subpar_vertices(bip, essential, viable)
    print("Subpar vertices:", subpar)

if __name__ == "__main__":
    main()
