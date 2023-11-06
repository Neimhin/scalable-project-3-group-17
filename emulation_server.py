import http.server
import json

class RegisterRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        print("handling post")
        if self.path == "/emulation/register":
            content_length = int(self.headers.get("Content-Length"))
            post_data = self.rfile.read(content_length)
            
            try:
                json_data = json.loads(post_data.decode("utf-8"))
                print(json_data)
                self.send_response(200)
                self.end_headers()
                cache["register_data"] = json_data
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Invalid JSON data in the request.")
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Endpoint not found.")

if __name__ == "__main__":
    server_address = ('', 33334)  # Change the host and port as needed
    cache = {}  # A dictionary to store the register request data
    
    httpd = http.server.HTTPServer(server_address, RegisterRequestHandler)
    print("Server is running at http://{}:{}".format(*server_address))

    # TODO periodicall check which nodes are still alive
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")
