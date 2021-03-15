import matplotlib.pyplot as plt
import networkx as nx

G = nx.Graph()


G.add_edge("a", "b", weight=0.9)
G.add_edge("a", "c", weight=0.9)
G.add_edge("c", "d", weight=0.9)
G.add_edge("c", "e", weight=0.9)
G.add_edge("c", "f", weight=0.9)
G.add_edge("a", "d", weight=0.9)
G.add_edge("a", "f", weight=0.9)

edgeList_ = [(u, v) for (u, v, d) in G.edges(data=True)]

#elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] > 0.5]
#esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] <= 0.5]

pos = nx.spring_layout(G)  # positions for all nodes

# nodes
nx.draw_networkx_nodes(G, pos, node_size=700)

# edges
nx.draw_networkx_edges(G, pos, edgelist=edgeList_, width=6)

# labels
nx.draw_networkx_labels(G, pos, font_size=20, font_family="sans-serif")

plt.axis("off")
plt.show()