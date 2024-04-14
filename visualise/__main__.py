from visualise import serve_benchmark_visualiser, serve_simulated_annealing_visualiser
from benchmarking import Benchmark
from longestpath import gen_num_edges, gen_num_edges_undirected
from longestpath.anneal import recorded_anneal, compute_inserts
import itertools
from longestpath import brute, StandardGraph

# benchmark = Benchmark.load("benchmarks/qubo_known/2")
# serve_benchmark_visualiser(benchmark)

n = 40
d = 1.2

# while True:

#     graph = gen_num_edges_undirected(n, round(n*d))

#     if graph.is_connected():
#         break

with open("visualise/sim-anneal-graph-1.txt", "r") as f:
    graph = StandardGraph.from_string(f.read())

longest_path = brute.solve(graph, "BRANCH_N_BOUND")["path"]

runs = []
max_length = 0
while max_length < len(longest_path) - 1:
    events = recorded_anneal(set(graph.edges), compute_inserts(graph), alpha=0.9, initial_temp=1, final_temp=0.33, num_sweeps=10)
    max_length = max(len(e['path'])-1 for e in events)
    # first_max_index = next(i for i, e in enumerate(events) if len(e['path'])-1 == max_length)
    # events = events[:first_max_index+1]
    runs.append(events)

runs = runs[-30:]

# with open("visualiser-graph.txt", "w") as f:
#     f.write(str(graph))

serve_simulated_annealing_visualiser(graph, runs)