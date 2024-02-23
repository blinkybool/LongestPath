import math, random
from dataclasses import dataclass
from typing import List, Tuple


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
		return StandardGraph(self.vertices, self.edges[:])

	def wedge(self, other, self_vert, other_vert):
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

		


# https://en.wikipedia.org/wiki/Erdős–Rényi_model
def gen_erdos_reyni(num_vertices: int, num_edges:int = None, p:float = None) -> StandardGraph:
	if num_edges is None:
		assert p is not None, "Expected num_edges or probability p"
	else:
		assert p is None, "Specify only one of num_edges and probability p"

	num_edges = num_edges or round(p * math.comb(num_vertices, 2))

	edges: List[Tuple[int, int]] = []

	for _ in range(num_edges):
		source: int = random.randint(0, num_vertices-1)
		target: int = random.randint(0, num_vertices-1)
		edges.append((source, target))

	return StandardGraph(vertices=num_vertices, edges=sorted(edges))

def gen_average_degree(num_vertices: int, average_degree: int) -> StandardGraph:
	return gen_erdos_reyni(num_vertices=num_vertices, num_edges=round(num_vertices * average_degree / 2))

"""
This class is intended to serve as an interface.
It represents a graph for which we know:
1. For each vertex: the length of the longest path for which this vertex is an endpoint.
2. The longest path length of the entire graph (this can be derived in polynomial time from 1).
"""
@dataclass
class GraphWithLongestPaths:
	graph: StandardGraph

	def longest_path_length_from(self, vert: int) -> int:
		pass

	def longest_path_length(self) -> int:
		return max(*[self.longest_path_length_from(v) for v in range(self.graph.vertices)])

	def extend(self, p):
		# result = 

		# for v in range(self.graph.vertices):
		pass



class LinearGraph(GraphWithLongestPaths): 
	def __init__(self, vertices: int):
		self.graph = StandardGraph(
			vertices, 
			list(zip(range(vertices), range(1, vertices)))
		)

	def longest_path_length_from(self, vert: int) -> int:
		return max(vert + 1, self.graph.vertices - vert)

	def longest_path_length(self) -> int:
		return self.graph.vertices

    

if __name__ == "__main__":
	# print(gen_average_degree(10, average_degree=2))
    print(LinearGraph(5).graph)
