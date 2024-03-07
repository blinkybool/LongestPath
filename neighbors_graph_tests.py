from gen import StandardGraph, linear_graph, complete_graph
from neighbors_graph import *
import unittest
import random

class TestGen(unittest.TestCase):
    def assertEqualGraphs(self, G1, G2):
      self.assertEqual(G1.in_nodes, G2.in_nodes)
      self.assertEqual(G1.out_nodes, G2.out_nodes)

    def test_shortest_path_linear_forward(self):
      G = NeighborsGraph(linear_graph(5))
      self.assertEqual(G.shortest_path(0, 4), [0, 1, 2, 3, 4])

    def test_shortest_path_linear_backward(self):
      G = NeighborsGraph(linear_graph(5))
      self.assertEqual(G.shortest_path(4, 0), None)

    def test_shortest_path_linear_proper(self):
      G = NeighborsGraph(linear_graph(7))
      self.assertEqual(G.shortest_path(1, 5), [1,2,3,4,5])

    def test_shortest_path1(self):
      G = NeighborsGraph(StandardGraph(5,
        [(0,1), (1,2), (2,3), (0,4), (4, 3)]
      ))
      self.assertEqual(G.shortest_path(0, 3), [0,4,3])

    def test_remove_nodes(self):
      G = NeighborsGraph(complete_graph(5))
      G.remove_nodes([4])

      self.assertEqualGraphs(G, NeighborsGraph(complete_graph(4)))

    def test_successors(self):
      G = NeighborsGraph(linear_graph(5))
      self.assertEqual(G.successors({2}), {3})

    def test_vertices(self):
      G = NeighborsGraph(linear_graph(5))
      self.assertEqual(G.vertices(), [0,1,2,3,4])

    def test_shortest_path_from_vertices1(self):
      G = NeighborsGraph(StandardGraph(5,
        [(0,1), (1,2), (2,3), (0,4), (4, 3)]
      ))
      self.assertEqual(G.shortest_path_from_vertices([0], 3), [0,4,3])

    def test_shortest_path_from_vertices1(self):
      G = NeighborsGraph(StandardGraph(6,
        [(0,1),(1,2),(3,4),(0,5),(5,4)]
      ))
      self.assertEqual(G.shortest_path_from_vertices([0,1], 4), [0,5,4])

if __name__ == '__main__':
    unittest.main()