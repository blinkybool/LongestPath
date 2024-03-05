#include "neighbours_graph.h"
#include <stdio.h>
#include <string.h>

NeighboursGraph *new_graph(int vertices) {
	NeighboursGraph *graph = malloc(sizeof(NeighboursGraph) + sizeof(VertArray) * vertices);
	graph->vertices = vertices;

	for (int i=0; i<vertices; i++) {
		graph->adj[i].count = 0;
		graph->adj[i].elems = (int *) malloc(sizeof(int) * vertices);
	}

	return graph;
}

void add_edge(NeighboursGraph *graph, int source, int target) {
	graph->adj[source].elems[graph->adj[source].count++] = target;
}

void init_random_graph(NeighboursGraph *graph, float p, unsigned int random_seed) {
	srand(random_seed);
	int p_upper_rand = p * (float) RAND_MAX;
	for (int i = 0; i < graph->vertices; i++) {
		for (int j = 0; j < graph->vertices; j++) {
			if (rand() < p_upper_rand) add_edge(graph, i, j);
		}
	}
}

void init_random_undirected_graph(NeighboursGraph *graph, float p, unsigned int random_seed) {
	srand(random_seed);
	int p_upper_rand = (int) (p * (float) RAND_MAX);
	for (int i = 0; i < graph->vertices; i++) {
		for (int j = 0; j <= i; j++) {
			if (rand() < p_upper_rand) {
				add_edge(graph, i, j);
				if (i != j) add_edge(graph, j, i);
			}
		}
	}
}

void print_graph(NeighboursGraph *graph) {
	printf("%d\n", graph->vertices);
	for (int i = 0; i < graph->vertices; i++) {
		FOREACH_ARRAY(int, j, graph->adj[i], {
			printf("%d %d\n", i, j);
		})
	}
}

void print_undirected_graph(NeighboursGraph *graph) {
	printf("%d\n", graph->vertices);
	for (int i = 0; i < graph->vertices; i++) {
		FOREACH_ARRAY(int, j, graph->adj[i], {
			if (i <= j) printf("%d %d\n", i, j);
		})
	}
}

void free_graph(NeighboursGraph *graph) {
	for (int i=0; i<graph->vertices; i++) {
		graph->adj[i].count = 0;
		free(graph->adj[i].elems);
	}
	free(graph);
}

// True iff path is a non-empty and valid path in graph (i.e. the edges exist)
bool verify_path(VertArray *path, NeighboursGraph *graph) {
	assert(path->count > 0);

	for (int i=1; i < path->count; i++) {
		bool found_edge = false;
		FOREACH_ARRAY(int, adj_vertex, graph->adj[path->elems[i-1]], {
			if (adj_vertex == path->elems[i]) {
				found_edge = true;
				break;
			}
		})
		if (!found_edge) return false;
	}

	return true;
}

NeighboursGraph *read_graph(bool undirected) {
	int vertices;
	if (scanf("%d\n", &vertices) != 1){
		fprintf(stderr, "No graph provided.\n");
		exit(1);
	}

	NeighboursGraph *graph = new_graph(vertices);
	
	int source, target;
	int edges = 0;
	while (scanf("%d %d\n", &source, &target) == 2) {
		edges++;
		add_edge(graph, source, target);
		if (undirected) {
			add_edge(graph, target, source);
		}
	}

	printf("Read graph. vertices: %d, edges: %d\n", vertices, edges);

	return graph;
}

/*
Perform brute-force depth-first search for the longest path, writing answer
in best_path. Specify stop_at_max=true to shortcut search at hamiltonian path.
*/
void longest_path_brute_force(VertArray *best_path, NeighboursGraph *graph, bool stop_at_hamiltonian) {
	int v = graph->vertices;

	// The current path (so far)
	int *path = malloc(sizeof(int) * v);
	// The index of the edge chosen to get to path[i+1] from path[i]
	int *branch_indices = malloc(sizeof(int) * (v-1));

	// Lookup table for checking if 
	bool *path_set = malloc(sizeof(bool) * v);
	memset(path_set, false, v);
	
	int len = 1;
	int vertex = 0;
	// The index of the first edge out of `vertex` to try in the next loop
	// Also equals the number of edges out of `vertex` we've already tried.
	int branch_index = 0;
	bool backtrack;
	path_set[vertex] = true;

	// Each loop, either try to extend the path, or backtrack to try the next
	// edge out of the previous vertex.
	while (vertex < v) {

		backtrack = true;

		for (int i=branch_index; i<graph->adj[vertex].count; i++) {
			int next_vertex = graph->adj[vertex].elems[i];
			if (!path_set[next_vertex]) {
				// Extend path and update relevant state
				path[len] = next_vertex;
				branch_indices[len-1] = i;
				len++;
				path_set[next_vertex] = true;
				vertex=next_vertex;
				// Repeat this for loop instead of backtracking
				backtrack = false;
				branch_index = 0;
				break;
			}
		}

		if (backtrack) {
			// Found better path
			if (len > best_path->count) {
				memcpy(best_path->elems, path, sizeof(int)*len);
				best_path->count = len;
				if (stop_at_hamiltonian && (len == v)) break;
			}
			
			// Search from new start vertex
			if (len == 1) {
				path_set[vertex] = false;
				vertex++;
				path_set[vertex] = true;
				path[0] = vertex;
				backtrack = false;
				branch_index = 0;
				// printf("start:%d\n", node);
				continue;
			}

			// Rewind state to previous vertex with new branch_index
			vertex = path[len-2];
			branch_index = branch_indices[len-2]+1;
			path_set[path[len-1]] = false;
			len--;
		}
	}

	free(path);
	free(branch_indices);
	free(path_set);
}

