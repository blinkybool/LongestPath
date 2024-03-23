from pyqubo import Binary, Array, Num
import numpy as np
from dimod import ExactSolver, BinaryQuadraticModel
import neal
from longestpath import gen_average_degree_directed, gen_planted_path, StandardGraph, complete_graph
import itertools
from collections import defaultdict
import time

# Like bqm.update but with a pyqubo exp and a scalar
def update(bqm, exp, scalar):
	exp_bqm = exp.compile().to_bqm()
	exp_bqm.scale(scalar)
	bqm.update(exp_bqm)

def generate_qubo_bqm(graph: StandardGraph, max_length_path: int | None = None):

	if max_length_path is None:
		max_length_path = graph.vertices

	# Variable names closer to mathematical expressions
	N = graph.vertices
	M = max_length_path
	P = -(M+1)

	# The variable V[m][n] will be compiled to its label X[m][n] in the bqm
	# So use V in pyqubo expressions, and X when updating the bqm directly
	X = [[f"X[{m}][{n}]" for n in range(N+1)] for m in range(M+1)]
	V = [[Binary(X[m][n]) for n in range(N+1)] for m in range(M+1)]

	bqm = BinaryQuadraticModel('BINARY')

	for block in V:
		update(bqm, (sum(block) - Num(1))**2, P)

	for v in range(N):
		for m in range(M):
			for after_m in range(m+1, M+1):
				bqm.add_quadratic(X[m][v], X[after_m][v], P)

	edge_set = set(graph.edges)

	for m in range(M):
		for i in range(N):
			for j in range(N):
				if i == j:
					continue
				
				if (min(i,j), max(i,j)) in edge_set:
					bqm.add_quadratic(X[m][i], X[m+1][j], 1)
				else:
					bqm.add_quadratic(X[m][i], X[m+1][j], P)

	for m in range(M):
		for v in range(N):
			bqm.add_quadratic(X[m][N], X[m+1][v], P)

	return bqm, X

if __name__ == "__main__":

	graph = gen_average_degree_directed(10, 2)
	# Make it undirected
	inv_edges = [(j,i) for (i, j) in graph.edges]
	graph.edges = list(set(graph.edges + inv_edges))
	
	bqm, X = generate_qubo_bqm(graph)

	sa = neal.SimulatedAnnealingSampler()

	start = time.perf_counter()
	def interrupt():
		e = time.time()
		if (e - start) > 10:
			return True
		return False
	
	bqm.scale(-1)

	sampleset = sa.sample(bqm, num_reads= 100, num_sweeps= 1000, interrupt_function= interrupt)

	best_sample = sampleset.first
	multi_path = [[v for v in range(graph.vertices+1) if best_sample.sample[X[m][v]] == 1] for m in range(graph.vertices+1)]
	
	# Not actually a comprehensive check
	if not all(len(multi_path[m]) == 1 for m in range(graph.vertices+1)):
		print("fail")

	path = list(itertools.takewhile(lambda v: v < graph.vertices, [vertices[0] for vertices in multi_path]))

	print(-best_sample.energy, path)

	for (i,j) in zip(path, path[1:]):
		if (i,j) not in graph.edges:
			print(f"bad path, no edge {i} {j}")
			exit(0)
	print("valid path")
