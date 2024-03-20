from benchmarking import RandomParams, Benchmark, new_random_benchmark, Solver, new_graph_file_benchmark
import inspect
import pickle

params_list = [RandomParams(directed=True, num_vertices=n, average_degree=a) 
								for n in [100] for a in [0.5,0.75,1, 1.5, 2]]

benchmark = new_random_benchmark(params_list, [
	Solver("brute", "FAST_BOUND"),
	# Solver("brute", "BRUTE_FORCE"),
	Solver("ilp"),
])

# benchmark = Benchmark.load_latest()

# benchmark = new_graph_file_benchmark(
#     "datasets/rob-top/rob-top2000-graph.txt",
# 	[Solver("brute", "FAST_BOUND"), Solver("brute", "BRUTE_FORCE")],
#     "benchmarks/rob-top-2000")

print(benchmark.benchmark_path)
benchmark.run(retryFailures=True, timeout=20)