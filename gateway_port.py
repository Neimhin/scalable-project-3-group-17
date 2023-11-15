import socket

START_PORT = 33100
END_PORT = 34000
start_port = START_PORT

# find a free port in the range 33000 to 34000, excluding 33333
# i think it's good that this is a blocking function to avoid races (neimhin)
def find_free_gateway_port():
    global start_port
    for port in range(start_port, END_PORT):
        try:
            # Attempt to bind to the port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                # move start_port for more efficient search next time
                start_port = port + 1
                if start_port >= END_PORT:
                    start_port = START_PORT
                return port
        except OSError:
            # port already in use, try another port
            continue
    raise IOError("No free port found in the specified range")


if __name__ == "__main__":
    for i in range(100):
        print(find_free_gateway_port())
