from longestpath import brute, anneal, ilp, qubo, qubo_edge
from longestpath.gen import gen_num_edges, gen_planted_hamiltonian_undirected_fixed_degree, gen_planted_path
from longestpath import StandardGraph
from longestpath.utils import with_timed_result

# Random graph generation
N = 30
d = 1.4
graph = gen_num_edges(N, round(N * d))

# From file
# graph = StandardGraph.from_file("graph.txt")

def pretty_result(result):
    if "failure" in result or 'path' not in result:
        return str(result)
    return f'run_time={result["run_time"]:0.6f} (s), length={len(result["path"])-1}, path={" ".join(str(i) for i in result["path"])}'

# Brute force
# Methods: 'BRUTE_FORCE' | 'BRANCH_N_BOUND' | 'FAST_BOUND' | 'BRUTE_FORCE_COMPLETE'
method: brute.Method = 'BRANCH_N_BOUND'
result = brute.solve(graph, method)
print(f'Brute force: {pretty_result(result)}')

# Other methods may use this if they are told to halt early when they find a path of this length
graph.set_known_longest_path_length(len(result["path"])-1)

# Simulated Annealing
result = with_timed_result(anneal.solve)(graph, num_reads=100, num_sweeps=32)
print(f'Simulated Annealing: {pretty_result(result)}')

# Integer Linear Programming
max_path_length = N-1
result = with_timed_result(ilp.solve)(graph, max_path_length=max_path_length)
print(f'Integer Linear Programming: {pretty_result(result)}')

# QUBO
max_path_length = N-1
solver = qubo.QUBOSolver(graph, max_length_path=max_path_length)
min_beta, max_beta = solver.get_default_beta_range()
result = with_timed_result(solver.solve)(num_reads=1000, num_sweeps=100, beta_range=(0.1, 0.5*max_beta))
del result['sampleset_info'], result['energies']
print(f'QUBO: {pretty_result(result)}')

# QUBO edge
max_path_length = N-1
solver = qubo_edge.QUBO_Edge_Solver(graph, max_path_length)
min_beta, max_beta = solver.get_default_beta_range()
result = with_timed_result(solver.solve)(num_reads=1000, num_sweeps=100, beta_range=(0.1, 0.5*max_beta))
print(f'QUBO edge: {pretty_result(result)}')