
from longestpath import brute, ilp, kalp, qubo, anneal
from dataclasses import dataclass
from typing import TypedDict, List, Any, Dict
from .utils import with_timed_result

# Assignment of names to specific solver implementations
# A solver should be a function with a StandardGraph as its first positional argument and with an optional keyword argument called process_queue.
solvers = {
	"brute": brute.solve,
	"kalp": kalp.solve_KaLP,
	"ilp": with_timed_result(ilp.solve),
	"qubo": with_timed_result(qubo.solve),
	"anneal": with_timed_result(anneal.solve),
}

@dataclass
class Solver():
	"""
	A serializable description of longest path solvers.
	It simply stores the name of a solver from the `solvers` dict and it stores the args and kwargs used to run the solver.
	"""
	name: str
	args: List[Any]
	kwargs: Dict[str, Any]

	def __init__(self, name, *args, **kwargs):
		assert name in solvers, "Unknown solver name"
		self.name = name
		self.args = args
		self.kwargs = kwargs

	def run(self, graph, process_queue=None):
		return solvers[self.name](graph, *self.args, process_queue=process_queue, **self.kwargs)

	def serialise(self):
		return {
			"name": self.name,
			"args": self.args,
			"kwargs": self.kwargs,
		}

	@classmethod
	def deserialise(cls, json):
		return Solver(json["name"], *json["args"], **json["kwargs"])

	def __str__(self):
		args = [i.__repr__() for i in self.args]
		kwargs = [f"{key}={val.__repr__()}" for key, val in self.kwargs.items()]
		return f"{self.name}({', '.join(args + kwargs)})"

