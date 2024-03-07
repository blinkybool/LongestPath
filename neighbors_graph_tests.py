from gen import StandardGraph, linear_graph
from neighbors_graph import *
import unittest
import random

class TestGen(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()