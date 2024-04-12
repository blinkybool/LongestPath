"""
This module contains code for a benchmarking system for longest path solvers.
"""
import os, json, sys, shutil
from datetime import datetime
from typing import List, TypedDict, Optional, NamedTuple, Dict
from longestpath import (
	StandardGraph,
	gen_num_edges,
	gen_random_edges_average_degree_directed,
	gen_density,
	gen_random_edges_directed)
from longestpath.solvers import Solver
from longestpath.utils import with_timeout
import time
import shutil
from pathlib import Path
import pandas as pd

class RandomParams(NamedTuple):
	directed: bool
	num_vertices: int
	num_edges: Optional[int] = None
	average_degree: Optional[int] = None
	density: Optional[float] = None
	p: Optional[float] = None

	def serialise(self):
		'''
		To deserialise d = params.serialise(), do RandomParams(**d)
		'''
		return {k:v for k,v in self._asdict().items() if v is not None}
	
	def gen_graph(self):
		if self.num_edges is not None:
			return gen_num_edges(self.num_vertices, self.num_edges)
		elif self.p is not None:
			return gen_random_edges_directed(self.num_vertices, self.p)
		elif self.average_degree is not None:
			return gen_random_edges_average_degree_directed(self.num_vertices, self.average_degree)
		elif self.density is not None:
			return gen_density(self.num_vertices, self.density, self.directed)
		else:
			raise RuntimeError(f"Invalid params: {self}")

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

	def add_solver(self, solver: Solver):
		self.solvers.append(solver)
		self.info['solvers'] = [m.serialise() for m in self.solvers]
		with open(self.info_path, "w") as info_file:
			json.dump(self.info, info_file, indent=2)

		self.__init__(self.benchmark_path, self.graphs_path, self.info_path)

	def run(self,
			timeout: float | None = None,
			solver_indices: List[int] = None,
			retryFailures: bool = False):

		results_path = os.path.join(self.benchmark_path, "results.json")

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
			if solver_indices is not None and solver_index not in solver_indices:
				continue

			for graph_id, graph in self.graphs:
				# Find the results that are already present in the file for this solver and this graph
				existing_results = [
					result for result in results 
						if result["graph_id"] == graph_id and result["solver"] == solver_index
				]
				assert len(existing_results) in {0,1}, "Multiple results for same graph_id and solver"

				# If the previous result was a failure and retryFailures is enabled then we re-run the benchmark
				# If however, there was no failure or retry failures is not enables we skip this benchmark
				if len(existing_results) == 1:
					existing_result = existing_results[0]
					if not ("failure" in existing_result and retryFailures):
						continue

				print(f"graph: {graph_id}.txt, solver: {solver} ... ", end="")

				# Run the benchmark
				interrupted = False
				run_time = None
				result = None

				try:
					tick = time.perf_counter()
					if timeout:
						result = with_timeout(timeout, default=None)(solver.run)(graph)
					else:
						result = solver.run(graph)
				except KeyboardInterrupt:
					# Will stop after writing results
					interrupted = True
					tock = time.perf_counter()
					run_time = tock - tick

				# Format the results
				if result is None:
					result = {
						"failure": interrupted and "interrupted" or "timeout",
						"run_time": run_time or timeout,
					}
					print("❌ (timeout)")
				elif "failure" in result:
					print(f'❌ ({result["failure"]})')
				else:
					assert("run_time" in result)
					assert("path" in result)
					result["length"] = len(result["path"]) - 1
					print(f'✅')
					print(f'length: {result["length"]}, run_time: {result["run_time"]}')

				result["solver"] = solver_index
				result["graph_id"] = graph_id

				# Append the results to the list
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

	def get_results_dataframe(self):
		df = pd.DataFrame(self.results())
		solver_names = [str(solver) for solver in self.solvers]
		df["solver_name"] = df["solver"].apply(lambda i: solver_names[i])

		if not "failure" in df:
			df["failure"] = None

		return df

	def get_graph_dataframe(self):
		df = pd.DataFrame([{"graph_id" : id, "vertices": graph.vertices, "edges": len(graph.edges)} for id, graph in self.graphs])
		df["average_out_degree"] = df["edges"] / df["vertices"]
		df_infos = pd.DataFrame(self.info["graph_infos"]).T.add_suffix("_spec")

		return pd.merge(df, df_infos, left_on="graph_id", right_index=True, suffixes=("", "_spec"))

	def get_dataframe(self):
		return pd.merge(self.get_results_dataframe(), self.get_graph_dataframe(), on="graph_id")
	
	def solver_names(self):
		return [str(solver) for solver in self.solvers]
	
		
