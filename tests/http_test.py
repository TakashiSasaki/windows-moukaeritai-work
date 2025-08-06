import pytest
from aiohttp import web
from pathlib import Path
import tempfile
import shutil

from filelist_mcp_server import http_server
from filelist_mcp_server import handlers

# Mark all tests in this file as async
pytestmark = pytest.mark.asyncio

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files and clean up afterwards."""
    d = Path(tempfile.mkdtemp())
    yield d
    shutil.rmtree(d)

@pytest.fixture
async def mcp_client(aiohttp_client):
    """
    Fixture that sets up the aiohttp application and provides a test client.
    `aiohttp_client` is a fixture provided by pytest-aiohttp.
    """
    # Ensure our request handlers are loaded
    _ = handlers

    app = web.Application()
    # Register the same handler that the real server uses
    app.router.add_route('POST', '/mcp', http_server.mcp_handler)

    # aiohttp_client creates a client that talks to the app in-memory
    client = await aiohttp_client(app)
    return client

async def test_http_initialize(mcp_client):
    """Test the initialize method over HTTP."""
    request = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {"capabilities": {}},
        "id": 1
    }
    response = await mcp_client.post('/mcp', json=request)
    assert response.status == 200
    data = await response.json()
    assert "result" in data
    assert data['result']['capabilities']['tools'][0]['name'] == 'catalog/create'

async def test_http_catalog_create_success(mcp_client, temp_dir):
    """Test a successful catalog/create call over HTTP."""
    source_dir = temp_dir / "source"
    output_file = temp_dir / "catalog.tsv"
    source_dir.mkdir()
    (source_dir / "file1.txt").write_text("http test")

    request = {
        "jsonrpc": "2.0",
        "method": "catalog/create",
        "params": {"target_dir": str(source_dir), "output_file": str(output_file)},
        "id": 2
    }
    response = await mcp_client.post('/mcp', json=request)
    assert response.status == 200
    data = await response.json()
    assert "result" in data
    assert data['result']['status'] == 'success'
    assert output_file.exists()

async def test_http_catalog_create_error(mcp_client, temp_dir):
    """Test a failing catalog/create call (output file exists) over HTTP."""
    source_dir = temp_dir / "source"
    output_file = temp_dir / "catalog.tsv"
    source_dir.mkdir()
    output_file.touch() # Pre-create the file to cause an error

    request = {
        "jsonrpc": "2.0",
        "method": "catalog/create",
        "params": {"target_dir": str(source_dir), "output_file": str(output_file)},
        "id": 3
    }
    response = await mcp_client.post('/mcp', json=request)
    # The HTTP call itself is successful, but the JSON-RPC response contains an error.
    assert response.status == 200
    data = await response.json()
    assert "error" in data
    assert data['error']['code'] == 1001 # Our custom code for "file exists"
