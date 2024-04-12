from collections import defaultdict
from longestpath import StandardGraph, gen_num_edges
import numpy as np
from typing import List, Set, Tuple, Dict
from longestpath import brute
from .utils import with_timed_result

def compute_inserts(graph: StandardGraph) -> Dict[Tuple[int, int], List[int]]:
    '''
    Computes the list of vertices that can be inserted between any two vertices in the graph.
    Keys are pairs of vertices, values are lists of vertices that can be inserted between them.
    The special key (-1,-1) corresponds to the empty path.
    The special key (-1, v) corresponds to inserting v at the beginning of the path.
    The special key (v, -1) corresponds to inserting v at the end of the path.
    '''
    inserts = defaultdict(list)

    for (a,b) in graph.edges:
        if a == b:
            continue
        # Prepending and appending
        inserts[(-1, b)].append(a)
        inserts[(a, -1)].append(b)
        # Inserting into the empty path []
        inserts[(-1,-1)].append(a)
        inserts[(-1,-1)].append(b)
        
        for (b2,c) in graph.edges:
            if b == b2 and c != b and c != a:
                inserts[(a,c)].append(b)

    for pair, vertices in inserts.items():
        inserts[pair] = list(set(vertices))

    return inserts

SWAP = 0
INSERT = 1
DELETE = 2
def nudge_path(path: List[int],
        edge_set: Set[Tuple[int,int]],
        inserts: Dict[Tuple[int, int], List[int]],
        temp: float):
    '''
    Modifies the path in-place by swapping, inserting, or deleting a vertex.
    Returns whether the path is a local maximum (cannot be improved by a single nudge)
    '''
    moves = []
    n = len(path)

    # Compute inserts
    # (INSERT, (i,v)) corresponds to inserting v into the path at index i
    for i in range(n-1):
        moves.extend((INSERT, (i+1, v)) for v in inserts[(path[i], path[i+1])] if v not in path)
    if n == 0:
        moves.extend((INSERT, (0, v)) for v in inserts[(-1, -1)])
    else:
        moves.extend((INSERT, (0, v)) for v in inserts[(-1, path[0])] if v not in path)
        moves.extend((INSERT, (n, v)) for v in inserts[(path[-1], -1)] if v not in path)

    local_max = len(moves) == 0
    
    # Compute deletes
    if temp is not None:
        for i in range(n):
            if i == 0 or i == n-1 or (path[i-1], path[i+1]) in edge_set:
                moves.append((DELETE, i))
    
    if len(moves) == 0:
        return local_max
    
    # Choose random move
    kind, data = moves[np.random.randint(0, len(moves))]

    # Make the move (but if it's a shorter path, check against temp)
    if kind == SWAP:
        i, j = data
        path[i], path[j] = path[j], path[i]
    elif kind == INSERT:
        i, v = data
        path.insert(i, v)
    elif kind == DELETE:
        i = data
        delta = 1.0 if (i == 0 or i == n-1) else 2.0
        if np.random.rand() < np.exp(-delta/temp):
            path.pop(i)
    else:
        raise ValueError("Invalid move kind")
    
    # Uncomment this to validate the path
    for (u,v) in zip(path[:-1], path[1:]):
        if (u,v) not in edge_set:
            raise ValueError(f"Invalid path. No edge {u} -> {v}")

    return local_max

def anneal(
        edge_set: Set[Tuple[int,int]],
        inserts: Dict[Tuple[int,int],List[int]],
        num_sweeps: int = 64,
        alpha: float = 0.9,
        initial_temp: float = 1.0,
        final_temp: float = 0.00122) -> List[int]:
    path = []
    temp = initial_temp
    while temp > final_temp:
        for _ in range(num_sweeps):
            local_max = nudge_path(path, edge_set, inserts, temp)
        while not local_max:
            local_max = nudge_path(path, edge_set, inserts, None)

        temp *= alpha
    return path

def solve(graph: StandardGraph, use_known_length: bool = False, process_queue=None, num_reads=100, **anneal_kwargs):
    if use_known_length:
        until_length = graph.get_known_longest_path_length()
    else:
        until_length = graph.vertices-1
    inserts = compute_inserts(graph)
    edge_set = set(graph.edges)

    best = []
    for _ in range(num_reads):
        path = anneal(edge_set, inserts, **anneal_kwargs)
        if len(path) > len(best):
            best = path
            if len(path)-1 >= until_length:
                break
    return {"path": best}

def main():
    n = 30
    d = 2
    graph = gen_num_edges(n, round(n*d))

    def pretty_result(result):
        info = {k:v for k,v in result.items() if type(v) in [int, float, str]}
        if "path" in result:
            info["length"] = len(result['path'])-1
            format_str = "{:<3}"*len(result['path'])
            return str(info) + "\n" + format_str.format(*list(map(str, result['path'])))
        else:
            return str(info)

    brute_result = brute.solve(graph, "BRANCH_N_BOUND")
    actual_length = len(brute_result['path'])-1
    print("brute", pretty_result(brute_result))
    graph.set_known_longest_path_length(actual_length)
    print("anneal", pretty_result(with_timed_result(solve)(graph, use_known_length=True, num_reads=100, num_sweeps=32)))


if __name__ == "__main__":
    main()