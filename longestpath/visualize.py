import math, random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt 
from dataclasses import dataclass
from .gen import *
from typing import List, Tuple, Callable

@dataclass
class VisualizableGraph:
    """
    We want to split a graph into two parts:
    1. The path
    2. The remainder of the graph
    We do this, because we want the path to have a different color than the 
    remainder of the graph
    """
    G:StandardGraph 
    pathVertices: List[int]
    pathEdges: List[Tuple[int, int]]
    otherVertices: List[int]
    otherEdges: List[Tuple[int,int]]

  
    def separate(self, path):
        """
    Given a path, this function divides the vertices of the graph into two groups.
    One group consists of all edges and vertices which are in the path.
    The other group consists of the remaining of the edges and vertices.  
        """
        #separate the edges
        for (s,t) in self.G.edges:
            if (s,t) in path:
                self.pathEdges.append((s,t))
            else:
                self.otherEdges.append((s,t))
        
        #separate the vertices
        vertexInPath =[]
        for (s,t) in path:
            vertexInPath.append(s)
            vertexInPath.append(t)
        for vertex in range (self.G.vertices):
            if vertex in vertexInPath:
                self.pathVertices.append(vertex)
            else:
                self.otherVertices.append(vertex)


    def visualize(self, path, path_color='r', other_color='b', width= 3):
        """
        Make a visualized undirected graph
        It is possible to adjust the color of the path, the color of the 
        vertices not in the path, and the width of the arrows.
        """
        self.separate(path)

        #make the code compatible with networkx
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

        #plot the figure
        plt.figure(figsize =(9, 9)) 
        nx.draw(H,  edge_color=ecolors, node_color= ncolors, 
                width=width,with_labels=True)
        plt.show()

    def visualize_directed(self, path, path_color='r', other_color='b', width =2):
        """
        Make a visualized directed graph 
        """
        self.separate(path)

        #make the code compatible with networkx
        H = nx.DiGraph()
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

        #plot the figure
        plt.figure(figsize =(9, 9))
        nx.draw(H,  edge_color=ecolors, node_color= ncolors,
                 width=width, with_labels=True )
        plt.show()


def gen_visualizableGraph(G: StandardGraph) -> VisualizableGraph:
    "Generate a visualizable graph datastructure"
    return(VisualizableGraph(G=G,pathEdges=[],pathVertices=[],otherEdges=[],otherVertices=[]))


def visualize_graph(G, path=[],directed= True, width =2):
    """
    Visualize graph, we can choose whether the graph is directed or undirected. 
    Add a graph and a path. A path is a list of vertices.
    """

    #generate a visualizableGraph datastructure
    VG = gen_visualizableGraph(G)
    len_path = len(path)

    #Define all the edges of the path
    if(len_path ==0):
        path_edges =[]
    else:
        path_edges= [(path[i],path[i+1]) for i in range(len_path-1)]
    
    #visualize the graph
    if(directed==False):
        VG.visualize(path=path_edges, width=width)
    else:
        VG.visualize_directed(path=path_edges, width=width)






