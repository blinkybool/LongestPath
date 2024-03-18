#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "neighbours_graph.h"
#include <unistd.h>
#include <ctype.h>

#define USAGE "Usage: brute -m <method>\n"

int main(int argc, char **argv) {

	int c;
	bool directed = true;
	FILE *prog = NULL;
	bool close_prog = false;
	enum { UNSET, BRUTE_FORCE, BRANCH_N_BOUND, FAST_BOUND, BRUTE_FORCE_COMPLETE } method = UNSET;

	opterr = 0; //if (opterr != 0) (which it is by default), getopt() prints its own error messages for invalid options and for missing option arguments.
	while ((c = getopt (argc, argv, "m:up:")) != -1)
		switch (c) {
			case 'm':
				if (strcmp(optarg, "BRUTE_FORCE") == 0) {
					method = BRUTE_FORCE;
				} else if (strcmp(optarg, "BRANCH_N_BOUND") == 0) {
					method = BRANCH_N_BOUND;
				} else if (strcmp(optarg, "FAST_BOUND") == 0) {
					method = FAST_BOUND;
				} else if (strcmp(optarg, "BRUTE_FORCE_COMPLETE") == 0) {
					method = BRUTE_FORCE_COMPLETE;
				} else {
					fprintf(stderr, "Unrecognised search method %s.\n\n", optarg);
					exit(EXIT_FAILURE);
				}
				break;
			case 'u':
				directed = false;
				break;
			case 'p':
				printf("using: %s\n", optarg);
				prog = fopen(optarg, "w");
				close_prog = true;
				break;
			case '?':
				if (optopt == 'm')
					fprintf (stderr, "Option -%c requires an argument.\n", optopt);
				else if(optopt == 'p' && isprint(optopt)) {
					printf("using stdout\n");
					prog = stdout;
					break;
				}
				else if (isprint (optopt))
					fprintf (stderr, "Unknown option `-%c'.\n", optopt);
				else
					fprintf (stderr, "Unknown option character `\\x%x'.\n", optopt);
				return 1;
			default:
				abort ();
		}

	if (method == UNSET) {
		fprintf (stderr, "No method provided.\n%s", USAGE);
		exit(EXIT_FAILURE);
	}

	NeighboursGraph *graph = read_graph(!directed);

	VertArray *best_path = malloc(sizeof(VertArray));
	best_path->count = 0;
	best_path->elems = malloc(sizeof(int) * graph->vertices);

	switch (method) {
		case BRUTE_FORCE: printf("Search method: brute force\n"); break;
		case BRANCH_N_BOUND: printf("Search method: branch and bound\n"); break;
		case FAST_BOUND: printf("Search method: fast bound\n"); break;
		case BRUTE_FORCE_COMPLETE: printf("Search method: brute force (complete)\n"); break;
		default:
			fprintf(stderr, "bad switch");
			exit(EXIT_FAILURE);
	}

	clock_t tick, tock;
	
	tick = clock();
	switch (method) {
		case BRUTE_FORCE: longest_path_brute_force(best_path, graph, true, prog); break;
		case BRANCH_N_BOUND: longest_path_branch_and_bound(best_path, graph, prog); break;
		case FAST_BOUND: longest_path_fast_bound(best_path, graph, prog); break;
		case BRUTE_FORCE_COMPLETE: longest_path_brute_force(best_path, graph, false, prog); break;
		default:
			fprintf(stderr, "bad switch");
			exit(EXIT_FAILURE);
	}
	tock = clock();
	double elapsed = (double) (tock - tick) / CLOCKS_PER_SEC;

	if (close_prog) fclose(prog);

	if (!verify_path(best_path, graph)) {
		fprintf(stderr, "FAIL: Path is invalid.\n");
		exit(1);
	}

	printf("length: %d\n", best_path->count-1);

	printf("longest_path:");
	FOREACH_ARRAY(int, vertex, (*best_path), {
		printf(" %d", vertex);
	});
	printf("\n");

	printf("time: %f\n", elapsed);

	free(best_path->elems);
	free(best_path);
	free_graph(graph);
	return 0;
}