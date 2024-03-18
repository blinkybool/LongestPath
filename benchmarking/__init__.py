import os, json
from dataclasses import dataclass
from datetime import datetime
from typing import List, TypedDict, Optional, NamedTuple, Dict
from enum import Enum
from longestpath import (
	StandardGraph,
	gen_num_edges,
	gen_average_degree_directed,
	gen_erdos_reyni_directed,
	brute)

class Method(str, Enum):
	BRUTE_FORCE = "BRUTE_FORCE"
	BRANCH_N_BOUND = "BRANCH_N_BOUND"
	FAST_BOUND = "FAST_BOUND"
	BRUTE_FORCE_COMPLETE = "BRUTE_FORCE_COMPLETE"

	def is_brute(self) -> bool:
		return self.value in {
			Method.BRUTE_FORCE,
			Method.BRANCH_N_BOUND,
			Method.FAST_BOUND,
			Method.BRUTE_FORCE_COMPLETE,
		}

class RandomParams(NamedTuple):
	directed: bool
	num_vertices: int
	num_edges: Optional[int] = None
	average_degree: Optional[int] = None
	p: Optional[float] = None

	def serialise(self):
		return {k:v for k,v in self._asdict().items() if v is not None}

Result = TypedDict('Result',
	graph_id=str,
	path=List[int],
	length=int,
	run_time=float,
	method=str,
	failure=Optional[str])

class RandomBenchmark:

	def __init__(self,
		params_list: List[RandomParams],
		methods: List[Method],
		override_benchmark_path: str | None = None) -> None:

		self.params_list = params_list
		self.methods = methods
		self.override_benchmark_path = override_benchmark_path
		
		if override_benchmark_path:
			self.benchmark_path = override_benchmark_path
		else:
			if not os.path.exists("./benchmarks"):
				os.mkdir("./benchmarks")
			if not os.path.isdir("./benchmarks"):
				raise RuntimeError("Failed to make ./benchmarks folder")
			
			datetime_str = datetime.now().strftime('%Y-%m-%d--%H-%M-%S')
			self.benchmark_path = os.path.join("./benchmarks", f"random-{datetime_str}")

		self.graphs_path = os.path.join(self.benchmark_path, "graphs")
		
		if os.path.exists(self.benchmark_path):
			raise FileExistsError(f"Benchmark already exists: {str(self.benchmark_path)}")

		self.graphs: List[(str, StandardGraph)] = []

		for i, params in enumerate(params_list):
			graph_id = str(i)
			if not params.directed:
				# Unclear what the undirected graph format is.
				raise RuntimeError("Undirected graphs not properly handled")

			graph: StandardGraph
			if params.num_edges:
				graph = gen_num_edges(params.num_vertices, params.num_edges)
			elif params.p:
				graph = gen_erdos_reyni_directed(params.num_vertices, params.p)
			elif params.average_degree:
				graph = gen_average_degree_directed(params.num_vertices, params.average_degree)
			else:
				raise RuntimeError(f"Invalid params: {params}")

			self.graphs.append((graph_id, graph))

		os.mkdir(self.benchmark_path)
		os.mkdir(self.graphs_path)

		for graph_id, graph in self.graphs:
			with open(os.path.join(self.graphs_path, f"{graph_id}.txt"), "w") as graph_file:
				graph_file.write(str(graph))
			
		info_path = os.path.join(self.benchmark_path, "info.json")
		with open(info_path, "w") as info_file:
			json.dump({
				"type": "random",
				"params_list": [params.serialise() for params in params_list],
				"methods": methods,
				"graph_ids": list(range(len(self.graphs)))
			}, info_file, indent=2)

	def run(self,
			progressfile: str | None = None,
			timeout: float | None = None,
			retryFailures: bool = False):

		results_path = os.path.join(self.benchmark_path, "results.json")

		for graph_id, graph in self.graphs:
			if os.path.exists(results_path):
				with open(results_path, "r") as f:
					results = json.load(f)
			else:
				with open(results_path, "w") as f:
					# Put an empty results.json file there
					json.dump([], f)
				results = []
			
			for method in self.methods:
				if any(result["graph_id"] == graph_id and result["method"] == method for result in results):
					if not retryFailures:
						continue

				if not method.is_brute():
					raise RuntimeError("Non-brute solver not handled")
				
				print(method.name, graph_id)
				try:
					result = brute.solve(graph, method, progressfile=progressfile, timeout=timeout)
					assert("run_time" in result)
					assert("path" in result)
					result["length"] = len(result["path"])
				except TimeoutError:
					result = {
						"graph_id": graph_id,
						"failure": "timeout",
						"run_time": timeout,
					}

				result["method"] = method.name
				result["graph_id"] = graph_id

				results.append(result)
	
				# Eagerly write results in case of interruption
				with open(results_path, "w") as f:
					json.dump(results, f, indent = 2)

	def results(self) -> List[Result]:
		results_path = os.path.join(self.benchmark_path, "results.json")

		with open(results_path, "r") as f:
			results = json.load(f)

		return results

