class TopSorter:
	"""
	Deprecated
	"""
	# Definition: An initial node is a node which has no incoming edges.

	# We divide a graph into layers in the following manner:
	# 1. Find all intial nodes. These will be the layer for this iteration.
	# 2. Remove all of these nodes from the graph.
	# 3. Repeat.

	def __init__(self, graph):
		self.graph = graph

	def run(self):
		# For each vertex v the vertices u such that (v,u) is an edge
		# This variable doesn't change throughout the process.
		self.out_nodes = {v : [] for v in range(self.graph.vertices)}

		# For each vertex v these are the vertices u such that (u,v) is an edge.
		# This variable changes as we 'remove' initial nodes from the graph.
		self.in_nodes = {v : set() for v in range(self.graph.vertices)}

		# This will be the output of topsort
		self.layers = []

		# Initializes in_nodes and out_nodes
		for (s, t) in self.graph.edges:
			self.in_nodes[t].add(s)
			self.out_nodes[s].append(t)

		# These are the nodes we consider in each iteration.
		# At each stage this set should include all initial nodes but it not does not need to include all nodes of the graph.
		nodes_to_consider = set(range(self.graph.vertices))

		while True:
			layer = self.find_inital_nodes(nodes_to_consider)
			
			if len(layer) == 0: break

			self.layers.append(layer)
			nodes_to_consider = self.next_nodes(layer)
			self.remove_from_in_nodes(layer)

		return self.layers

	def find_inital_nodes(self, nodes):
		"""
		Finds the initial nodes using the current state of self.in_nodes
		"""
		return set(
				v 
				for v in nodes
				if len(self.in_nodes[v]) == 0
			)

	def remove_from_in_nodes(self, nodes):
		"""
		Removes the nodes specified in `nodes` from the self.in_nodes dictionary.
		"""
		for s in nodes:
			for t in self.out_nodes[s]:
				if s in self.in_nodes[t]:
					self.in_nodes[t].remove(s)

	def next_nodes(self, nodes):
		"""
		Returns the 'successors' of the nodes in `nodes`.
		"""
		out = []

		for s in nodes:
			for t in self.out_nodes[s]:
				out.append(t)

		return out

	