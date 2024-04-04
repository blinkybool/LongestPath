from pyqubo import Array, LogEncInteger
import neal
from longestpath import gen_average_degree_directed, gen_planted_path, StandardGraph, gen_num_edges, gen_num_edges_no_loops
from typing import List
from longestpath import brute
import multiprocessing
from .utils import with_timed_result

class QUBO_Edge_Solver:
    def __init__(self, graph: StandardGraph, max_length_path: int | None = None):
        if max_length_path is None:
            max_length_path = graph.vertices-1
                        
        self.graph = graph
        self.max_length_path = max_length_path

    # This function turns a graph into new graph with a tail of specified length.
    # All vertices in the original graph are connected to the beginning of the tail.
    def make_tail_graph(self, tail_length : int) -> StandardGraph:
        graph = self.graph

        if tail_length == 0:
            tail_graph = StandardGraph(0, [])
            tail_graph.vertices += graph.vertices
            tail_graph.edges = graph.edges.copy()
            return tail_graph

        # We set the vertex amount of tail_graph and copy the edges of the original graph into tail_graph.edges.
        tail_graph = StandardGraph(0, [])
        tail_graph.vertices += graph.vertices + tail_length
        tail_graph.edges = graph.edges.copy()
        
        
        # The tail part starts at index graph.vertices.
        # We connect all the original vertices to the beginning of the tail.
        for i in range(0,graph.vertices):
            tail_graph.edges.append((i,graph.vertices))
        
        #We add the connections within the tail.
        for i in range(graph.vertices , graph.vertices + tail_length - 1):
            tail_graph.edges.append((i, i+1))

        return tail_graph

    # This functions computes for every vertex in a graph the indices of the edges that are connected to a specific vertex.
    # These collections of indices are stored in lists of integers.
    # The lists are then stored in an outer list of which the indices correspond to the vertices of the graph.
    def make_vertex_edges(self) -> List[List[int]] :
        graph = self.tail_graph
        out = [[] for i in range(graph.vertices)]

        for i in range(len(graph.edges)):
            (v_1, v_2) = graph.edges[i]
            
            out[v_1].append(i)
            out[v_2].append(i)
        
        return out

    # We endow an orientation on all the edged in a graph.
    # Edge (i,j) goes from i to j.
    # With respect to this orientation, we compute for each vertex in a graph which edges point towards that vertex
    def make_in_flow_edges(self) -> List[List[int]] :
        graph = self.tail_graph
        out = [[] for i in range(graph.vertices)]

        for i in range(len(graph.edges)):
            (_, v_2) = graph.edges[i]

            out[v_2].append(i)
        
        return out

    #We also compute, for each vertex, which edges point away from that vertex
    def make_out_flow_edges(self) -> List[List[int]] :
        graph = self.tail_graph
        out = [[] for i in range(graph.vertices)]

        for i in range(len(graph.edges)):
            (v_1, _) = graph.edges[i]

            out[v_1].append(i)
        
        return out
    
    def generate_bqm(self):
        
        # N is the amount of vertices in the graph
        # K is the maximal length of a path that the algorithm can find
        # P is the penalty value that we use for the QUBO algorithm

        N = self.graph.vertices
        K = self.max_length_path
        P = -N

		# We add a tail to the original graph as is described in the report.
        self.tail_graph = self.make_tail_graph(K)
        tail_graph = self.tail_graph

        # For each vertex we compute which edges are connected to it.
        tail_vertex_edges = self.make_vertex_edges()

        # We view all edges as oriented edges and store for each vertex
        # the ingoing and outgoing edges.
        out_flow_edges = self.make_out_flow_edges()
        in_flow_edges = self.make_in_flow_edges()

        # We formulate the problem as a maximization problem.

        # We create for each vertex a binary variable that indicates if that vertex is on the path.

        vertex_vars = Array.create('vertex', tail_graph.vertices, vartype='BINARY')

        # For each edge in the graph with tail, we create a binary value that indicates if that edge is used in the path.
        # We also consider edges from an initial and terminal "vertex". The values of these variables indicate where a path begins and ends.

        edge_vars = Array.create('edge', len(tail_graph.edges), vartype='BINARY')
        initial_edge_vars = Array.create('init_edge', graph.vertices, vartype='BINARY')
        terminal_edge_vars = Array.create('term_edge', tail_graph.vertices, vartype='BINARY')

        # For each edge (with initial and terminal edges included) we store a inetger flow value in the possitive dirrection of the edges.
        # A flow value can be at most K + 2 and must be at least 0.

        flow_vars = [LogEncInteger(f"flow_vars[{i}]", (0,K + 2)) for i in range(len(tail_graph.edges))]
        initial_flow_vars = [LogEncInteger(f"initial_flow_vars[{i}]", (0,K + 2)) for i in range(graph.vertices)] #assumed to be ingoing
        terminal_flow_vars = [LogEncInteger(f"terminal_flow_vars[{i}]", (0,K + 2)) for i in range(tail_graph.vertices)] #assumed to be outgoing
        # We also store flow values for the negative directions of edges.

        contra_flow_vars = [LogEncInteger(f"contra_flow_vars[{i}]", (0,K + 2)) for i in range(len(tail_graph.edges))]
        initial_contra_flow_vars = [LogEncInteger(f"initial_contra_flow_vars[{i}]", (0,K + 2)) for i in range(graph.vertices)] #assumed to be outgoing
        terminal_contra_flow_vars = [LogEncInteger(f"terminal_contra_flow_vars[{i}]", (0,K + 2)) for i in range(tail_graph.vertices)] #assumed to be ingoing

        # This variable will store the matrix for the qubo formulation in the form of a quadratic expression.
        qubo_matrix_expression = 0

        #This part of the expression rewards longer paths which 1 point per used edge.
        candy_exp = sum(edge_vars[i] for i in range(len(graph.edges)))
        qubo_matrix_expression += candy_exp

        # This part of the expression results in a penalty if multiple initial edges are used.
        initial_node_exp = P * (1 - sum(initial_edge_vars[i] for i in range(graph.vertices)))**2
        qubo_matrix_expression += initial_node_exp

        # This part of the expression results in a penalty if multiple terminal edges are used.
        terminal_node_exp = P * (1 - sum(terminal_edge_vars[i] for i in range(tail_graph.vertices)))**2
        qubo_matrix_expression += terminal_node_exp

        # This part of the expression results in a penalty if multiple vertices are connected to the beginning of the tail.
        fake_terminal_node_exp_1 = P * (vertex_vars[graph.vertices] - sum(edge_vars[i] for i in range( len(graph.edges), len(graph.edges) + graph.vertices)))**2
        qubo_matrix_expression += fake_terminal_node_exp_1

        # This part of the expression results in a penalty if second vertex in the tail is used without using the beginning of the tail.
        fake_terminal_node_exp_2 = P * (1 - vertex_vars[graph.vertices]) * vertex_vars[graph.vertices + 1]
        qubo_matrix_expression += fake_terminal_node_exp_2

        # This part of the expression results in a penalty if there are not exactly 2 edges used that are connected to the same vertex while that vertex lies on the path.
        # If a vertex does not lie on the path it results in a penalty if any more than 0 connected edges are used.
        # We also consider the terminal and intial edges in this case.
        real_node_deg_2_exp = 0
        for i in range(tail_graph.vertices):
            temp1 = sum(edge_vars[tail_vertex_edges[i][j]] for j in range(len(tail_vertex_edges[i])))
            
            temp1 += terminal_edge_vars[i]

            # Only vertices from the input graph are connected to initial edges
            if i < graph.vertices:
                temp1 += initial_edge_vars[i]

            # For vertex i we make sure that exactly 0 or 2 connected edges are used (depending on if the vertex lies on the path)
            real_node_deg_2_exp += P * (2 * vertex_vars[i] - temp1)**2

        qubo_matrix_expression += real_node_deg_2_exp

        #This part of the expression results in a penalty if the flow and contra flow values of any edge that is used do not add up to K + 3.
        pairing_flow_exp = P * sum([((K + 3) * edge_vars[i] - flow_vars[i] - contra_flow_vars[i])**2 for i in range(len(edge_vars))])

        pairing_flow_exp += P * sum([((K + 3) * initial_edge_vars[i] - initial_flow_vars[i] - initial_contra_flow_vars[i])**2 for i in range(len(initial_edge_vars))])

        pairing_flow_exp += P * sum([((K + 3) * terminal_edge_vars[i] - terminal_flow_vars[i] - terminal_contra_flow_vars[i])**2 for i in range(len(terminal_edge_vars))])
            
        qubo_matrix_expression += pairing_flow_exp

        # This part of the expression makes sure that value of the initial flow and the value of the contra terminal flow are both equal to 1.
        set_initial_flow_exp = P * (1 - sum([a for a in initial_flow_vars]))**2
        set_terminal_flow_exp = P * (1 - sum(b for b in terminal_contra_flow_vars))**2

        qubo_matrix_expression += set_initial_flow_exp + set_terminal_flow_exp

        # This part of the expression results in a penalty if the total ingoing flow in any vertex that lies on the path is unequal to K + 2
        # For vertices that do not lie on the path the expression results in a penalty if the total ingoing flow is unequal to 0.
        set_out_flow_exp = 0
        for i in range(tail_graph.vertices):
            #For each vertex we set the value that the ingoing flow must be
            temp_exp = (K+2) * vertex_vars[i]

            # For each connected vertex we subtract the corresponging ingoing flow value
            if i < graph.vertices:
                temp_exp += -initial_flow_vars[i]
            temp_exp += -terminal_contra_flow_vars[i]
            temp_exp += -sum([contra_flow_vars[j] for j in out_flow_edges[i]])
            temp_exp += -sum([flow_vars[j] for j in in_flow_edges[i]])

            temp_exp = temp_exp**2

            set_out_flow_exp += P * temp_exp	

        qubo_matrix_expression += set_out_flow_exp

        # We take the negative version of the expression to turn the maximization problem into a minimization problem.
        qubo_matrix_expression = - qubo_matrix_expression
        model = qubo_matrix_expression.compile()
        bqm = model.to_bqm()
        return bqm
    
    def get_bqm(self):
        if not hasattr(self, "bqm"):
            self.bqm = self.generate_bqm()
        return self.bqm

    def get_default_beta_range(self):
        bqm = self.get_bqm()
        return neal.sampler.default_beta_range(bqm)


    def sample(self, **kwargs):
        bqm = self.get_bqm()
        sa = neal.SimulatedAnnealingSampler()
        sampleset = sa.sample(bqm, **kwargs)
        return sampleset

    @with_timed_result
    def solve(self, **sampler_kwargs):
        sampleset = self.sample(**sampler_kwargs)
        best_sample = sampleset.first
        return self.sample_to_result(best_sample)
    
    def solve_for_sample(self, **sampler_kwargs):
        sampleset = self.sample(**sampler_kwargs)
        best_sample = sampleset.first
        return best_sample

    def sample_to_result(self, sample):
        multi_path = []
        result = {"reward": -sample.energy, 'multi_path': multi_path}
        return result

if __name__ == "__main__":
    n = 3
    d = 1
    graph = gen_num_edges_no_loops(n, round(n * d))

    print(graph)

    # graph = StandardGraph(3, [
	# (0,1),
    # (1,2),
    # ])

    def pretty_result(result):
        info = {k:v for k,v in result.items() if type(v) in [int, float, str]}
        if "path" in result:
            info["length"] = len(result['path'])-1
            format_str = "{:>3},"*len(result['path'])
            return str(info) + "\n" + format_str.format(*list(map(str, result['path'])))
        else:
            return str(info)

    brute_result = brute.solve(multiprocessing.Queue(), graph, "BRANCH_N_BOUND")
    print("BRUTE", pretty_result(brute_result))

    solver = QUBO_Edge_Solver(graph)
    min_beta, max_beta = solver.get_default_beta_range()
    result = solver.solve(num_reads=10_000, num_sweeps=1000, beta_range=(0.1, 0.5*max_beta))
    print("QUBOSolver", result)# pretty_result(result))
    