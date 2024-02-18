#include <stddef.h>
#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>

typedef struct {
	int vertices;
	bool *matrix;
} MatrixGraph;

MatrixGraph *new_graph(int vertices);

void add_edge(MatrixGraph *graph, int source, int target);

void remove_edge(MatrixGraph *graph, int source, int target);

bool has_edge(MatrixGraph *graph, int source, int target);

void init_random_graph(MatrixGraph *graph, float p);

void init_random_undirected_graph(MatrixGraph *graph, float p);

void print_graph(MatrixGraph *graph);