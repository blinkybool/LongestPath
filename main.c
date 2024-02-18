#include <time.h>
#include "neighbours_graph.h"

int main(int argc, char **argv) {
	if (argc != 2) {
		printf("Expected 1 argument (num vertices)");
	}

	int vertices = atoi(argv[1]);

	NeighboursGraph *graph = new_graph(vertices);
	init_random_undirected_graph(graph, 3.0 / vertices, time(NULL));
	print_undirected_graph(graph);

	VertArray *best_path = malloc(sizeof(VertArray));
	best_path->elems = malloc(sizeof(int) * graph->vertices);

	longest_path_brute_force(best_path, graph, true);

	printf("Longest path length: %d\n", best_path->count-1);

	printf("Longest path: ");
	FOREACH_ARRAY(int, vertex, (*best_path), {
		printf("%d ", vertex);
	});
	printf("\n");

	if (!verify_path(best_path, graph))
		printf("FAIL: Path is invalid.\n");

	free_graph(graph);
	return 0;
}