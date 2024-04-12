"""
Contains various kinds of random graph generation methods.
In particular it contains
- Various different Erdős–Rényi (https://en.wikipedia.org/wiki/Erdős–Rényi_model) implementations
- An ad-hoc way to generate random DAGs
- Various ways to generate graphs with planted longest paths
- A way to enlargen graphs without changing the length of the longest path.
"""

import math, random
from dataclasses import dataclass
from typing import List, Tuple, Callable
import numpy as np
from .neighbors_graph import NeighborsGraph
from .standard_graph import StandardGraph, linear_graph, complete_graph

def random_subset(set: list, p: float) -> list:
	"""
	Selects a random subset of `set` uniformly at random.
	"""
	n = np.random.binomial(len(set), p)
	choices = np.random.choice(range(len(set)), n, replace = False)
	return [set[i] for i in choices]

def gen_random_edges_directed(num_vertices: int, p:float) -> StandardGraph:
	all_edges = [(s, t) for s in range(num_vertices) for t in range(num_vertices)]
	
	return StandardGraph(num_vertices, list(random_subset(all_edges, p)))

def gen_random_edges_average_degree_directed(num_vertices: int, average_degree: float) -> StandardGraph:
	p = min(1, average_degree / num_vertices)
	return gen_random_edges_directed(num_vertices, p)

def gen_num_edges(num_vertices: int, num_edges: int) -> StandardGraph:
	all_edges = [(s, t) for s in range(num_vertices) for t in range(num_vertices)]
	random_edges = [all_edges[i] for i in np.random.choice(len(all_edges), num_edges, replace = False)]
	return StandardGraph(num_vertices, random_edges)

def gen_num_edges_no_loops(num_vertices: int, num_edges: int) -> StandardGraph:
	all_edges = [(s, t) for s in range(num_vertices) for t in range(num_vertices) if s < t]
	random_edges = [all_edges[i] for i in np.random.choice(len(all_edges), min(num_edges, len(all_edges)), replace = False)]
	return StandardGraph(num_vertices, random_edges)

def gen_num_edges_undirected(num_vertices: int, num_edges: int) -> StandardGraph:
	all_edges = [{s, t} for s in range(num_vertices) for t in range(num_vertices) if s != t]
	random_edges = [all_edges[i] for i in np.random.choice(len(all_edges), num_edges, replace = False)]

	random_edges2 = [tuple(e) for e in random_edges]
	random_edges3 = random_edges2 + [(t, s) for s,t in random_edges2]

	return StandardGraph(num_vertices, random_edges3)

def gen_density(num_vertices: int, density: float, directed: bool = True) -> StandardGraph:
	if not directed:
		raise NotImplementedError()
	assert 0 <= density and density <= 1
	all_edges = [(s, t) for s in range(num_vertices) for t in range(num_vertices)]
	num_edges = round(density * len(all_edges))
	random_edges = [all_edges[i] for i in np.random.choice(len(all_edges), num_edges, replace = False)]
	return StandardGraph(num_vertices, random_edges)

def gen_planted_path(path_length: int, p: float, node_count: Callable[[int], int] = lambda n: n) -> StandardGraph:
	"""
	Generates a random graph such that its longest path consits of exactly `path_length` many nodes.

	Args:
		p: The probability used in Erdos-Reyni to generate bubbles.
		node_count: Should return the size of a bubble given the upper bound. This can be any non-order-increasing procedure.
	"""
	result = linear_graph(path_length)

	for v in range(path_length):
		max_nodes = min(v + 1, path_length - v)
		G = gen_random_edges_directed(node_count(max_nodes), p = p)
		result.wedge(G, v, 0)
	
	return result

def gen_planted_path_with_average_degree(path_length: int, average_degree, node_count: Callable[[int], int] = lambda n: n) -> StandardGraph:
	result = linear_graph(path_length)

	for v in range(path_length):
		max_nodes = min(v + 1, path_length - v)
		G = gen_random_edges_average_degree_directed(node_count(max_nodes), average_degree=average_degree)
		result.wedge(G, v, 0)
	
	return result


def gen_planted_hamiltonian(vertices: int, p: float) -> StandardGraph:
	line = linear_graph(vertices).edges
	line_set = set(line)
	all_edges = [
		(s, t) 
			for s in range(vertices) 
			for t in range(vertices) 
			if (s,t) not in line_set
	]
	
	return StandardGraph(vertices, list(random_subset(all_edges, p)) + line)

def gen_planted_hamiltonian_undirected_fixed_degree(vertices: int, num_edges: int) -> StandardGraph:
	line = linear_graph(vertices).edges
	line_set = set(line)
	all_edges = [
		(s, t) 
			for s in range(vertices) 
			for t in range(vertices) 
			if (s,t) not in line_set and (t,s) not in line_set and s < t
	]

	amount_of_edges_to_choose = max(0, min(len(all_edges), num_edges - vertices + 1))

	random_edges = [
		all_edges[i] for i in np.random.choice(
			len(all_edges), 
			amount_of_edges_to_choose, 
			replace = False
		)
	]

	edges = random_edges + line

	final_edges = edges + [(t, s) for s,t in edges]
	
	return StandardGraph(vertices, final_edges)



