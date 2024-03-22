from pyqubo import Binary, Array, Num
import numpy as np
from dimod import ExactSolver
import neal
from longestpath import gen_average_degree_directed, gen_planted_path, StandardGraph

vars = Array.create('x', shape=(M+1, N+1), vartype='BINARY')

import time

start = time.time()
serial_exp = Num(-p) * sum([(sum(block) - Num(1))**2 for block in vars]) + Num(0)
end = time.time()

print(f"Done with serial_exp : Took {end - start} seconds")

#Seems to output same matrix as below
# serial_exp = Num(0)

# for m in range(M+1):
# 	temp_exp = Num(-1)
# 	for n in range(N+1):
# 		temp_exp += vars[m][n]
# 	serial_exp += Num(-p) * temp_exp ** 2

no_repeat_blocks_exp = Num(0)

start = time.time()

for i in range(N):
	print(f"{i} / {N-1}")
	for j in range(M):

		no_repeat_blocks_exp += sum([vars[j][i] * vars[k][i] for k in range(j+1, M+1)])

# 		for k in range(j+1, M+1):
# 			no_repeat_blocks_exp += vars[j][i] * vars[k][i] * Num(-p)
no_repeat_blocks_exp *= Num(-p)

end = time.time()

print(f"Done with no_repeatblocks_exp : Took {end - start} seconds")

start = time.time()
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
		edges_exp += Num(-p) * vars[m][N] * vars[m+1][i]

end = time.time()

print(f"Done with edges_exp : Took {end - start} seconds")