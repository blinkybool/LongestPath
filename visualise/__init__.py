import http.server
import socketserver
import json
import os
from longestpath import brute

PORT = 8080

def serve(html_page, data):
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/data':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            elif self.path == '/':
                with open(html_page, 'rb') as f:
                    html_content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(html_content)
            else:
                # return http.server.SimpleHTTPRequestHandler.do_GET(self)
                raise Exception(f"Unknown path: {self.path}")

    print("chdir", os.path.dirname(os.path.abspath(__file__)))
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    httpd = socketserver.TCPServer(("", PORT), CustomHandler, bind_and_activate=False)
    httpd.allow_reuse_address = True
    httpd.server_bind()
    print(f"Server active: http://localhost:{PORT}/")
    httpd.server_activate()
    httpd.serve_forever()

def serve_benchmark_visualiser(benchmark):

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
        vis_graph["data"]["nodes"] = [{"id": i} for i in range(graph.vertices)]
        vis_graph["data"]["links"] = [{"source": i, "target": j} for i, j in graph.edges]
        vis_data["graphs"].append(vis_graph)

    serve("./benchmark.html", vis_data)

def serve_simulated_annealing_visualiser(graph, runs):

    longest_path = brute.solve(graph, "BRANCH_N_BOUND")["path"]
    vis_graph = {
        "data":  {
            "nodes": [{"id": i} for i in range(graph.vertices)],
            "links": [{"source": i, "target": j} for i, j in graph.edges if i < j],
        },
    }

    data = {
        "graph": vis_graph,
        "longest_path": longest_path,
        "runs": runs,
    }

    serve("./simulated_annealing.html", data)

