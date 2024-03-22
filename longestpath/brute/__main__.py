from longestpath import gen_num_edges, gen_average_degree_directed
from longestpath import brute

graph = gen_average_degree_directed(20, 7)
result = brute.solve(graph, "FAST_BOUND")
print(result)
print(len(result["path"]))