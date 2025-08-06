import subprocess
import json
import sys
import pytest
from pathlib import Path
import tempfile
import shutil
import threading
import queue
import os

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files and clean up afterwards."""
    d = Path(tempfile.mkdtemp())
    yield d
    shutil.rmtree(d)

class MCPClient:
    """
    A client that runs the MCP server as a subprocess and communicates
    with it over stdio.
    """
    def __init__(self):
        # The poetry environment in the sandbox is broken. `poetry run` does not
        # correctly expose site-packages to the subprocess.
        # As a workaround, we manually construct the PYTHONPATH to include both
        # the project's src directory and the virtualenv's site-packages,
        # and then call the python executable directly.

        python_executable = sys.executable

        # Find the site-packages directory from the current environment
        site_packages = ""
        for p in sys.path:
            if 'site-packages' in p:
                site_packages = p
                break
        if not site_packages:
            raise RuntimeError("Could not find site-packages directory.")

        # Add the project's 'src' directory to the path
        project_root = Path(__file__).parent.parent
        src_path = project_root / "src"

        # Construct the environment for the subprocess
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join([str(src_path), site_packages, env.get("PYTHONPATH", "")])

        # Using -u for unbuffered output is a good practice for subprocess communication
        self.process = subprocess.Popen(
            [python_executable, "-u", "-m", "filelist_mcp_server.main", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            env=env
        )
        self.request_id = 1

        # It's good practice to read stderr on a separate thread to prevent deadlocks
        self.stderr_queue = queue.Queue()
        self.stderr_thread = threading.Thread(target=self._read_stderr)
        self.stderr_thread.daemon = True
        self.stderr_thread.start()

    def _read_stderr(self):
        for line in iter(self.process.stderr.readline, ''):
            self.stderr_queue.put(line)

    def send_request(self, method, params=None):
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self.request_id
        }
        self.request_id += 1

        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()

        # This might block if the server doesn't respond. A timeout would be good for production.
        response_line = self.process.stdout.readline()
        return json.loads(response_line)

    def send_notification(self, method, params=None):
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        self.process.stdin.write(json.dumps(notification) + "\n")
        self.process.stdin.flush()

    def close(self):
        """Closes stdin and waits for the process to terminate."""
        if self.process.stdin:
            self.process.stdin.close()

        self.process.wait(timeout=2)
        self.stderr_thread.join(timeout=1)

        # Check for any errors printed by the server
        stderr_output = []
        while not self.stderr_queue.empty():
            stderr_output.append(self.stderr_queue.get())

        if stderr_output:
            print("MCP Server stderr:\n", "".join(stderr_output))


def test_protocol_full_lifecycle(temp_dir):
    """Tests the full lifecycle of the MCP server from init to exit."""
    client = MCPClient()
    try:
        # 1. Initialize: Check if the server returns its capabilities
        response = client.send_request("initialize", {"capabilities": {}})
        assert "result" in response, "Response should contain a 'result' field"
        assert "capabilities" in response["result"], "Result should contain 'capabilities'"
        tools = response["result"]["capabilities"].get("tools", [])
        assert len(tools) == 1, "Server should advertise one tool"
        assert tools[0]["name"] == "catalog/create", "Tool name should be 'catalog/create'"

        # 2. Successful Tool Call: Create a catalog
        source_dir = temp_dir / "source"
        output_file = temp_dir / "catalog.tsv"
        (source_dir / "file.txt").write_text("some test data")

        response = client.send_request("catalog/create", {
            "target_dir": str(source_dir),
            "output_file": str(output_file)
        })
        assert "result" in response, "Successful call should return a result"
        assert response["result"]["status"] == "success", "Status should be 'success'"
        assert output_file.exists(), "Output file should have been created"
        assert "some test data" in output_file.read_text(), "File content check failed"

        # 3. Failed Tool Call: Trigger an error by using an existing output file
        response = client.send_request("catalog/create", {
            "target_dir": str(source_dir),
            "output_file": str(output_file)
        })
        assert "error" in response, "Failed call should return an error"
        # Custom error code for OutputFileExistsError
        assert response["error"]["code"] == 1001, "Error code should indicate file exists"

        # 4. Shutdown and Exit
        client.send_notification("shutdown")
        client.send_notification("exit")

        # The 'exit' notification should cause the process to terminate.
        assert client.process.wait(timeout=1) == 0, "Process should terminate gracefully"

    finally:
        client.close()
        # In case of early failure, ensure the process is terminated
        if client.process.poll() is None:
            client.process.kill()
