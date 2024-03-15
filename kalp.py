from standard_graph import StandardGraph, linear_graph
import os
import subprocess
from gen import gen_planted_path, gen_erdos_reyni_directed
import random
import numpy as np
from dotenv import dotenv_values
import re

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


def export_KaLP_dimacs(path: str, graph: StandardGraph, weights=lambda s, t: 1):
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
            f.write(f"a {s + 1} {t + 1} {weights(s, t)}\n")

def export_KaLP_dimacs_with_universal_nodes(path: str, graph: StandardGraph):
    graph = graph.clone()
    graph.add_universal_nodes()

    univ = {graph.vertices - 1, graph.vertices - 2}

    export_KaLP_dimacs(
        path, 
        graph,
        lambda s, t: 0 if s in univ or t in univ else 1
    )


def export_KaLP_metis(path: str, graph: StandardGraph):
    undirected = {frozenset([s, t]) for s, t in graph.edges}
    undirected_list = [tuple(e) for e in undirected if len(e) > 1]

    neighbor_dict = {v : set() for v in range(graph.vertices)}

    for (s, t) in undirected_list:
        neighbor_dict[s].add(t)
        neighbor_dict[t].add(s)

    with open(path, "w") as f:
        f.write(f"{graph.vertices} {len(undirected_list)}\n")

        for v in range(graph.vertices):
            neighbors = neighbor_dict[v]
            f.write(" ".join(str(u + 1) for u in neighbors) + "\n")

def export_KaLP_metis_with_universal_nodes(path: str, graph: StandardGraph):
    graph = graph.clone()
    graph.add_universal_nodes()

    # univ = {graph.vertices - 1, graph.vertices - 2}

    export_KaLP_metis(
        path, 
        graph,
    )

def check_KaLP_metis(
    path: str, 
    kalp_graphchecker_path = (dotenv_values(".env")["KALP_PATH"] + "/graphchecker")
    ):
    result = subprocess.run(
        [kalp_graphchecker_path, path], 
        stdout=subprocess.PIPE, 
        text=True
    )
    return result.stdout

def run_KaLP_with_start_and_target(
        path: str, 
        start, 
        target,
        threads=None,
        steps=None,
        partition_configuration=None,
        kalp_path = (dotenv_values(".env")["KALP_PATH"] + "/kalp")
    ):
    """
    Runs KaLP on the file specified by `path`. 
    NOTE: Uses the environment variable KALP_PATH by default if the argument kalp_path is not provided.

    Note that start and target here should be between 0 and nr_vertices - 1.
    """
    command = [
        kalp_path, 
        path, 
        f'--start_vertex={start}', 
        f'--target_vertex={target}', 
        '--print_path'
    ]

    if threads != None:
        command.append(f"--threads={threads}")
    if steps != None:
        command.append(f"--steps={steps}")
    if partition_configuration != None:
        command.append(f"--partition_configuration={partition_configuration}")

    result = subprocess.run(
        command, 
        stdout=subprocess.PIPE, 
        text=True
    )

    if result.returncode != 0:
        print("result")
        print(result)
        print("stderr")
        print(result.stderr)
        raise RuntimeError("Executable exited with error.")


    lines = result.stdout.splitlines()

    path = []

    while len(lines) > 0:
        line = lines.pop()
        if line.strip().isdigit():
            path.append(int(line))
        else:
            break

    return path, result.stdout

def run_KaLP_with_universal_nodes(path: str, *args, **kwargs):
    """
    Runs KaLP using `run_KaLP_with_start_and_target` to find the longest path in a graph specified by `path`.
    This is inteded to be used on files generated by `export_KaLP_dimacs_with_universal_nodes`.
    """
    nr_vertices = None

    with open(path, 'r') as f:
        nr_vertices = int(f.readline().split(" ")[2])

    path, stdout = run_KaLP_with_start_and_target(path, nr_vertices - 2, nr_vertices - 1, *args, **kwargs)

    if len(path) > 2:
        return path[1:-1], stdout
    else:
        return [], stdout

def run_KaLP_universal(file_path: str, *args, **kwargs):
    nr_vertices = None

    if re.search(r".*\.dimacs$", file_path) != None:
        with open(file_path, 'r') as f:
            nr_vertices = int(f.readline().split(" ")[2])
    elif re.search(r".*\.graph$", file_path) != None:
        with open(file_path, 'r') as f:
            nr_vertices = sum(1 for _ in f) - 2
    else:
        raise ValueError(f"File should have .graph or .dimacs extension but the path is: {path}")

    longest_path = []

    for s in range(nr_vertices):
        for t in range(0, s):
            path, stdout = run_KaLP_with_start_and_target(file_path, s, t, *args, **kwargs)
            if len(path) > len(longest_path):
                longest_path = path

    return longest_path

if __name__ == "__main__":
    random.seed(0)
    np.random.seed(0)
    G = gen_planted_path(20, 0)

    # export_KaLP_metis("test.graph", G)
    export_KaLP_metis_with_universal_nodes("test.graph", G)
    print(check_KaLP_metis("test.graph"))

    # export_KaLP_dimacs_with_universal_nodes("test.dimacs", G)
    # export_KaLP_dimacs("test.dimacs", G)
    # print(check_KaLP_dimacs_format("test.dimacs")[0])
    
    path, stdout = run_KaLP_with_start_and_target(
        "test.graph", 0, 19,
        threads=8
    )
    # path, stdout = run_KaLP_with_start_and_target("../KaLP/examples/maze_one.dimacs", 
    #     1422, 1462,
    #     threads=4, 
    #     partition_configuration="fast"
    # )

    print(stdout)
    print(path)
