from standard_graph import StandardGraph, linear_graph

def check_KaLP_dimacs_format(path: str):
    nr_vertices = None
    nr_edges = None
    edges = []
    with open(path, "r") as f:
        for i, line in enumerate(f):
            l = line.split(" ")

            if len(l) != 4: return f"Wrong format at line {i + 1}"

            if i == 0:
                if l[0] != 'p': return f"First line does not start with 'p'."
                if l[1] != 'sp': return f"First line does not include 'sp'."
                nr_vertices = int(l[2])
                nr_edges = int(l[3])
            else:
                if l[0] != 'a': return f"Line {i + 1} does not start with 'a'"
                if l[3].strip() != '1': return f"Line {i + 1} does not end with '1'"
                edges.append((int(l[1]), int(l[2])))

    if len(edges) != nr_edges: return f"Number of edges is incorrect: {nr_edges} claimed but there are {len(edges)}."

    vertices = set([v for (v, _) in edges] + [v for (_, v) in edges])

    if min(vertices) <= 0: return f"Vertices must be greater than or equal to 1."
    if max(vertices) > nr_vertices: return f"Number of vertices is incorrect: {nr_vertices} claimed but there is a vertex of number '{max(vertices)}'"

    undirected = {frozenset([s, t]) for s, t in edges}
    undirected_list = [tuple(e) for e in undirected]
    undirected_directed_list = undirected_list + [(t, s) for (s, t) in undirected_list]

    edges.sort()
    undirected_directed_list.sort()

    if edges != undirected_directed_list: return "Graph format incorrect. NOTE: The graph should contain all back edges."

    return "Correct", StandardGraph(nr_vertices, [(s - 1, t - 1) for (s, t) in edges])

def export_KaLP_dimacs(path: str, graph: StandardGraph):
    """
    Writes a graph to a dimacs file in a format that KaLP will accept.
    WARNING: KaLP wants vertices to be >= 1 so all vertices are shifted over by +1 in the output file. Note that the kalp command wants start and target vertex starting from 0 so KaLP subtracts 1 again.
    WARNING: KaLP only accepts undirected graphs. Hence this function turns the graph into an undirected one by adding all back edges. Moreover, all selfloops are removed.
    """

    undirected = {frozenset([s, t]) for s, t in graph.edges}
    undirected_list = [tuple(e) for e in undirected if len(e) > 1]
    undirected_directed_list = undirected_list + [(t, s) for (s, t) in undirected_list]

    with open(path, "w") as f:
        f.write(f"p sp {graph.vertices} {len(undirected_directed_list)}\n")

        for s, t in undirected_directed_list:
            f.write(f"a {s + 1} {t + 1} 1\n")

def export_KaLP_dimacs_with_universal_nodes(path: str, graph: StandardGraph):
    graph = graph.clone()
    graph.add_universal_nodes()
    export_KaLP_dimacs(path, graph)


if __name__ == "__main__":
	# print(check_KaLP_dimacs_format("datasets/rob-top/rob-top2000-KALP.dimacs"))
    export_KaLP_dimacs_with_universal_nodes("test.dimacs", linear_graph(3))
    print(check_KaLP_dimacs_format("test.dimacs"))
