from collections import deque

class NeighborsGraph:
  def __init__(self, standard_graph):
    vertices = range(standard_graph.vertices)
    self.in_nodes = {}
    self.out_nodes = {}

    self.add_edges(standard_graph.edges)

  def vertices(self):
    return list(self.in_nodes.keys())

  def add_edges(self, edges):
    for (s, t) in edges:
      if s not in self.out_nodes:
        self.out_nodes[s] = set()
      if s not in self.in_nodes:
        self.in_nodes[s] = set()
      if t not in self.out_nodes:
        self.out_nodes[t] = set()
      if t not in self.in_nodes:
        self.in_nodes[t] = set()  

      self.out_nodes[s].add(t)        
      self.in_nodes[t].add(s)

  def remove_nodes(self, nodes):
    for v in nodes:
      for t in self.out_nodes[v]:
        self.in_nodes[t].remove(v)
      for s in self.in_nodes[v]:
        self.out_nodes[s].remove(v)
      del self.in_nodes[v]
      del self.out_nodes[v]

  def successors(self, nodes):
    out = set()

    for v in nodes:
      for t in self.out_nodes[v]:
        out.add(t)

    return out

  def find_initial_nodes(self, nodes):
    return set(
      v for v in nodes
      if len(self.in_nodes[v]) == 0
    )

  def shortest_path(self, source, target):
    queue = deque([(source, t) for t in self.out_nodes[source]])
    visited = set()
    tree = {}

    while True:
      if len(queue) == 0: return None
      
      (s, v) = queue.popleft()
      tree[v] = s

      if v in visited: continue
      if v == target: break

      for t in self.out_nodes[v]:
        queue.append((v, t))

      visited.add(v)

    path = [target]

    node = target
    while node != source:
      node = tree[node]
      path.append(node)

    path.reverse()

    return path    

  def shortest_path_from_vertices(self, sources, target):
    new_vertex = max(self.vertices()) + 1
    
    self.add_edges((new_vertex, s) for s in sources)

    path = self.shortest_path(new_vertex, target)

    self.remove_nodes([new_vertex])

    if path == None:
      return None
    else:
      return path[1:]



