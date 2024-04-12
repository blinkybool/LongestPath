These are some of the larger benchmarks that where run:
- `all_methods_1.2-3.6_50_runs`
- `all_methods_3.8-4.8_50_runs`
- `only_ham_3brute_ilp_kalp_deg1-10_50runs`

The names should be relatively self explanatory.
`all_methods_3.8-4.8_50_runs` is essentially a continuation of `all_methods_1.2-3.6_50_runs`.
These two benchmarks consist of undirected graphs with 30 vertices and average degrees 1.2-3.6 and 3.8-4.8 in increments of 0.2.
For each graph and method they contain 50 runs.
The methods that where used are
- `brute('BRANCH_N_BOUND')`
- `brute('BRUTE_FORCE')`
- `brute('BRUTE_FORCE_COMPLETE')`
- `brute('FAST_BOUND')`
- `ilp()`
- `kalp()`
- `kalp(threads=4)`

`only_ham_3brute_ilp_kalp_deg1-10_50runs`  consists of undirected graphs of 30 vertices and average degrees 1-10.
For each graph and method they contain 50 runs.
- `brute("FAST_BOUND")`
- `brute("BRUTE_FORCE")`
- `brute("BRANCH_N_BOUND")`
- `ilp()`
- `kalp(threads=4)`

**Benchmarks used in the report:**
- `all_methods_1.2-3.6_50_runs`
- `only_ham_3brute_ilp_kalp_deg1-10_50runs`

