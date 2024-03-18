from longestpath import gen_num_edges
from longestpath import brute

if __name__ == "__main__":
	graph = gen_num_edges(10, 15)
	result = brute.solve(graph, brute.Method.BRUTE_FORCE)
	print(result)