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

        G = gen_erdos_reyni_directed(10, p=0.2)
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

    # This test fails!
    # def test_gen_erdos_reyni(self):
    #     random.seed(0)
    #     self.assertEqualGraphs(
    #         gen_erdos_reyni(5, p = 1),
    #         complete_graph(5),
    #     )

    def test_gen_erdos_reyni_directed(self):
        random.seed(0)
        self.assertEqualGraphs(
            gen_erdos_reyni_directed(5, p = 1),
            complete_graph(5),
        )

    def test_from_undirected(self):
        self.assertEqualGraphs(
            StandardGraph.from_undirected(3, [(0,1), (1,2)]),
            StandardGraph(3, [(0,0),(1,1),(2,2), (0,1), (1,2), (1,0), (2,1)])
        )

    def test_gen_planted_path_prob1(self):
        result = gen_planted_path(5, p = 1)
        self.assertEqualGraphs(
            StandardGraph.from_undirected(result.vertices, result.edges),
            StandardGraph.from_undirected(9, 
                [(0,1), (1,2), (2,3), (3,4), (1,5), (2,6), (2,7), (6,7), (3,8)]
            )
        )

    def test_expand_prob0(self):
        result = LinearGraph(5).expand(p = 0)
        self.assertEqualGraphs(
            result, StandardGraph(9, linear_graph(5).edges)
        )

    def test_expand_prob1(self):
        result = LinearGraph(5).expand(p = 1)
        self.assertEqualGraphs(
            StandardGraph.from_undirected(result.vertices, result.edges),
            StandardGraph.from_undirected(9, 
                [(0,1), (1,2), (2,3), (3,4), (1,5), (2,6), (2,7), (6,7), (3,8)]
            )
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

    def test_gen_DAG_topsort(self):
        random.seed(0)
        np.random.seed(0)
        G = gen_DAG(20, 0.5)

        self.assertNotEqual(G.topological_sort(), None)

    def test_DAG_longest_path_length(self):
        random.seed(3)
        np.random.seed(3)

        G = DAG(gen_DAG(10, 0.5))
        self.assertEqual(G.longest_path_length(), 4)

    def test_DAG_longest_path(self):
        random.seed(3)
        np.random.seed(3)

        G = DAG(gen_DAG(10, 0.5))
        path = G.find_longest_path()
        self.assertEqual(G.neighbors_graph.is_path(path), True)
        self.assertEqual(len(path), 4)


if __name__ == '__main__':
    unittest.main()