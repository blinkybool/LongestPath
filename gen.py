import math, random
from dataclasses import dataclass
from typing import List, Tuple, Callable
import numpy as np

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


# https://en.wikipedia.org/wiki/Erdős–Rényi_model
def gen_erdos_reyni(num_vertices: int, num_edges:int = None, p:float = None) -> StandardGraph:
	if num_edges is None:
		assert p is not None, "Expected num_edges or probability p"
	else:
		assert p is None, "Specify only one of num_edges and probability p"

	num_edges = num_edges or round(p * math.comb(num_vertices, 2))

	print(num_edges)

	edges: List[Tuple[int, int]] = []

	for _ in range(num_edges):
		source: int = random.randint(0, num_vertices-1)
		target: int = random.randint(0, num_vertices-1)
		edges.append((source, target))

	return StandardGraph(vertices=num_vertices, edges=sorted(edges))

def random_subset(set: list, p: float) -> list:
	n = np.random.binomial(len(set), p)

	choices = np.random.choice(range(len(set)), n, replace = False)
	return [set[i] for i in choices]

# This is a more direct implementation of Erdos Renyi.
# https://en.wikipedia.org/wiki/Erdős–Rényi_model
def gen_erdos_reyni_(num_vertices: int, p:float = None) -> StandardGraph:
	all_edges = [(s, t) for s in range(num_vertices) for t in range(num_vertices)]
	
	return StandardGraph(num_vertices, list(random_subset(all_edges, p)))

def complete_graph(vertices: int) -> StandardGraph:
	return StandardGraph(
		vertices,
		[(s, t) for s in range(vertices) for t in range(vertices)]
	)

def gen_average_degree(num_vertices: int, average_degree: int) -> StandardGraph:
	return gen_erdos_reyni(num_vertices=num_vertices, num_edges=round(num_vertices * average_degree / 2))

def linear_graph(vertices: int) -> StandardGraph:
	edges = list(zip(range(vertices),range(1,vertices)))
	return StandardGraph(vertices, edges)

def gen_planted_path(path_length: int, p: float, node_count: Callable[[int], int] = lambda n: n) -> StandardGraph:
	"""
	Generates a random graph such that its longest path length is exactly `path_length`.

	Args:
		p: The probability used in Erdos-Reyni to generate bubbles.
		node_count: Should return the size of a bubble given the upper bound. This can be any non-order-increasing procedure.
	"""
	result = linear_graph(path_length)

	for v in range(path_length):
		max_nodes = min(v + 1, path_length - v)
		G = gen_erdos_reyni_(node_count(max_nodes), p = p)
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

class ExpandableGraph:
	"""
	This class is intended to serve as an interface. Subclasses are supposed to represent graphs for which we can compute, what I call the least expansion distance of each vertex.
	This can then be used to expand the graph by wedging 'bubbles' to each vertex in such a way as to avoid lengthening the longest path.

	For a path p, the backward expansion distance is the length (in edge distance) of the longest path q such that qp is again a path.
	Similarly the forward expansion distance is the length of the longest path q such that pq is a path.

	The backward least expansion distance for a vertex v is then the minimum of the backward expansion distances of paths starting in v, and similarly so for the forward least expansion distance.
	"""
	graph: StandardGraph

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
			G = gen_erdos_reyni_(node_count(max_bubble_size), p = p)
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

if __name__ == "__main__":
    # print(gen_planted_hamiltonian(7, p = 0.2).undirected_str())
    print(LinearGraph(5).expand(1).undirected_str())

