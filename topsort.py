
class TopSorter:
	def __init__(self, graph):
		self.graph = graph
		self.in_nodes = {v : set() for v in range(graph.vertices)}
		self.out_nodes = {v : [] for v in range(graph.vertices)}
		self.layers = []

		for (s, t) in graph.edges:
			self.in_nodes[t].add(s)
			self.out_nodes[s].append(t)


	def inital_nodes(self, nodes):
		return set(
				v 
				for v in nodes
				if len(self.in_nodes[v]) == 0
			)

	def remove_from_in_nodes(self, nodes):
		for s in nodes:
			for t in self.out_nodes[s]:
				if s in self.in_nodes[t]:
					self.in_nodes[t].remove(s)

	def next_nodes(self, nodes):
		out = []

		for s in nodes:
			for t in self.out_nodes[s]:
				out.append(t)

		return out

	def run(self):
		nodes = set(range(self.graph.vertices))

		while True:
			layer = self.inital_nodes(nodes)
			
			if len(layer) == 0: return self.layers

			self.layers.append(layer)
			nodes = self.next_nodes(layer)
			self.remove_from_in_nodes(layer)