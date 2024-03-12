
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

    if max(vertices) > nr_vertices: return f"Number of vertices is incorrect: {nr_vertices} claimed but there is a vertex of number '{max(vertices)}'"

    undirected = {frozenset([s, t]) for s, t in edges}
    undirected_list = [tuple(e) for e in undirected]
    undirected_directed_list = undirected_list + [(t, s) for (s, t) in undirected_list]

    edges.sort()
    undirected_directed_list.sort()

    if edges != undirected_directed_list: return "Graph format incorrect. NOTE: The graph should contain all back edges."

    return "Correct", nr_vertices, nr_edges, max(vertices)


if __name__ == "__main__":
	print(check_KaLP_dimacs_format("datasets/rob-top/rob-top2000-KALP.dimacs"))