typedef struct {
	VertArray stack;
	bool *ignore_set;
} DFS_State;

DFS_State new_DFS_State(int vertices) {
	DFS_State state;
	state.stack.elems = (int *) malloc(vertices * vertices * sizeof(int));
	state.ignore_set = (bool *) malloc(vertices * sizeof(bool));
	return state;
}

void free_DFS_State(DFS_State *state) {
	free(state->stack.elems);
	free(state->ignore_set);
}

// Pass dfs_state so memory can be re-used instead of allocated every time.
int subgraph_size_dfs(DFS_State *dfs_state, NeighboursGraph *graph, int start, bool *avoid_vertex_set) {
	dfs_state->stack.count = 1;
	dfs_state->stack.elems[0] = start;

	int visited = 0;
	memcpy(dfs_state->ignore_set, avoid_vertex_set, graph->vertices * sizeof(bool));
	while (dfs_state->stack.count > 0) {
		int vertex = dfs_state->stack.elems[--dfs_state->stack.count];
		if (!dfs_state->ignore_set[vertex]) {
			// Extend the stack with the neighbours of vertex
			memcpy(dfs_state->stack.elems + dfs_state->stack.count, graph->adj[vertex].elems, graph->adj[vertex].count * sizeof(int));
			dfs_state->stack.count += graph->adj[vertex].count;
			dfs_state->ignore_set[vertex] = true;
			visited++;
		}
	}

	return visited;
}

void longest_path_DFBnB(VertArray *best_path, NeighboursGraph *graph) {
	int v = graph->vertices;

	best_path->count = 0;
	DFS_State heuristic_dfs_state = new_DFS_State(v);

	// The current path (so far)
	int *path = malloc(sizeof(int) * v);
	// The index of the edge chosen to get to path[i+1] from path[i]
	int *branch_indices = malloc(sizeof(int) * (v-1));

	// Lookup table for vertices belonging to path
	bool *path_set = malloc(sizeof(bool) * v);
	memset(path_set, false, v);
	
	int len = 1;
	int vertex = 0;
	// The index of the first edge out of `vertex` to try in the next loop
	// Also equals the number of edges out of `vertex` we've already tried.
	int branch_index = 0;
	bool backtrack;
	path_set[vertex] = true;

	// Each loop, either try to extend the path, or backtrack to try the next
	// edge out of the previous vertex.
	while (vertex < v) {

		backtrack = true;

		for (int i=branch_index; i<graph->adj[vertex].count; i++) {
			int next_vertex = graph->adj[vertex].elems[i];
			if (!path_set[next_vertex]) {

				if (best_path->count > 0) {
					int future_path_bound = subgraph_size_dfs(&heuristic_dfs_state, graph, next_vertex, path_set);
					if (len + future_path_bound <= best_path->count) {
						// Continuing the path through next_vertex cannot yield a longer path than current solution
						continue;
					}
				}

				// Extend path and update relevant state
				path[len] = next_vertex;
				branch_indices[len-1] = i;
				len++;
				path_set[next_vertex] = true;
				vertex=next_vertex;
				// Repeat this for loop instead of backtracking
				backtrack = false;
				branch_index = 0;
				break;
			}
		}

		if (backtrack) {
			// Found better path
			if (len > best_path->count) {
				memcpy(best_path->elems, path, sizeof(int)*len);
				best_path->count = len;
				if (len == v) break;
			}
			
			// Search from new start vertex
			if (len == 1) {
				path_set[vertex] = false;
				vertex++;
				path_set[vertex] = true;
				path[0] = vertex;
				backtrack = false;
				branch_index = 0;
				// printf("start:%d\n", node);
				continue;
			}

			// Rewind state to previous vertex with new branch_index
			vertex = path[len-2];
			branch_index = branch_indices[len-2]+1;
			path_set[path[len-1]] = false;
			len--;
		}
	}

	free_DFS_State(&heuristic_dfs_state);
	free(path);
	free(branch_indices);
	free(path_set);
}