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

	def undirected_str(self) -> str:
		edges = set(frozenset(e) for e in self.edges if e[0] != e[1])

		return f"{self.vertices}\n" + "\n".join(f"{a} {b}" for (a,b) in edges)

	def from_undirected(vertices, edges):
		return StandardGraph(vertices, 
				[(v, v) for v in range(vertices)]
				+ edges
				+ [(t, s) for (s, t) in edges]
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
	result = linear_graph(path_length)

	for v in range(path_length):
		max_nodes = min(v + 1, path_length - v)
		G = gen_erdos_reyni_(node_count(max_nodes), p = p)
		result.wedge(G, v, 0)
	
	return result

if __name__ == "__main__":
	# print(gen_average_degree(10, average_degree=2))
    print(gen_planted_path(5, 1).undirected_str())
	# random.seed(0)
	# print(gen_erdos_reyni_(5, p = 1))
