import socket


class View:
    @staticmethod
    def root(**args) -> bytes:
        """
        Returns the HTTP response for the root URL.

        Returns:
            bytes: The HTTP response in bytes.
        """
        return b"HTTP/1.1 200 OK\r\n\r\n"


    @staticmethod
    def echo(**args) -> bytes:
        """
        Returns the HTTP response for the echo URL.

        Args:
            url (str): The requested URL.

        Returns:
            bytes: The HTTP response in bytes.
        """
        content = args["url"].split("/")[2]
        content_len = len(content)
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {content_len}\r\n\r\n{content}".encode(
            "utf-8"
        )

    @staticmethod
    def not_found(**args) -> bytes:
        """
        Returns the HTTP response for a 404 Not Found error.

        Returns:
            bytes: The HTTP response in bytes.
        """
        return b"HTTP/1.1 404 Not Found\r\n\r\n"


    @staticmethod
    def user_agent(**args) -> bytes:
        """
        Returns the HTTP response containing the User-Agent header.

        Args:
            url (str): The requested URL.

        Returns:
            bytes: The HTTP response in bytes.
        """
        content = args["user_agent"]
        content_len = len(content)
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {content_len}\r\n\r\n{content}".encode(
            "utf-8"
        )


def router(request: str) -> bytes:
    """
    Checks the requested URL and returns the appropriate HTTP response.

    Args:
        url (str): The requested URL.

    Returns:
        bytes: The HTTP response in bytes.
    """
    ENDPOINT_SLICE = slice(0, 2)
    request_lines = request.splitlines()
    url = request_lines[0].split()[1]
    print("Request LINES: ", request_lines)
    user_agent = request_lines[2].split()[1]
    print(f"Requested URL: {url}")
    endpoint = "".join(url.split("/")[ENDPOINT_SLICE])
    print(f"Endpoint: {endpoint}")
    mapping = {"": View.root, "echo": View.echo, "user-agent": View.user_agent}
    return mapping.get(endpoint, View.not_found)(url=url, user_agent=user_agent)


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
            response = router(request)
            client_sock.sendall(response)
            client_sock.close()


if __name__ == "__main__":
    main()
