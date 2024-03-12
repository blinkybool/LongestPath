from standard_graph import *
import unittest
import random

class TestGen(unittest.TestCase):
    def assertEqualGraphs(self, G1, G2):
        self.assertEqual(G1.vertices, G2.vertices)
        self.assertEqual(set(G1.edges), set(G2.edges))

    def test_linear_graph(self):
        self.assertEqualGraphs(
            linear_graph(5),
            StandardGraph(5, [(0,1),(1,2),(2,3),(3,4)])
        )

    def test_wedge(self):
        G1 = linear_graph(3)
        G2 = linear_graph(4)

        G1.wedge(G2, 2, 0)

        expected = linear_graph(6)

        self.assertEqualGraphs(G1, expected)

    def test_clone(self):
        random.seed(0)

        G = complete_graph(5)
        G_cloned = G.clone()

        self.assertEqualGraphs(G, G_cloned)

        G.vertices = 0
        G.edges = []

        self.assertNotEqual(G.vertices, G_cloned.vertices)

    def test_complete_graph(self):
        self.assertEqualGraphs(
            complete_graph(2),
            StandardGraph(2, [(0,0), (0,1), (1,0), (1,1)])
        )

    def test_from_undirected(self):
        self.assertEqualGraphs(
            StandardGraph.from_undirected(3, [(0,1), (1,2)]),
            StandardGraph(3, [(0,0),(1,1),(2,2), (0,1), (1,2), (1,0), (2,1)])
        )

    def test_invert_edges(self):
        G = StandardGraph(3, [(0,1),(1,2)])
        G.invert_edges()
        self.assertEqualGraphs(
            G,
            StandardGraph(3, [(2,1),(1,0)]),
        )

    def test_topsort_cycle(self):
        G = StandardGraph(4, [
            (0, 1),
            (1, 2), (2, 3), (3, 1)
        ])
        self.assertEqual(G.topological_sort(), None)

    def test_topsort_DAG(self):
        G = StandardGraph(5, [
            (0, 1), (0, 2), (0, 3),
            (1, 4), (2, 4), (3, 4)
        ])
        self.assertEqual(G.topological_sort(), [
            {0}, {1, 2, 3}, {4}    
        ])

    def test_universal_nodes(self):
        G = linear_graph(5)

        G.add_universal_nodes()

        self.assertEqualGraphs(G, StandardGraph(7, [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6),
            (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6)
        ]))

if __name__ == '__main__':
    unittest.main()