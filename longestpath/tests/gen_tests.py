from ..gen import *
import unittest
import random
from ..standard_graph import complete_graph, discrete_graph

class TestGen(unittest.TestCase):
    def assertEqualGraphs(self, G1, G2):
        self.assertEqual(G1.vertices, G2.vertices)
        self.assertEqual(set(G1.edges), set(G2.edges))
   
    def test_gen_random_edges_directed(self):
        random.seed(0)
        self.assertEqualGraphs(
            gen_random_edges_directed(5, p = 1),
            complete_graph(5),
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
        result = LinearGraph(5).expand(generator=discrete_graph)
        self.assertEqualGraphs(
            result, StandardGraph(9, linear_graph(5).edges)
        )

    def test_expand_prob1(self):
        result = LinearGraph(5).expand(generator=complete_graph)
        self.assertEqualGraphs(
            StandardGraph.from_undirected(result.vertices, result.edges),
            StandardGraph.from_undirected(9, 
                [(0,1), (1,2), (2,3), (3,4), (1,5), (2,6), (2,7), (6,7), (3,8)]
            )
        )

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