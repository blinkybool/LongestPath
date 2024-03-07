from collections import deque

class NeighborsGraph:
  def __init__(self, standard_graph):
    vertices = range(standard_graph.vertices)
    self.in_nodes = {v : set() for v in vertices}
    self.out_nodes = {v : set() for v in vertices}

    for (s, t) in standard_graph.edges:
      self.out_nodes[s].add(t)
      self.in_nodes[t].add(s)

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




