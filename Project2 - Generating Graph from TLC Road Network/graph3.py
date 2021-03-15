import networkx as nx
import matplotlib.pyplot as plt

G=nx.Graph()

G.add_node("a")
G.add_nodes_from(["b","c"])

G.add_edge(1,2)
edge = ("d", "e")
G.add_edge(*edge)
edge = ("a", "b")
G.add_edge(*edge)

print("Nodes of graph: ")
print(G.nodes())
print("Edges of graph: ")
print(G.edges())

# adding a list of edges:
G.add_edges_from([("a","c"),("c","d"), ("a",1), (1,"d"), ("a",2)])

#pos = nx.spring_layout(G)  # positions for all nodes


nx.draw(G)
nx.draw_networkx_labels(G)
#nx.draw_networkx_labels(G, pos, font_size=16)

plt.savefig("simple_path.png") # save as png
plt.show() # display