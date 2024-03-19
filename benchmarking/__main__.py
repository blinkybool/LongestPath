from benchmarking import RandomParams, RandomBenchmark, new_random_benchmark, Solver
from longestpath.brute import Method

params_list = [RandomParams(True, n, e) for n in [40, 50] for e in [20, 30, 40]]

benchmark = new_random_benchmark(params_list, [
    Solver("brute", Method.BRUTE_FORCE),
    Solver("brute", Method.BRANCH_N_BOUND)
])

benchmark = RandomBenchmark.load_latest()

print(benchmark.benchmark_path)
benchmark.run(retryFailures=True)

# def bingbong():
#     return 8

# print(Solver(bingbong, 0, 2).serialise())