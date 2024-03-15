#!/usr/bin/env python3
from gen import StandardGraph
from subprocess import run, PIPE
import re
from enum import Enum

# TODO Test suite for graph generation, algorithm run-time testing, and plotting results with matplotlib

class Method(Enum):
	BRUTE_FORCE = 1
	DFBNB = 2

def run_test(graph: StandardGraph, method: Method) -> float:
	p = run(['./lpath', method.name], stdout=PIPE, input=str(graph), encoding='ascii')

	print(p.stdout)

	if p.returncode != 0:
		print("result")
		print(p)
		print("stderr")
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
