import math, random
import numpy as np
from gen import *
from visualize import *


random.seed(3)
np.random.seed(3)

G = DAG(gen_DAG(10, 0.5))
print(G.graph)
print(G.lower_topo_sorting)
print(G.upper_topo_sorting)
print(G.find_longest_path())

path = G.find_longest_path()

visualize_graph(G.graph, zip(path, path[1:]))