def setup_benchmark(graphs_to_write, info, benchmark_path = None):
	# If the benchmark_path is None we use the default path: benchmarks/benchmark-[DATE]
	if not benchmark_path:
		if not os.path.exists("./benchmarks"):
			os.mkdir("./benchmarks")
		if not os.path.isdir("./benchmarks"):
			raise RuntimeError("Failed to make ./benchmarks folder")
		
		datetime_str = datetime.now().strftime('%Y-%m-%d--%H-%M-%S')
		benchmark_path = os.path.join("./benchmarks", f"benchmark-{datetime_str}")
	
	# If a benchmark with this name already exists we append (n) for some n.
	# We support at most 100 of such duplicates for now.
	if os.path.exists(benchmark_path):
		for i in range(1,100):
			if not os.path.exists(benchmark_path + f"({i})"):
				benchmark_path += f"({i})"
				break
		else:
			raise FileExistsError(f"Too many files of this name: {str(benchmark_path)}")

	# Create the benchmark and the graphs folders
	graphs_path = os.path.join(benchmark_path, "graphs")
	Path(benchmark_path).mkdir(parents=True)
	os.mkdir(graphs_path)

	# Write insert the graph files into the graphs folder
	for graph_id, graph in graphs_to_write:
		with open(os.path.join(graphs_path, f"{graph_id}.txt"), "w") as graph_file:
			graph_file.write(str(graph))

	# Create the info.json file
	info_path = os.path.join(benchmark_path, "info.json")
	with open(info_path, "w") as info_file:
		json.dump(info, info_file, indent=2)

	return Benchmark(benchmark_path, graphs_path, info_path)


def new_random_benchmark(
		params_list: List[RandomParams],
		solvers: List[Solver],
		override_benchmark_path: str | None = None,
		params_code: str | None = None) -> Benchmark:

	graphs_to_write = []
	graph_infos = {}

	# Generate random graphs
	for i, params in enumerate(params_list):
		graph_id = str(i)
		if not params.directed:
			# Unclear what the undirected graph format is.
			raise RuntimeError("Undirected graphs not properly handled")

		graph = params.gen_graph()
		graphs_to_write.append((graph_id, graph))
		graph_infos[graph_id] = params.serialise()

	# Setup info for info.json
	info = {
		"type": "random",
		"solvers": [m.serialise() for m in solvers],
		"graph_infos": graph_infos,
	}
	if params_code is not None: info["params_code"] = params_code

	return setup_benchmark(graphs_to_write, info, override_benchmark_path)


def new_benchmark(
		graphs: List[StandardGraph],
		solvers: List[Solver],
		override_benchmark_path: str | None = None,
		params_code: str | None = None) -> Benchmark:

	graphs_to_write = []
	graph_infos = {}

	# Generate random graphs
	for i, graph in enumerate(graphs):
		graph_id = str(i)
		graphs_to_write.append((graph_id, graph))
		graph_infos[graph_id] = {}

	# Setup info for info.json
	info = {
		"type": "custom",
		"solvers": [m.serialise() for m in solvers],
		"graph_infos": graph_infos
	}
	if params_code is not None: info["params_code"] = params_code

	return setup_benchmark(graphs_to_write, info, override_benchmark_path)


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