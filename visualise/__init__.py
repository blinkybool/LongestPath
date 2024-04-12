import http.server
import socketserver
import json
import os

PORT = 8080

def serve_visualiser(vis_data):

    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/vis_data':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(vis_data).encode())
            else:
                if self.path == '/':
                    self.path = '/index.html'
                return http.server.SimpleHTTPRequestHandler.do_GET(self)

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"Server active: http://localhost:{PORT}/")
        httpd.allow_reuse_address = True
        httpd.serve_forever()