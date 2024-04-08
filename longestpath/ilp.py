from ortools.linear_solver import pywraplp
from longestpath import gen_average_degree_directed, gen_planted_path, StandardGraph

# Map status int to string
# e.g. pywraplp.Solver.OPTIMAL is 0, so STATUS[0] = "OPTIMAL"
STATUS = {
	pywraplp.Solver.OPTIMAL: "OPTIMAL",
	pywraplp.Solver.FEASIBLE: "FEASIBLE",
	pywraplp.Solver.INFEASIBLE: "INFEASIBLE",
	pywraplp.Solver.MODEL_INVALID: "MODEL_INVALID",
}

# For interpreting variable solution outputs
# Is the admissable?
def var_solution_is_one(var):
	return round(var.solution_value()) == 1

def solve(graph: StandardGraph, max_path_length: int | None = None, process_queue = None):
	
	solver, variables = create_solver(graph, max_path_length=max_path_length)

	status = solver.Solve()

	result = {
		# Default to code value - don't want to crash for no reason!
		"status": STATUS.get(status, status)
	}

	if status != pywraplp.Solver.OPTIMAL:
		result["failure"] = "non-optimal"
		return result

	result["objective_value"] = solver.Objective().Value()

	path = []
	for block in variables:
		# Ignore terminal vertex
		for v, var in enumerate(block[:-1]):
			if var_solution_is_one(var):
				path.append(v)
				break
		else:
			# If no break in the inner loop, path hasn't continued at current time step
			break

	result["path"] = path
	return result


def create_solver(graph: StandardGraph, max_path_length: int = None):

	if max_path_length is None:
		max_path_length = graph.vertices

	# Easier to compare the implementation to the mathematics with these names
	N = graph.vertices
	M = max_path_length

	solver = pywraplp.Solver.CreateSolver("CP-SAT")

	variables = [[solver.IntVar(0.0, 1.0, f"X[{place}, {vert}]") for vert in range(N + 1)] for place in range(M)]

	# Define cost function
	cost = sum([sum([vars[i] for i in range(N)]) for vars in variables])

	solver.Maximize(cost)

	# No repeated vertices restriction
	for vert in range(N):
		solver.Add(sum(variables[place][vert] for place in range(M)) <= 1)

	# Use exactly one vertex at each place in the path (terminal vertex included)
	for vars in variables:
		solver.Add(sum(vars) == 1)

	edge_set = set(graph.edges)

	# Allow only usage of existing edges
	for place in range(M - 1):
		for vert1 in range(N+1):
			for vert2 in range(N+1):

				if vert1 == N:
					if vert2 != N:
						solver.Add(variables[place][vert1] + variables[place + 1][vert2] <= 1)
				else:
					if vert2 != N and vert1 != vert2:
						if (vert1, vert2) not in edge_set:
							solver.Add(variables[place][vert1] + variables[place + 1][vert2] <= 1)
	
	return solver, variables

if __name__ == "__main__":
	from longestpath import gen_num_edges, gen_average_degree_directed
	from .utils import with_time

	n = 50
	d = 2
	graph = gen_num_edges(n, round(n * d))

	result, run_time = with_time(solve)(graph)
	print(result)
	print("run_time", run_time)
	print("path length", len(result["path"])-1)