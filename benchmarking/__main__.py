from benchmarking import RandomParams, RandomBenchmark, new_random_benchmark, Solver
from longestpath.brute import Method

params_list = [RandomParams(directed=True, num_vertices=n, average_degree=a) 
								for n in [30] for a in [2,3]]

# benchmark = new_random_benchmark(params_list, [
# 	Solver("brute", "FAST_BOUND"),
# 	Solver("brute", "BRUTE_FORCE"),
# 	Solver("ilp"),
# ], override_benchmark_path="benchmarks/test_benchmark")

benchmark = RandomBenchmark.load("benchmarks/test_benchmark")

print(benchmark.benchmark_path)
benchmark.run(retryFailures=True, timeout=5)