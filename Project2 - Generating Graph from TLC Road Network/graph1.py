import networkx as nx
import matplotlib.pyplot as plt


G = nx.path_graph(5)
pos = nx.spring_layout(G)  # positions for all nodes

# nodes
options = {"node_size": 500, "alpha": 0.8}
nx.draw_networkx_nodes(G, pos, nodelist=[0, 1, 2, 3, ], node_color="r", **options)

# edges
nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
nx.draw_networkx_edges(
    G,
    pos,
    edgelist=[(0, 1), (1, 2), (2, 3), (3, 0)],
    width=8,
    alpha=0.5,
    edge_color="r",
)

# some math labels
labels = {}
labels[0] = r"$a$"
labels[1] = r"$b$"
labels[2] = r"$c$"
labels[3] = r"$d$"

nx.draw_networkx_labels(G, pos, font_size=16)

#nx.draw_networkx_labels(G, pos, labels, font_size=16)

plt.axis("off")
plt.show()
