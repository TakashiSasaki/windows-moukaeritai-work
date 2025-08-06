import argparse
from .server import TCPServer

def main():
    """
    The main entry point for the MCP server application.
    It parses command-line arguments and starts the TCP server.
    """
    parser = argparse.ArgumentParser(description="A TCP server to create file catalogs.")
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="The host address to bind the server to. Defaults to 'localhost'."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=10000,
        help="The port number for the server to listen on. Defaults to 10000."
    )
    args = parser.parse_args()

    try:
        # The 'with' statement ensures that the server's shutdown() method is
        # called automatically, even if errors occur.
        with TCPServer((args.host, args.port)) as server:
            # The server will run indefinitely until interrupted (e.g., with Ctrl+C).
            server.serve_forever()
    except OSError as e:
        print(f"Error: Could not start server on {args.host}:{args.port}. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
