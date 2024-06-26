#include <stddef.h>
#include <stdio.h>
#include <stdbool.h>
#include <assert.h>
#include <string.h>
#include <stdlib.h>

#define FOREACH_ARRAY(type, elem, array, body)  \
    for (size_t elem_##index = 0;                           \
         elem_##index < array.count;                        \
         ++elem_##index)                                    \
    {                                                       \
        type elem = array.elems[elem_##index];            \
        body;                                               \
    }

typedef struct {
	int count;
	int *elems;
} VertArray;

typedef struct {
	int vertices;
	VertArray adj[];
} NeighboursGraph;

NeighboursGraph *new_graph(int vertices);

void free_graph(NeighboursGraph *graph);

void add_edge(NeighboursGraph *graph, int source, int target);

void remove_edge(NeighboursGraph *graph, int source, int target);

void init_random_graph(NeighboursGraph *graph, float p, unsigned int random_seed);

void init_random_undirected_graph(NeighboursGraph *graph, float p, unsigned int random_seed);

void print_graph(NeighboursGraph *graph);

void print_undirected_graph(NeighboursGraph *graph);

bool verify_path(VertArray *path, NeighboursGraph *graph);

NeighboursGraph *read_graph(bool undirected, FILE *file);

void longest_path_brute_force(VertArray *best_path, NeighboursGraph *graph, bool stop_at_hamiltonian, FILE *prog);

void longest_path_branch_and_bound(VertArray *best_path, NeighboursGraph *graph, FILE *prog);

void longest_path_fast_bound(VertArray *best_path, NeighboursGraph *graph, FILE *prog);