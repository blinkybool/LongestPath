import os, json, sys, shutil
from datetime import datetime
from typing import List, TypedDict, Optional, NamedTuple
from longestpath import (
	StandardGraph,
	gen_num_edges,
	gen_average_degree_directed,
	gen_erdos_reyni_directed)
from longestpath.solvers import Solver
from longestpath.utils import with_timeout
import time
import shutil

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
	solver=str,
	failure=Optional[str])

class Benchmark:

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
			self.info = json.load(info_file)
			self.solvers = [Solver.deserialise(solver_str) for solver_str in self.info["solvers"]]
			self.graph_ids = [graph_id for graph_id, _ in self.info["graph_infos"].items()]
		
		self.graphs = []
		
		for graph_id in self.graph_ids:
			with open(os.path.join(self.graphs_path, f"{graph_id}.txt"), "r") as graph_file:
				self.graphs.append((graph_id, StandardGraph.from_string(graph_file.read())))

	def run(self,
			timeout: float | None = None,
			retryFailures: bool = False):

		results_path = os.path.join(self.benchmark_path, "results.json")

		for graph_id, graph in self.graphs:
			# Load results.json
			if os.path.exists(results_path):
				with open(results_path, "r") as f:
					results = json.load(f)
					assert(type(results) == list)
			else:
				with open(results_path, "w") as f:
					# Put an empty results.json file there
					json.dump([], f)
				results = []
			
			# Run benchmark
			for solver_index, solver in enumerate(self.solvers):
				existing_list = [
					result for result in results 
						if result["graph_id"] == graph_id and result["solver"] == solver_index
				]
				assert len(existing_list) in {0,1}, "Multiple results for same graph_id and solver"
				if len(existing_list) == 1:
					existing = existing_list[0]
					if not ("failure" in existing and retryFailures):
						continue

				print(f"graph: {graph_id}.txt, solver: {solver} ... ", end="")


				interrupted = False
				run_time = None
				result = None

				try:
					tick = time.perf_counter()
					result = with_timeout(timeout, default=None)(solver.run)(graph)
				except KeyboardInterrupt:
					# Will stop after writing results
					interrupted = True
					tock = time.perf_counter()
					run_time = tock - tick


				if result is None:
					result = {
						"failure": interrupted and "interrupted" or "timeout",
						"run_time": run_time or timeout,
					}
					print("❌ (timeout)")
				elif "failure" in result:
					print(f'❌ ({result["failure"]})')
					if "run_time" not in result:
						result["run_time"] = timeout
				else:
					assert("run_time" in result)
					assert("path" in result)
					result["length"] = len(result["path"]) - 1
					print(f'✅')
					print(f'length: {result["length"]}, run_time: {result["run_time"]}')

				result["solver"] = solver_index
				result["graph_id"] = graph_id

				results = [r for r in results if not (r["graph_id"] == graph_id and r["solver"] == solver_index)]
				results.append(result)
	
				# Eagerly write results in case of interruption
				with open(results_path, "w") as f:
					json.dump(results, f, indent = 2)

				if interrupted:
					sys.exit(130)

	def results(self) -> List[Result]:
		results_path = os.path.join(self.benchmark_path, "results.json")

		with open(results_path, "r") as f:
			results = json.load(f)

		return results

def new_random_benchmark(
		params_list: List[RandomParams],
		solvers: List[Solver],
		override_benchmark_path: str | None = None,
		params_code: str | None = None) -> Benchmark:

	
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

	graphs_to_write = []
	graph_infos = {}

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

		graphs_to_write.append((graph_id, graph))
		graph_infos[graph_id] = params.serialise()

	os.mkdir(benchmark_path)
	os.mkdir(graphs_path)

	for graph_id, graph in graphs_to_write:
		with open(os.path.join(graphs_path, f"{graph_id}.txt"), "w") as graph_file:
			graph_file.write(str(graph))
		
	info_path = os.path.join(benchmark_path, "info.json")
	with open(info_path, "w") as info_file:
		info = {
			"type": "random",
			"solvers": [m.serialise() for m in solvers],
			"graph_infos": graph_infos,
		}
		if params_code is not None:
			info["params_code"] = params_code
		json.dump(info, info_file, indent=2)

	return Benchmark(benchmark_path, graphs_path, info_path)

def new_graph_file_benchmark(
		graph_path: str,
		solvers: List[Solver],
		benchmark_path: str | None = None) -> Benchmark:
	'''
	benchmark_path should probably be of the form ./benchmarks/name
	'''

	graphs_path = os.path.join(benchmark_path, "graphs")

	if os.path.exists(benchmark_path):
		raise FileExistsError(f"Benchmark already exists: {str(benchmark_path)}")

	try:
		with open(graph_path, "r") as f:
			graph = StandardGraph.from_string(f.read())
	except Exception:
		raise Exception(f"Cannot read graph at path {graph_path}")
	
	graph_name, _ = os.path.splitext(os.path.basename(graph_path))

	graph_infos = {
		graph_name: {
			"source_path": graph_path,
		}
	}

	os.mkdir(benchmark_path)
	os.mkdir(graphs_path)

	shutil.copy2(graph_path, os.path.join(graphs_path, graph_name + ".txt"))

	info_path = os.path.join(benchmark_path, "info.json")
	with open(info_path, "w") as info_file:
		json.dump({
			"type": "graph_file",
			"solvers": [m.serialise() for m in solvers],
			"graph_infos": graph_infos,
		}, info_file, indent=2)

	return Benchmark(benchmark_path, graphs_path, info_path)