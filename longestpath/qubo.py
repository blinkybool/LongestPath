from pyqubo import Binary, Array, Num
import numpy as np
from dimod import ExactSolver, BinaryQuadraticModel, RandomSampler
import neal
from typing import List
from longestpath import gen_average_degree_directed, gen_planted_path, StandardGraph, complete_graph
import itertools
from longestpath import brute
import time

# Like bqm.update but with a pyqubo exp and a scalar
def update(bqm, exp, scalar):
	exp_bqm = exp.compile().to_bqm()
	exp_bqm.scale(scalar)
	bqm.update(exp_bqm)

def generate_qubo_bqm(graph: StandardGraph, max_length_path: int | None = None):

	if max_length_path is None:
		max_length_path = graph.vertices-1

	# Variable names closer to mathematical expressions
	N = graph.vertices
	M = max_length_path
	P = -(M+1)

	# The variable V[m][n] will be compiled to its label X[m][n] in the bqm
	# So use V in pyqubo expressions, and X when updating the bqm directly
	X = [[f"X[{m}][{n}]" for n in range(N+1)] for m in range(M+1)]
	V = [[Binary(X[m][n]) for n in range(N+1)] for m in range(M+1)]

	bqm = BinaryQuadraticModel('BINARY')

	# for block in V:
	# 	update(bqm, (sum(block) - Num(1))**2, P)
	
	for m in range(M+1):
		for u in range(N+1):
			for v in range(N+1):
				if u != v:
					bqm.add_quadratic(X[m][u], X[m][v], P)

	for v in range(N):
		for m in range(M):
			for after_m in range(m+1, M+1):
				bqm.add_quadratic(X[m][v], X[after_m][v], P)

	edge_set = set(graph.edges)

	for m in range(M):
		for u in range(N):
			for v in range(N):
				if u == v:
					continue
				
				if (u,v) in edge_set:
					bqm.add_quadratic(X[m][u], X[m+1][v], 1)
				else:
					bqm.add_quadratic(X[m][u], X[m+1][v], P)

	for m in range(M):
		for v in range(N):
			bqm.add_quadratic(X[m][N], X[m+1][v], P)

	return bqm, X

def valid_terminal_path(graph: StandardGraph, terminal_path: List[int]):
	'''
	A terminal path is of the form v1, v2, ..., vn, N, N, N
	where the vi form a valid path, and N = graph.vertices
	(there should not be another valid vertex after the first N)
	'''

	N = graph.vertices

	path = list(itertools.takewhile(lambda v: v < graph.vertices, terminal_path))
	Ntail = itertools.dropwhile(lambda v: v < graph.vertices, terminal_path)

	for v in Ntail:
		if v != N:
			return False, f"Path has invalid edge N={N} -> {v}"
	
	return graph.valid_path(path)

if __name__ == "__main__":

	graph = gen_average_degree_directed(4, 2)
	
	bqm, X = generate_qubo_bqm(graph)

	# sa = neal.SimulatedAnnealingSampler()
	sa = RandomSampler()

	start = time.perf_counter()
	def interrupt():
		e = time.time()
		if (e - start) > 10:
			return True
		return False
	
	bqm.scale(-1)

	sampleset = sa.sample(bqm, num_reads= 100000)
	# sampleset = sa.sample(bqm, num_reads= 100000, interrupt_function= interrupt)

	best_sample = sampleset.first
	multi_path = [[v for v in range(graph.vertices+1) if best_sample.sample[X[m][v]] == 1] for m in range(graph.vertices)]

	print(f"Reward: {-best_sample.energy}")
	print(multi_path)

	for m in range(graph.vertices):
		if len(multi_path[m]) < 1:
			print(f"Path broken at step {m}")
			exit(0)
		if len(multi_path[m]) > 1:
			print(f"Path non-deterministic at step {m}: {multi_path[m]}")
			exit(0)

	terminal_path = [vertices[0] for vertices in multi_path]
	valid, msg = valid_terminal_path(graph, terminal_path)
	if not valid:
		print(msg)
		exit(0)

	path = list(itertools.takewhile(lambda v: v < graph.vertices, terminal_path))

	print(path)
	
	result = brute.solve(graph, "BRUTE_FORCE_COMPLETE")
	if len(result["path"]) > len(path):
		print("Path not longest:")
		print(f"Longest path: {result['path']}")
