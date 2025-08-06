import socket
import threading
import time
import pytest
from pathlib import Path
import tempfile
import shutil

from filelist_mcp_server.server import TCPServer, MCPRequestHandler

# Use a non-default port for testing to avoid conflicts with a running server
SERVER_HOST = "localhost"
SERVER_PORT = 10001

@pytest.fixture
def server_thread():
    """
    A pytest fixture that runs the TCP server in a background thread.
    This allows the tests to run a client against a live server instance.
    """
    # Create a server instance
    server = TCPServer((SERVER_HOST, SERVER_PORT), MCPRequestHandler)

    # Run the server in a daemon thread. Daemon threads are automatically
    # terminated when the main program exits.
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    # Brief pause to ensure the server is up and listening
    time.sleep(0.1)

    # Yield the server instance to the test function
    yield server

    # Teardown: cleanly shut down the server after the test is done
    server.shutdown()
    server.server_close()
    thread.join()

@pytest.fixture
def temp_dir():
    """Fixture to create a temporary directory for test files and clean up."""
    d = Path(tempfile.mkdtemp())
    yield d
    shutil.rmtree(d)

def mcp_client(request_str: str) -> str:
    """
    A simple TCP client to send a request string to the test server and
    return the response.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_HOST, SERVER_PORT))
        sock.sendall(request_str.encode('utf-8'))
        response = sock.recv(1024).decode('utf-8')
    return response

def test_integration_success(server_thread, temp_dir):
    """
    Integration test for a successful catalog creation request.
    """
    # Setup
    source_dir = temp_dir / "source"
    output_file = temp_dir / "catalog.tsv"
    (source_dir / "subdir").mkdir(parents=True, exist_ok=True)
    (source_dir / "subdir" / "my_test_file.txt").write_text("some data")

    # Execute
    request = f"{source_dir}|{output_file}"
    response = mcp_client(request)

    # Verify
    assert response == "SUCCESS"
    assert output_file.exists()
    # A simple check to ensure the file was mentioned in the catalog
    assert "my_test_file.txt" in output_file.read_text(encoding='utf-8')

def test_integration_output_exists_error(server_thread, temp_dir):
    """
    Integration test for a request that fails because the output file exists.
    """
    # Setup
    source_dir = temp_dir / "source"
    output_file = temp_dir / "catalog.tsv"
    source_dir.mkdir()
    output_file.touch() # Pre-create the output file to trigger the error

    # Execute
    request = f"{source_dir}|{output_file}"
    response = mcp_client(request)

    # Verify
    assert response.startswith("ERROR")
    assert "Output file already exists" in response

def test_integration_invalid_request_format(server_thread):
    """
    Integration test for a request with an invalid format.
    """
    # Execute
    response = mcp_client("this is not a valid request")

    # Verify
    assert response.startswith("ERROR")
    assert "Invalid request format" in response