def shuffle_vertex_names(graph: StandardGraph) -> StandardGraph:
	'''
	Some algorithms might be advantaged by the longest path being 0 -> 1 -> 2 etc,
	so use this to shuffle the vertex names and the edges.
	'''
	mapper = np.random.permutation(graph.vertices)

	edges = [(mapper[i], mapper[j]) for (i,j) in graph.edges]
	random.shuffle(edges)

	return StandardGraph(graph.vertices, edges)




class ExpandableGraph:
	"""
	This class is intended to serve as an interface. Subclasses are supposed to represent graphs for which we can compute, what I call the least expansion distance of each vertex.
	This can then be used to expand the graph by wedging 'bubbles' to each vertex in such a way as to avoid lengthening the longest path.

	For a path p, the backward expansion distance is the length (in edge distance) of the longest path q such that qp is again a path.
	Similarly the forward expansion distance is the length of the longest path q such that pq is a path.

	The backward least expansion distance for a vertex v is then the minimum of the backward expansion distances of paths starting in v, and similarly so for the forward least expansion distance.
	"""

	# WARNING: This should be given in edge distance
	def backward_least_expansion_distance(self, v: int):
		pass

	# WARNING: This should be given in edge distance
	def forward_least_expansion_distance(self, v: int):
		pass

	# WARNING: This should be given in edge distance
	def least_expansion_distance(self, v: int):
		return min(
			self.forward_least_expansion_distance(v), 
			self.backward_least_expansion_distance(v)
		)

	def expand(self, generator: Callable[[int], StandardGraph] = lambda n: n) -> StandardGraph:
		"""
		Returns a new graph G such that self.graph is a subgraph of G and such that there is a longest path of G that sits fully inside of self.graph.

		Args:
			generator: A graph generator for generating the bubbles.
				`generator(n)` should return a `StandardGraph` with at most n nodes.
		"""
		result = self.graph.clone()

		for v in range(self.graph.vertices):
			max_bubble_path_edge_length = self.least_expansion_distance(v)
			max_bubble_size = max_bubble_path_edge_length + 1
			G = generator(max_bubble_size)
			result.wedge(G, v, 0)

		return result



@dataclass
class LinearGraph(ExpandableGraph):
	graph: StandardGraph
	def __init__(self, vertices: int):
		self.graph = linear_graph(vertices)
	
	def backward_least_expansion_distance(self, v: int):
		return v

	def forward_least_expansion_distance(self, v: int):
		return self.graph.vertices - 1 - v

	def __repr__(self):
		return f"{LinearGraph.__name__}({self.graph.vertices})"

def compute_index_dict(set_list):
	result = {}

	for i, s in enumerate(set_list):
		for x in s:
			result[x] = i

	return result



@dataclass
class DAG(ExpandableGraph):
	graph: StandardGraph
	"""
	NOTE: The graph should not be mutated!
	These are directed acyclic graphs.
	
	For any paths p and q such that end(p) = start(q) we know that pq is a path.
	Therefore computing the least expansion distances is easy in these cases.
	"""
	def __init__(self, graph: StandardGraph):
		self.graph = graph
		self.lower_topo_sorting = self.graph.topological_sort()
		self.graph.invert_edges()
		self.upper_topo_sorting = self.graph.topological_sort()
		self.graph.invert_edges()
		self.neighbors_graph = NeighborsGraph(self.graph)
		
		self.lower_topo_sorting_by_node = compute_index_dict(self.lower_topo_sorting)
		self.upper_topo_sorting_by_node = compute_index_dict(self.upper_topo_sorting)


	def backward_least_expansion_distance(self, v: int):
		return self.lower_topo_sorting_by_node[v]

	def forward_least_expansion_distance(self, v: int):
		return self.upper_topo_sorting_by_node[v]

	def longest_path_length(self):
		"""
		The amount of nodes in the longest path.
		"""
		return len(self.lower_topo_sorting)

	def find_longest_path(self):
		"""
		Returns a longest path.
		"""
		layers = self.lower_topo_sorting[:]
		path = []

		while len(layers) > 0:
			layer = layers.pop()

			if len(path) == 0:
				path.append(list(layer)[0])
			else:
				new_node = None

				for s in self.neighbors_graph.in_nodes[path[-1]]:
					if s in layer:
						new_node = s
						break
		
				path.append(new_node)

		path.reverse()

		return path


def gen_DAG(vertices: int, p: float):
	"""
	Generates random DAGs in a very adhoc way.
	"""
	nlayers = random.randint(1, vertices)

	layer_assignemnts = {}

	for v in range(vertices):
		layer_assignemnts[v] = random.randint(1, nlayers)

	all_edges = [(s, t) 
		for s in range(vertices) 
		for t in range(vertices) 
		if layer_assignemnts[s] < layer_assignemnts[t]
	]

	edges = random_subset(all_edges, p)

	return StandardGraph(vertices, edges)


if __name__ == "__main__":
	pass
