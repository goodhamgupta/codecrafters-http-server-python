import socket


def router(url) -> bytes:
    """
    Checks the requested URL and returns the appropriate HTTP response.

    Args:
        url (str): The requested URL.

    Returns:
        bytes: The HTTP response in bytes.
    """
    if url == "/":
        return b"HTTP/1.1 200 OK\r\n\r\n"
    elif url.startswith("/echo"):
        content = url.split("/")[2]
        content_len = len(content)
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {content_len}\r\n\r\n{content}".encode(
            "utf-8"
        )
    else:
        return b"HTTP/1.1 404 Not Found\r\n\r\n"


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    with server_socket:
        while True:
            client_sock, client_addr = server_socket.accept()  # wait for client
            request = client_sock.recv(1024).decode("utf-8")
            # 'request' object has the format:
            # GET /shampoo HTTP/1.1
            # Host: localhost:4221
            # User-Agent: curl/8.4.0
            # Accept: */*
            print("Received request:", request)
            request_line = request.splitlines()[0]
            url = request_line.split()[1]
            print(f"Requested URL: {url}")
            response = router(url)
            client_sock.sendall(response)
            client_sock.close()


if __name__ == "__main__":
    main()
