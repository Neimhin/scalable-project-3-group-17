import http.server
import jwt
import json
import requests

cache = {
    "meaning of life": 42
}

LOGFILE = "tcdicn_node.log"

def discover_neighbours():
    pass

class ICNHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # let the emulation server check if this server is still alive
        if self.path == "/emulation/status":
            self.send_response(200)
            self.end_headers()
            return

            
    def do_POST(self):

        request_type = self.get_request_type()

        if request_type == "subscription":
            self.handle_subscription()
        if request_type == "publish":
            self.handle_publish()
    
    def get_request_type(self):
        # TODO handle errors
        t = self.headers.get("x-tcdicn-type")
        return t

    def handle_subscription(self):
        content_length = int(self.headers.get("Content-Length",0))
        # self.verify(data)
        # TODO set maximum content lenght to mitigate DoS/DDoS
        data = self.rfile.read(content_length)
        data = json.loads(data.decode("utf-8"))
        print(data)
        interested_in = data["name"]
        satisfy_data = cache[interested_in]
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(satisfy_data).encode("utf-8"))

        # TODO should update interest table if necessary

    def get_interested_in(data):
        # TODO should decode JWT and get the "name" field
        as_dict = json.loads(data)
        return as_dict["name"]



def register_with_emulation_server(host,port):
    data = json.dumps({
        "port": port,
        "host": host,
        "logfile": LOGFILE,
        "public key": "TODO public key", # TODO send public key
    })
    headers = {
        "Content-Type": "application/json",
    }
    response = requests.post("http://localhost:33334/emulation/register",data,headers)
    if response.status_code != 200:
        raise Exception("can't reach emulation server")
    print("successfully register with emulation server")

# start the routing server
def listen():
    import http.server
    # port=0 asks the operating system to choose a port for us to run on
    server_address = ("", 0)
    server_class = http.server.HTTPServer
    handler_class = ICNHTTPRequestHandler
    httpd = server_class(server_address, handler_class)
    host, port = httpd.server_address
    register_with_emulation_server(host,port)
    # TODO generate public key
    print("listening:", host, port)


    httpd.serve_forever()



if __name__ == "__main__":
    listen()