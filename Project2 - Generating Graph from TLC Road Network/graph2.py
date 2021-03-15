import networkx as nx
import matplotlib.pyplot as plt

G=nx.path_graph(4)
pos = nx.spring_layout(G)  # positions for all nodes

cities = {0:"Toronto",1:"London",2:"Berlin",3:"New York"}

H=nx.relabel_nodes(G,cities)
 
print("Nodes of graph: ")
print(H.nodes())
print("Edges of graph: ")
print(H.edges())
nx.draw(H)
nx.draw_networkx_labels(G, pos, cities, font_size=16)

plt.savefig("path_graph_cities.png")
plt.show()