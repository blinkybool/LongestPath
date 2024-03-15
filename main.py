import math, random
import numpy as np
from gen import *
from visualize import *


random.seed(3)
np.random.seed(3)

G = DAG(gen_DAG(10, 0.5))

path = G.find_longest_path()

visualize_graph(G.expand(1), path)