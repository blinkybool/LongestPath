import math, random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt 
from dataclasses import dataclass
from gen import *
from typing import List, Tuple, Callable

@dataclass
class VisualizableGraph:
    G:StandardGraph 
    pathVertices: List[int]
    pathEdges: List[Tuple[int, int]]
    otherVertices: List[int]
    otherEdges: List[Tuple[int,int]]

  
    def separate(self, path):
        """
    Make two groups: 
    One group consists of all edges and vertices which are in the path
    The other group consists of the remaining of the edges and vertices  
        """
        for (s,t) in self.G.edges:
            if (s,t) in path:
                self.pathEdges.append((s,t))
            else:
                self.otherEdges.append((s,t))
        vertexInPath =[]
        for (s,t) in path:
            vertexInPath.append(s)
            vertexInPath.append(t)
        for vertex in range (self.G.vertices):
            if vertex in vertexInPath:
                self.pathVertices.append(vertex)
            else:
                self.otherVertices.append(vertex)


    def visualize(self, path, path_color='r', other_color='b'):
        """
        Make a visualized graph
        """
        self.separate(path)
        # print("other edges", self.otherEdges)
        # print("other vertices", self.otherVertices)
        # print("path vertices", self.pathVertices)
        # print("path edges", self.pathEdges)
        H = nx.Graph()
        for (s,t) in self.pathEdges:
            H.add_edge(s,t,color=path_color)
        for (s,t) in self.otherEdges: 
            H.add_edge(s,t,color=other_color)
        for s in self.pathVertices:
            H.add_node(s,color=path_color)
        for s in self.otherVertices:
            H.add_node(s,color=other_color)
        edges = H.edges()
        nodes = H.nodes()
        ecolors = [H[u][v]['color'] for u,v in edges]
        ncolors =[H.nodes[u]['color'] for u in nodes]


        nx.draw(H,  edge_color=ecolors, node_color= ncolors, width=3,with_labels=True)

        plt.show()


def gen_visualizableGraph(G: StandardGraph) -> VisualizableGraph:
    return(VisualizableGraph(G=G,pathEdges=[],pathVertices=[],otherEdges=[],otherVertices=[]))


# def read_longest_path(filename, )-> VisualizableGraph:
#     return 

def visualize_graph(G, path=[]):
    VG = gen_visualizableGraph(G)
    len_path = len(path)
    path_edges= [(path[i],path[i+1]) for i in range(len_path-1)]
    VG.visualize(path=path_edges)


if __name__ == "__main__": 
    G=LinearGraph(15).expand(0.5)
    path =[]
    for i in range(15):
        path.append(i)
    visualize_graph(G,path=path)


# if __name__ == "__main__":
#     G=StandardGraph()
    


# G=LinearGraph(15).expand(0.5)
# VG = gen_visualizableGraph(G)
# path =[]
# for i in range(14):
#     path.append((i,i+1))
# VG.visualize(path=path)



