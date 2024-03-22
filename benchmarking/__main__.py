from benchmarking import RandomParams, Benchmark, new_random_benchmark, Solver, new_graph_file_benchmark
import numpy as np

params_code = \
"""
[RandomParams(directed=True, num_vertices=30, average_degree=a) 
	for a in np.arange(1, 4.0, 0.5) for _ in range(3)]
"""
params_list = eval(params_code)

benchmark = new_random_benchmark(params_list, solvers=[
	Solver("brute", "FAST_BOUND"),
	Solver("brute", "BRUTE_FORCE"),
	# Solver("kalp"),
	# Solver("kalp", threads=8),
	# Solver("ilp"),
], params_code = params_code)
# , graph_path="datasets/citation/citation-graph.txt", benchmark_path="benchmarks/citation")

benchmark = Benchmark.load_latest()

print(benchmark.benchmark_path)
benchmark.run(retryFailures=False, timeout=10)