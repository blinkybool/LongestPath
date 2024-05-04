# LongestPath
Implementations of various longest path algorithms, including brute force (with various branch and bound strategies) and QUBO formulations.

## Setup
You need `make` and `gcc` to compile the C code, and python3.10 for the python code.
WSL is recommended for running on Windows.

### Compile brute

```bash
# compile brute
make
```
This creates the brute executable at `longestpath/brute/brute` (`brute.exe` on windows).
You can skip the python setup if you just want to run brute.

### Python setup
Option 1: Manage python version and dependencies with conda.
```bash
conda create --name longest-path-env python=3.10
conda activate longest-path-env
# Uses pip from conda env
pip install -r requirements.txt
```
Option 2: Install python3.10 your own way and use virtualenv.
```bash
# Create virtualenv
python3 -m venv venv
# Activate it (repeat this step on shell restart)
source ./venv/bin/activate
# Upgrade pip
pip install -U pip
# Install dependencies
pip install -r requirements.txt
```
In order for KaLP to run you need to install KaLP manually and expose the executable path to python.
For installing KaLP checkout: https://karlsruhelongestpaths.github.io/.
To give python access to the KaLP executable you need to set the `KALP_PATH` environment variable to `your_kalp_location/deploy` using `.env` files.
In order for the notebooks to work you also need a duplicate of this `.env` file to be included in `./notebooks`.
```bash
touch .env
echo "KALP_PATH=[you_kalp_path/deploy]" > .env
cp .env notebooks/.env
```

## Usage
### Brute
```
# Run brute with input file and optional -m method = BRUTE_FORCE | BRANCH_N_BOUND | FAST_BOUND | BRUTE_FORCE_COMPLETE
./longestpath/brute/brute [-m method] <input_file>
# example
./longestpath/brute/brute -m BRANCH_N_BOUND graph.txt
```

### Solvers
See [./usage.py](./usage.py) for examples of runnning each solver on an single graph.
For benchmarking examples, see [notebooks](./notebooks/)

## Code Structure
- [longestpath/standard_graph](longestpath/standard_graph): is the graph format used as input for the solvers.
- [longestpath/gen](longestpath/gen) functions for generating random graphs
- Solvers:
    - [longestpath/brute](longestpath/brute): a python module wrapper for the C program `brute`.
    - [longestpath/qubo](longestpath/qubo): time based qubo formulation (+simulated annealing via DWAVE)
    - [longestpath/qubo_edge](longestpath/qubo_edge): edge based qubo formulation (+simulated annealing via DWAVE)
    - [longestpath/anneal](longestpath/anneal): direct simulated annealing approach
    - [longestpath/ilp](longestpath/ilp): ILP formulation using Google OR-Tools
    - [longestpath/kalp](longestpath/kalp): python wrapper for calling KaLP executable (must be installed separately)
- [datasets](./datasets/): real world datasets for benchmarking
    - Example: `longestpath/brute/brute -m FAST_BOUND ./datasets/rob-top/rob-top2000-graph.txt`
- [benchmarking](./benchmarking/): python module for creating and running interruptable benchmarks
- [notebooks](./notebooks/): jupyter notebooks for benchmarking and plotting
- [visualise](./visualise/): A force-graph based visualisation tool for demonstrating how simulated annealing works.