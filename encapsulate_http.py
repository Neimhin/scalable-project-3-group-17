import socket
def http_request(path, tcp_host, tcp_port, method='GET'):
    request_headers = [
        f"{method} {path} HTTP/1.1",
        f"Host: {tcp_host}",
        "Connection: close",
        "\r\n"
    ]

    # create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((tcp_host, tcp_port))

    # Send the HTTP request as raw data
    request_data = "\r\n".join(request_headers).encode()
    s.sendall(request_data)

    # read headers from tcp stream 
    response_headers = ''
    while '\r\n\r\n' not in response_headers:
        response_headers += s.recv(4096).decode()

    # content length header
    content_length = None
    for header in response_headers.split('\r\n'):
        if header.lower().startswith('content-length'):
            content_length = int(header.split(':')[1].strip())
            break

    # read response body according to content-length
    response_body = ''
    if content_length:
        while len(response_body) < content_length:
            response_body += s.recv(4096).decode()

    s.close()

    return response_headers + response_body

def extract_body_from_response(http_response):
    # split the response into headers and body
    parts = http_response.split('\r\n\r\n', 1)

    # check if the split found both headers and body
    if len(parts) > 1:
        headers, body = parts
        return body
    else:
        # no body, return an empty string
        return ''

if __name__ == "__main__":
        response = http_request('/', '10.35.70.37', 33000)
        print(response)
        print("RESPONSE BODY\n", extract_body_from_response(response))
