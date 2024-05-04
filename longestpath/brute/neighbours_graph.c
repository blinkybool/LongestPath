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

NeighboursGraph *read_graph(bool undirected, FILE *file) {
	int vertices;
	if (fscanf(file, "%d\n", &vertices) != 1){
		fprintf(stderr, "No graph provided.\n");
		exit(1);
	}

	NeighboursGraph *graph = new_graph(vertices);
	
	int source, target;
	int edges = 0;
	while (fscanf(file, "%d %d\n", &source, &target) == 2) {
		edges++;
		add_edge(graph, source, target);
		if (undirected) {
			add_edge(graph, target, source);
		}
	}

	printf("Read graph.\n");
	printf("vertices: %d\n", vertices);
	printf("edges: %d\n", edges);
	printf("directed: %s\n", undirected ? "false" : "true");
	return graph;
}

static inline void log_found_path(FILE *prog, VertArray *path) {
	fprintf(prog, "LOG: Found path %d -> %d (length %d)\n", path->elems[0], path->elems[1], path->count-1);
	fprintf(prog, "path:");
	FOREACH_ARRAY(int, vertex, (*path), {
		fprintf(prog, " %d", vertex);
	});
	fprintf(prog, "\n");
	fflush(prog);
}

/*
Perform brute-force depth-first search for the longest path, writing answer
in best_path. Specify stop_at_max=true to shortcut search at hamiltonian path.
*/
void longest_path_brute_force(VertArray *best_path, NeighboursGraph *graph, bool stop_at_hamiltonian, FILE *prog) {
	int v = graph->vertices;

	// The current path (so far)
	int *path = malloc(sizeof(int) * v);
	// The index of the edge chosen to get to path[i+1] from path[i]
	int *branch_indices = malloc(sizeof(int) * (v-1));

	// Lookup table for checking if 
	int *path_set = malloc(sizeof(int) * v);
	memset(path_set, 0, sizeof(int) * v);
	
	int len = 1;
	int vertex = 0;
	// The index of the first edge out of `vertex` to try in the next loop
	// Also equals the number of edges out of `vertex` we've already tried.
	int branch_index = 0;
	bool backtrack;
	path_set[vertex] = true;
	best_path->count = 0;

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
				if (prog != NULL) log_found_path(prog, best_path);
				if (stop_at_hamiltonian && (len == v)) break;
			}
			
			// Search from new start vertex
			if (len == 1) {
				path_set[vertex] = 0;
				vertex++;
				if (vertex >= v) break;
				path_set[vertex] = 1;
				path[0] = vertex;
				backtrack = false;
				branch_index = 0;
				// printf("start:%d\n", node);
				continue;
			}

			// Rewind state to previous vertex with new branch_index
			vertex = path[len-2];
			branch_index = branch_indices[len-2]+1;
			path_set[path[len-1]] = 0;
			len--;
		}
	}

	free(path);
	free(branch_indices);
	free(path_set);
}

typedef struct {
	VertArray stack;
	int *ignore_set;
} DFS_State;

DFS_State *new_DFS_State(int vertices) {
	DFS_State *state = (DFS_State *) malloc(sizeof(DFS_State));
	state->stack.elems = (int *) malloc(vertices * vertices * sizeof(int));
	state->ignore_set = (int *) malloc(vertices * sizeof(int));
	return state;
}

void free_DFS_State(DFS_State *state) {
	free(state->stack.elems);
	free(state->ignore_set);
	free(state);
}

// Pass dfs_state so memory can be re-used instead of allocated every time.
int subgraph_size_dfs(DFS_State *dfs_state, NeighboursGraph *graph, int start, int *avoid_vertex_set) {
	dfs_state->stack.count = 1;
	dfs_state->stack.elems[0] = start;

	int visited = 0;
	memcpy(dfs_state->ignore_set, avoid_vertex_set, graph->vertices * sizeof(int));
	while (dfs_state->stack.count > 0) {
		int vertex = dfs_state->stack.elems[--dfs_state->stack.count];
		if (!dfs_state->ignore_set[vertex]) {
			// Extend the stack with the neighbours of vertex
			memcpy(dfs_state->stack.elems + dfs_state->stack.count, graph->adj[vertex].elems, graph->adj[vertex].count * sizeof(int));
			dfs_state->stack.count += graph->adj[vertex].count;
			dfs_state->ignore_set[vertex] = 1;
			visited++;
		}
	}

	return visited;
}

void longest_path_branch_and_bound(VertArray *best_path, NeighboursGraph *graph, FILE *prog) {
	int v = graph->vertices;

	best_path->count = 0;
	DFS_State *heuristic_dfs_state = new_DFS_State(v);

	// The current path (so far)
	int *path = malloc(sizeof(int) * v);
	// The index of the edge chosen to get to path[i+1] from path[i]
	int *branch_indices = malloc(sizeof(int) * (v-1));

	// Lookup table for vertices belonging to path
	int *path_set = malloc(sizeof(int) * v);
	memset(path_set, 0, sizeof(int) * v);
	
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
					int future_path_bound = subgraph_size_dfs(heuristic_dfs_state, graph, next_vertex, path_set);
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
				if (prog != NULL) log_found_path(prog, best_path);
				if (len == v) break;
			}
			
			// Search from new start vertex
			if (len == 1) {
				path_set[vertex] = 0;
				vertex++;
				if (vertex >= v) break;
				path_set[vertex] = 1;
				path[0] = vertex;
				backtrack = false;
				branch_index = 0;
				// printf("start:%d\n", node);
				continue;
			}

			// Rewind state to previous vertex with new branch_index
			vertex = path[len-2];
			branch_index = branch_indices[len-2]+1;
			path_set[path[len-1]] = 0;
			len--;
		}
	}

	free_DFS_State(heuristic_dfs_state);
	free(path);
	free(branch_indices);
	free(path_set);
}

