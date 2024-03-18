from benchmarking import RandomParams, RandomBenchmark, Method

params_list = [RandomParams(True, n, e) for n in [40, 50] for e in [20, 30, 40]]

benchmark = RandomBenchmark(params_list, [Method.BRUTE_FORCE, Method.FAST_BOUND])

benchmark.run()