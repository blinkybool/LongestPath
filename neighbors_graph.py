from collections import deque

class NeighborsGraph:
  """
  This class represents a graph by storing for each node a sets of neighboring nodes.
  """
  def __init__(self, standard_graph):
    vertices = range(standard_graph.vertices)
    self.in_nodes = {}
    self.out_nodes = {}

    self.add_vertices(range(standard_graph.vertices))
    self.add_edges(standard_graph.edges)

  def vertices(self):
    """
    The list of vertices of the graph.
    """
    return list(self.in_nodes.keys())

  def add_vertices(self, nodes):
    for v in nodes:
      self.in_nodes[v] = set()
      self.out_nodes[v] = set()

  def add_edges(self, edges):
    """
    Mutably adds a list of edges to the graph.
    """
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
    """
    Mutably removes a list of nodes from the graph.
    The edges connected to these nodes are also removed.
    """
    for v in nodes:
      for t in self.out_nodes[v]:
        self.in_nodes[t].remove(v)
      for s in self.in_nodes[v]:
        self.out_nodes[s].remove(v)
      del self.in_nodes[v]
      del self.out_nodes[v]

  def successors(self, nodes):
    """
    Returns a set containing all nodes reachable from the `nodes` list in one forward step.
    """
    out = set()

    for v in nodes:
      for t in self.out_nodes[v]:
        out.add(t)

    return out

  def find_initial_nodes(self, nodes):
    """
    Returns the set of all nodes that have no incomming edges.
    """
    return set(
      v for v in nodes
      if v not in self.in_nodes or len(self.in_nodes[v]) == 0
    )

  def shortest_path(self, source, target):
    """
    Returns the shortest path going from the source node to the target node.
    """
    # We find the shortest path using breath first search.
    
    # We maintain a queue of pairs of nodes (s, t) where t is a node to be considered
    # and s is a preceding node. 
    # By following the chain of preceding nodes one always finds a shortest path to source.
    queue = deque([(source, t) for t in self.out_nodes[source]])

    # A set of nodes that have already been visited
    visited = set()

    # This dict points each node that has been considered to its preceding node.
    tree = {}

    # Perorms the breath first search.
    while True:
      if len(queue) == 0: return None
      
      (s, v) = queue.popleft()
      tree[v] = s

      if v in visited: continue
      if v == target: break

      for t in self.out_nodes[v]:
        queue.append((v, t))

      visited.add(v)

    # Builds the path.
    path = [target]
    node = target
    while node != source:
      node = tree[node]
      path.append(node)

    path.reverse()

    return path    

  def shortest_path_from_vertices(self, sources, target):
    """
    Returns the shortest path going from a list of sources to a single target.
    """
    # We reuse the shortest_path algorithm between two specific nodes by
    # adding a new node which we connect to all nodes in sources.
    # We then find the longest path from this new node to the target 
    # and we then remove the new node again from the path and from the graph.

    new_vertex = max(self.vertices()) + 1
    
    self.add_edges((new_vertex, s) for s in sources)

    path = self.shortest_path(new_vertex, target)

    self.remove_nodes([new_vertex])

    if path == None:
      return None
    else:
      return path[1:]

  def is_path(self, vertices):
    visited = set()

    if len(vertices) == 0: return True

    for (s,t) in zip(vertices, vertices[1:]):
      if s in visited:
        return False

      visited.add(s)

      if t not in self.out_nodes[s]:
        return False

    if vertices[-1] in visited:
      return False

    return True