import socket
import asyncio
def http_request(path, tcp_host, tcp_port, method='GET',headers=[],body=""):

    if body:
        headers.append(f"Content-Length: {len(body.encode('utf-8'))}")
    request_headers = [
        f"{method} {path} HTTP/1.1",
        f"Host: {tcp_host}",
        "Connection: close",
        *headers,
        "\r\n"
    ]
    request_data = ("\r\n".join(request_headers) + body).encode()

    print(request_data)
    # create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((tcp_host, tcp_port))
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

async def async_http_request(path, tcp_host, tcp_port, method='GET', headers=[], body=""):
    if body:
        headers.append(f"Content-Length: {len(body.encode('utf-8'))}")
    request_headers = [
        f"{method} {path} HTTP/1.1",
        f"Host: {tcp_host}",
        "Connection: close",
        *headers,
        "\r\n"
    ]
    request_data = ("\r\n".join(request_headers) + body).encode()

    # create an asynchronous socket
    reader, writer = await asyncio.open_connection(tcp_host, tcp_port)

    # send the request
    writer.write(request_data)
    await writer.drain()

    # read headers from the response
    response_headers = b''
    while b'\r\n\r\n' not in response_headers:
        response_headers += await reader.read(4096)

    # content length header
    content_length = None
    for header in response_headers.decode().split('\r\n'):
        if header.lower().startswith('content-length'):
            content_length = int(header.split(':')[1].strip())
            break

    # read response body according to content-length
    response_body = b''
    if content_length:
        while len(response_body) < content_length:
            response_body += await reader.read(4096)

    # close the connection
    writer.close()
    await writer.wait_closed()

    return response_headers + response_body

# Example usage
async def main():
    response = await async_http_request('/path', 'example.com', 80, method='GET', headers=['User-Agent: MyClient'], body='')
    print(response.decode())

# Run the asynchronous function
#asyncio.run(main())

if __name__ == "__main__":
        response = http_request('/', '10.35.70.37', 33000)
        print(response)
        print("RESPONSE BODY\n", extract_body_from_response(response))
