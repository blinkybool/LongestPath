#!/usr/bin/env python3
import math
from gen import StandardGraph, gen_average_degree
from typing import List, Tuple
from subprocess import run, PIPE
import re
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

# TODO Test suite for graph generation, algorithm run-time testing, and plotting results with matplotlib

def run_test(graph: StandardGraph) -> float:
	p = run(['./lpath'], stdout=PIPE, input=str(graph), encoding='ascii')

	if p.returncode != 0:
		print(p.stderr)
		raise RuntimeError("Executable exited with error.")

	# Search for the pattern in the text
	match = re.search(r"Time: (\d+\.\d+)s", p.stdout)

	# If a match is found, extract the runtime
	if not match:
		print(p.stdout)
		raise RuntimeError("Failed to get elapsed time")
	
	elapsed = float(match.group(1))
	return elapsed

def run_benchmarks(vertices_range, average_degree, tests=10):
	graph_groups: List[List[StandardGraph]] = []

	for vertices in vertices_range:
		group = [gen_average_degree(vertices, average_degree) for _ in range(tests)]
		graph_groups.append(group)

	times: List[float] = []

	for group in graph_groups:
		elapsed = np.average([run_test(graph) for graph in group])
		times.append(elapsed)

	return times
