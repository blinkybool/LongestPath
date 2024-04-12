from dataclasses import dataclass
from typing import List, Tuple, Callable
from .neighbors_graph import NeighborsGraph
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
	
	@classmethod
	def from_string(cls, graph_string: str):
		lines = graph_string.strip().split('\n')
		vertices = int(lines[0])
		edges = []
		for line in lines[1:]:
			u, v = map(int, line.split())
			edges.append((u,v))
		return cls(vertices=vertices, edges=edges)
	
	def to_matrix(self) -> List[List[bool]]:
		matrix = [[False for _ in range(self.vertices)] for _ in range(self.vertices)]
		for (i,j) in self.edges:
			matrix[i][j] = True
		return matrix

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

	def add_universal_nodes(self):
		"""
		WARNING: Mutates the graph.
		This adds two nodes s and t to the graph acting as a universal source and universal sink respectively.
		So there is an edge (s, v) for all v and an edge (v, t) for all v.
		"""
		s = self.vertices
		t = s + 1
		self.vertices += 2

		self.edges += [(s, v) for v in range(self.vertices)]
		self.edges += [(v, t) for v in range(self.vertices)]

	def valid_path(self, path: List[int]):
		for v in path:
			if type(v) != int or v < 0 or v >= self.vertices:
				return False, f"Bad vertex, {v}"
		
		for (u,v) in zip(path, path[1:]):
			if (u,v) not in self.edges:
				return False, f"Bad edge {u} -> {v}"

		return True, ""

	# def average_degree(self):
	# 	return 2 * len(self.edges) / self.vertices
	
	def get_known_longest_path_length(self):
		return self.longest_path_length
	
	def set_known_longest_path_length(self, length):
		self.longest_path_length = length

	def average_out_degree(self):
		return len(self.edges) / self.vertices


def complete_graph(vertices: int) -> StandardGraph:
	return StandardGraph(
		vertices,
		[(s, t) for s in range(vertices) for t in range(vertices)]
	)

def linear_graph(vertices: int) -> StandardGraph:
	edges = list(zip(range(vertices),range(1,vertices)))
	return StandardGraph(vertices, edges)
