import os, json, pathlib
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
		'''
		To deserialise d = params.serialise(), do RandomParams(**d)
		'''
		return {k:v for k,v in self._asdict().items() if v is not None}

Result = TypedDict('Result',
	graph_id=str,
	path=List[int],
	length=int,
	run_time=float,
	method=str,
	failure=Optional[str])

def new_random_benchmark(
		params_list: List[RandomParams],
		methods: List[Method],
		override_benchmark_path: str | None = None) -> None:

	
	if override_benchmark_path:
		benchmark_path = override_benchmark_path
	else:
		if not os.path.exists("./benchmarks"):
			os.mkdir("./benchmarks")
		if not os.path.isdir("./benchmarks"):
			raise RuntimeError("Failed to make ./benchmarks folder")
		
		datetime_str = datetime.now().strftime('%Y-%m-%d--%H-%M-%S')
		benchmark_path = os.path.join("./benchmarks", f"random-{datetime_str}")

	graphs_path = os.path.join(benchmark_path, "graphs")
	
	if os.path.exists(benchmark_path):
		raise FileExistsError(f"Benchmark already exists: {str(benchmark_path)}")

	graphs = []

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

		graphs.append((graph_id, graph))

	os.mkdir(benchmark_path)
	os.mkdir(graphs_path)

	for graph_id, graph in graphs:
		with open(os.path.join(graphs_path, f"{graph_id}.txt"), "w") as graph_file:
			graph_file.write(str(graph))
		
	info_path = os.path.join(benchmark_path, "info.json")
	with open(info_path, "w") as info_file:
		json.dump({
			"type": "random",
			"params_list": [params.serialise() for params in params_list],
			"methods": methods,
			"graph_ids": [graph_id for graph_id, graph in graphs]
		}, info_file, indent=2)

	return RandomBenchmark(benchmark_path, graphs_path, info_path)

class RandomBenchmark:

	@classmethod
	def is_benchmark_dir(cls, path: str):
		return all([
			os.path.isdir(path),
			os.path.isdir(os.path.join(path, "graphs")),
			os.path.isfile(os.path.join(path, "info.json")),
		])
	
	@classmethod
	def get_valid_benchmark_paths(cls, benchmarks_container: str = "./benchmarks"):
		return [os.path.join(benchmarks_container, path)
							for path in os.listdir(benchmarks_container)
								if cls.is_benchmark_dir(os.path.join(benchmarks_container, path))]

	@classmethod
	def load_latest(cls, benchmarks_container: str = "./benchmarks"):
		benchmark_paths = cls.get_valid_benchmark_paths(benchmarks_container)
		latest_modified = max(benchmark_paths, key=os.path.getmtime)
		return cls.load(latest_modified)

	@classmethod
	def load(cls, benchmark_path: str):
		graphs_path = os.path.join(benchmark_path, "graphs")
		info_path = os.path.join(benchmark_path, "info.json")
		return cls(benchmark_path, graphs_path, info_path)

	def __init__(self,
		benchmark_path: str,
		graphs_path: str,
		info_path: str):
		'''
		We always load from file (rather than accepting graphs list directly) to ensure idempotence
		'''

		self.benchmark_path = benchmark_path
		self.graphs_path = graphs_path
		self.info_path = info_path

		with open(self.info_path, "r") as info_file:
			info = json.load(info_file)
			self.params_list = [RandomParams(**d) for d in info["params_list"]]
			self.methods = [Method[method_str] for method_str in info["methods"]]
			self.graph_ids = info["graph_ids"]
		
		self.graphs = []
		
		for graph_id in self.graph_ids:
			with open(os.path.join(self.graphs_path, f"{graph_id}.txt"), "r") as graph_file:
				self.graphs.append((graph_id, StandardGraph.from_string(graph_file.read())))

	def run(self,
			progressfile: str | None = None,
			timeout: float | None = None,
			retryFailures: bool = False):

		results_path = os.path.join(self.benchmark_path, "results.json")

		for graph_id, graph in self.graphs:
			if os.path.exists(results_path):
				with open(results_path, "r") as f:
					results = json.load(f)
					assert(type(results) == list)
			else:
				with open(results_path, "w") as f:
					# Put an empty results.json file there
					json.dump([], f)
				results = []
			
			for method in self.methods:
				existing_list = [result for result in results if result["graph_id"] == graph_id and result["method"] == method]
				assert len(existing_list) in {0,1}, "Multiple results for same graph_id and method"
				if len(existing_list) == 1:
					existing = existing_list[0]
					if not ("failure" in existing and retryFailures):
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

				results = [r for r in results if not (r["graph_id"] == graph_id and r["method"] == method)]
				results.append(result)
	
				# Eagerly write results in case of interruption
				with open(results_path, "w") as f:
					json.dump(results, f, indent = 2)

	def results(self) -> List[Result]:
		results_path = os.path.join(self.benchmark_path, "results.json")

		with open(results_path, "r") as f:
			results = json.load(f)

		return results

