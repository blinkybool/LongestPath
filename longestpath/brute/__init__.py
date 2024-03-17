#!/usr/bin/env python3
from ..gen import StandardGraph
from subprocess import run, PIPE
import re
from enum import Enum
import pathlib
brute_path = pathlib.Path(__file__).parent.joinpath("brute")

class Method(Enum):
	BRUTE_FORCE = 1
	DFBNB = 2
	SMART_FORCE = 3

def solve(graph: StandardGraph, method: Method):

	if not brute_path.exists():
		raise RuntimeError("No brute executable found. Run `make`")

	p = run([brute_path, method.name], stdout=PIPE, input=str(graph), encoding='ascii')

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
