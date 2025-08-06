import socketserver
import threading
from .catalog import create_catalog
from .exceptions import CatalogError

class MCPRequestHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our MCP server.
    An instance of this class is created for each incoming connection.
    """
    def handle(self):
        """
        Handles a single client request.
        """
        try:
            # self.request is the TCP socket connected to the client.
            # We expect a request in the format: "target_dir|output_file"
            data = self.request.recv(4096).strip().decode('utf-8')

            # A simple check for empty data
            if not data:
                print(f"Received empty request from {self.client_address[0]}. Closing connection.")
                return

            print(f"Received request from {self.client_address[0]}: {data}")

            parts = data.split('|', 1)
            if len(parts) != 2:
                raise ValueError("Invalid request format. Expected 'target_dir|output_file'")

            target_dir, output_file = parts

            # Call the catalog creation logic
            create_catalog(target_dir, output_file)

            response = "SUCCESS"
            print(f"Successfully created catalog for '{target_dir}' at '{output_file}'")

        except CatalogError as e:
            response = f"ERROR: {e}"
            print(f"Cataloging error for {self.client_address[0]}: {e}")
        except FileNotFoundError as e:
            response = f"ERROR: {e}"
            print(f"File not found error for {self.client_address[0]}: {e}")
        except ValueError as e:
            response = f"ERROR: {e}"
            print(f"Invalid request from {self.client_address[0]}: {e}")
        except Exception as e:
            # Catch any other unexpected errors
            response = f"ERROR: An unexpected server error occurred: {e}"
            print(f"Unexpected error for {self.client_address[0]}: {e}")

        # Send the response back to the client
        self.request.sendall(response.encode('utf-8'))


class TCPServer(socketserver.ThreadingTCPServer):
    """
    A threading TCP server that allows address reuse.
    """
    # This option allows the server to restart quickly without waiting for the OS
    # to release the socket, which is useful for development.
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass=MCPRequestHandler):
        super().__init__(server_address, RequestHandlerClass)

    def serve_forever(self, poll_interval=0.5):
        print(f"MCP server starting on {self.server_address[0]}:{self.server_address[1]}...")
        super().serve_forever(poll_interval)
