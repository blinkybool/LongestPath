#!/usr/bin/env python3
from ..gen import StandardGraph
import subprocess
import platform
from enum import Enum
from typing import Literal
import pathlib
from ..solveresult import SolveResult

if platform.system() == "Windows":
	brute_path = pathlib.Path(__file__).parent.joinpath("brute.exe")
else:
	brute_path = pathlib.Path(__file__).parent.joinpath("brute")

Method = Literal['BRUTE_FORCE', 'BRANCH_N_BOUND', 'FAST_BOUND', 'BRUTE_FORCE_COMPLETE']

def solve(graph: StandardGraph, method: Method, progressfile: str | None = None, process_queue = None) -> SolveResult:
	if not brute_path.exists():
		raise FileNotFoundError("No brute executable found. Run `make`")

	args = [brute_path, "-m", method]

	if progressfile is not None:
		args.append("-p")
		args.append(progressfile)

	process = subprocess.Popen(
		args, 
		executable=brute_path, 
		text=True, 
		stdout=subprocess.PIPE,
		stdin=subprocess.PIPE,
		stderr=subprocess.PIPE,
	)

	process_queue.put(process.pid)
	
	output, err = process.communicate(
		input=str(graph)
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
	
	for line in output.split('\n'):
		parts = line.strip().split(':')
		if len(parts) == 2:
			key, value = parts
			data[key.strip()] = value.strip()

	result = {}
	result["path"] = list(map(int, data["longest_path"].split()))
	result["run_time"] = float(data["time"])

	return result