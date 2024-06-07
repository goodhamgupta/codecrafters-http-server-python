import socket
from pathlib import Path
from threading import Thread
from argparse import Namespace
import argparse
from typing import Tuple


class View:
    ENCODING_IDX = 2
    VALID_ENCODINGS = ["utf-8", "utf-16", "utf-32", "gzip"]

    @staticmethod
    def root(**args) -> bytes:
        """
        Returns the HTTP response for the root URL.

        Returns:
            bytes: The HTTP response in bytes.
        """
        return b"HTTP/1.1 200 OK\r\n\r\n"

    @classmethod
    def echo(cls, **args) -> bytes:
        """
        Returns the HTTP response for the echo URL.

        Args:
            url (str): The requested URL.

        Returns:
            bytes: The HTTP response in bytes.
        """
        content = args["url"].split("/")[2]
        content_encoding_header = ""
        if len(args["request_lines"]) > cls.ENCODING_IDX:
            encoding_split = args["request_lines"][cls.ENCODING_IDX].split(":")
            if len(encoding_split) > 1:
                encoding = encoding_split[1].strip()
                if encoding in cls.VALID_ENCODINGS:
                    content_encoding_header = f"Content-Encoding: {encoding}"
        content_len = len(content)
        if len(content_encoding_header) > 0:
            return f"HTTP/1.1 200 OK\r\n{content_encoding_header}\r\nContent-Type: text/plain\r\nContent-Length: {content_len}\r\n\r\n{content}".encode(
                "utf-8"
            )
        else:
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
        user_agent = ""
        request_lines = args["request_lines"]
        if len(request_lines) > 2:
            user_agent = (
                request_lines[2].split()[1] if len(request_lines[2]) > 0 else ""
            )
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}".encode(
            "utf-8"
        )

    @staticmethod
    def files(**args) -> bytes:
        """
        Returns the HTTP response for the files URL.

        Args:
            url (str): The requested URL.

        Returns:
            bytes: The HTTP response in bytes.
        """
        fname = args["url"].split("/")[2]
        root_dir = getattr(args["parser_args"], "directory")
        path = Path(f"{root_dir}/{fname}")
        method = args["request_lines"][0].split()[0].strip().upper()
        if method == "GET":
            if path.exists():
                content = path.read_text()
                content_len = len(content.encode("utf-8"))
                return f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {content_len}\r\n\r\n{content}".encode(
                    "utf-8"
                )
            else:
                return b"HTTP/1.1 404 Not Found\r\n\r\n"
        elif method == "POST":
            content_slice = slice(4, None)
            content = "\n".join(args["request_lines"][content_slice])
            path.write_text(content)
            return b"HTTP/1.1 201 Created\r\n\r\n"
        else:
            return b"HTTP/1.1 405 Method Not Allowed\r\n\r\n"


def router(request: str, parser_args: Namespace) -> bytes:
    """
    Checks the requested URL and returns the appropriate HTTP response.

    Args:
        url (str): The requested URL.

    Returns:
        bytes: The HTTP response in bytes.
    """
    ENDPOINT_SLICE = slice(0, 2)
    request_lines = request.splitlines()
    print("Request lines: ", request_lines)
    if len(request_lines) < 1:
        print("Invalid request")
        return b""
    url = request_lines[0].split()[1]
    print(f"Requested URL: {url}")
    endpoint = "".join(url.split("/")[ENDPOINT_SLICE])
    print(f"Endpoint: {endpoint}")
    mapping = {
        "": View.root,
        "echo": View.echo,
        "user-agent": View.user_agent,
        "files": View.files,
    }
    return mapping.get(endpoint, View.not_found)(
        url=url, request_lines=request_lines, parser_args=parser_args
    )


def process_request(
    client_sock: socket.socket, client_addr: Tuple[str], parser_args: Namespace
):
    """
    Processes the incoming client request and sends back the appropriate HTTP response.

    Args:
        client_sock (socket.socket): The client socket object.
        client_addr (tuple): The client address.
    """
    print("Processing request from: ", client_addr)
    request = client_sock.recv(1024).decode("utf-8")
    # 'request' object has the format:
    # GET /shampoo HTTP/1.1
    # Host: localhost:4221
    # User-Agent: curl/8.4.0
    # Accept: */*
    print("Received request:", request)
    response = router(request, parser_args=parser_args)
    client_sock.sendall(response)
    client_sock.close()


def main():
    """
    Starts the HTTP server and listens for incoming client connections.

    The server listens on localhost at port 4221. For each incoming client connection,
    a new thread is spawned to handle the request using the `process_request` function.
    """
    parser = argparse.ArgumentParser(description="HTTP Server")
    parser.add_argument(
        "--directory", type=str, help="Directory to serve files from", default="/tmp/"
    )
    parser_args = parser.parse_args()
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.listen(5)
    while server_socket:
        client_sock, client_addr = server_socket.accept()  # wait for client
        Thread(
            target=process_request, args=(client_sock, client_addr, parser_args)
        ).start()


if __name__ == "__main__":
    main()
