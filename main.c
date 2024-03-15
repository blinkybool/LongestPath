#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "neighbours_graph.h"
#include <unistd.h>


int main(int argc, char **argv) {

	if (argc != 2) {
		fprintf(stderr, "Exactly one argument expected.\nUsage: ./lpath BRUTE_FORCE | DFBNB\n");
		exit(EXIT_FAILURE);
	}

	enum { BRUTE_FORCE, DFBNB } mode = BRUTE_FORCE;

	if (strcmp(argv[1], "DFBNB") == 0) {
		mode = DFBNB;
	} else if (strcmp(argv[1], "BRUTE_FORCE") != 0) {
		fprintf(stderr, "Unrecognised search mode %s.\nUsage: ./lpath BRUTE_FORCE | DFBNB\n", argv[1]);
		exit(EXIT_FAILURE);
	}

	NeighboursGraph *graph = read_graph(false);

	VertArray *best_path = malloc(sizeof(VertArray));
	best_path->count = 0;
	best_path->elems = malloc(sizeof(int) * graph->vertices);

	switch (mode) {
		case BRUTE_FORCE: printf("Search mode: BRUTE_FORCE\n"); break;
		case DFBNB: printf("Search mode: DFBNB\n"); break;
		default:
			fprintf(stderr, "bad switch");
			exit(EXIT_FAILURE);
	}

	clock_t tick, tock;
	
	tick = clock();
	switch (mode) {
		case BRUTE_FORCE: longest_path_brute_force(best_path, graph, true); break;
		case DFBNB: longest_path_DFBnB(best_path, graph); break;
		default:
			fprintf(stderr, "bad switch");
			exit(EXIT_FAILURE);
	}
	tock = clock();

	double elapsed = (double) (tock - tick) / CLOCKS_PER_SEC;

	if (!verify_path(best_path, graph)) {
		fprintf(stderr, "FAIL: Path is invalid.\n");
		exit(1);
	}

	printf("Longest path length: %d\n", best_path->count-1);

	printf("Longest path: ");
	FOREACH_ARRAY(int, vertex, (*best_path), {
		printf("%d ", vertex);
	});
	printf("\n");

	printf("Time: %fs\n", elapsed);

	free(best_path->elems);
	free(best_path);
	free_graph(graph);
	return 0;
}