from visualise import serve_visualiser
from benchmarking import Benchmark
import pandas as pd

benchmark = Benchmark.load("benchmarks/rob-top-2000")

vis_data = {
    "solvers": [f"{i}-{solver}" for i, solver in enumerate(benchmark.solvers)],
    "graphs": [],
}

results = benchmark.results()

for graph_id, graph in benchmark.graphs:
    vis_graph = {
        "graph_id": graph_id,
        "data": {},
        "results": [result for result in results if result["graph_id"] == graph_id],
    }
    vis_graph["data"]["nodes"] = [{"id": i, "path": False} for i in range(graph.vertices)]
    vis_graph["data"]["links"] = [{"source": i, "target": j} for i, j in graph.edges]
    vis_data["graphs"].append(vis_graph)


serve_visualiser(vis_data)