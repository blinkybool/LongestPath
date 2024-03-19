from benchmarking import RandomParams, RandomBenchmark, new_random_benchmark, Solver
from longestpath.brute import Method

params_list = [RandomParams(directed=True, num_vertices=n, average_degree=a) 
								for n in [50] for a in [2,3,4]]

benchmark = new_random_benchmark(params_list, [
	Solver("brute", Method.FAST_BOUND),
	Solver("ilp"),
], override_benchmark_path="benchmarks/test_benchmark")

# benchmark = RandomBenchmark.load("benchmarks/test")

print(benchmark.benchmark_path)
benchmark.run(retryFailures=True)