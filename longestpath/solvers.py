
import longestpath.brute as brute
import longestpath.kalp as kalp
from dataclasses import dataclass
from typing import TypedDict, List, Any, Dict

solvers = {
    "brute": brute.solve,
	"kalp": kalp.solve_KaLP
}

@dataclass
class Solver():
	name: str
	args: List[Any]
	kwargs: Dict[str, Any]

	def __init__(self, name, *args, **kwargs):
		assert name in solvers, "Unknown solver name"
		self.name = name
		self.args = args
		self.kwargs = kwargs

	def run(self, graph, timeout):
		return solvers[self.name](graph, timeout, *self.args, **self.kwargs)

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

