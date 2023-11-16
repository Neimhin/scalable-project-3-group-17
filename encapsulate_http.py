import socket
def encapsulate_http_request(path, tcp_host, tcp_port):
    request_headers = [
        f"GET {path} HTTP/1.1",
        f"Host: {tcp_host}",
        "Connection: close",
        "\r\n"
    ]

    # Create a TCP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((tcp_host, tcp_port))

    # Send the HTTP request as raw data
    request_data = "\r\n".join(request_headers).encode()
    s.sendall(request_data)

    # Receive the response headers
    response_headers = ''
    while '\r\n\r\n' not in response_headers:
        response_headers += s.recv(4096).decode()

    # Extract content length
    content_length = None
    for header in response_headers.split('\r\n'):
        if header.lower().startswith('content-length'):
            content_length = int(header.split(':')[1].strip())
            break

    # Read the response body
    response_body = ''
    if content_length:
        while len(response_body) < content_length:
            response_body += s.recv(4096).decode()

    s.close()

    return response_headers + response_body

# def encapsulate_http_request(path, tcp_host, tcp_port):
#     # HTTP request headers
#     request_headers = [
#         f"GET {path} HTTP/1.1",
#         f"Host: {tcp_host}",
#         "Connection: close",
#         "\r\n"
#     ]
# 
#     # Create a TCP socket
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.connect((tcp_host, tcp_port))
# 
#     # Send the HTTP request as raw data
#     request_data = "\r\n".join(request_headers).encode()
#     s.sendall(request_data)
# 
#     # Receive the response (this is simplified, real-world use requires more robust handling)
#     response = s.recv(4096)
#     s.close()
# 
#     return response

if __name__ == "__main__":
        response = encapsulate_http_request('http://10.35.70.37:33000', '10.35.70.37', 33000)
        print(response)
