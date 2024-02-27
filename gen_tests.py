from gen import *
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

        G = gen_erdos_reyni(10, p=0.2)
        G_cloned = G.clone()

        self.assertEqualGraphs(G, G_cloned)

        G.vertices = 0
        G.edges = []

        self.assertNotEqual(G.vertices, G_cloned.vertices)


if __name__ == '__main__':
    unittest.main()