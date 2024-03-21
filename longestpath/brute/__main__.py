from longestpath import gen_num_edges
from longestpath import brute

if __name__ == "__main__":
	graph = gen_num_edges(40, 20)
	result = brute.solve(graph, brute.Method.FAST_BOUND)
	print(result)