from longestpath import gen_num_edges, gen_random_edges_average_degree_directed
from longestpath import brute
import numpy as np

graphs = [gen_random_edges_average_degree_directed(1000, 1) for _ in range(10)]
results = [brute.solve(graph, "BRUTE_FORCE") for graph in graphs]
lengths = [len(result["path"])-1 for result in results]
run_times = [result["run_time"] for result in results]
print(np.min(lengths), np.mean(lengths), np.max(lengths))
print(np.min(run_times), np.mean(run_times), np.max(run_times))