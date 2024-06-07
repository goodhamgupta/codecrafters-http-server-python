import socket


def check_url(url) -> bytes:
    """
    Checks the requested URL and returns the appropriate HTTP response.

    Args:
        url (str): The requested URL.

    Returns:
        bytes: The HTTP response in bytes.
    """
    if url == "/":
        return b"HTTP/1.1 200 OK\r\n\r\n"
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
            request_line = request.splitlines()[0]
            url = request_line.split()[1]
            print(f"Requested URL: {url}")
            response = check_url(url)
            client_sock.sendall(response)
            client_sock.close()


if __name__ == "__main__":
    main()
