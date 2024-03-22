from benchmarking import RandomParams, Benchmark, new_random_benchmark, Solver, new_graph_file_benchmark
import numpy as np

# params_code = "[RandomParams(directed=True, num_vertices=50, average_degree=a) for a in np.arange(1, 8.5, 0.5) for _ in range(3)]"
# params_list = eval(params_code)

benchmark = new_graph_file_benchmark(solvers=[
	Solver("brute", "FAST_BOUND"),
], graph_path="datasets/citation/citation-graph.txt", benchmark_path="benchmarks/citation")

# benchmark = Benchmark.load_latest()

print(benchmark.benchmark_path)
benchmark.run(retryFailures=True)