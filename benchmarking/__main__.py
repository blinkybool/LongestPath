from benchmarking import RandomParams, RandomBenchmark, Method, new_random_benchmark

# params_list = [RandomParams(True, n, e) for n in [40, 50] for e in [20, 30, 40]]

# benchmark = new_random_benchmark(params_list, [Method.BRUTE_FORCE, Method.FAST_BOUND])

benchmark = RandomBenchmark.load_latest()

print(benchmark.benchmark_path)
benchmark.run(retryFailures=True)