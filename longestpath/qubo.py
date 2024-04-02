from pyqubo import Binary, Array, Num
import numpy as np
from dimod import BinaryQuadraticModel
import neal
from typing import List, Dict, Tuple
from longestpath import gen_average_degree_directed, gen_planted_path, StandardGraph, complete_graph, gen_num_edges
import itertools
from longestpath import brute
from .utils import with_timed_result
import multiprocessing

# Like bqm.update but with a pyqubo exp and a scalar
def update(bqm, exp, scalar):
	exp_bqm = exp.compile().to_bqm()
	exp_bqm.scale(scalar)
	bqm.update(exp_bqm)

class QUBOSolver:
	def __init__(self, graph: StandardGraph, max_length_path: int | None = None):
		if max_length_path is None:
			max_length_path = graph.vertices-1

		self.graph = graph
		self.max_length_path = max_length_path

		N = self.graph.vertices
		M = self.max_length_path
		self.var_names_matrix = [[f"X[{m}][{n}]" for n in range(N+1)] for m in range(M+1)]

	def generate_bqm(self):
		N = self.graph.vertices
		M = self.max_length_path
		P = -(M+1)

		# The variable V[m][n] will be compiled to its label X[m][n] in the bqm
		# So use V in pyqubo expressions, and X when updating the bqm directly
		X = self.var_names_matrix
		V = [[Binary(X[m][n]) for n in range(N+1)] for m in range(M+1)]

		bqm = BinaryQuadraticModel('BINARY')

		# Exactly one vertex at each time-step block
		for block in V:
			update(bqm, (sum(block) - Num(1))**2, P)
		
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

		# Convert maximisation problem to minimisation problem
		bqm.scale(-1)

		return bqm
	
	def initial_states(self, num_states: int | None = None):

		X = self.var_names_matrix
		M = self.max_length_path
		N = self.graph.vertices

		if num_states is None:
			num_states = M * 200

		def gen_random_path(length: int) -> List[int]:
			path = np.random.permutation(graph.vertices)[:length+1]
			path = np.pad(path, (0, M+1-len(path)), constant_values=graph.vertices)
			return path
	
		def to_state(path: List[int]) -> Dict[Tuple[int, int], int]:
			state = {X[m][v]: 0 for m in range(M+1) for v in range(graph.vertices+1)}
			for m, v in enumerate(path):
				state[X[m][v]] = 1
			for m in range(len(path), M+1):
				state[X[m][graph.vertices]] = 1
			return state
		
		# return [to_state(gen_random_path(N-1))] * 2000
		# return [to_state([])]
		# return [to_state([n]) for n in range(N)]
		
		self.initial_paths = [gen_random_path(M) for _ in range(num_states)]
		# initial_paths = [gen_random_path(m) for m in range(M+1) for _ in range(10 + 10 * m)]
		initial_states = [to_state(path) for path in self.initial_paths]
		return initial_states
	
	def get_bqm(self):
		if not hasattr(self, "bqm"):
			self.bqm = self.generate_bqm()
		return self.bqm
	
	def get_default_beta_range(self):
		bqm = self.get_bqm()
		return neal.sampler.default_beta_range(bqm)

	def sample(self, **kwargs):
		bqm = self.get_bqm()
		sa = neal.SimulatedAnnealingSampler()
		sampleset = sa.sample(bqm, **kwargs)
		return sampleset
	
	def sample_to_result(self, sample):
		X = self.var_names_matrix

		multi_path = [[v for v in range(graph.vertices+1) if sample.sample.get(X[m][v], 0) == 1] for m in range(graph.vertices)]

		result = {"reward": -sample.energy, 'multi_path': multi_path}

		for m in range(graph.vertices):
			if len(multi_path[m]) < 1:
				result['failure'] = f"Path broken at step {m}"
				return result
			if len(multi_path[m]) > 1:
				result['failure'] = f"Path non-deterministic at step {m}: {multi_path[m]}"
				return result
		else:
			terminal_path = [vertices[0] for vertices in multi_path]

			path = list(itertools.takewhile(lambda v: v < graph.vertices, terminal_path))
			Ntail = itertools.dropwhile(lambda v: v < graph.vertices, terminal_path)
			N = graph.vertices

			for v in Ntail:
				if v != N:
					result['failure'] = f"Path has invalid edge N={N} -> {v}"
			else:
				result['path'] = path

		return result

	@with_timed_result
	def solve(self, **sampler_kwargs):
		sampleset = self.sample(**sampler_kwargs)
		best_sample = sampleset.first
		return self.sample_to_result(best_sample)

if __name__ == "__main__":
	n = 20
	d = 2
	graph = gen_num_edges(n, round(n * d))

	def pretty_result(result):
		info = {k:v for k,v in result.items() if type(v) in [int, float, str]}
		if "path" in result:
			info["length"] = len(result['path'])-1
			format_str = "{:>3},"*len(result['path'])
			return str(info) + "\n" + format_str.format(*list(map(str, result['path'])))
		else:
			return str(info)

	brute_result = brute.solve(multiprocessing.Queue(), graph, "BRANCH_N_BOUND")
	print("BRUTE", pretty_result(brute_result))

	solver = QUBOSolver(graph)
	min_beta, max_beta = solver.get_default_beta_range()
	result = solver.solve(num_reads=10_000, num_sweeps=100, beta_range=(0.1, 0.5*max_beta))
	print("QUBOSolver", pretty_result(result))