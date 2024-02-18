#include "matrix_graph.h"

MatrixGraph *new_graph(int vertices) {
	MatrixGraph *graph = (MatrixGraph *)malloc(sizeof(MatrixGraph));
	graph->vertices = vertices;
	graph->matrix = malloc(sizeof(bool) * vertices * vertices);

	return graph;
}

void add_edge(MatrixGraph *graph, int source, int target) {
	graph->matrix[source * graph->vertices + target] = true;
}

void remove_edge(MatrixGraph *graph, int source, int target) {
	graph->matrix[source * graph->vertices + target] = false;
}

bool has_edge(MatrixGraph *graph, int source, int target) {
	return graph->matrix[source * graph->vertices + target];
}

void init_random_graph(MatrixGraph *graph, float p) {
	int p_upper_rand = (int) (p * (float) RAND_MAX);
	for (int i = 0; i < graph->vertices; i++) {
		for (int j = 0; j < graph->vertices; j++) {
			if (rand() < p_upper_rand) add_edge(graph, i, j);
		}
	}
}

void init_random_undirected_graph(MatrixGraph *graph, float p) {
	int p_upper_rand = (int) (p * (float) RAND_MAX);
	for (int i = 0; i < graph->vertices; i++) {
		for (int j = 0; j <= i; j++) {
			if (rand() < p_upper_rand) {
				add_edge(graph, i, j);
				add_edge(graph, j, i);
			}
		}
	}
}

void print_graph(MatrixGraph *graph) {
	printf("%d\n", graph->vertices);
	for (int i = 0; i < graph->vertices; i++) {
		for (int j = 0; j < graph->vertices; j++) {
			if (has_edge(graph, i, j)) {
				printf("%d %d\n", i, j);
			}
		}
	}
}
