#!/usr/bin/env python3
from ..gen import StandardGraph
import subprocess
from enum import Enum
from typing import TypedDict, List, Optional
import pathlib
brute_path = pathlib.Path(__file__).parent.joinpath("brute")

class Method(str, Enum):
	BRUTE_FORCE = "BRUTE_FORCE"
	BRANCH_N_BOUND = "BRANCH_N_BOUND"
	FAST_BOUND = "FAST_BOUND"
	BRUTE_FORCE_COMPLETE = "BRUTE_FORCE_COMPLETE"

SolveResult = TypedDict('SolveResult', {'path': List[int], 'run_time': float})

def solve(graph: StandardGraph, timeout: float, method: str, progressfile: Optional[str] = None) -> SolveResult:
	'''
	Throws TimeoutError if timeout is exceeded
	'''

	if not brute_path.exists():
		raise FileNotFoundError("No brute executable found. Run `make`")

	args = [brute_path, "-m", method]

	if progressfile is not None:
		args.append("-p")
		args.append(progressfile)

	process = subprocess.run(
		args, 
		executable=brute_path, 
		input=str(graph), 
		stdout=subprocess.PIPE, 
		text=True, 
		timeout=timeout
	)

	if process.returncode < 0:
		print(process.stdout)
		print(process.stderr)
		raise RuntimeError(f"Executable exited with error. Return code {process.returncode}")

	if process.returncode != 0:
		print(process.stdout)
		print(process.stderr)
		raise RuntimeError("Executable exited with error.")
	
	data = {}
	
	for line in process.stdout.split('\n'):
		parts = line.strip().split(':')
		if len(parts) == 2:
			key, value = parts
			data[key.strip()] = value.strip()

	result = {}
	result["path"] = list(map(int, data["longest_path"].split()))
	result["run_time"] = float(data["time"])

	return result