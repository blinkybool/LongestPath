#!/usr/bin/env python3
from ..gen import StandardGraph
import subprocess
from enum import Enum
from typing import Literal
import pathlib
from ..solveresult import SolveResult

brute_path = pathlib.Path(__file__).parent.joinpath("brute.exe")

Method = Literal['BRUTE_FORCE', 'BRANCH_N_BOUND', 'FAST_BOUND', 'BRUTE_FORCE_COMPLETE']

def solve(graph: StandardGraph, method: Method, progressfile: str | None = None) -> SolveResult:

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
		capture_output=True,
		text=True, 
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