typedef struct {
	int vertex;
	int in_degree;
} VertexInfo;

int compare_in_degree(const void *a, const void *b) {
	return ((VertexInfo *) b)->in_degree - ((VertexInfo *) a)->in_degree;
}

void sort_vertices_by_in_degree(NeighboursGraph *graph, int *sorted_vertices) {
	int num_vertices = graph->vertices;

	VertexInfo *vertex_infos = malloc(sizeof(VertexInfo) * num_vertices);

	for (int i = 0; i < num_vertices; ++i) {
		vertex_infos[i].vertex = i;
		vertex_infos[i].in_degree = 0;
	}

	// Iterate over every edge. Whenever an edge i->j is found, increment j's in-degree
	for (int i = 0; i < num_vertices; ++i) {
		int *adj_vertices = graph->adj[i].elems;
		int d = graph->adj[i].count;
		for (int j = 0; j < d; ++j) {
			int neighbor = adj_vertices[j];
			++vertex_infos[neighbor].in_degree;
		}
	}

	qsort(vertex_infos, num_vertices, sizeof(VertexInfo), compare_in_degree);
	
	for (int i = 0; i < num_vertices; ++i) {
		sorted_vertices[i] = vertex_infos[i].vertex;
	}

	// Free the dynamically allocated memory
	free(vertex_infos);
}

void longest_path_fast_bound(VertArray *longest_path, NeighboursGraph *graph, FILE *prog) {
	int num_vertices = graph->vertices;

	// The current path which we are building and backtracking
	int *path = malloc(sizeof(int) * num_vertices);
	// The index of the edge chosen to get to path[i+1] from path[i]
	// When we backtrack, we continue search from the next index.
	int *branch_indices = malloc(sizeof(int) * (num_vertices-1));
	
	// The number of vertices in the current path array
	int len;
	// The vertex at the end of the current path
	int vertex;
	// The index of the first edge out of `vertex` to try in the next loop
	// Also equals the number of edges out of `vertex` we've already tried.
	int branch_index;
	// Flag to trigger backtracking logic in the loop
	bool backtrack;

	// Lookup table for vertices belonging to path
	int *path_set = malloc(sizeof(int) * num_vertices);
	memset(path_set, 0, sizeof(int) * num_vertices);

	// If k = upperbound_from[i] then either k is either -1 (no upper bound known)
	// or every path starting from vertex i is known to have length at most k.
	int *upperbound_from = malloc(sizeof(int) * num_vertices);
	memset(upperbound_from, -1, sizeof(int) * num_vertices);

	// We update longest_path whenever a longer path is found
	longest_path->count = 0;

	// Vertices with higher in-degree are (in theory) encountered more often
	// So we get higher bound re-use if we solve those first
	int *sorted_vertices = malloc(sizeof(int) * num_vertices);
	sort_vertices_by_in_degree(graph, sorted_vertices);

	// The current upper bound on paths starting from path[0]
	// This gets added to the upperbound_from table when path[0] changes
	int current_bound = 1;
	int sorted_index = 0;
	vertex = sorted_vertices[0];
	len = 1;
	path[0] = vertex;
	path_set[vertex] = true;
	branch_index = 0;

	// Each loop, either try to extend the path, or backtrack to try the next
	// edge out of the previous vertex.
	while (sorted_index < num_vertices) {

		backtrack = true;

		for (int i=branch_index; i<graph->adj[vertex].count; i++) {
			int next_vertex = graph->adj[vertex].elems[i];
			if (!path_set[next_vertex]) {

				// If we know an upper bound on paths starting from next_vertex, we obtain an upper bound
				// on the longest path continuing this current path through it.
				if (longest_path->count > 0 && upperbound_from[next_vertex] > 0 && len + upperbound_from[next_vertex] <= longest_path->count) {

					// Update the bound on paths starting from path[0]
					if (upperbound_from[next_vertex] + len > current_bound) {
						current_bound = upperbound_from[next_vertex] + len;
					}
					// Yay! We pruned this branch of the search
					continue;
				}

				// Extend path and update relevant state
				path[len] = next_vertex;
				branch_indices[len-1] = i;
				len++;
				path_set[next_vertex] = true;
				vertex=next_vertex;
				// Repeat this for-loop instead of backtracking
				backtrack = false;
				branch_index = 0;
				break;
			}
		}

		if (backtrack) {
			// Found better path
			if (len > longest_path->count) {
				memcpy(longest_path->elems, path, sizeof(int)*len);
				longest_path->count = len;
				if (prog != NULL) log_found_path(prog, longest_path);
				if (len == num_vertices) break;
			}
			if (len > current_bound) {
				current_bound = len;
			}
			
			// Search from new start vertex
			if (len == 1) {
				upperbound_from[path[0]] = current_bound;
				path_set[vertex] = 0;

				++sorted_index;
				if (sorted_index >= num_vertices) {
					break;
				}
				vertex = sorted_vertices[sorted_index];

				path_set[vertex] = 1;
				path[0] = vertex;
				backtrack = false;
				branch_index = 0;
				continue;
			}

			// Rewind state to previous vertex with new branch_index
			vertex = path[len-2];
			branch_index = branch_indices[len-2]+1;
			path_set[path[len-1]] = 0;
			len--;
		}
	}

	free(sorted_vertices);
	free(upperbound_from);
	free(path);
	free(branch_indices);
	free(path_set);
}