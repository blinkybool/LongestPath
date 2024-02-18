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


if __name__ == "__main__":
	print(gen_average_degree(10, average_degree=2))