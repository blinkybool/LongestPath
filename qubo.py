from pyqubo import Binary, Array, Num
import numpy as np
from dimod import ExactSolver
import neal
from gen import gen_average_degree_directed, gen_planted_path, StandardGraph


graph = StandardGraph(5, [
	(0,1),
	(1,3),
	(3,4),
	(1,2),
])

# max length
N = graph.vertices
M = 3

p = M+1

matrix = graph.to_matrix()

vars = Array.create('x', shape=(M+1, N+1), vartype='BINARY')

serial_exp = Num(-p) * sum([(sum(block) - Num(1))**2 for block in vars]) + Num(0)

# for block in vars:
# 	varsum = Num(-1)
# 	for var in block:
# 		print(var)
# 		varsum += var

# 	print(varsum)
# 	serial_exp += Num(-p) * varsum * varsum
# 	print(serial_exp)
# 	break

# 
# exit(0)

no_repeat_blocks_exp = Num(0)

for i in range(N):
	for j in range(M+1):
		for k in range(j+1, M+1):
			print(i, j, k)
			print(vars[j][i] * vars[k][i] * Num(-p))
			no_repeat_blocks_exp += vars[j][i] * vars[k][i] * Num(-p)

edges_exp = Num(0)

for m in range(M):
	for i in range(N):
		for j in range(N):
			if i == j:
				continue

			if matrix[i][j]:
				edges_exp += vars[m][i] * vars[m+1][j]
			else:
				edges_exp += Num(-p) * vars[m][i] * vars[m+1][j]

for m in range(M):
	for i in range(N):
		edges_exp += vars[m][i] * vars[m+1][N]

def to_matrix(exp):
	model = exp.compile()
	qubo, energy_offset = model.to_qubo(index_label=True)

	return np.matrix([[int(qubo.get((i,j), 0)) for j in range((M+1)*(N+1))] for i in range((M+1)*(N+1))])

total_exp = serial_exp + no_repeat_blocks_exp + edges_exp
# model = total_exp.compile()
# bqm = model.to_bqm()

print(to_matrix(no_repeat_blocks_exp))


# sa = neal.SimulatedAnnealingSampler()
# sampleset = sa.sample(bqm, num_reads=100)
# decoded_samples = model.decode_sampleset(sampleset)
# best_sample = min(decoded_samples, key=lambda x: x.energy)
# print(best_sample.energy)

# sampleset = ExactSolver().sample(bqm)
# decoded_samples = model.decode_sampleset(sampleset)
# best_sample = max(decoded_samples, key=lambda s: s.energy)
# print(best_sample.energy)
