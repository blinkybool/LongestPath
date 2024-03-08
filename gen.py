import math, random
from dataclasses import dataclass
from typing import List, Tuple, Callable
import numpy as np
from topsort import TopSorter
from neighbors_graph import NeighborsGraph

@dataclass
class StandardGraph:
	vertices: int
	edges: List[Tuple[int, int]]

	# Standard format for graphs is the vertex count on the first line
	# and every subsequent line has a space seperated pair of ints (non-neg)
	# representing edges between vertices
	# Example (with 10 vertices, 3 edges):
	# 
	# 10
	# 0 5
	# 2 7
	# 8 9
	def __str__(self) -> str:
		return f"{self.vertices}\n" + "\n".join(f"{a} {b}" for (a,b) in self.edges)

	def clone(self):
		"""
		Makes a deep copy of the graph
		"""
		return StandardGraph(self.vertices, self.edges[:])

	def wedge(self, other, self_vert, other_vert):
		"""
		Warning: This mutates the graph.

		Extends self by merging it with other while making sure that exactly the vertices self_vert and other_vert become identified.
		"""
		n = self.vertices
		self.vertices += other.vertices - 1

		def other_map(v):
			if v < other_vert:
				return n + v
			elif v == other_vert:
				return self_vert
			else:
				return n + v - 1

		self.edges += [(other_map(s), other_map(t)) for (s, t) in other.edges]

	def undirected_str(self) -> str:
		"""
		Returns a string representing the graph, leaving out direction and selfloops.
		"""
		edges = set(frozenset(e) for e in self.edges if e[0] != e[1])

		return f"{self.vertices}\n" + "\n".join(f"{a} {b}" for (a,b) in edges)

	def from_undirected(vertices, edges):
		"""
		Freely turns an undirected representation of a graph into a directed graph.
		In other words, it adds all selfloops and oposites of edges from edges.
		"""
		return StandardGraph(vertices, 
				list(set([(v, v) for v in range(vertices)]
				+ edges
				+ [(t, s) for (s, t) in edges]))
			)

	def invert_edges(self):
		"""
		WARNING: Mutates the graph.
		This flips all adges.
		"""
		for i, (s, t) in enumerate(self.edges):
			self.edges[i] = (t, s)

	def topological_sort(self):
		"""
		Attempts to topologically sort a graph.
		Returns a topological sorting if the graph is acyclic.
		Returns None if the graph contains a cycle.
		"""
		layers = []
		graph = NeighborsGraph(self)
		nodes_to_consider = list(range(self.vertices))

		while True:
			initial_nodes = graph.find_initial_nodes(nodes_to_consider)
			if len(initial_nodes) == 0: break
			layers.append(initial_nodes)

			nodes_to_consider = graph.successors(initial_nodes)
			graph.remove_nodes(initial_nodes)
		
		if sum(len(layer) for layer in layers) == self.vertices:
			return layers
		else:
			return None

def random_subset(set: list, p: float) -> list:
	n = np.random.binomial(len(set), p)

	choices = np.random.choice(range(len(set)), n, replace = False)
	return [set[i] for i in choices]

# This is a more direct implementation of Erdos Renyi.
# https://en.wikipedia.org/wiki/Erdős–Rényi_model
def gen_erdos_reyni_directed(num_vertices: int, p:float = None) -> StandardGraph:
	all_edges = [(s, t) for s in range(num_vertices) for t in range(num_vertices)]
	
	return StandardGraph(num_vertices, list(random_subset(all_edges, p)))

def complete_graph(vertices: int) -> StandardGraph:
	return StandardGraph(
		vertices,
		[(s, t) for s in range(vertices) for t in range(vertices)]
	)

def linear_graph(vertices: int) -> StandardGraph:
	edges = list(zip(range(vertices),range(1,vertices)))
	return StandardGraph(vertices, edges)

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
		G = gen_erdos_reyni_directed(node_count(max_nodes), p = p)
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

	def expand(self, p: float, node_count: Callable[[int], int] = lambda n: n) -> StandardGraph:
		"""
		Returns a new graph G such that self.graph is a subgraph of G and such that there is a longest path of G that sits fully inside of self.graph.

		Args:
			p: The probability used in Erdos-Reyni to generate bubbles.
			node_count: Should return the size of a bubble given the upper bound. This can be any non-order-increasing procedure.
		"""
		result = self.graph.clone()

		for v in range(self.graph.vertices):
			max_bubble_path_edge_length = self.least_expansion_distance(v)
			max_bubble_size = max_bubble_path_edge_length + 1
			G = gen_erdos_reyni_directed(node_count(max_bubble_size), p = p)
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
		self.upper_topo_sorting.reverse()
		self.graph.invert_edges()
		self.neighbors_graph = NeighborsGraph(self.graph)

	def backward_least_expansion_distance(self, v: int):
		pass

	def forward_least_expansion_distance(self, v: int):
		pass

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
	random.seed(3)
	np.random.seed(3)
	# n = 50
	# d = 3
	# p = d/n
	# graph = gen_erdos_reyni_directed(100, 0.011)
	# print(graph)
	G = DAG(gen_DAG(10, 0.5))
	print(G.graph)
	print(G.lower_topo_sorting)
	print(G.upper_topo_sorting)
	print(G.find_longest_path())

	# print(shuffle_vertex_names(gen_planted_path(n, p)))
	# print(LinearGraph(15).expand(0.5))
	# print(gen_erdos_reyni_directed(20, 0.1))
	# G = gen_erdos_reyni_directed(10, 0.1)
	# print(G)
	# print(G.topological_sort())

