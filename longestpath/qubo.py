from pyqubo import Binary, Array, Num
import numpy as np
from dimod import ExactSolver
import neal
from longestpath import gen_average_degree_directed, gen_planted_path, StandardGraph
from collections import defaultdict
import time


def doit():

	N = 100
	M = N
	P = -(M+1)

	graph = gen_average_degree_directed(100, 5)

	offset = 0
	Q = defaultdict(int)

	start = time.perf_counter()
	# P * sum_v=1^N (1 - sum_i=1^M x_i^v)^2
	for v in range(N+1):
		# Constant
		offset += P
		for v in range(M+1):
			# Linear 
			Q[((v,v),(v,v))] += - P
			# Quadratic
			for u in range(v+1, M+1):
				Q[((v,v),(u,v))] += 2 * P

	end = time.perf_counter()

	print(f"Done with serial_exp : Took {end - start} seconds")

	start = time.time()

	for v in range(N):
		# print(f"{v} / {N-1}")
		for u in range(M):
			for j in range(u+1, M+1):
				Q[((u,v), (j,v))] += P

	end = time.time()

	print(f"Done with no_repeatblocks_exp : Took {end - start} seconds")

	edge_set = set(graph.edges)

	start = time.time()
	for m in range(M):
		for v in range(N):
			for u in range(N):
				if v == u:
					continue
				
				if (v,u) in edge_set:
					Q[(m,v),(m+1,u)] += 1
				else:
					Q[(m,v),(m+1,u)] += P

	for m in range(M):
		for v in range(N):
			Q[((m,N),(m+1,v))] = P

	end = time.time()

	print(f"Done with edges_exp : Took {end - start} seconds")