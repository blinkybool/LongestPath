#include <time.h>
#include "neighbours_graph.h"

int main(int argc, char **argv) {
	NeighboursGraph *graph = read_undirected_graph();

	VertArray *best_path = malloc(sizeof(VertArray));
	best_path->elems = malloc(sizeof(int) * graph->vertices);

	clock_t tick = clock();
	longest_path_brute_force(best_path, graph, true);
	clock_t tock = clock();
	double elapsed = (double) (tock - tick) / CLOCKS_PER_SEC;

	printf("Longest path length: %d\n", best_path->count-1);

	printf("Longest path: ");
	FOREACH_ARRAY(int, vertex, (*best_path), {
		printf("%d ", vertex);
	});
	printf("\n");

	printf("Time: %fs\n", elapsed);

	if (!verify_path(best_path, graph))
		printf("FAIL: Path is invalid.\n");

	free_graph(graph);
	return 0;
}